import re
with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    content = f.read()

lines = content.split('\n')
for i, line in enumerate(lines):
    if "val entityRegex =" in line:
        lines[i] = '                    val entityRegex = "\\\\"entity\\\\":(\\\\{.*?\\\\}),\\\\"".toRegex()'
    
content = '\n'.join(lines)
with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(content)
print("done")
