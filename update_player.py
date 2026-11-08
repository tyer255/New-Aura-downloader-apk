import re

compose_code = """
@Composable
fun SpotifyMusicPlayer(
    title: String,
    artist: String?,
    thumbnailUrl: String,
    audioUrl: String,
    isDarkMode: Boolean
) {
    val context = LocalContext.current
    var mediaPlayer by remember { mutableStateOf<MediaPlayer?>(null) }
    var isPlaying by remember { mutableStateOf(false) }
    var isLooping by remember { mutableStateOf(false) }
    var currentSpeed by remember { mutableFloatStateOf(1.0f) }
    var volume by remember { mutableFloatStateOf(1.0f) }
    var isMuted by remember { mutableStateOf(false) }
    var currentPositionMs by remember { mutableIntStateOf(0) }
    var durationMs by remember { mutableIntStateOf(0) }
    var isPrepared by remember { mutableStateOf(false) }
    var isBuffering by remember { mutableStateOf(true) }
    var isError by remember { mutableStateOf(false) }
    var isUserScrubbing by remember { mutableStateOf(false) }
    var sliderPositionMs by remember { mutableFloatStateOf(0f) }
    
    var isMinimized by remember { mutableStateOf(false) }
    var showOptionsMenu by remember { mutableStateOf(false) }

    val infiniteTransition = rememberInfiniteTransition(label = "spin")
    val rotation by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(10000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "spinAnimation"
    )

    var activeAudioUrl by remember { mutableStateOf<String?>(null) }
    LaunchedEffect(audioUrl, title, artist) {
        isPrepared = false
        isBuffering = true
        isError = false
        currentSpeed = 1.0f
        activeAudioUrl = resolveSpotifyUrl(audioUrl, title, artist)
    }

    DisposableEffect(activeAudioUrl) {
        val targetUrl = activeAudioUrl
        if (targetUrl.isNullOrEmpty()) {
            return@DisposableEffect onDispose {}
        }
        val player = MediaPlayer().apply {
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                    setAudioAttributes(
                        android.media.AudioAttributes.Builder()
                            .setContentType(android.media.AudioAttributes.CONTENT_TYPE_MUSIC)
                            .setUsage(android.media.AudioAttributes.USAGE_MEDIA)
                            .build()
                    )
                }
                setDataSource(context, Uri.parse(targetUrl))
                setOnPreparedListener { mp ->
                    isPrepared = true
                    isBuffering = false
                    durationMs = mp.duration
                    mp.isLooping = isLooping
                    val currentVol = if (isMuted) 0f else volume
                    mp.setVolume(currentVol, currentVol)
                    if (isPlaying) {
                        try { mp.start() } catch (e: Exception) { e.printStackTrace() }
                    }
                }
                setOnCompletionListener { mp ->
                    if (!mp.isLooping) {
                        isPlaying = false
                        currentPositionMs = 0
                    }
                }
                setOnErrorListener { _, _, _ ->
                    isBuffering = false
                    isPrepared = false
                    isPlaying = false
                    isError = true
                    false
                }
                prepareAsync()
            } catch (e: Exception) {
                e.printStackTrace()
                isBuffering = false
                isError = true
            }
        }
        mediaPlayer = player

        onDispose {
            try {
                if (player.isPlaying) {
                    player.stop()
                }
                player.release()
            } catch (e: Exception) {
                e.printStackTrace()
            }
            mediaPlayer = null
        }
    }

    LaunchedEffect(isPlaying, isUserScrubbing) {
        while (isPlaying && !isUserScrubbing) {
            mediaPlayer?.let { mp ->
                try {
                    if (mp.isPlaying) {
                        currentPositionMs = mp.currentPosition
                        durationMs = mp.duration
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }
            delay(200)
        }
    }

    val bgGradient = if (isDarkMode) {
        Brush.linearGradient(colors = listOf(Color(0xFF0F172A), Color(0xFF1E1B4B), Color(0xFF312E81)))
    } else {
        Brush.linearGradient(colors = listOf(Color(0xFFE2E8F0), Color(0xFFC7D2FE), Color(0xFFDDD6FE)))
    }
    val glassBg = if (isDarkMode) Color.White.copy(alpha = 0.03f) else Color.White.copy(alpha = 0.40f)
    val glassBorder = if (isDarkMode) Color.White.copy(alpha = 0.05f) else Color.White.copy(alpha = 0.50f)
    val textMain = if (isDarkMode) Color.White else Color(0xFF1E293B)
    val textMuted = if (isDarkMode) Color(0xFF94A3B8) else Color(0xFF64748B)
    val accent = if (isDarkMode) Color(0xFF818CF8) else Color(0xFF4F46E5)
    val progressBg = if (isDarkMode) Color.White.copy(alpha = 0.1f) else Color.Black.copy(alpha = 0.1f)
    val textGradient = if (isDarkMode) {
        Brush.linearGradient(colors = listOf(Color(0xFFC7D2FE), Color(0xFFE0E7FF)))
    } else {
        Brush.linearGradient(colors = listOf(Color(0xFF312E81), Color(0xFF4F46E5)))
    }

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(40.dp))
            .background(bgGradient)
            .border(1.dp, glassBorder, RoundedCornerShape(40.dp))
            .animateContentSize()
            .clickable(
                enabled = isMinimized,
                onClick = { isMinimized = false },
                interactionSource = remember { MutableInteractionSource() },
                indication = null
            ),
        contentAlignment = Alignment.Center
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(glassBg)
        )
        
        if (isMinimized) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(90.dp)
                    .padding(horizontal = 20.dp, vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.weight(1f)
                ) {
                    Box(
                        modifier = Modifier
                            .size(56.dp)
                            .clip(CircleShape)
                            .graphicsLayer {
                                rotationZ = if (isPlaying) rotation else 0f
                            },
                        contentAlignment = Alignment.Center
                    ) {
                        if (thumbnailUrl.isNotEmpty()) {
                            AsyncImage(
                                model = coil.request.ImageRequest.Builder(context).data(thumbnailUrl).build(),
                                contentDescription = "Album Cover",
                                contentScale = ContentScale.Crop,
                                modifier = Modifier.fillMaxSize()
                            )
                        } else {
                            Box(modifier = Modifier.fillMaxSize().background(glassBg), contentAlignment = Alignment.Center) {
                                Icon(Icons.Filled.MusicNote, null, tint = textMuted, modifier = Modifier.size(24.dp))
                            }
                        }
                    }
                    
                    Spacer(modifier = Modifier.width(12.dp))
                    
                    Column(
                        modifier = Modifier.weight(1f),
                        verticalArrangement = Arrangement.Center
                    ) {
                        Text(
                            text = title,
                            style = TextStyle(
                                brush = textGradient,
                                fontWeight = FontWeight.SemiBold,
                                fontSize = 16.sp,
                            ),
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                        if (!artist.isNullOrEmpty()) {
                            Text(
                                text = artist,
                                color = textMuted,
                                fontWeight = FontWeight.Light,
                                fontSize = 12.sp,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis
                            )
                        }
                    }
                }
                
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    // Rewind
                    Box(
                        modifier = Modifier
                            .size(36.dp)
                            .clip(CircleShape)
                            .background(glassBg)
                            .clickable {
                                mediaPlayer?.let { mp ->
                                    val newPos = (mp.currentPosition - 5000).coerceAtLeast(0)
                                    mp.seekTo(newPos)
                                    currentPositionMs = newPos
                                }
                            }
                            .border(1.dp, glassBorder, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(Icons.Filled.SkipPrevious, "Rewind", tint = textMain, modifier = Modifier.size(20.dp))
                    }

                    // Play/Pause
                    Box(
                        modifier = Modifier
                            .size(44.dp)
                            .clip(CircleShape)
                            .background(glassBg)
                            .clickable {
                                mediaPlayer?.let { mp ->
                                    if (isPrepared) {
                                        if (mp.isPlaying) { mp.pause(); isPlaying = false }
                                        else { mp.start(); isPlaying = true }
                                    } else {
                                        isPlaying = !isPlaying
                                    }
                                }
                            }
                            .border(1.dp, glassBorder, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = if (isPlaying) Icons.Filled.Pause else Icons.Filled.PlayArrow,
                            contentDescription = if (isPlaying) "Pause" else "Play",
                            tint = textMain,
                            modifier = Modifier.size(24.dp).padding(start = if (isPlaying) 0.dp else 2.dp)
                        )
                    }

                    // Forward
                    Box(
                        modifier = Modifier
                            .size(36.dp)
                            .clip(CircleShape)
                            .background(glassBg)
                            .clickable {
                                mediaPlayer?.let { mp ->
                                    val newPos = (mp.currentPosition + 5000).coerceAtMost(mp.duration)
                                    mp.seekTo(newPos)
                                    currentPositionMs = newPos
                                }
                            }
                            .border(1.dp, glassBorder, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(Icons.Filled.SkipNext, "Forward", tint = textMain, modifier = Modifier.size(20.dp))
                    }
                    
                    // Repeat
                    Box(
                        modifier = Modifier
                            .size(30.dp)
                            .clip(CircleShape)
                            .clickable(
                                interactionSource = remember { MutableInteractionSource() },
                                indication = null
                            ) {
                                isLooping = !isLooping
                                mediaPlayer?.let { mp -> mp.isLooping = isLooping }
                            },
                        contentAlignment = Alignment.Center
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Icon(
                                imageVector = Icons.Filled.Repeat,
                                contentDescription = "Repeat",
                                tint = if (isLooping) accent else textMuted,
                                modifier = Modifier.size(18.dp)
                            )
                            if (isLooping) {
                                Box(modifier = Modifier
                                    .padding(top = 2.dp)
                                    .size(3.dp)
                                    .clip(CircleShape)
                                    .background(accent)
                                )
                            }
                        }
                    }
                }
            }
        } else {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(32.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Top Nav
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 32.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(40.dp)
                            .clip(CircleShape)
                            .background(glassBg)
                            .clickable { isMinimized = true }
                            .border(1.dp, glassBorder, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Filled.KeyboardArrowDown,
                            contentDescription = "Minimize",
                            tint = textMain,
                            modifier = Modifier.size(24.dp)
                        )
                    }
                    
                    Text(
                        text = "NOW PLAYING",
                        color = textMuted,
                        fontWeight = FontWeight.SemiBold,
                        fontSize = 12.sp,
                        letterSpacing = 2.sp
                    )
                    
                    Box(
                        modifier = Modifier
                            .size(40.dp)
                            .clip(CircleShape)
                            .background(glassBg)
                            .clickable { showOptionsMenu = !showOptionsMenu }
                            .border(1.dp, glassBorder, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Filled.MoreVert,
                            contentDescription = "Options",
                            tint = textMain,
                            modifier = Modifier.size(24.dp)
                        )
                        androidx.compose.material3.DropdownMenu(
                            expanded = showOptionsMenu,
                            onDismissRequest = { showOptionsMenu = false },
                            modifier = Modifier.background(glassBg).border(1.dp, glassBorder, RoundedCornerShape(16.dp))
                        ) {
                            androidx.compose.material3.DropdownMenuItem(
                                text = { Text("Show Lyrics", color = textMain) },
                                leadingIcon = { Icon(Icons.Filled.Mic, null, tint = textMain) },
                                onClick = { showOptionsMenu = false; Toast.makeText(context, "Lyrics coming soon!", Toast.LENGTH_SHORT).show() }
                            )
                            androidx.compose.material3.DropdownMenuItem(
                                text = { Text("Share", color = Color(0xFFF87171)) },
                                leadingIcon = { Icon(Icons.Filled.Share, null, tint = Color(0xFFF87171)) },
                                onClick = { showOptionsMenu = false; Toast.makeText(context, "Sharing...", Toast.LENGTH_SHORT).show() }
                            )
                        }
                    }
                }

                // Album Art
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .aspectRatio(1f)
                        .clip(RoundedCornerShape(32.dp))
                        .shadow(24.dp, RoundedCornerShape(32.dp)),
                    contentAlignment = Alignment.Center
                ) {
                    if (thumbnailUrl.isNotEmpty()) {
                        AsyncImage(
                            model = coil.request.ImageRequest.Builder(context).data(thumbnailUrl).build(),
                            contentDescription = "Album Cover",
                            contentScale = ContentScale.Crop,
                            modifier = Modifier.fillMaxSize()
                        )
                    } else {
                        Box(modifier = Modifier.fillMaxSize().background(glassBg), contentAlignment = Alignment.Center) {
                            Icon(
                                imageVector = Icons.Filled.MusicNote,
                                contentDescription = null,
                                tint = textMuted,
                                modifier = Modifier.size(64.dp)
                            )
                        }
                    }
                    
                    if (showOptionsMenu) {
                        Box(modifier = Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.6f)))
                    }
                    
                    if (isBuffering) {
                        CircularProgressIndicator(
                            color = accent,
                            strokeWidth = 3.dp,
                            modifier = Modifier.size(36.dp)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(32.dp))
                
                // Track Info
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 8.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = title,
                        style = TextStyle(
                            brush = textGradient,
                            fontWeight = FontWeight.SemiBold,
                            fontSize = 24.sp,
                            textAlign = TextAlign.Center
                        ),
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                    if (!artist.isNullOrEmpty()) {
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = artist,
                            color = textMuted,
                            fontWeight = FontWeight.Light,
                            fontSize = 14.sp,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                            textAlign = TextAlign.Center
                        )
                    }
                }

                Spacer(modifier = Modifier.height(32.dp))
                
                // Progress
                val displayMs = if (isUserScrubbing) sliderPositionMs.toInt() else currentPositionMs
                val maxMs = if (durationMs > 0) durationMs.toFloat() else 1f
                Column(modifier = Modifier.fillMaxWidth()) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(start = 4.dp, top = 0.dp, end = 4.dp, bottom = 8.dp),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            text = formatTimeMs(displayMs),
                            color = textMuted,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Medium
                        )
                        Text(
                            text = formatTimeMs(durationMs),
                            color = textMuted,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Medium
                        )
                    }
                    Slider(
                        value = displayMs.toFloat().coerceIn(0f, maxMs),
                        onValueChange = { newValue ->
                            isUserScrubbing = true
                            sliderPositionMs = newValue
                        },
                        onValueChangeFinished = {
                            isUserScrubbing = false
                            mediaPlayer?.let { mp ->
                                try {
                                    mp.seekTo(sliderPositionMs.toInt())
                                    currentPositionMs = sliderPositionMs.toInt()
                                } catch (e: Exception) {
                                    e.printStackTrace()
                                }
                            }
                        },
                        valueRange = 0f..maxMs,
                        colors = SliderDefaults.colors(
                            thumbColor = Color.White,
                            activeTrackColor = accent,
                            inactiveTrackColor = progressBg,
                            activeTickColor = Color.Transparent,
                            inactiveTickColor = Color.Transparent
                        ),
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(12.dp)
                    )
                }

                Spacer(modifier = Modifier.height(32.dp))
                
                // Controls
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 4.dp, vertical = 8.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(modifier = Modifier.width(40.dp))
                    
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        // Rewind
                        Box(
                            modifier = Modifier
                                .size(48.dp)
                                .clip(CircleShape)
                                .background(glassBg)
                                .clickable {
                                    mediaPlayer?.let { mp ->
                                        val newPos = (mp.currentPosition - 5000).coerceAtLeast(0)
                                        mp.seekTo(newPos)
                                        currentPositionMs = newPos
                                    }
                                }
                                .border(1.dp, glassBorder, CircleShape),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Filled.SkipPrevious,
                                contentDescription = "Rewind",
                                tint = textMain,
                                modifier = Modifier.size(24.dp)
                            )
                        }

                        // Play/Pause
                        Box(
                            modifier = Modifier
                                .size(80.dp)
                                .clip(CircleShape)
                                .background(glassBg)
                                .clickable {
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
                                }
                                .border(1.dp, glassBorder, CircleShape),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = if (isPlaying) Icons.Filled.Pause else Icons.Filled.PlayArrow,
                                contentDescription = if (isPlaying) "Pause" else "Play",
                                tint = textMain,
                                modifier = Modifier.size(40.dp).padding(start = if (isPlaying) 0.dp else 4.dp)
                            )
                        }

                        // Forward
                        Box(
                            modifier = Modifier
                                .size(48.dp)
                                .clip(CircleShape)
                                .background(glassBg)
                                .clickable {
                                    mediaPlayer?.let { mp ->
                                        val newPos = (mp.currentPosition + 5000).coerceAtMost(mp.duration)
                                        mp.seekTo(newPos)
                                        currentPositionMs = newPos
                                    }
                                }
                                .border(1.dp, glassBorder, CircleShape),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Filled.SkipNext,
                                contentDescription = "Forward",
                                tint = textMain,
                                modifier = Modifier.size(24.dp)
                            )
                        }
                    }

                    // Repeat
                    Box(
                        modifier = Modifier
                            .size(40.dp)
                            .clip(CircleShape)
                            .clickable(
                                interactionSource = remember { MutableInteractionSource() },
                                indication = null
                            ) {
                                isLooping = !isLooping
                                mediaPlayer?.let { mp ->
                                    mp.isLooping = isLooping
                                }
                            },
                        contentAlignment = Alignment.Center
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Icon(
                                imageVector = Icons.Filled.Repeat,
                                contentDescription = "Repeat",
                                tint = if (isLooping) accent else textMuted,
                                modifier = Modifier.size(20.dp)
                            )
                            if (isLooping) {
                                Box(modifier = Modifier
                                    .padding(top = 4.dp)
                                    .size(4.dp)
                                    .clip(CircleShape)
                                    .background(accent)
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
"""

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

start_str = "@Composable\nfun SpotifyMusicPlayer("
start_idx = content.find(start_str)

if start_idx != -1:
    brackets = 0
    in_fun = False
    end_idx = -1
    for i in range(start_idx, len(content)):
        if content[i] == '{':
            brackets += 1
            in_fun = True
        elif content[i] == '}':
            brackets -= 1
        
        if in_fun and brackets == 0:
            end_idx = i + 1
            break
            
    if end_idx != -1:
        new_content = content[:start_idx] + compose_code.strip() + "\n" + content[end_idx:]
        
        imports = [
            "import androidx.compose.material.icons.filled.SkipNext",
            "import androidx.compose.material.icons.filled.SkipPrevious"
        ]
        
        for imp in imports:
            if imp not in new_content:
                new_content = new_content.replace("import androidx.compose.material.icons.filled.PlayArrow", f"{imp}\nimport androidx.compose.material.icons.filled.PlayArrow")

        with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
            f.write(new_content)
        print("Replaced successfully")
    else:
        print("End not found")
else:
    print("Start not found")
