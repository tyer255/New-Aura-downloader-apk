import re

with open("app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt", "r") as f:
    content = f.read()

pattern = r"                    is MusicCommand\.Pause -> mediaPlayer\?\.pause\(\)\n                    is MusicCommand\.SeekTo -> mediaPlayer\?\.seekTo\(cmd\.position\)\n                    is MusicCommand\.Stop -> stopSelf\(\)\n                    else -> \{\}"

replacement = """                    is MusicCommand.Pause -> mediaPlayer?.pause()
                    is MusicCommand.Next -> mediaPlayer?.let { mp ->
                        val newPos = (mp.currentPosition + 5000).coerceAtMost(mp.duration)
                        mp.seekTo(newPos)
                        MusicController.updatePosition(newPos, mp.duration)
                    }
                    is MusicCommand.Previous -> mediaPlayer?.let { mp ->
                        val newPos = (mp.currentPosition - 5000).coerceAtLeast(0)
                        mp.seekTo(newPos)
                        MusicController.updatePosition(newPos, mp.duration)
                    }
                    is MusicCommand.SeekTo -> mediaPlayer?.seekTo(cmd.position)
                    is MusicCommand.Stop -> stopSelf()
                    else -> {}"""

if "is MusicCommand.Next -> mediaPlayer?.let" not in content:
    content = re.sub(pattern, replacement, content)
    with open("app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt", "w") as f:
        f.write(content)
