from playwright.sync_api import sync_playwright
from app.db import setup_qdrant, insert_vector, insert_products
from app.embedder import embed_image_from_url
import uuid
import time
import random

MAX_PAGES = 200  # There are about 200 pages total

def scrape_flannels(page, max_pages=MAX_PAGES):
    products = []
    seen = set()

    base_url = "https://www.flannels.com/women/clothing"

    for page_num in range(1, max_pages + 1):
        fragment = f"#dcp={page_num}&dppp=59&OrderBy=rank"
        full_url = base_url + fragment

        print(f"\n🌐 Visiting: {full_url}")
        try:
            page.goto(base_url, timeout=60000, wait_until="domcontentloaded")
            page.evaluate(f"window.location.hash = '{fragment}'")
            page.wait_for_timeout(3000)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_selector("li.plp-product-card", timeout=15000)
        except Exception as e:
            print(f"⚠️ Failed to load page {page_num}: {e}")
            continue

        cards = page.query_selector_all("li.plp-product-card")
        print(f"🧾 Found {len(cards)} product cards on page {page_num}")

        for card in cards:
            image_url = card.get_attribute("li-imageurl")
            if not image_url:
                img = card.query_selector("img")
                image_url = img.get_attribute("src") if img else None

            if not image_url or "flannels.com" not in image_url:
                continue
            if image_url.startswith("//"):
                image_url = "https:" + image_url
            if image_url.startswith("data:") or image_url in seen:
                continue
            seen.add(image_url)

            product_path = card.get_attribute("li-url")
            product_url = f"https://www.flannels.com{product_path}" if product_path else image_url

            title = card.get_attribute("li-name") or image_url.split("/")[-1].split("?")[0]

            print(f"🔗 Found image: {image_url}")
            print(f"➡️ Product URL: {product_url}")
            print(f"🧠 Embedding: {image_url}")

            vector = None
            for attempt in range(3):
                vector = embed_image_from_url(image_url)
                if vector is not None:
                    print("✅ Embed successful")
                    break
                print(f"❌ Embed error on attempt {attempt + 1}/3")
                time.sleep(1)

            if vector is None:
                print("⚠️ Skipping product, embedding failed.")
                continue

            product_id = str(uuid.uuid4())
            product = {
                "id": product_id,
                "brand": "Flannels",
                "title": title.strip(),
                "url": product_url,
                "image_url": image_url
            }

            insert_vector(product_id, vector, product)
            products.append(product)

            time.sleep(random.uniform(0.5, 1.2))

        # Pause before next simulated page
        time.sleep(random.uniform(2.0, 3.5))

    return products


def main(reset_qdrant=False):
    if reset_qdrant:
        setup_qdrant()
    # rest unchanged

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US"
        )
        page = context.new_page()

        print("=== Scraping Flannels ===")
        products = scrape_flannels(page)
        insert_products(products)

        print(f"\n✅ Scraped {len(products)} unique items from Flannels")
        browser.close()


if __name__ == "__main__":
    main()
