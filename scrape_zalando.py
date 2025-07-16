from playwright.sync_api import sync_playwright
from app.embedder import embed_image_from_url
from app.db import client, COLLECTION_NAME
import time
import uuid

brands = [
    "Nanushka", "Staud", "Reformation", "Sézane", "Faithfull the Brand", "House of CB",
    "Tory Burch", "Paloma Wool", "Djerf Avenue", "With Jéan", "Musier Paris", "Rouje", "Rat & Boa",
    "Aya Muse", "Les Coyotes de Paris", "Stine Goya", "Gimaguas", "Agolde", "Aritzia", "For Love & Lemons",
    "Christopher Esber", "Camilla and Marc", "Bec + Bridge", "Sir the Label", "Sandro", "Maje", "Arket"
]

def format_brand(brand):
    return brand.lower().replace(" ", "-").replace("&", "").replace("é", "e")

def scrape_brand(playwright, brand):
    browser = playwright.chromium.launch(headless=False, slow_mo=200)
    page = browser.new_page()

    url = f"https://www.zalando.co.uk/{format_brand(brand)}/"
    print(f"🔗 Opening {url}")
    page.goto(url, timeout=30000)

    try:
        page.wait_for_selector("article", timeout=10000)
    except:
        print(f"⚠️ No articles found for {brand}")
        browser.close()
        return []

    products = []
    cards = page.query_selector_all("article")[:30]

    for card in cards:
        try:
            img_tag = card.query_selector("img")
            img_url = img_tag.get_attribute("src") or img_tag.get_attribute("data-src")
            if not img_url or "data:image" in img_url:
                print(f"⚠️ Skipping invalid image URL: {img_url}")
                continue

            title = img_tag.get_attribute("alt") or "No title"
            price_tag = card.query_selector("[data-testid='price']") or card.query_selector("span")
            price = price_tag.inner_text().strip() if price_tag else "N/A"
            link_tag = card.query_selector("a")
            href = link_tag.get_attribute("href") if link_tag else None
            link = f"https://www.zalando.co.uk{href}" if href else "#"

            vec = embed_image_from_url(img_url)

            products.append({
                "id": str(uuid.uuid4()),  # Qdrant-compatible UUID
                "vector": vec.tolist(),
                "payload": {
                    "title": title,
                    "image_url": img_url,
                    "price": price,
                    "link": link,
                    "brand": brand
                }
            })

            print(f"✅ {title}")
            time.sleep(0.3)

        except Exception as e:
            print(f"❌ Error parsing product: {e}")

    browser.close()
    return products

def insert_brand_products():
    with sync_playwright() as playwright:
        for brand in brands:
            print(f"\n🔍 Scraping {brand}...")
            points = scrape_brand(playwright, brand)
            print(f"➡️ Found {len(points)} products.")
            if points:
                client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=points
                )
                print(f"✅ Upserted to Qdrant.")
            else:
                print(f"⚠️ No products collected for {brand}.")

if __name__ == "__main__":
    insert_brand_products()
