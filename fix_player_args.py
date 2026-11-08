import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

old_call = """                                SpotifyMusicPlayer(
                                    title = activeTitle,
                                    artist = activeArtist,
                                    thumbnailUrl = activeThumb,
                                    audioUrl = activeAudioToPlay,
                                    isDarkMode = isDarkMode
                                )"""
new_call = """                                SpotifyMusicPlayer(
                                    title = activeTitle,
                                    artist = activeArtist,
                                    thumbnailUrl = activeThumb,
                                    audioUrl = activeAudioToPlay,
                                    isDarkMode = isDarkMode,
                                    lyrics = selectedPlaylistTrack?.lyrics ?: r.lyrics,
                                    syncedLyrics = selectedPlaylistTrack?.syncedLyrics ?: r.syncedLyrics
                                )"""
content = content.replace(old_call, new_call)

old_fun = """fun SpotifyMusicPlayer(
    title: String,
    artist: String?,
    thumbnailUrl: String,
    audioUrl: String,
    isDarkMode: Boolean
) {"""
new_fun = """data class LyricLine(val timeMs: Long, val text: String)

fun parseLrc(lrc: String?): List<LyricLine> {
    if (lrc.isNullOrEmpty()) return emptyList()
    val regex = Regex("\\[(\\\\d+):(\\\\d+\\\\.\\\\d+)\\](.*)")
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
fun SpotifyMusicPlayer(
    title: String,
    artist: String?,
    thumbnailUrl: String,
    audioUrl: String,
    isDarkMode: Boolean,
    lyrics: String? = null,
    syncedLyrics: String? = null
) {"""
content = content.replace(old_fun, new_fun)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
