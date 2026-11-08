awk '
/val playbackState by MusicController\.playbackState\.collectAsState\(\)/ {
    if (in_spotify_player) {
        print "    var userLyricsOffsetMs by remember { mutableLongStateOf(0L) }"
    }
    print $0
    next
}
/fun SpotifyMusicPlayer\(/ {
    in_spotify_player = 1
    print $0
    next
}
/var isMinimized by remember \{ mutableStateOf\(false\) \}/ {
    print "    val autoOffsetMs = remember(durationMs, expectedDurationMs) {"
    print "        if (durationMs > 0 && expectedDurationMs > 0 && durationMs > expectedDurationMs + 1000) {"
    print "            (durationMs - expectedDurationMs) / 2"
    print "        } else 0L"
    print "    }"
    print "    val totalOffsetMs = autoOffsetMs + userLyricsOffsetMs"
    print $0
    next
}
/val expectedDurationMs = remember\(expectedDurationStr\) \{/ {
    if (in_spotify_player) {
        print "    val expectedDurationMs = remember(expectedDurationStr) {"
        print "        if (expectedDurationStr == null) 0L else {"
        print "            val parts = expectedDurationStr.split(\":\")"
        print "            when (parts.size) {"
        print "                2 -> (parts[0].toLongOrNull() ?: 0L) * 60000 + (parts[1].toLongOrNull() ?: 0L) * 1000"
        print "                3 -> (parts[0].toLongOrNull() ?: 0L) * 3600000 + (parts[1].toLongOrNull() ?: 0L) * 60000 + (parts[2].toLongOrNull() ?: 0L) * 1000"
        print "                else -> 0L"
        print "            }"
        print "        }"
        print "    }"
        skip_to = "    val scope = rememberCoroutineScope()"
        next
    }
}
/SyncedLyricsView\(/ {
    if (in_spotify_player) {
        print "                SyncedLyricsView("
        print "                    lyrics = lyrics,"
        print "                    currentPositionMs = currentPositionMs.toLong(),"
        print "                    offsetMs = totalOffsetMs,"
        print "                    onOffsetChange = { userLyricsOffsetMs = it - autoOffsetMs },"
        print "                    activeColor = if (isDarkMode) Color.White else Color.Black,"
        print "                    textColor = if (isDarkMode) Color.White.copy(alpha = 0.5f) else Color.Black.copy(alpha = 0.5f)"
        print "                )"
        skip_to = "                )"
        next
    } else {
        print "                var bottomSheetOffsetMs by remember { mutableLongStateOf(0L) }"
        print "                SyncedLyricsView("
        print "                    lyrics = showLyrics ?: \"\","
        print "                    currentPositionMs = playbackState.positionMs.toLong(),"
        print "                    offsetMs = bottomSheetOffsetMs,"
        print "                    onOffsetChange = { bottomSheetOffsetMs = it },"
        print "                    activeColor = selectedPlatform.brandColor,"
        print "                    textColor = textColor"
        print "                )"
        skip_to = "                )"
        next
    }
}
{
    if (skip_to != "") {
        if ($0 ~ skip_to) {
            skip_to = ""
        }
        next
    }
    print $0
}
' app/src/main/java/com/auradownloader/app/MainActivity.kt > tmp.kt && mv tmp.kt app/src/main/java/com/auradownloader/app/MainActivity.kt
