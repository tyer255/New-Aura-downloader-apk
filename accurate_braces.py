import re

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt') as f:
    raw_lines = f.readlines()

def clean_line(line):
    line = re.sub(r'//.*', '', line)
    line = re.sub(r'\"\"\"[\s\S]*?\"\"\"', '""', line)
    line = re.sub(r'"([^"\\]|\\.)*"', '""', line)
    line = re.sub(r"'([^'\\]|\\.)*'", "''", line)
    return line

depth = 0
in_multiline_comment = False
in_multiline_string = False

for i, line in enumerate(raw_lines):
    # This is still a bit naive for multiline strings across lines
    # Let's just do a simpler tokenization
    pass

def tokenize(code):
    i = 0
    depth = 0
    line_num = 1
    while i < len(code):
        if code[i:i+2] == '//':
            while i < len(code) and code[i] != '\n':
                i += 1
        elif code[i:i+2] == '/*':
            while i < len(code) and code[i:i+2] != '*/':
                if code[i] == '\n': line_num += 1
                i += 1
            i += 2
        elif code[i:i+3] == '"""':
            i += 3
            while i < len(code) and code[i:i+3] != '"""':
                if code[i] == '\n': line_num += 1
                i += 1
            i += 3
        elif code[i] == '"':
            i += 1
            while i < len(code) and code[i] != '"':
                if code[i] == '\\':
                    i += 2
                else:
                    if code[i] == '\n': line_num += 1
                    i += 1
            i += 1
        elif code[i] == '\n':
            line_num += 1
            i += 1
        elif code[i] == '{':
            depth += 1
            i += 1
        elif code[i] == '}':
            depth -= 1
            if depth < 0:
                print(f"Negative depth at line {line_num}")
                depth = 0
            i += 1
        else:
            i += 1
        
        # Check specific keywords
        if code[i-4:i] == 'fun ' or code[i-6:i] == 'class ':
            # We are at a declaration
            pass
            
    return depth

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt') as f:
    code = f.read()
    
print("Final depth:", tokenize(code))
