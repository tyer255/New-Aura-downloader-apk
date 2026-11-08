import re

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    code = f.read()

# Find result?.let { r -> block
start_marker = "result?.let { r ->"
end_marker = "// Error UI"

start_idx = code.find(start_marker)
end_idx = code.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_ui_block = """result?.let { r ->
                if (r.success) {
                    // Result UI
                    Box(
                        modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(16.dp)).background(glassBg).border(1.dp, glassBorder, RoundedCornerShape(16.dp)).padding(16.dp)
                    ) {
                        Column {
                            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.background(Color(0xFF22C55E).copy(alpha = 0.15f), RoundedCornerShape(8.dp)).padding(horizontal = 12.dp, vertical = 6.dp)) {
                                Icon(Icons.Filled.CheckCircle, null, tint = Color(0xFF22C55E), modifier = Modifier.size(16.dp))
                                Spacer(modifier = Modifier.width(6.dp))
                                Text("Extraction Successful", color = Color(0xFF22C55E), fontWeight = FontWeight.Bold, style = MaterialTheme.typography.labelSmall)
                            }
                            Spacer(modifier = Modifier.height(16.dp))

                            if (r.thumbnailUrl.isNotEmpty()) {
                                Box(
                                    modifier = Modifier.fillMaxWidth().aspectRatio(16f/9f).clip(RoundedCornerShape(12.dp)).background(if (isDarkMode) Color.DarkGray.copy(0.5f) else Color.LightGray.copy(0.5f)),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Icon(Icons.Filled.Image, contentDescription = null, tint = subTextColor, modifier = Modifier.size(48.dp))
                                    AsyncImage(
                                        model = coil.request.ImageRequest.Builder(context).data(r.thumbnailUrl).crossfade(true).build(),
                                        contentDescription = "Thumbnail",
                                        contentScale = ContentScale.Crop,
                                        modifier = Modifier.fillMaxSize()
                                    )
                                    if (r.isSpotify) {
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
                                    }
                                }
                                Spacer(modifier = Modifier.height(16.dp))
                            }

                            Text(text = r.title, color = textColor, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, maxLines = 2, overflow = TextOverflow.Ellipsis)
                            if (!r.artistName.isNullOrEmpty()) {
                                Spacer(modifier = Modifier.height(4.dp))
                                Text(text = r.artistName, color = subTextColor, style = MaterialTheme.typography.bodyMedium, maxLines = 1, overflow = TextOverflow.Ellipsis)
                            }
                            Spacer(modifier = Modifier.height(16.dp))

                            if (r.isSpotify && r.spotifyTracks.isNotEmpty()) {
                                Card(
                                    modifier = Modifier.fillMaxWidth(),
                                    colors = CardDefaults.cardColors(containerColor = if (isDarkMode) Color(0xFF181818) else Color(0xFFF0F0F0)),
                                    shape = RoundedCornerShape(12.dp)
                                ) {
                                    Column(modifier = Modifier.padding(12.dp)) {
                                        Row(verticalAlignment = Alignment.CenterVertically) {
                                            Icon(Icons.Filled.QueueMusic, contentDescription = null, tint = Color(0xFF1DB954), modifier = Modifier.size(20.dp))
                                            Spacer(modifier = Modifier.width(8.dp))
                                            Text(
                                                text = if (r.isPlaylist) "Playlist Tracks (${r.spotifyTracks.size} Songs)" else "Track Information",
                                                fontWeight = FontWeight.Bold,
                                                color = textColor,
                                                style = MaterialTheme.typography.titleSmall
                                            )
                                        }
                                        Spacer(modifier = Modifier.height(8.dp))
                                        r.spotifyTracks.take(20).forEach { track ->
                                            Column {
                                                Row(
                                                    modifier = Modifier
                                                        .fillMaxWidth()
                                                        .padding(vertical = 6.dp),
                                                    horizontalArrangement = Arrangement.SpaceBetween,
                                                    verticalAlignment = Alignment.CenterVertically
                                                ) {
                                                    Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.weight(1f)) {
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
                                                    }
                                                }
                                                HorizontalDivider(color = glassBorder.copy(alpha = 0.2f))
                                            }
                                        }
                                        if (r.spotifyTracks.size > 20) {
                                            Spacer(modifier = Modifier.height(6.dp))
                                            Text(
                                                text = "+ ${r.spotifyTracks.size - 20} more tracks included in ZIP package",
                                                color = subTextColor,
                                                style = MaterialTheme.typography.bodySmall
                                            )
                                        }
                                    }
                                }
                                Spacer(modifier = Modifier.height(16.dp))
                            }

                            Text("Available Downloads:", color = subTextColor, style = MaterialTheme.typography.labelMedium)
                            Spacer(modifier = Modifier.height(8.dp))

                            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                r.qualities.forEach { q ->
                                    val isZip = q.label.contains("zip", true)
                                    Button(
                                        onClick = {
                                            val action = {
                                                resolveAndTriggerDownload(
                                                    context = context,
                                                    coroutineScope = coroutineScope,
                                                    q = q,
                                                    title = r.title,
                                                    thumbnailUrl = r.thumbnailUrl
                                                )
                                            }
                                            if (android.os.Build.VERSION.SDK_INT <= 28 && androidx.core.content.ContextCompat.checkSelfPermission(context, android.Manifest.permission.WRITE_EXTERNAL_STORAGE) != android.content.pm.PackageManager.PERMISSION_GRANTED) {
                                                pendingDownloadAction = action
                                                storagePermissionLauncher.launch(android.Manifest.permission.WRITE_EXTERNAL_STORAGE)
                                            } else {
                                                action()
                                            }
                                        },
                                        modifier = Modifier.fillMaxWidth().height(48.dp),
                                        shape = RoundedCornerShape(12.dp),
                                        colors = ButtonDefaults.buttonColors(
                                            containerColor = if (isZip) Color(0xFF1DB954) else if (isDarkMode) Color.White.copy(0.1f) else Color.White,
                                            contentColor = if (isZip) Color.White else textColor
                                        ),
                                        border = if (isZip) null else androidx.compose.foundation.BorderStroke(1.dp, glassBorder)
                                    ) {
                                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                                            Row(verticalAlignment = Alignment.CenterVertically) {
                                                val iconVector = when {
                                                    isZip -> Icons.Filled.FolderZip
                                                    q.label.contains("Audio", true) || q.label.contains("mp3", true) -> Icons.Filled.Audiotrack
                                                    q.label.contains("Thumbnail", true) || q.label.contains("jpg", true) -> Icons.Filled.Image
                                                    else -> Icons.Filled.VideoFile
                                                }
                                                Icon(iconVector, null, modifier = Modifier.size(18.dp), tint = if (isZip) Color.White else selectedPlatform.brandColor)
                                                Spacer(modifier = Modifier.width(8.dp))
                                                Text(q.label, fontWeight = FontWeight.Bold)
                                            }
                                            Row(verticalAlignment = Alignment.CenterVertically) {
                                                if (q.size != null) {
                                                    Text(q.size, color = if (isZip) Color.White.copy(0.8f) else subTextColor, style = MaterialTheme.typography.bodySmall)
                                                    Spacer(modifier = Modifier.width(8.dp))
                                                }
                                                Icon(Icons.Filled.Download, "Download", modifier = Modifier.size(16.dp), tint = if (isZip) Color.White else subTextColor)
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                } else {
                    """
    code = code[:start_idx] + new_ui_block + code[end_idx:]
    with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
        f.write(code)
    print("UI block updated successfully!")
else:
    print("Could not locate UI block markers")
