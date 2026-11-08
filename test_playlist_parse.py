import urllib.request
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def parse_spotify(url):
    print("=== Testing URL:", url)
    encoded_url = urllib.parse.quote(url, safe='')
    
    # 1. oEmbed
    title = "Spotify Item"
    thumbnail = ""
    try:
        req = urllib.request.Request(f"https://open.spotify.com/oembed?url={encoded_url}", headers=headers)
        with urllib.request.urlopen(req) as res:
            ojson = json.loads(res.read().decode())
            title = ojson.get("title", title)
            thumbnail = ojson.get("thumbnail_url", thumbnail)
            print(f"oEmbed Title: '{title}', Thumbnail: '{thumbnail}'")
    except Exception as e:
        print("oEmbed error:", e)

    # 2. Embed HTML
    m = re.search(r'spotify\.com\/(?:[a-zA-Z0-9-]+\/)?(track|playlist|album|artist)\/([a-zA-Z0-9]{22})', url)
    tracks = []
    if m:
        kind, item_id = m.group(1), m.group(2)
        embed_url = f"https://open.spotify.com/embed/{kind}/{item_id}"
        print("Fetching embed URL:", embed_url)
        try:
            req = urllib.request.Request(embed_url, headers=headers)
            with urllib.request.urlopen(req) as res:
                html = res.read().decode('utf-8', errors='ignore')
                
                # Try finding JSON data in html
                # Regex for "name":"..." and "artists" or track lists
                # or script tag with resource entity
                resource_m = re.search(r'"resource":(\{.*?\}),"', html) or re.search(r'"entity":(\{.*?\}),"', html)
                if resource_m:
                    print("Found resource/entity match")
                else:
                    # Search for script containing tracks or names
                    # Let's see if we can find tracks via regex patterns in html
                    # e.g., "title":"..." or "name":"..."
                    track_matches = re.findall(r'"name":"([^"]+)","artists":\[(.*?)\]', html)
                    for t_name, a_block in track_matches[:15]:
                        a_names = re.findall(r'"name":"([^"]+)"', a_block)
                        artist_str = ", ".join(a_names) if a_names else ""
                        tracks.append((t_name, artist_str))
                    
                    if not tracks:
                        # Fallback simple name matching
                        simple_names = re.findall(r'"title":"([^"]+)".*?"subtitle":"([^"]+)"', html)
                        for sn, ss in simple_names[:15]:
                            tracks.append((sn, ss))

        except Exception as e:
            print("Embed fetch error:", e)

    print(f"Parsed {len(tracks)} tracks:")
    for idx, (tn, ta) in enumerate(tracks[:10], 1):
        print(f"  #{idx} {tn} - {ta}")

parse_spotify("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
parse_spotify("https://open.spotify.com/album/4a3Y19Vo2R1L4X3S3Gy13G")
parse_spotify("https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT")
