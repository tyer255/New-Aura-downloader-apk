import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

target = """fun parseLrc(lrc: String?): List<LyricLine> {
    if (lrc.isNullOrEmpty()) return emptyList()
    val regex = Regex("\\\\[(\\\\d+):(\\\\d+\\\\.\\\\d+)\\\\](.*)")"""

replacement = """fun parseLrc(lrc: String?): List<LyricLine> {
    if (lrc.isNullOrEmpty()) return emptyList()
    val regex = Regex("\\\\[(\\\\d+):(\\\\d+(?:\\\\.\\\\d+)?)\\\\](.*)")"""

content = content.replace(target, replacement)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
