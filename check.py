with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "modifier = Modifier" in line and "}" in lines[i-1]:
        print(f"Suspicious line {i}: {line.strip()}")
