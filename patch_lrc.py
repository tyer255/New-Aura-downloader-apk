import re

with open('app/src/main/java/com/auradownloader/app/SyncedLyricsView.kt', 'r') as f:
    text = f.read()

old_parse = """fun parseLrc(lrcText: String): List<LrcLine> {
    val lines = lrcText.split("\\n")
    val result = mutableListOf<LrcLine>()
    val timeRegex = Regex(\"\"\"\\[(\\d{2}):(\\d{2}(?:\\.\\d{2,3})?)]\"\"\")
    
    for (line in lines) {
        val matches = timeRegex.findAll(line)
        for (match in matches) {
            val min = match.groupValues[1].toLong()
            val sec = match.groupValues[2].toDouble()
            val timeMs = (min * 60000 + sec * 1000).toLong()
            val text = line.replace(timeRegex, "").trim()
            if (text.isNotEmpty()) {
                result.add(LrcLine(timeMs, text))
            }
        }
    }
    return result.sortedBy { it.timeMs }
}"""

new_parse = """fun parseLrc(lrcText: String, durationMs: Long = 0L): List<LrcLine> {
    val lines = lrcText.split("\\n")
    val result = mutableListOf<LrcLine>()
    // More forgiving regex for timestamps
    val timeRegex = Regex(\"\"\"\\[(\\d{1,3}):(\\d{1,2}(?:\\.\\d{1,3})?)]\"\"\")
    
    for (line in lines) {
        val matches = timeRegex.findAll(line)
        for (match in matches) {
            val min = match.groupValues[1].toLong()
            val sec = match.groupValues[2].toDouble()
            val timeMs = (min * 60000 + sec * 1000).toLong()
            val text = line.replace(timeRegex, "").trim()
            if (text.isNotEmpty()) {
                result.add(LrcLine(timeMs, text))
            }
        }
    }
    
    if (result.isEmpty()) {
        // Fallback: If lyrics are plain text without timestamps, distribute them evenly
        val cleanLines = lines.map { it.trim() }.filter { it.isNotEmpty() }
        if (cleanLines.isNotEmpty()) {
            val validDuration = if (durationMs > 0) durationMs else 180000L // Default 3 mins if duration is unknown
            val timePerLine = validDuration / cleanLines.size
            for ((index, line) in cleanLines.withIndex()) {
                result.add(LrcLine(index * timePerLine, line))
            }
        }
    }
    
    return result.sortedBy { it.timeMs }
}"""

text = text.replace(old_parse, new_parse)

text = text.replace(
    "val parsedLyrics = remember(lyrics) { parseLrc(lyrics) }",
    "val parsedLyrics = remember(lyrics, durationMs) { parseLrc(lyrics, durationMs) }"
)

with open('app/src/main/java/com/auradownloader/app/SyncedLyricsView.kt', 'w') as f:
    f.write(text)

print("Patched parseLrc")
