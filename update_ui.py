with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    code = f.read()

# 1. Add carousel UI before "Available Downloads:"
target_carousel = """                            }

                            Text("Available Downloads:", color = subTextColor, style = MaterialTheme.typography.labelMedium)"""

replacement_carousel = """                            }

                            if (r.carouselItems.isNotEmpty()) {
                                Text("Carousel Media (${r.carouselItems.size} items)", fontWeight = FontWeight.Bold, color = textColor, style = MaterialTheme.typography.titleSmall)
                                Spacer(modifier = Modifier.height(8.dp))
                                androidx.compose.foundation.lazy.LazyRow(
                                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                                    contentPadding = PaddingValues(bottom = 8.dp)
                                ) {
                                    items(r.carouselItems.size) { index ->
                                        val item = r.carouselItems[index]
                                        Card(
                                            shape = RoundedCornerShape(12.dp),
                                            modifier = Modifier.width(140.dp)
                                        ) {
                                            Column {
                                                Box(modifier = Modifier.fillMaxWidth().aspectRatio(1f).background(Color.Black)) {
                                                    val thumbUrl = if (!item.thumbnail.isNullOrEmpty()) item.thumbnail else item.url
                                                    AsyncImage(
                                                        model = coil.request.ImageRequest.Builder(context).data(thumbUrl).crossfade(true).build(),
                                                        contentDescription = null,
                                                        contentScale = ContentScale.Crop,
                                                        modifier = Modifier.fillMaxSize()
                                                    )
                                                    if (item.type == "video") {
                                                        Box(modifier = Modifier.align(Alignment.TopEnd).padding(4.dp).background(Color.Black.copy(0.6f), RoundedCornerShape(4.dp)).padding(4.dp)) {
                                                            Icon(Icons.Filled.PlayArrow, contentDescription = null, tint = Color.White, modifier = Modifier.size(16.dp))
                                                        }
                                                    }
                                                }
                                                Button(
                                                    onClick = {
                                                        val action = {
                                                            val q = MediaQuality(if (item.type == "video") "Download Video" else "Download Image", null, item.url)
                                                            resolveAndTriggerDownload(context, coroutineScope, q, r.title, item.thumbnail ?: "")
                                                        }
                                                        if (android.os.Build.VERSION.SDK_INT <= 28 && androidx.core.content.ContextCompat.checkSelfPermission(context, android.Manifest.permission.WRITE_EXTERNAL_STORAGE) != android.content.pm.PackageManager.PERMISSION_GRANTED) {
                                                            pendingDownloadAction = action
                                                            storagePermissionLauncher.launch(android.Manifest.permission.WRITE_EXTERNAL_STORAGE)
                                                        } else {
                                                            action()
                                                        }
                                                    },
                                                    modifier = Modifier.fillMaxWidth().height(36.dp),
                                                    shape = RoundedCornerShape(0.dp, 0.dp, 12.dp, 12.dp),
                                                    contentPadding = PaddingValues(0.dp)
                                                ) {
                                                    Text("Download", style = MaterialTheme.typography.labelSmall)
                                                }
                                            }
                                        }
                                    }
                                }
                                Spacer(modifier = Modifier.height(16.dp))
                            }

                            if (r.qualities.isNotEmpty()) {
                                Text("Available Downloads:", color = subTextColor, style = MaterialTheme.typography.labelMedium)
                            } else if (r.carouselItems.isEmpty()) {
                                Text("No downloads found for this link.", color = subTextColor, style = MaterialTheme.typography.labelMedium)
                            }"""

if target_carousel in code:
    code = code.replace(target_carousel, replacement_carousel)
    print("Replaced carousel UI")

# 2. Update Spotify audio badge logic
target_badge = """                                    if (r.isSpotify) {
                                        Box(
                                            modifier = Modifier
                                                .align(Alignment.TopEnd)
                                                .padding(8.dp)
                                                .background(Color(0xFF1DB954), RoundedCornerShape(20.dp))
                                                .padding(horizontal = 10.dp, vertical = 4.dp)
                                        ) {
                                            Row(verticalAlignment = Alignment.CenterVertically) {
                                                Icon(Icons.Filled.Audiotrack, contentDescription = null, tint = Color.White, modifier = Modifier.size(12.dp))
                                                Spacer(modifier = Modifier.width(4.dp))
                                                Text(
                                                    text = if (r.isPlaylist) "Spotify Playlist" else "Spotify Track",
                                                    color = Color.White,
                                                    fontWeight = FontWeight.Bold,
                                                    style = MaterialTheme.typography.labelSmall
                                                )
                                            }
                                        }
                                    }"""

replacement_badge = """                                    if (r.isSpotify || r.mediaType == "audio") {
                                        Box(
                                            modifier = Modifier
                                                .align(Alignment.TopEnd)
                                                .padding(8.dp)
                                                .background(if (r.isSpotify) Color(0xFF1DB954) else Color(0xFF3B82F6), RoundedCornerShape(20.dp))
                                                .padding(horizontal = 10.dp, vertical = 4.dp)
                                        ) {
                                            Row(verticalAlignment = Alignment.CenterVertically) {
                                                Icon(Icons.Filled.Audiotrack, contentDescription = null, tint = Color.White, modifier = Modifier.size(12.dp))
                                                Spacer(modifier = Modifier.width(4.dp))
                                                Text(
                                                    text = if (r.isSpotify) (if (r.isPlaylist) "Spotify Playlist" else "Spotify Track") else "Audio File",
                                                    color = Color.White,
                                                    fontWeight = FontWeight.Bold,
                                                    style = MaterialTheme.typography.labelSmall
                                                )
                                            }
                                        }
                                    }"""

if target_badge in code:
    code = code.replace(target_badge, replacement_badge)
    print("Replaced audio badge UI")

# 3. Update Audio player logic
target_audio_player = """                            if (r.isSpotify || !r.previewAudioUrl.isNullOrEmpty()) {"""
replacement_audio_player = """                            if (r.isSpotify || r.mediaType == "audio" || !r.previewAudioUrl.isNullOrEmpty()) {"""

if target_audio_player in code:
    code = code.replace(target_audio_player, replacement_audio_player)
    print("Replaced audio player UI check")

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(code)
