import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

# Fix the media array processing first
pattern_media = r'if \(qLabel\.equals\("image", ignoreCase = true\) \|\| qLabel\.equals\("video", ignoreCase = true\)\) \{\s*if \(qLabel\.equals\("video", ignoreCase = true\) \|\| qUrl\.contains\("\.mp4", ignoreCase = true\) \|\| url\.contains\("/reel/", ignoreCase = true\) \|\| url\.contains\("/video/", ignoreCase = true\)\) \{\s*qLabel = "Video \(MP4\)"\s*\} else if \(qUrl\.contains\("\.jpg", ignoreCase = true\) \|\| qUrl\.contains\("\.png", ignoreCase = true\)\) \{\s*qLabel = "Image \(JPG\)"\s*\} else \{\s*qLabel = if \(rootFilename\.endsWith\("\.mp4", ignoreCase = true\)\) "Video \(MP4\)" else "Image \(JPG\)"\s*\}\s*\}'

replacement_media = """if (qLabel.equals("image", ignoreCase = true) || qLabel.equals("video", ignoreCase = true) || qLabel == "Download") {
                        if (qLabel.equals("video", ignoreCase = true) || qUrl.contains(".mp4", ignoreCase = true) || url.contains("/reel/", ignoreCase = true) || url.contains("/video/", ignoreCase = true)) {
                            qLabel = "Video (MP4)"
                        } else if (qUrl.contains(".jpg", ignoreCase = true) || qUrl.contains(".png", ignoreCase = true)) {
                            qLabel = "Image (JPG)"
                        } else {
                            // If API returned "image" but root filename is mp4 and URLs match
                            if (qLabel.equals("image", ignoreCase = true) && rootFilename.endsWith(".mp4", ignoreCase = true) && qUrl == rootUrl) {
                                qLabel = "Video (MP4)"
                            } else {
                                qLabel = if (qLabel.equals("image", ignoreCase = true)) "Image (JPG)" else if (rootFilename.endsWith(".mp4", ignoreCase = true)) "Video (MP4)" else "Image (JPG)"
                            }
                        }
                    }"""

# Fix the rootUrl processing to handle duplicate overriding
pattern_root = r'val rootUrl = json\.optString\("url", json\.optString\("streamUrl", json\.optString\("downloadUrl", ""\)\)\)\s*if \(rootUrl\.isNotEmpty\(\)\) \{\s*var fullRootUrl = rootUrl\s*if \(fullRootUrl\.startsWith\("/"\)\) fullRootUrl = baseApiUrl \+ fullRootUrl\s*if \(qs\.none \{ it\.url == fullRootUrl \}\) \{\s*val qualityLabel = if \(json\.has\("quality"\)\) "Download \$\{json\.optString\("quality"\)\}" else "Download High Quality"\s*qs\.add\(0, MediaQuality\(qualityLabel, null, fullRootUrl\)\)\s*\}\s*\}'

replacement_root = """val rootUrl = json.optString("url", json.optString("streamUrl", json.optString("downloadUrl", "")))
            if (rootUrl.isNotEmpty()) {
                var fullRootUrl = rootUrl
                if (fullRootUrl.startsWith("/")) fullRootUrl = baseApiUrl + fullRootUrl
                
                var qualityLabel = if (json.has("quality")) "Download ${json.optString("quality")}" else "Download High Quality"
                if (rootFilename.endsWith(".mp4", ignoreCase = true) || fullRootUrl.contains(".mp4", ignoreCase = true)) {
                    qualityLabel = "Video (MP4)"
                }
                
                val existingItem = qs.find { it.url == fullRootUrl }
                if (existingItem == null) {
                    qs.add(0, MediaQuality(qualityLabel, null, fullRootUrl))
                } else {
                    // Update label if it was incorrectly marked as Image
                    if (qualityLabel == "Video (MP4)" && existingItem.label.contains("Image")) {
                        val idx = qs.indexOf(existingItem)
                        qs[idx] = existingItem.copy(label = "Video (MP4)")
                    }
                }
            }"""

content = re.sub(pattern_media, replacement_media, content)
content = re.sub(pattern_root, replacement_root, content)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
