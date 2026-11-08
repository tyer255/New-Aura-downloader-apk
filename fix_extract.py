with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    code = f.read()

start_kw = "suspend fun extractWithCobalt"
end_kw = "fun extractUrlFromIntent"

s_idx = code.find(start_kw)
e_idx = code.find(end_kw)

clean_fn = """suspend fun extractWithCobalt(url: String): DownloadResult = withContext(Dispatchers.IO) {
    val lowerUrl = url.lowercase()

    // SPOTIFY LINK HANDLING
    if (lowerUrl.contains("spotify.com") || lowerUrl.contains("spotify:")) {
        return@withContext handleSpotifyExtraction(url)
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

                val finalQs = qs.distinctBy { it.label + it.url }.toMutableList()

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

code = code[:s_idx] + clean_fn + code[e_idx:]
with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(code)

print("Cleaned extractWithCobalt")
