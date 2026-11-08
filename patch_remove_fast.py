import re

with open('app/src/main/java/com/example/MainActivity.kt', 'r') as f:
    content = f.read()

start_marker = 'suspend fun extractWithCobalt(url: String): DownloadResult = withContext(Dispatchers.IO) {'
end_marker = 'fun extractUrlFromIntent(context: Context, intent: Intent?): String? {'

idx1 = content.find(start_marker)
idx2 = content.find(end_marker)

if idx1 != -1 and idx2 != -1:
    before = content[:idx1]
    after = content[idx2:]
    
    new_func = """suspend fun extractWithCobalt(url: String): DownloadResult = withContext(Dispatchers.IO) {
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
                        
                        // For audio/MP3, don't show the size if it seems incorrectly large
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
    with open('app/src/main/java/com/example/MainActivity.kt', 'w') as f:
        f.write(before + new_func + after)
    print("Patched successfully!")
else:
    print("Could not find markers")
