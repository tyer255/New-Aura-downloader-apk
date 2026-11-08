import re
import json

html = '''<script id="__NEXT_DATA__" type="application/json">{"props":{"pageProps":{"state":{"data":{"entity":{"type":"track","name":"Never Gonna Give You Up","uri":"spotify:track:4cOdK2wGLETKBW3PvgPWqT","id":"4cOdK2wGLETKBW3PvgPWqT","title":"Never Gonna Give You Up","artists":[{"name":"Rick Astley","uri":"spotify:artist:0gxyHStUsqpMadRV0Di1Qt"}],"releaseDate":{"isoString":"1987-11-12T00:00:00Z"},"duration":213573,"isPlayable":true,"playabilityReason":"PLAYABLE","isExplicit":false,"isNineteenPlus":false,"contentRatings":{"labels":[]},"audioPreview":{"url":"https://p.scdn.co/mp3-preview/b4c682084c3fd05538726d0a126b7e14b6e92c83"},"hasVideo":false,"relatedEntityUri":"spotify:artist:0gxyHStUsqpMadRV0Di1Qt","visualIdentity":{"backgroundBase":{"alpha":255,"blue":119,"green":89,"red":0},"backgroundTintedBase":{"alpha":255,"blue":81,"green":53,"red":0},"textBase":{"alpha":255,"blue":255,"green":255,"red":255},"textBrightAccent":{"alpha":255,"blue":255,"green":255,"red":255},"textSubdued":{"alpha":255,"blue":251,"green":217,"red":125},"image":[{"url":"https://image-cdn-ak.spotifycdn.com/image/ab67616d00001e02baf89eb11ec7c657805d2da0","maxHeight":300,"maxWidth":300},{"url":"https://image-cdn-ak.spotifycdn.com/image/ab67616d00004851baf89eb11ec7c657805d2da0","maxHeight":64,"maxWidth":64},{"url":"https://image-cdn-ak.spotifycdn.com/image/ab67616d0000b273baf89eb11ec7c657805d2da0","maxHeight":640,"maxWidth":640}]}},"embeded_entity_uri":"spotify:track:4cOdK2wGLETKBW3PvgPWqT"}}}}}}'''

match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
if match:
    s = match.group(1)
    print("Matched script!")
else:
    print("No script match")
