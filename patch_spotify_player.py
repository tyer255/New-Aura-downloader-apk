import re

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    content = f.read()

# 1. Update DownloadResult data class
old_download_result = """data class DownloadResult(
    val success: Boolean,
    val title: String,
    val thumbnailUrl: String,
    val qualities: List<MediaQuality>,
    val error: String? = null
)"""

new_download_result = """data class DownloadResult(
    val success: Boolean,
    val title: String,
    val thumbnailUrl: String,
    val qualities: List<MediaQuality>,
    val error: String? = null,
    val isSpotify: Boolean = false,
    val previewAudioUrl: String? = null,
    val artistName: String? = null
)"""

if old_download_result in content:
    content = content.replace(old_download_result, new_download_result)
    print("DownloadResult patched successfully")
else:
    print("Could not find old DownloadResult")

# 2. Update extractWithCobalt
start_marker = 'suspend fun extractWithCobalt(url: String): DownloadResult = withContext(Dispatchers.IO) {'
end_marker = 'fun extractUrlFromIntent(context: Context, intent: Intent?): String? {'

idx1 = content.find(start_marker)
idx2 = content.find(end_marker)

if idx1 != -1 and idx2 != -1:
    before = content[:idx1]
    after = content[idx2:]

    new_extract_func = """suspend fun extractWithCobalt(url: String): DownloadResult = withContext(Dispatchers.IO) {
    val lowerUrl = url.lowercase()

    // SPOTIFY LINK HANDLING
    if (lowerUrl.contains("spotify.com") || lowerUrl.contains("spotify:")) {
        if (lowerUrl.contains("/playlist") || lowerUrl.contains("/album") || lowerUrl.contains("/artist")) {
            return@withContext DownloadResult(
                success = false,
                title = "",
                thumbnailUrl = "",
                qualities = emptyList(),
                error = "Spotify playlists, albums & artists are not supported. Please paste a link to a single Spotify song/track."
            )
        }

        val trackRegex = "(?:spotify\\\\.com\\\\/(?:[a-zA-Z0-9-]+\\\\/" + ")?track\\\\/|spotify:track:)([a-zA-Z0-9]{22})".toRegex()
        val match = trackRegex.find(url)
        val trackId = match?.groupValues?.get(1)

        if (trackId != null) {
            try {
                val embedUrl = "https://open.spotify.com/embed/track/$trackId"
                val request = Request.Builder()
                    .url(embedUrl)
                    .addHeader("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                    .build()

                val response = okHttpClient.newCall(request).execute()
                var trackTitle = "Spotify Track"
                var artistName = "Spotify Artist"
                var thumbnailUrl = ""
                var previewUrl = ""

                if (response.isSuccessful) {
                    val html = response.body?.string() ?: ""

                    val entityRegex = "\"entity\":(\\\\{.*?\\\\}),\"".toRegex()
                    val entityMatch = entityRegex.find(html)
                    if (entityMatch != null) {
                        try {
                            val json = JSONObject(entityMatch.groupValues[1])
                            trackTitle = json.optString("name", "Spotify Track")
                            val artistsArray = json.optJSONArray("artists")
                            if (artistsArray != null && artistsArray.length() > 0) {
                                val names = mutableListOf<String>()
                                for (i in 0 until artistsArray.length()) {
                                    names.add(artistsArray.getJSONObject(i).optString("name"))
                                }
                                artistName = names.joinToString(", ")
                            }

                            val audioPreviewObj = json.optJSONObject("audioPreview")
                            if (audioPreviewObj != null) {
                                previewUrl = audioPreviewObj.optString("url", "")
                            }

                            val visualIdentityObj = json.optJSONObject("visualIdentity")
                            if (visualIdentityObj != null) {
                                val images = visualIdentityObj.optJSONArray("image")
                                if (images != null && images.length() > 0) {
                                    thumbnailUrl = images.getJSONObject(0).optString("url", "")
                                }
                            }
                        } catch (e: Exception) {
                            e.printStackTrace()
                        }
                    }
                }

                if (thumbnailUrl.isEmpty()) {
                    try {
                        val oembedReq = Request.Builder().url("https://open.spotify.com/oembed?url=https://open.spotify.com/track/$trackId").build()
                        val oembedRes = okHttpClient.newCall(oembedReq).execute()
                        if (oembedRes.isSuccessful) {
                            val ojson = JSONObject(oembedRes.body?.string() ?: "")
                            if (trackTitle == "Spotify Track") trackTitle = ojson.optString("title", "Spotify Track")
                            thumbnailUrl = ojson.optString("thumbnail_url", "")
                        }
                    } catch (e: Exception) {
                        e.printStackTrace()
                    }
                }

                val backendUrl = BuildConfig.BACKEND_URL
                val qualities = mutableListOf<MediaQuality>()
                val baseApiUrl = backendUrl.replace("/api/download", "")

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
                                    qualities.add(MediaQuality(qLabel, item.optString("size", null), qUrl))
                                }
                            }
                        }
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                }

                if (previewUrl.isNotEmpty()) {
                    qualities.add(0, MediaQuality("Preview Track (30s MP3)", null, previewUrl))
                }
                if (qualities.isEmpty() && previewUrl.isNotEmpty()) {
                    qualities.add(MediaQuality("Download Track MP3", null, previewUrl))
                }
                if (thumbnailUrl.isNotEmpty()) {
                    qualities.add(MediaQuality("Album Cover Art (JPG)", null, thumbnailUrl))
                }

                val displayTitle = if (artistName.isNotEmpty() && !trackTitle.contains(artistName)) "$trackTitle - $artistName" else trackTitle

                val finalPreviewAudio = if (previewUrl.isNotEmpty()) previewUrl else qualities.firstOrNull { it.url.isNotEmpty() }?.url

                return@withContext DownloadResult(
                    success = true,
                    title = displayTitle,
                    thumbnailUrl = thumbnailUrl,
                    qualities = qualities,
                    isSpotify = true,
                    previewAudioUrl = finalPreviewAudio,
                    artistName = artistName
                )
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

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
                val title = json.optString("title", "Video Download")
                val thumbnail = json.optString("thumbnail", "")
                val qs = mutableListOf<MediaQuality>()
                val arr = json.optJSONArray("qualities") ?: json.optJSONArray("media")
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

                var finalQs = qs.distinctBy { it.label + it.url }.toMutableList()

                if (thumbnail.isNotEmpty()) {
                    finalQs.add(MediaQuality("Thumbnail (JPG)", null, thumbnail))
                }

                if (finalQs.isNotEmpty() || arr != null) {
                    return@withContext DownloadResult(true, title, thumbnail, finalQs)
                }
            } else {
                return@withContext DownloadResult(false, "", "", emptyList(), json.optString("message", "Extraction failed."))
            }
        }
    } catch (e: Exception) {
        e.printStackTrace()
        return@withContext DownloadResult(false, "", "", emptyList(), "Failed to connect to Server. Please check your internet connection.")
    }

    return@withContext DownloadResult(false, "", "", emptyList(), "Failed to extract video. Make sure the link is valid.")
}

"""
    content = before + new_extract_func + after
    print("extractWithCobalt patched successfully")
else:
    print("Could not find extractWithCobalt markers")

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(content)

