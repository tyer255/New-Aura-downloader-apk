import re

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    lines = f.readlines()

new_lines = []
skip_next = False

for i, line in enumerate(lines):
    if skip_next:
        skip_next = False
        continue
    
    new_lines.append(line)
    
    if re.match(r'^\s*\}\s*$', line):
        if i + 1 < len(lines) and lines[i+1] == line:
            skip_next = True

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.writelines(new_lines)

