import urllib.request
import urllib.parse
import json

url = "https://aura-downloader-yg40.onrender.com/api/lyrics?title=" + urllib.parse.quote("Never Gonna Give You Up") + "&artist=" + urllib.parse.quote("Rick Astley")
req = urllib.request.Request(url)
response = urllib.request.urlopen(req)
data = json.loads(response.read())
print(json.dumps(data, indent=2))
