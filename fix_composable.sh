awk '
/@Composable/ {
    if (last_line == "@Composable") {
        next
    }
}
{
    print $0
    last_line = $0
}
' app/src/main/java/com/auradownloader/app/SyncedLyricsView.kt > tmp.kt && mv tmp.kt app/src/main/java/com/auradownloader/app/SyncedLyricsView.kt
