import re

with open("app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt", "r") as f:
    content = f.read()

# Make playTrack set isPlaying = true so that UI shows Pause right away,
# making it clear that it's going to play.
old_playTrack = """    fun playTrack(url: String, title: String, artist: String?, thumbnailUrl: String) {
        _playbackState.value = _playbackState.value.copy(
            url = url,
            title = title,
            artist = artist ?: "",
            thumbnailUrl = thumbnailUrl
        )
        _commandFlow.value = MusicCommand.PlayUrl(url)
    }"""

new_playTrack = """    fun playTrack(url: String, title: String, artist: String?, thumbnailUrl: String) {
        _playbackState.value = _playbackState.value.copy(
            url = url,
            title = title,
            artist = artist ?: "",
            thumbnailUrl = thumbnailUrl,
            isPlaying = true,
            isBuffering = true
        )
        _commandFlow.value = MusicCommand.PlayUrl(url)
    }"""

content = content.replace(old_playTrack, new_playTrack)

# Also when prepared, we only start if isPlaying is true.
# Because if the user pressed Pause while it was buffering, we shouldn't play it.
old_prepared = """                setOnPreparedListener { mp ->
                    MusicController.updateIsPrepared(true)
                    MusicController.updateIsBuffering(false)
                    MusicController.updatePosition(0, mp.duration)
                    mp.start()
                    MusicController.updateIsPlaying(true)
                }"""

new_prepared = """                setOnPreparedListener { mp ->
                    MusicController.updateIsPrepared(true)
                    MusicController.updateIsBuffering(false)
                    MusicController.updatePosition(0, mp.duration)
                    if (MusicController.playbackState.value.isPlaying) {
                        mp.start()
                    }
                }"""

content = content.replace(old_prepared, new_prepared)

with open("app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt", "w") as f:
    f.write(content)

