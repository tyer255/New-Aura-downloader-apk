with open("app/src/main/java/com/auradownloader/app/MainActivity.kt") as f:
    lines = f.readlines()

depth = 0
for i, line in enumerate(lines):
    depth += line.count('{') - line.count('}')
    if depth == 1 and line.count('{') > 0 and (line.strip().startswith("fun ") or line.strip().startswith("class ") or line.strip().startswith("suspend fun ")):
        print(f"Top-level block started at {i+1}: {line.strip()}")

