import re

with open("app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt", "r") as f:
    content = f.read()

target = """            isPlaying = true,
            isBuffering = true,
            positionMs = 0"""

replacement = """            isPlaying = true,
            isBuffering = true,
            isPrepared = false,
            positionMs = 0"""

if target in content:
    content = content.replace(target, replacement)
    with open("app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt", "w") as f:
        f.write(content)
    print("Success 1")

target2 = """    private fun playUrl(url: String) {
        try {
            mediaPlayer?.release()"""

replacement2 = """    private fun playUrl(url: String) {
        try {
            MusicController.updateIsPrepared(false)
            mediaPlayer?.release()"""

if target2 in content:
    with open("app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt", "w") as f:
        f.write(content.replace(target2, replacement2))
    print("Success 2")

