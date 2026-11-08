import re

with open('app/src/main/java/com/example/MainActivity.kt', 'r') as f:
    content = f.read()

target1 = '''            kotlinx.coroutines.delay(4500)
            return@withContext DownloadResult(true, title, thumbnail, qs)'''
replace1 = '''            val finalQs = qs.toMutableList()
            if (thumbnail.isNotEmpty()) {
                finalQs.add(MediaQuality("Thumbnail (JPG)", null, thumbnail))
            }
            kotlinx.coroutines.delay(4500)
            return@withContext DownloadResult(true, title, thumbnail, finalQs)'''

target2 = '''                if (arr != null) {
                    for (i in 0 until arr.length()) {
                        val item = arr.getJSONObject(i)
                        val qLabel = item.optString("label", item.optString("resolution", "Download"))
                        var qUrl = item.optString("url")
                        if (qUrl.startsWith("/")) qUrl = backendUrl.replace("/api/download", "") + qUrl
                        val qSize = item.optString("size", "")
                        qs.add(MediaQuality(qLabel, if(qSize.isEmpty() || qSize == "Unknown Size") null else qSize, qUrl))
                    }
                }
                if (qs.isNotEmpty() || arr != null) {
                    return@withContext DownloadResult(true, title, thumbnail, qs)
                }'''
replace2 = '''                if (arr != null) {
                    for (i in 0 until arr.length()) {
                        val item = arr.getJSONObject(i)
                        val qLabel = item.optString("label", item.optString("resolution", "Download"))
                        var qUrl = item.optString("url")
                        if (qUrl.startsWith("/")) qUrl = backendUrl.replace("/api/download", "") + qUrl
                        val qSize = item.optString("size", "")
                        
                        // For audio/MP3, don't show the size if it seems incorrectly large
                        val isAudio = qLabel.contains("audio", true) || qLabel.contains("mp3", true)
                        val finalSize = if (qSize.isEmpty() || qSize == "Unknown Size") null else if (isAudio) null else qSize
                        
                        qs.add(MediaQuality(qLabel, finalSize, qUrl))
                    }
                }
                
                // Filter out exact duplicates by URL or label if they have same sizes, or just show highest quality for Instagram
                var finalQs = qs.distinctBy { it.label + it.url }.toMutableList()
                
                // If Instagram, just show one video file (HD) and audio
                if (url.contains("instagram.com") || url.contains("tiktok.com")) {
                    val videoQs = finalQs.filter { !it.label.contains("audio", true) && !it.label.contains("mp3", true) }
                    val audioQs = finalQs.filter { it.label.contains("audio", true) || it.label.contains("mp3", true) }
                    
                    finalQs.clear()
                    if (videoQs.isNotEmpty()) {
                        // Take the best or first video
                        finalQs.add(videoQs.first().copy(label = "Download HD (MP4)"))
                    }
                    finalQs.addAll(audioQs)
                }
                
                if (thumbnail.isNotEmpty()) {
                    finalQs.add(MediaQuality("Thumbnail (JPG)", null, thumbnail))
                }
                
                if (finalQs.isNotEmpty() || arr != null) {
                    return@withContext DownloadResult(true, title, thumbnail, finalQs)
                }'''

content = content.replace(target1, replace1).replace(target2, replace2)

with open('app/src/main/java/com/example/MainActivity.kt', 'w') as f:
    f.write(content)
