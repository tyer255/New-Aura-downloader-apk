with open('app/src/main/java/com/auradownloader/app/MainActivity.kt') as f:
    lines = f.readlines()

depth = 0
started = False
for i, line in enumerate(lines):
    if i < 1000: continue
    if not started:
        if "fun HomeScreen(" in line:
            started = True
    else:
        import re
        c_line = re.sub(r'//.*', '', line)
        c_line = re.sub(r'"([^"\\]|\\.)*"', '""', c_line)
        for char in c_line:
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
        print(f"{i+1:4d} | {depth:2d} | {line.strip()}")
        if depth <= 0 and i > 1012:
            break
