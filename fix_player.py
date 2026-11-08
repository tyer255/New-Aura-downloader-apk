import re

with open("player.txt", "r") as f:
    player_code = f.read()

# 1. Remove MediaPlayer instantiation and DisposableEffect
pattern_vars = r"    var mediaPlayer by remember \{ mutableStateOf<MediaPlayer\?>(null) \}\n    var isPlaying by remember \{ mutableStateOf\(false\) \}\n    var isLooping by remember \{ mutableStateOf\(false\) \}\n    var currentSpeed by remember \{ mutableFloatStateOf\(1\.0f\) \}\n    var volume by remember \{ mutableFloatStateOf\(1\.0f\) \}\n    var isMuted by remember \{ mutableStateOf\(false\) \}\n    var currentPositionMs by remember \{ mutableIntStateOf\(0\) \}\n    var durationMs by remember \{ mutableIntStateOf\(0\) \}\n    var isPrepared by remember \{ mutableStateOf\(false\) \}\n    var isBuffering by remember \{ mutableStateOf\(true\) \}\n    var isError by remember \{ mutableStateOf\(false\) \}\n"

replacement_vars = """    val playbackState by MusicController.playbackState.collectAsState()
    val isPlaying = playbackState.isPlaying
    val isPrepared = playbackState.isPrepared
    val isBuffering = playbackState.isBuffering
    val isError = playbackState.isError
    val currentPositionMs = playbackState.positionMs
    val durationMs = playbackState.durationMs
    
    var isLooping by remember { mutableStateOf(false) }
    var currentSpeed by remember { mutableFloatStateOf(1.0f) }
    var volume by remember { mutableFloatStateOf(1.0f) }
    var isMuted by remember { mutableStateOf(false) }
"""

player_code = player_code.replace(
"""    var mediaPlayer by remember { mutableStateOf<MediaPlayer?>(null) }
    var isPlaying by remember { mutableStateOf(false) }
    var isLooping by remember { mutableStateOf(false) }
    var currentSpeed by remember { mutableFloatStateOf(1.0f) }
    var volume by remember { mutableFloatStateOf(1.0f) }
    var isMuted by remember { mutableStateOf(false) }
    var currentPositionMs by remember { mutableIntStateOf(0) }
    var durationMs by remember { mutableIntStateOf(0) }
    var isPrepared by remember { mutableStateOf(false) }
    var isBuffering by remember { mutableStateOf(true) }
    var isError by remember { mutableStateOf(false) }""",
replacement_vars
)

# 2. Replace LaunchedEffect and DisposableEffect
pattern_effects = """    LaunchedEffect(audioUrl, title, artist) {
        isPrepared = false
        isBuffering = true
        isError = false
        currentSpeed = 1.0f
        activeAudioUrl = resolveSpotifyUrl(audioUrl, title, artist)
    }

    DisposableEffect(activeAudioUrl) {"""

# We need to find the end of DisposableEffect.
disposable_start = player_code.find("DisposableEffect(activeAudioUrl) {")
if disposable_start != -1:
    brackets = 0
    in_fun = False
    disposable_end = -1
    for i in range(disposable_start, len(player_code)):
        if player_code[i] == '{':
            brackets += 1
            in_fun = True
        elif player_code[i] == '}':
            brackets -= 1
        
        if in_fun and brackets == 0:
            disposable_end = i + 1
            break

    launched_effect_start = player_code.find("LaunchedEffect(audioUrl, title, artist) {")
    
    effects_replacement = """    LaunchedEffect(audioUrl, title, artist) {
        activeAudioUrl = resolveSpotifyUrl(audioUrl, title, artist)
    }
    
    LaunchedEffect(activeAudioUrl) {
        if (!activeAudioUrl.isNullOrEmpty() && activeAudioUrl != playbackState.url) {
            val intent = Intent(context, MusicPlaybackService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                ContextCompat.startForegroundService(context, intent)
            } else {
                context.startService(intent)
            }
            MusicController.playTrack(activeAudioUrl!!, title, artist, thumbnailUrl)
        }
    }"""
    
    player_code = player_code[:launched_effect_start] + effects_replacement + player_code[disposable_end:]

# 3. Replace all mediaPlayer?.let {...} with MusicController calls

# For Slider onValueChangeFinished
slider_pattern = """                        onValueChangeFinished = {
                            isUserScrubbing = false
                            mediaPlayer?.let { mp ->
                                try {
                                    mp.seekTo(sliderPositionMs.toInt())
                                    currentPositionMs = sliderPositionMs.toInt()
                                } catch (e: Exception) {
                                    e.printStackTrace()
                                }
                            }
                        }"""
slider_replacement = """                        onValueChangeFinished = {
                            isUserScrubbing = false
                            MusicController.seekTo(sliderPositionMs.toInt())
                        }"""
player_code = player_code.replace(slider_pattern, slider_replacement)

# Rewind
rewind_pattern = """                                .clickable {
                                    mediaPlayer?.let { mp ->
                                        val newPos = (mp.currentPosition - 5000).coerceAtLeast(0)
                                        mp.seekTo(newPos)
                                        currentPositionMs = newPos
                                    }
                                }"""
rewind_replacement = """                                .clickable {
                                    val newPos = (currentPositionMs - 5000).coerceAtLeast(0)
                                    MusicController.seekTo(newPos)
                                }"""
player_code = player_code.replace(rewind_pattern, rewind_replacement)

# Forward
forward_pattern = """                                .clickable {
                                    mediaPlayer?.let { mp ->
                                        val newPos = (mp.currentPosition + 5000).coerceAtMost(mp.duration)
                                        mp.seekTo(newPos)
                                        currentPositionMs = newPos
                                    }
                                }"""
forward_replacement = """                                .clickable {
                                    val newPos = (currentPositionMs + 5000).coerceAtMost(durationMs)
                                    MusicController.seekTo(newPos)
                                }"""
player_code = player_code.replace(forward_pattern, forward_replacement)

# Play/Pause
play_pattern = """                                .clickable {
                                    mediaPlayer?.let { mp ->
                                        if (isPrepared) {
                                            if (mp.isPlaying) {
                                                mp.pause()
                                                isPlaying = false
                                            } else {
                                                mp.start()
                                                isPlaying = true
                                            }
                                        } else {
                                            isPlaying = !isPlaying
                                        }
                                    }
                                }"""
play_replacement = """                                .clickable {
                                    if (isPrepared) {
                                        if (isPlaying) {
                                            MusicController.pause()
                                        } else {
                                            MusicController.play()
                                        }
                                    }
                                }"""
player_code = player_code.replace(play_pattern, play_replacement)

# Play/pause in minimized view
play_min_pattern = """                            .clickable {
                                mediaPlayer?.let { mp ->
                                    if (isPrepared) {
                                        if (mp.isPlaying) {
                                            mp.pause()
                                            isPlaying = false
                                        } else {
                                            mp.start()
                                            isPlaying = true
                                        }
                                    }
                                }
                            }"""
play_min_replacement = """                            .clickable {
                                if (isPrepared) {
                                    if (isPlaying) {
                                        MusicController.pause()
                                    } else {
                                        MusicController.play()
                                    }
                                }
                            }"""
player_code = player_code.replace(play_min_pattern, play_min_replacement)


# Repeat button (isLooping)
repeat_pattern = """                            .clickable(
                                interactionSource = remember { MutableInteractionSource() },
                                indication = null
                            ) {
                                isLooping = !isLooping
                                mediaPlayer?.let { mp ->
                                    mp.isLooping = isLooping
                                }
                            }"""
repeat_replacement = """                            .clickable(
                                interactionSource = remember { MutableInteractionSource() },
                                indication = null
                            ) {
                                isLooping = !isLooping
                                // Looping is currently not supported in the new MediaController architecture
                                // or we'd have to pass it to MusicController. For now, just toggle state.
                            }"""
player_code = player_code.replace(repeat_pattern, repeat_replacement)

# 4. FIX WHITE BOX UI BUGS

# Bug 1: DropdownMenu background
player_code = player_code.replace(
    "modifier = Modifier.background(glassBg).border(1.dp, glassBorder, RoundedCornerShape(16.dp))",
    "modifier = Modifier.background(if(isDarkMode) glassBg else Color.White).border(1.dp, glassBorder, RoundedCornerShape(16.dp))"
)

# Bug 2: Minimized view play button shadow (shadow after background causing white box)
player_code = player_code.replace(
"""                        modifier = Modifier
                            .size(44.dp)
                            .clip(CircleShape)
                            .background(glassBg)
                            .border(1.dp, glassBorder, CircleShape)
                            .shadow(4.dp, CircleShape)""",
"""                        modifier = Modifier
                            .size(44.dp)
                            .shadow(4.dp, CircleShape, clip = false)
                            .background(glassBg, CircleShape)
                            .border(1.dp, glassBorder, CircleShape)"""
)

# Bug 3: Expanded view buttons (just reorder to ensure background shape)
player_code = player_code.replace(
"""                            modifier = Modifier
                                .size(48.dp)
                                .clip(CircleShape)
                                .background(glassBg)""",
"""                            modifier = Modifier
                                .size(48.dp)
                                .background(glassBg, CircleShape)
                                .clip(CircleShape)"""
)
player_code = player_code.replace(
"""                            modifier = Modifier
                                .size(80.dp)
                                .clip(CircleShape)
                                .background(glassBg)""",
"""                            modifier = Modifier
                                .size(80.dp)
                                .background(glassBg, CircleShape)
                                .clip(CircleShape)"""
)
player_code = player_code.replace(
"""                    Box(
                        modifier = Modifier
                            .size(40.dp)
                            .clip(CircleShape)
                            .background(glassBg)""",
"""                    Box(
                        modifier = Modifier
                            .size(40.dp)
                            .background(glassBg, CircleShape)
                            .clip(CircleShape)"""
)

# Bug 4: Album Art white box 
player_code = player_code.replace(
"""                // Album Art
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .aspectRatio(1f)
                        .clip(RoundedCornerShape(32.dp))
                        .shadow(24.dp, RoundedCornerShape(32.dp)),""",
"""                // Album Art
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .aspectRatio(1f)
                        .shadow(24.dp, RoundedCornerShape(32.dp))
                        .background(glassBg, RoundedCornerShape(32.dp))
                        .clip(RoundedCornerShape(32.dp)),"""
)

with open("player_fixed.txt", "w") as f:
    f.write(player_code)
