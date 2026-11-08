import re

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    code = f.read()

# 1. Replace handleSpotifyExtraction
new_spotify_extraction = """suspend fun handleSpotifyExtraction(url: String): DownloadResult {
    val lowerUrl = url.lowercase()
    val spotifyRegex: kotlin.text.Regex = kotlin.text.Regex("(?:spotify\\\\.com\\\\/(?:[a-zA-Z0-9-]+\\\\/" + ")?|spotify:)(track|playlist|album|artist)[:\\\\/]([a-zA-Z0-9]{22})")
    val match = spotifyRegex.find(url)
    val kind = match?.groupValues?.get(1)?.lowercase() ?: if (lowerUrl.contains("/playlist")) "playlist" else if (lowerUrl.contains("/album")) "album" else "track"
    val itemId = match?.groupValues?.get(2)

    var trackTitle = "Spotify Music"
    var artistName = ""
    var thumbnailUrl = ""
    var previewAudioUrl: String? = null
    val spotifyTracks = mutableListOf<SpotifyTrack>()

    try {
        val encodedUrl = URLEncoder.encode(url, "UTF-8")
        val oembedReq = Request.Builder().url("https://open.spotify.com/oembed?url=$encodedUrl").build()
        val oembedRes = okHttpClient.newCall(oembedReq).execute()
        if (oembedRes.isSuccessful) {
            val ojson = JSONObject(oembedRes.body?.string() ?: "")
            trackTitle = ojson.optString("title", trackTitle)
            thumbnailUrl = ojson.optString("thumbnail_url", thumbnailUrl)
        }
    } catch (e: Exception) {
        e.printStackTrace()
    }

    try {
        val embedKind = if (itemId != null) kind else if (lowerUrl.contains("/playlist")) "playlist" else "track"
        val embedUrl = if (itemId != null) "https://open.spotify.com/embed/$embedKind/$itemId" else url
        val req = Request.Builder()
            .url(embedUrl)
            .addHeader("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            .build()
        val res = okHttpClient.newCall(req).execute()
        if (res.isSuccessful) {
            val html = res.body?.string() ?: ""

            // Try to extract audio preview from HTML regexes
            val previewRegexes = listOf(
                kotlin.text.Regex("\\"audioPreview\\":\\\\s*\\\\{\\\\"url\\":\\\\s*\\"([^\\"]+)\\""),
                kotlin.text.Regex("\\"preview_url\\":\\\\s*\\"([^\\"]+)\\""),
                kotlin.text.Regex("\\"audio_preview_url\\":\\\\s*\\"([^\\"]+)\\""),
                kotlin.text.Regex("(https://p\\\\.scdn\\\\.co/mp3-preview/[a-zA-Z0-9]+)")
            )
            for (pr in previewRegexes) {
                val m = pr.find(html)
                if (m != null) {
                    val foundUrl = m.groupValues[1]
                    if (foundUrl.isNotEmpty()) {
                        previewAudioUrl = foundUrl
                        break
                    }
                }
            }

            val nextDataRegex: kotlin.text.Regex = kotlin.text.Regex("<script id=\\"__NEXT_DATA__\\" type=\\"application/json\\">(.*?)</script>", setOf(RegexOption.DOT_MATCHES_ALL))
            val nextDataMatch = nextDataRegex.find(html)
            if (nextDataMatch != null) {
                try {
                    val rootJson = JSONObject(nextDataMatch.groupValues[1])
                    val entity = rootJson.optJSONObject("props")
                        ?.optJSONObject("pageProps")
                        ?.optJSONObject("state")
                        ?.optJSONObject("data")
                        ?.optJSONObject("entity")

                    if (entity != null) {
                        val entTitle = entity.optString("title", entity.optString("name", ""))
                        if (entTitle.isNotEmpty()) trackTitle = entTitle

                        val entSub = entity.optString("subtitle", entity.optString("authors", ""))
                        if (entSub.isNotEmpty()) artistName = entSub

                        val entAudio = entity.optString("audioPreviewUrl", entity.optString("preview_url", entity.optString("audio_preview_url", "")))
                        if (entAudio.isNotEmpty()) {
                            previewAudioUrl = entAudio
                        } else {
                            val audioObj = entity.optJSONObject("audioPreview")
                            if (audioObj != null) {
                                val audioUrlStr = audioObj.optString("url", "")
                                if (audioUrlStr.isNotEmpty()) previewAudioUrl = audioUrlStr
                            }
                        }

                        val coverArt = entity.optJSONObject("coverArt")
                        val sources = coverArt?.optJSONArray("sources")
                        if (sources != null && sources.length() > 0) {
                            val img = sources.getJSONObject(0).optString("url", "")
                            if (img.isNotEmpty()) thumbnailUrl = img
                        }

                        val trackList = entity.optJSONArray("trackList")
                        if (trackList != null && trackList.length() > 0) {
                            for (i in 0 until trackList.length()) {
                                val tObj = trackList.getJSONObject(i)
                                val tTitle = tObj.optString("title", tObj.optString("name", "Track ${i + 1}"))
                                val tSub = tObj.optString("subtitle", tObj.optString("artist", artistName))
                                val durMs = tObj.optLong("duration", 0L)
                                var durStr: String? = null
                                if (durMs > 0) {
                                    val durSec = durMs / 1000
                                    val mins = durSec / 60
                                    val secs = durSec % 60
                                    durStr = String.format(java.util.Locale.US, "%d:%02d", mins, secs)
                                }
                                spotifyTracks.add(SpotifyTrack(name = tTitle, artist = tSub, durationStr = durStr, trackNumber = i + 1))
                            }
                        }
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }

            if (thumbnailUrl.isEmpty()) {
                val visualIdentityRegex = kotlin.text.Regex("\\"coverArt\\":\\\\{\\"sources\\":\\\\[\\\\{\\"url\\":\\"([^\\"]+)\\"")
                val visualMatch = visualIdentityRegex.find(html)
                if (visualMatch != null) {
                    thumbnailUrl = visualMatch.groupValues[1]
                }
            }
        }
    } catch (e: Exception) {
        e.printStackTrace()
    }

    if (spotifyTracks.isEmpty()) {
        spotifyTracks.add(SpotifyTrack(name = trackTitle, artist = artistName, durationStr = null, trackNumber = 1))
    }

    val isPlaylist = kind == "playlist" || kind == "album" || spotifyTracks.size > 1
    val backendUrl = BuildConfig.BACKEND_URL
    val baseApiUrl = backendUrl.replace("/api/download", "")
    val qualities = mutableListOf<MediaQuality>()

    val encodedParam = URLEncoder.encode(url, "UTF-8")
    val zipLabel = if (isPlaylist) "Download Playlist (.zip Archive)" else "Download Song (.zip Archive)"
    val zipSize = if (isPlaylist) "${spotifyTracks.size} Tracks (.zip)" else "ZIP Archive"
    val zipUrl = "$baseApiUrl/api/spotify-download?url=$encodedParam&format=zip"

    qualities.add(MediaQuality(zipLabel, zipSize, zipUrl))
    qualities.add(MediaQuality("Download High Quality MP3 (320kbps)", "MP3 Audio", "$baseApiUrl/api/spotify-download?url=$encodedParam&format=mp3"))

    try {
        val jsonPayload = JSONObject().apply { put("url", url) }.toString()
        val requestBody = jsonPayload.toRequestBody("application/json".toMediaType())
        val req = Request.Builder().url(backendUrl).post(requestBody).addHeader("Content-Type", "application/json").build()
        val res = okHttpClient.newCall(req).execute()
        if (res.isSuccessful) {
            val resJson = JSONObject(res.body?.string() ?: "")
            if (resJson.optBoolean("success", false)) {
                val arr = resJson.optJSONArray("qualities") ?: resJson.optJSONArray("media")
                if (arr != null) {
                    for (i in 0 until arr.length()) {
                        val item = arr.getJSONObject(i)
                        val qLabel = item.optString("label", "Download MP3")
                        var qUrl = item.optString("url")
                        if (qUrl.startsWith("/")) qUrl = baseApiUrl + qUrl
                        if (!qualities.any { it.url == qUrl }) {
                            qualities.add(MediaQuality(qLabel, item.optString("size", null), qUrl))
                        }
                    }
                }
            }
        }
    } catch (e: Exception) {
        e.printStackTrace()
    }

    if (thumbnailUrl.isNotEmpty()) {
        qualities.add(MediaQuality("Download Cover Art (JPG)", "HD Cover", thumbnailUrl))
    }

    if (previewAudioUrl.isNullOrEmpty()) {
        previewAudioUrl = "$baseApiUrl/api/spotify-download?url=$encodedParam&format=mp3"
    }

    val displayTitle = if (artistName.isNotEmpty() && !trackTitle.contains(artistName)) "$trackTitle - $artistName" else trackTitle

    return DownloadResult(
        success = true,
        title = displayTitle,
        thumbnailUrl = thumbnailUrl,
        qualities = qualities,
        isSpotify = true,
        isPlaylist = isPlaylist,
        previewAudioUrl = previewAudioUrl,
        artistName = artistName,
        spotifyTracks = spotifyTracks
    )
}"""

old_fn_start = code.find("suspend fun handleSpotifyExtraction")
old_fn_end = code.find("suspend fun extractWithCobalt")

if old_fn_start != -1 and old_fn_end != -1:
    code = code[:old_fn_start] + new_spotify_extraction + "\n\n" + code[old_fn_end:]
    print("Replaced handleSpotifyExtraction")
else:
    print("Could not find handleSpotifyExtraction bounds")

# 2. Update SpotifyMusicPlayer composable to handle auto-preparation & playing state safely
old_player_start = code.find("@Composable\nfun SpotifyMusicPlayer")
if old_player_start == -1:
    old_player_start = code.find("fun SpotifyMusicPlayer")

old_player_end = code.rfind("fun formatTimeMs")
if old_player_end == -1:
    old_player_end = code.find("fun formatTimeMs")

new_player_code = """@Composable
fun SpotifyMusicPlayer(
    title: String,
    artist: String?,
    thumbnailUrl: String,
    audioUrl: String,
    isDarkMode: Boolean
) {
    val context = LocalContext.current
    var mediaPlayer by remember { mutableStateOf<MediaPlayer?>(null) }
    var isPlaying by remember { mutableStateOf(false) }
    var isLooping by remember { mutableStateOf(false) }
    var currentSpeed by remember { mutableFloatStateOf(1.0f) }
    var volume by remember { mutableFloatStateOf(1.0f) }
    var isMuted by remember { mutableStateOf(false) }
    var previousVolume by remember { mutableFloatStateOf(1.0f) }

    var currentPositionMs by remember { mutableIntStateOf(0) }
    var durationMs by remember { mutableIntStateOf(0) }
    var isPrepared by remember { mutableStateOf(false) }
    var isBuffering by remember { mutableStateOf(true) }
    var isError by remember { mutableStateOf(false) }
    var isUserScrubbing by remember { mutableStateOf(false) }
    var sliderPositionMs by remember { mutableFloatStateOf(0f) }

    DisposableEffect(audioUrl) {
        isPrepared = false
        isBuffering = true
        isError = false

        val player = MediaPlayer().apply {
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.21) {
                    setAudioAttributes(
                        android.media.AudioAttributes.Builder()
                            .setContentType(android.media.AudioAttributes.CONTENT_TYPE_MUSIC)
                            .setUsage(android.media.AudioAttributes.USAGE_MEDIA)
                            .build()
                    )
                }
                setDataSource(context, Uri.parse(audioUrl))
                setOnPreparedListener { mp ->
                    isPrepared = true
                    isBuffering = false
                    durationMs = mp.duration
                    mp.isLooping = isLooping
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                        try {
                            val params = mp.playbackParams
                            params.speed = currentSpeed
                            mp.playbackParams = params
                        } catch (e: Exception) {
                            e.printStackTrace()
                        }
                    }
                    val currentVol = if (isMuted) 0f else volume
                    mp.setVolume(currentVol, currentVol)
                    if (isPlaying) {
                        try { mp.start() } catch (e: Exception) { e.printStackTrace() }
                    }
                }
                setOnCompletionListener { mp ->
                    if (!mp.isLooping) {
                        isPlaying = false
                        currentPositionMs = 0
                    }
                }
                setOnErrorListener { _, _, _ ->
                    isBuffering = false
                    isPrepared = false
                    isPlaying = false
                    isError = true
                    false
                }
                prepareAsync()
            } catch (e: Exception) {
                e.printStackTrace()
                isBuffering = false
                isError = true
            }
        }
        mediaPlayer = player

        onDispose {
            try {
                if (player.isPlaying) {
                    player.stop()
                }
                player.release()
            } catch (e: Exception) {
                e.printStackTrace()
            }
            mediaPlayer = null
        }
    }

    LaunchedEffect(isPlaying, isUserScrubbing) {
        while (isPlaying && !isUserScrubbing) {
            mediaPlayer?.let { mp ->
                try {
                    if (mp.isPlaying) {
                        currentPositionMs = mp.currentPosition
                        durationMs = mp.duration
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }
            delay(200)
        }
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(20.dp)),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF121212)),
        elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Spotify3DIcon(
                        modifier = Modifier.size(22.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "Spotify Player",
                        color = Color.White,
                        fontWeight = FontWeight.Bold,
                        style = MaterialTheme.typography.titleMedium
                    )
                }
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = Color(0xFF1DB954).copy(alpha = 0.15f)
                ) {
                    Text(
                        text = if (isError) "AUDIO ERROR" else if (isBuffering) "LOADING..." else if (isPlaying) "PLAYING" else "READY",
                        color = if (isError) Color(0xFFFF4D4D) else Color(0xFF1DB954),
                        fontWeight = FontWeight.Black,
                        style = MaterialTheme.typography.labelSmall,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            Box(
                modifier = Modifier
                    .size(200.dp)
                    .clip(RoundedCornerShape(16.dp))
                    .background(Color(0xFF282828)),
                contentAlignment = Alignment.Center
            ) {
                if (thumbnailUrl.isNotEmpty()) {
                    AsyncImage(
                        model = thumbnailUrl,
                        contentDescription = "Album Cover",
                        contentScale = ContentScale.Crop,
                        modifier = Modifier.fillMaxSize()
                    )
                } else {
                    Icon(
                        imageVector = Icons.Filled.MusicNote,
                        contentDescription = null,
                        tint = Color.White.copy(alpha = 0.5f),
                        modifier = Modifier.size(64.dp)
                    )
                }
                if (isBuffering) {
                    CircularProgressIndicator(
                        color = Color(0xFF1DB954),
                        strokeWidth = 3.dp,
                        modifier = Modifier.size(36.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            Text(
                text = title,
                color = Color.White,
                fontWeight = FontWeight.Bold,
                style = MaterialTheme.typography.titleMedium,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
                textAlign = TextAlign.Center
            )

            if (!artist.isNullOrEmpty()) {
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = artist,
                    color = Color(0xFFB3B3B3),
                    fontWeight = FontWeight.Medium,
                    style = MaterialTheme.typography.bodyMedium,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    textAlign = TextAlign.Center
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            val displayMs = if (isUserScrubbing) sliderPositionMs.toInt() else currentPositionMs
            val maxMs = if (durationMs > 0) durationMs.toFloat() else 1f

            Column(modifier = Modifier.fillMaxWidth()) {
                Slider(
                    value = displayMs.toFloat().coerceIn(0f, maxMs),
                    onValueChange = { newValue ->
                        isUserScrubbing = true
                        sliderPositionMs = newValue
                    },
                    onValueChangeFinished = {
                        isUserScrubbing = false
                        mediaPlayer?.let { mp ->
                            try {
                                mp.seekTo(sliderPositionMs.toInt())
                                currentPositionMs = sliderPositionMs.toInt()
                            } catch (e: Exception) {
                                e.printStackTrace()
                            }
                        }
                    },
                    valueRange = 0f..maxMs,
                    colors = SliderDefaults.colors(
                        thumbColor = Color(0xFF1DB954),
                        activeTrackColor = Color(0xFF1DB954),
                        inactiveTrackColor = Color.White.copy(alpha = 0.2f)
                    ),
                    modifier = Modifier.fillMaxWidth()
                )

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 4.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = formatTimeMs(displayMs),
                        color = Color(0xFFB3B3B3),
                        style = MaterialTheme.typography.labelSmall
                    )
                    Text(
                        text = formatTimeMs(durationMs),
                        color = Color(0xFFB3B3B3),
                        style = MaterialTheme.typography.labelSmall
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly,
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(
                    onClick = {
                        isLooping = !isLooping
                        mediaPlayer?.let { mp ->
                            mp.isLooping = isLooping
                        }
                    },
                    modifier = Modifier
                        .clip(CircleShape)
                        .background(if (isLooping) Color(0xFF1DB954).copy(alpha = 0.2f) else Color.Transparent)
                ) {
                    Icon(
                        imageVector = Icons.Filled.Repeat,
                        contentDescription = "Loop",
                        tint = if (isLooping) Color(0xFF1DB954) else Color.White.copy(alpha = 0.7f),
                        modifier = Modifier.size(24.dp)
                    )
                }

                IconButton(
                    onClick = {
                        mediaPlayer?.let { mp ->
                            if (isPrepared) {
                                if (mp.isPlaying) {
                                    mp.pause()
                                    isPlaying = false
                                } else {
                                    mp.start()
                                    isPlaying = true
                                }
                            } else {
                                isPlaying = !isPlaying
                            }
                        }
                    },
                    modifier = Modifier
                        .size(56.dp)
                        .clip(CircleShape)
                        .background(Color(0xFF1DB954))
                ) {
                    Icon(
                        imageVector = if (isPlaying) Icons.Filled.Pause else Icons.Filled.PlayArrow,
                        contentDescription = if (isPlaying) "Pause" else "Play",
                        tint = Color.Black,
                        modifier = Modifier.size(32.dp)
                    )
                }

                val speeds = listOf(0.5f, 1.0f, 1.5f, 2.0f)
                Button(
                    onClick = {
                        val nextIdx = (speeds.indexOf(currentSpeed) + 1) % speeds.size
                        val newSpeed = speeds[nextIdx]
                        currentSpeed = newSpeed
                        mediaPlayer?.let { mp ->
                            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                                try {
                                    val wasPlaying = mp.isPlaying
                                    val params = mp.playbackParams
                                    params.speed = newSpeed
                                    mp.playbackParams = params
                                    if (!wasPlaying && mp.isPlaying) {
                                        mp.pause()
                                    }
                                } catch (e: Exception) {
                                    e.printStackTrace()
                                }
                            }
                        }
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF282828),
                        contentColor = Color.White
                    ),
                    shape = RoundedCornerShape(20.dp),
                    contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp)
                ) {
                    Text(
                        text = "${currentSpeed}x",
                        fontWeight = FontWeight.Bold,
                        style = MaterialTheme.typography.labelMedium
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(
                    onClick = {
                        if (isMuted) {
                            isMuted = false
                            volume = if (previousVolume > 0f) previousVolume else 0.8f
                        } else {
                            previousVolume = volume
                            isMuted = true
                        }
                        mediaPlayer?.let { mp ->
                            val currentVol = if (isMuted) 0f else volume
                            mp.setVolume(currentVol, currentVol)
                        }
                    },
                    modifier = Modifier.size(32.dp)
                ) {
                    val volIcon = when {
                        isMuted || volume == 0f -> Icons.Filled.VolumeOff
                        volume < 0.5f -> Icons.Filled.VolumeDown
                        else -> Icons.Filled.VolumeUp
                    }
                    Icon(
                        imageVector = volIcon,
                        contentDescription = "Volume",
                        tint = Color.White.copy(alpha = 0.8f),
                        modifier = Modifier.size(20.dp)
                    )
                }

                Slider(
                    value = if (isMuted) 0f else volume,
                    onValueChange = { newVol ->
                        volume = newVol
                        isMuted = newVol == 0f
                        mediaPlayer?.let { mp ->
                            mp.setVolume(newVol, newVol)
                        }
                    },
                    valueRange = 0f..1f,
                    colors = SliderDefaults.colors(
                        thumbColor = Color.White,
                        activeTrackColor = Color.White,
                        inactiveTrackColor = Color.White.copy(alpha = 0.2f)
                    ),
                    modifier = Modifier.weight(1f)
                )
            }
        }
    }
}"""

if old_player_start != -1 and old_player_end != -1:
    code = code[:old_player_start] + new_player_code + "\n\n" + code[old_player_end:]
    print("Replaced SpotifyMusicPlayer composable")
else:
    print("Could not find SpotifyMusicPlayer bounds")

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(code)

print("Saved updated MainActivity.kt")
