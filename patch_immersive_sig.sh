awk '
/fun ImmersiveLyricsScreen\(/ {
    print "@Composable"
    print "fun ImmersiveLyricsScreen("
    print "    lyrics: String,"
    print "    currentPositionMs: Long,"
    print "    durationMs: Long,"
    print "    offsetMs: Long,"
    print "    onOffsetChange: (Long) -> Unit,"
    print "    isPlaying: Boolean,"
    print "    title: String,"
    print "    artist: String?,"
    print "    thumbnailUrl: String,"
    print "    onPlayPause: () -> Unit,"
    print "    onSeek: (Int) -> Unit,"
    print "    onClose: () -> Unit"
    print ") {"
    skip_to = "    val parsedLyrics"
    next
}
/userLyricsOffsetMs -= 500L/ {
    gsub(/userLyricsOffsetMs -= 500L/, "onOffsetChange(offsetMs - 500L)")
}
/userLyricsOffsetMs \+= 500L/ {
    gsub(/userLyricsOffsetMs \+= 500L/, "onOffsetChange(offsetMs + 500L)")
}
/totalOffsetMs \/ 1000f/ {
    gsub(/totalOffsetMs/, "offsetMs")
}
/totalOffsetMs >= 0/ {
    gsub(/totalOffsetMs/, "offsetMs")
}
/val activeIndex = remember\(currentPositionMs, parsedLyrics, totalOffsetMs\)/ {
    print "    val activeIndex = remember(currentPositionMs, parsedLyrics, offsetMs) {"
    print "        parsedLyrics.indexOfLast { it.timeMs + offsetMs <= currentPositionMs }"
    print "    }"
    skip_to = "    }"
    next
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
' app/src/main/java/com/auradownloader/app/SyncedLyricsView.kt > tmp.kt && mv tmp.kt app/src/main/java/com/auradownloader/app/SyncedLyricsView.kt
