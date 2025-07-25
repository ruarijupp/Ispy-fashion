from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.app.embedder import embed_image_from_file
from qdrant_client import QdrantClient

import tempfile

COLLECTION_NAME = "fashion_items"
client = QdrantClient("localhost", port=6333)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/search")
async def search(query: str = Form(None), file: UploadFile = File(None)):
    if file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(await file.read())
            vec = embed_image_from_file(tmp.name)
    elif query:
        vec = embed_text(query)
    else:
        return {"error": "Provide an image or text"}

    if vec is None:
        return {"error": "Failed to embed input"}

    hits = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vec,
        limit=12
    )

    return {
        "results": [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload
            }
            for hit in hits
        ]
    }


@app.post("/search-html", response_class=HTMLResponse)
async def search_html(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(await file.read())
        vec = embed_image_from_file(tmp.name)

    if vec is None:
        return HTMLResponse("<h2>❌ Failed to embed image</h2>")

    hits = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vec,
        limit=5
    )

    html = "<h2>Top Matches:</h2><div style='display: flex; gap: 20px; flex-wrap: wrap;'>"
    for hit in hits:
        p = hit.payload
        html += f"""
            <div style="text-align: center;">
                <img src="{p.get('image_url', '')}" alt="{p.get('title', 'No Title')}" width="200"/><br/>
                <strong>{p.get('title', 'No Title')}</strong><br/>
                {p.get('price', '')}<br/>
                <a href="{p.get('url', '#')}" target="_blank">View Product</a>
            </div>
        """
    html += "</div>"
    return html
