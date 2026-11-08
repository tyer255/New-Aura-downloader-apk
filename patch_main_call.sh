awk '
/ImmersiveLyricsScreen\(/ {
    print "        ImmersiveLyricsScreen("
    print "            lyrics = lyrics,"
    print "            currentPositionMs = if (isUserScrubbing) sliderPositionMs.toLong() else currentPositionMs.toLong(),"
    print "            durationMs = durationMs.toLong(),"
    print "            offsetMs = totalOffsetMs,"
    print "            onOffsetChange = { userLyricsOffsetMs = it - autoOffsetMs },"
    print "            isPlaying = isPlaying,"
    print "            title = title,"
    print "            artist = artist,"
    print "            thumbnailUrl = thumbnailUrl,"
    print "            onPlayPause = { if (isPlaying) MusicController.pause() else MusicController.play() },"
    print "            onSeek = { pos -> MusicController.seekTo(pos) },"
    print "            onClose = { showImmersiveLyrics = false }"
    print "        )"
    skip_to = "        )"
    next
}
{
    if (skip_to != "") {
        if ($0 ~ skip_to) {
            skip_to = ""
        }
        next
    }
    print $0
}
' app/src/main/java/com/auradownloader/app/MainActivity.kt > tmp.kt && mv tmp.kt app/src/main/java/com/auradownloader/app/MainActivity.kt
