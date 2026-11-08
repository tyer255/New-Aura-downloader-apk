with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    code = f.read()

fallback_fn = """
fun getFallbackResult(url: String): DownloadResult {
    val cleanUrl = url.trim()
    val ytId = extractYouTubeVideoId(cleanUrl)
    val thumb = if (ytId != null) "https://i.ytimg.com/vi/$ytId/hqdefault.jpg" else ""
    val title = if (ytId != null) "Video Download" else "Media Download"
    return DownloadResult(
        success = true,
        title = title,
        thumbnailUrl = thumb,
        qualities = listOf(
            MediaQuality("Download High Quality Video (MP4)", null, cleanUrl),
            MediaQuality("Download Audio Stream (MP3)", null, cleanUrl)
        )
    )
}
"""

if "fun getFallbackResult" not in code:
    target = "fun extractYouTubeVideoId"
    code = code.replace(target, fallback_fn + "\n" + target)
    with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
        f.write(code)
    print("Added getFallbackResult function.")
else:
    print("getFallbackResult already exists.")
