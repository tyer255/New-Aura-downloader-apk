import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

box_target = """                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(if (showLyrics) 350.dp else 56.dp)
                            .animateContentSize()
                            .clip(RoundedCornerShape(24.dp))
                            .background(glassBg)
                            .clickable { if (!showLyrics) showLyrics = true }
                    ) {"""

box_repl = """                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .then(if (showLyrics) Modifier.weight(1f) else Modifier.height(56.dp))
                            .clip(RoundedCornerShape(24.dp))
                            .background(glassBg)
                            .clickable { if (!showLyrics) showLyrics = true }
                    ) {"""
content = content.replace(box_target, box_repl)

text_target = """                                            val targetFontSize = if (isActive) 28f else 22f
                                            val targetAlpha = if (isActive) 1.0f else 0.3f
                                            
                                            val animatedFontSize by androidx.compose.animation.core.animateFloatAsState(
                                                targetValue = targetFontSize,
                                                animationSpec = androidx.compose.animation.core.spring(dampingRatio = 0.65f, stiffness = 200f)
                                            )
                                            val animatedAlpha by androidx.compose.animation.core.animateFloatAsState(
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

text_repl = """                                            val targetAlpha = if (isActive) 1.0f else 0.4f
                                            
                                            val animatedAlpha by androidx.compose.animation.core.animateFloatAsState(
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
                                                fontWeight = FontWeight.Bold,
                                                fontSize = 24.sp,
                                                lineHeight = 32.sp,
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
content = content.replace(text_target, text_repl)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
