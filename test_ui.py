import re
with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()
idx = content.find("fun SpotifyMusicPlayer")
if idx != -1:
    print(content[idx:idx+3000])
else:
    print("Not found")
