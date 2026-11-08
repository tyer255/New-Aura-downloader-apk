import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

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
    val spotifyTracks: List<SpotifyTrack> = emptyList(),
    val mediaType: String = "",
    val carouselItems: List<CarouselItem> = emptyList()
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
    val carouselItems: List<CarouselItem> = emptyList(),
    val lyrics: String? = null,
    val syncedLyrics: String? = null
)"""
content = content.replace(old_dr, new_dr)

# Update SpotifyTrack
old_st = """data class SpotifyTrack(
    val name: String,
    val artist: String = "",
    val durationStr: String? = null,
    val trackNumber: Int = 1,
    val resolveUrl: String? = null,
    val directAudioUrl: String? = null,
    val thumbnailUrl: String? = null
)"""
new_st = """data class SpotifyTrack(
    val name: String,
    val artist: String = "",
    val durationStr: String? = null,
    val trackNumber: Int = 1,
    val resolveUrl: String? = null,
    val directAudioUrl: String? = null,
    val thumbnailUrl: String? = null,
    val lyrics: String? = null,
    val syncedLyrics: String? = null
)"""
content = content.replace(old_st, new_st)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
