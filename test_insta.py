import urllib.request
import json
req = urllib.request.Request(
    'https://aura-downloader-yg40.onrender.com/api/download',
    data=json.dumps({'url': 'https://www.instagram.com/p/C-V_aF3IKq4/'}).encode(),
    headers={'Content-Type': 'application/json'}
)
res = urllib.request.urlopen(req)
print(res.read().decode())
