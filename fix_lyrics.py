import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

target = """                        }
                    }
                }
            }
        }
    }
}

fun formatTimeMs(ms: Int): String {"""

replacement = """                        }
                    }
                }
                
                // Lyrics View
                var showLyrics by remember { mutableStateOf(false) }
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
                                    IconButton(onClick = { showLyrics = false }) {
                                        Icon(Icons.Filled.Close, contentDescription = "Close", tint = textMain)
                                    }
                                }
                                Spacer(modifier = Modifier.height(8.dp))
                                
                                if (parsedLyrics.isNotEmpty()) {
                                    val listState = rememberLazyListState()
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
                                        itemsIndexed(parsedLyrics) { index, line ->
                                            val isActive = index == activeIndex
                                            val scale by animateFloatAsState(if (isActive) 1.05f else 1.0f)
                                            val alpha by animateFloatAsState(if (isActive) 1.0f else 0.4f)
                                            
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
                                                        transformOrigin = TransformOrigin(0f, 0.5f)
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
            }
        }
    }
}

fun formatTimeMs(ms: Int): String {"""

content = content.replace(target, replacement)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
