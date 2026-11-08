import urllib.request
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

url = "https://open.spotify.com/embed/playlist/37i9dQZF1DXcBWIGoYBM5M"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as res:
    html = res.read().decode('utf-8', errors='ignore')

# find initial state or script JSON
scripts = re.findall(r'<script[^>]*id="([^"]+)"[^>]*>(.*?)</script>', html, re.DOTALL)
print("Found script IDs:", [s[0] for s in scripts])

for sid, code in scripts:
    if "session" in sid or "initial" in sid or "data" in sid:
        print(f"--- Script {sid} len {len(code)} ---")
        print(code[:300])

# Also check for regex "name" or track objects
tracks = re.findall(r'\{"name":"([^"]+)".*?"artists":\[(.*?)\]', html)
print(f"Found {len(tracks)} track matches with regex")
for name, art_block in tracks[:10]:
    artists = re.findall(r'"name":"([^"]+)"', art_block)
    print(f"  Track: {name} | Artists: {', '.join(artists)}")

