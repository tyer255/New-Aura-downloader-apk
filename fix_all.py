import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

# 1. Replace the DropdownMenu with a custom Popup and real share intent
menu_target = """                        androidx.compose.material3.DropdownMenu(
                            expanded = showOptionsMenu,
                            onDismissRequest = { showOptionsMenu = false },
                            modifier = Modifier.background(if(isDarkMode) glassBg else Color.White).border(1.dp, glassBorder, RoundedCornerShape(16.dp))
                        ) {
                            androidx.compose.material3.DropdownMenuItem(
                                text = { Text("Show Lyrics", color = textMain) },
                                leadingIcon = { Icon(Icons.Filled.Notes, null, tint = textMain) },
                                onClick = { showOptionsMenu = false; showLyrics = true }
                            )
                            androidx.compose.material3.DropdownMenuItem(
                                text = { Text("Share", color = Color(0xFFF87171)) },
                                leadingIcon = { Icon(Icons.Filled.Share, null, tint = Color(0xFFF87171)) },
                                onClick = { showOptionsMenu = false; Toast.makeText(context, "Sharing...", Toast.LENGTH_SHORT).show() }
                            )
                        }"""

menu_repl = """                        if (showOptionsMenu) {
                            androidx.compose.ui.window.Popup(
                                alignment = Alignment.TopEnd,
                                onDismissRequest = { showOptionsMenu = false },
                                offset = androidx.compose.ui.unit.IntOffset(-40, 120)
                            ) {
                                Column(
                                    modifier = Modifier
                                        .width(200.dp)
                                        .clip(RoundedCornerShape(24.dp))
                                        .background(glassBg)
                                        .border(1.dp, glassBorder, RoundedCornerShape(24.dp))
                                        .padding(8.dp)
                                ) {
                                    Row(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .clip(RoundedCornerShape(16.dp))
                                            .clickable {
                                                showOptionsMenu = false
                                                showLyrics = true
                                            }
                                            .padding(16.dp),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Icon(Icons.Filled.Notes, contentDescription = null, tint = textMain, modifier = Modifier.size(20.dp))
                                        Spacer(modifier = Modifier.width(16.dp))
                                        Text("Show Lyrics", color = textMain, fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
                                    }
                                    Spacer(modifier = Modifier.height(4.dp))
                                    Row(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .clip(RoundedCornerShape(16.dp))
                                            .clickable {
                                                showOptionsMenu = false
                                                val shareIntent = Intent(Intent.ACTION_SEND).apply {
                                                    type = "text/plain"
                                                    putExtra(Intent.EXTRA_TEXT, "Check out \\"$title\\" by ${artist ?: "this artist"} on Aura Downloader!")
                                                }
                                                context.startActivity(Intent.createChooser(shareIntent, "Share Track"))
                                            }
                                            .padding(16.dp),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Icon(Icons.Filled.Share, contentDescription = null, tint = Color(0xFFF87171), modifier = Modifier.size(20.dp))
                                        Spacer(modifier = Modifier.width(16.dp))
                                        Text("Share", color = Color(0xFFF87171), fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
                                    }
                                }
                            }
                        }"""
content = content.replace(menu_target, menu_repl)

# 2. Fix the Lyrics animation to not cut off words (use fontSize instead of scale)
lyrics_target = """                                            val targetScale = if (isActive) 1.15f else 1.0f
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

lyrics_repl = """                                            val targetFontSize = if (isActive) 28f else 22f
                                            val targetAlpha = if (isActive) 1.0f else 0.3f
                                            
                                            val animatedFontSize by androidx.compose.animation.core.animateFloatAsState(
                                                targetValue = targetFontSize,
                                                animationSpec = androidx.compose.animation.core.spring(dampingRatio = 0.65f, stiffness = 200f)
                                            )
                                            val animatedAlpha by androidx.compose.animation.core.animateFloatAsState(
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
content = content.replace(lyrics_target, lyrics_repl)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
