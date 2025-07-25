from playwright.sync_api import sync_playwright
from app.embedder import embed_image_from_url
import sqlite3
import uuid
import time
import random

FAST_MODE = True  # Set False to enable embedding
CATEGORIES = {
    "shoes": 38,
    "bags": 5
}

MAX_RETRIES = 3

def scrape_outnet(page):
    all_products = []
    seen = set()

    for category, max_pages in CATEGORIES.items():
        print(f"\n👟 Scraping category: {category}")

        for page_num in range(1, max_pages + 1):
            url = (
                f"https://www.theoutnet.com/en-gb/shop/{category}"
                if page_num == 1 else f"https://www.theoutnet.com/en-gb/shop/{category}?pageNumber={page_num}"
            )

            success = False
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    print(f"\n🌐 Visiting: {url} (Attempt {attempt})")
                    page.goto(url, timeout=60000)
                    page.wait_for_load_state("load")
                    page.wait_for_selector("li[class*='ProductItem']", timeout=10000)
                    page.wait_for_timeout(random.randint(1000, 3000))  # Slightly human-like pause
                    success = True
                    break
                except Exception as e:
                    print(f"❌ Failed attempt {attempt} for page {page_num}: {e}")
                    time.sleep(random.uniform(2, 5))

            if not success:
                print(f"🚫 Giving up on {url}")
                continue

            cards = page.query_selector_all("li[class*='ProductItem']")
            print(f"👜 Found {len(cards)} products on page {page_num}")

            for card in cards:
                try:
                    img_el = card.query_selector("img")
                    a_el = card.query_selector("a")

                    if not img_el or not a_el:
                        continue

                    image_url = img_el.get_attribute("src") or img_el.get_attribute("data-src")
                    product_path = a_el.get_attribute("href")

                    if not image_url or not product_path:
                        continue
                    if image_url.startswith("//"):
                        image_url = "https:" + image_url
                    if image_url.startswith("data:") or image_url in seen:
                        continue
                    seen.add(image_url)

                    title = img_el.get_attribute("alt") or "Untitled"
                    full_url = f"https://www.theoutnet.com{product_path}"

                    print(f"🔗 {title}")
                    print(f"🖼️ {image_url}")
                    print(f"➡️ {full_url}")

                    vector = None
                    if not FAST_MODE:
                        vector = embed_image_from_url(image_url)
                        if vector is None:
                            print("⚠️ Skipping: embedding failed")
                            continue

                    product_id = str(uuid.uuid4())
                    product = {
                        "id": product_id,
                        "brand": "The Outnet",
                        "title": title.strip(),
                        "url": full_url,
                        "image_url": image_url
                    }

                    all_products.append(product)
                    time.sleep(random.uniform(0.3, 1.0))  # Between items

                except Exception as e:
                    print(f"❌ Error parsing item: {e}")
                    continue

            time.sleep(random.uniform(2, 5))  # Between pages

    return all_products

def save_to_db(products, db_name="theoutnet"):
    conn = sqlite3.connect(f"{db_name}.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            brand TEXT,
            title TEXT,
            url TEXT,
            image_url TEXT
        )
    """)
    for p in products:
        try:
            c.execute("INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?, ?)", (
                p["id"], p["brand"], p["title"], p["url"], p["image_url"]
            ))
        except Exception as e:
            print(f"❌ DB insert error: {e}")
    conn.commit()
    conn.close()

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            java_script_enabled=True,
            ignore_https_errors=True
        )
        page = context.new_page()

        # 🕵️ Stealth tweak
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

        print("🚀 Starting The Outnet scrape")
        products = scrape_outnet(page)
        save_to_db(products)

        print(f"\n✅ Scraped {len(products)} total products from The Outnet")
        browser.close()

if __name__ == "__main__":
    main()
