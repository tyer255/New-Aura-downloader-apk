import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

pattern = r'(\s*)else \{\n(\s*)Icon\(Icons\.Filled\.ContentPaste, null, tint = textColor, modifier = Modifier\.size\(20\.dp\)\)\n(\s*)\}\n(\s*)\}'
repl = r'\1if (url.isNotEmpty()) IconButton(onClick = { url = ""; result = null }) { Icon(Icons.Filled.Clear, "Clear", tint = subTextColor) }\n\1else {\n\1    IconButton(onClick = { clipboardManager.getText()?.text?.let { url = it; if (it.length > 5) warmUpBackend() } }, modifier = Modifier.clip(RoundedCornerShape(16.dp)).background(Color.White.copy(0.15f)).size(44.dp)) {\n\2Icon(Icons.Filled.ContentPaste, null, tint = textColor, modifier = Modifier.size(20.dp))\n\3}\n\4}'
content = re.sub(pattern, repl, content)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
