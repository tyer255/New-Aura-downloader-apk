awk '
/    if \(showSuccessAnimation\) {/ {
    if (count == 0) {
        count = 1
        skip = 14
        next
    }
}
{
    if (skip > 0) {
        skip--
        next
    }
    print $0
}
' app/src/main/java/com/auradownloader/app/MainActivity.kt > tmp.kt && mv tmp.kt app/src/main/java/com/auradownloader/app/MainActivity.kt
