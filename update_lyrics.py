with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

target = """                                            val scale by androidx.compose.animation.core.animateFloatAsState(if (isActive) 1.05f else 1.0f)
                                            val alpha by androidx.compose.animation.core.animateFloatAsState(if (isActive) 1.0f else 0.4f)
                                            
                                            Text(
                                                text = line.text,
                                                color = textMain.copy(alpha = alpha),
                                                fontWeight = if (isActive) FontWeight.Bold else FontWeight.Normal,
                                                fontSize = 18.sp,
                                                modifier = Modifier
                                                    .fillMaxWidth()
                                                    .padding(vertical = 8.dp)
                                                    .graphicsLayer {
                                                        scaleX = scale
                                                        scaleY = scale
                                                        transformOrigin = androidx.compose.ui.graphics.TransformOrigin(0f, 0.5f)
                                                    }
                                                    .clickable {
                                                        MusicController.seekTo(line.timeMs.toInt())
                                                    }
                                            )"""

replacement = """                                            val targetScale = if (isActive) 1.15f else 1.0f
                                            val targetAlpha = if (isActive) 1.0f else 0.35f
                                            val scale by androidx.compose.animation.core.animateFloatAsState(
                                                targetValue = targetScale,
                                                animationSpec = androidx.compose.animation.core.spring(dampingRatio = 0.8f, stiffness = 100f)
                                            )
                                            val alpha by androidx.compose.animation.core.animateFloatAsState(
                                                targetValue = targetAlpha,
                                                animationSpec = androidx.compose.animation.core.tween(durationMillis = 350)
                                            )
                                            
                                            Text(
                                                text = line.text,
                                                color = textMain.copy(alpha = alpha),
                                                fontWeight = if (isActive) FontWeight.Bold else FontWeight.SemiBold,
                                                fontSize = 22.sp,
                                                lineHeight = 28.sp,
                                                modifier = Modifier
                                                    .fillMaxWidth()
                                                    .padding(vertical = 12.dp, horizontal = 8.dp)
                                                    .graphicsLayer {
                                                        scaleX = scale
                                                        scaleY = scale
                                                        transformOrigin = androidx.compose.ui.graphics.TransformOrigin(0f, 0.5f)
                                                    }
                                                    .clickable {
                                                        MusicController.seekTo(line.timeMs.toInt())
                                                    }
                                            )"""

content = content.replace(target, replacement)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
