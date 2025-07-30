# backend/app/scrapers/farfetch.py

from playwright.sync_api import sync_playwright
from app.db import setup_qdrant, insert_products, insert_product_to_qdrant
from embedder import embed_image_from_url
from app.scrapers.nanushka import save_products_to_db
import sqlite3
import time

MAX_PAGES = 50  # Increase as needed

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
            page.wait_for_timeout(3000)
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
                if image_url.startswith("data:") or image_url in seen:
                    continue
                seen.add(image_url)

                title = image_el.get_attribute("alt") or "Untitled"
                full_url = f"https://www.farfetch.com{product_path}"

                print(f"🔗 Found image: {image_url}")
                print(f"➡️ Product URL: {full_url}")

                vector = embed_image_from_url(image_url)
                if vector is None:
                    print("⚠️ Skipping product, embedding failed.")
                    continue

                product = {
                    "id": image_url,  # Use image URL as stable unique ID
                    "brand": "Farfetch",
                    "title": title.strip(),
                    "url": full_url,
                    "image_url": image_url
                }

                insert_product_to_qdrant(product, vector)
                products.append(product)

            except Exception as e:
                print(f"❌ Error scraping product: {e}")
                continue

        # Pause to avoid rate limits
        time.sleep(2)

    return products

def main(reset_qdrant=False):
    if reset_qdrant:
        setup_qdrant()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("=== Scraping Farfetch ===")
        products = scrape_farfetch(page)

        insert_products(products)
        save_products_to_db(products, "farfetch")

        print(f"\n✅ Scraped {len(products)} unique items from Farfetch")
        browser.close()

if __name__ == "__main__":
    main()
