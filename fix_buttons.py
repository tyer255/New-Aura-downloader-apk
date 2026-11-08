import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

# Fix Button 1 (Around line 1616)
content = content.replace("            Spacer(modifier = Modifier.height(24.dp))\n                onClick = {\n                    if (url.isNotEmpty()) {", "            Spacer(modifier = Modifier.height(24.dp))\n            Button(\n                onClick = {\n                    if (url.isNotEmpty()) {")

# Fix Button 2 (Around line 1951)
content = content.replace("                                    val isZip = q.label.contains(\"zip\", true)\n                                        onClick = {\n                                            val action = {", "                                    val isZip = q.label.contains(\"zip\", true)\n                                    Button(\n                                        onClick = {\n                                            val action = {")

# Fix Button 3 (Around line 2840)
content = content.replace("                val speeds = listOf(0.5f, 1.0f, 1.5f, 2.0f)\n                    onClick = {\n                        val nextIdx = (speeds.indexOf(currentSpeed) + 1) % speeds.size", "                val speeds = listOf(0.5f, 1.0f, 1.5f, 2.0f)\n                Button(\n                    onClick = {\n                        val nextIdx = (speeds.indexOf(currentSpeed) + 1) % speeds.size")

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
