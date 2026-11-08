with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    lines = f.readlines()

new_lines = []
i = 0
replaced = False

while i < len(lines):
    line = lines[i]
    if "// Thumbnail" in line and not replaced:
        # We replace lines 994 to 1009
        spotify_ui = """                                if (r.isSpotify && !r.previewAudioUrl.isNullOrEmpty()) {
                                    SpotifyMusicPlayer(
                                        title = r.title,
                                        artist = r.artistName,
                                        thumbnailUrl = r.thumbnailUrl,
                                        audioUrl = r.previewAudioUrl,
                                        isDarkMode = isDarkMode
                                    )
                                    Spacer(modifier = Modifier.height(16.dp))
                                } else {
                                    if (r.thumbnailUrl.isNotEmpty()) {
                                        Box(modifier = Modifier.fillMaxWidth().aspectRatio(16f/9f).clip(RoundedCornerShape(12.dp)).background(if (isDarkMode) Color.DarkGray.copy(0.5f) else Color.LightGray.copy(0.5f)), contentAlignment = Alignment.Center) {
                                            Icon(Icons.Filled.Image, contentDescription = null, tint = subTextColor, modifier = Modifier.size(48.dp))
                                            AsyncImage(
                                                model = coil.request.ImageRequest.Builder(context).data(r.thumbnailUrl).decoderFactory(coil.decode.VideoFrameDecoder.Factory()).crossfade(true).build(),
                                                contentDescription = "Thumbnail",
                                                contentScale = ContentScale.Crop,
                                                modifier = Modifier.fillMaxSize()
                                            )
                                        }
                                        Spacer(modifier = Modifier.height(16.dp))
                                    }
                                    Text(text = r.title, color = textColor, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, maxLines = 2, overflow = TextOverflow.Ellipsis)
                                    Spacer(modifier = Modifier.height(16.dp))
                                }
"""
        new_lines.append(spotify_ui)
        # Skip until after Text(text = r.title... and Spacer
        while i < len(lines) and "Available Qualities" not in lines[i]:
            i += 1
        replaced = True
        continue
    new_lines.append(line)
    i += 1

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.writelines(new_lines)

print("Replacement done, replaced=", replaced)
