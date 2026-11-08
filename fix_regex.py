import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

content = content.replace('val regex = Regex(""""\\\\[(\\\\d+):(\\\\d+\\\\.\\\\d+)\\\\](.*)""")', 'val regex = Regex("\\\\[(\\\\d+):(\\\\d+\\\\.\\\\d+)\\\\](.*)")')

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
