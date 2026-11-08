import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

pattern = r'AnimatedVisibility\(visible = detectedClipboardUrl != null && url\.isEmpty\(\)\) \{'

replacement = """Spacer(modifier = Modifier.height(12.dp))
            Button(
                onClick = { 
                    url = "https://www.instagram.com/reel/DbiZBaEIsLq/?igsh=MWg0eXRwMjc3ZnlqYQ==" 
                    coroutineScope.launch {
                        kotlinx.coroutines.delay(500)
                        warmUpBackend()
                    }
                },
                modifier = Modifier.fillMaxWidth().height(48.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFE1306C))
            ) {
                Text("TEST INSTAGRAM LINK", color = Color.White, fontWeight = FontWeight.Bold)
            }
            Spacer(modifier = Modifier.height(12.dp))
            AnimatedVisibility(visible = detectedClipboardUrl != null && url.isEmpty()) {"""

content = re.sub(pattern, replacement, content)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
