import re
line = '            if (!clipText.isNullOrEmpty() && (clipText.startsWith("http://") || clipText.startsWith("https://")) && clipText != url) {\n'
c_line = re.sub(r'//.*', '', line)
c_line = re.sub(r'"([^"\\]|\\.)*"', '""', c_line)
print(c_line)
print("Count {:", c_line.count('{'))
