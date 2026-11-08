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
    print("Keys in __NEXT_DATA__:", data.keys())
    props = data.get('props', {}).get('pageProps', {})
    print("Keys in pageProps:", props.keys())
    state = props.get('state', {})
    print("Keys in state:", state.keys())
    data_data = props.get('data', {})
    print("Keys in pageProps.data:", data_data.keys() if isinstance(data_data, dict) else type(data_data))
    if 'entity' in data_data:
        entity = data_data['entity']
        print("Entity name:", entity.get('name'))
        print("Entity type:", entity.get('type'))
        if 'trackList' in entity:
            print("Track list count:", len(entity['trackList']))
            for t in entity['trackList'][:10]:
                print("  Track:", t.get('title'), "| Subtitle:", t.get('subtitle'), "| Duration:", t.get('duration'))
