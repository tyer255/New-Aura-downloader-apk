package com.auradownloader.app

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.*
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Fullscreen
import androidx.compose.material.icons.filled.GraphicEq
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.MusicNote
import androidx.compose.material.icons.filled.Pause
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.blur
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawWithContent
import androidx.compose.ui.graphics.*
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.zIndex
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import coil.compose.AsyncImage
import kotlinx.coroutines.launch

data class LrcLine(val timeMs: Long, val text: String)

fun parseLrc(lrcText: String, durationMs: Long = 0L): List<LrcLine> {
    val lines = lrcText.split("\n")
    val result = mutableListOf<LrcLine>()
    
    // Check for global offset tag [offset:+/-ms]
    val offsetRegex = Regex("""\[offset:\s*([+-]?\d+)]""", RegexOption.IGNORE_CASE)
    var globalOffsetMs = 0L
    for (line in lines) {
        val offsetMatch = offsetRegex.find(line)
        if (offsetMatch != null) {
            globalOffsetMs = offsetMatch.groupValues[1].toLongOrNull() ?: 0L
        }
    }

    // Support standard [mm:ss.xx], [mm:ss:xx], [mm:ss], etc.
    val timeRegex = Regex("""\[(\d{1,3}):(\d{1,2})(?:[:.](\d{1,3}))?\]""")
    
    for (line in lines) {
        val matches = timeRegex.findAll(line).toList()
        if (matches.isNotEmpty()) {
            val cleanText = line.replace(timeRegex, "").trim()
            for (match in matches) {
                val min = match.groupValues[1].toLong()
                val sec = match.groupValues[2].toLong()
                val fracStr = match.groupValues.getOrNull(3) ?: ""
                val ms = when (fracStr.length) {
                    1 -> fracStr.toLong() * 100
                    2 -> fracStr.toLong() * 10
                    3 -> fracStr.toLong()
                    else -> 0L
                }
                val timeMs = (min * 60000 + sec * 1000 + ms + globalOffsetMs).coerceAtLeast(0L)
                val displayText = if (cleanText.isEmpty()) "♪" else cleanText
                result.add(LrcLine(timeMs, displayText))
            }
        }
    }
    
    return result.sortedBy { it.timeMs }
}

@Composable
fun ImmersiveLyricsScreen(
    lyrics: String,
    currentPositionMs: Long,
    durationMs: Long,
    offsetMs: Long,
    onOffsetChange: (Long) -> Unit,
    isPlaying: Boolean,
    title: String,
    artist: String?,
    thumbnailUrl: String,
    onPlayPause: () -> Unit,
    onSeek: (Int) -> Unit,
    onClose: () -> Unit
) {
    
    val parsedLyrics = remember(lyrics, durationMs) { parseLrc(lyrics, durationMs) }
    val activeIndex = remember(currentPositionMs, parsedLyrics, offsetMs) {
        parsedLyrics.indexOfLast { it.timeMs <= currentPositionMs + offsetMs }
    }

    val bgColors = listOf(
        Color(0xFF1E1014),
        Color(0xFF0D141F),
        Color(0xFF170E1C),
        Color(0xFF1C140D),
        Color(0xFF0E1712),
        Color(0xFF121212)
    )

    val targetBgColor = if (activeIndex >= 0) bgColors[activeIndex % bgColors.size] else bgColors.last()
    val animatedBgColor by animateColorAsState(
        targetValue = targetBgColor,
        animationSpec = tween(durationMillis = 2000, easing = FastOutSlowInEasing),
        label = "bg_color"
    )

    Dialog(
        onDismissRequest = onClose,
        properties = DialogProperties(usePlatformDefaultWidth = false, decorFitsSystemWindows = false)
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(animatedBgColor)
        ) {
            // Sync Controls
            Row(
                modifier = Modifier
                    .align(Alignment.TopStart)
                    .padding(top = 48.dp, start = 16.dp)
                    .zIndex(10f)
                    .background(Color(0x33FFFFFF), RoundedCornerShape(20.dp))
                    .padding(horizontal = 8.dp, vertical = 4.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(onClick = { onOffsetChange(offsetMs - 500L) }, modifier = Modifier.size(32.dp)) {
                    Text("-", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 20.sp)
                }
                Text(
                    text = "${if (offsetMs >= 0) "+" else ""}${offsetMs / 1000f}s",
                    color = Color.White,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium,
                    modifier = Modifier.padding(horizontal = 8.dp)
                )
                IconButton(onClick = { onOffsetChange(offsetMs + 500L) }, modifier = Modifier.size(32.dp)) {
                    Text("+", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 20.sp)
                }
            }

            // Close Button
            IconButton(
                onClick = onClose,
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .padding(top = 48.dp, end = 16.dp)
                    .zIndex(10f)
            ) {
                Box(
                    modifier = Modifier.size(40.dp).background(Color(0x33FFFFFF), CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(Icons.Filled.KeyboardArrowDown, contentDescription = "Close", tint = Color.White, modifier = Modifier.size(28.dp))
                }
            }

            // Cinematic Mask Brush
            val maskBrush = Brush.verticalGradient(
                0.0f to Color.Transparent,
                0.10f to Color.Black,
                0.90f to Color.Black,
                1.0f to Color.Transparent
            )

            val listState = rememberLazyListState()
            val coroutineScope = rememberCoroutineScope()

            LaunchedEffect(activeIndex) {
                if (activeIndex >= 0) {
                    coroutineScope.launch {
                        listState.animateScrollToItem(maxOf(0, activeIndex))
                    }
                }
            }

            LazyColumn(
                state = listState,
                modifier = Modifier
                    .fillMaxSize()
                    .graphicsLayer { compositingStrategy = CompositingStrategy.Offscreen }
                    .drawWithContent {
                        drawContent()
                        drawRect(brush = maskBrush, blendMode = BlendMode.DstIn)
                    },
                contentPadding = PaddingValues(top = 350.dp, bottom = 350.dp, start = 24.dp, end = 24.dp),
                verticalArrangement = Arrangement.spacedBy(24.dp)
            ) {
                if (parsedLyrics.isEmpty()) {
                    item {
                        Text(
                            text = lyrics.ifEmpty { "No lyrics found." },
                            color = Color.White,
                            fontSize = 24.sp,
                            fontWeight = FontWeight.Bold,
                            lineHeight = 34.sp
                        )
                    }
                } else {
                    items(parsedLyrics.size) { index ->
                        val line = parsedLyrics[index]
                        val isActive = index == activeIndex
                        
                        val animatedAlpha by animateFloatAsState(
                            targetValue = if (isActive) 1f else 0.4f,
                            animationSpec = tween(durationMillis = 150, easing = FastOutSlowInEasing),
                            label = "alpha"
                        )
                        
                        val animatedScale by animateFloatAsState(
                            targetValue = if (isActive) 1f else 0.98f,
                            animationSpec = tween(durationMillis = 150, easing = FastOutSlowInEasing),
                            label = "scale"
                        )

                        val animatedBlur by animateFloatAsState(
                            targetValue = if (isActive) 0f else 1f,
                            animationSpec = tween(durationMillis = 150, easing = FastOutSlowInEasing),
                            label = "blur"
                        )
                        
                        Text(
                            text = line.text,
                            color = Color.White,
                            fontWeight = if (isActive) FontWeight.ExtraBold else FontWeight.Bold,
                            fontSize = 32.sp,
                            lineHeight = 40.sp,
                            letterSpacing = (-0.02).sp,
                            textAlign = TextAlign.Start,
                            modifier = Modifier
                                .fillMaxWidth()
                                .graphicsLayer {
                                    scaleX = animatedScale
                                    scaleY = animatedScale
                                    transformOrigin = TransformOrigin(0f, 0.5f)
                                    alpha = animatedAlpha
                                }
                                .blur(if (animatedBlur > 0.1f) animatedBlur.dp else 0.dp)
                                .clickable(
                                    interactionSource = remember { MutableInteractionSource() },
                                    indication = null
                                ) {
                                    onSeek((line.timeMs - offsetMs).toInt().coerceAtLeast(0))
                                }
                        )
                    }
                }
            }

            // Bottom Glass Player Dock
            GlassDockPlayer(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(bottom = 32.dp, start = 16.dp, end = 16.dp)
                    .navigationBarsPadding(),
                title = title,
                artist = artist,
                thumbnailUrl = thumbnailUrl,
                isPlaying = isPlaying,
                currentPositionMs = currentPositionMs,
                durationMs = durationMs,
                onPlayPause = onPlayPause,
                onSeek = onSeek
            )
        }
    }
}

@Composable
fun GlassDockPlayer(
    modifier: Modifier = Modifier,
    title: String,
    artist: String?,
    thumbnailUrl: String,
    isPlaying: Boolean,
    currentPositionMs: Long,
    durationMs: Long,
    onPlayPause: () -> Unit,
    onSeek: (Int) -> Unit
) {
    var isUserScrubbing by remember { mutableStateOf(false) }
    var sliderPositionMs by remember { mutableFloatStateOf(0f) }
    
    val displayMs = if (isUserScrubbing) sliderPositionMs.toInt() else currentPositionMs.toInt()
    val maxMs = if (durationMs > 0) durationMs.toFloat() else 1f

    Box(
        modifier = modifier
            .fillMaxWidth()
            .shadow(24.dp, RoundedCornerShape(24.dp))
            .clip(RoundedCornerShape(24.dp))
            .background(Color(0x66191919)) // rgba(25, 25, 25, 0.4)
            .border(1.dp, Color.White.copy(alpha = 0.1f), RoundedCornerShape(24.dp))
            .padding(20.dp)
    ) {
        Column {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.fillMaxWidth()
            ) {
                AsyncImage(
                    model = coil.request.ImageRequest.Builder(LocalContext.current).data(thumbnailUrl).build(),
                    contentDescription = "Album Cover",
                    contentScale = ContentScale.Crop,
                    modifier = Modifier
                        .size(48.dp)
                        .clip(RoundedCornerShape(8.dp))
                )
                
                Spacer(modifier = Modifier.width(16.dp))
                
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = title,
                        color = Color.White,
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                    if (!artist.isNullOrEmpty()) {
                        Text(
                            text = artist,
                            color = Color(0xFFD1D5DB),
                            fontSize = 14.sp,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                    }
                }
                
                Spacer(modifier = Modifier.width(16.dp))
                
                Box(
                    modifier = Modifier
                        .size(56.dp)
                        .shadow(12.dp, CircleShape, spotColor = Color.White, ambientColor = Color.White)
                        .background(Color.White, CircleShape)
                        .clip(CircleShape)
                        .clickable { onPlayPause() },
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = if (isPlaying) Icons.Filled.Pause else Icons.Filled.PlayArrow,
                        contentDescription = "Play/Pause",
                        tint = Color.Black,
                        modifier = Modifier
                            .size(32.dp)
                            .padding(start = if (isPlaying) 0.dp else 4.dp)
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = formatTimeMs(displayMs),
                    color = Color(0xFF9CA3AF),
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Medium,
                    modifier = Modifier.width(40.dp),
                    textAlign = TextAlign.End
                )
                
                Spacer(modifier = Modifier.width(12.dp))
                
                Slider(
                    value = displayMs.toFloat().coerceIn(0f, maxMs),
                    onValueChange = { newValue ->
                        isUserScrubbing = true
                        sliderPositionMs = newValue
                    },
                    onValueChangeFinished = {
                        isUserScrubbing = false
                        onSeek(sliderPositionMs.toInt())
                    },
                    valueRange = 0f..maxMs,
                    colors = SliderDefaults.colors(
                        thumbColor = Color.White,
                        activeTrackColor = Color.White,
                        inactiveTrackColor = Color.White.copy(alpha = 0.2f),
                        activeTickColor = Color.Transparent,
                        inactiveTickColor = Color.Transparent
                    ),
                    modifier = Modifier
                        .weight(1f)
                        .height(24.dp)
                )
                
                Spacer(modifier = Modifier.width(12.dp))
                
                Text(
                    text = formatTimeMs(durationMs.toInt()),
                    color = Color(0xFF9CA3AF),
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Medium,
                    modifier = Modifier.width(40.dp),
                    textAlign = TextAlign.Start
                )
            }
        }
    }
}

// Keep the old SyncedLyricsView for compatibility if it's used elsewhere like bottom sheet
@Composable
fun SyncedLyricsView(lyrics: String, currentPositionMs: Long, offsetMs: Long, onOffsetChange: ((Long) -> Unit)?, activeColor: Color, textColor: Color) {
    val parsedLyrics = remember(lyrics) { parseLrc(lyrics, 0L) }
    
    if (parsedLyrics.isEmpty()) {
        LazyColumn(modifier = Modifier.fillMaxWidth().fillMaxHeight(0.7f)) {
            item {
                Text(
                    text = lyrics,
                    color = textColor,
                    style = MaterialTheme.typography.bodyMedium.copy(fontSize = 18.sp, lineHeight = 28.sp),
                    modifier = Modifier.padding(bottom = 32.dp)
                )
            }
        }
        return
    }
    
    val listState = rememberLazyListState()
    
    val currentIndex = remember(currentPositionMs, parsedLyrics, offsetMs) {
        parsedLyrics.indexOfLast { it.timeMs <= currentPositionMs + offsetMs }
    }
    
    LaunchedEffect(currentIndex) {
        if (currentIndex >= 0) {
            listState.animateScrollToItem(index = maxOf(0, currentIndex - 2))
        }
    }
    
    Column(modifier = Modifier.fillMaxWidth()) {
        if (onOffsetChange != null) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 8.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.End
            ) {
                IconButton(onClick = { onOffsetChange(offsetMs - 500L) }, modifier = Modifier.size(32.dp)) {
                    Text("-", color = textColor, fontWeight = FontWeight.Bold, fontSize = 20.sp)
                }
                Text(
                    text = "${if (offsetMs >= 0) "+" else ""}${offsetMs / 1000f}s",
                    color = textColor,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium,
                    modifier = Modifier.padding(horizontal = 8.dp)
                )
                IconButton(onClick = { onOffsetChange(offsetMs + 500L) }, modifier = Modifier.size(32.dp)) {
                    Text("+", color = textColor, fontWeight = FontWeight.Bold, fontSize = 20.sp)
                }
            }
        }
        LazyColumn(
            state = listState,
            modifier = Modifier.fillMaxWidth().weight(1f),
            contentPadding = PaddingValues(vertical = 32.dp)
        ) {
            items(parsedLyrics.size) { index ->
                val line = parsedLyrics[index]
                val isActive = index == currentIndex
                
                val animatedAlpha by animateFloatAsState(
                    targetValue = if (isActive) 1f else 0.4f,
                    animationSpec = tween(durationMillis = 150)
                )
                val animatedSize by animateFloatAsState(
                    targetValue = if (isActive) 24f else 20f,
                    animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy, stiffness = Spring.StiffnessLow)
                )
                
                Text(
                    text = line.text,
                    color = if (isActive) activeColor else textColor,
                    fontWeight = if (isActive) FontWeight.Bold else FontWeight.Medium,
                    fontSize = animatedSize.sp,
                    lineHeight = (animatedSize + 8).sp,
                    modifier = Modifier
                        .fillMaxWidth()
                        .alpha(animatedAlpha)
                        .padding(vertical = 8.dp)
                )
            }
        }
    }
}

@Composable
fun LiveAnimatedLyricsCard(
    lyrics: String?,
    currentPositionMs: Long,
    durationMs: Long,
    offsetMs: Long,
    isLoading: Boolean,
    isDarkMode: Boolean,
    accent: Color,
    onExpandClick: () -> Unit,
    onRetryClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val parsedLyrics = remember(lyrics, durationMs) {
        if (lyrics.isNullOrEmpty()) emptyList() else parseLrc(lyrics, durationMs)
    }

    val hasSyncedLyrics = parsedLyrics.isNotEmpty()
    val activeIndex = remember(currentPositionMs, parsedLyrics, offsetMs) {
        if (!hasSyncedLyrics) -1
        else parsedLyrics.indexOfLast { it.timeMs <= currentPositionMs + offsetMs }
    }

    val cardBg = if (isDarkMode) Color.White.copy(alpha = 0.04f) else Color.White.copy(alpha = 0.60f)
    val cardBorder = if (isDarkMode) Color.White.copy(alpha = 0.08f) else Color.Black.copy(alpha = 0.06f)
    val textPrimary = if (isDarkMode) Color.White else Color(0xFF1E293B)
    val textSecondary = if (isDarkMode) Color(0xFF94A3B8) else Color(0xFF64748B)

    Box(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp))
            .background(cardBg)
            .border(1.dp, cardBorder, RoundedCornerShape(16.dp))
            .clickable(
                onClick = onExpandClick,
                interactionSource = remember { MutableInteractionSource() },
                indication = null
            )
            .padding(14.dp)
    ) {
        Column(modifier = Modifier.fillMaxWidth()) {
            // Header Row
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    Icon(
                        imageVector = if (hasSyncedLyrics) Icons.Filled.GraphicEq else Icons.Filled.MusicNote,
                        contentDescription = "Lyrics",
                        tint = accent,
                        modifier = Modifier.size(16.dp)
                    )
                    Text(
                        text = if (hasSyncedLyrics) "LIVE SYNCED LYRICS" else "LYRICS",
                        color = accent,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        letterSpacing = 1.sp
                    )
                }

                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    if (lyrics.isNullOrEmpty() && !isLoading) {
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(8.dp))
                                .background(accent.copy(alpha = 0.12f))
                                .clickable { onRetryClick() }
                                .padding(horizontal = 8.dp, vertical = 2.dp)
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(4.dp)
                            ) {
                                Icon(
                                    imageVector = Icons.Filled.Refresh,
                                    contentDescription = "Search",
                                    tint = accent,
                                    modifier = Modifier.size(12.dp)
                                )
                                Text(
                                    text = "Sync",
                                    color = accent,
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.SemiBold
                                )
                            }
                        }
                    }

                    if (!lyrics.isNullOrEmpty()) {
                        IconButton(
                            onClick = onExpandClick,
                            modifier = Modifier.size(24.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Filled.Fullscreen,
                                contentDescription = "Full Screen",
                                tint = textSecondary,
                                modifier = Modifier.size(18.dp)
                            )
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            when {
                isLoading -> {
                    val infiniteTransition = rememberInfiniteTransition(label = "shimmer")
                    val alpha by infiniteTransition.animateFloat(
                        initialValue = 0.3f,
                        targetValue = 0.8f,
                        animationSpec = infiniteRepeatable(
                            animation = tween(800, easing = LinearEasing),
                            repeatMode = RepeatMode.Reverse
                        ),
                        label = "shimmerAlpha"
                    )
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.Center
                    ) {
                        Text(
                            text = "♪ Finding synchronized lyrics...",
                            color = textSecondary.copy(alpha = alpha),
                            fontSize = 13.sp,
                            fontWeight = FontWeight.Medium
                        )
                    }
                }

                hasSyncedLyrics -> {
                    val prevLine = if (activeIndex > 0) parsedLyrics.getOrNull(activeIndex - 1)?.text else null
                    val currentLine = if (activeIndex >= 0) parsedLyrics.getOrNull(activeIndex)?.text else "♪ Instrumental ♪"
                    val nextLine = if (activeIndex >= 0) parsedLyrics.getOrNull(activeIndex + 1)?.text else parsedLyrics.firstOrNull()?.text

                    Column(
                        modifier = Modifier.fillMaxWidth(),
                        verticalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        if (!prevLine.isNullOrEmpty()) {
                            Text(
                                text = prevLine,
                                color = textSecondary.copy(alpha = 0.45f),
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Normal,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis
                            )
                        }

                        AnimatedContent(
                            targetState = currentLine ?: "♪ ♪ ♪",
                            transitionSpec = {
                                fadeIn(animationSpec = tween(180)) togetherWith fadeOut(animationSpec = tween(140))
                            },
                            label = "lyricLine"
                        ) { targetText ->
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(8.dp))
                                    .background(accent.copy(alpha = 0.12f))
                                    .border(1.dp, accent.copy(alpha = 0.3f), RoundedCornerShape(8.dp))
                                    .padding(horizontal = 10.dp, vertical = 6.dp),
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(6.dp)
                                        .background(accent, CircleShape)
                                )
                                Text(
                                    text = targetText,
                                    color = textPrimary,
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.Bold,
                                    lineHeight = 19.sp,
                                    maxLines = 2,
                                    overflow = TextOverflow.Ellipsis,
                                    modifier = Modifier.weight(1f)
                                )
                            }
                        }

                        if (!nextLine.isNullOrEmpty()) {
                            Text(
                                text = nextLine,
                                color = textSecondary.copy(alpha = 0.65f),
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Normal,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis
                            )
                        }
                    }
                }

                !lyrics.isNullOrEmpty() -> {
                    // Plain text lyrics
                    val sample = lyrics.lines().take(3).joinToString("\n") { it.trim() }.ifEmpty { lyrics.take(120) }
                    Text(
                        text = sample,
                        color = textPrimary,
                        fontSize = 13.sp,
                        lineHeight = 18.sp,
                        maxLines = 3,
                        overflow = TextOverflow.Ellipsis
                    )
                }

                else -> {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 4.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.Center
                    ) {
                        Text(
                            text = "Tap to load synchronized lyrics",
                            color = textSecondary,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Normal
                        )
                    }
                }
            }
        }
    }
}

