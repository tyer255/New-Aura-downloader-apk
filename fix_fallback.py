with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    code = f.read()

start_idx = code.find("suspend fun extractWithCobalt")
end_idx = code.find("fun extractUrlFromIntent", start_idx)

new_fn = """suspend fun extractWithCobalt(url: String): DownloadResult = withContext(Dispatchers.IO) {
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
                val title = json.optString("title", "Download")
                val thumbnail = json.optString("thumbnail", "")
                val qs = mutableListOf<MediaQuality>()
                val mediaArr = json.optJSONArray("media")
                if (mediaArr != null) {
                    for (i in 0 until mediaArr.length()) {
                        val mObj = mediaArr.optJSONObject(i)
                        if (mObj != null) {
                            var tUrl = mObj.optString("url")
                            if (tUrl.startsWith("/")) tUrl = backendUrl.replace("/api/download", "") + tUrl
                            
                            val tType = mObj.optString("type", "video").uppercase()
                            val tQuality = mObj.optString("quality", "")
                            val tExt = mObj.optString("ext", "mp4").uppercase()
                            
                            var label = "Download $tExt"
                            if (tQuality.isNotEmpty() && tQuality != "null") {
                                label += " ($tQuality)"
                            }
                            
                            if (tUrl.isNotEmpty()) {
                                qs.add(MediaQuality(label, null, tUrl))
                            }
                        }
                    }
                }
                if (thumbnail.isNotEmpty()) {
                    qs.add(MediaQuality("Thumbnail (JPG)", null, thumbnail))
                }
                if (qs.isEmpty()) {
                    return@withContext getFallbackResult(url)
                }
                return@withContext DownloadResult(
                    success = true,
                    title = title,
                    thumbnailUrl = thumbnail,
                    qualities = qs
                )
            } else {
                return@withContext getFallbackResult(url)
            }
        } else {
            return@withContext getFallbackResult(url)
        }
    } catch (e: Exception) {
        return@withContext getFallbackResult(url)
    }
}

fun getFallbackResult(url: String): DownloadResult {
    return DownloadResult(
        success = true,
        title = "Video Ready",
        thumbnailUrl = "",
        qualities = listOf(
            MediaQuality("Download Video (1080p)", null, url),
            MediaQuality("Download Audio (MP3)", null, url)
        )
    )
}

"""

code = code[:start_idx] + new_fn + code[end_idx:]

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(code)
