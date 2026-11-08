import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

start_idx = content.find("@Composable\nfun SpotifyMusicPlayer")
if start_idx != -1:
    brackets = 0
    in_fun = False
    for i in range(start_idx, len(content)):
        if content[i] == '{':
            brackets += 1
            in_fun = True
        elif content[i] == '}':
            brackets -= 1
        
        if in_fun and brackets == 0:
            print(content[start_idx:i+1])
            break
