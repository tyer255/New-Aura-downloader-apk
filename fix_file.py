import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

bad_block = """@Composable
data class LyricLine(val timeMs: Long, val text: String)
fun parseLrc(lrc: String?): List<LyricLine> {
    if (lrc.isNullOrEmpty()) return emptyList()
    val regex = Regex("\\[(\\d+):(\\d+\\.\\d+)\\](.*)")
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
}

@Composable
fun SpotifyMusicPlayer("""

good_block = """@Composable
fun SpotifyMusicPlayer("""

# Since it might have a bad regex syntax in the string:
import re
content = re.sub(r'@Composable\s*data class LyricLine\(.*?\n@Composable\nfun SpotifyMusicPlayer\(', '@Composable\nfun SpotifyMusicPlayer(', content, flags=re.DOTALL)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
