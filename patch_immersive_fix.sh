awk '
/val activeIndex = remember\(currentPositionMs, parsedLyrics, offsetMs\)/ {
    print "    val parsedLyrics = remember(lyrics, durationMs) { parseLrc(lyrics, durationMs) }"
    print $0
    next
}
{ print $0 }
' app/src/main/java/com/auradownloader/app/SyncedLyricsView.kt > tmp.kt && mv tmp.kt app/src/main/java/com/auradownloader/app/SyncedLyricsView.kt
