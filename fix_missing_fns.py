import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    code = f.read()

fns = """
fun extractYouTubeVideoId(url: String): String? {
    val regex = Regex(\"\"\"(?<=v=|v/|vi=|vi/|youtu.be/|/shorts/|/e/|/embed/|/v/|/watch\?v=|&v=)([a-zA-Z0-9_-]{11})\"\"\")
    return regex.find(url)?.groupValues?.getOrNull(1) ?: Regex(\"\"\"[a-zA-Z0-9_-]{11}\"\"\").find(url)?.value
}

suspend fun resolveSpotifyUrl(url: String, trackTitle: String? = null, trackArtist: String? = null): String = withContext(Dispatchers.IO) {
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
        } catch (e: Exception) {}
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
        } catch (e: Exception) {}
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
                val json = org.json.JSONObject(resStr)
                if (json.optBoolean("success", true) && json.has("url")) {
                    val realUrl = json.getString("url")
                    if (realUrl.isNotEmpty()) {
                        return@withContext realUrl
                    }
                }
            }
        }
    } catch (e: Exception) {}
    return@withContext url
}

"""

if "fun extractYouTubeVideoId" not in code:
    idx = code.find("fun extractUrlFromIntent")
    code = code[:idx] + fns + code[idx:]

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(code)
