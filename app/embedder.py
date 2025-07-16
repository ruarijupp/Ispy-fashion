import torch
import clip
from PIL import Image
from io import BytesIO
import requests

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

def embed_image_from_url(url):
    # Add headers to avoid 403/HTML responses
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    # Raise error if image request fails
    if response.status_code != 200:
        raise Exception(f"Image download failed: {response.status_code} - {url}")

    image = Image.open(BytesIO(response.content)).convert("RGB")
    image_input = preprocess(image).unsqueeze(0).to(device)

    with torch.no_grad():
        embedding = model.encode_image(image_input).cpu().numpy()[0]
    return embedding

def embed_uploaded_image(file):
    image = Image.open(file.file).convert("RGB")
    image_input = preprocess(image).unsqueeze(0).to(device)

    with torch.no_grad():
        embedding = model.encode_image(image_input).cpu().numpy()[0]
    return embedding
