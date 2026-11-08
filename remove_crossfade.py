import re

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    content = f.read()

content = content.replace('.crossfade(true)', '')

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(content)

print("Removed crossfade")
