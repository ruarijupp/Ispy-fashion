from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from app.embedder import embed_uploaded_image
from qdrant_client import QdrantClient

COLLECTION_NAME = "fashion_items"
client = QdrantClient("localhost", port=6333)

app = FastAPI()

@app.post("/search")
async def search(file: UploadFile = File(...)):
    # Get CLIP embedding of uploaded image
    vec = embed_uploaded_image(file)

    # Search in Qdrant
    hits = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vec,
        limit=5
    )

    results = [
        {
            "id": hit.id,
            "score": hit.score,
            "payload": hit.payload
        }
        for hit in hits
    ]

    return {"results": results}


@app.post("/search-html", response_class=HTMLResponse)
async def search_html(file: UploadFile = File(...)):
    vec = embed_uploaded_image(file)
    hits = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vec,
        limit=5
    )

    html = "<h2>Top Matches:</h2><div style='display: flex; gap: 20px; flex-wrap: wrap;'>"
    for hit in hits:
        payload = hit.payload
        html += f"""
            <div style="text-align: center;">
                <img src="{payload['image_url']}" alt="{payload['title']}" width="200"/><br/>
                <strong>{payload['title']}</strong><br/>
                {payload['price']}<br/>
                <a href="{payload['link']}" target="_blank">View Product</a>
            </div>
        """
    html += "</div>"
    return HTMLResponse(content=html)
