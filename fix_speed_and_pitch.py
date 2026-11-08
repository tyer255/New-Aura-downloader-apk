with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    code = f.read()

# 1. Reset currentSpeed in LaunchedEffect(audioUrl)
old_launched = """    LaunchedEffect(audioUrl) {
        isPrepared = false
        isBuffering = true
        isError = false
        activeAudioUrl = resolveSpotifyUrl(audioUrl)
    }"""

new_launched = """    LaunchedEffect(audioUrl) {
        isPrepared = false
        isBuffering = true
        isError = false
        currentSpeed = 1.0f
        activeAudioUrl = resolveSpotifyUrl(audioUrl)
    }"""

if old_launched in code:
    code = code.replace(old_launched, new_launched)
    print("Updated LaunchedEffect(audioUrl) to reset currentSpeed = 1.0f")

# 2. Only apply playbackParams if currentSpeed != 1.0f in setOnPreparedListener and set pitch = 1.0f
old_prep = """                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                        try {
                            val params = mp.playbackParams
                            params.speed = currentSpeed
                            mp.playbackParams = params
                        } catch (e: Exception) {
                            e.printStackTrace()
                        }
                    }"""

new_prep = """                    if (currentSpeed != 1.0f && Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                        try {
                            val params = mp.playbackParams
                            params.speed = currentSpeed
                            params.pitch = 1.0f
                            mp.playbackParams = params
                        } catch (e: Exception) {
                            e.printStackTrace()
                        }
                    }"""

if old_prep in code:
    code = code.replace(old_prep, new_prep)
    print("Updated setOnPreparedListener to preserve pitch and avoid touching playbackParams at 1.0x")

# 3. Update speed toggle logic
old_speed_toggle = """                val speeds = listOf(0.5f, 1.0f, 1.5f, 2.0f)
                Button(
                    onClick = {
                        val nextIdx = (speeds.indexOf(currentSpeed) + 1) % speeds.size
                        val newSpeed = speeds[nextIdx]
                        currentSpeed = newSpeed
                        mediaPlayer?.let { mp ->
                            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                                try {
                                    val wasPlaying = mp.isPlaying
                                    val params = mp.playbackParams
                                    params.speed = newSpeed
                                    mp.playbackParams = params
                                    if (!wasPlaying && mp.isPlaying) {
                                        mp.pause()
                                    }
                                } catch (e: Exception) {
                                    e.printStackTrace()
                                }
                            }
                        }
                    }
                )"""

new_speed_toggle = """                val speeds = listOf(0.5f, 1.0f, 1.5f, 2.0f)
                Button(
                    onClick = {
                        val nextIdx = (speeds.indexOf(currentSpeed) + 1) % speeds.size
                        val newSpeed = speeds[nextIdx]
                        currentSpeed = newSpeed
                        mediaPlayer?.let { mp ->
                            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                                try {
                                    val params = mp.playbackParams
                                    params.speed = newSpeed
                                    params.pitch = 1.0f
                                    mp.playbackParams = params
                                } catch (e: Exception) {
                                    e.printStackTrace()
                                }
                            }
                        }
                    }
                )"""

if old_speed_toggle in code:
    code = code.replace(old_speed_toggle, new_speed_toggle)
    print("Updated speed toggle logic")

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(code)

print("Fix applied successfully")
