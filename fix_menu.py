import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

target_menu = """                        if (showOptionsMenu) {
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
                                        Icon(Icons.Filled.Lyrics, contentDescription = null, tint = textMain, modifier = Modifier.size(20.dp))
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

replacement_menu = """                        // Overlay menu replaced in the outer box"""

content = content.replace(target_menu, replacement_menu)

outer_box_target = """                    if (showOptionsMenu) {
                        Box(modifier = Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.6f)))
                    }"""

outer_box_repl = """                    if (showOptionsMenu) {
                        Box(
                            modifier = Modifier
                                .fillMaxSize()
                                .background(Color.Black.copy(alpha = 0.5f))
                                .clickable { showOptionsMenu = false },
                            contentAlignment = Alignment.TopEnd
                        ) {
                            Column(
                                modifier = Modifier
                                    .padding(top = 70.dp, end = 24.dp)
                                    .width(220.dp)
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
                                    Icon(Icons.Filled.Lyrics, contentDescription = null, tint = textMain, modifier = Modifier.size(20.dp))
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

content = content.replace(outer_box_target, outer_box_repl)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
