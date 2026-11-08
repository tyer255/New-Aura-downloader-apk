package com.auradownloader.app

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.*
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
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.Pause
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.blur
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawWithContent
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.*
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.compose.ui.zIndex
import coil.compose.AsyncImage
import kotlinx.coroutines.launch

data class LrcLine(val timeMs: Long, val text: String)

/**
 * Parses LRC formatted string into a strictly ordered list of [LrcLine].
 * Accurately parses standard [mm:ss.xx], [mm:ss:xx], [m:ss.xxx], [mm:ss] timestamp tags.
 * If the input is plain lyrics (without timestamp tags), each line is assigned a calculated
 * timestamp distributed evenly across the track duration, preventing lyrics from collapsing
 * into an unformatted single paragraph block.
 */
fun parseLrc(lrcText: String, durationMs: Long = 0L): List<LrcLine> {
    if (lrcText.isBlank()) return emptyList()

    val rawLines = lrcText.split("\n")
    val result = mutableListOf<LrcLine>()

    // Global offset tag [offset:+/-ms]
    val offsetRegex = Regex("""\[offset:\s*([+-]?\d+)]""", RegexOption.IGNORE_CASE)
    var globalOffsetMs = 0L
    for (line in rawLines) {
        val match = offsetRegex.find(line)
        if (match != null) {
            globalOffsetMs = match.groupValues[1].toLongOrNull() ?: 0L
        }
    }

    // Time tag regex: [mm:ss.xx], [mm:ss:xx], [mm:ss], [m:ss.xxx]
    val timeRegex = Regex("""\[(\d{1,3}):(\d{1,2})(?:[:.](\d{1,3}))?\]""")

    for (line in rawLines) {
        val trimmed = line.trim()
        if (trimmed.isEmpty()) continue

        // Skip metadata header tags like [ti:], [ar:], [al:], [by:], [length:], etc.
        if (trimmed.startsWith("[") && !trimmed.matches(Regex("""^\[\d{1,3}:\d{1,2}.*"""))) {
            continue
        }

        val matches = timeRegex.findAll(line).toList()
        if (matches.isNotEmpty()) {
            val cleanText = line.replace(timeRegex, "").trim()
            if (cleanText.isNotEmpty()) {
                for (match in matches) {
                    val min = match.groupValues[1].toLongOrNull() ?: 0L
                    val sec = match.groupValues[2].toLongOrNull() ?: 0L
                    val fracStr = match.groupValues.getOrNull(3) ?: ""
                    val ms = when (fracStr.length) {
                        1 -> (fracStr.toLongOrNull() ?: 0L) * 100
                        2 -> (fracStr.toLongOrNull() ?: 0L) * 10
                        3 -> (fracStr.toLongOrNull() ?: 0L)
                        else -> 0L
                    }
                    val timeMs = (min * 60000L + sec * 1000L + ms + globalOffsetMs).coerceAtLeast(0L)
                    result.add(LrcLine(timeMs, cleanText))
                }
            }
        }
    }

    if (result.isNotEmpty()) {
        return result.sortedBy { it.timeMs }
    }

    // If no timestamp tags were present, divide every non-empty line evenly across the song duration
    val plainLines = rawLines.map { it.trim() }.filter { it.isNotEmpty() && !it.startsWith("[") }
    if (plainLines.isNotEmpty()) {
        val effectiveDuration = if (durationMs > 10000L) durationMs else (plainLines.size * 3500L)
        val timeStep = (effectiveDuration * 0.90f / plainLines.size).toLong().coerceAtLeast(2000L)
        val startTime = (effectiveDuration * 0.05f).toLong()
        return plainLines.mapIndexed { index, text ->
            LrcLine(startTime + index * timeStep, text)
        }
    }

    return emptyList()
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
    
    // Snappy lookup matching the 200ms threshold from the player template
    val activeIndex = remember(currentPositionMs, parsedLyrics, offsetMs) {
        val targetPos = currentPositionMs + 200L
        parsedLyrics.indexOfLast { it.timeMs + offsetMs <= targetPos }
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
            // Timing Offset Adjustment Controls
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

            // Dismiss Button
            IconButton(
                onClick = onClose,
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .padding(top = 48.dp, end = 16.dp)
                    .zIndex(10f)
            ) {
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .background(Color(0x33FFFFFF), CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Filled.KeyboardArrowDown,
                        contentDescription = "Close Lyrics",
                        tint = Color.White,
                        modifier = Modifier.size(28.dp)
                    )
                }
            }

            // Cinematic Mask Brush for Top & Bottom Fade (10% to 90%)
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
                contentPadding = PaddingValues(top = 340.dp, bottom = 360.dp, start = 24.dp, end = 24.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                if (parsedLyrics.isEmpty()) {
                    item {
                        Text(
                            text = "No lyrics found for this track.",
                            color = Color.White.copy(alpha = 0.7f),
                            fontSize = 24.sp,
                            fontWeight = FontWeight.SemiBold,
                            textAlign = TextAlign.Center,
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 32.dp)
                        )
                    }
                } else {
                    items(parsedLyrics.size) { index ->
                        val line = parsedLyrics[index]
                        val isActive = index == activeIndex

                        // 0.5s ease-out animation matching the template specs
                        val animatedAlpha by animateFloatAsState(
                            targetValue = if (isActive) 1f else 0.4f,
                            animationSpec = tween(durationMillis = 500, easing = FastOutSlowInEasing),
                            label = "alpha"
                        )

                        val animatedScale by animateFloatAsState(
                            targetValue = if (isActive) 1.0f else 0.98f,
                            animationSpec = tween(durationMillis = 500, easing = FastOutSlowInEasing),
                            label = "scale"
                        )

                        val animatedBlur by animateFloatAsState(
                            targetValue = if (isActive) 0f else 1.0f,
                            animationSpec = tween(durationMillis = 500, easing = FastOutSlowInEasing),
                            label = "blur"
                        )

                        Text(
                            text = line.text,
                            color = Color.White,
                            fontWeight = if (isActive) FontWeight.ExtraBold else FontWeight.Bold,
                            fontSize = 32.sp,
                            lineHeight = 42.sp,
                            letterSpacing = (-0.02).sp,
                            textAlign = TextAlign.Start,
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 8.dp)
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
                                    onSeek(line.timeMs.toInt())
                                }
                        )
                    }
                }
            }

            // Bottom Glass Player Dock
            GlassDockPlayer(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(bottom = 24.dp, start = 16.dp, end = 16.dp)
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
            .shadow(30.dp, RoundedCornerShape(24.dp), ambientColor = Color.Black, spotColor = Color.Black)
            .clip(RoundedCornerShape(24.dp))
            .background(Color(0x66191919))
            .border(1.dp, Color.White.copy(alpha = 0.1f), RoundedCornerShape(24.dp))
            .padding(horizontal = 20.dp, vertical = 18.dp)
    ) {
        Column {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.fillMaxWidth()
            ) {
                // Album Art / Gradient fallback
                Box(
                    modifier = Modifier
                        .size(48.dp)
                        .clip(RoundedCornerShape(8.dp))
                        .background(
                            Brush.linearGradient(
                                listOf(Color(0xFFA855F7), Color(0xFFEC4899))
                            )
                        )
                ) {
                    if (thumbnailUrl.isNotEmpty()) {
                        AsyncImage(
                            model = coil.request.ImageRequest.Builder(LocalContext.current)
                                .data(thumbnailUrl)
                                .crossfade(true)
                                .build(),
                            contentDescription = "Album Cover",
                            contentScale = ContentScale.Crop,
                            modifier = Modifier.fillMaxSize()
                        )
                    }
                }

                Spacer(modifier = Modifier.width(16.dp))

                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = title.ifEmpty { "Track Title" },
                        color = Color.White,
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                    Text(
                        text = if (!artist.isNullOrEmpty()) artist else "Artist Name",
                        color = Color(0xFFD1D5DB),
                        fontSize = 13.sp,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }

                Spacer(modifier = Modifier.width(16.dp))

                // Circular play/pause button with white glow shadow
                Box(
                    modifier = Modifier
                        .size(56.dp)
                        .shadow(16.dp, CircleShape, spotColor = Color.White.copy(alpha = 0.5f), ambientColor = Color.White.copy(alpha = 0.3f))
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
                    modifier = Modifier.width(36.dp),
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
                        inactiveTrackColor = Color.White.copy(alpha = 0.15f),
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
                    modifier = Modifier.width(36.dp),
                    textAlign = TextAlign.Start
                )
            }
        }
    }
}

/**
 * Standard SyncedLyricsView used inside sheets and modal dialogs.
 */
@Composable
fun SyncedLyricsView(
    lyrics: String,
    currentPositionMs: Long,
    offsetMs: Long,
    onOffsetChange: ((Long) -> Unit)?,
    activeColor: Color,
    textColor: Color
) {
    val parsedLyrics = remember(lyrics) { parseLrc(lyrics, 0L) }

    if (parsedLyrics.isEmpty()) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(32.dp),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "No lyrics found for this track.",
                color = textColor.copy(alpha = 0.7f),
                style = MaterialTheme.typography.bodyLarge,
                textAlign = TextAlign.Center
            )
        }
        return
    }

    val listState = rememberLazyListState()

    val currentIndex = remember(currentPositionMs, parsedLyrics, offsetMs) {
        val targetPos = currentPositionMs + 200L
        parsedLyrics.indexOfLast { it.timeMs + offsetMs <= targetPos }
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
            modifier = Modifier
                .fillMaxWidth()
                .heightIn(max = 450.dp),
            contentPadding = PaddingValues(vertical = 24.dp)
        ) {
            items(parsedLyrics.size) { index ->
                val line = parsedLyrics[index]
                val isActive = index == currentIndex

                val animatedAlpha by animateFloatAsState(
                    targetValue = if (isActive) 1f else 0.4f,
                    animationSpec = tween(durationMillis = 300),
                    label = "sheet_alpha"
                )
                val animatedSize by animateFloatAsState(
                    targetValue = if (isActive) 22f else 18f,
                    animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy, stiffness = Spring.StiffnessLow),
                    label = "sheet_size"
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
