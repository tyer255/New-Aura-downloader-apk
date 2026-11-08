import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

# 1. Add LyricsCache object
cache_code = """object LyricsCache {
    private val cache = android.util.LruCache<String, List<LyricLine>>(20)
    fun getParsedLyrics(lrc: String?): List<LyricLine> {
        if (lrc.isNullOrEmpty()) return emptyList()
        cache.get(lrc)?.let { return it }
        val parsed = parseLrc(lrc)
        cache.put(lrc, parsed)
        return parsed
    }
}

fun parseLrc"""

content = content.replace("fun parseLrc", cache_code)

# 2. Update remember to use LyricsCache
content = content.replace("val parsedLyrics = remember(syncedLyrics) { parseLrc(syncedLyrics) }", "val parsedLyrics = remember(syncedLyrics) { LyricsCache.getParsedLyrics(syncedLyrics) }")

# 3. Add glow effect
glow_target = """                                            val animatedAlpha by androidx.compose.animation.core.animateFloatAsState(
                                                targetValue = targetAlpha,
                                                animationSpec = androidx.compose.animation.core.tween(durationMillis = 300)
                                            )
                                            
                                            Text(
                                                text = line.text,
                                                color = textMain.copy(alpha = animatedAlpha),
                                                fontWeight = if (isActive) FontWeight.ExtraBold else FontWeight.Medium,
                                                fontSize = animatedFontSize.sp,
                                                lineHeight = (animatedFontSize * 1.3f).sp,
                                                modifier = Modifier
                                                    .fillMaxWidth()
                                                    .padding(vertical = 12.dp, horizontal = 12.dp)
                                                    .clickable {
                                                        MusicController.seekTo(line.timeMs.toInt())
                                                    }
                                            )"""

glow_repl = """                                            val animatedAlpha by androidx.compose.animation.core.animateFloatAsState(
                                                targetValue = targetAlpha,
                                                animationSpec = androidx.compose.animation.core.tween(durationMillis = 300)
                                            )
                                            
                                            val glowRadius by androidx.compose.animation.core.animateFloatAsState(
                                                targetValue = if (isActive) 12f else 0f,
                                                animationSpec = androidx.compose.animation.core.tween(durationMillis = 300)
                                            )
                                            
                                            Text(
                                                text = line.text,
                                                color = textMain.copy(alpha = animatedAlpha),
                                                fontWeight = if (isActive) FontWeight.ExtraBold else FontWeight.Medium,
                                                fontSize = animatedFontSize.sp,
                                                lineHeight = (animatedFontSize * 1.3f).sp,
                                                style = androidx.compose.ui.text.TextStyle(
                                                    shadow = if (isActive) androidx.compose.ui.graphics.Shadow(
                                                        color = textMain.copy(alpha = 0.5f),
                                                        blurRadius = glowRadius,
                                                        offset = androidx.compose.ui.geometry.Offset.Zero
                                                    ) else null
                                                ),
                                                modifier = Modifier
                                                    .fillMaxWidth()
                                                    .padding(vertical = 12.dp, horizontal = 12.dp)
                                                    .clickable {
                                                        MusicController.seekTo(line.timeMs.toInt())
                                                    }
                                            )"""

content = content.replace(glow_target, glow_repl)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
