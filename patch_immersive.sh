awk '
/val autoOffsetMs = remember\(durationMs, expectedDurationMs\) \{/ {
    print "    val autoOffsetMs = remember(durationMs, expectedDurationMs) {"
    print "        if (durationMs > 0 && expectedDurationMs > 0 && durationMs > expectedDurationMs + 1000) {"
    print "            (durationMs - expectedDurationMs) / 2"
    print "        } else 0L"
    print "    }"
    skip_to = "    }"
    next
}
/parsedLyrics\.indexOfLast \{ it\.timeMs <= currentPositionMs \+ totalOffsetMs \}/ {
    print "        parsedLyrics.indexOfLast { it.timeMs + totalOffsetMs <= currentPositionMs }"
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
