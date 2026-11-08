with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    code = f.read()

import re

# Add CarouselItem data class
if 'data class CarouselItem' not in code:
    code = code.replace('data class DownloadResult(', '''data class CarouselItem(
    val url: String,
    val type: String,
    val thumbnail: String? = null
)

data class DownloadResult(''')

# Update DownloadResult
old_dr = """data class DownloadResult(
    val success: Boolean,
    val title: String,
    val thumbnailUrl: String,
    val qualities: List<MediaQuality>,
    val error: String? = null,
    val isSpotify: Boolean = false,
    val isPlaylist: Boolean = false,
    val previewAudioUrl: String? = null,
    val artistName: String? = null,
    val spotifyTracks: List<SpotifyTrack> = emptyList()
)"""

new_dr = """data class DownloadResult(
    val success: Boolean,
    val title: String,
    val thumbnailUrl: String,
    val qualities: List<MediaQuality>,
    val error: String? = null,
    val isSpotify: Boolean = false,
    val isPlaylist: Boolean = false,
    val previewAudioUrl: String? = null,
    val artistName: String? = null,
    val spotifyTracks: List<SpotifyTrack> = emptyList(),
    val mediaType: String = "",
    val carouselItems: List<CarouselItem> = emptyList()
)"""

if old_dr in code:
    code = code.replace(old_dr, new_dr)
    print("Updated DownloadResult")
else:
    print("DownloadResult not found")

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(code)
