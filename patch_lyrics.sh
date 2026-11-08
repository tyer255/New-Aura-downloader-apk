sed -i 's/val parsedLyrics = remember(lyrics, durationMs) { parseLrc(lyrics, durationMs) }/var userLyricsOffsetMs by remember { mutableLongStateOf(0L) }\n    val parsedLyrics = remember(lyrics, durationMs) { parseLrc(lyrics, durationMs) }/g' app/src/main/java/com/auradownloader/app/SyncedLyricsView.kt

sed -i 's/val activeIndex = remember(currentPositionMs, parsedLyrics) {/val activeIndex = remember(currentPositionMs, parsedLyrics, userLyricsOffsetMs) {/g' app/src/main/java/com/auradownloader/app/SyncedLyricsView.kt

sed -i 's/parsedLyrics.indexOfLast { it.timeMs <= currentPositionMs }/parsedLyrics.indexOfLast { it.timeMs <= currentPositionMs + userLyricsOffsetMs }/g' app/src/main/java/com/auradownloader/app/SyncedLyricsView.kt
