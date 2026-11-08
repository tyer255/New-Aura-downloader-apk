with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    code = f.read()

# 1. Update resolveSpotifyUrl signature and implementation
old_resolve_fn = """suspend fun resolveSpotifyUrl(url: String): String = withContext(Dispatchers.IO) {
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
}"""

new_resolve_fn = """suspend fun resolveSpotifyUrl(url: String, trackTitle: String? = null, trackArtist: String? = null): String = withContext(Dispatchers.IO) {
    if (url.isEmpty()) return@withContext url
    if (!url.contains("spotify-resolve")) return@withContext url

    var fullUrl = if (url.startsWith("/")) {
        BuildConfig.BACKEND_URL.replace("/api/download", "") + url
    } else url

    if (!trackTitle.isNullOrEmpty()) {
        try {
            val encodedTitle = java.net.URLEncoder.encode(trackTitle, "UTF-8")
            if (fullUrl.contains("title=&")) {
                fullUrl = fullUrl.replace("title=&", "title=$encodedTitle&")
            } else if (fullUrl.endsWith("title=")) {
                fullUrl += encodedTitle
            } else if (!fullUrl.contains("title=")) {
                fullUrl += "&title=$encodedTitle"
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    if (!trackArtist.isNullOrEmpty()) {
        try {
            val encodedArtist = java.net.URLEncoder.encode(trackArtist, "UTF-8")
            if (fullUrl.contains("artist=&")) {
                fullUrl = fullUrl.replace("artist=&", "artist=$encodedArtist&")
            } else if (fullUrl.endsWith("artist=")) {
                fullUrl += encodedArtist
            } else if (!fullUrl.contains("artist=")) {
                fullUrl += "&artist=$encodedArtist"
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

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
}"""

if old_resolve_fn in code:
    code = code.replace(old_resolve_fn, new_resolve_fn)
    print("Updated resolveSpotifyUrl function with trackTitle & trackArtist parameters")

# 2. Update resolveSpotifyUrl call in extractWithCobalt
old_cobalt_qs = """                val resolvedQs = rawQs.map { q ->
                    if (q.url.contains("spotify-resolve")) {
                        val directUrl = resolveSpotifyUrl(q.url)
                        MediaQuality(q.label, q.size, directUrl)
                    } else {
                        q
                    }
                }.toMutableList()"""

new_cobalt_qs = """                val resolvedQs = rawQs.map { q ->
                    if (q.url.contains("spotify-resolve")) {
                        val directUrl = resolveSpotifyUrl(q.url, title, artistName)
                        MediaQuality(q.label, q.size, directUrl)
                    } else {
                        q
                    }
                }.toMutableList()"""

if old_cobalt_qs in code:
    code = code.replace(old_cobalt_qs, new_cobalt_qs)
    print("Updated resolvedQs in extractWithCobalt")

# 3. Update firstAudio resolve in extractWithCobalt
old_first_audio = """                    if (firstAudio == null && parsedTracks.isNotEmpty()) {
                        val firstTrackUrl = parsedTracks.first().resolveUrl
                        if (!firstTrackUrl.isNullOrEmpty()) {
                            firstAudio = resolveSpotifyUrl(firstTrackUrl)
                        }
                    }"""

new_first_audio = """                    if (firstAudio == null && parsedTracks.isNotEmpty()) {
                        val firstTrack = parsedTracks.first()
                        val firstTrackUrl = firstTrack.resolveUrl
                        if (!firstTrackUrl.isNullOrEmpty()) {
                            firstAudio = resolveSpotifyUrl(firstTrackUrl, firstTrack.name, firstTrack.artist.ifEmpty { artistName })
                        }
                    }"""

if old_first_audio in code:
    code = code.replace(old_first_audio, new_first_audio)
    print("Updated firstAudio in extractWithCobalt")

# 4. Update LaunchedEffect in SpotifyMusicPlayer
old_player_effect = """    LaunchedEffect(audioUrl) {
        isPrepared = false
        isBuffering = true
        isError = false
        currentSpeed = 1.0f
        activeAudioUrl = resolveSpotifyUrl(audioUrl)
    }"""

new_player_effect = """    LaunchedEffect(audioUrl, title, artist) {
        isPrepared = false
        isBuffering = true
        isError = false
        currentSpeed = 1.0f
        activeAudioUrl = resolveSpotifyUrl(audioUrl, title, artist)
    }"""

if old_player_effect in code:
    code = code.replace(old_player_effect, new_player_effect)
    print("Updated LaunchedEffect in SpotifyMusicPlayer")

# 5. Update resolveAndTriggerDownload
old_dl_target = """            if (initialUrl.contains("/api/get-youtube-link") || initialUrl.contains("get-youtube-link") || initialUrl.contains("spotify-resolve")) {"""
new_dl_target = """            if (initialUrl.contains("spotify-resolve")) {
                if (title.isNotEmpty()) {
                    try {
                        val encT = java.net.URLEncoder.encode(title, "UTF-8")
                        if (initialUrl.contains("title=&")) initialUrl = initialUrl.replace("title=&", "title=$encT&")
                        else if (initialUrl.endsWith("title=")) initialUrl += encT
                        else if (!initialUrl.contains("title=")) initialUrl += "&title=$encT"
                    } catch (e: Exception) { e.printStackTrace() }
                }
            }
            if (initialUrl.contains("/api/get-youtube-link") || initialUrl.contains("get-youtube-link") || initialUrl.contains("spotify-resolve")) {"""

if old_dl_target in code:
    code = code.replace(old_dl_target, new_dl_target)
    print("Updated resolveAndTriggerDownload for title injection")

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(code)

print("Update finished")
