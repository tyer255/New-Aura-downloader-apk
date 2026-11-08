awk '
/fun SettingsScreen\(isDarkMode: Boolean\) \{/ {
    print $0
    print "    val context = LocalContext.current"
    next
}
/fun SpotifyMusicPlayer\(/ {
    print $0
    in_spotify = 1
    next
}
in_spotify == 1 && /\) \{/ {
    print $0
    print "    val context = LocalContext.current"
    in_spotify = 0
    next
}
{ print $0 }
' app/src/main/java/com/auradownloader/app/MainActivity.kt > tmp.kt && mv tmp.kt app/src/main/java/com/auradownloader/app/MainActivity.kt
