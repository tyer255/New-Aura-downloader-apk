import json

raw_json = '{"success":true,"title":"Instagram Post","thumbnail":"thumb_url","url":"/api/url","filename":"snapsave-app.mp4","mediaType":"image","media":[{"type":"image","url":"/api/url"}]}'
data = json.loads(raw_json)

rootFilename = data.get("filename", "")
print(f"rootFilename: {rootFilename}")
