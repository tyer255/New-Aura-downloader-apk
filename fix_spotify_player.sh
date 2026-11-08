awk '
/fun formatTimeMs\(ms: Int\): String \{/ {
    print "}"
    print $0
    next
}
{ print $0 }
' app/src/main/java/com/auradownloader/app/MainActivity.kt > tmp.kt && mv tmp.kt app/src/main/java/com/auradownloader/app/MainActivity.kt
