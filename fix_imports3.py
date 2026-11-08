import re

with open('app/src/main/java/com/example/MainActivity.kt', 'r') as f:
    text = f.read()

# Replace package com.exampleimport
text = re.sub(r'package com\.example\s*import', 'package com.example\n\nimport', text)
# Ensure every import is on its own line
text = re.sub(r'(import [a-zA-Z0-9_\.]+)', r'\1\n', text)

with open('app/src/main/java/com/example/MainActivity.kt', 'w') as f:
    f.write(text)

