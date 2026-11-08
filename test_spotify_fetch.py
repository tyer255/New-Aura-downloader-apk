import urllib.request
import json
import re

def test_url(url):
    print("Testing:", url)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    # 1. Test oembed
    oembed_url = f"https://open.spotify.com/oembed?url={url}"
    try:
        req = urllib.request.Request(oembed_url, headers=headers)
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            print("  OEmbed Title:", data.get('title'))
            print("  OEmbed Thumbnail:", data.get('thumbnail_url'))
            print("  OEmbed Type:", data.get('type'))
    except Exception as e:
        print("  OEmbed Error:", e)

    # 2. Test embed HTML
    m = re.search(r'spotify\.com\/(?:[a-zA-Z0-9-]+\/)?(track|playlist|album)\/([a-zA-Z0-9]{22})', url)
    if m:
        item_type, item_id = m.group(1), m.group(2)
        embed_url = f"https://open.spotify.com/embed/{item_type}/{item_id}"
        try:
            req = urllib.request.Request(embed_url, headers=headers)
            with urllib.request.urlopen(req) as res:
                html = res.read().decode('utf-8')
                entity_m = re.search(r'"entity":(\{.*?\}),"', html)
                if entity_m:
                    entity_json = json.loads(entity_m.group(1))
                    print("  Entity Name:", entity_json.get('name'))
                    if 'tracks' in entity_json:
                        print("  Tracks count:", len(entity_json['tracks']))
                    elif 'track' in entity_json:
                        print("  Single track found")
                else:
                    # look for initial state json
                    state_m = re.search(r'<script id="session" type="application/json">(.*?)</script>', html)
                    if state_m:
                        print("  Found session script")
                    else:
                        print("  No entity regex match in embed HTML length:", len(html))
        except Exception as e:
            print("  Embed Error:", e)

test_url("https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT")
test_url("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
test_url("https://open.spotify.com/album/4a3Y19Vo2R1L4X3S3Gy13G")

