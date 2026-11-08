with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    code = f.read()

target = """                                    val wasPlaying = mp.isPlaying
                                    val params = mp.playbackParams
                                    params.speed = newSpeed
                                    mp.playbackParams = params
                                    if (!wasPlaying && mp.isPlaying) {
                                        mp.pause()
                                    }"""

replacement = """                                    val wasPlaying = mp.isPlaying
                                    val params = mp.playbackParams
                                    params.speed = newSpeed
                                    params.pitch = 1.0f
                                    mp.playbackParams = params
                                    if (!wasPlaying && mp.isPlaying) {
                                        mp.pause()
                                    }"""

if target in code:
    code = code.replace(target, replacement)
    with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
        f.write(code)
    print("Replaced speed toggle params")
else:
    print("Target not found")
