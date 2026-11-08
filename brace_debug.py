with open('app/src/main/java/com/auradownloader/app/MainActivity.kt') as f:
    lines = f.readlines()

stack = []
for i, line in enumerate(lines):
    for char in line:
        if char == '{':
            stack.append((i+1, line.strip()))
        elif char == '}':
            if stack:
                stack.pop()

if stack:
    for s in stack:
        print(f"Unclosed at {s[0]}: {s[1]}")
