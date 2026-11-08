with open('app/src/main/java/com/auradownloader/app/MainActivity.kt') as f:
    lines = f.readlines()

depth = 0
for i, line in enumerate(lines):
    if i < 1000:
        continue
    
    # naive brace counting
    depth += line.count('{') - line.count('}')
    
    if depth == 0 and "}" in line:
        print(f"Depth became 0 at line {i+1}: {line.strip()}")
        break
    if depth < 0:
        print(f"Depth became negative ({depth}) at line {i+1}: {line.strip()}")
        break
