import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

# 1. Remove the LaunchedEffect that updates position
effect_pattern = r"    LaunchedEffect\(isPlaying, isUserScrubbing\) \{\n        while \(isPlaying && !isUserScrubbing\) \{\n            mediaPlayer\?\.let \{ mp ->\n                try \{\n                    if \(mp\.isPlaying\) \{\n                        currentPositionMs = mp\.currentPosition\n                        durationMs = mp\.duration\n                    \}\n                \} catch \(e: Exception\) \{\n                    e\.printStackTrace\(\)\n                \}\n            \}\n            delay\(200\)\n        \}\n    \}"

content = re.sub(effect_pattern, "", content)


# 2. Fix rewind
rewind_pattern = r"                                mediaPlayer\?\.let \{ mp ->\n                                    val newPos = \(mp\.currentPosition - 5000\)\.coerceAtLeast\(0\)\n                                    mp\.seekTo\(newPos\)\n                                    currentPositionMs = newPos\n                                \}"
rewind_replace = """                                    val newPos = (currentPositionMs - 5000).coerceAtLeast(0)
                                    MusicController.seekTo(newPos)"""
content = re.sub(rewind_pattern, rewind_replace, content)

# 3. Fix play/pause
play_pattern = r"                                mediaPlayer\?\.let \{ mp ->\n                                    if \(isPrepared\) \{\n                                        if \(mp\.isPlaying\) \{ mp\.pause\(\); isPlaying = false \}\n                                        else \{ mp\.start\(\); isPlaying = true \}\n                                    \} else \{\n                                        isPlaying = !isPlaying\n                                    \}\n                                \}"
play_replace = """                                    if (isPrepared) {
                                        if (isPlaying) { MusicController.pause() }
                                        else { MusicController.play() }
                                    }"""
content = re.sub(play_pattern, play_replace, content)

# 4. Fix forward
forward_pattern = r"                                mediaPlayer\?\.let \{ mp ->\n                                    val newPos = \(mp\.currentPosition \+ 5000\)\.coerceAtMost\(mp\.duration\)\n                                    mp\.seekTo\(newPos\)\n                                    currentPositionMs = newPos\n                                \}"
forward_replace = """                                    val newPos = (currentPositionMs + 5000).coerceAtMost(durationMs)
                                    MusicController.seekTo(newPos)"""
content = re.sub(forward_pattern, forward_replace, content)

# 5. Fix looping
loop_pattern = r"                                mediaPlayer\?\.let \{ mp -> mp\.isLooping = isLooping \}"
loop_replace = """                                // Looping handled by state"""
content = re.sub(loop_pattern, loop_replace, content)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)

