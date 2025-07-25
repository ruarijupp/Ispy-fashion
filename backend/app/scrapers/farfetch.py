from playwright.sync_api import sync_playwright
from app.embedder import embed_image_from_url
import sqlite3
import uuid
import time
import random

MAX_PAGES = 100  # Increase to 2162 for full scrape
FAST_MODE = True  # Toggle to speed things up by skipping embedding and delays

def scrape_farfetch(page):
    products = []
    seen = set()

    for page_num in range(1, MAX_PAGES + 1):
        url = (
            "https://www.farfetch.com/uk/shopping/women/clothing-1/items.aspx"
            if page_num == 1
            else f"https://www.farfetch.com/uk/shopping/women/clothing-1/items.aspx?page={page_num}"
        )

        print(f"\n🌐 Visiting: {url}")
        try:
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000 if FAST_MODE else 3000)
        except Exception as e:
            print(f"❌ Failed to load page {page_num}: {e}")
            continue

        items = page.query_selector_all("li[data-testid='productCard']")
        print(f"📟 Found {len(items)} product cards on page {page_num}")

        for item in items:
            try:
                image_el = item.query_selector("img")
                link_el = item.query_selector("a")

                if not image_el or not link_el:
                    continue

                image_url = image_el.get_attribute("src") or image_el.get_attribute("data-src")
                product_path = link_el.get_attribute("href")

                if not image_url or not product_path:
                    continue
                if image_url.startswith("//"):
                    image_url = "https:" + image_url
                if image_url.startswith("data:"):
                    continue
                if image_url in seen:
                    continue
                seen.add(image_url)

                title = image_el.get_attribute("alt") or "Untitled"
                full_url = f"https://www.farfetch.com{product_path}"

                print(f"🔗 Found image: {image_url}")
                print(f"➡️ Product URL: {full_url}")

                vector = None
                if not FAST_MODE:
                    print(f"🧠 Embedding: {image_url}")
                    for attempt in range(1, 3):
                        vector = embed_image_from_url(image_url)
                        if vector is not None:
                            print("✅ Embed successful")
                            break
                        print(f"❌ Embed error on attempt {attempt}/2")
                        time.sleep(0.25)

                    if vector is None:
                        print("⚠️ Skipping product, embedding failed.")
                        continue

                product_id = str(uuid.uuid4())
                product = {
                    "id": product_id,
                    "brand": "Farfetch",
                    "title": title.strip(),
                    "url": full_url,
                    "image_url": image_url
                }

                products.append(product)

                if not FAST_MODE:
                    time.sleep(random.uniform(0.5, 1.5))
                else:
                    time.sleep(0.1)

            except Exception as e:
                print(f"❌ Error scraping product: {e}")
                continue

        time.sleep(1 if FAST_MODE else random.uniform(1.5, 3.0))

    return products

def save_to_db(products, db_name):
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
        context = browser.new_context()
        page = context.new_page()

        # Stealth patch
        page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )

        print("=== Scraping Farfetch ===")
        products = scrape_farfetch(page)
        save_to_db(products, "farfetch")

        print(f"\n✅ Scraped {len(products)} unique items from Farfetch")
        browser.close()

if __name__ == "__main__":
    main()
