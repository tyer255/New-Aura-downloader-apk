import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

# 1. Add showLyrics state
state_target = "var isMinimized by remember { mutableStateOf(false) }"
state_repl = "var isMinimized by remember { mutableStateOf(false) }\n    var showLyrics by remember { mutableStateOf(false) }"
content = content.replace(state_target, state_repl)

# 2. Update the dropdown menu (line ~2601)
menu_target = """                            androidx.compose.material3.DropdownMenuItem(
                                text = { Text("Show Lyrics", color = textMain) },
                                leadingIcon = { Icon(Icons.Filled.Mic, null, tint = textMain) },
                                onClick = { showOptionsMenu = false; Toast.makeText(context, "Lyrics coming soon!", Toast.LENGTH_SHORT).show() }
                            )"""
menu_repl = """                            androidx.compose.material3.DropdownMenuItem(
                                text = { Text("Show Lyrics", color = textMain) },
                                leadingIcon = { Icon(Icons.AutoMirrored.Filled.Notes, null, tint = textMain) },
                                onClick = { showOptionsMenu = false; showLyrics = true }
                            )"""
content = content.replace(menu_target, menu_repl)

# 3. Add Lyrics View at the bottom of the "else" (full screen) view
# Find the exact ending block for the `} else {` part.
# The structure is:
#         } else {
#             Column(...) {
#                 ... (Top Nav, Album Art, Song Info, Slider, Controls)
#             }
#         }
#     }
# }

# We want to replace the end of that column with the lyrics UI.

end_target = """                    Box(
                        modifier = Modifier
                            .size(40.dp)
                            .clip(CircleShape)
                            .clickable(
                                interactionSource = remember { MutableInteractionSource() },
                                indication = null
                            ) {
                                isLooping = !isLooping
                                // Looping is currently not supported in the new MediaController architecture
                                // or we'd have to pass it to MusicController. For now, just toggle state.
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
}"""

end_repl = """                    Box(
                        modifier = Modifier
                            .size(40.dp)
                            .clip(CircleShape)
                            .clickable(
                                interactionSource = remember { MutableInteractionSource() },
                                indication = null
                            ) {
                                isLooping = !isLooping
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
                
                // --- LYRICS VIEW ---
                val parsedLyrics = remember(syncedLyrics) { parseLrc(syncedLyrics) }
                
                if (parsedLyrics.isNotEmpty() || !lyrics.isNullOrEmpty()) {
                    Spacer(modifier = Modifier.height(24.dp))
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(if (showLyrics) 350.dp else 56.dp)
                            .animateContentSize()
                            .clip(RoundedCornerShape(24.dp))
                            .background(glassBg)
                            .clickable { if (!showLyrics) showLyrics = true }
                    ) {
                        if (!showLyrics) {
                            Text(
                                text = "Lyrics",
                                color = textMain,
                                fontWeight = FontWeight.SemiBold,
                                modifier = Modifier.align(Alignment.Center)
                            )
                        } else {
                            Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text("Lyrics", color = textMain, fontWeight = FontWeight.Bold, fontSize = 18.sp)
                                    androidx.compose.material3.IconButton(onClick = { showLyrics = false }) {
                                        Icon(Icons.Filled.Close, contentDescription = "Close", tint = textMain)
                                    }
                                }
                                Spacer(modifier = Modifier.height(8.dp))
                                
                                if (parsedLyrics.isNotEmpty()) {
                                    val listState = androidx.compose.foundation.lazy.rememberLazyListState()
                                    var activeIndex by remember { mutableStateOf(-1) }
                                    
                                    LaunchedEffect(currentPositionMs) {
                                        var newActive = -1
                                        for (i in parsedLyrics.indices) {
                                            if (currentPositionMs >= parsedLyrics[i].timeMs) {
                                                newActive = i
                                            } else {
                                                break
                                            }
                                        }
                                        if (newActive != activeIndex && newActive != -1) {
                                            activeIndex = newActive
                                            listState.animateScrollToItem((newActive - 2).coerceAtLeast(0))
                                        }
                                    }
                                    
                                    androidx.compose.foundation.lazy.LazyColumn(state = listState, modifier = Modifier.fillMaxWidth().weight(1f)) {
                                        items(parsedLyrics.size) { index ->
                                            val line = parsedLyrics[index]
                                            val isActive = index == activeIndex
                                            val scale by androidx.compose.animation.core.animateFloatAsState(if (isActive) 1.05f else 1.0f)
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
                                            )
                                        }
                                    }
                                } else {
                                    val scrollState = rememberScrollState()
                                    Text(
                                        text = lyrics ?: "",
                                        color = textMain.copy(alpha = 0.8f),
                                        fontSize = 16.sp,
                                        modifier = Modifier.fillMaxWidth().weight(1f).verticalScroll(scrollState)
                                    )
                                }
                            }
                        }
                    }
                }
                // -------------------

            }
        }
    }
}"""
content = content.replace(end_target, end_repl)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
