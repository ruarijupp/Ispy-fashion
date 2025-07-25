from playwright.sync_api import sync_playwright
from app.db import setup_qdrant, insert_vector, insert_products
from app.embedder import embed_image_from_url
import uuid
import time
import random

MAX_PAGES = 35  # FWRD: 35 total pages

def scrape_fwrd(page):
    products = []
    seen = set()

    for page_num in range(1, MAX_PAGES + 1):
        url = f"https://www.fwrd.com/category-clothing/3699fc/?navsrc=main&pageNum={page_num}"
        print(f"\n🌐 Visiting: {url}")

        # Retry-safe page load
        for attempt in range(1, 3):
            try:
                page.goto(url, timeout=60000, wait_until="networkidle")
                page.wait_for_timeout(3000)
                break
            except Exception as e:
                print(f"❌ Attempt {attempt} failed loading page {page_num}: {e}")
                time.sleep(2)
        else:
            print(f"🚫 Skipping page {page_num} after 2 failed attempts")
            continue

        image_elements = page.query_selector_all("img")
        print(f"🖼️ Found {len(image_elements)} images on page {page_num}")

        for img in image_elements:
            image_url = img.get_attribute("src")
            if not image_url or "fwrd.com" not in image_url:
                continue
            if image_url.startswith("//"):
                image_url = "https:" + image_url
            if image_url.startswith("data:") or image_url in seen:
                continue
            seen.add(image_url)

            # Try to get product link
            try:
                anchor = img.evaluate_handle("img => img.closest('a')")
                product_url = anchor.get_attribute("href") if anchor else None
                if product_url and product_url.startswith("/"):
                    product_url = f"https://www.fwrd.com{product_url}"
            except Exception:
                product_url = None

            print(f"🔗 Found image: {image_url}")
            print(f"➡️ Product URL: {product_url or 'None'}")

            try:
                vector = None
                for attempt in range(1, 4):
                    vector = embed_image_from_url(image_url)
                    if vector is not None:
                        print("✅ Embed successful")
                        break
                    print(f"❌ Embed error on attempt {attempt}/3")
                    time.sleep(1)

                if vector is None:
                    print("⚠️ Skipping product, embedding failed.")
                    continue

                product_id = str(uuid.uuid4())
                product = {
                    "id": product_id,
                    "brand": "FWRD",
                    "title": image_url.split("/")[-1].split("?")[0],
                    "url": product_url or image_url,
                    "image_url": image_url
                }

                insert_vector(product_id, vector, product)
                products.append(product)

            except Exception as e:
                print(f"❌ Error scraping product: {e}")

        time.sleep(random.uniform(3.5, 6.0))  # longer delay to reduce blocks

    return products


def main():
    setup_qdrant()
    print("🧹 Qdrant collection reset.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print("=== Scraping FWRD ===")
        products = scrape_fwrd(page)
        insert_products(products)

        print(f"\n✅ Scraped {len(products)} unique items from FWRD")
        browser.close()

if __name__ == "__main__":
    main()
