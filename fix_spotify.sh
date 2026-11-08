awk '
NR == 3025 {
    print "}"
}
{ print $0 }
' app/src/main/java/com/auradownloader/app/MainActivity.kt > tmp.kt && mv tmp.kt app/src/main/java/com/auradownloader/app/MainActivity.kt
