with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "Icon(iconVector" in line or "Icon(Icons.Filled.Download" in line:
        print(f"Line {i}: {line.strip()}")
        print(f"Before {i-1}: {lines[i-1].strip()}")
        print(f"Before {i-2}: {lines[i-2].strip()}")
