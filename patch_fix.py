import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

pattern = """                    var qLabel = item.optString("label", item.optString("resolution", item.optString("type", "Download")))
                    if (qLabel.equals("image", ignoreCase = true) && qUrl.contains(".mp4", ignoreCase = true)) {
                        qLabel = "Video (MP4)"
                    } else if (qLabel.equals("video", ignoreCase = true)) {
                        qLabel = "Video (MP4)"
                    } else if (qLabel.equals("image", ignoreCase = true) && (qUrl.contains(".jpg", ignoreCase = true) || qUrl.contains(".png", ignoreCase = true) || qUrl.contains("thumb", ignoreCase = true) || qUrl.contains("image", ignoreCase = true))) {
                        qLabel = "Image (JPG)"
                    } else if (qLabel.equals("image", ignoreCase = true) && item.optString("mediaType", "").equals("video", ignoreCase = true)) {
                        qLabel = "Video (MP4)"
                    } else if (qLabel.equals("image", ignoreCase = true)) {
                        qLabel = "Video (MP4)" // Default to video if API returns image but it might be video in IG
                    }
                    var qUrl = item.optString("url", item.optString("src", ""))
                    if (qUrl.startsWith("/")) qUrl = baseApiUrl + qUrl"""

replacement = """                    var qUrl = item.optString("url", item.optString("src", ""))
                    if (qUrl.startsWith("/")) qUrl = baseApiUrl + qUrl
                    var qLabel = item.optString("label", item.optString("resolution", item.optString("type", "Download")))
                    if (qLabel.equals("image", ignoreCase = true) && qUrl.contains(".mp4", ignoreCase = true)) {
                        qLabel = "Video (MP4)"
                    } else if (qLabel.equals("video", ignoreCase = true)) {
                        qLabel = "Video (MP4)"
                    } else if (qLabel.equals("image", ignoreCase = true) && (qUrl.contains(".jpg", ignoreCase = true) || qUrl.contains(".png", ignoreCase = true) || qUrl.contains("thumb", ignoreCase = true) || qUrl.contains("image", ignoreCase = true))) {
                        qLabel = "Image (JPG)"
                    } else if (qLabel.equals("image", ignoreCase = true) && item.optString("mediaType", "").equals("video", ignoreCase = true)) {
                        qLabel = "Video (MP4)"
                    } else if (qLabel.equals("image", ignoreCase = true)) {
                        qLabel = "Video (MP4)"
                    }"""

content = content.replace(pattern, replacement)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
