import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

pattern1 = r'(\s*Spacer\(modifier = Modifier.height\(24.dp\)\)\s*)onClick = \{\s*if \(url\.isNotEmpty\(\)\) \{'
repl1 = r'\1Button(\n                onClick = {\n                    if (url.isNotEmpty()) {'
content = re.sub(pattern1, repl1, content)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
