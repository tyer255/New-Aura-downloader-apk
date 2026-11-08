with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    code = f.read()

s_marker = "suspend fun handleSpotifyExtraction"
e_marker = "suspend fun extractWithCobalt"

s_idx = code.find(s_marker)
e_idx = code.find(e_marker)

clean_handle_spotify = """suspend fun handleSpotifyExtraction(url: String): DownloadResult {
    val lowerUrl = url.lowercase()
    val spotifyRegex = kotlin.text.Regex("(?:spotify\\\\.com\\\\/(?:[a-zA-Z0-9-]+\\\\/" + ")?|spotify:)(track|playlist|album|artist)[:\\\\/]([a-zA-Z0-9]{22})")
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

            if (html.contains("p.scdn.co/mp3-preview/")) {
                val scdnRegex = kotlin.text.Regex("https://p\\\\.scdn\\\\.co/mp3-preview/[a-f0-9]+")
                val scdnMatch = scdnRegex.find(html)
                if (scdnMatch != null) {
                    previewAudioUrl = scdnMatch.value
                }
            }

            val nextDataRegex = kotlin.text.Regex("<script id=\\"__NEXT_DATA__\\" type=\\"application/json\\">(.*?)</script>", setOf(RegexOption.DOT_MATCHES_ALL))
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
}

"""

if s_idx != -1 and e_idx != -1:
    code = code[:s_idx] + clean_handle_spotify + code[e_idx:]
    with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
        f.write(code)
    print("Cleaned handleSpotifyExtraction")
else:
    print("Failed to find handleSpotifyExtraction index range")
