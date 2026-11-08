import re

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    content = f.read()

new_extract = """suspend fun extractWithCobalt(url: String): DownloadResult = withContext(Dispatchers.IO) {
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

                return@withContext DownloadResult(
                    success = true,
                    title = title,
                    thumbnailUrl = thumbnail,
                    qualities = qs
                )
            } else {
                val message = json.optString("message", "Failed to extract link.")
                return@withContext DownloadResult(false, "", "", emptyList(), error = message)
            }
        } else {
            return@withContext DownloadResult(false, "", "", emptyList(), error = "Server returned ${response.code}")
        }
    } catch (e: Exception) {
        return@withContext DownloadResult(false, "", "", emptyList(), error = e.localizedMessage ?: "Unknown error")
    }
}"""

start_idx = content.find("suspend fun extractWithCobalt(url: String): DownloadResult = withContext(Dispatchers.IO) {")
if start_idx != -1:
    end_idx = content.find("fun extractUrlFromIntent", start_idx)
    if end_idx != -1:
        new_content = content[:start_idx] + new_extract + "\n\n" + content[end_idx:]
        with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
            f.write(new_content)
        print("Replaced!")
    else:
        print("Could not find end")
else:
    print("Could not find start")
