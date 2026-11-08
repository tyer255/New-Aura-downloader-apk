import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

pattern = r'if \(qLabel\.equals\("video", ignoreCase = true\) \|\| qUrl\.contains\("\.mp4", ignoreCase = true\) \|\| rootFilename\.endsWith\("\.mp4", ignoreCase = true\)\) \{\s*qLabel = "Video \(MP4\)"\s*\} else if \(qUrl\.contains\("\.jpg", ignoreCase = true\) \|\| qUrl\.contains\("\.png", ignoreCase = true\) \|\| rootFilename\.endsWith\("\.jpg", ignoreCase = true\) \|\| rootFilename\.endsWith\("\.png", ignoreCase = true\)\) \{\s*qLabel = "Image \(JPG\)"\s*\} else \{\s*qLabel = if \(rootFilename\.endsWith\("\.mp4", ignoreCase = true\)\) "Video \(MP4\)" else "Image \(JPG\)"\s*\}'

replacement = """if (qLabel.equals("video", ignoreCase = true) || qUrl.contains(".mp4", ignoreCase = true)) {
                            qLabel = "Video (MP4)"
                        } else if (qUrl.contains(".jpg", ignoreCase = true) || qUrl.contains(".png", ignoreCase = true)) {
                            qLabel = "Image (JPG)"
                        } else {
                            qLabel = if (rootFilename.endsWith(".mp4", ignoreCase = true)) "Video (MP4)" else "Image (JPG)"
                        }"""

content = re.sub(pattern, replacement, content)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
