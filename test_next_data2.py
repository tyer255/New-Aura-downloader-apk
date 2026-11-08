import urllib.request
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

url = "https://open.spotify.com/embed/playlist/37i9dQZF1DXcBWIGoYBM5M"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as res:
    html = res.read().decode('utf-8', errors='ignore')

m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
if m:
    data = json.loads(m.group(1))
    st_data = data['props']['pageProps']['state']['data']
    print("Keys in state.data:", st_data.keys())
    entity = st_data.get('entity', {})
    print("Entity name:", entity.get('name'))
    print("Entity keys:", entity.keys())
    track_list = entity.get('trackList', [])
    print("Track list length:", len(track_list))
    for idx, tr in enumerate(track_list[:10], 1):
        title = tr.get('title') or tr.get('name')
        subtitle = tr.get('subtitle') or tr.get('artist')
        duration = tr.get('duration')
        print(f"  #{idx}: {title} -- {subtitle} ({duration}ms)")
