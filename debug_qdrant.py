from qdrant_client import QdrantClient

COLLECTION_NAME = "fashion_items"
client = QdrantClient(url="http://localhost:6333")  # or your Qdrant Cloud URL

# STEP 1: Count vectors
print("\n🔢 --- COUNT ---")
count = client.count(collection_name=COLLECTION_NAME)
print(f"✅ Total vectors in '{COLLECTION_NAME}': {count.count}")

# STEP 2: Inspect first vector
print("\n🔍 --- SAMPLE VECTOR ---")
results, _ = client.scroll(
    collection_name=COLLECTION_NAME,
    limit=1,
    with_payload=True,
    with_vectors=True
)

if results:
    first = results[0]
    vector = getattr(first, 'vector', None)

    if vector:
        print(f"🧠 Vector length: {len(vector)}")
        print(f"🧠 First values: {vector[:5]}")
        print(f"📦 Payload: {first.payload}")
    else:
        print("⚠️ No vector found in first result. Something is wrong with the insert.")
else:
    print("❌ No results found in scroll")
