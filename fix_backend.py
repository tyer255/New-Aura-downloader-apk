import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

# Update fetchBackendApi return DownloadResult
old_dr_ret = """return DownloadResult(true, title, thumbnail, finalQs)"""
new_dr_ret = """val lyrics = json.optString("lyrics", "").takeIf { it.isNotEmpty() }
                val syncedLyrics = json.optString("syncedLyrics", "").takeIf { it.isNotEmpty() }
                return DownloadResult(true, title, thumbnail, finalQs, lyrics = lyrics, syncedLyrics = syncedLyrics)"""
content = content.replace(old_dr_ret, new_dr_ret)

# Update extractWithCobalt (Spotify section)
old_extract = """                    DownloadResult(
                        success = true,
                        title = displayTitle,
                        thumbnailUrl = thumbnailUrl,
                        qualities = qualities,
                        isSpotify = true,
                        previewAudioUrl = finalPreviewAudio,
                        artistName = artistName
                    )"""
new_extract = """                    DownloadResult(
                        success = true,
                        title = displayTitle,
                        thumbnailUrl = thumbnailUrl,
                        qualities = qualities,
                        isSpotify = true,
                        previewAudioUrl = finalPreviewAudio,
                        artistName = artistName,
                        lyrics = backendResult?.lyrics,
                        syncedLyrics = backendResult?.syncedLyrics
                    )"""
content = content.replace(old_extract, new_extract)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
