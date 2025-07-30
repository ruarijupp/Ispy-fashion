# backend/app/scrapers/moda_operandi.py

from playwright.sync_api import sync_playwright
from app.db import setup_qdrant, insert_products, insert_product_to_qdrant
from embedder import embed_image_from_url
from app.scrapers.nanushka import save_products_to_db

MAX_PAGES = 41

def scrape_moda_operandi(page):
    products = []
    seen = set()

    for page_num in range(1, MAX_PAGES + 1):
        url = f"https://www.modaoperandi.com/women/products/clothing?page={page_num}"
        print(f"\n🌐 Visiting: {url}")
        try:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"❌ Failed to load page {page_num}: {e}")
            continue

        image_elements = page.query_selector_all("img")

        for img in image_elements:
            image_url = img.get_attribute("src")
            if not image_url or "modaoperandi.com" not in image_url:
                continue
            if image_url.startswith("//"):
                image_url = "https:" + image_url
            if image_url.startswith("data:") or image_url in seen:
                continue
            seen.add(image_url)

            try:
                anchor = img.evaluate_handle("img => img.closest('a')")
                product_url = anchor.get_attribute("href") if anchor else None
                if product_url and product_url.startswith("/"):
                    product_url = f"https://www.modaoperandi.com{product_url}"
            except Exception:
                product_url = None

            print(f"🔗 Found image: {image_url}")
            print(f"➡️ Product URL: {product_url or 'None'}")

            vector = embed_image_from_url(image_url)
            if vector is None:
                print("⚠️ Skipping product, embedding failed.")
                continue

            product = {
                "id": image_url,  # Use image URL as stable unique ID
                "brand": "Moda Operandi",
                "title": image_url.split("/")[-1].split("?")[0],
                "url": product_url or image_url,
                "image_url": image_url
            }

            insert_product_to_qdrant(product, vector)
            products.append(product)

    return products

def main(reset_qdrant=False):
    if reset_qdrant:
        setup_qdrant()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("=== Scraping Moda Operandi ===")
        products = scrape_moda_operandi(page)

        insert_products(products)
        save_products_to_db(products, "moda_operandi")

        print(f"\n✅ Scraped {len(products)} unique items from Moda Operandi")
        browser.close()

if __name__ == "__main__":
    main()
