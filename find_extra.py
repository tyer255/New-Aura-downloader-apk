with open('app/src/main/java/com/auradownloader/app/MainActivity.kt') as f:
    lines = f.readlines()

stack = []
for i, line in enumerate(lines):
    # ignore strings
    line = line.replace('"{""', 'STRING').replace('"}"', 'STRING')
    for char in line:
        if char == '{':
            stack.append(i+1)
        elif char == '}':
            if stack:
                stack.pop()
            else:
                print(f"Extra closing brace at line {i+1}")
