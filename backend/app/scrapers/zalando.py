# app/scrape_zalando.py

from playwright.sync_api import sync_playwright
from app.db import setup_qdrant, insert_vector, insert_products
from backend.embedder import embed_image_from_url
import uuid
import time
import random

MAX_PAGES = 428


def scrape_zalando(page):
    """
    Scrapes Zalando product images across multiple pages and returns a list of product dicts.
    """
    products = []
    seen = set()

    for page_num in range(1, MAX_PAGES + 1):
        url = f"https://www.zalando.co.uk/womens-clothing/?p={page_num}"
        print(f"\n🌐 Visiting: {url}")
        try:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"❌ Failed to load page {page_num}: {e}")
            continue

        # Optional: scroll for lazy-loaded images
        for _ in range(3):
            page.evaluate("window.scrollBy(0, document.body.scrollHeight / 3)")
            time.sleep(random.uniform(0.5, 1.0))

        image_elements = page.query_selector_all("img")
        print(f"🧾 Found {len(image_elements)} <img> tags on page {page_num}")

        for img in image_elements:
            image_url = img.get_attribute("src")
            if not image_url or "zalando" not in image_url:
                continue

            # Normalize protocol
            if image_url.startswith("//"):
                image_url = "https:" + image_url

            if image_url in seen:
                continue
            seen.add(image_url)

            print(f"🔗 Found image: {image_url}")
            try:
                vector = embed_image_from_url(image_url)
                if vector is None:
                    print("⚠️ Skipping product, embedding failed.")
                    continue

                product_id = str(uuid.uuid4())
                product = {
                    "id": product_id,
                    "brand": "Zalando",
                    "title": image_url.split("/")[-1].split("?")[0],
                    "url": image_url,
                    "image_url": image_url
                }

                insert_vector(product_id, vector, product)
                products.append(product)

            except Exception as e:
                print(f"❌ Error scraping product: {e}")
                continue

        # Polite delay between pages
        time.sleep(random.uniform(1.5, 3.0))

    return products


def main():
    setup_qdrant()
    print("🧹 Qdrant collection reset.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("=== Scraping Zalando ===")
        products = scrape_zalando(page)
        insert_products(products)

        print(f"\n✅ Scraped {len(products)} unique items from Zalando")
        browser.close()


if __name__ == "__main__":
    main()
