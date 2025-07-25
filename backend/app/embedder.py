import requests
from PIL import Image
from io import BytesIO
import torch
import clip
import time
import os

# Load CLIP model
model, preprocess = clip.load("ViT-B/32")

def embed_image_from_url(url, retries=3, timeout=30):
    print(f"🧠 Embedding from URL: {url}")

    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            image = Image.open(BytesIO(response.content)).convert("RGB")
            image_input = preprocess(image).unsqueeze(0)

            with torch.no_grad():
                image_features = model.encode_image(image_input)

            print("✅ Embed successful (URL)")
            return image_features.squeeze(0).cpu().numpy()

        except Exception as e:
            print(f"❌ Embed error on attempt {attempt + 1}/{retries}: {e}")
            time.sleep(2 * (attempt + 1))  # exponential backoff

    print("⚠️ Skipping: embedding failed from URL.")
    return None

def embed_image_from_file(path):
    try:
        print(f"🧠 Embedding from file: {os.path.basename(path)}")

        with open(path, "rb") as f:
            image = Image.open(f).convert("RGB")
            image_input = preprocess(image).unsqueeze(0)

        with torch.no_grad():
            image_features = model.encode_image(image_input)

        print("✅ Embed successful (file)")
        return image_features.squeeze(0).cpu().numpy()

    except Exception as e:
        print(f"❌ Failed to embed image from file: {e}")
        return None
