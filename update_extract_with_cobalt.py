with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    code = f.read()

# 1. Remove handleSpotifyExtraction completely
s_marker = "suspend fun handleSpotifyExtraction"
e_marker = "suspend fun extractWithCobalt"
s_idx = code.find(s_marker)
e_idx = code.find(e_marker)

if s_idx != -1 and e_idx != -1:
    code = code[:s_idx] + code[e_idx:]
    print("Removed handleSpotifyExtraction")

# 2. Update extractWithCobalt to remove manual intercept and just flag isSpotify
old_cobalt_start = code.find("suspend fun extractWithCobalt")
old_cobalt_end = code.find("fun validateUrl")

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

                val finalQs = qs.distinctBy { it.label + it.url }.toMutableList()

                if (thumbnail.isNotEmpty()) {
                    finalQs.add(MediaQuality("Thumbnail (JPG)", null, thumbnail))
                }

                if (finalQs.isNotEmpty() || arr != null) {
                    val firstAudio = finalQs.firstOrNull { it.label.contains("audio", true) || it.label.contains("mp3", true) }?.url

                    // The backend might also return these for playlist/album if they added custom logic
                    val artistName = json.optString("artist", "")
                    val isPlaylist = json.optBoolean("isPlaylist", false)

                    return@withContext DownloadResult(
                        success = true,
                        title = title,
                        thumbnailUrl = thumbnail,
                        qualities = finalQs,
                        isSpotify = isSpotify,
                        isPlaylist = isPlaylist,
                        artistName = artistName,
                        previewAudioUrl = firstAudio
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
        return@withContext DownloadResult(false, "", "", emptyList(), "Error connecting to server: ${e.message}")
    }
    return@withContext DownloadResult(false, "", "", emptyList(), "Failed to extract media.")
}"""

if old_cobalt_start != -1 and old_cobalt_end != -1:
    code = code[:old_cobalt_start] + new_cobalt + "\n\n" + code[old_cobalt_end:]
    print("Updated extractWithCobalt")

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(code)
print("Done")
