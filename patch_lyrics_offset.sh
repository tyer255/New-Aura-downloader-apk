awk '
/fun ImmersiveLyricsScreen\(/ {
    in_func = 1
}
in_func == 1 && /artist: String\?,/ {
    print $0
    print "    expectedDurationStr: String? = null,"
    in_func = 0
    next
}
/var userLyricsOffsetMs by remember \{ mutableLongStateOf\(0L\) \}/ {
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
    print "    val autoOffsetMs = remember(durationMs, expectedDurationMs) {"
    print "        if (durationMs > 0 && expectedDurationMs > 0 && durationMs > expectedDurationMs + 1000) {"
    print "            -((durationMs - expectedDurationMs) / 2)"
    print "        } else 0L"
    print "    }"
    print "    var userLyricsOffsetMs by remember { mutableLongStateOf(0L) }"
    print "    val totalOffsetMs = autoOffsetMs + userLyricsOffsetMs"
    next
}
/val activeIndex = remember\(currentPositionMs, parsedLyrics, userLyricsOffsetMs\) \{/ {
    print "    val activeIndex = remember(currentPositionMs, parsedLyrics, totalOffsetMs) {"
    print "        parsedLyrics.indexOfLast { it.timeMs <= currentPositionMs + totalOffsetMs }"
    skip_next = 1
    next
}
skip_next == 1 {
    skip_next = 0
    next
}
/text = \"\$\{if \(userLyricsOffsetMs >= 0\) \"\+\" else \"\"\}\$\{userLyricsOffsetMs \/ 1000f\}s\",/ {
    print "                    text = \"${if (totalOffsetMs >= 0) \"+\" else \"\"}${totalOffsetMs / 1000f}s\","
    next
}
{ print $0 }
' app/src/main/java/com/auradownloader/app/SyncedLyricsView.kt > tmp.kt && mv tmp.kt app/src/main/java/com/auradownloader/app/SyncedLyricsView.kt
