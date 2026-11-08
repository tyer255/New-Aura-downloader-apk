awk '
/serviceScope\.launch \{/ {
    in_loop = 1
}
in_loop == 1 && /var lastRealTime = 0L/ {
    print "            while (isActive) {"
    print "                mediaPlayer?.let { mp ->"
    print "                    try {"
    print "                        if (mp.isPlaying) {"
    print "                            val pos = mp.currentPosition"
    print "                            val dur = mp.duration"
    print "                            MusicController.updatePosition(pos, dur)"
    print "                        }"
    print "                    } catch (e: Exception) {"
    print "                        e.printStackTrace()"
    print "                    }"
    print "                }"
    print "                delay(100L)"
    print "            }"
    print "        }"
    skip = 1
    next
}
skip == 1 && /delay\(16L\)/ {
    skip = 2
    next
}
skip == 2 && /^\s*\}\s*$/ {
    skip = 0
    in_loop = 0
    next
}
skip > 0 { next }
{ print $0 }
' app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt > tmp.kt && mv tmp.kt app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt
