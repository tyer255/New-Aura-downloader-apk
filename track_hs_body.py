with open('app/src/main/java/com/auradownloader/app/MainActivity.kt') as f:
    lines = f.readlines()

depth = 0
started = False
for i, line in enumerate(lines):
    if not started:
        if i >= 1000 and "{" in line:
            # wait until the actual opening brace of HomeScreen
            if "fun HomeScreen" in line or (i > 1003 and "{" in line and "}" not in line):
                 started = True
                 depth += line.count('{') - line.count('}')
    else:
        # naive string/comment strip
        import re
        c_line = re.sub(r'//.*', '', line)
        c_line = re.sub(r'"([^"\\]|\\.)*"', '""', c_line)
        depth += c_line.count('{') - c_line.count('}')
        if depth <= 0:
            print(f"Body ended at line {i+1}: {line.strip()}")
            if depth < 0:
                print("Negative depth!")
            break
