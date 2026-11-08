import urllib.request, json, urllib.parse

def check(trackId_str):
    url = f"https://aura-downloader-yg40.onrender.com/api/spotify-resolve?trackId={urllib.parse.quote(trackId_str)}&title=Aarzu&artist=Noor&artists=Noor%2CKhan%2CMadhurxo&durationMs=187567&isrc="
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode())
            print(f"TrackId {trackId_str} resolved to:", res.get("videoId"))
    except Exception as e:
        print('Error:', e)

check("0wHYuCTWPntEgWiUVED4wB?si=0Zy-UpIKTmOrdHhjN_4gSw")
check("0wHYuCTWPntEgWiUVED4wB")
