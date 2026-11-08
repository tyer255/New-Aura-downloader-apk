awk '
/DownloadResult\(false, "", "", emptyList\(\), "Unable to extract media\. Please check the URL and try again\."\)/ {
    print $0
    print "    }"
    next
}
{ print $0 }
' app/src/main/java/com/auradownloader/app/MainActivity.kt > tmp.kt && mv tmp.kt app/src/main/java/com/auradownloader/app/MainActivity.kt
