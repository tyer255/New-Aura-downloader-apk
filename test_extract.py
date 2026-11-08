import requests
import json

url = "https://youtube.com/shorts/xn0WXyZUhzM"
# Simulate fetchFastMeta
fast_meta_url = f"https://www.youtube.com/oembed?url={url}&format=json"
fast_meta_res = requests.get(fast_meta_url).json()
print("FastMeta title:", fast_meta_res.get("title"))

# Simulate fetchBackendApi
backend_res = requests.post("https://aura-downloader-yg40.onrender.com/api/download", json={"url": url}).json()
print("Backend success:", backend_res.get("success"))
qualities = backend_res.get("qualities", [])
print("Backend qualities count:", len(qualities))
for q in qualities:
    print(q.get("label"))
