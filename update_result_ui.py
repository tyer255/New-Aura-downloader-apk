with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    code = f.read()

target = """if (!r.artistName.isNullOrEmpty()) {
                                Spacer(modifier = Modifier.height(4.dp))
                                Text(text = r.artistName, color = subTextColor, style = MaterialTheme.typography.bodyMedium, maxLines = 1, overflow = TextOverflow.Ellipsis)
                            }
                            Spacer(modifier = Modifier.height(16.dp))"""

replacement = """if (!r.artistName.isNullOrEmpty()) {
                                Spacer(modifier = Modifier.height(4.dp))
                                Text(text = r.artistName, color = subTextColor, style = MaterialTheme.typography.bodyMedium, maxLines = 1, overflow = TextOverflow.Ellipsis)
                            }
                            Spacer(modifier = Modifier.height(16.dp))

                            if (r.isSpotify || !r.previewAudioUrl.isNullOrEmpty()) {
                                val audioToPlay = if (!r.previewAudioUrl.isNullOrEmpty()) r.previewAudioUrl else {
                                    r.qualities.firstOrNull { q -> q.label.contains("MP3", true) || q.label.contains("Audio", true) }?.url
                                }
                                if (!audioToPlay.isNullOrEmpty()) {
                                    SpotifyMusicPlayer(
                                        title = r.title,
                                        artist = r.artistName,
                                        thumbnailUrl = r.thumbnailUrl,
                                        audioUrl = audioToPlay,
                                        isDarkMode = isDarkMode
                                    )
                                    Spacer(modifier = Modifier.height(16.dp))
                                }
                            }"""

if target in code:
    code = code.replace(target, replacement)
    with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
        f.write(code)
    print("Updated Result UI with SpotifyMusicPlayer successfully!")
else:
    print("Target not found in code")
