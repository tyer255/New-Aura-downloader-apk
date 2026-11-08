import re

with open('app/src/main/java/com/example/MainActivity.kt', 'r') as f:
    content = f.read()

# Fix the merged header at top
content = content.replace("import android.media.MediaPlayerpackage com.exampleimport android.Manifest", "package com.example\n\nimport android.media.MediaPlayer\nimport android.Manifest")

# Fix any other merged imports if any
content = re.sub(r'import ([a-zA-Z0-9_\.]+)import ', r'import \1\nimport ', content)

with open('app/src/main/java/com/example/MainActivity.kt', 'w') as f:
    f.write(content)

