with open("app/src/main/java/com/auradownloader/app/MainActivity.kt") as f:
    lines = f.readlines()

depth = 0
for i, line in enumerate(lines):
    depth += line.count('{') - line.count('}')
    if "fun MainScreen" in line or "fun HomeScreen" in line or "class MainActivity" in line or "fun Platform3DIcon" in line:
        print(f"Line {i+1}: {line.strip()} (Depth after line: {depth})")
    
