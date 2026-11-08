awk '
/var bottomSheetOffsetMs by remember \{ mutableLongStateOf\(0L\) \}/ {
    print "                var bottomSheetOffsetMs by remember(showLyrics) { mutableLongStateOf(0L) }"
    next
}
/var userLyricsOffsetMs by remember \{ mutableLongStateOf\(0L\) \}/ {
    print "    var userLyricsOffsetMs by remember(lyrics) { mutableLongStateOf(0L) }"
    next
}
{ print $0 }
' app/src/main/java/com/auradownloader/app/MainActivity.kt > tmp.kt && mv tmp.kt app/src/main/java/com/auradownloader/app/MainActivity.kt
