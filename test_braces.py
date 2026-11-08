with open("app/src/main/java/com/auradownloader/app/MainActivity.kt") as f:
    lines = f.readlines()

depth = 0
for i, line in enumerate(lines):
    depth += line.count('{') - line.count('}')
    if depth < 0:
        print(f"Negative depth at line {i+1}: {line.strip()}")
        depth = 0

print(f"Final depth: {depth}")
