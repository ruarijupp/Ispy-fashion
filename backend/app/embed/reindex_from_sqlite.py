import os
import sqlite3
from qdrant_client import QdrantClient
from qdrant_client.models import CountRequest
from backend.app.db import insert_vector
from backend.app.embedder import embed_image_from_url

DATA_FOLDER = "data"
DB_FILES = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".db")]

client = QdrantClient("localhost", port=6333)

def reindex_sqlite_db(db_path):
    print(f"\n📦 Reindexing from: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, image_url, title, url, price FROM products")
        rows = cursor.fetchall()

        success = 0
        for row in rows:
            id, image_url, title, url, price = row
            payload = {
                "title": title,
                "url": url,
                "price": price,
                "image_url": image_url
            }

            try:
                insert_vector(id, image_url, payload)
                success += 1
                print(f"✅ Inserted: {title[:30]}... ({image_url})")
            except Exception as e:
                print(f"❌ Failed to insert {id}: {e}")

        print(f"🎯 {success}/{len(rows)} vectors saved from {os.path.basename(db_path)}")
    except Exception as e:
        print(f"❌ Error reading {db_path}: {e}")
    finally:
        conn.close()

    # Check current Qdrant count
    try:
        count = client.count(collection_name="fashion_items", count_request=CountRequest(exact=True)).count
        print(f"📊 Total vectors in Qdrant after {os.path.basename(db_path)}: {count}")
    except Exception as e:
        print(f"⚠️ Could not retrieve Qdrant count: {e}")

if __name__ == "__main__":
    for file in DB_FILES:
        full_path = os.path.join(DATA_FOLDER, file)
        reindex_sqlite_db(full_path)
