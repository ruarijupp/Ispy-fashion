import csv
import uuid
from backend.embedder import embed_image_from_url
from app.db import insert_vector

# 🔧 Adjust paths if needed
FILES = {
    "farfetch": "data/farfetch.csv",
    "flannels": "data/flannels.csv"
}

def load_csv(filepath):
    with open(filepath, newline='', encoding="utf-8") as f:
        return list(csv.DictReader(f))

def clean_row(row):
    return {
        "id": row.get("id") or str(uuid.uuid4()),
        "brand": row.get("brand") or "Unknown",
        "title": row.get("title") or "Untitled",
        "url": row.get("url"),
        "image_url": row.get("image_url")
    }

def process_file(name, filepath):
    print(f"\n📦 Processing: {name} from {filepath}")
    rows = load_csv(filepath)
    success = 0
    skipped = 0

    for row in rows:
        try:
            product = clean_row(row)
            vector = embed_image_from_url(product["image_url"])
            if not vector:
                print(f"⚠️ Skipped (no embedding): {product['title']}")
                skipped += 1
                continue
            insert_vector(vector, payload=product)
            success += 1
        except Exception as e:
            print(f"❌ Error on row: {e}")
            skipped += 1

    print(f"✅ Done: {success} embedded, {skipped} skipped.")

def main():
    for name, filepath in FILES.items():
        process_file(name, filepath)

if __name__ == "__main__":
    main()
