import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

pattern = r'val success = json\.optBoolean\("success", true\)\s*val title = json\.optString\("title", json\.optString\("filename", "Media Download"\)\)\s*val thumbnail = json\.optString\("thumbnail", json\.optString\("cover", json\.optString\("image", ""\)\)\)\s*val qs = mutableListOf<MediaQuality>\(\)'

replacement = """val success = json.optBoolean("success", true)
            val title = json.optString("title", json.optString("filename", "Media Download"))
            val thumbnail = json.optString("thumbnail", json.optString("cover", json.optString("image", "")))
            val rootFilename = json.optString("filename", "")
            val qs = mutableListOf<MediaQuality>()"""

content = re.sub(pattern, replacement, content)

pattern2 = r'var qLabel = item\.optString\("label", item\.optString\("resolution", item\.optString\("type", "Download"\)\)\)\s*if \(qLabel\.equals\("image", ignoreCase = true\) && qUrl\.contains\("\.mp4", ignoreCase = true\)\) \{\s*qLabel = "Video \(MP4\)"\s*\} else if \(qLabel\.equals\("video", ignoreCase = true\)\) \{\s*qLabel = "Video \(MP4\)"\s*\} else if \(qLabel\.equals\("image", ignoreCase = true\) && \(qUrl\.contains\("\.jpg", ignoreCase = true\) \|\| qUrl\.contains\("\.png", ignoreCase = true\) \|\| qUrl\.contains\("thumb", ignoreCase = true\) \|\| qUrl\.contains\("image", ignoreCase = true\)\)\) \{\s*qLabel = "Image \(JPG\)"\s*\} else if \(qLabel\.equals\("image", ignoreCase = true\) && item\.optString\("mediaType", ""\)\.equals\("video", ignoreCase = true\)\) \{\s*qLabel = "Video \(MP4\)"\s*\} else if \(qLabel\.equals\("image", ignoreCase = true\)\) \{\s*qLabel = "Video \(MP4\)"\s*\}'

replacement2 = """var qLabel = item.optString("label", item.optString("resolution", item.optString("type", "Download")))
                    if (qLabel.equals("image", ignoreCase = true) || qLabel.equals("video", ignoreCase = true)) {
                        if (qLabel.equals("video", ignoreCase = true) || qUrl.contains(".mp4", ignoreCase = true) || rootFilename.endsWith(".mp4", ignoreCase = true)) {
                            qLabel = "Video (MP4)"
                        } else if (qUrl.contains(".jpg", ignoreCase = true) || qUrl.contains(".png", ignoreCase = true) || rootFilename.endsWith(".jpg", ignoreCase = true) || rootFilename.endsWith(".png", ignoreCase = true)) {
                            qLabel = "Image (JPG)"
                        } else {
                            qLabel = if (rootFilename.endsWith(".mp4", ignoreCase = true)) "Video (MP4)" else "Image (JPG)"
                        }
                    }"""

content = re.sub(pattern2, replacement2, content)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
