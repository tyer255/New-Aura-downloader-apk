import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    main_code = f.read()

with open("player_fixed.txt", "r") as f:
    player_fixed = f.read()

start_idx = main_code.find("@Composable\nfun SpotifyMusicPlayer")
if start_idx != -1:
    brackets = 0
    in_fun = False
    end_idx = -1
    for i in range(start_idx, len(main_code)):
        if main_code[i] == '{':
            brackets += 1
            in_fun = True
        elif main_code[i] == '}':
            brackets -= 1
        
        if in_fun and brackets == 0:
            end_idx = i + 1
            break
            
    if end_idx != -1:
        main_code = main_code[:start_idx] + player_fixed + main_code[end_idx:]

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(main_code)
