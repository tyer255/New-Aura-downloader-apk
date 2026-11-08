with open('app/src/main/java/com/auradownloader/app/MainActivity.kt') as f:
    code = f.read()

i = 0
depth = 0
line_num = 1
while i < len(code):
    if code[i:i+3] == '"""':
        i += 3
        while i < len(code) and code[i:i+3] != '"""':
            if code[i] == '\n': line_num += 1
            i += 1
        i += 3
    elif code[i] == '"':
        i += 1
        while i < len(code) and code[i] != '"':
            if code[i] == '\\': i += 2
            else:
                if code[i] == '\n': line_num += 1
                i += 1
        i += 1
    elif code[i] == "'":
        i += 1
        while i < len(code) and code[i] != "'":
            if code[i] == '\\': i += 2
            else:
                if code[i] == '\n': line_num += 1
                i += 1
        i += 1
    elif code[i:i+2] == '//':
        while i < len(code) and code[i] != '\n': i += 1
    elif code[i:i+2] == '/*':
        while i < len(code) and code[i:i+2] != '*/':
            if code[i] == '\n': line_num += 1
            i += 1
        i += 2
    elif code[i] == '\n':
        line_num += 1
        i += 1
    elif code[i] == '{':
        depth += 1
        i += 1
    elif code[i] == '}':
        depth -= 1
        i += 1
    else:
        i += 1
print(f"Final Depth: {depth}")
