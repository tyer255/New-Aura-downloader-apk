import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    code = f.read()

# Add necessary imports
new_imports = """
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.CoroutineScope
import okhttp3.Call
import okhttp3.Callback
import okhttp3.ConnectionPool
import okhttp3.Response
import java.io.IOException
import java.util.concurrent.TimeUnit
"""

if "import kotlinx.coroutines.async" not in code:
    code = code.replace("import kotlinx.coroutines.Dispatchers", new_imports + "\nimport kotlinx.coroutines.Dispatchers")

# Replace okHttpClient definition and extractWithCobalt
old_target_start = "val okHttpClient = OkHttpClient.Builder()"
old_target_end = "fun extractUrlFromIntent(context: Context, intent: Intent?): String? {"

idx1 = code.find(old_target_start)
idx2 = code.find(old_target_end)

if idx1 != -1 and idx2 != -1:
    before = code[:idx1]
    after = code[idx2:]

    replacement = '''val okHttpClient = OkHttpClient.Builder()
    .connectTimeout(12, TimeUnit.SECONDS)
    .readTimeout(25, TimeUnit.SECONDS)
    .writeTimeout(15, TimeUnit.SECONDS)
    .connectionPool(ConnectionPool(10, 5, TimeUnit.MINUTES))
    .retryOnConnectionFailure(true)
    .build()

fun warmUpBackend() {
    CoroutineScope(Dispatchers.IO).launch {
        try {
            val req = Request.Builder()
                .url("https://aura-downloader-yg40.onrender.com/")
                .header("User-Agent", "AuraDownloaderFast/1.0")
                .build()
            okHttpClient.newCall(req).enqueue(object : Callback {
                override fun onFailure(call: Call, e: IOException) {}
                override fun onResponse(call: Call, response: Response) { response.close() }
            })
        } catch (_: Exception) {}
    }
}

data class FastMeta(val title: String, val thumbnailUrl: String, val streamUrl: String? = null)

fun fetchFastMeta(url: String): FastMeta? {
    val lower = url.lowercase()
    try {
        if (lower.contains("youtube.com") || lower.contains("youtu.be")) {
            val ytRegex = Regex("""(?:youtu\\.be/|youtube\\.com/(?:embed/|v/|watch\\?v=|watch\\?.+&v=|shorts/))([a-zA-Z0-9_-]{11})""")
            val videoId = ytRegex.find(url)?.groupValues?.getOrNull(1)
            var thumb = if (videoId != null) "https://i.ytimg.com/vi/$videoId/hqdefault.jpg" else ""
            var title = "YouTube Video"

            val oembedReq = Request.Builder().url("https://www.youtube.com/oembed?url=$url&format=json").build()
            val oembedRes = okHttpClient.newCall(oembedReq).execute()
            if (oembedRes.isSuccessful) {
                val json = JSONObject(oembedRes.body?.string() ?: "")
                title = json.optString("title", title)
                val author = json.optString("author_name", "")
                if (author.isNotEmpty() && !title.contains(author)) {
                    title = "$title - $author"
                }
                val oThumb = json.optString("thumbnail_url", "")
                if (oThumb.isNotEmpty()) thumb = oThumb
            }
            return FastMeta(title, thumb)
        }

        if (lower.contains("tiktok.com")) {
            val oembedReq = Request.Builder().url("https://www.tiktok.com/oembed?url=$url").build()
            val oembedRes = okHttpClient.newCall(oembedReq).execute()
            if (oembedRes.isSuccessful) {
                val json = JSONObject(oembedRes.body?.string() ?: "")
                val title = json.optString("title", "TikTok Video")
                val author = json.optString("author_name", "")
                val displayTitle = if (author.isNotEmpty()) "$title - @$author" else title
                val thumb = json.optString("thumbnail_url", "")
                return FastMeta(displayTitle, thumb)
            }
        }
    } catch (_: Exception) {}
    return null
}

fun fetchBackendApi(url: String): DownloadResult? {
    val backendUrl = BuildConfig.BACKEND_URL
    val baseApiUrl = backendUrl.replace("/api/download", "")

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
            val success = json.optBoolean("success", true)

            val title = json.optString("title", json.optString("filename", "Media Download"))
            val thumbnail = json.optString("thumbnail", json.optString("cover", json.optString("image", "")))

            val qs = mutableListOf<MediaQuality>()

            val arr = json.optJSONArray("qualities")
                ?: json.optJSONArray("media")
                ?: json.optJSONArray("picker")
                ?: json.optJSONArray("items")

            if (arr != null) {
                for (i in 0 until arr.length()) {
                    val item = arr.getJSONObject(i)
                    val qLabel = item.optString("label", item.optString("resolution", item.optString("type", "Download")))
                    var qUrl = item.optString("url", item.optString("src", ""))
                    if (qUrl.startsWith("/")) qUrl = baseApiUrl + qUrl
                    val qSize = item.optString("size", "")
                    val finalSize = if (qSize.isEmpty() || qSize == "Unknown Size") null else qSize

                    if (qUrl.isNotEmpty()) {
                        qs.add(MediaQuality(qLabel, finalSize, qUrl))
                    }
                }
            }

            val rootUrl = json.optString("url", json.optString("streamUrl", json.optString("downloadUrl", "")))
            if (rootUrl.isNotEmpty()) {
                var fullRootUrl = rootUrl
                if (fullRootUrl.startsWith("/")) fullRootUrl = baseApiUrl + fullRootUrl
                if (qs.none { it.url == fullRootUrl }) {
                    val qualityLabel = if (json.has("quality")) "Download ${json.optString("quality")}" else "Download High Quality"
                    qs.add(0, MediaQuality(qualityLabel, null, fullRootUrl))
                }
            }

            val pickerObj = json.optJSONObject("picker")
            if (pickerObj != null) {
                val pickerArr = pickerObj.optJSONArray("images") ?: pickerObj.optJSONArray("items")
                if (pickerArr != null) {
                    for (i in 0 until pickerArr.length()) {
                        val item = pickerArr.getJSONObject(i)
                        var pUrl = item.optString("url", "")
                        if (pUrl.startsWith("/")) pUrl = baseApiUrl + pUrl
                        if (pUrl.isNotEmpty()) {
                            qs.add(MediaQuality("Photo / Media #${i + 1}", null, pUrl))
                        }
                    }
                }
            }

            val finalQs = qs.distinctBy { it.label + it.url }
            if (finalQs.isNotEmpty()) {
                return DownloadResult(true, title, thumbnail, finalQs)
            } else if (!success) {
                return DownloadResult(false, "", "", emptyList(), json.optString("message", "Extraction failed."))
            }
        }
    } catch (e: Exception) {
        e.printStackTrace()
    }
    return null
}

suspend fun extractWithCobalt(url: String): DownloadResult = withContext(Dispatchers.IO) {
    val cleanUrl = url.trim()
    val lowerUrl = cleanUrl.lowercase()

    warmUpBackend()

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

        val trackRegex = Regex("""(?:spotify\\.com/(?:[a-zA-Z0-9-]+/)?track/|spotify:track:)([a-zA-Z0-9]{22})""")
        val trackId = trackRegex.find(cleanUrl)?.groupValues?.getOrNull(1)

        if (trackId != null) {
            try {
                return@withContext coroutineScope {
                    val embedDeferred = async {
                        try {
                            val req = Request.Builder()
                                .url("https://open.spotify.com/embed/track/$trackId")
                                .addHeader("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                                .build()
                            val res = okHttpClient.newCall(req).execute()
                            if (res.isSuccessful) res.body?.string() else null
                        } catch (_: Exception) { null }
                    }

                    val oembedDeferred = async {
                        try {
                            val req = Request.Builder().url("https://open.spotify.com/oembed?url=https://open.spotify.com/track/$trackId").build()
                            val res = okHttpClient.newCall(req).execute()
                            if (res.isSuccessful) JSONObject(res.body?.string() ?: "") else null
                        } catch (_: Exception) { null }
                    }

                    val backendDeferred = async {
                        fetchBackendApi(cleanUrl)
                    }

                    val html = embedDeferred.await()
                    val ojson = oembedDeferred.await()
                    val backendResult = backendDeferred.await()

                    var trackTitle = ojson?.optString("title")?.takeIf { it.isNotEmpty() } ?: "Spotify Track"
                    var artistName = ""
                    var thumbnailUrl = ojson?.optString("thumbnail_url") ?: ""
                    var previewUrl = ""

                    if (!html.isNullOrEmpty()) {
                        val entityRegex = Regex(""""entity":(\{.*?\}),"*""")
                        val entityMatch = entityRegex.find(html)
                        if (entityMatch != null) {
                            try {
                                val entityJsonStr = entityMatch.groupValues.getOrNull(1) ?: ""
                                val json = JSONObject(entityJsonStr)
                                val name = json.optString("name", "")
                                if (name.isNotEmpty()) trackTitle = name

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

                                if (thumbnailUrl.isEmpty()) {
                                    val visualIdentityObj = json.optJSONObject("visualIdentity")
                                    val images = visualIdentityObj?.optJSONArray("image")
                                    if (images != null && images.length() > 0) {
                                        thumbnailUrl = images.getJSONObject(0).optString("url", "")
                                    }
                                }
                            } catch (_: Exception) {}
                        }
                    }

                    val qualities = mutableListOf<MediaQuality>()
                    if (backendResult != null && backendResult.qualities.isNotEmpty()) {
                        qualities.addAll(backendResult.qualities)
                    }

                    if (previewUrl.isNotEmpty()) {
                        qualities.add(0, MediaQuality("Preview Track (30s MP3)", null, previewUrl))
                    }
                    if (qualities.isEmpty() && previewUrl.isNotEmpty()) {
                        qualities.add(MediaQuality("Download Track MP3", null, previewUrl))
                    }
                    if (thumbnailUrl.isNotEmpty() && qualities.none { it.label.contains("Art") }) {
                        qualities.add(MediaQuality("Album Cover Art (JPG)", null, thumbnailUrl))
                    }

                    val displayTitle = if (artistName.isNotEmpty() && !trackTitle.contains(artistName)) "$trackTitle - $artistName" else trackTitle
                    val finalPreviewAudio = if (previewUrl.isNotEmpty()) previewUrl else qualities.firstOrNull { it.url.isNotEmpty() }?.url

                    DownloadResult(
                        success = true,
                        title = displayTitle,
                        thumbnailUrl = thumbnailUrl,
                        qualities = qualities,
                        isSpotify = true,
                        previewAudioUrl = finalPreviewAudio,
                        artistName = artistName
                    )
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    return@withContext coroutineScope {
        val fastMetaDeferred = async { fetchFastMeta(cleanUrl) }
        val backendDeferred = async { fetchBackendApi(cleanUrl) }

        val fastMeta = fastMetaDeferred.await()
        val backendRes = backendDeferred.await()

        if (backendRes != null && backendRes.success) {
            val finalTitle = if (backendRes.title.isNotEmpty() && backendRes.title != "Video Download" && backendRes.title != "Media Download") backendRes.title else (fastMeta?.title ?: "Media Download")
            val finalThumb = if (backendRes.thumbnailUrl.isNotEmpty()) backendRes.thumbnailUrl else (fastMeta?.thumbnailUrl ?: "")

            val qualities = backendRes.qualities.toMutableList()
            if (finalThumb.isNotEmpty() && qualities.none { it.label.contains("Thumbnail") || it.label.contains("Cover") }) {
                qualities.add(MediaQuality("Thumbnail / Cover (JPG)", null, finalThumb))
            }

            return@coroutineScope DownloadResult(
                success = true,
                title = finalTitle,
                thumbnailUrl = finalThumb,
                qualities = qualities.distinctBy { it.label + it.url }
            )
        }

        if (fastMeta != null && fastMeta.title.isNotEmpty()) {
            val fallbackQualities = mutableListOf<MediaQuality>()
            if (fastMeta.streamUrl != null && fastMeta.streamUrl.isNotEmpty()) {
                fallbackQualities.add(MediaQuality("Direct Media Stream", null, fastMeta.streamUrl))
            }
            if (fastMeta.thumbnailUrl.isNotEmpty()) {
                fallbackQualities.add(MediaQuality("High-Res Photo / Cover (JPG)", null, fastMeta.thumbnailUrl))
            }

            if (fallbackQualities.isNotEmpty()) {
                return@coroutineScope DownloadResult(
                    success = true,
                    title = fastMeta.title,
                    thumbnailUrl = fastMeta.thumbnailUrl,
                    qualities = fallbackQualities
                )
            }
        }

        if (backendRes != null && backendRes.error != null) {
            return@coroutineScope DownloadResult(false, "", "", emptyList(), backendRes.error)
        }

        DownloadResult(false, "", "", emptyList(), "Unable to extract media. Please check the URL and try again.")
    }
}

'''

    code = before + replacement + after
    with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
        f.write(code)
    print("SUCCESS update_extraction")
else:
    print("FAILED markers not found")

