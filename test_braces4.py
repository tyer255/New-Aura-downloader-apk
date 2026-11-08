with open("app/src/main/java/com/auradownloader/app/MainActivity.kt") as f:
    lines = f.readlines()

depth = 0
for i, line in enumerate(lines):
    prev_depth = depth
    depth += line.count('{') - line.count('}')
    
    if prev_depth == 0 and "fun " in line and "(" in line:
        print(f"Top-level function at line {i+1}: {line.strip()}")
    elif prev_depth == 0 and "class " in line and "{" in line:
        print(f"Top-level class at line {i+1}: {line.strip()}")
    elif prev_depth == 0 and "object " in line and "{" in line:
        print(f"Top-level object at line {i+1}: {line.strip()}")

