with open("app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt", "r") as f:
    content = f.read()

target = """                        if (mp.isPlaying) {
                            val pos = mp.currentPosition
                            val dur = mp.duration
                            MusicController.updatePosition(pos, dur)
                        }"""

replacement = """                        if (MusicController.playbackState.value.isPrepared && mp.isPlaying) {
                            val pos = mp.currentPosition
                            val dur = mp.duration
                            MusicController.updatePosition(pos, dur)
                        }"""

if target in content:
    with open("app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt", "w") as f:
        f.write(content.replace(target, replacement))
    print("Success 3")
