awk '
BEGIN { skipping = 0 }
/val qualities = mutableListOf<MediaQuality>\(\)/ { skipping = 1 }
/val finalPreviewAudio = fullAudioUrl \?: previewUrl/ {
    print "                    val displayTitle = if (artistName.isNotEmpty() && !trackTitle.contains(artistName)) \"$trackTitle - $artistName\" else trackTitle"
    print "                    var youtubeAudioUrl: String? = null"
    print "                    try {"
    print "                        val query = java.net.URLEncoder.encode(displayTitle, \"UTF-8\")"
    print "                        val ytSearchReq = Request.Builder()"
    print "                            .url(\"https://www.youtube.com/results?search_query=$query\")"
    print "                            .addHeader(\"User-Agent\", \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\")"
    print "                            .build()"
    print "                        val ytRes = okHttpClient.newCall(ytSearchReq).execute()"
    print "                        if (ytRes.isSuccessful) {"
    print "                            val ytHtml = ytRes.body?.string() ?: \"\""
    print "                            val ytMatch = Regex(\"\\\"videoId\\\":\\\"([a-zA-Z0-9_-]{11})\\\"\").find(ytHtml)"
    print "                            val videoId = ytMatch?.groupValues?.getOrNull(1)"
    print "                            if (videoId != null) {"
    print "                                youtubeAudioUrl = BuildConfig.BACKEND_URL.replace(\"/api/download\", \"\") + \"/api/get-youtube-link?url=https://youtube.com/watch?v=$videoId&quality=audio\""
    print "                            }"
    print "                        }"
    print "                    } catch (e: Exception) {"
    print "                        e.printStackTrace()"
    print "                    }"
    print ""
    print "                    val qualities = mutableListOf<MediaQuality>()"
    print "                    if (youtubeAudioUrl != null) {"
    print "                        qualities.add(MediaQuality(\"Full Track (MP3)\", null, youtubeAudioUrl))"
    print "                    }"
    print "                    if (backendResult != null && backendResult.qualities.isNotEmpty()) {"
    print "                        qualities.addAll(backendResult.qualities)"
    print "                    }"
    print "                    if (previewUrl.isNotEmpty()) {"
    print "                        qualities.add(MediaQuality(\"Preview Track (30s MP3)\", null, previewUrl))"
    print "                    }"
    print "                    if (thumbnailUrl.isNotEmpty() && qualities.none { it.label.contains(\"Art\") }) {"
    print "                        qualities.add(MediaQuality(\"Album Cover Art (JPG)\", null, thumbnailUrl))"
    print "                    }"
    print "                    val fullAudioUrl = youtubeAudioUrl ?: qualities.firstOrNull { it.url.contains(\"spotify-resolve\") || it.label.contains(\"MP3\") || it.label.contains(\"Audio\") }?.url"
    print "                    val finalPreviewAudio = fullAudioUrl ?: previewUrl"
    skipping = 0
    next
}
{
    if (skipping == 0) print $0
}
' app/src/main/java/com/auradownloader/app/MainActivity.kt > tmp.kt && mv tmp.kt app/src/main/java/com/auradownloader/app/MainActivity.kt
