import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

start_idx = content.find("@Composable\\ndata class LyricLine")
if start_idx == -1:
    start_idx = content.find("@Composable\\n\\ndata class LyricLine")
if start_idx == -1:
    start_idx = content.find("@Composable\\r\\ndata class LyricLine")

end_str = "    return parsedLines\\n}"
end_idx = content.find(end_str, start_idx) + len(end_str)

new_block = """data class LyricLine(val timeMs: Long, val text: String)

fun parseLrc(lrc: String?): List<LyricLine> {
    if (lrc.isNullOrEmpty()) return emptyList()
    val regex = Regex("\"\"\"\\\\[(\\\\d+):(\\\\d+\\\\.\\\\d+)\\\\](.*)\"\"\")
    val lines = lrc.lines()
    val parsedLines = mutableListOf<LyricLine>()
    for (line in lines) {
        val matchResult = regex.find(line)
        if (matchResult != null) {
            try {
                val minutes = matchResult.groupValues[1].toLong()
                val seconds = matchResult.groupValues[2].toFloat()
                val text = matchResult.groupValues[3].trim()
                val timeMs = (minutes * 60 * 1000) + (seconds * 1000).toLong()
                parsedLines.add(LyricLine(timeMs, text))
            } catch (e: Exception) {}
        }
    }
    return parsedLines
}"""

content = content[:start_idx] + new_block + content[end_idx:]

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
