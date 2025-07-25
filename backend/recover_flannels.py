import re
import pandas as pd

# Read the binary .db file
with open("products.db", "rb") as f:
    raw = f.read().decode("utf-8", errors="ignore")

# Filter lines that contain Flannels product data
lines = [line for line in raw.splitlines() if "flannels.com" in line]

# Use regex to extract id, brand, title, url, and image_url
pattern = re.compile(
    r"(?P<id>[a-f0-9\-]{36})"
    r"(?P<brand>Flannels)"
    r"(?P<title>.+?)"
    r"(https://www\.flannels\.com/[^\s#]+)"
    r".*?(https://www\.flannels\.com/images/products/[^\s]+\.jpg)"
)

records = []
for line in lines:
    match = pattern.search(line)
    if match:
        groups = match.groups()
        records.append({
            "id": groups[0],
            "brand": groups[1],
            "title": groups[2].strip(),
            "url": groups[3],
            "image_url": groups[4],
        })

# Save to CSV
df = pd.DataFrame(records)
df.to_csv("flannels_recovered.csv", index=False)

print(f"✅ Extracted {len(df)} Flannels items to flannels_recovered.csv")
