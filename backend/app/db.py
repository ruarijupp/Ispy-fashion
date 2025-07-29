import uuid
import sqlite3
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

DB_PATH = "products.db"
COLLECTION_NAME = "fashion_items"

# ✅ Connect to Docker Qdrant (or Qdrant Cloud if needed)
client = QdrantClient(url="http://localhost:6333")  # Change this for cloud if needed


# === SQLite local product store ===

def insert_products(products):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Drop and recreate table for clean run — adjust in prod
    c.execute("DROP TABLE IF EXISTS products")
    c.execute('''
        CREATE TABLE products (
            id TEXT PRIMARY KEY,
            brand TEXT,
            title TEXT,
            url TEXT,
            image_url TEXT
        )
    ''')

    for p in products:
        c.execute("INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?, ?)", (
            p["id"], p["brand"], p["title"], p["url"], p["image_url"]
        ))

    conn.commit()
    conn.close()


# === Qdrant vector store ===

def setup_qdrant():
    if not client.collection_exists(COLLECTION_NAME):
        print(f"🛠️ Creating Qdrant collection: {COLLECTION_NAME}")
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=512, distance=Distance.DOT)  # or COSINE
        )
    else:
        print(f"✅ Qdrant collection already exists: {COLLECTION_NAME}")


def insert_vector(id, vector, payload):
    print(f"📥 Inserting vector for: {payload.get('title')} (id: {id})")
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=id,
                vector=vector,
                payload=payload
            )
        ]
    )


# === Unified insert wrapper ===

def insert_product_to_qdrant(product, vector):
    insert_vector(
        id=str(uuid.uuid4()),         # ✅ Use valid UUID for Qdrant Docker
        vector=vector,
        payload=product               # Payload contains image_url, title, etc.
    )
