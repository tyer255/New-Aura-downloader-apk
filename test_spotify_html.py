import urllib.request
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def inspect_embed(url):
    print("=== URL:", url)
    # oembed
    oembed_url = f"https://open.spotify.com/oembed?url={url}"
    try:
        req = urllib.request.Request(oembed_url, headers=headers)
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            print("OEmbed:", json.dumps(data, indent=2))
    except Exception as e:
        print("Oembed err:", e)

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as res:
            html = res.read().decode('utf-8', errors='ignore')
            # find __NEXT_DATA__ or initial state or JSON scripts
            scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
            for s in scripts:
                if 'Spotify' in s or 'tracks' in s or 'name' in s:
                    if len(s) > 100:
                        print("Found script tag containing tracks/Spotify, len:", len(s))
                        # find track names
                        names = re.findall(r'"name":"([^"]+)"', s)
                        print("Sample names in script:", names[:10])
                        break
    except Exception as e:
        print("Embed page err:", e)

inspect_embed("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
inspect_embed("https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT")
