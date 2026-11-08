import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

target = """            val request = android.app.DownloadManager.Request(downloadUri).apply {
                setTitle(title)
                setDescription("Downloading $title")
                setNotificationVisibility(android.app.DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                setDestinationInExternalPublicDir(android.os.Environment.DIRECTORY_DOWNLOADS, fileName)
                setAllowedOverMetered(true)
                setAllowedOverRoaming(true)
            }"""

replacement = """            val mimeType = when (extension) {
                "mp4" -> "video/mp4"
                "webm" -> "video/webm"
                "mp3" -> "audio/mpeg"
                "m4a" -> "audio/mp4"
                "jpg", "jpeg" -> "image/jpeg"
                "png" -> "image/png"
                "webp" -> "image/webp"
                "gif" -> "image/gif"
                else -> "*/*"
            }
            
            val request = android.app.DownloadManager.Request(downloadUri).apply {
                setTitle(title)
                setDescription("Downloading $title")
                setMimeType(mimeType)
                setNotificationVisibility(android.app.DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                setDestinationInExternalPublicDir(android.os.Environment.DIRECTORY_DOWNLOADS, fileName)
                setAllowedOverMetered(true)
                setAllowedOverRoaming(true)
            }"""

content = content.replace(target, replacement)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
