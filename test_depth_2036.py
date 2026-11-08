with open('app/src/main/java/com/auradownloader/app/MainActivity.kt') as f:
    code = f.read()
depth = 0
for i, line in enumerate(code.split('\n')):
    depth += line.count('{') - line.count('}')
    if i + 1 == 2036:
        print(f"Depth at 2036 is {depth}")
        break
