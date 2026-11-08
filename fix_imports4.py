import re

with open('app/src/main/java/com/example/MainActivity.kt', 'r') as f:
    text = f.read()

text = text.replace("package com.exampleimport ", "package com.example\n\nimport ")
text = text.replace("import ", "\nimport ")
text = re.sub(r'([a-zA-Z0-9_\.\*])import ', r'\1\nimport ', text)

with open('app/src/main/java/com/example/MainActivity.kt', 'w') as f:
    f.write(text)

