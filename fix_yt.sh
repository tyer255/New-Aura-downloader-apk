awk '
/if \(backendResult != null && backendResult\.qualities\.isNotEmpty\(\)\) \{/ {
    print "                    val qualities = mutableListOf<MediaQuality>()"
    print "                    if (youtubeAudioUrl != null) {"
    print "                        qualities.add(MediaQuality(\"Full Track (MP3)\", null, youtubeAudioUrl))"
    print "                    }"
    print $0
    next
}
/val qualities = mutableListOf<MediaQuality>\(\)/ {
    next
}
/if \(youtubeAudioUrl != null\) \{/ {
    skip_yt = 1
    next
}
/qualities\.add\(MediaQuality\("Full Track \(MP3\)", null, youtubeAudioUrl\)\)/ {
    if (skip_yt) next
}
/^\s*\}\s*$/ {
    if (skip_yt) {
        skip_yt = 0
        next
    }
    print $0
}
{
    print $0
}
' app/src/main/java/com/auradownloader/app/MainActivity.kt > tmp.kt && mv tmp.kt app/src/main/java/com/auradownloader/app/MainActivity.kt
