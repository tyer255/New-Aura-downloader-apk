with open('app/src/main/java/com/example/MainActivity.kt', 'r') as f:
    content = f.read()

target = '''    } else if (url.contains("instagram.com") || url.contains("tiktok.com")) {
        val title = if (url.contains("instagram")) "Instagram Video" else "TikTok Video"
        val baseApiUrl = backendUrl.replace("/api/download", "")
        val encodedUrl = java.net.URLEncoder.encode(url, "UTF-8")
        val qs = listOf(
            MediaQuality("Download (MP4)", null, "$baseApiUrl/api/proxy-download?url=$encodedUrl")
        )
        kotlinx.coroutines.delay(4500)
        return@withContext DownloadResult(true, title, "", qs)
    }'''

new_content = content.replace(target, "    }")

with open('app/src/main/java/com/example/MainActivity.kt', 'w') as f:
    f.write(new_content)
