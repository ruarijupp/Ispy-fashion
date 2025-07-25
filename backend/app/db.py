import sqlite3
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

DB_PATH = "products.db"
COLLECTION_NAME = "fashion_items"

# === SQLite ===
def insert_products(products):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Force schema reset to prevent column mismatch
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

# === Qdrant ===
client = QdrantClient(path="qdrant_data")

def setup_qdrant():
    if not client.collection_exists(COLLECTION_NAME):
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=512, distance=Distance.DOT)
        )

def insert_vector(id, vector, payload):
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[PointStruct(id=id, vector=vector, payload=payload)]
    )

# === Unified wrapper ===
def insert_product_to_qdrant(product, vector):
    insert_vector(
        id=product["image_url"],  # Use image URL as unique ID in vector DB
        vector=vector,
        payload=product
    )
