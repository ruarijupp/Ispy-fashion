# app/scrapers/shopbop.py

from playwright.sync_api import sync_playwright
from app.utils.stealth import apply_stealth
from app.db import insert_products, insert_vector, setup_qdrant
from backend.embedder import embed_image_from_url
import uuid
import time
import random

BASE_URL = "https://www.shopbop.com/clothing/br/v=1/2534374302063518.htm"
MAX_PAGES = 47
ITEMS_PER_PAGE = 100

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.141 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
]

def scrape_shopbop(page):
    all_products = []
    seen = set()

    for i in range(MAX_PAGES):
        offset = i * ITEMS_PER_PAGE
        url = f"{BASE_URL}?offset={offset}" if offset else BASE_URL
        print(f"\n🌍 Scraping Shopbop page {i + 1} — {url}")

        ua = random.choice(USER_AGENTS)
        page.set_extra_http_headers({"User-Agent": ua})

        for attempt in range(3):
            try:
                page.goto(url, timeout=60000)
                page.wait_for_selector("div.browse-tile", timeout=30000)
                break
            except Exception as e:
                print(f"⚠️ Retry {attempt+1} for page {i + 1}: {e}")
                time.sleep(2)
        else:
            print(f"❌ Failed to load page {i + 1}")
            continue

        for _ in range(30):
            page.evaluate("window.scrollBy(0, document.body.scrollHeight / 15)")
            page.wait_for_timeout(300)

        images = page.query_selector_all("div.browse-tile img")
        print(f"🧾 Found {len(images)} product images on page {i + 1}")

        for img in images:
            image_url = img.get_attribute("src") or img.get_attribute("data-src") or img.get_attribute("srcset")
            if not image_url or image_url.startswith("data:") or "Shopbop/media" not in image_url:
                continue
            if image_url.startswith("//"):
                image_url = "https:" + image_url
            if image_url in seen:
                continue
            seen.add(image_url)

            print(f"🔗 Found product image: {image_url}")
            vector = embed_image_from_url(image_url)
            if vector is None:
                print("⚠️ Skipped: embedding failed.")
                continue
            print("✅ Embed successful")

            product = {
                "id": str(uuid.uuid4()),
                "brand": "Shopbop",
                "title": image_url.split("/")[-1].split("?")[0],
                "url": image_url,
                "image_url": image_url
            }

            insert_vector(product["id"], vector, product)
            all_products.append(product)
            time.sleep(random.uniform(0.3, 1.2))

        time.sleep(random.uniform(1.5, 3.0))

    return all_products

def main():
    setup_qdrant()
    print("🧹 Qdrant collection reset.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        apply_stealth(page)

        print("=== Scraping Shopbop ===")
        products = scrape_shopbop(page)
        insert_products(products)

        print(f"\n✅ Shopbop: {len(products)} images collected.")
        browser.close()

if __name__ == "__main__":
    main()