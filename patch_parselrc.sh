awk '
/if \(result\.isEmpty\(\)\) \{/ {
    in_fallback = 1
    next
}
/return result\.sortedBy \{ it\.timeMs \}/ {
    if (in_fallback) {
        in_fallback = 0
    }
    print $0
    next
}
{
    if (!in_fallback) {
        print $0
    }
}
' app/src/main/java/com/auradownloader/app/SyncedLyricsView.kt > tmp.kt && mv tmp.kt app/src/main/java/com/auradownloader/app/SyncedLyricsView.kt
