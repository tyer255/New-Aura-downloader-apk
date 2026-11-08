awk '
/val activeIndex = remember\(currentPositionMs, parsedLyrics, userLyricsOffsetMs\)/ {
    print $0
    getline
    print "        parsedLyrics.indexOfLast { it.timeMs <= currentPositionMs + userLyricsOffsetMs }"
    next
}
{ print $0 }
' app/src/main/java/com/auradownloader/app/SyncedLyricsView.kt > tmp.kt && mv tmp.kt app/src/main/java/com/auradownloader/app/SyncedLyricsView.kt
