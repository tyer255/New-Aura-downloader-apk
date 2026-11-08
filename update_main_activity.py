import re

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    code = f.read()

# 1. Update SpotifyTrack data class
old_track_class = "data class SpotifyTrack(\n    val name: String,\n    val artist: String = \"\",\n    val durationStr: String? = null,\n    val trackNumber: Int = 1\n)"
new_track_class = """data class SpotifyTrack(
    val name: String,
    val artist: String = "",
    val durationStr: String? = null,
    val trackNumber: Int = 1,
    val resolveUrl: String? = null,
    val directAudioUrl: String? = null,
    val thumbnailUrl: String? = null
)"""

if old_track_class in code:
    code = code.replace(old_track_class, new_track_class)
    print("Updated SpotifyTrack data class")

# 2. Add resolveSpotifyUrl function
resolve_fn = """
suspend fun resolveSpotifyUrl(url: String): String = withContext(Dispatchers.IO) {
    if (url.isEmpty()) return@withContext url
    if (!url.contains("spotify-resolve")) return@withContext url

    val fullUrl = if (url.startsWith("/")) {
        BuildConfig.BACKEND_URL.replace("/api/download", "") + url
    } else url

    try {
        val request = Request.Builder()
            .url(fullUrl)
            .get()
            .addHeader("User-Agent", "Mozilla/5.0")
            .build()
        val response = okHttpClient.newCall(request).execute()
        if (response.isSuccessful) {
            val resStr = response.body?.string() ?: ""
            if (resStr.trim().startsWith("{")) {
                val json = JSONObject(resStr)
                if (json.optBoolean("success", true) && json.has("url")) {
                    val realUrl = json.getString("url")
                    if (realUrl.isNotEmpty()) {
                        return@withContext realUrl
                    }
                }
            }
        }
    } catch (e: Exception) {
        e.printStackTrace()
    }
    return@withContext fullUrl
}
"""

if "suspend fun resolveSpotifyUrl" not in code:
    code = code.replace("suspend fun extractWithCobalt", resolve_fn + "\nsuspend fun extractWithCobalt")
    print("Added resolveSpotifyUrl")

# 3. Replace extractWithCobalt implementation
s_marker = "suspend fun extractWithCobalt(url: String): DownloadResult = withContext(Dispatchers.IO) {"
e_marker = "fun extractUrlFromIntent"

s_idx = code.find(s_marker)
e_idx = code.find(e_marker)

new_cobalt = """suspend fun extractWithCobalt(url: String): DownloadResult = withContext(Dispatchers.IO) {
    val lowerUrl = url.lowercase()
    val isSpotify = lowerUrl.contains("spotify.com") || lowerUrl.contains("spotify:")

    val backendUrl = BuildConfig.BACKEND_URL
    try {
        val jsonPayload = JSONObject().apply { put("url", url) }.toString()
        val requestBody = jsonPayload.toRequestBody("application/json".toMediaType())
        val request = Request.Builder()
            .url(backendUrl)
            .post(requestBody)
            .addHeader("Content-Type", "application/json")
            .build()

        val response = okHttpClient.newCall(request).execute()
        if (response.isSuccessful) {
            val resStr = response.body?.string() ?: ""
            val json = JSONObject(resStr)
            val success = json.optBoolean("success", false)

            if (success) {
                val title = json.optString("title", "Audio/Video Download")
                val thumbnail = json.optString("thumbnail", "")
                val mediaType = json.optString("mediaType", "")
                val artistName = json.optString("artist", "")
                val isPlaylist = mediaType == "playlist" || mediaType == "album" || json.optBoolean("isPlaylist", false)

                val qs = mutableListOf<MediaQuality>()
                val parsedTracks = mutableListOf<SpotifyTrack>()

                val mediaArr = json.optJSONArray("media")
                if (mediaArr != null) {
                    for (i in 0 until mediaArr.length()) {
                        val mObj = mediaArr.optJSONObject(i)
                        if (mObj != null) {
                            val tTitle = mObj.optString("title", "Track ${i+1}")
                            val tThumb = mObj.optString("thumbnail", thumbnail)
                            var tUrl = mObj.optString("url")
                            if (tUrl.startsWith("/")) tUrl = backendUrl.replace("/api/download", "") + tUrl

                            val innerQs = mObj.optJSONArray("qualities")
                            if (innerQs != null && innerQs.length() > 0) {
                                val q0 = innerQs.optJSONObject(0)
                                if (q0 != null) {
                                    var q0U = q0.optString("url")
                                    if (q0U.startsWith("/")) q0U = backendUrl.replace("/api/download", "") + q0U
                                    if (q0U.isNotEmpty()) tUrl = q0U
                                }
                            }

                            parsedTracks.add(SpotifyTrack(
                                name = tTitle,
                                artist = artistName,
                                trackNumber = i + 1,
                                resolveUrl = tUrl,
                                thumbnailUrl = tThumb
                            ))
                        }
                    }
                }

                val tracksArray = json.optJSONArray("spotifyTracks")
                if (tracksArray != null) {
                    for (i in 0 until tracksArray.length()) {
                        val tObj = tracksArray.optJSONObject(i)
                        if (tObj != null) {
                            val name = tObj.optString("name", "Track")
                            val art = tObj.optString("artist", artistName)
                            val dur = tObj.optString("durationStr", null)
                            val tNum = tObj.optInt("trackNumber", i + 1)
                            var resUrl = tObj.optString("url", tObj.optString("resolveUrl", ""))
                            if (resUrl.startsWith("/")) resUrl = backendUrl.replace("/api/download", "") + resUrl

                            if (parsedTracks.none { it.name == name }) {
                                parsedTracks.add(SpotifyTrack(
                                    name = name,
                                    artist = art,
                                    durationStr = dur,
                                    trackNumber = tNum,
                                    resolveUrl = if (resUrl.isNotEmpty()) resUrl else null
                                ))
                            }
                        }
                    }
                }

                val arr = json.optJSONArray("qualities")
                if (arr != null) {
                    for (i in 0 until arr.length()) {
                        val item = arr.getJSONObject(i)
                        val qLabel = item.optString("label", item.optString("resolution", "Download"))
                        var qUrl = item.optString("url")
                        if (qUrl.startsWith("/")) qUrl = backendUrl.replace("/api/download", "") + qUrl
                        val qSize = item.optString("size", "")
                        val isAudio = qLabel.contains("audio", true) || qLabel.contains("mp3", true)
                        val finalSize = if (qSize.isEmpty() || qSize == "Unknown Size") null else if (isAudio) null else qSize
                        qs.add(MediaQuality(qLabel, finalSize, qUrl))
                    }
                }

                val rawQs = qs.distinctBy { it.label + it.url }.toMutableList()

                val resolvedQs = rawQs.map { q ->
                    if (q.url.contains("spotify-resolve")) {
                        val directUrl = resolveSpotifyUrl(q.url)
                        MediaQuality(q.label, q.size, directUrl)
                    } else {
                        q
                    }
                }.toMutableList()

                if (thumbnail.isNotEmpty()) {
                    resolvedQs.add(MediaQuality("Thumbnail (JPG)", null, thumbnail))
                }

                if (resolvedQs.isNotEmpty() || parsedTracks.isNotEmpty() || arr != null || mediaArr != null) {
                    var firstAudio = resolvedQs.firstOrNull {
                        it.label.contains("audio", true) || it.label.contains("mp3", true) || it.url.endsWith(".mp3") || it.url.contains("savetube")
                    }?.url

                    if (firstAudio == null && parsedTracks.isNotEmpty()) {
                        val firstTrackUrl = parsedTracks.first().resolveUrl
                        if (!firstTrackUrl.isNullOrEmpty()) {
                            firstAudio = resolveSpotifyUrl(firstTrackUrl)
                        }
                    }

                    return@withContext DownloadResult(
                        success = true,
                        title = title,
                        thumbnailUrl = thumbnail,
                        qualities = resolvedQs,
                        isSpotify = isSpotify,
                        isPlaylist = isPlaylist,
                        artistName = artistName,
                        previewAudioUrl = firstAudio,
                        spotifyTracks = parsedTracks
                    )
                }
            } else {
                return@withContext DownloadResult(false, "", "", emptyList(), json.optString("message", "Extraction failed."))
            }
        } else {
            return@withContext DownloadResult(false, "", "", emptyList(), "Server returned code ${response.code}")
        }
    } catch (e: Exception) {
        e.printStackTrace()
        return@withContext DownloadResult(false, "", "", emptyList(), "Failed to connect to Server. Please check your internet connection.")
    }
    return@withContext DownloadResult(false, "", "", emptyList(), "Failed to extract media. Make sure the link is valid.")
}

"""

if s_idx != -1 and e_idx != -1:
    code = code[:s_idx] + new_cobalt + code[e_idx:]
    print("Replaced extractWithCobalt")

# 4. Update SpotifyMusicPlayer DisposableEffect
sp_player_start = code.find("fun SpotifyMusicPlayer(")
sp_disposable_start = code.find("DisposableEffect(audioUrl) {", sp_player_start)
sp_disposable_end = code.find("LaunchedEffect(isPlaying, isUserScrubbing)", sp_disposable_start)

if sp_disposable_start != -1 and sp_disposable_end != -1:
    new_sp_logic = """    var activeAudioUrl by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(audioUrl) {
        isPrepared = false
        isBuffering = true
        isError = false
        activeAudioUrl = resolveSpotifyUrl(audioUrl)
    }

    DisposableEffect(activeAudioUrl) {
        val targetUrl = activeAudioUrl
        if (targetUrl.isNullOrEmpty()) {
            return@DisposableEffect onDispose {}
        }

        val player = MediaPlayer().apply {
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                    setAudioAttributes(
                        android.media.AudioAttributes.Builder()
                            .setContentType(android.media.AudioAttributes.CONTENT_TYPE_MUSIC)
                            .setUsage(android.media.AudioAttributes.USAGE_MEDIA)
                            .build()
                    )
                }
                setDataSource(context, Uri.parse(targetUrl))
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

"""
    code = code[:sp_disposable_start] + new_sp_logic + code[sp_disposable_end:]
    print("Updated SpotifyMusicPlayer disposable effect")

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(code)

print("Update completed successfully")
