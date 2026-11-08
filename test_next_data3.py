import urllib.request
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def test_url(url):
    print("=== URL:", url)
    m = re.search(r'spotify\.com\/(?:[a-zA-Z0-9-]+\/)?(track|playlist|album|artist)\/([a-zA-Z0-9]{22})', url)
    if not m:
        print("No regex match for url:", url)
        return
    kind, item_id = m.group(1), m.group(2)
    embed_url = f"https://open.spotify.com/embed/{kind}/{item_id}"
    req = urllib.request.Request(embed_url, headers=headers)
    try:
        with urllib.request.urlopen(req) as res:
            html = res.read().decode('utf-8', errors='ignore')
            m_data = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
            if m_data:
                data = json.loads(m_data.group(1))
                entity = data.get('props', {}).get('pageProps', {}).get('state', {}).get('data', {}).get('entity', {})
                name = entity.get('title') or entity.get('name') or "Spotify Item"
                subtitle = entity.get('subtitle') or ""
                cover_art = entity.get('coverArt', {})
                sources = cover_art.get('sources', [])
                img_url = sources[0].get('url') if sources else ""
                track_list = entity.get('trackList', [])
                print(f" Kind: {kind} | Title: {name} | Subtitle: {subtitle} | Img: {img_url}")
                print(f" Track Count: {len(track_list)}")
                for idx, t in enumerate(track_list[:3], 1):
                    dur_sec = (t.get('duration', 0) or 0) // 1000
                    dur_str = f"{dur_sec // 60}:{dur_sec % 60:02d}" if dur_sec > 0 else ""
                    print(f"   #{idx}: {t.get('title')} - {t.get('subtitle')} [{dur_str}]")
            else:
                print(" No __NEXT_DATA__ script found")
    except Exception as e:
        print(" Error fetching embed:", e)

test_url("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
test_url("https://open.spotify.com/album/4a3Y19Vo2R1L4X3S3Gy13G")
test_url("https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT")

