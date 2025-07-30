# app/scrapers/ssense.py

from playwright.sync_api import sync_playwright, Error as PlaywrightError
from app.db import setup_qdrant, insert_vector, insert_products
from backend.embedder import embed_image_from_url
import uuid
import time
import random

MAX_PAGES = 605
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.141 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
]

def scrape_ssense(page):
    products = []
    seen = set()

    for page_num in range(1, MAX_PAGES + 1):
        url = f"https://www.ssense.com/en-es/women?page={page_num}"
        print(f"\n🌐 Visiting: {url}")

        for attempt in range(1, 4):
            try:
                page.goto(url, timeout=60000, wait_until="load")
                break
            except PlaywrightError as e:
                print(f"⚠️ Load failed (attempt {attempt}/3): {e}")
                time.sleep(2 + random.random())
        else:
            print(f"❌ Skipping page {page_num} after 3 failed attempts")
            continue

        page.wait_for_timeout(random.randint(1500, 3500))
        imgs = page.query_selector_all("img")
        print(f"📟 Found {len(imgs)} <img> tags")

        for img in imgs:
            src = img.get_attribute("src")
            if not src:
                print("⚠️ Skipping: no src found")
                continue

            if "ssense.com" not in src:
                print(f"⚠️ Skipping: not a product image → {src}")
                continue

            if src.startswith("//"):
                src = "https:" + src
            if src in seen or src.startswith("data:"):
                continue
            seen.add(src)

            print(f"🔗 Found image: {src}")
            try:
                vector = embed_image_from_url(src)
                if vector is None:
                    print("⚠️ Skipping product, embedding failed.")
                    continue

                pid = str(uuid.uuid4())
                product = {
                    "id": pid,
                    "brand": "SSENSE",
                    "title": src.split("/")[-1].split("?")[0],
                    "url": src,
                    "image_url": src
                }
                insert_vector(pid, vector, product)
                products.append(product)
                time.sleep(random.uniform(0.2, 0.7))

            except Exception as e:
                print(f"❌ Error embedding {src}: {e}")

        time.sleep(random.uniform(1.0, 2.0))

    return products

def main():
    setup_qdrant()
    print("🧹 Qdrant collection reset.")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--enable-features=NetworkService",
            ]
        )
        context = browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1280, "height": 800},
            locale="en-US",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document"
            }
        )
        page = context.new_page()

        page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', { get: () => undefined })"
        )

        print("=== Scraping SSENSE ===")
        prods = scrape_ssense(page)
        insert_products(prods)

        print(f"\n✅ Scraped {len(prods)} unique items from SSENSE")
        browser.close()

if __name__ == "__main__":
    main()
