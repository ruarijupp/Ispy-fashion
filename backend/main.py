from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from embedder import embed_image_from_file, embed_text
from qdrant_client import QdrantClient
import tempfile
import os

# Qdrant Cloud connection
COLLECTION_NAME = "fashion_items"
client = QdrantClient(
    url="https://a4138a07-f277-4fe7-aaeb-074af7ae938b.eu-west-2-0.aws.cloud.qdrant.io:6333",
    api_key=os.getenv("QDRANT_API_KEY")
)

# FastAPI app setup
app = FastAPI()

# CORS middleware to allow Netlify frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://glittering-gecko-87cbe9.netlify.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Search endpoint (JSON response)
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
        limit=12,
        with_payload=True
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

# Search endpoint (HTML preview response)
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
        limit=12,
        with_payload=True
    )

    if not hits:
        return HTMLResponse("<p>No results found. Try a clearer or different image.</p>")

    html = """
    <h2>Top Matches:</h2>
    <div style='display: flex; flex-wrap: wrap; gap: 24px;'>
    """

    for hit in hits:
        p = hit.payload
        image_url = p.get("image_url", "")
        url = p.get("url", "#")

        html += f"""
            <a href="{url}" target="_blank" style="display: block; width: 200px;">
                <img src="{image_url}" style="width: 100%; height: auto; object-fit: contain; border-radius: 6px;" />
            </a>
        """

    html += "</div>"
    return HTMLResponse(html)
