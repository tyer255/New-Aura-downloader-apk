awk '
/var userLyricsOffsetMs by remember \{ mutableLongStateOf\(-800L\)/ || /var userLyricsOffsetMs by remember \{ mutableLongStateOf\(0L\)/ {
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
{ print $0 }
' app/src/main/java/com/auradownloader/app/SyncedLyricsView.kt > tmp.kt && mv tmp.kt app/src/main/java/com/auradownloader/app/SyncedLyricsView.kt
