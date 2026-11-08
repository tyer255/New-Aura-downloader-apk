import urllib.request, json, re
trackId = '0wHYuCTWPntEgWiUVED4wB'
req = urllib.request.Request(f'https://open.spotify.com/embed/track/{trackId}', headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode()
        entityMatch = re.search(r'"audioPreview":\{"url":"([^"]+)"', html)
        if entityMatch:
            print("Preview URL:", entityMatch.group(1))
        else:
            print("No audioPreview found")
except Exception as e:
    print('Error:', e)
