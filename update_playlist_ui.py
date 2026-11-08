with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    code = f.read()

target_start = "            result?.let { r ->\n                if (r.success) {"
replacement_start = """            result?.let { r ->
                if (r.success) {
                    var selectedPlaylistTrack by remember(r) { mutableStateOf<SpotifyTrack?>(null) }"""

if target_start in code:
    code = code.replace(target_start, replacement_start)
    print("Added selectedPlaylistTrack state")

target_player = """                            if (r.isSpotify || !r.previewAudioUrl.isNullOrEmpty()) {
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

replacement_player = """                            if (r.isSpotify || !r.previewAudioUrl.isNullOrEmpty()) {
                                val defaultAudioToPlay = if (!r.previewAudioUrl.isNullOrEmpty()) r.previewAudioUrl else {
                                    r.qualities.firstOrNull { q -> q.label.contains("MP3", true) || q.label.contains("Audio", true) }?.url
                                }
                                val activeAudioToPlay = selectedPlaylistTrack?.resolveUrl ?: selectedPlaylistTrack?.directAudioUrl ?: defaultAudioToPlay
                                val activeTitle = selectedPlaylistTrack?.name ?: r.title
                                val activeArtist = selectedPlaylistTrack?.artist?.ifEmpty { r.artistName } ?: r.artistName
                                val activeThumb = selectedPlaylistTrack?.thumbnailUrl?.ifEmpty { r.thumbnailUrl } ?: r.thumbnailUrl

                                if (!activeAudioToPlay.isNullOrEmpty()) {
                                    SpotifyMusicPlayer(
                                        title = activeTitle,
                                        artist = activeArtist,
                                        thumbnailUrl = activeThumb,
                                        audioUrl = activeAudioToPlay,
                                        isDarkMode = isDarkMode
                                    )
                                    Spacer(modifier = Modifier.height(16.dp))
                                }
                            }"""

if target_player in code:
    code = code.replace(target_player, replacement_player)
    print("Updated SpotifyMusicPlayer call to use active selected track")

target_track_row = """                                                     Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.weight(1f)) {
                                                         Text(
                                                             text = "#${track.trackNumber}",
                                                             color = Color(0xFF1DB954),
                                                             fontWeight = FontWeight.Bold,
                                                             style = MaterialTheme.typography.labelMedium
                                                         )
                                                         Spacer(modifier = Modifier.width(8.dp))
                                                         Column {
                                                             Text(
                                                                 text = track.name,
                                                                 color = textColor,
                                                                 fontWeight = FontWeight.SemiBold,
                                                                 style = MaterialTheme.typography.bodyMedium,
                                                                 maxLines = 1,
                                                                 overflow = TextOverflow.Ellipsis
                                                             )
                                                             if (track.artist.isNotEmpty()) {
                                                                 Text(
                                                                     text = track.artist,
                                                                     color = subTextColor,
                                                                     style = MaterialTheme.typography.bodySmall,
                                                                     maxLines = 1,
                                                                     overflow = TextOverflow.Ellipsis
                                                                 )
                                                             }
                                                         }
                                                     }
                                                     if (!track.durationStr.isNullOrEmpty()) {
                                                         Text(
                                                             text = track.durationStr,
                                                             color = subTextColor,
                                                             style = MaterialTheme.typography.bodySmall,
                                                             fontWeight = FontWeight.Medium
                                                         )
                                                     }"""

replacement_track_row = """                                                     Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.weight(1f)) {
                                                         Text(
                                                             text = "#${track.trackNumber}",
                                                             color = Color(0xFF1DB954),
                                                             fontWeight = FontWeight.Bold,
                                                             style = MaterialTheme.typography.labelMedium
                                                         )
                                                         Spacer(modifier = Modifier.width(8.dp))
                                                         Column(modifier = Modifier.weight(1f)) {
                                                             Text(
                                                                 text = track.name,
                                                                 color = textColor,
                                                                 fontWeight = FontWeight.SemiBold,
                                                                 style = MaterialTheme.typography.bodyMedium,
                                                                 maxLines = 1,
                                                                 overflow = TextOverflow.Ellipsis
                                                             )
                                                             if (track.artist.isNotEmpty()) {
                                                                 Text(
                                                                     text = track.artist,
                                                                     color = subTextColor,
                                                                     style = MaterialTheme.typography.bodySmall,
                                                                     maxLines = 1,
                                                                     overflow = TextOverflow.Ellipsis
                                                                 )
                                                             }
                                                         }
                                                     }
                                                     Row(verticalAlignment = Alignment.CenterVertically) {
                                                         if (!track.resolveUrl.isNullOrEmpty() || !track.directAudioUrl.isNullOrEmpty()) {
                                                             IconButton(
                                                                 onClick = { selectedPlaylistTrack = track },
                                                                 modifier = Modifier.size(32.dp)
                                                             ) {
                                                                 Icon(
                                                                     Icons.Filled.PlayCircle,
                                                                     contentDescription = "Play Track",
                                                                     tint = if (selectedPlaylistTrack == track) Color(0xFF1DB954) else subTextColor,
                                                                     modifier = Modifier.size(20.dp)
                                                                 )
                                                             }
                                                             IconButton(
                                                                 onClick = {
                                                                     val tUrl = track.resolveUrl ?: track.directAudioUrl ?: ""
                                                                     if (tUrl.isNotEmpty()) {
                                                                         resolveAndTriggerDownload(
                                                                             context,
                                                                             coroutineScope,
                                                                             MediaQuality("Download MP3", null, tUrl),
                                                                             track.name,
                                                                             track.thumbnailUrl ?: r.thumbnailUrl
                                                                         )
                                                                     }
                                                                 },
                                                                 modifier = Modifier.size(32.dp)
                                                             ) {
                                                                 Icon(
                                                                     Icons.Filled.Download,
                                                                     contentDescription = "Download Track",
                                                                     tint = subTextColor,
                                                                     modifier = Modifier.size(18.dp)
                                                                 )
                                                             }
                                                         } else if (!track.durationStr.isNullOrEmpty()) {
                                                             Text(
                                                                 text = track.durationStr,
                                                                 color = subTextColor,
                                                                 style = MaterialTheme.typography.bodySmall,
                                                                 fontWeight = FontWeight.Medium
                                                             )
                                                         }
                                                     }"""

if target_track_row in code:
    code = code.replace(target_track_row, replacement_track_row)
    print("Updated track row with play and download buttons")

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(code)

print("Playlist UI updated successfully")
