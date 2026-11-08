import re

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    code = f.read()

# 1. Add URLEncoder import
if 'import java.net.URLEncoder' not in code:
    code = code.replace('package com.auradownloader.app\n', 'package com.auradownloader.app\nimport java.net.URLEncoder\n')

# 2. Add SpotifyTrack & update DownloadResult
old_dr = """data class DownloadResult(
    val success: Boolean,
    val title: String,
    val thumbnailUrl: String,
    val qualities: List<MediaQuality>,
    val error: String? = null,
    val isSpotify: Boolean = false,
    val previewAudioUrl: String? = null,
    val artistName: String? = null
)"""

new_dr = """data class SpotifyTrack(
    val name: String,
    val artist: String = "",
    val durationStr: String? = null,
    val trackNumber: Int = 1
)

data class DownloadResult(
    val success: Boolean,
    val title: String,
    val thumbnailUrl: String,
    val qualities: List<MediaQuality>,
    val error: String? = null,
    val isSpotify: Boolean = false,
    val isPlaylist: Boolean = false,
    val previewAudioUrl: String? = null,
    val artistName: String? = null,
    val spotifyTracks: List<SpotifyTrack> = emptyList()
)"""

code = code.replace(old_dr, new_dr)

# 3. Add handleSpotifyExtraction function
spotify_fn = """
suspend fun handleSpotifyExtraction(url: String): DownloadResult {
    val lowerUrl = url.lowercase()
    val spotifyRegex = "(?:spotify\\\\.com\\\\/(?:[a-zA-Z0-9-]+\\\\/" + ")?|spotify:)(track|playlist|album|artist)[:\\\\/]([a-zA-Z0-9]{22})".toRegex()
    val match = spotifyRegex.find(url)
    val kind = match?.groupValues?.get(1)?.lowercase() ?: if (lowerUrl.contains("/playlist")) "playlist" else if (lowerUrl.contains("/album")) "album" else "track"
    val itemId = match?.groupValues?.get(2)

    var trackTitle = "Spotify Music"
    var artistName = ""
    var thumbnailUrl = ""
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
            val nextDataRegex = "<script id=\\"__NEXT_DATA__\\" type=\\"application/json\\">(.*?)</script>".toRegex(RegexOption.DOT_MATCHES_ALL)
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
                val visualIdentityRegex = "\\"coverArt\\":\\\\{\\"sources\\":\\\\[\\\\{\\"url\\":\\"([^\\"]+)\\"".toRegex()
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

    val displayTitle = if (artistName.isNotEmpty() && !trackTitle.contains(artistName)) "$trackTitle - $artistName" else trackTitle

    return DownloadResult(
        success = true,
        title = displayTitle,
        thumbnailUrl = thumbnailUrl,
        qualities = qualities,
        isSpotify = true,
        isPlaylist = isPlaylist,
        artistName = artistName,
        spotifyTracks = spotifyTracks
    )
}
"""

# Replace SPOTIFY LINK HANDLING block in extractWithCobalt
spotify_block_regex = r'// SPOTIFY LINK HANDLING.*?return@withContext DownloadResult\(\s*success = true,.*?\)'
replacement_block = """// SPOTIFY LINK HANDLING
    if (lowerUrl.contains("spotify.com") || lowerUrl.contains("spotify:")) {
        return@withContext handleSpotifyExtraction(url)
    }"""

code = re.sub(spotify_block_regex, replacement_block, code, flags=re.DOTALL)

# Insert handleSpotifyExtraction right before extractWithCobalt
code = code.replace("suspend fun extractWithCobalt", spotify_fn + "\nsuspend fun extractWithCobalt")

# Update guessExtension and mimeType in resolveAndTriggerDownload
code = code.replace('lowerLabel.contains("mp3")', 'lowerLabel.contains("zip") || lowerUrl.contains(".zip") || lowerUrl.contains("format=zip") -> "zip"\n        lowerLabel.contains("mp3")')
code = code.replace('"mp4" -> "video/mp4"', '"zip" -> "application/zip"\n                "mp4" -> "video/mp4"')

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(code)

print("Spotify logic updated successfully!")
