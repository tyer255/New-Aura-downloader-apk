import re

with open('app/src/main/java/com/example/MainActivity.kt', 'r') as f:
    content = f.read()

content = content.replace("kotlinx.coroutines.delay((800..2000).random().toLong())", "kotlinx.coroutines.delay((100..300).random().toLong())")

with open('app/src/main/java/com/example/MainActivity.kt', 'w') as f:
    f.write(content)
