import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

pattern = r'if \(qLabel\.equals\("image", ignoreCase = true\) \|\| qLabel\.equals\("video", ignoreCase = true\)\) \{\s*if \(qLabel\.equals\("video", ignoreCase = true\) \|\| qUrl\.contains\("\.mp4", ignoreCase = true\)\) \{\s*qLabel = "Video \(MP4\)"\s*\} else if \(qUrl\.contains\("\.jpg", ignoreCase = true\) \|\| qUrl\.contains\("\.png", ignoreCase = true\)\) \{\s*qLabel = "Image \(JPG\)"\s*\} else \{\s*qLabel = if \(rootFilename\.endsWith\("\.mp4", ignoreCase = true\)\) "Video \(MP4\)" else "Image \(JPG\)"\s*\}\s*\}'

replacement = """if (qLabel.equals("image", ignoreCase = true) || qLabel.equals("video", ignoreCase = true)) {
                        if (qLabel.equals("video", ignoreCase = true) || qUrl.contains(".mp4", ignoreCase = true) || url.contains("/reel/", ignoreCase = true) || url.contains("/video/", ignoreCase = true)) {
                            qLabel = "Video (MP4)"
                        } else if (qUrl.contains(".jpg", ignoreCase = true) || qUrl.contains(".png", ignoreCase = true)) {
                            qLabel = "Image (JPG)"
                        } else {
                            qLabel = if (rootFilename.endsWith(".mp4", ignoreCase = true)) "Video (MP4)" else "Image (JPG)"
                        }
                    }"""

content = re.sub(pattern, replacement, content)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
