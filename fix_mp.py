import re

with open("app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt", "r") as f:
    content = f.read()

# I will replace the command loop with a try-catch wrapped version
replacement = """
                    is MusicCommand.Play -> mediaPlayer?.let { mp ->
                        try {
                            if (MusicController.playbackState.value.isPrepared) {
                                if (mp.duration > 0 && mp.currentPosition >= mp.duration - 500) {
                                    mp.seekTo(0)
                                    MusicController.updatePosition(0, mp.duration)
                                }
                                mp.start()
                                MusicController.updatePosition(mp.currentPosition, mp.duration)
                            } else {
                                MusicController.updateIsPlaying(true)
                            }
                        } catch (e: Exception) {}
                    }
                    is MusicCommand.Pause -> mediaPlayer?.let { mp ->
                        try {
                            if (MusicController.playbackState.value.isPrepared) {
                                mp.pause()
                            } else {
                                MusicController.updateIsPlaying(false)
                            }
                        } catch (e: Exception) {}
                    }
                    is MusicCommand.Next -> mediaPlayer?.let { mp ->
                        try {
                            if (MusicController.playbackState.value.isPrepared) {
                                val newPos = (mp.currentPosition + 5000).coerceAtMost(mp.duration)
                                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                                    mp.seekTo(newPos.toLong(), MediaPlayer.SEEK_CLOSEST)
                                } else {
                                    mp.seekTo(newPos)
                                }
                                MusicController.updatePosition(newPos, mp.duration)
                            }
                        } catch (e: Exception) {}
                    }
                    is MusicCommand.Previous -> mediaPlayer?.let { mp ->
                        try {
                            if (MusicController.playbackState.value.isPrepared) {
                                val newPos = (mp.currentPosition - 5000).coerceAtLeast(0)
                                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                                    mp.seekTo(newPos.toLong(), MediaPlayer.SEEK_CLOSEST)
                                } else {
                                    mp.seekTo(newPos)
                                }
                                MusicController.updatePosition(newPos, mp.duration)
                            }
                        } catch (e: Exception) {}
                    }
                    is MusicCommand.SeekTo -> mediaPlayer?.let { mp ->
                        try {
                            if (MusicController.playbackState.value.isPrepared) {
                                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                                    mp.seekTo(cmd.position.toLong(), MediaPlayer.SEEK_CLOSEST)
                                } else {
                                    mp.seekTo(cmd.position)
                                }
                                MusicController.updatePosition(cmd.position, mp.duration)
                            }
                        } catch (e: Exception) {}
                    }
"""

target = """
                    is MusicCommand.Play -> mediaPlayer?.let { mp ->
                        if (mp.duration > 0 && mp.currentPosition >= mp.duration - 500) {
                            mp.seekTo(0)
                            MusicController.updatePosition(0, mp.duration)
                        }
                        mp.start()
                        MusicController.updatePosition(mp.currentPosition, mp.duration)
                    }
                    is MusicCommand.Pause -> mediaPlayer?.pause()
                    is MusicCommand.Next -> mediaPlayer?.let { mp ->
                        val newPos = (mp.currentPosition + 5000).coerceAtMost(mp.duration)
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                            mp.seekTo(newPos.toLong(), MediaPlayer.SEEK_CLOSEST)
                        } else {
                            mp.seekTo(newPos)
                        }
                        MusicController.updatePosition(newPos, mp.duration)
                    }
                    is MusicCommand.Previous -> mediaPlayer?.let { mp ->
                        val newPos = (mp.currentPosition - 5000).coerceAtLeast(0)
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                            mp.seekTo(newPos.toLong(), MediaPlayer.SEEK_CLOSEST)
                        } else {
                            mp.seekTo(newPos)
                        }
                        MusicController.updatePosition(newPos, mp.duration)
                    }
                    is MusicCommand.SeekTo -> mediaPlayer?.let { mp ->
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                            mp.seekTo(cmd.position.toLong(), MediaPlayer.SEEK_CLOSEST)
                        } else {
                            mp.seekTo(cmd.position)
                        }
                        MusicController.updatePosition(cmd.position, mp.duration)
                    }
"""

target = target.strip('\n')
replacement = replacement.strip('\n')

if target in content:
    content = content.replace(target, replacement)
    with open("app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt", "w") as f:
        f.write(content)
    print("Success")
else:
    print("Target not found")
