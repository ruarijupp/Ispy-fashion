from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from app.embedder import embed_image_from_url
import json

client = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "fashion_items"

def setup_qdrant():
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=512, distance=Distance.COSINE)
    )

def insert_products():
    with open("app/products.json") as f:
        products = json.load(f)

    points = []
    for i, product in enumerate(products):
        vec = embed_image_from_url(product["image_url"])
        points.append(PointStruct(
            id=i,
            vector=vec,
            payload=product
        ))

    client.upsert(collection_name=COLLECTION_NAME, points=points)

def search_vector(vector, k=5):
    return client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector.tolist(),
        limit=k
    )
