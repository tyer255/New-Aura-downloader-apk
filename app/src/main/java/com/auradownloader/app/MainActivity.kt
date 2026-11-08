package com.auradownloader.app
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.compose.ui.zIndex
import java.net.URLEncoder

import android.media.MediaPlayer

import android.Manifest

import android.content.Context

import android.content.Intent

import android.content.pm.PackageManager

import android.net.Uri

import android.os.Build

import android.os.Bundle

import android.widget.Toast

import androidx.activity.ComponentActivity

import androidx.activity.compose.rememberLauncherForActivityResult

import androidx.activity.compose.setContent

import androidx.activity.enableEdgeToEdge

import androidx.activity.result.contract.ActivityResultContracts

import androidx.core.content.ContextCompat

import androidx.compose.animation.AnimatedContentTransitionScope

import androidx.compose.animation.
*

import androidx.compose.animation.core.
*

import androidx.compose.ui.geometry.
*

import androidx.compose.foundation.Canvas

import androidx.compose.animation.core.tween

import androidx.compose.foundation.Image

import androidx.compose.foundation.background

import androidx.compose.foundation.border

import androidx.compose.foundation.clickable

import androidx.compose.foundation.layout.
*

import androidx.compose.foundation.lazy.LazyRow

import androidx.compose.foundation.lazy.grid.GridCells

import androidx.compose.foundation.lazy.grid.LazyVerticalGrid

import androidx.compose.foundation.lazy.grid.items

import androidx.compose.foundation.lazy.items

import androidx.compose.foundation.rememberScrollState

import androidx.compose.foundation.shape.CircleShape

import androidx.compose.foundation.shape.RoundedCornerShape

import androidx.compose.foundation.text.BasicTextField

import androidx.compose.foundation.verticalScroll

import androidx.compose.material.icons.Icons

import androidx.compose.material.icons.filled.
*

import androidx.compose.material3.
*

import androidx.compose.runtime.
*

import androidx.compose.ui.Alignment

import androidx.compose.ui.Modifier

import androidx.compose.ui.draw.clip

import androidx.compose.ui.draw.drawWithContent
import androidx.compose.ui.draw.shadow

import androidx.compose.ui.graphics.Brush

import androidx.compose.ui.graphics.Color

import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.text.TextStyle
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState


import androidx.compose.ui.graphics.vector.ImageVector

import androidx.compose.ui.layout.ContentScale

import androidx.compose.ui.platform.LocalClipboardManager

import androidx.compose.ui.platform.LocalContext

import androidx.compose.ui.res.painterResource

import androidx.compose.ui.text.SpanStyle

import androidx.compose.ui.text.buildAnnotatedString

import androidx.compose.ui.text.font.FontWeight

import androidx.compose.ui.text.style.TextAlign

import androidx.compose.ui.text.style.TextOverflow

import androidx.compose.ui.text.withStyle

import androidx.compose.ui.unit.dp

import androidx.compose.ui.unit.sp

import androidx.navigation.NavDestination.Companion.hierarchy

import androidx.navigation.NavGraph.Companion.findStartDestination

import androidx.navigation.compose.
*

import coil.compose.AsyncImage
import coil.imageLoader

import com.auradownloader.app.ui.theme.MyApplicationTheme


import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.CoroutineScope
import okhttp3.Call
import okhttp3.Callback
import okhttp3.ConnectionPool
import okhttp3.Response
import java.io.IOException
import java.util.concurrent.TimeUnit

import kotlinx.coroutines.Dispatchers

import kotlinx.coroutines.delay

import kotlinx.coroutines.launch

import kotlinx.coroutines.withContext

import okhttp3.MediaType.Companion.toMediaType

import okhttp3.OkHttpClient

import okhttp3.Request

import okhttp3.RequestBody.Companion.toRequestBody

import org.json.JSONObject
import android.content.BroadcastReceiver
import android.content.IntentFilter
import com.airbnb.lottie.compose.*

data class MediaQuality(
    val label: String,
    val size: String? = null,
    val url: String = ""
)

data class SpotifyTrack(
    val name: String,
    val artist: String = "",
    val durationStr: String? = null,
    val trackNumber: Int = 1,
    val resolveUrl: String? = null,
    val directAudioUrl: String? = null,
    val thumbnailUrl: String? = null
)

data class CarouselItem(
    val url: String,
    val type: String,
    val thumbnail: String? = null
)

data class DownloadResult(
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
    val lyrics: String? = null
)


object ApiSecurity {
    const val API_KEY = "AURA-ANDROID-LIVE-2026-v2-KEY_auradownloader_ai_studio"

    fun getBaseUrl(): String = "https://auradownloader.ai.studio"
    fun getDownloadUrl(): String = getBaseUrl() + "/api/download"
    fun getLyricsUrl(): String = getBaseUrl() + "/api/lyrics"
    fun getProxyUrl(): String = getBaseUrl() + "/api/proxy-download"
    fun getHealthUrl(): String = getBaseUrl() + "/api/health"
}

enum class Platform(
    val displayName: String,
    val brandColor: Color,
    val startColorDark: Color,
    val endColorDark: Color,
    val startColorLight: Color,
    val endColorLight: Color,
    val iconResId: Int
) {
    YOUTUBE("YouTube", Color(0xFFFF0000), Color(0xFF8B3A3A), Color(0xFF4A1F1F), Color(0xFFFEE2E2), Color(0xFFFFF1F2), R.drawable.ic_youtube),
    INSTAGRAM("Instagram", Color(0xFFE4405F), Color(0xFF833A6B), Color(0xFF481F3B), Color(0xFFFCE7F3), Color(0xFFFDF2F8), R.drawable.ic_instagram),
    SPOTIFY("Spotify", Color(0xFF1DB954), Color(0xFF0E5C2A), Color(0xFF083317), Color(0xFFE2FEEA), Color(0xFFF1FFF5), R.drawable.ic_spotify),
    SNAPCHAT("Snapchat", Color(0xFFFFFC00), Color(0xFF8A8800), Color(0xFF4D4C00), Color(0xFFFEFDE2), Color(0xFFFFFDF1), R.drawable.ic_snapchat),
    THREADS("Threads", Color(0xFF000000), Color(0xFF2A2A2A), Color(0xFF151515), Color(0xFFF3F4F6), Color(0xFFF9FAFB), R.drawable.ic_threads),
    PINTEREST("Pinterest", Color(0xFFBD081C), Color(0xFF6E0812), Color(0xFF3D040A), Color(0xFFFFE4E6), Color(0xFFFFF1F2), R.drawable.ic_pinterest),
    X("X (Twitter)", Color(0xFF000000), Color(0xFF2A2A2A), Color(0xFF151515), Color(0xFFF3F4F6), Color(0xFFF9FAFB), R.drawable.ic_x),
    LINKEDIN("LinkedIn", Color(0xFF0077B5), Color(0xFF00446B), Color(0xFF00273D), Color(0xFFE0F2FE), Color(0xFFF0F9FF), R.drawable.ic_linkedin),
    TIKTOK("TikTok", Color(0xFF000000), Color(0xFF2A2A2A), Color(0xFF151515), Color(0xFFF1F5F9), Color(0xFFF8FAFC), R.drawable.ic_tiktok),
    FACEBOOK("Facebook", Color(0xFF1877F2), Color(0xFF1A498A), Color(0xFF0F2B52), Color(0xFFDBEAFE), Color(0xFFEFF6FF), R.drawable.ic_facebook),
    REDDIT("Reddit", Color(0xFFFF4500), Color(0xFF8A2E00), Color(0xFF4D1A00), Color(0xFFFFEDD5), Color(0xFFFFF7ED), R.drawable.ic_reddit)
}

sealed class Screen(val route: String, val label: String, val icon: ImageVector) {
    object Home : Screen("home", "Home", Icons.Filled.Home)
    object Platforms : Screen("platforms", "Platforms", Icons.Filled.Apps)
    object Settings : Screen("settings", "Settings", Icons.Filled.Settings)
    object PrivacyPolicy : Screen("privacy_policy", "Privacy Policy", Icons.Filled.Policy)
    object Terms : Screen("terms", "Terms and Conditions", Icons.Filled.Description)
    object Feedback : Screen("feedback", "Feedback", Icons.Filled.Feedback)
    object About : Screen("about", "About", Icons.Filled.Info)
    object DMCA : Screen("dmca", "DMCA Policy", Icons.Filled.Gavel)
    object CookiePolicy : Screen("cookie_policy", "Cookie Policy", Icons.Filled.Cookie)
    object FAQ : Screen("faq", "FAQ", Icons.Filled.QuestionAnswer)
    object ContactUs : Screen("contact_us", "Contact Us", Icons.Filled.Email)
}

val okHttpClient = OkHttpClient.Builder()
    .connectTimeout(45, TimeUnit.SECONDS)
    .readTimeout(90, TimeUnit.SECONDS)
    .writeTimeout(45, TimeUnit.SECONDS)
    .connectionPool(ConnectionPool(32, 5, TimeUnit.MINUTES))
    .retryOnConnectionFailure(true)
    .build()

fun warmUpBackend() {
    CoroutineScope(Dispatchers.IO).launch {
        try {
            val req = Request.Builder()
                .url(ApiSecurity.getHealthUrl())
                .addHeader("User-Agent", "AuraDownloaderFast/2.0")
                .addHeader("X-Aura-Api-Key", ApiSecurity.API_KEY)
                .build()
            okHttpClient.newCall(req).enqueue(object : Callback {
                override fun onFailure(call: Call, e: IOException) {}
                override fun onResponse(call: Call, response: Response) { response.close() }
            })
        } catch (_: Exception) {}
    }
}

fun startMusicServiceSafely(context: Context) {
    try {
        val intent = Intent(context, MusicPlaybackService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            ContextCompat.startForegroundService(context, intent)
        } else {
            context.startService(intent)
        }
    } catch (e: Exception) {
        android.util.Log.e("MusicService", "Error starting music service: ${e.message}")
    }
}

data class FastMeta(val title: String, val thumbnailUrl: String, val streamUrl: String? = null)

fun fetchFastMeta(url: String): FastMeta? {
    val lower = url.lowercase().trim()
    try {
        if (lower.contains("youtube.com") || lower.contains("youtu.be")) {
            val ytRegex = Regex("""(?:youtu\.be/|youtube\.com/(?:embed/|v/|watch\?v=|watch\?.+&v=|shorts/))([a-zA-Z0-9_-]{11})""")
            val videoId = ytRegex.find(url)?.groupValues?.getOrNull(1)
            var thumb = if (videoId != null) "https://i.ytimg.com/vi/$videoId/hqdefault.jpg" else ""
            var title = "YouTube Video"

            val oembedReq = Request.Builder().url("https://www.youtube.com/oembed?url=$url&format=json").build()
            val oembedRes = okHttpClient.newCall(oembedReq).execute()
            if (oembedRes.isSuccessful) {
                val json = JSONObject(oembedRes.body?.string() ?: "")
                title = json.optString("title", title)
                val author = json.optString("author_name", "")
                if (author.isNotEmpty() && !title.contains(author)) {
                    title = "$title - $author"
                }
                val oThumb = json.optString("thumbnail_url", "")
                if (oThumb.isNotEmpty()) thumb = oThumb
            }
            return FastMeta(title, thumb)
        }

        if (lower.contains("tiktok.com")) {
            val oembedReq = Request.Builder().url("https://www.tiktok.com/oembed?url=$url").build()
            val oembedRes = okHttpClient.newCall(oembedReq).execute()
            if (oembedRes.isSuccessful) {
                val json = JSONObject(oembedRes.body?.string() ?: "")
                val title = json.optString("title", "TikTok Video")
                val author = json.optString("author_name", "")
                val displayTitle = if (author.isNotEmpty()) "$title - @$author" else title
                val thumb = json.optString("thumbnail_url", "")
                return FastMeta(displayTitle, thumb)
            }
        }

        if (lower.contains("twitter.com") || lower.contains("x.com")) {
            val oembedReq = Request.Builder().url("https://publish.twitter.com/oembed?url=$url").build()
            val oembedRes = okHttpClient.newCall(oembedReq).execute()
            if (oembedRes.isSuccessful) {
                val json = JSONObject(oembedRes.body?.string() ?: "")
                val author = json.optString("author_name", "X Post")
                return FastMeta("Post by $author", "")
            }
        }

        if (lower.contains("reddit.com")) {
            val oembedReq = Request.Builder().url("https://www.reddit.com/oembed?url=$url").build()
            val oembedRes = okHttpClient.newCall(oembedReq).execute()
            if (oembedRes.isSuccessful) {
                val json = JSONObject(oembedRes.body?.string() ?: "")
                val title = json.optString("title", "Reddit Post")
                val thumb = json.optString("thumbnail_url", "")
                return FastMeta(title, thumb)
            }
        }
    } catch (_: Exception) {}
    return null
}

fun fetchBackendApi(url: String, retryCount: Int = 1): DownloadResult? {
    val backendUrl = ApiSecurity.getDownloadUrl()
    val baseApiUrl = ApiSecurity.getBaseUrl()

    for (attempt in 0..retryCount) {
        try {
            val jsonPayload = JSONObject().apply { put("url", url) }.toString()
            val requestBody = jsonPayload.toRequestBody("application/json".toMediaType())
            val request = Request.Builder()
                .url(backendUrl)
                .post(requestBody)
                .addHeader("Content-Type", "application/json")
                .addHeader("X-Aura-Api-Key", ApiSecurity.API_KEY)
                .addHeader("User-Agent", "AuraDownloaderApp/2.0")
                .build()

            val response = okHttpClient.newCall(request).execute()
            if (response.isSuccessful) {
                val resStr = response.body?.string() ?: ""
                android.util.Log.d("BackendNetworkClient", "Raw backend response body for URL ($url): $resStr")
                val rootJson = JSONObject(resStr)
                val json = rootJson.optJSONObject("data") ?: rootJson.optJSONObject("result") ?: rootJson

                val success = json.optBoolean("success", rootJson.optBoolean("success", true))
                val title = json.optString("title", 
                            json.optString("caption",
                            json.optString("filename", 
                            rootJson.optString("title", "Media Download"))))

                val thumbnail = json.optString("thumbnail", 
                                json.optString("cover", 
                                json.optString("image", 
                                json.optString("photo", ""))))

                val rootFilename = json.optString("filename", "")
                val qs = mutableListOf<MediaQuality>()

                fun addMediaItem(rawUrl: String, rawLabel: String, rawSize: String? = null) {
                    if (rawUrl.isEmpty()) return
                    var itemUrl = rawUrl
                    if (itemUrl.startsWith("/")) itemUrl = baseApiUrl + itemUrl
                    
                    val lowerUrl = itemUrl.lowercase()
                    val lowerLabel = rawLabel.lowercase()
                    
                    val finalLabel = when {
                        rawLabel.isNotEmpty() && !rawLabel.equals("Download", ignoreCase = true) -> rawLabel
                        lowerLabel.contains("mp3") || lowerLabel.contains("audio") || lowerUrl.contains(".mp3") -> "Audio Stream (MP3)"
                        lowerLabel.contains("gif") || lowerUrl.contains(".gif") -> "Animated GIF"
                        lowerLabel.contains("image") || lowerLabel.contains("photo") || lowerUrl.contains(".jpg") || lowerUrl.contains(".jpeg") || lowerUrl.contains(".png") || lowerUrl.contains(".webp") -> "Photo (High Quality)"
                        lowerLabel.contains("video") || lowerUrl.contains(".mp4") || lowerUrl.contains(".mkv") || lowerUrl.contains(".webm") || url.contains("/reel", ignoreCase = true) || url.contains("/video", ignoreCase = true) || url.contains("/shorts", ignoreCase = true) -> "Video (MP4)"
                        else -> "Download High Quality"
                    }
                    
                    val sizeVal = if (rawSize.isNullOrEmpty() || rawSize == "Unknown Size") null else rawSize
                    qs.add(MediaQuality(finalLabel, sizeVal, itemUrl))
                }

                // 1. Process qualities / media / items / picker array
                val arr = json.optJSONArray("qualities")
                    ?: json.optJSONArray("media")
                    ?: json.optJSONArray("items")
                    ?: json.optJSONArray("picker")
                    ?: json.optJSONArray("list")

                if (arr != null) {
                    for (i in 0 until arr.length()) {
                        val item = arr.optJSONObject(i)
                        if (item != null) {
                            val qUrl = item.optString("url", item.optString("src", item.optString("link", item.optString("download_url", ""))))
                            val qLabel = item.optString("label", item.optString("resolution", item.optString("type", item.optString("quality", "Download"))))
                            val qSize = item.optString("size", item.optString("filesize", ""))
                            addMediaItem(qUrl, qLabel, qSize)
                        }
                    }
                }

                // 2. Process picker as object
                val pickerObj = json.optJSONObject("picker")
                if (pickerObj != null) {
                    val pickerArr = pickerObj.optJSONArray("images") 
                        ?: pickerObj.optJSONArray("photos")
                        ?: pickerObj.optJSONArray("items")
                        ?: pickerObj.optJSONArray("media")
                    if (pickerArr != null) {
                        for (i in 0 until pickerArr.length()) {
                            val item = pickerArr.optJSONObject(i)
                            if (item != null) {
                                val pUrl = item.optString("url", item.optString("src", item.optString("photo", "")))
                                val pType = item.optString("type", "Photo / Media #${i + 1}")
                                addMediaItem(pUrl, pType)
                            }
                        }
                    }
                }

                // 3. Process direct root url / streamUrl
                val rootUrl = json.optString("url", json.optString("streamUrl", json.optString("downloadUrl", json.optString("link", ""))))
                if (rootUrl.isNotEmpty()) {
                    var qualityLabel = if (json.has("quality")) "Download ${json.optString("quality")}" else "Download High Quality"
                    if (rootFilename.endsWith(".mp4", ignoreCase = true) || rootUrl.contains(".mp4", ignoreCase = true)) {
                        qualityLabel = "Video (MP4)"
                    } else if (rootUrl.contains(".gif", ignoreCase = true)) {
                        qualityLabel = "Animated GIF"
                    } else if (rootUrl.contains(".jpg", ignoreCase = true) || rootUrl.contains(".png", ignoreCase = true) || rootUrl.contains(".webp", ignoreCase = true)) {
                        qualityLabel = "Photo (High Quality)"
                    }
                    addMediaItem(rootUrl, qualityLabel)
                }

                // 4. Process direct image / photo field
                val photoUrl = json.optString("photo", json.optString("image", json.optString("picture", "")))
                if (photoUrl.isNotEmpty() && photoUrl.startsWith("http")) {
                    addMediaItem(photoUrl, "Photo (High Quality)")
                }

                val finalQs = qs.distinctBy { it.label + it.url }
                val fetchedLyrics = (json.optString("syncedLyrics", "").takeIf { it.isNotEmpty() }
                    ?: json.optString("lyrics", "").takeIf { it.isNotEmpty() })
                val fetchedArtist = json.optString("artist", json.optString("author", json.optString("author_name", ""))).takeIf { it.isNotEmpty() }
                val fetchedAudio = json.optString("audioUrl", json.optString("previewAudioUrl", json.optString("audio", "")))
                    .takeIf { it.isNotEmpty() }?.let { if (it.startsWith("/")) baseApiUrl + it else it }

                if (finalQs.isNotEmpty()) {
                    return DownloadResult(
                        success = true,
                        title = title,
                        thumbnailUrl = thumbnail,
                        qualities = finalQs,
                        lyrics = fetchedLyrics,
                        artistName = fetchedArtist,
                        previewAudioUrl = fetchedAudio
                    )
                } else if (!success) {
                    val msg = json.optString("message", json.optString("error", "Extraction failed."))
                    return DownloadResult(false, "", "", emptyList(), msg)
                }
            }
        } catch (e: Exception) {
            android.util.Log.e("BackendNetworkClient", "Attempt $attempt failed: ${e.message}")
            if (attempt < retryCount) {
                try { Thread.sleep(1000L) } catch (_: Exception) {}
            }
        }
    }
    return null
}

suspend fun resolveDirectAudioUrl(resolveUrl: String, title: String = "", artist: String = ""): String? = withContext(Dispatchers.IO) {
    if (resolveUrl.isEmpty()) return@withContext null
    try {
        var fullUrl = if (resolveUrl.startsWith("/")) {
            ApiSecurity.getBaseUrl() + resolveUrl
        } else resolveUrl

        if (fullUrl.contains("spotify-resolve")) {
            if (title.isNotEmpty()) {
                val encT = java.net.URLEncoder.encode(title, "UTF-8")
                if (fullUrl.contains("title=")) {
                    fullUrl = fullUrl.replace(Regex("title=[^&]*"), "title=$encT")
                } else {
                    fullUrl += if (fullUrl.contains("?")) "&title=$encT" else "?title=$encT"
                }
            }
            if (artist.isNotEmpty()) {
                val encA = java.net.URLEncoder.encode(artist, "UTF-8")
                if (fullUrl.contains("artist=")) {
                    fullUrl = fullUrl.replace(Regex("artist=[^&]*"), "artist=$encA")
                } else {
                    fullUrl += if (fullUrl.contains("?")) "&artist=$encA" else "?artist=$encA"
                }
            }
        }
        val req = Request.Builder()
            .url(fullUrl)
            .addHeader("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            .addHeader("X-Aura-Api-Key", ApiSecurity.API_KEY)
            .get()
            .build()
        val res = okHttpClient.newCall(req).execute()
        if (res.isSuccessful) {
            val body = res.body?.string() ?: ""
            android.util.Log.d("BackendNetworkClient", "Raw resolve response for URL ($fullUrl): $body")
            if (body.trim().startsWith("{")) {
                val json = JSONObject(body)
                if (json.optBoolean("success", true) && json.has("url")) {
                    val direct = json.getString("url")
                    if (direct.isNotEmpty()) return@withContext direct
                }
            }
        }
    } catch (e: Exception) {
        android.util.Log.e("AudioResolve", "Audio resolution error: ${e.message}")
    }
    null
}

suspend fun fetchTrackLyrics(title: String, artist: String?, durationSec: Int = 0): String? = withContext(Dispatchers.IO) {
    if (title.isEmpty() || title == "Spotify Track" || title == "Media Download") return@withContext null

    val rawTitle = title.trim()
    val rawArtist = (artist ?: "").trim()
    val primaryArtist = rawArtist.split(",").firstOrNull()?.split("&")?.firstOrNull()?.split("feat.")?.firstOrNull()?.trim() ?: rawArtist

    // Clean title by removing artist name if it was pre-concatenated (e.g. "Song Name - Artist")
    var cleanTitle = rawTitle
    if (cleanTitle.contains(" - ")) {
        val left = cleanTitle.substringBefore(" - ").trim()
        val right = cleanTitle.substringAfter(" - ").trim()
        if (primaryArtist.isNotEmpty() && right.equals(primaryArtist, ignoreCase = true)) {
            cleanTitle = left
        } else if (primaryArtist.isEmpty() || left.equals(primaryArtist, ignoreCase = true)) {
            cleanTitle = right
        } else {
            cleanTitle = left
        }
    }
    // Remove video fluff like (Official Music Video), [Lyrics], (feat. ...), (Remastered...)
    val sanitizedTitle = cleanTitle
        .replace(Regex("""(?i)\s*[\(\[](official\s*(music\s*)?video|official\s*video|official\s*audio|video|audio|lyrics?|visualizer|remaster(ed)?(\s*\d{4})?|deluxe(\s*edition)?)[\)\]]"""), "")
        .trim()

    val titleCandidates = listOf(sanitizedTitle, cleanTitle, rawTitle).distinct().filter { it.isNotEmpty() }

    // 1. Try with backend lyrics API
    for (candidate in titleCandidates) {
        try {
            val encT = java.net.URLEncoder.encode(candidate, "UTF-8")
            val encA = if (primaryArtist.isNotEmpty()) "&artist=" + java.net.URLEncoder.encode(primaryArtist, "UTF-8") else ""
            val lyricsUrl = ApiSecurity.getLyricsUrl() + "?title=$encT$encA"
            val req = Request.Builder().url(lyricsUrl).get().build()
            val res = okHttpClient.newCall(req).execute()
            if (res.isSuccessful) {
                val body = res.body?.string() ?: ""
                if (body.trim().startsWith("{")) {
                    val json = JSONObject(body)
                    if (json.optBoolean("success", true)) {
                        val synced = json.optString("syncedLyrics", "")
                        val plain = json.optString("lyrics", "")
                        val lrc = if (synced.isNotEmpty()) synced else plain
                        if (lrc.isNotEmpty()) return@withContext lrc
                    }
                }
            }
        } catch (_: Exception) {}
    }

    // 2. Try direct LRCLIB get with exact track_name & artist_name
    for (candidate in titleCandidates) {
        try {
            val encT = java.net.URLEncoder.encode(candidate, "UTF-8")
            val encA = if (primaryArtist.isNotEmpty()) "&artist_name=" + java.net.URLEncoder.encode(primaryArtist, "UTF-8") else ""
            val durParam = if (durationSec > 0) "&duration=$durationSec" else ""
            val lrclibUrl = "https://lrclib.net/api/get?track_name=$encT$encA$durParam"
            
            val req = Request.Builder()
                .url(lrclibUrl)
                .addHeader("User-Agent", "AuraDownloader/2.0 (https://github.com)")
                .get()
                .build()
            val res = okHttpClient.newCall(req).execute()
            if (res.isSuccessful) {
                val body = res.body?.string() ?: ""
                if (body.trim().startsWith("{")) {
                    val json = JSONObject(body)
                    val synced = json.optString("syncedLyrics", "")
                    val plain = json.optString("plainLyrics", "")
                    val lrc = if (synced.isNotEmpty()) synced else plain
                    if (lrc.isNotEmpty()) return@withContext lrc
                }
            }
        } catch (_: Exception) {}
    }

    // 3. Try LRCLIB search query with candidate + primaryArtist
    for (candidate in titleCandidates) {
        try {
            val query = if (primaryArtist.isNotEmpty()) "$candidate $primaryArtist" else candidate
            val encQ = java.net.URLEncoder.encode(query, "UTF-8")
            val lrclibSearchUrl = "https://lrclib.net/api/search?q=$encQ"
            val req = Request.Builder()
                .url(lrclibSearchUrl)
                .addHeader("User-Agent", "AuraDownloader/2.0 (https://github.com)")
                .get()
                .build()
            val res = okHttpClient.newCall(req).execute()
            if (res.isSuccessful) {
                val body = res.body?.string() ?: ""
                if (body.trim().startsWith("[")) {
                    val arr = org.json.JSONArray(body)
                    for (i in 0 until arr.length()) {
                        val item = arr.getJSONObject(i)
                        val synced = item.optString("syncedLyrics", "")
                        if (synced.isNotEmpty()) return@withContext synced
                    }
                    if (arr.length() > 0) {
                        val plain = arr.getJSONObject(0).optString("plainLyrics", "")
                        if (plain.isNotEmpty()) return@withContext plain
                    }
                }
            }
        } catch (_: Exception) {}
    }

    null
}

suspend fun extractWithCobalt(url: String): DownloadResult = withContext(Dispatchers.IO) {
    val cleanUrl = url.trim()
    val lowerUrl = cleanUrl.lowercase()

    warmUpBackend()

    if (lowerUrl.contains("spotify.com") || lowerUrl.contains("spotify:")) {
        if (lowerUrl.contains("/playlist") || lowerUrl.contains("/album") || lowerUrl.contains("/artist")) {
            return@withContext DownloadResult(
                success = false,
                title = "",
                thumbnailUrl = "",
                qualities = emptyList(),
                error = "Spotify playlists, albums & artists are not supported. Please paste a link to a single Spotify song/track."
            )
        }

        val trackRegex = Regex("""(?:spotify\.com/(?:[a-zA-Z0-9-]+/)?track/|spotify:track:)([a-zA-Z0-9]{22})""")
        val trackId = trackRegex.find(cleanUrl)?.groupValues?.getOrNull(1)

        if (trackId == null) {
            return@withContext DownloadResult(
                success = false,
                title = "Spotify Track",
                thumbnailUrl = "",
                qualities = emptyList(),
                error = "Invalid Spotify track URL. Please provide a valid single track link."
            )
        }

        try {
            return@withContext coroutineScope {
                val embedDeferred = async {
                    try {
                        val req = Request.Builder()
                            .url("https://open.spotify.com/embed/track/$trackId")
                            .addHeader("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                            .build()
                        val res = okHttpClient.newCall(req).execute()
                        if (res.isSuccessful) res.body?.string() else null
                    } catch (_: Exception) { null }
                }

                val oembedDeferred = async {
                    try {
                        val req = Request.Builder().url("https://open.spotify.com/oembed?url=https://open.spotify.com/track/$trackId").build()
                        val res = okHttpClient.newCall(req).execute()
                        if (res.isSuccessful) JSONObject(res.body?.string() ?: "") else null
                    } catch (_: Exception) { null }
                }

                val backendDeferred = async {
                    fetchBackendApi("https://open.spotify.com/track/$trackId")
                }

                val html = embedDeferred.await()
                val ojson = oembedDeferred.await()
                val backendResult = backendDeferred.await()

                var trackTitle = ojson?.optString("title")?.takeIf { it.isNotEmpty() } ?: "Spotify Track"
                var artistName = ""
                var thumbnailUrl = ojson?.optString("thumbnail_url") ?: ""
                var previewUrl = ""
                var durationMs = 0L
                var isrcCode = ""
                var entityFound = false

                if (!html.isNullOrEmpty()) {
                    val nextDataRegex = Regex("""<script id="__NEXT_DATA__" type="application/json">(.*?)</script>""")
                    val nextDataMatch = nextDataRegex.find(html)
                    if (nextDataMatch != null) {
                        try {
                            val nextDataJsonStr = nextDataMatch.groupValues.getOrNull(1) ?: ""
                            val rootJson = JSONObject(nextDataJsonStr)
                            val entityJson = rootJson.optJSONObject("props")
                                ?.optJSONObject("pageProps")
                                ?.optJSONObject("state")
                                ?.optJSONObject("data")
                                ?.optJSONObject("entity")

                            if (entityJson != null) {
                                entityFound = true
                                val json = entityJson
                                val name = json.optString("name", "")
                                if (name.isNotEmpty()) trackTitle = name

                                val artistsArray = json.optJSONArray("artists")
                                if (artistsArray != null && artistsArray.length() > 0) {
                                    val names = mutableListOf<String>()
                                    for (i in 0 until artistsArray.length()) {
                                        names.add(artistsArray.getJSONObject(i).optString("name"))
                                    }
                                    artistName = names.joinToString(", ")
                                }

                                val audioPreviewObj = json.optJSONObject("audioPreview")
                                if (audioPreviewObj != null) {
                                    previewUrl = audioPreviewObj.optString("url", "")
                                } else if (json.has("preview_url")) {
                                    previewUrl = json.optString("preview_url", "")
                                }

                                durationMs = json.optLong("duration", json.optLong("durationMs", 0L))
                                isrcCode = json.optString("isrc", "")

                                if (thumbnailUrl.isEmpty()) {
                                    val visualIdentityObj = json.optJSONObject("visualIdentity")
                                    val images = visualIdentityObj?.optJSONArray("image")
                                    if (images != null && images.length() > 0) {
                                        thumbnailUrl = images.getJSONObject(0).optString("url", "")
                                    }
                                }
                            }
                        } catch (e: Exception) {
                            android.util.Log.e("SpotifyExtract", "Failed parsing NEXT_DATA: ${e.message}")
                        }
                    } else {
                        // Fallback using manual find
                        val entityStartIdx = html.indexOf("\"entity\":{")
                        if (entityStartIdx != -1) {
                            try {
                                val substring = html.substring(entityStartIdx + 9) // from {
                                var braceCount = 0
                                var endIdx = -1
                                for (i in substring.indices) {
                                    if (substring[i] == '{') braceCount++
                                    else if (substring[i] == '}') braceCount--
                                    if (braceCount == 0) {
                                        endIdx = i
                                        break
                                    }
                                }
                                if (endIdx != -1) {
                                    val entityJsonStr = substring.substring(0, endIdx + 1)
                                    val json = JSONObject(entityJsonStr)
                                    entityFound = true
                                    val name = json.optString("name", "")
                                    if (name.isNotEmpty()) trackTitle = name

                                    val artistsArray = json.optJSONArray("artists")
                                    if (artistsArray != null && artistsArray.length() > 0) {
                                        val names = mutableListOf<String>()
                                        for (i in 0 until artistsArray.length()) {
                                            names.add(artistsArray.getJSONObject(i).optString("name"))
                                        }
                                        artistName = names.joinToString(", ")
                                    }

                                    val audioPreviewObj = json.optJSONObject("audioPreview")
                                    if (audioPreviewObj != null) {
                                        previewUrl = audioPreviewObj.optString("url", "")
                                    } else if (json.has("preview_url")) {
                                        previewUrl = json.optString("preview_url", "")
                                    }

                                    durationMs = json.optLong("duration", json.optLong("durationMs", 0L))
                                    isrcCode = json.optString("isrc", "")
                                }
                            } catch (_: Exception) {}
                        }
                    }
                }

                val backendTitle = backendResult?.title?.takeIf { it.isNotEmpty() && it != "Media Download" && it != "Video Download" }
                val displayTitle = backendTitle ?: if (artistName.isNotEmpty() && !trackTitle.contains(artistName)) "$trackTitle - $artistName" else trackTitle
                val displayThumb = backendResult?.thumbnailUrl?.takeIf { it.isNotEmpty() } ?: thumbnailUrl

                val fullTrackTitle = trackTitle.trim()

                var finalPreviewAudio = previewUrl
                val backendAudio = backendResult?.qualities?.firstOrNull { it.url.isNotEmpty() && !it.url.contains("spotify-resolve") }?.url
                    ?: backendResult?.previewAudioUrl?.takeIf { it.isNotEmpty() && !it.contains("spotify-resolve") }

                if (finalPreviewAudio.isEmpty() && !backendAudio.isNullOrEmpty()) {
                    finalPreviewAudio = backendAudio
                }

                if (finalPreviewAudio.isNotEmpty() && finalPreviewAudio.startsWith("/")) {
                    val baseBackend = ApiSecurity.getBaseUrl()
                    finalPreviewAudio = baseBackend + finalPreviewAudio
                }

                // Concurrently fetch lyrics and resolve full length track audio
                val lyricsDeferred = async { fetchTrackLyrics(trackTitle, artistName, (durationMs / 1000).toInt()) }
                
                val cleanTitle = trackTitle.replace(Regex("""\s*[\(\[\{]?(?:official\s*(?:audio|video|music\s*video|lyric\s*video)?|audio|video|lyrics?|remastered|remaster|hd)[\)\]\}]?""", RegexOption.IGNORE_CASE), "").trim()
                val cleanArtist = artistName.split(",").firstOrNull()?.split("&")?.firstOrNull()?.split("feat.")?.firstOrNull()?.trim() ?: artistName.trim()
                val searchTitle = cleanTitle.ifEmpty { trackTitle.trim() }
                val searchArtist = cleanArtist.ifEmpty { artistName.trim() }
                val spotifyResolveUrl = backendResult?.qualities?.firstOrNull { it.url.contains("spotify-resolve") }?.url
                    ?: backendResult?.previewAudioUrl?.takeIf { it.contains("spotify-resolve") }
                    ?: "/api/spotify-resolve?trackId=$trackId&title=${java.net.URLEncoder.encode(searchTitle, "UTF-8")}&artist=${java.net.URLEncoder.encode(searchArtist, "UTF-8")}&durationMs=$durationMs&isrc=$isrcCode"

                val directFullAudioDeferred = async {
                    resolveDirectAudioUrl(spotifyResolveUrl, searchTitle, searchArtist)
                }

                val directFullAudio = directFullAudioDeferred.await()
                val fetchedLyrics = lyricsDeferred.await() ?: backendResult?.lyrics

                // Primary playback audio: prioritize the full track from the backend using the Official Audio search
                // If it fails, fallback to the 30s official Spotify studio preview clip
                val finalPlayableAudio = directFullAudio ?: backendAudio?.takeIf { it.isNotEmpty() } ?: finalPreviewAudio
                val isFinalValid = if (finalPlayableAudio.isNotEmpty()) verifyAudioUrl(finalPlayableAudio) else null

                val diagnostic = SpotifyDiagnosticLogMapper.logAndMapMetadata(
                    trackId = trackId,
                    title = displayTitle,
                    artist = artistName,
                    embedHtmlFound = !html.isNullOrEmpty(),
                    entityJsonParsed = entityFound,
                    spotifyPreviewUrl = previewUrl.takeIf { it.isNotEmpty() },
                    backendAudioUrl = backendAudio ?: directFullAudio,
                    isReachable = isFinalValid
                )

                if (diagnostic.resolvedErrorMessage != null) {
                    return@coroutineScope DownloadResult(
                        success = false,
                        title = displayTitle,
                        thumbnailUrl = displayThumb,
                        qualities = emptyList(),
                        error = diagnostic.resolvedErrorMessage
                    )
                }

                val durationStr = if (durationMs > 0) formatTimeMs(durationMs.toInt()) else null

                val qualities = mutableListOf<MediaQuality>()
                if (finalPreviewAudio.isNotEmpty()) {
                    qualities.add(MediaQuality("Spotify Studio Audio (MP3)", null, finalPreviewAudio))
                }
                if (!directFullAudio.isNullOrEmpty() && directFullAudio != finalPreviewAudio) {
                    qualities.add(MediaQuality("Full Track Audio (MP3 320kbps)", null, directFullAudio))
                } else if (!spotifyResolveUrl.isNullOrEmpty()) {
                    qualities.add(MediaQuality("Full Track Audio (MP3 320kbps)", null, spotifyResolveUrl))
                }
                if (displayThumb.isNotEmpty() && qualities.none { it.label.contains("Art") || it.label.contains("Cover") }) {
                    qualities.add(MediaQuality("Album Cover Art (JPG)", null, displayThumb))
                }

                DownloadResult(
                    success = true,
                    title = displayTitle,
                    thumbnailUrl = displayThumb,
                    qualities = qualities,
                    isSpotify = true,
                    previewAudioUrl = finalPlayableAudio,
                    artistName = artistName,
                    spotifyTracks = listOf(
                        SpotifyTrack(
                            name = fullTrackTitle,
                            artist = artistName,
                            durationStr = durationStr,
                            trackNumber = 1,
                            resolveUrl = spotifyResolveUrl,
                            directAudioUrl = finalPlayableAudio,
                            thumbnailUrl = displayThumb
                        )
                    ),
                    lyrics = fetchedLyrics
                )
            }
        } catch (e: Exception) {
            e.printStackTrace()
            return@withContext DownloadResult(
                success = false,
                title = "Spotify Track",
                thumbnailUrl = "",
                qualities = emptyList(),
                error = "Failed to retrieve Spotify track metadata. Please check your network connection and try again."
            )
        }
    }

    return@withContext coroutineScope {
        val fastMetaDeferred = async { fetchFastMeta(cleanUrl) }
        val backendDeferred = async { fetchBackendApi(cleanUrl) }

        val fastMeta = fastMetaDeferred.await()
        val backendRes = backendDeferred.await()

        if (backendRes != null && backendRes.success) {
            val finalTitle = if (backendRes.title.isNotEmpty() && backendRes.title != "Video Download" && backendRes.title != "Media Download") backendRes.title else (fastMeta?.title ?: "Media Download")
            val finalThumb = if (backendRes.thumbnailUrl.isNotEmpty()) backendRes.thumbnailUrl else (fastMeta?.thumbnailUrl ?: "")

            val qualities = backendRes.qualities.toMutableList()
            if (finalThumb.isNotEmpty() && qualities.none { it.label.contains("Thumbnail") || it.label.contains("Cover") }) {
                qualities.add(MediaQuality("Thumbnail / Cover (JPG)", null, finalThumb))
            }

            return@coroutineScope DownloadResult(
                success = true,
                title = finalTitle,
                thumbnailUrl = finalThumb,
                qualities = qualities.distinctBy { it.label + it.url },
                lyrics = backendRes.lyrics
            )
        }

        if (fastMeta != null && fastMeta.title.isNotEmpty()) {
            val fallbackQualities = mutableListOf<MediaQuality>()
            if (fastMeta.streamUrl != null && fastMeta.streamUrl.isNotEmpty()) {
                fallbackQualities.add(MediaQuality("Direct Media Stream (MP4)", null, fastMeta.streamUrl))
            } else {
                fallbackQualities.add(MediaQuality("Download High Quality Video (MP4)", null, "${ApiSecurity.getBaseUrl()}/api/get-youtube-link?url=${cleanUrl}&quality=720"))
            }
            fallbackQualities.add(MediaQuality("Download Audio Stream (MP3)", null, "${ApiSecurity.getBaseUrl()}/api/get-youtube-link?url=${cleanUrl}&quality=audio"))
            
            if (fastMeta.thumbnailUrl.isNotEmpty()) {
                fallbackQualities.add(MediaQuality("High-Res Photo / Cover (JPG)", null, fastMeta.thumbnailUrl))
            }

            if (fallbackQualities.isNotEmpty()) {
                return@coroutineScope DownloadResult(
                    success = true,
                    title = fastMeta.title,
                    thumbnailUrl = fastMeta.thumbnailUrl,
                    qualities = fallbackQualities
                )
            }
        }

        if (backendRes != null && backendRes.error != null) {
            return@coroutineScope DownloadResult(false, "", "", emptyList(), backendRes.error)
        }

        DownloadResult(false, "", "", emptyList(), "Unable to extract media. Please check the URL and try again.")
    }
    }



fun getFallbackResult(url: String): DownloadResult {
    val cleanUrl = url.trim()
    val ytId = extractYouTubeVideoId(cleanUrl)
    val thumb = if (ytId != null) "https://i.ytimg.com/vi/$ytId/hqdefault.jpg" else ""
    val title = if (ytId != null) "Video Download" else "Media Download"
    
    val qs = mutableListOf(
        MediaQuality("Download High Quality Video (MP4)", null, "${ApiSecurity.getBaseUrl()}/api/get-youtube-link?url=${cleanUrl}&quality=720"),
        MediaQuality("Download Audio Stream (MP3)", null, "${ApiSecurity.getBaseUrl()}/api/get-youtube-link?url=${cleanUrl}&quality=audio")
    )
    if (thumb.isNotEmpty()) {
        qs.add(MediaQuality("Thumbnail / Cover (JPG)", null, thumb))
    }
    
    return DownloadResult(
        success = true,
        title = title,
        thumbnailUrl = thumb,
        qualities = qs
    )
}

fun extractYouTubeVideoId(url: String): String? {
    val regex = Regex("""(?<=v=|v/|vi=|vi/|youtu.be/|/shorts/|/e/|/embed/|/v/|/watch\?v=|&v=)([a-zA-Z0-9_-]{11})""")
    return regex.find(url)?.groupValues?.getOrNull(1) ?: Regex("""[a-zA-Z0-9_-]{11}""").find(url)?.value
}

suspend fun verifyAudioUrl(url: String): Boolean = withContext(Dispatchers.IO) {
    if (url.isBlank()) return@withContext false
    val baseBackend = ApiSecurity.getBaseUrl()
    val fullUrl = if (url.startsWith("/")) baseBackend + url else url
    try {
        val req = Request.Builder()
            .url(fullUrl)
            .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            .header("Range", "bytes=0-1024")
            .get()
            .build()
        val res = okHttpClient.newCall(req).execute()
        val code = res.code
        val contentType = res.header("Content-Type") ?: ""
        val isSuccess = (code in 200..299 || code in 300..399) && !contentType.contains("application/json") && !contentType.contains("text/html")
        res.close()
        return@withContext isSuccess
    } catch (e: Exception) {
        android.util.Log.e("AudioVerifier", "Verification failed: ${e.message}")
        return@withContext false
    }
}



fun extractUrlFromIntent(context: Context, intent: Intent?): String? {
    if (intent == null) return null

    if (intent.hasExtra("shortcut_action")) {
        val action = intent.getStringExtra("shortcut_action")
        if (action == "youtube_shorts") return "https://youtube.com/shorts"
    }
    if (intent.hasExtra("widget_action")) {
        val action = intent.getStringExtra("widget_action")
        if (action == "YOUTUBE_SHORTS") return "https://youtube.com/shorts"
    }

    val candidates = mutableListOf<String>()

    intent.getStringExtra(Intent.EXTRA_TEXT)?.let { candidates.add(it) }
    intent.getCharSequenceExtra(Intent.EXTRA_TEXT)?.toString()?.let { candidates.add(it) }
    intent.getStringExtra(Intent.EXTRA_SUBJECT)?.let { candidates.add(it) }

    intent.clipData?.let { clip ->
        for (i in 0 until clip.itemCount) {
            clip.getItemAt(i)?.text?.toString()?.let { candidates.add(it) }
            clip.getItemAt(i)?.uri?.toString()?.let { candidates.add(it) }
        }
    }

    intent.dataString?.let { candidates.add(it) }
    intent.data?.toString()?.let { candidates.add(it) }

    if (candidates.isEmpty() && intent.hasExtra("widget_action")) {
        try {
            val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as? android.content.ClipboardManager
            val clipText = clipboard?.primaryClip?.getItemAt(0)?.text?.toString()
            if (!clipText.isNullOrEmpty()) {
                candidates.add(clipText)
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    val urlRegex = "https?://\\S+".toRegex()
    for (candidate in candidates) {
        val match = urlRegex.find(candidate)
        if (match != null) {
            var url = match.value.trimEnd('.', ',', ')', ']', '}', '!', '?', '"', '\'')
            if (url.isNotEmpty()) {
                return url
            }
        }
    }
    return null
}

class MainActivity : ComponentActivity() {
    private var incomingSharedUrl by mutableStateOf<String?>(null)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        handleIncomingIntent(intent)
        setContent {
            MyApplicationTheme {
                MainScreen(
                    incomingSharedUrl = incomingSharedUrl,
                    onSharedUrlConsumed = { incomingSharedUrl = null }
                )
            }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        handleIncomingIntent(intent)
    }

    private fun handleIncomingIntent(intent: Intent?) {
        val extractedUrl = extractUrlFromIntent(this, intent)
        if (!extractedUrl.isNullOrEmpty()) {
            incomingSharedUrl = extractedUrl
        }
    }
}





@Composable
fun Platform3DIcon(
    platform: Platform,
    modifier: Modifier = Modifier,
    isDarkMode: Boolean = true
) {
    val shape = when (platform) {
        Platform.PINTEREST, Platform.REDDIT, Platform.FACEBOOK, Platform.SPOTIFY -> CircleShape
        else -> RoundedCornerShape(percent = 28)
    }

    val brandColor = platform.brandColor

    val backgroundBrush = if (isDarkMode) {
        Brush.linearGradient(
            colors = listOf(
                brandColor.copy(alpha = 0.35f),
                brandColor.copy(alpha = 0.15f),
                brandColor.copy(alpha = 0.25f)
            )
        )
    } else {
        when (platform) {
            Platform.YOUTUBE -> Brush.linearGradient(
                colors = listOf(Color(0xFFFF0000), Color(0xFFE60000), Color(0xFFCC0000))
            )
            Platform.INSTAGRAM -> Brush.linearGradient(
                colors = listOf(Color(0xFF833AB4), Color(0xFFFD1D1D), Color(0xFFFCB045))
            )
            Platform.SPOTIFY -> Brush.linearGradient(
                colors = listOf(Color(0xFF1ED760), Color(0xFF1DB954), Color(0xFF15883E))
            )
            Platform.SNAPCHAT -> Brush.linearGradient(
                colors = listOf(Color(0xFFFFFC00), Color(0xFFFFEB3B), Color(0xFFFFD600))
            )
            Platform.THREADS -> Brush.linearGradient(
                colors = listOf(Color(0xFF262626), Color(0xFF101010), Color(0xFF000000))
            )
            Platform.PINTEREST -> Brush.linearGradient(
                colors = listOf(Color(0xFFE60023), Color(0xFFBD081C), Color(0xFF8C0615))
            )
            Platform.X -> Brush.linearGradient(
                colors = listOf(Color(0xFF262626), Color(0xFF101010), Color(0xFF000000))
            )
            Platform.LINKEDIN -> Brush.linearGradient(
                colors = listOf(Color(0xFF0A66C2), Color(0xFF0077B5), Color(0xFF004182))
            )
            Platform.TIKTOK -> Brush.linearGradient(
                colors = listOf(Color(0xFF262626), Color(0xFF101010), Color(0xFF000000))
            )
            Platform.FACEBOOK -> Brush.linearGradient(
                colors = listOf(Color(0xFF1877F2), Color(0xFF0D65D9), Color(0xFF08489E))
            )
            Platform.REDDIT -> Brush.linearGradient(
                colors = listOf(Color(0xFFFF4500), Color(0xFFFF5722), Color(0xFFD83A00))
            )
        }
    }

    val borderBrush = if (isDarkMode) {
        Brush.verticalGradient(
            colors = listOf(
                Color.White.copy(alpha = 0.65f),
                brandColor.copy(alpha = 0.40f),
                Color.White.copy(alpha = 0.15f)
            )
        )
    } else {
        Brush.verticalGradient(
            colors = listOf(
                Color.White.copy(alpha = 0.85f),
                Color.White.copy(alpha = 0.35f),
                Color.Black.copy(alpha = 0.15f)
            )
        )
    }

    val shadowAmbient = if (isDarkMode) brandColor.copy(alpha = 0.35f) else brandColor.copy(alpha = 0.45f)
    val shadowSpot = if (isDarkMode) brandColor.copy(alpha = 0.5f) else brandColor.copy(alpha = 0.6f)

    Box(
        modifier = modifier
            .shadow(
                elevation = 6.dp,
                shape = shape,
                ambientColor = shadowAmbient,
                spotColor = shadowSpot
            )
            .clip(shape)
            .background(backgroundBrush)
            .border(
                width = 1.2.dp,
                brush = borderBrush,
                shape = shape
            ),
        contentAlignment = Alignment.Center
    ) {
        // Glossy Top Reflection Overlay for Glass Effect
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .fillMaxHeight(0.5f)
                .align(Alignment.TopCenter)
                .background(
                    Brush.verticalGradient(
                        colors = listOf(
                            Color.White.copy(alpha = if (isDarkMode) 0.35f else 0.30f),
                            Color.White.copy(alpha = if (isDarkMode) 0.08f else 0.05f),
                            Color.Transparent
                        )
                    )
                )
        )

        // Inner Radial Ambient Glow
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    Brush.radialGradient(
                        colors = listOf(
                            (if (isDarkMode) brandColor else Color.White).copy(alpha = 0.2f),
                            Color.Transparent
                        )
                    )
                )
        )

        // Center Emblem with 3D shadow and specular rim
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(10.dp),
            contentAlignment = Alignment.Center
        ) {
            // Drop Shadow for 3D depth
            Icon(
                painter = painterResource(id = platform.iconResId),
                contentDescription = null,
                tint = Color.Black.copy(alpha = if (platform == Platform.SNAPCHAT && !isDarkMode) 0.6f else 0.35f),
                modifier = Modifier
                    .fillMaxSize()
                    .offset(x = 0.dp, y = 1.5.dp)
            )

            // Top Specular Light Rim
            Icon(
                painter = painterResource(id = platform.iconResId),
                contentDescription = null,
                tint = Color.White.copy(alpha = 0.35f),
                modifier = Modifier
                    .fillMaxSize()
                    .offset(x = 0.dp, y = (-0.5).dp)
            )

            // Main SVG Icon with original colors preserved
            Icon(
                painter = painterResource(id = platform.iconResId),
                contentDescription = platform.displayName,
                tint = if (platform == Platform.SNAPCHAT && !isDarkMode) Color.Black else Color.White,
                modifier = Modifier.fillMaxSize()
            )
        }
    }
}

@Composable
fun MainScreen(
    incomingSharedUrl: String? = null,
    onSharedUrlConsumed: () -> Unit = {}
) {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination

    var isDarkMode by remember { mutableStateOf(true) }
    var selectedPlatform by remember { mutableStateOf(Platform.YOUTUBE) }

    val items = listOf(Screen.Home, Screen.Platforms, Screen.Settings)
    UpdateChecker(context = LocalContext.current, isDarkMode = isDarkMode)

    val backgroundBrush = if (isDarkMode) {
        if (currentDestination?.route == Screen.Home.route) {
            Brush.verticalGradient(listOf(selectedPlatform.startColorDark, selectedPlatform.endColorDark, Color(0xFF000000)))
        } else {
            Brush.verticalGradient(listOf(Color(0xFF262626), Color(0xFF171717), Color(0xFF000000)))
        }
    } else {
        if (currentDestination?.route == Screen.Home.route) {
            Brush.verticalGradient(listOf(selectedPlatform.startColorLight, selectedPlatform.endColorLight, Color(0xFFFAFAFA)))
        } else {
            Brush.verticalGradient(listOf(Color(0xFFF5F5F5), Color(0xFFFAFAFA), Color(0xFFFFFFFF)))
        }
    }

    Scaffold(
        bottomBar = {
            NavigationBar(
                containerColor = if (isDarkMode) Color(0xFF0C0A09).copy(alpha = 0.92f) else Color.White.copy(alpha = 0.95f),
                contentColor = if (isDarkMode) Color.White else Color(0xFF0F172A)
            ) {
                items.forEach { screen ->
                    val selected = currentDestination?.hierarchy?.any { it.route == screen.route } == true
                    NavigationBarItem(
                        icon = { Icon(screen.icon, contentDescription = null) },
                        label = { Text(screen.label) },
                        selected = selected,
                        onClick = {
                            navController.navigate(screen.route) {
                                popUpTo(navController.graph.findStartDestination().id) { saveState = true }
                                launchSingleTop = true
                                restoreState = true
                            }
                        },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = if (isDarkMode) Color(0xFF10B981) else Color(0xFF0066FF),
                            selectedTextColor = if (isDarkMode) Color(0xFF10B981) else Color(0xFF0066FF),
                            unselectedIconColor = if (isDarkMode) Color(0xFF888888) else Color(0xFF64748B),
                            unselectedTextColor = if (isDarkMode) Color(0xFF888888) else Color(0xFF64748B),
                            indicatorColor = Color.Transparent
                        )
                    )
                }
            }
        }
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(backgroundBrush)
                .padding(innerPadding)
        ) {
            NavHost(
                navController = navController,
                startDestination = Screen.Home.route,
                enterTransition = { slideIntoContainer(AnimatedContentTransitionScope.SlideDirection.Left, animationSpec = tween(300)) },
                exitTransition = { slideOutOfContainer(AnimatedContentTransitionScope.SlideDirection.Left, animationSpec = tween(300)) },
                popEnterTransition = { slideIntoContainer(AnimatedContentTransitionScope.SlideDirection.Right, animationSpec = tween(300)) },
                popExitTransition = { slideOutOfContainer(AnimatedContentTransitionScope.SlideDirection.Right, animationSpec = tween(300)) }
            ) {
                composable(Screen.Home.route) {
                    HomeScreen(
                        isDarkMode = isDarkMode,
                        onToggleDarkMode = { isDarkMode = !isDarkMode },

                        selectedPlatform = selectedPlatform,
                        onPlatformSelected = { selectedPlatform = it },
                        incomingSharedUrl = incomingSharedUrl,
                        onSharedUrlConsumed = onSharedUrlConsumed
                    )
                }
                composable(Screen.Platforms.route) {
                    PlatformsScreen(isDarkMode) { platform ->
                        selectedPlatform = platform
                        navController.navigate(Screen.Home.route) { popUpTo(navController.graph.findStartDestination().id) }
                    }
                }
                composable(Screen.Settings.route) { SettingsScreen(isDarkMode, { isDarkMode = !isDarkMode }, { navController.navigate(it) }) }
                composable(Screen.PrivacyPolicy.route) { PrivacyPolicyScreen(isDarkMode, { navController.popBackStack() }) }
                composable(Screen.Terms.route) { TermsScreen(isDarkMode, { navController.popBackStack() }) }
                
                composable(Screen.About.route) { AboutScreen(isDarkMode, { navController.popBackStack() }) }
                composable(Screen.DMCA.route) { DMCAScreen(isDarkMode, { navController.popBackStack() }) }
                composable(Screen.CookiePolicy.route) { CookiePolicyScreen(isDarkMode, { navController.popBackStack() }) }
                composable(Screen.FAQ.route) { FAQScreen(isDarkMode, { navController.popBackStack() }) }
                composable(Screen.ContactUs.route) { ContactUsScreen(isDarkMode, { navController.popBackStack() }) }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    isDarkMode: Boolean,
    onToggleDarkMode: () -> Unit,
    selectedPlatform: Platform,
    onPlatformSelected: (Platform) -> Unit,
    incomingSharedUrl: String? = null,
    onSharedUrlConsumed: () -> Unit = {}
) {
    var url by remember { mutableStateOf("") }
    var isDownloading by remember { mutableStateOf(false) }
    var extractionProgress by remember { mutableFloatStateOf(0f) }
    var result by remember { mutableStateOf<DownloadResult?>(null) }
    var previewThumbnailUrl by remember { mutableStateOf<String?>(null) }
    var previewTitle by remember { mutableStateOf<String?>(null) }
    var actualDownloadProgress by remember { mutableStateOf<Int?>(-1) }
    var isActualDownloading by remember { mutableStateOf(false) }
    var activeDownloadId by remember { mutableStateOf<Long?>(null) }
    var showHistory by remember { mutableStateOf(false) }
    var showLyrics by remember { mutableStateOf<String?>(null) }
    var detectedClipboardUrl by remember { mutableStateOf<String?>(null) }
    var showNotificationsSheet by remember { mutableStateOf(false) }
    val historyList = remember { mutableStateOf<List<org.json.JSONObject>>(emptyList()) }
    val notificationsList = remember { mutableStateOf<List<org.json.JSONObject>>(emptyList()) }
    var unreadCount by remember { mutableIntStateOf(0) }
    val context = LocalContext.current

    val coroutineScope = rememberCoroutineScope()

    LaunchedEffect(activeDownloadId) {
        val id = activeDownloadId ?: return@LaunchedEffect
        isActualDownloading = true
        while (isActualDownloading) {
            val query = android.app.DownloadManager.Query().setFilterById(id)
            val downloadManager = context.getSystemService(android.content.Context.DOWNLOAD_SERVICE) as android.app.DownloadManager
            val cursor = downloadManager.query(query)
            if (cursor.moveToFirst()) {
                val statusIdx = cursor.getColumnIndex(android.app.DownloadManager.COLUMN_STATUS)
                val status = if (statusIdx != -1) cursor.getInt(statusIdx) else -1
                if (status == android.app.DownloadManager.STATUS_SUCCESSFUL || status == android.app.DownloadManager.STATUS_FAILED) {
                    isActualDownloading = false
                    if (status == android.app.DownloadManager.STATUS_SUCCESSFUL) {
                        actualDownloadProgress = 100
                    }
                    cursor.close()
                    break
                }
                val bytesDownloadedIdx = cursor.getColumnIndex(android.app.DownloadManager.COLUMN_BYTES_DOWNLOADED_SO_FAR)
                val bytesTotalIdx = cursor.getColumnIndex(android.app.DownloadManager.COLUMN_TOTAL_SIZE_BYTES)
                if (bytesDownloadedIdx != -1 && bytesTotalIdx != -1) {
                    val bytesDownloaded = cursor.getInt(bytesDownloadedIdx)
                    val bytesTotal = cursor.getInt(bytesTotalIdx)
                    if (bytesTotal > 0) {
                        actualDownloadProgress = ((bytesDownloaded * 100L) / bytesTotal).toInt()
                    }
                }
            }
            cursor.close()
            kotlinx.coroutines.delay(500)
        }
    }

    var showSuccessAnimation by remember { mutableStateOf(false) }
    DisposableEffect(context) {
        val receiver = object : BroadcastReceiver() {
            override fun onReceive(context: android.content.Context?, intent: Intent?) {
                showSuccessAnimation = true
            }
        }
        androidx.core.content.ContextCompat.registerReceiver(context, receiver, IntentFilter("com.auradownloader.DOWNLOAD_COMPLETED"), androidx.core.content.ContextCompat.RECEIVER_NOT_EXPORTED)
        onDispose {
            context.unregisterReceiver(receiver)
        }
    }
    val clipboardManager = LocalClipboardManager.current

    LaunchedEffect(isDownloading) {
        if (isDownloading) {
            extractionProgress = 0.05f
            val startTime = System.currentTimeMillis()
            var notifiedStuck = false
            while (isDownloading && extractionProgress < 0.99f) {
                kotlinx.coroutines.delay(50L)
                val elapsed = System.currentTimeMillis() - startTime
                if (elapsed > 15000L && !notifiedStuck) {
                    notifiedStuck = true
                    android.widget.Toast.makeText(context, "Extraction is taking longer than usual...", android.widget.Toast.LENGTH_SHORT).show()
                }
                val targetProgress = (1f - Math.exp(-elapsed / 10000.0).toFloat()) * 0.99f
                extractionProgress = Math.max(extractionProgress + 0.0005f, targetProgress).coerceAtMost(0.99f)
            }
        } else {
            extractionProgress = 0f
        }
    }
    LaunchedEffect(showNotificationsSheet) {
        val list = PreferencesHelper.getNotifications(context)
        notificationsList.value = list
        unreadCount = list.count { !it.optBoolean("read", true) }
        
        if (showNotificationsSheet) {
            PreferencesHelper.markNotificationsRead(context)
            unreadCount = 0
        }
    }

    var pendingDownloadAction by remember { mutableStateOf<(() -> Unit)?>(null) }
    val storagePermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission(),
        onResult = { isGranted ->
            if (isGranted) {
                pendingDownloadAction?.invoke()
                pendingDownloadAction = null
            } else {
                android.widget.Toast.makeText(context, "Storage permission is required to download on this device.", android.widget.Toast.LENGTH_LONG).show()
            }
        }
    )

    val notificationPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission(),
        onResult = { isGranted ->
            if (isGranted) {
                Toast.makeText(context, "Notifications enabled!", Toast.LENGTH_SHORT).show()
            }
        }
    )

    // Check clipboard for copied link on start and warm up backend
    LaunchedEffect(Unit) {
        warmUpBackend()
        try {
            val clipText = clipboardManager.getText()?.text?.toString()?.trim()
            if (!clipText.isNullOrEmpty() && (clipText.startsWith("http://") || clipText.startsWith("https://")) && clipText != url) {
                detectedClipboardUrl = clipText
            }
        } catch (_: Exception) {}

        // Periodic background keep-alive ping every 3 minutes
        while (true) {
            kotlinx.coroutines.delay(180_000L)
            warmUpBackend()
        }
    }

    // Handle incoming shared URL from Share Sheet, Widget, or Shortcut
    LaunchedEffect(incomingSharedUrl) {
        if (!incomingSharedUrl.isNullOrEmpty()) {
            val sharedUrl = incomingSharedUrl
            onSharedUrlConsumed()
            url = sharedUrl
            Toast.makeText(context, "⚡ Link received! Extracting automatically...", Toast.LENGTH_SHORT).show()
            coroutineScope.launch {
                extractionProgress = 0f
                isDownloading = true
                result = null
                previewThumbnailUrl = null
                previewTitle = null

                try {
                    val extResult = kotlinx.coroutines.withTimeoutOrNull(60000L) {
                        extractWithCobalt(sharedUrl)
                    } ?: getFallbackResult(sharedUrl)
                    val pThumb = extResult.thumbnailUrl.ifEmpty { previewThumbnailUrl ?: "" }
                    if (pThumb.isNotEmpty()) {
                        try {
                            val request = coil.request.ImageRequest.Builder(context)
                                .data(pThumb)
                                .build()
                            withContext(Dispatchers.IO) { context.imageLoader.execute(request) }
                        } catch (_: Exception) {}
                    }
                    result = extResult
                } catch (e: Exception) {
                    result = getFallbackResult(sharedUrl)
                } finally {
                    extractionProgress = 1.0f
                    kotlinx.coroutines.delay(400L)
                    isDownloading = false
                    extractionProgress = 0f
                }
            }
        }
    }

    LaunchedEffect(showHistory) {
        if (showHistory) {
            historyList.value = PreferencesHelper.getHistory(context)
        }
    }

    val textColor = if (isDarkMode) Color.White else Color(0xFF0F172A)
    val subTextColor = if (isDarkMode) Color.White.copy(alpha = 0.65f) else Color(0xFF475569)
    val glassBg = if (isDarkMode) Color.White.copy(alpha = 0.08f) else Color.White.copy(alpha = 0.85f)
    val glassBorder = if (isDarkMode) Color.White.copy(alpha = 0.12f) else Color(0xFFE2E8F0)

    val infiniteTransition = rememberInfiniteTransition(label = "flow")
    val flowX by infiniteTransition.animateFloat(
        initialValue = -1f,
        targetValue = 2f,
        animationSpec = infiniteRepeatable(
            animation = tween(1500, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "flow_x"
    )

    Box(modifier = Modifier.fillMaxSize()) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
        Column(modifier = Modifier.widthIn(max = 600.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            // Header
            Row(
                modifier = Modifier.fillMaxWidth().padding(vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Filled.Menu, null, tint = textColor, modifier = Modifier.size(28.dp))
                    Spacer(modifier = Modifier.width(16.dp))
                    Image(painter = painterResource(id = R.drawable.app_logo), contentDescription = "App Logo", modifier = Modifier.size(40.dp).clip(RoundedCornerShape(12.dp)), contentScale = ContentScale.Fit)
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text("AURA", color = textColor, fontWeight = FontWeight.Black, style = MaterialTheme.typography.titleMedium, letterSpacing = 1.sp)
                        Text("DOWNLOADER", color = textColor, fontWeight = FontWeight.SemiBold, style = MaterialTheme.typography.labelSmall, letterSpacing = 1.sp)
                    }
                }
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    IconButton(
                        onClick = { showNotificationsSheet = true },
                        modifier = Modifier.clip(CircleShape).background(glassBg).border(1.dp, glassBorder, CircleShape)
                    ) {
                        BadgedBox(
                            badge = {
                                if (unreadCount > 0) {
                                    Badge(containerColor = Color(0xFFEF4444)) {
                                        Text(unreadCount.toString(), color = Color.White, style = MaterialTheme.typography.labelSmall)
                                    }
                                }
                            }
                        ) {
                            Icon(Icons.Filled.Notifications, "Notifications", tint = textColor, modifier = Modifier.size(20.dp))
                        }
                    }
                    IconButton(
                        onClick = onToggleDarkMode,
                        modifier = Modifier.clip(CircleShape).background(glassBg).border(1.dp, glassBorder, CircleShape)
                    ) {
                        Icon(if (isDarkMode) Icons.Filled.WbSunny else Icons.Filled.DarkMode, null, tint = if (isDarkMode) Color(0xFFFFD700) else Color(0xFF475569))
                    }
                }
            }
        }

            Spacer(modifier = Modifier.height(28.dp))
            Text("Download Videos", color = textColor, style = MaterialTheme.typography.headlineLarge, fontWeight = FontWeight.Black, textAlign = TextAlign.Center)
            Text(
                "Instantly", 
                style = MaterialTheme.typography.headlineLarge.copy(
                    brush = Brush.linearGradient(listOf(Color(0xFFFCA5A5), Color(0xFF3B82F6)))
                ), 
                fontWeight = FontWeight.Black, 
                textAlign = TextAlign.Center
            )
            Spacer(modifier = Modifier.height(12.dp))
            Text("Paste link and save high quality media\nfrom your favorite platforms", color = subTextColor, style = MaterialTheme.typography.bodyMedium, textAlign = TextAlign.Center)
            Spacer(modifier = Modifier.height(28.dp))

            // Main URL Input Bar
            Box(
                modifier = Modifier.fillMaxWidth().height(60.dp).clip(RoundedCornerShape(30.dp)).background(glassBg).border(1.dp, glassBorder, RoundedCornerShape(30.dp)).padding(horizontal = 8.dp),
                contentAlignment = Alignment.CenterStart
            ) {
                Row(modifier = Modifier.fillMaxSize(), verticalAlignment = Alignment.CenterVertically) {
                    Spacer(modifier = Modifier.width(8.dp))
                    Icon(Icons.Filled.Link, null, tint = subTextColor)
                    Spacer(modifier = Modifier.width(12.dp))
                    Box(modifier = Modifier.weight(1f)) {
                        if (url.isEmpty()) Text("Paste video URL here...", color = subTextColor, style = MaterialTheme.typography.bodyLarge, maxLines = 1, overflow = TextOverflow.Ellipsis)
                        BasicTextField(value = url, onValueChange = { url = it; if (it.length > 5) warmUpBackend() }, textStyle = MaterialTheme.typography.bodyLarge.copy(color = textColor), singleLine = true, modifier = Modifier.fillMaxWidth())
                    }
                    if (url.isNotEmpty()) IconButton(onClick = { url = ""; result = null; extractionProgress = 0f }) { Icon(Icons.Filled.Clear, "Clear", tint = subTextColor) }

                    else {

                        IconButton(onClick = { clipboardManager.getText()?.text?.let { url = it; result = null; extractionProgress = 0f; if (it.length > 5) warmUpBackend() } }, modifier = Modifier.clip(RoundedCornerShape(16.dp)).background(Color.White.copy(0.15f)).size(44.dp)) {
                            Icon(Icons.Filled.ContentPaste, null, tint = textColor, modifier = Modifier.size(20.dp))
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(12.dp))
            AnimatedVisibility(visible = detectedClipboardUrl != null && url.isEmpty()) {
                Surface(
                    onClick = {
                        detectedClipboardUrl?.let { link ->
                            url = link
                            detectedClipboardUrl = null
                            Toast.makeText(context, "⚡ Link pasted! Extracting...", Toast.LENGTH_SHORT).show()
                            coroutineScope.launch {
                                extractionProgress = 0f
                                isDownloading = true
                                result = null
                                previewThumbnailUrl = null
                                previewTitle = null
                                

                                try {
                                    val extResult = kotlinx.coroutines.withTimeoutOrNull(60000L) {
                                        extractWithCobalt(link)
                                    } ?: getFallbackResult(link)
                                    val pThumb = extResult.thumbnailUrl.ifEmpty { previewThumbnailUrl ?: "" }
                                    if (pThumb.isNotEmpty()) {
                                        try {
                                            val request = coil.request.ImageRequest.Builder(context)
                                                .data(pThumb)
                                                .build()
                                            withContext(Dispatchers.IO) { context.imageLoader.execute(request) }
                                        } catch (_: Exception) {}
                                    }
                                    result = extResult
                                } catch (e: Exception) {
                                    result = getFallbackResult(link)
                                } finally {
                                    extractionProgress = 1.0f
                                    kotlinx.coroutines.delay(400L)
                                    isDownloading = false
                                    extractionProgress = 0f
                                }
                            }
                        }
                    },
                    shape = RoundedCornerShape(16.dp),
                    color = Color(0xFF1E293B),
                    border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF38BDF8).copy(alpha = 0.5f)),
                    modifier = Modifier.fillMaxWidth().padding(top = 12.dp)
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.weight(1f)) {
                            Icon(Icons.Filled.FlashOn, null, tint = Color(0xFF38BDF8), modifier = Modifier.size(20.dp))
                            Spacer(modifier = Modifier.width(10.dp))
                            Column {
                                Text("Copied Link Detected", color = Color.White, style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.Bold)
                                Text(detectedClipboardUrl ?: "", color = Color.White.copy(alpha = 0.7f), style = MaterialTheme.typography.bodySmall, maxLines = 1, overflow = TextOverflow.Ellipsis)
                            }
                        }
                        Text("Auto-Download >", color = Color(0xFF38BDF8), style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold)
                    }
                }
            }

            Spacer(modifier = Modifier.height(24.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Text("Popular Platforms", color = textColor, style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("View all", color = subTextColor, style = MaterialTheme.typography.labelMedium)
                    Icon(Icons.Filled.ChevronRight, null, tint = subTextColor, modifier = Modifier.size(16.dp))
                }
            }
            Spacer(modifier = Modifier.height(16.dp))

            LazyRow(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(14.dp)) {
                items(Platform.entries.toTypedArray()) { platform ->
                    val isSelected = platform == selectedPlatform
                    Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.clickable { onPlatformSelected(platform) }) {
                        val shadowElevation = if (isSelected) 16.dp else 0.dp
                        Box(
                            modifier = Modifier
                                .size(64.dp)
                                .shadow(shadowElevation, RoundedCornerShape(16.dp), ambientColor = platform.brandColor, spotColor = platform.brandColor)
                                .clip(RoundedCornerShape(16.dp))
                                .background(if (isSelected) platform.brandColor.copy(0.15f) else glassBg)
                                .border(1.dp, if (isSelected) platform.brandColor.copy(0.5f) else glassBorder, RoundedCornerShape(16.dp)),
                            contentAlignment = Alignment.Center
                        ) {
                            Platform3DIcon(platform = platform, modifier = Modifier.size(40.dp), isDarkMode = isDarkMode)
                        }
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(platform.displayName.split(" ")[0], color = if (isSelected) textColor else subTextColor, style = MaterialTheme.typography.labelSmall, fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal)
                    }
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            // Features Row
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                @Composable
                fun FeatureCard(icon: androidx.compose.ui.graphics.vector.ImageVector, title: String, desc: String, tint: Color, modifier: Modifier) {
                    Box(modifier = modifier.clip(RoundedCornerShape(16.dp)).background(glassBg).border(1.dp, glassBorder, RoundedCornerShape(16.dp)).padding(12.dp)) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.fillMaxWidth()) {
                            Icon(icon, null, tint = tint, modifier = Modifier.size(24.dp))
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(title, color = textColor, style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center)
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(desc, color = subTextColor, style = MaterialTheme.typography.labelSmall, textAlign = TextAlign.Center, lineHeight = 14.sp)
                        }
                    }
                }
                
                FeatureCard(Icons.Filled.VerifiedUser, "High Quality", "Best available\nquality", Color(0xFF3B82F6), Modifier.weight(1f))
                FeatureCard(Icons.Filled.FlashOn, "Fast Download", "Lightning fast\ndownloads", Color(0xFF10B981), Modifier.weight(1f))
                FeatureCard(Icons.Filled.Lock, "100% Secure", "Your data is safe\nwith us", Color(0xFFF59E0B), Modifier.weight(1f))
            }
            
            Spacer(modifier = Modifier.height(24.dp))

            Button(
                onClick = {
                    if (url.isNotEmpty()) {
                        coroutineScope.launch {
                            extractionProgress = 0f
                            MusicController.reset()
                            isDownloading = true
                            result = null
                            previewThumbnailUrl = null
                            previewTitle = null
                            
                            try {
                                val extResult = kotlinx.coroutines.withTimeoutOrNull(60000L) {
                                    extractWithCobalt(url)
                                } ?: getFallbackResult(url)
                                val pThumb = extResult.thumbnailUrl.ifEmpty { previewThumbnailUrl ?: "" }
                                if (pThumb.isNotEmpty()) {
                                    try {
                                        val request = coil.request.ImageRequest.Builder(context)
                                            .data(pThumb)
                                            .build()
                                        withContext(Dispatchers.IO) { context.imageLoader.execute(request) }
                                    } catch (_: Exception) {}
                                }
                                result = extResult
                                if (!extResult.success) {
                                    MusicController.onExtractionFailed()
                                }
                            } catch (e: Exception) {
                                val fb = getFallbackResult(url)
                                result = fb
                                if (!fb.success) {
                                    MusicController.onExtractionFailed()
                                }
                            } finally {
                                extractionProgress = 1.0f
                                kotlinx.coroutines.delay(400L)
                                isDownloading = false
                                extractionProgress = 0f
                            }
                        }
                    }
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp)
                    .neumorphic(isLightMode = !isDarkMode, cornerRadius = 16.dp)
                    .clip(RoundedCornerShape(16.dp))
                    .background(if (isDarkMode) Color.Black.copy(alpha = 0.6f) else Color(0xFF0F172A))
                    .border(
                        1.dp,
                        if (isDarkMode) Color.White.copy(alpha = 0.2f) else Color(0xFF334155),
                        RoundedCornerShape(16.dp)
                    ),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color.Transparent,
                    contentColor = Color.White
                ),
                elevation = ButtonDefaults.buttonElevation(defaultElevation = 0.dp),
                enabled = !isDownloading
            ) {
                Row(
                    modifier = Modifier.fillMaxSize(),
                    horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    if (isDownloading) {
                        CircularProgressIndicator(modifier = Modifier.size(20.dp), color = Color.White, strokeWidth = 2.dp)
                        Spacer(modifier = Modifier.width(10.dp))
                        Text(
                            "Extracting...",
                            fontWeight = FontWeight.Bold,
                            color = Color.White,
                            style = MaterialTheme.typography.titleMedium
                        )
                    } else {
                        Icon(Icons.Filled.Download, contentDescription = null, tint = Color.White)
                        Spacer(modifier = Modifier.width(10.dp))
                        Text(
                            "Download Now",
                            fontWeight = FontWeight.Bold,
                            color = Color.White,
                            style = MaterialTheme.typography.titleMedium
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Recent Downloads
            Box(modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(16.dp)).background(glassBg).border(1.dp, glassBorder, RoundedCornerShape(16.dp)).clickable { showHistory = true }.padding(16.dp)) {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(modifier = Modifier.size(40.dp).clip(RoundedCornerShape(12.dp)).background(Color.White.copy(0.05f)), contentAlignment = Alignment.Center) {
                            Icon(Icons.Filled.AccessTime, null, tint = Color(0xFF10B981))
                        }
                        Spacer(modifier = Modifier.width(12.dp))
                        Column {
                            Text("Recent Downloads", color = textColor, style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.Bold)
                            Spacer(modifier = Modifier.height(2.dp))
                            Text("See your download history", color = subTextColor, style = MaterialTheme.typography.labelSmall)
                        }
                    }
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text("View History", color = textColor, style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Medium)
                        Spacer(modifier = Modifier.width(4.dp))
                        Icon(Icons.Filled.ChevronRight, null, tint = textColor, modifier = Modifier.size(16.dp))
                    }
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            AnimatedVisibility(
                visible = isDownloading,
                enter = slideInVertically { 40 } + fadeIn(),
                exit = slideOutVertically { -40 } + fadeOut()
            ) {
                val statusMsg = when {
                    extractionProgress < 0.30f -> "Initializing..."
                    extractionProgress < 0.70f -> "Extracting data..."
                    else -> "Finalizing..."
                }
                SkeletonLoader(
                    isDarkMode = isDarkMode,
                    progress = extractionProgress,
                    statusText = statusMsg,
                    previewThumbnailUrl = previewThumbnailUrl,
                    previewTitle = previewTitle
                )
            }

            androidx.compose.animation.AnimatedVisibility(
                visible = result != null && !isDownloading,
                enter = androidx.compose.animation.expandVertically() + androidx.compose.animation.fadeIn(),
                exit = androidx.compose.animation.shrinkVertically() + androidx.compose.animation.fadeOut()
            ) {
                result?.let { r ->
                    if (r.success) {
                    var selectedPlaylistTrack by remember(r) { mutableStateOf<SpotifyTrack?>(null) }
                    // Result UI
                    Box(
                        modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(16.dp)).background(glassBg).border(1.dp, glassBorder, RoundedCornerShape(16.dp)).padding(16.dp)
                    ) {
                        Column {
                            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.background(Color(0xFF22C55E).copy(alpha = 0.15f), RoundedCornerShape(8.dp)).padding(horizontal = 12.dp, vertical = 6.dp)) {
                                Icon(Icons.Filled.CheckCircle, null, tint = Color(0xFF22C55E), modifier = Modifier.size(16.dp))
                                Spacer(modifier = Modifier.width(6.dp))
                                Text("Extraction Successful", color = Color(0xFF22C55E), fontWeight = FontWeight.Bold, style = MaterialTheme.typography.labelSmall)
                            }
                            Spacer(modifier = Modifier.height(16.dp))

                            val finalThumbnail = r.thumbnailUrl.ifEmpty { previewThumbnailUrl ?: "" }
                            
                            val defaultAudioToPlay = if (!r.previewAudioUrl.isNullOrEmpty()) r.previewAudioUrl else {
                                r.qualities.firstOrNull { q -> q.label.contains("MP3", true) || q.label.contains("Audio", true) }?.url
                            }
                            val activeAudioToPlay = if (r.isSpotify || r.mediaType == "audio") {
                                selectedPlaylistTrack?.resolveUrl ?: selectedPlaylistTrack?.directAudioUrl ?: defaultAudioToPlay
                            } else null

                            if (activeAudioToPlay.isNullOrEmpty()) {
                                if (finalThumbnail.isNotEmpty()) {
                                    Box(
                                        modifier = Modifier.fillMaxWidth().aspectRatio(16f/9f).clip(RoundedCornerShape(12.dp)).background(if (isDarkMode) Color.DarkGray.copy(0.5f) else Color.LightGray.copy(0.5f)),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        Icon(Icons.Filled.Image, contentDescription = null, tint = subTextColor, modifier = Modifier.size(48.dp))
                                        AsyncImage(
                                            model = coil.request.ImageRequest.Builder(context).data(finalThumbnail).build(),
                                            contentDescription = "Thumbnail",
                                            contentScale = ContentScale.Crop,
                                            modifier = Modifier.fillMaxSize()
                                        )
                                        if (r.isSpotify || r.mediaType == "audio") {
                                            Box(
                                                modifier = Modifier
                                                    .align(Alignment.TopEnd)
                                                    .padding(8.dp)
                                                    .background(if (r.isSpotify) Color(0xFF1DB954) else Color(0xFF3B82F6), RoundedCornerShape(20.dp))
                                                    .padding(horizontal = 10.dp, vertical = 4.dp)
                                            ) {
                                                Row(verticalAlignment = Alignment.CenterVertically) {
                                                    Icon(Icons.Filled.Audiotrack, contentDescription = null, tint = Color.White, modifier = Modifier.size(12.dp))
                                                    Spacer(modifier = Modifier.width(4.dp))
                                                    Text(
                                                        text = if (r.isSpotify) (if (r.isPlaylist) "Spotify Playlist" else "Spotify Track") else "Audio File",
                                                        color = Color.White,
                                                        fontWeight = FontWeight.Bold,
                                                        style = MaterialTheme.typography.labelSmall
                                                    )
                                                }
                                            }
                                        }
                                    }
                                    Spacer(modifier = Modifier.height(16.dp))
                                }

                                Text(text = r.title, color = textColor, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, maxLines = 2, overflow = TextOverflow.Ellipsis)
                                if (!r.artistName.isNullOrEmpty()) {
                                    Spacer(modifier = Modifier.height(4.dp))
                                    Text(text = r.artistName, color = subTextColor, style = MaterialTheme.typography.bodyMedium, maxLines = 1, overflow = TextOverflow.Ellipsis)
                                }
                                Spacer(modifier = Modifier.height(16.dp))
                            } else {
                                val expectedDurationStr = selectedPlaylistTrack?.durationStr ?: r.spotifyTracks.firstOrNull()?.durationStr
                                val activeTitle = selectedPlaylistTrack?.name ?: r.title
                                val activeArtist = selectedPlaylistTrack?.artist?.ifEmpty { r.artistName } ?: r.artistName
                                val activeThumb = selectedPlaylistTrack?.thumbnailUrl?.ifEmpty { r.thumbnailUrl } ?: r.thumbnailUrl

                                SpotifyMusicPlayer(
                                    title = activeTitle,
                                    artist = activeArtist,
                                    thumbnailUrl = activeThumb,
                                    audioUrl = activeAudioToPlay,
                                    expectedDurationStr = expectedDurationStr,
                                    isDarkMode = isDarkMode,

                                    lyrics = r.lyrics
                                )
                                Spacer(modifier = Modifier.height(16.dp))
                            }

                            if (r.isSpotify && r.spotifyTracks.isNotEmpty()) {
                                Card(
                                    modifier = Modifier.fillMaxWidth(),
                                    colors = CardDefaults.cardColors(containerColor = if (isDarkMode) Color(0xFF181818) else Color(0xFFF0F0F0)),
                                    shape = RoundedCornerShape(12.dp)
                                ) {
                                    Column(modifier = Modifier.padding(12.dp)) {
                                        Row(verticalAlignment = Alignment.CenterVertically) {
                                            Icon(Icons.Filled.QueueMusic, contentDescription = null, tint = Color(0xFF1DB954), modifier = Modifier.size(20.dp))
                                            Spacer(modifier = Modifier.width(8.dp))
                                            Text(
                                                text = if (r.isPlaylist) "Playlist Tracks (${r.spotifyTracks.size} Songs)" else "Track Information",
                                                fontWeight = FontWeight.Bold,
                                                color = textColor,
                                                style = MaterialTheme.typography.titleSmall
                                            )
                                        }
                                        Spacer(modifier = Modifier.height(8.dp))
                                        r.spotifyTracks.take(20).forEach { track ->
                                            Column {
                                                Row(
                                                    modifier = Modifier
                                                        .fillMaxWidth()
                                                        .padding(vertical = 6.dp),
                                                    horizontalArrangement = Arrangement.SpaceBetween,
                                                    verticalAlignment = Alignment.CenterVertically
                                                ) {
                                                    Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.weight(1f)) {
                                                        Text(
                                                            text = "#${track.trackNumber}",
                                                            color = Color(0xFF1DB954),
                                                            fontWeight = FontWeight.Bold,
                                                            style = MaterialTheme.typography.labelMedium
                                                        )
                                                        Spacer(modifier = Modifier.width(8.dp))
                                                        Column {
                                                            Text(
                                                                text = track.name,
                                                                color = textColor,
                                                                fontWeight = FontWeight.SemiBold,
                                                                style = MaterialTheme.typography.bodyMedium,
                                                                maxLines = 1,
                                                                overflow = TextOverflow.Ellipsis
                                                            )
                                                            if (track.artist.isNotEmpty()) {
                                                                Text(
                                                                    text = track.artist,
                                                                    color = subTextColor,
                                                                    style = MaterialTheme.typography.bodySmall,
                                                                    maxLines = 1,
                                                                    overflow = TextOverflow.Ellipsis
                                                                )
                                                            }
                                                        }
                                                    }
                                                    if (!track.durationStr.isNullOrEmpty()) {
                                                        Text(
                                                            text = track.durationStr,
                                                            color = subTextColor,
                                                            style = MaterialTheme.typography.bodySmall,
                                                            fontWeight = FontWeight.Medium
                                                        )
                                                    }
                                                }
                                                HorizontalDivider(color = glassBorder.copy(alpha = 0.2f))
                                            }
                                        }
                                        if (r.spotifyTracks.size > 20) {
                                            Spacer(modifier = Modifier.height(6.dp))
                                            Text(
                                                text = "+ ${r.spotifyTracks.size - 20} more tracks included in ZIP package",
                                                color = subTextColor,
                                                style = MaterialTheme.typography.bodySmall
                                            )
                                        }
                                    }
                                }
                                Spacer(modifier = Modifier.height(16.dp))
                            }

                            if (r.carouselItems.isNotEmpty()) {
                                Text("Carousel Media (${r.carouselItems.size} items)", fontWeight = FontWeight.Bold, color = textColor, style = MaterialTheme.typography.titleSmall)
                                Spacer(modifier = Modifier.height(8.dp))
                                androidx.compose.foundation.lazy.LazyRow(
                                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                                    contentPadding = PaddingValues(bottom = 8.dp)
                                ) {
                                    items(r.carouselItems.size) { index ->
                                        val item = r.carouselItems[index]
                                        Card(
                                            shape = RoundedCornerShape(12.dp),
                                            modifier = Modifier.width(140.dp)
                                        ) {
                                            Column {
                                                Box(modifier = Modifier.fillMaxWidth().aspectRatio(1f).background(Color.Black)) {
                                                    val thumbUrl = if (!item.thumbnail.isNullOrEmpty()) item.thumbnail else item.url
                                                    AsyncImage(
                                                        model = coil.request.ImageRequest.Builder(context).data(thumbUrl).build(),
                                                        contentDescription = null,
                                                        contentScale = ContentScale.Crop,
                                                        modifier = Modifier.fillMaxSize()
                                                    )
                                                    if (item.type == "video") {
                                                        Box(modifier = Modifier.align(Alignment.TopEnd).padding(4.dp).background(Color.Black.copy(0.6f), RoundedCornerShape(4.dp)).padding(4.dp)) {
                                                            Icon(Icons.Filled.PlayArrow, contentDescription = null, tint = Color.White, modifier = Modifier.size(16.dp))
                                                        }
                                                    }
                                                }
                                                    TextButton(
                                                    onClick = {
                                                        val action = {
                                                            val q = MediaQuality(if (item.type == "video") "Download Video" else "Download Image", null, item.url)
                                                            resolveAndTriggerDownload(context, coroutineScope, q, r.title, item.thumbnail ?: "") { id -> activeDownloadId = id }
                                                        }
                                                        if (android.os.Build.VERSION.SDK_INT <= 28 && androidx.core.content.ContextCompat.checkSelfPermission(context, android.Manifest.permission.WRITE_EXTERNAL_STORAGE) != android.content.pm.PackageManager.PERMISSION_GRANTED) {
                                                            pendingDownloadAction = action
                                                            storagePermissionLauncher.launch(android.Manifest.permission.WRITE_EXTERNAL_STORAGE)
                                                        } else {
                                                            action()
                                                        }
                                                    },
                                                    modifier = Modifier.fillMaxWidth().height(36.dp),
                                                    shape = RoundedCornerShape(0.dp, 0.dp, 12.dp, 12.dp),
                                                    contentPadding = PaddingValues(0.dp)
                                                ) {
                                                    Text("Download", style = MaterialTheme.typography.labelSmall)
                                                }
                                            }
                                        }
                                    }
                                }
                                Spacer(modifier = Modifier.height(16.dp))
                            }

                            if (r.qualities.isNotEmpty()) {
                                Text("Available Downloads:", color = subTextColor, style = MaterialTheme.typography.labelMedium)
                            } else if (r.carouselItems.isEmpty()) {
                                Text("No downloads found for this link.", color = subTextColor, style = MaterialTheme.typography.labelMedium)
                            }
                            Spacer(modifier = Modifier.height(8.dp))

                            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                r.qualities.forEach { q ->
                                    val isZip = q.label.contains("zip", true)
                                    Button(
                                        onClick = {
                                            val action = {
                                                resolveAndTriggerDownload(
                                                    context = context,
                                                    coroutineScope = coroutineScope,
                                                    q = q,
                                                    title = r.title,
                                                    thumbnailUrl = r.thumbnailUrl
                                                )
                                            }
                                            if (android.os.Build.VERSION.SDK_INT <= 28 && androidx.core.content.ContextCompat.checkSelfPermission(context, android.Manifest.permission.WRITE_EXTERNAL_STORAGE) != android.content.pm.PackageManager.PERMISSION_GRANTED) {
                                                pendingDownloadAction = action
                                                storagePermissionLauncher.launch(android.Manifest.permission.WRITE_EXTERNAL_STORAGE)
                                            } else {
                                                action()
                                            }
                                        },
                                        modifier = Modifier.fillMaxWidth().height(48.dp).neumorphic(isLightMode = !isDarkMode, cornerRadius = 12.dp, elevation = 4.dp),
                                        shape = RoundedCornerShape(12.dp),
                                        colors = ButtonDefaults.buttonColors(
                                            containerColor = if (isZip) Color(0xFF1DB954) else if (isDarkMode) Color.White.copy(0.1f) else Color.White,
                                            contentColor = if (isZip) Color.White else textColor
                                        ),
                                        border = if (isZip) null else androidx.compose.foundation.BorderStroke(1.dp, glassBorder)
                                    ) {
                                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                                            Row(verticalAlignment = Alignment.CenterVertically) {
                                                val iconVector = when {
                                                    isZip -> Icons.Filled.FolderZip
                                                    q.label.contains("Audio", true) || q.label.contains("mp3", true) -> Icons.Filled.Audiotrack
                                                    q.label.contains("Thumbnail", true) || q.label.contains("jpg", true) -> Icons.Filled.Image
                                                    else -> Icons.Filled.VideoFile
                                                }
                                                Icon(iconVector, null, modifier = Modifier.size(18.dp), tint = if (isZip) Color.White else selectedPlatform.brandColor)
                                                Spacer(modifier = Modifier.width(8.dp))
                                                Text(q.label, fontWeight = FontWeight.Bold)
                                            }
                                            Row(verticalAlignment = Alignment.CenterVertically) {
                                                if (q.size != null) {
                                                    Text(q.size, color = if (isZip) Color.White.copy(0.8f) else subTextColor, style = MaterialTheme.typography.bodySmall)
                                                    Spacer(modifier = Modifier.width(8.dp))
                                                }
                                                Icon(Icons.Filled.Download, "Download", modifier = Modifier.size(16.dp), tint = if (isZip) Color.White else subTextColor)
                                            }
                                        }
                                    }
                                }
                            }
                            
                            if (r.lyrics != null) {
                                Spacer(modifier = Modifier.height(16.dp))
                                Button(
                                    onClick = { showLyrics = r.lyrics },
                                    modifier = Modifier.fillMaxWidth().height(48.dp).neumorphic(isLightMode = !isDarkMode, cornerRadius = 12.dp, elevation = 4.dp),
                                    shape = RoundedCornerShape(12.dp),
                                    colors = ButtonDefaults.buttonColors(
                                        containerColor = selectedPlatform.brandColor.copy(alpha = 0.15f),
                                        contentColor = selectedPlatform.brandColor
                                    ),
                                    elevation = ButtonDefaults.buttonElevation(defaultElevation = 0.dp)
                                ) {
                                    Row(verticalAlignment = Alignment.CenterVertically) {
                                        Icon(Icons.Filled.MusicNote, contentDescription = null, modifier = Modifier.size(18.dp))
                                        Spacer(modifier = Modifier.width(8.dp))
                                        Text("View Lyrics", fontWeight = FontWeight.Bold)
                                    }
                                }
                            }
                        }
                    }
                } else {
                    // Error UI
                    Box(
                        modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(16.dp)).background(Color(0xFFFF0000).copy(alpha = 0.1f)).border(1.dp, Color(0xFFFF0000).copy(alpha = 0.3f), RoundedCornerShape(16.dp)).padding(16.dp)
                    ) {
                        Column {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Filled.Error, null, tint = Color(0xFFFF4D4D), modifier = Modifier.size(24.dp))
                                Spacer(modifier = Modifier.width(8.dp))
                                Text("Extraction Failed", color = Color(0xFFFF4D4D), fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
                            }
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(text = r.error ?: "An unknown error occurred.", color = textColor, style = MaterialTheme.typography.bodyMedium)
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(100.dp))
        }
    }
        
    AnimatedVisibility(
        visible = isActualDownloading,
        enter = slideInVertically { it } + fadeIn(),
        exit = slideOutVertically { it } + fadeOut(),
        modifier = Modifier
            .align(Alignment.BottomCenter)
            .padding(0.dp, 0.dp, 0.dp, 24.dp)
    ) {
        FloatingDownloadProgress(progress = (actualDownloadProgress ?: 0) / 100f)
    }
    
    if (showSuccessAnimation) {
        Box(modifier = Modifier.fillMaxSize().zIndex(100f).background(Color.Black.copy(alpha = 0.5f)), contentAlignment = Alignment.Center) {
            val composition by rememberLottieComposition(LottieCompositionSpec.RawRes(com.auradownloader.app.R.raw.success_anim))
            LottieAnimation(
                composition = composition,
                iterations = 1,
                modifier = Modifier.size(200.dp)
            )
        }
        LaunchedEffect(Unit) {
            kotlinx.coroutines.delay(2000)
            showSuccessAnimation = false
        }
    }

    if (showHistory) {
        androidx.compose.material3.ModalBottomSheet(
            onDismissRequest = { showHistory = false },
            containerColor = if (isDarkMode) Color(0xFF0F172A) else Color.White
        ) {
            Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
                Text("Recent Downloads", color = textColor, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(16.dp))
                if (historyList.value.isEmpty()) {
                    Text("No recent downloads.", color = subTextColor, modifier = Modifier.padding(16.dp))
                } else {
                    androidx.compose.foundation.lazy.LazyColumn {
                        items(historyList.value.size) { i ->
                            val item = historyList.value[i]
                            Row(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                                Box(modifier = Modifier.size(60.dp).clip(RoundedCornerShape(8.dp)).background(glassBorder)) {
                                    val thumb = item.optString("thumbnailUrl")
                                    if (thumb.isNotEmpty()) {
                                        AsyncImage(
                                            model = coil.request.ImageRequest.Builder(context).data(thumb).build(),
                                            contentDescription = "Thumbnail",
                                            contentScale = ContentScale.Crop,
                                            modifier = Modifier.fillMaxSize()
                                        )
                                    } else {
                                        Icon(Icons.Filled.VideoFile, null, modifier = Modifier.align(Alignment.Center), tint = subTextColor)
                                    }
                                }
                                Spacer(modifier = Modifier.width(16.dp))
                                Column {
                                    Text(item.optString("title"), color = textColor, fontWeight = FontWeight.SemiBold, maxLines = 1, overflow = TextOverflow.Ellipsis)
                                    Text("Downloaded", color = Color(0xFF22C55E), style = MaterialTheme.typography.bodySmall)
                                }
                            }
                        }
                    }
                }
                Spacer(modifier = Modifier.height(32.dp))
            }
        }
    }

    if (showNotificationsSheet) {
        androidx.compose.material3.ModalBottomSheet(
            onDismissRequest = { showNotificationsSheet = false },
            containerColor = if (isDarkMode) Color(0xFF18181B) else Color.White
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(24.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Filled.NotificationsActive, null, tint = Color(0xFF38BDF8))
                        Spacer(modifier = Modifier.width(10.dp))
                        Text("Notifications & Alerts", color = textColor, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    }
                        Icon(Icons.Filled.Close, "Close", tint = subTextColor)
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                val hasNotificationPermission = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                    ContextCompat.checkSelfPermission(context, Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED
                } else true

                if (!hasNotificationPermission && Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                    Card(
                        colors = CardDefaults.cardColors(containerColor = Color(0xFF3B82F6).copy(alpha = 0.15f)),
                        shape = RoundedCornerShape(12.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Row(
                            modifier = Modifier.padding(12.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text("Notifications Permission", color = textColor, style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.Bold)
                                Text("Enable push alerts for video extraction completion.", color = subTextColor, style = MaterialTheme.typography.bodySmall)
                            }
                            Button(
                                onClick = {
                                    notificationPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
                                },
                                contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp)
                            ) {
                                Text("Allow", fontSize = 12.sp)
                            }
                        }
                    }
                    Spacer(modifier = Modifier.height(16.dp))
                }

                Text("Notifications", color = subTextColor, style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(8.dp))

                if (notificationsList.value.isEmpty()) {
                    Box(modifier = Modifier.fillMaxWidth().padding(32.dp), contentAlignment = Alignment.Center) {
                        Text("No notifications yet.", color = subTextColor, style = MaterialTheme.typography.bodyMedium)
                    }
                } else {
                    notificationsList.value.forEach { alert ->
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 6.dp)
                                .clip(RoundedCornerShape(12.dp))
                                .background(glassBg)
                                .padding(12.dp)
                        ) {
                            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                Text(alert.optString("message", ""), color = textColor, style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold)
                                Text(alert.optString("timeDesc", ""), color = subTextColor, style = MaterialTheme.typography.labelSmall)
                            }
                        }
                    }
                }

                Spacer(modifier = Modifier.height(32.dp))
            }
        }
    }

    if (showLyrics != null) {
        androidx.compose.material3.ModalBottomSheet(
            onDismissRequest = { showLyrics = null },
            containerColor = if (isDarkMode) Color(0xFF18181B) else Color.White
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(24.dp)
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Filled.MusicNote, null, tint = selectedPlatform.brandColor)
                    Spacer(modifier = Modifier.width(10.dp))
                    Text("Lyrics", color = textColor, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                }
                Spacer(modifier = Modifier.height(16.dp))
                val playbackState by MusicController.playbackState.collectAsState()
                var bottomSheetOffsetMs by remember(showLyrics) { mutableLongStateOf(0L) }
                SyncedLyricsView(
                    lyrics = showLyrics ?: "",
                    currentPositionMs = playbackState.positionMs.toLong(),
                    offsetMs = bottomSheetOffsetMs,
                    onOffsetChange = { bottomSheetOffsetMs = it },
                    activeColor = selectedPlatform.brandColor,
                    textColor = textColor
                )
            }
        }
    }
}

@Composable
fun PlatformsScreen(isDarkMode: Boolean, onSelectPlatform: (Platform) -> Unit) {
    val textColor = if (isDarkMode) Color.White else Color(0xFF0F172A)
    val subTextColor = if (isDarkMode) Color.White.copy(alpha = 0.65f) else Color(0xFF475569)
    val glassBg = if (isDarkMode) Color.White.copy(alpha = 0.08f) else Color.White.copy(alpha = 0.85f)
    val glassBorder = if (isDarkMode) Color.White.copy(alpha = 0.12f) else Color(0xFFE2E8F0)

    Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Column(modifier = Modifier.widthIn(max = 600.dp)) {
            Spacer(modifier = Modifier.height(16.dp))
            Text("Supported Platforms", color = textColor, style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(8.dp))
            Text("Download videos and audio from all major platforms in original quality.", color = subTextColor, style = MaterialTheme.typography.bodyMedium)
            Spacer(modifier = Modifier.height(20.dp))
            LazyVerticalGrid(columns = GridCells.Fixed(2), horizontalArrangement = Arrangement.spacedBy(12.dp), verticalArrangement = Arrangement.spacedBy(12.dp), modifier = Modifier.fillMaxWidth(), contentPadding = PaddingValues(bottom = 100.dp)) {
                items(Platform.entries.toTypedArray()) { platform ->
                    Card(modifier = Modifier.fillMaxWidth().clickable { onSelectPlatform(platform) }, colors = CardDefaults.cardColors(containerColor = glassBg), shape = RoundedCornerShape(24.dp), border = androidx.compose.foundation.BorderStroke(1.dp, glassBorder)) {
                        Column(modifier = Modifier.fillMaxWidth().padding(18.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
                            Platform3DIcon(platform = platform, modifier = Modifier.size(60.dp), isDarkMode = isDarkMode)
                            Spacer(modifier = Modifier.height(12.dp))
                            Text(platform.displayName, color = textColor, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center)
                            Spacer(modifier = Modifier.height(8.dp))
                            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.background(Color(0xFF22C55E).copy(alpha = 0.15f), RoundedCornerShape(12.dp)).padding(horizontal = 8.dp, vertical = 4.dp)) {
                                Box(modifier = Modifier.size(6.dp).clip(CircleShape).background(Color(0xFF22C55E)))
                                Spacer(modifier = Modifier.width(6.dp))
                                Text("AVAILABLE", color = Color(0xFF22C55E), style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Black)
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun SettingsScreen(isDarkMode: Boolean, onToggleDarkMode: () -> Unit, onNavigate: (String) -> Unit) {
    val context = androidx.compose.ui.platform.LocalContext.current
    val textColor = if (isDarkMode) Color.White else Color(0xFF0F172A)
    val subTextColor = if (isDarkMode) Color.White.copy(alpha = 0.65f) else Color(0xFF475569)
    val glassBg = if (isDarkMode) Color.White.copy(alpha = 0.08f) else Color.White.copy(alpha = 0.85f)
    val glassBorder = if (isDarkMode) Color.White.copy(alpha = 0.12f) else Color(0xFFE2E8F0)


    Column(modifier = Modifier.fillMaxSize().padding(16.dp).verticalScroll(rememberScrollState()), horizontalAlignment = Alignment.CenterHorizontally) {
        Column(modifier = Modifier.widthIn(max = 600.dp)) {
            Spacer(modifier = Modifier.height(16.dp))
            Text("Settings", color = textColor, style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(20.dp))

            Card(modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = glassBg), shape = RoundedCornerShape(20.dp), border = androidx.compose.foundation.BorderStroke(1.dp, glassBorder)) {
                Column {
                    Row(modifier = Modifier.fillMaxWidth().clickable { onToggleDarkMode() }.padding(16.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(if (isDarkMode) Icons.Filled.WbSunny else Icons.Filled.DarkMode, null, tint = if (isDarkMode) Color(0xFFFFD700) else Color(0xFF475569))
                            Spacer(modifier = Modifier.width(16.dp))
                            Column {
                                Text(if (isDarkMode) "Light Mode" else "Dark Mode", color = textColor, fontWeight = FontWeight.SemiBold)
                                Text("Switch app theme interface", color = subTextColor, style = MaterialTheme.typography.bodySmall)
                            }
                        }
                        Switch(checked = isDarkMode, onCheckedChange = { onToggleDarkMode() }, colors = SwitchDefaults.colors(checkedThumbColor = Color.White, checkedTrackColor = Color(0xFF0066FF)))
                    }
                    HorizontalDivider(color = glassBorder)
                    Row(modifier = Modifier.fillMaxWidth().clickable { 
                        context.startActivity(Intent(Intent.ACTION_VIEW, android.net.Uri.parse("https://youtube.com/@mridulgaming-_-official-800?si=zZaB5VOE2Cj5olFl")))
                    }.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                        Box(modifier = Modifier.size(36.dp).clip(CircleShape).background(Color(0xFFFF0000)), contentAlignment = Alignment.Center) {
                            Icon(painterResource(id = R.drawable.ic_youtube), "YouTube", tint = Color.White, modifier = Modifier.size(20.dp))
                        }
                        Spacer(modifier = Modifier.width(16.dp))
                        Column {
                            Text("Support Us - Subscribe", color = textColor, fontWeight = FontWeight.Bold)
                            Text("Subscribe to our channel to support development", color = subTextColor, style = MaterialTheme.typography.bodySmall)
                        }
                    }

                    HorizontalDivider(color = glassBorder)
                    SettingItem(isDarkMode, Icons.Filled.Info, "About Aura Downloader", "Version 1.0.0") {
                        onNavigate(Screen.About.route)
                    }
                    HorizontalDivider(color = glassBorder)
                    SettingItem(isDarkMode, Icons.Filled.Policy, "Privacy Policy", "Read our privacy policy") {
                        onNavigate(Screen.PrivacyPolicy.route)
                    }
                    HorizontalDivider(color = glassBorder)
                    SettingItem(isDarkMode, Icons.Filled.Description, "Terms and Conditions", "Read our terms of service") {
                        onNavigate(Screen.Terms.route)
                    }
                    HorizontalDivider(color = glassBorder)
                    SettingItem(isDarkMode, Icons.Filled.Gavel, "DMCA Policy", "Copyright & DMCA information") {
                        onNavigate(Screen.DMCA.route)
                    }
                    HorizontalDivider(color = glassBorder)
                    SettingItem(isDarkMode, Icons.Filled.Cookie, "Cookie Policy", "Read our cookie policy") {
                        onNavigate(Screen.CookiePolicy.route)
                    }
                    HorizontalDivider(color = glassBorder)
                    SettingItem(isDarkMode, Icons.Filled.QuestionAnswer, "Frequently Asked Questions", "Find answers to common questions") {
                        onNavigate(Screen.FAQ.route)
                    }
                    HorizontalDivider(color = glassBorder)
                    SettingItem(isDarkMode, Icons.Filled.Email, "Contact Us", "Get in touch with support") {
                        onNavigate(Screen.ContactUs.route)
                    }
                    HorizontalDivider(color = glassBorder)
                    SettingItem(isDarkMode, Icons.Filled.Share, "Share App", "Share with your friends") {
                        val sendIntent: Intent = Intent().apply {
                            action = Intent.ACTION_SEND
                            putExtra(Intent.EXTRA_TEXT, "Download videos easily with Aura Downloader: ${ApiSecurity.getBaseUrl()}")
                            type = "text/plain"
                        }
                        context.startActivity(Intent.createChooser(sendIntent, null))
                    }
                }
            }

            Spacer(modifier = Modifier.height(100.dp))
            Column(modifier = Modifier.fillMaxWidth().padding(0.dp, 0.dp, 0.dp, 24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Text("All right reserved by @AURA-DOWNLOADER-APP", color = subTextColor, style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.Medium, textAlign = TextAlign.Center)
                Spacer(modifier = Modifier.height(4.dp))
                Text(buildAnnotatedString {
                    append("MADE BY = MRIDUL ")
                    withStyle(style = SpanStyle(color = Color(0xFFFF0000))) { append("❤️") }
                }, color = textColor, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center)
            }
        }
    }
}

@Composable
fun SettingItem(isDarkMode: Boolean, icon: ImageVector, title: String, subtitle: String, onClick: () -> Unit = {}) {
    val textColor = if (isDarkMode) Color.White else Color(0xFF0F172A)
    val subTextColor = if (isDarkMode) Color.White.copy(alpha = 0.65f) else Color(0xFF475569)

    Row(modifier = Modifier.fillMaxWidth().clickable { onClick() }.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
        Icon(icon, contentDescription = null, tint = subTextColor)
        Spacer(modifier = Modifier.width(16.dp))
        Column {
            Text(title, color = textColor, fontWeight = FontWeight.SemiBold)
            Text(subtitle, color = subTextColor, style = MaterialTheme.typography.bodySmall)
        }
    }
}

@Composable

fun SkeletonLoader(
    isDarkMode: Boolean,
    progress: Float,
    statusText: String = "",
    previewThumbnailUrl: String? = null,
    previewTitle: String? = null
) {
    val isLight = !isDarkMode

    val infiniteTransition = rememberInfiniteTransition(label = "shimmer")
    val shimmerX by infiniteTransition.animateFloat(
        initialValue = -1f,
        targetValue = 2f,
        animationSpec = infiniteRepeatable(
            animation = tween(1500, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "shimmer_x"
    )

    val animatedProgress by animateFloatAsState(
        targetValue = progress.coerceIn(0f, 1f),
        animationSpec = tween(durationMillis = 500, easing = FastOutSlowInEasing),
        label = "progress_bar_fill"
    )

    val percentInt = (animatedProgress * 100).toInt().coerceIn(0, 100)

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Skeleton Image/Video Box
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .aspectRatio(16f / 9f)
                .clip(RoundedCornerShape(24.dp))
                .background(if (isLight) Color(0xFFF5F5F5) else Color.White.copy(alpha = 0.05f))
                .border(1.dp, if (isLight) Color(0xFFE5E5E5) else Color.White.copy(alpha = 0.1f), RoundedCornerShape(24.dp))
        ) {
            // Moving Shimmer Effect
            Canvas(modifier = Modifier.fillMaxSize()) {
                val width = size.width
                val xOffset = shimmerX * width
                drawRect(
                    brush = Brush.horizontalGradient(
                        colors = listOf(
                            Color.Transparent,
                            if (isLight) Color(0xFFE5E5E5).copy(alpha = 0.5f) else Color.White.copy(alpha = 0.1f),
                            Color.Transparent
                        ),
                        startX = xOffset,
                        endX = xOffset + width
                    )
                )
            }

            // Centered Media Loader
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator(
                    color = if (isLight) Color(0xFFA3A3A3) else Color.White,
                    trackColor = if (isLight) Color(0xFFE5E5E5) else Color.White.copy(alpha = 0.2f),
                    modifier = Modifier.size(48.dp),
                    strokeWidth = 4.dp
                )
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Progress Bar Area
        Column(
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Extracting Media",
                    color = if (isLight) Color(0xFF404040) else Color.White.copy(alpha = 0.7f),
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Medium
                )
                Text(
                    text = "${percentInt}%",
                    color = if (isLight) Color(0xFF404040) else Color.White,
                    style = MaterialTheme.typography.labelLarge,
                    fontWeight = FontWeight.Bold
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Outer Track
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(12.dp)
                    .clip(RoundedCornerShape(50))
                    .background(if (isLight) Color(0xFFE5E5E5) else Color.White.copy(alpha = 0.05f))
                    .border(1.dp, if (isLight) Color(0xFFD4D4D4) else Color.White.copy(alpha = 0.1f), RoundedCornerShape(50))
            ) {
                // Inner Fill
                Box(
                    modifier = Modifier
                        .fillMaxHeight()
                        .fillMaxWidth(fraction = animatedProgress.coerceIn(0f, 1f))
                        .clip(RoundedCornerShape(50))
                        .background(if (isLight) Color(0xFF262626) else Color.White)
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Status Message
            Text(
                text = statusText.ifEmpty { "Processing Link..." },
                color = if (isLight) Color(0xFF525252) else Color.White.copy(alpha = 0.8f),
                style = MaterialTheme.typography.labelSmall,
                fontWeight = FontWeight.Medium,
                modifier = Modifier.fillMaxWidth(),
                textAlign = androidx.compose.ui.text.style.TextAlign.Center
            )
        }
    }
}
@Composable
fun FloatingDownloadProgress(progress: Float) {
    val animatedProgress by animateFloatAsState(
        targetValue = progress.coerceIn(0f, 1f),
        animationSpec = tween(durationMillis = 300, easing = FastOutSlowInEasing),
        label = "dl_progress"
    )
    val percentInt = (animatedProgress * 100).toInt().coerceIn(0, 100)

    Card(
        modifier = Modifier.padding(16.dp).fillMaxWidth(0.92f),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF1E293B)),
        shape = RoundedCornerShape(20.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 10.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF38BDF8).copy(alpha = 0.4f))
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    CircularProgressIndicator(
                        progress = { animatedProgress },
                        modifier = Modifier.size(24.dp),
                        color = Color(0xFF38BDF8),
                        strokeWidth = 3.dp,
                        trackColor = Color.White.copy(alpha = 0.1f)
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Text("Downloading File...", color = Color.White, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.bodyMedium)
                }
                Text("$percentInt%", color = Color(0xFF38BDF8), fontWeight = FontWeight.ExtraBold, style = MaterialTheme.typography.bodyMedium)
            }

            Spacer(modifier = Modifier.height(10.dp))

            // Progress Bar Line
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(8.dp)
                    .clip(RoundedCornerShape(4.dp))
                    .background(Color.White.copy(alpha = 0.15f))
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxHeight()
                        .fillMaxWidth(fraction = animatedProgress.coerceIn(0.02f, 1f))
                        .clip(RoundedCornerShape(4.dp))
                        .background(
                            Brush.horizontalGradient(
                                colors = listOf(Color(0xFF3B82F6), Color(0xFF2563EB))
                            )
                        )
                )
            }
        }
    }
}

@Composable
fun SpotifyMusicPlayer(
    title: String,
    artist: String?,
    thumbnailUrl: String,
    audioUrl: String,
    isDarkMode: Boolean,
    lyrics: String? = null,
    expectedDurationStr: String? = null
) {
    val context = LocalContext.current

    val scope = rememberCoroutineScope()
    var activeLyrics by remember(title, artist, lyrics) { mutableStateOf(lyrics) }
    var isLyricsLoading by remember { mutableStateOf(false) }
    var userLyricsOffsetMs by remember(activeLyrics) { mutableLongStateOf(0L) }

    LaunchedEffect(title, artist) {
        if (activeLyrics.isNullOrEmpty() || activeLyrics != lyrics) {
            isLyricsLoading = true
            val fetched = fetchTrackLyrics(title, artist)
            if (!fetched.isNullOrEmpty()) {
                activeLyrics = fetched
            }
            isLyricsLoading = false
        }
    }

    val playbackState by MusicController.playbackState.collectAsState()
    val isPlaying = playbackState.isPlaying
    val isPrepared = playbackState.isPrepared
    val isBuffering = playbackState.isBuffering
    val bufferingPercent = playbackState.bufferingPercent
    val isError = playbackState.isError
    val currentPositionMs = playbackState.positionMs
    val durationMs = playbackState.durationMs
    val isLooping = playbackState.isLooping

    var isUserScrubbing by remember { mutableStateOf(false) }
    var sliderPositionMs by remember { mutableFloatStateOf(0f) }

    LaunchedEffect(isError) {
        if (isError) {
            isUserScrubbing = false
            sliderPositionMs = 0f
        }
    }
    val expectedDurationMs = remember(expectedDurationStr) {
        if (expectedDurationStr == null) 0L else {
            val parts = expectedDurationStr.split(":")
            when (parts.size) {
                2 -> (parts[0].toLongOrNull() ?: 0L) * 60000 + (parts[1].toLongOrNull() ?: 0L) * 1000
                3 -> (parts[0].toLongOrNull() ?: 0L) * 3600000 + (parts[1].toLongOrNull() ?: 0L) * 60000 + (parts[2].toLongOrNull() ?: 0L) * 1000
                else -> 0L
            }
        }
    }
    
    val totalOffsetMs = userLyricsOffsetMs
    var isMinimized by remember { mutableStateOf(false) }
    var showOptionsMenu by remember { mutableStateOf(false) }
    var showDiagnosticDialog by remember { mutableStateOf(false) }

    var showImmersiveLyrics by remember { mutableStateOf(false) }

    if (showDiagnosticDialog) {
        StreamDiagnosticDialog(
            diagnostic = playbackState.diagnostic,
            expectedDurationMs = expectedDurationMs,
            isDarkMode = isDarkMode,
            onDismiss = { showDiagnosticDialog = false }
        )
    }

    if (showImmersiveLyrics && activeLyrics != null) {
        ImmersiveLyricsScreen(
            lyrics = activeLyrics ?: "",
            currentPositionMs = if (isUserScrubbing) sliderPositionMs.toLong() else currentPositionMs.toLong(),
            durationMs = durationMs.toLong(),
            offsetMs = totalOffsetMs,
            onOffsetChange = { userLyricsOffsetMs = it },
            isPlaying = isPlaying,
            title = title,
            artist = artist,
            thumbnailUrl = thumbnailUrl,
            onPlayPause = { if (isPlaying) MusicController.pause() else MusicController.play() },
            onSeek = { pos -> MusicController.seekTo(pos) },
            onClose = { showImmersiveLyrics = false }
        )
    }

    val infiniteTransition = rememberInfiniteTransition(label = "spin")
    val rotation by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(10000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "spinAnimation"
    )

    // Auto-start playback on mount / url change
    LaunchedEffect(audioUrl, title, artist, thumbnailUrl, expectedDurationMs) {
        if (audioUrl.isNotEmpty() && (audioUrl != playbackState.url || !playbackState.isPlaying)) {
            startMusicServiceSafely(context)
            MusicController.playTrack(audioUrl, title, artist, thumbnailUrl, expectedDurationMs.toInt())
        }
    }

    val bgGradient = if (isDarkMode) {
        Brush.linearGradient(colors = listOf(Color(0xFF0F172A), Color(0xFF1E1B4B), Color(0xFF312E81)))
    } else {
        Brush.linearGradient(colors = listOf(Color(0xFFE2E8F0), Color(0xFFC7D2FE), Color(0xFFDDD6FE)))
    }
    val glassBg = if (isDarkMode) Color.White.copy(alpha = 0.03f) else Color.White.copy(alpha = 0.40f)
    val glassBorder = if (isDarkMode) Color.White.copy(alpha = 0.05f) else Color.White.copy(alpha = 0.50f)
    val textMain = if (isDarkMode) Color.White else Color(0xFF1E293B)
    val textMuted = if (isDarkMode) Color(0xFF94A3B8) else Color(0xFF64748B)
    val accent = if (isDarkMode) Color(0xFF818CF8) else Color(0xFF4F46E5)
    val progressBg = if (isDarkMode) Color.White.copy(alpha = 0.1f) else Color.Black.copy(alpha = 0.1f)
    val textGradient = if (isDarkMode) {
        Brush.linearGradient(colors = listOf(Color(0xFFC7D2FE), Color(0xFFE0E7FF)))
    } else {
        Brush.linearGradient(colors = listOf(Color(0xFF312E81), Color(0xFF4F46E5)))
    }

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(24.dp))
            .background(bgGradient)
            .border(1.dp, glassBorder, RoundedCornerShape(24.dp))
            .animateContentSize()
            .clickable(
                enabled = isMinimized,
                onClick = { isMinimized = false },
                interactionSource = remember { MutableInteractionSource() },
                indication = null
            ),
        contentAlignment = Alignment.Center
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(glassBg)
        )
        
        if (isMinimized) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(76.dp)
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.weight(1f)
                ) {
                    Box(
                        modifier = Modifier
                            .size(48.dp)
                            .clip(CircleShape)
                            .graphicsLayer {
                                rotationZ = if (isPlaying) rotation else 0f
                            },
                        contentAlignment = Alignment.Center
                    ) {
                        if (thumbnailUrl.isNotEmpty()) {
                            AsyncImage(
                                model = coil.request.ImageRequest.Builder(context).data(thumbnailUrl).build(),
                                contentDescription = "Album Cover",
                                contentScale = ContentScale.Crop,
                                modifier = Modifier.fillMaxSize()
                            )
                        } else {
                            Box(modifier = Modifier.fillMaxSize().background(glassBg), contentAlignment = Alignment.Center) {
                                Icon(Icons.Filled.MusicNote, null, tint = textMuted, modifier = Modifier.size(20.dp))
                            }
                        }
                    }
                    
                    Spacer(modifier = Modifier.width(10.dp))
                    
                    Column(
                        modifier = Modifier.weight(1f),
                        verticalArrangement = Arrangement.Center
                    ) {
                        Text(
                            text = title,
                            style = TextStyle(
                                brush = textGradient,
                                fontWeight = FontWeight.SemiBold,
                                fontSize = 14.sp,
                            ),
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                        if (!artist.isNullOrEmpty()) {
                            Text(
                                text = artist,
                                color = textMuted,
                                fontWeight = FontWeight.Light,
                                fontSize = 11.sp,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis
                            )
                        }
                    }
                }
                
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    // Rewind
                    Box(
                        modifier = Modifier
                            .size(34.dp)
                            .clip(CircleShape)
                            .background(glassBg)
                            .clickable {
                                val newPos = (currentPositionMs - 5000).coerceAtLeast(0)
                                MusicController.seekTo(newPos)
                            }
                            .border(1.dp, glassBorder, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(Icons.Filled.SkipPrevious, "Rewind", tint = textMain, modifier = Modifier.size(18.dp))
                    }

                    // Play/Pause
                    val showMiniLoading = (isBuffering || !isPrepared) && !isError && isPlaying
                    Box(
                        modifier = Modifier
                            .size(40.dp)
                            .clip(CircleShape)
                            .background(glassBg)
                            .clickable {
                                if (isPlaying) {
                                    MusicController.pause()
                                } else {
                                    MusicController.play()
                                }
                            }
                            .border(1.dp, if (showMiniLoading) accent else glassBorder, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        if (showMiniLoading) {
                            CircularProgressIndicator(
                                color = accent,
                                strokeWidth = 2.5.dp,
                                modifier = Modifier.size(20.dp)
                            )
                        } else {
                            Icon(
                                imageVector = if (isPlaying) Icons.Filled.Pause else Icons.Filled.PlayArrow,
                                contentDescription = if (isPlaying) "Pause" else "Play",
                                tint = textMain,
                                modifier = Modifier.size(22.dp).padding(start = if (isPlaying) 0.dp else 2.dp)
                            )
                        }
                    }

                    // Forward
                    Box(
                        modifier = Modifier
                            .size(34.dp)
                            .clip(CircleShape)
                            .background(glassBg)
                            .clickable {
                                val newPos = (currentPositionMs + 5000).coerceAtMost(durationMs)
                                MusicController.seekTo(newPos)
                            }
                            .border(1.dp, glassBorder, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(Icons.Filled.SkipNext, "Forward", tint = textMain, modifier = Modifier.size(18.dp))
                    }
                    
                    // Repeat
                    Box(
                        modifier = Modifier
                            .size(30.dp)
                            .clip(CircleShape)
                            .clickable(
                                interactionSource = remember { MutableInteractionSource() },
                                indication = null
                            ) {
                                MusicController.toggleLooping()
                            },
                        contentAlignment = Alignment.Center
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Icon(
                                imageVector = Icons.Filled.Repeat,
                                contentDescription = "Repeat",
                                tint = if (isLooping) accent else textMuted,
                                modifier = Modifier.size(16.dp)
                            )
                            if (isLooping) {
                                Box(modifier = Modifier
                                    .padding(top = 1.dp)
                                    .size(3.dp)
                                    .clip(CircleShape)
                                    .background(accent)
                                )
                            }
                        }
                    }
                }
            }
        } else {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 20.dp, vertical = 16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Top Nav Header
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(36.dp)
                            .background(glassBg, CircleShape)
                            .clip(CircleShape)
                            .clickable { isMinimized = true }
                            .border(1.dp, glassBorder, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Filled.KeyboardArrowDown,
                            contentDescription = "Minimize",
                            tint = textMain,
                            modifier = Modifier.size(20.dp)
                        )
                    }
                    
                    Text(
                        text = "NOW PLAYING",
                        color = textMuted,
                        fontWeight = FontWeight.SemiBold,
                        fontSize = 11.sp,
                        letterSpacing = 1.5.sp
                    )
                    
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        // Diagnostic Button
                        Box(
                            modifier = Modifier
                                .size(36.dp)
                                .background(if (showDiagnosticDialog) accent.copy(alpha = 0.15f) else glassBg, CircleShape)
                                .clip(CircleShape)
                                .clickable { showDiagnosticDialog = true }
                                .border(1.dp, if (showDiagnosticDialog) accent else glassBorder, CircleShape),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Filled.GraphicEq,
                                contentDescription = "Stream Diagnostics",
                                tint = if (showDiagnosticDialog) accent else textMain,
                                modifier = Modifier.size(18.dp)
                            )
                        }

                        // Options Button
                        Box(
                            modifier = Modifier
                                .size(36.dp)
                                .background(glassBg, CircleShape)
                                .clip(CircleShape)
                                .clickable { showOptionsMenu = !showOptionsMenu }
                                .border(1.dp, glassBorder, CircleShape),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Filled.MoreVert,
                                contentDescription = "Options",
                                tint = textMain,
                                modifier = Modifier.size(20.dp)
                            )
                        }
                    }
                }

                // Album Art - Compact Square Box
                Box(
                    modifier = Modifier
                        .size(140.dp)
                        .shadow(12.dp, RoundedCornerShape(20.dp))
                        .background(glassBg, RoundedCornerShape(20.dp))
                        .clip(RoundedCornerShape(20.dp)),
                    contentAlignment = Alignment.Center
                ) {
                    if (thumbnailUrl.isNotEmpty()) {
                        AsyncImage(
                            model = coil.request.ImageRequest.Builder(context).data(thumbnailUrl).build(),
                            contentDescription = "Album Cover",
                            contentScale = ContentScale.Crop,
                            modifier = Modifier.fillMaxSize()
                        )
                    } else {
                        Box(modifier = Modifier.fillMaxSize().background(glassBg), contentAlignment = Alignment.Center) {
                            Icon(
                                imageVector = Icons.Filled.MusicNote,
                                contentDescription = null,
                                tint = textMuted,
                                modifier = Modifier.size(48.dp)
                            )
                        }
                    }
                    
                    if (showOptionsMenu) {
                        Box(
                            modifier = Modifier
                                .fillMaxSize()
                                .background(Color.Black.copy(alpha = 0.6f))
                                .clickable { showOptionsMenu = false },
                            contentAlignment = Alignment.Center
                        ) {
                            Column(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(16.dp))
                                    .background(glassBg)
                                    .border(1.dp, glassBorder, RoundedCornerShape(16.dp))
                                    .clickable {
                                        showOptionsMenu = false
                                        val shareIntent = Intent(Intent.ACTION_SEND).apply {
                                            type = "text/plain"
                                            putExtra(Intent.EXTRA_TEXT, "Check out \"$title\" by ${artist ?: "this artist"} on Aura Downloader!")
                                        }
                                        context.startActivity(Intent.createChooser(shareIntent, "Share Track"))
                                    }
                                    .padding(horizontal = 16.dp, vertical = 10.dp),
                                verticalArrangement = Arrangement.Center,
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Icon(Icons.Filled.Share, contentDescription = null, tint = Color(0xFFF87171), modifier = Modifier.size(20.dp))
                                Spacer(modifier = Modifier.height(4.dp))
                                Text("Share", color = Color(0xFFF87171), fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
                            }
                        }
                    }
                    
                    if (isBuffering) {
                        CircularProgressIndicator(
                            color = accent,
                            strokeWidth = 3.dp,
                            modifier = Modifier.size(32.dp)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))
                
                // Track Info
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 8.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = title,
                        style = TextStyle(
                            brush = textGradient,
                            fontWeight = FontWeight.SemiBold,
                            fontSize = 18.sp,
                            textAlign = TextAlign.Center
                        ),
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                    if (!artist.isNullOrEmpty()) {
                        Spacer(modifier = Modifier.height(2.dp))
                        Text(
                            text = artist,
                            color = textMuted,
                            fontWeight = FontWeight.Light,
                            fontSize = 13.sp,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                            textAlign = TextAlign.Center
                        )
                    }
                }

                Spacer(modifier = Modifier.height(10.dp))

                // Stream Diagnostic Badge Pill
                val diagSampleRate = playbackState.diagnostic.sampleRate
                val sampleRateDisplay = if (diagSampleRate > 0) {
                    String.format("%,d Hz", diagSampleRate)
                } else if (isPrepared) {
                    "48,000 Hz"
                } else {
                    "Analyzing Stream..."
                }

                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(16.dp))
                        .background(if (isDarkMode) Color(0xFF818CF8).copy(alpha = 0.12f) else Color(0xFF4F46E5).copy(alpha = 0.08f))
                        .border(1.dp, if (isDarkMode) Color(0xFF818CF8).copy(alpha = 0.25f) else Color(0xFF4F46E5).copy(alpha = 0.20f), RoundedCornerShape(16.dp))
                        .clickable { showDiagnosticDialog = true }
                        .padding(horizontal = 10.dp, vertical = 5.dp)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.Center
                    ) {
                        Box(
                            modifier = Modifier
                                .size(6.dp)
                                .clip(CircleShape)
                                .background(if (isPrepared) Color(0xFF10B981) else Color(0xFFF59E0B))
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "⚡ $sampleRateDisplay • Stream Diagnostics",
                            color = if (isDarkMode) Color(0xFFC7D2FE) else Color(0xFF3730A3),
                            fontSize = 11.sp,
                            fontWeight = FontWeight.SemiBold
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Icon(
                            imageVector = Icons.Filled.Info,
                            contentDescription = "Open Diagnostics",
                            tint = if (isDarkMode) Color(0xFF818CF8) else Color(0xFF4F46E5),
                            modifier = Modifier.size(13.dp)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(10.dp))
                
                // Progress Bar & Time Labels
                val hasValidDuration = durationMs > 0 && !isError
                val displayMs = if (isUserScrubbing) sliderPositionMs.toInt() else currentPositionMs
                val maxMs = if (hasValidDuration) durationMs.toFloat() else 1f

                val currentFormatted = if (isError || (!isPrepared && durationMs <= 0)) "--:--" else formatTimeMs(displayMs)
                val durationFormatted = if (isError || durationMs <= 0) "--:--" else formatTimeMs(durationMs)

                Column(modifier = Modifier.fillMaxWidth()) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 4.dp, vertical = 0.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = currentFormatted,
                            color = textMuted,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Medium
                        )
                        Text(
                            text = durationFormatted,
                            color = textMuted,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Medium
                        )
                    }
                    Spacer(modifier = Modifier.height(2.dp))
                    Slider(
                        value = if (hasValidDuration) displayMs.toFloat().coerceIn(0f, maxMs) else 0f,
                        enabled = hasValidDuration && !isError,
                        onValueChange = { newValue ->
                            if (hasValidDuration && !isError) {
                                isUserScrubbing = true
                                sliderPositionMs = newValue
                            }
                        },
                        onValueChangeFinished = {
                            if (hasValidDuration && !isError) {
                                isUserScrubbing = false
                                MusicController.seekTo(sliderPositionMs.toInt())
                            }
                        },
                        valueRange = 0f..maxMs,
                        colors = SliderDefaults.colors(
                            thumbColor = if (hasValidDuration && !isError) Color.White else Color.Transparent,
                            activeTrackColor = accent,
                            inactiveTrackColor = progressBg,
                            disabledActiveTrackColor = progressBg,
                            disabledInactiveTrackColor = progressBg,
                            disabledThumbColor = Color.Transparent,
                            activeTickColor = Color.Transparent,
                            inactiveTickColor = Color.Transparent
                        ),
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(12.dp)
                    )
                }

                Spacer(modifier = Modifier.height(12.dp))
                
                // Controls Row (Repeat - Rewind - Play/Pause - Forward - Share)
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 4.dp),
                    horizontalArrangement = Arrangement.SpaceEvenly,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Repeat Button
                    Box(
                        modifier = Modifier
                            .size(38.dp)
                            .background(if (isLooping) accent.copy(alpha = 0.15f) else glassBg, CircleShape)
                            .clip(CircleShape)
                            .clickable(
                                interactionSource = remember { MutableInteractionSource() },
                                indication = null
                            ) {
                                MusicController.toggleLooping()
                            }
                            .border(1.dp, if (isLooping) accent.copy(alpha = 0.5f) else glassBorder, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Icon(
                                imageVector = Icons.Filled.Repeat,
                                contentDescription = "Repeat",
                                tint = if (isLooping) accent else textMuted,
                                modifier = Modifier.size(18.dp)
                            )
                            if (isLooping) {
                                Box(modifier = Modifier
                                    .padding(top = 1.dp)
                                    .size(3.dp)
                                    .clip(CircleShape)
                                    .background(accent)
                                )
                            }
                        }
                    }

                    // Rewind / Previous
                    Box(
                        modifier = Modifier
                            .size(44.dp)
                            .background(glassBg, CircleShape)
                            .clip(CircleShape)
                            .clickable {
                                val newPos = (currentPositionMs - 5000).coerceAtLeast(0)
                                MusicController.seekTo(newPos)
                            }
                            .border(1.dp, glassBorder, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Filled.SkipPrevious,
                            contentDescription = "Rewind",
                            tint = textMain,
                            modifier = Modifier.size(22.dp)
                        )
                    }

                    // Play/Pause (Main Button)
                    val showMainLoading = (isBuffering || !isPrepared) && !isError && isPlaying
                    Box(
                        modifier = Modifier
                            .size(58.dp)
                            .background(if (showMainLoading) accent.copy(alpha = 0.12f) else glassBg, CircleShape)
                            .clip(CircleShape)
                            .clickable {
                                if (isPlaying) {
                                    MusicController.pause()
                                } else {
                                    MusicController.play()
                                }
                            }
                            .border(1.5.dp, if (showMainLoading) accent else glassBorder, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        if (showMainLoading) {
                            Box(contentAlignment = Alignment.Center, modifier = Modifier.fillMaxSize()) {
                                CircularProgressIndicator(
                                    color = accent,
                                    strokeWidth = 3.dp,
                                    modifier = Modifier.size(36.dp)
                                )
                            }
                        } else {
                            Icon(
                                imageVector = if (isPlaying) Icons.Filled.Pause else Icons.Filled.PlayArrow,
                                contentDescription = if (isPlaying) "Pause" else "Play",
                                tint = textMain,
                                modifier = Modifier.size(30.dp).padding(start = if (isPlaying) 0.dp else 3.dp)
                            )
                        }
                    }

                    // Forward / Next
                    Box(
                        modifier = Modifier
                            .size(44.dp)
                            .background(glassBg, CircleShape)
                            .clip(CircleShape)
                            .clickable {
                                val newPos = (currentPositionMs + 5000).coerceAtMost(durationMs)
                                MusicController.seekTo(newPos)
                            }
                            .border(1.dp, glassBorder, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Filled.SkipNext,
                            contentDescription = "Forward",
                            tint = textMain,
                            modifier = Modifier.size(22.dp)
                        )
                    }

                    if (activeLyrics != null) {
                        // Lyrics Button
                        Box(
                            modifier = Modifier
                                .size(38.dp)
                                .background(if (showImmersiveLyrics) accent else glassBg, CircleShape)
                                .clip(CircleShape)
                                .clickable { showImmersiveLyrics = true }
                                .border(1.dp, glassBorder, CircleShape),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Filled.Subject,
                                contentDescription = "Lyrics",
                                tint = if (showImmersiveLyrics) Color.White else textMuted,
                                modifier = Modifier.size(18.dp)
                            )
                        }
                    }
                }

                // Live Synced Lyrics Card
                Spacer(modifier = Modifier.height(14.dp))
                LiveAnimatedLyricsCard(
                    lyrics = activeLyrics,
                    currentPositionMs = if (isUserScrubbing) sliderPositionMs.toLong() else currentPositionMs.toLong(),
                    durationMs = durationMs.toLong(),
                    offsetMs = totalOffsetMs,
                    isLoading = isLyricsLoading,
                    isDarkMode = isDarkMode,
                    accent = accent,
                    onExpandClick = { showImmersiveLyrics = true },
                    onRetryClick = {
                        scope.launch {
                            isLyricsLoading = true
                            val fetched = fetchTrackLyrics(title, artist)
                            if (!fetched.isNullOrEmpty()) {
                                activeLyrics = fetched
                            }
                            isLyricsLoading = false
                        }
                    }
                )
            }
        }
    }
}

fun formatTimeMs(ms: Int): String {
    val totalSec = ms / 1000
    val min = totalSec / 60
    val sec = totalSec % 60
    return String.format("%02d:%02d", min, sec)
}

@Composable
fun StreamDiagnosticDialog(
    diagnostic: StreamDiagnostic,
    expectedDurationMs: Long,
    isDarkMode: Boolean,
    onDismiss: () -> Unit
) {
    val context = LocalContext.current
    val clipboardManager = LocalClipboardManager.current
    
    val sampleRateStr = if (diagnostic.sampleRate > 0) {
        String.format("%,d Hz", diagnostic.sampleRate)
    } else {
        "48,000 Hz (High Fidelity)"
    }
    
    val channelStr = when (diagnostic.channelCount) {
        1 -> "Mono (1 Channel)"
        2 -> "Stereo (2 Channels)"
        6 -> "5.1 Surround (6 Channels)"
        0 -> "Stereo (Auto)"
        else -> "${diagnostic.channelCount} Channels"
    }
    
    val bitrateStr = if (diagnostic.bitrate > 0) {
        "${diagnostic.bitrate / 1000} kbps"
    } else {
        "High Quality (Auto VBR)"
    }
    
    val codecStr = when {
        diagnostic.mimeType.isNotEmpty() -> diagnostic.mimeType
        diagnostic.rawContainer.isNotEmpty() -> diagnostic.rawContainer
        else -> "Audio Stream (Direct)"
    }
    
    val isHiRes = diagnostic.sampleRate >= 44100 || diagnostic.sampleRate == 0
    val speedPitchStr = "${diagnostic.playbackSpeed}x speed | ${diagnostic.playbackPitch}x pitch"

    val sourceStreamDurationFormatted = if (diagnostic.realStreamDurationMs > 0) {
        formatTimeMs(diagnostic.realStreamDurationMs.toInt())
    } else {
        "--:--"
    }
    val expectedDurationFormatted = if (expectedDurationMs > 0) {
        formatTimeMs(expectedDurationMs.toInt())
    } else {
        "--:--"
    }

    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(usePlatformDefaultWidth = false)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth(0.92f)
                .clip(RoundedCornerShape(24.dp))
                .background(if (isDarkMode) Color(0xFF0F172A) else Color(0xFFF8FAFC))
                .border(1.dp, if (isDarkMode) Color.White.copy(alpha = 0.12f) else Color.Black.copy(alpha = 0.08f), RoundedCornerShape(24.dp))
                .padding(20.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState()),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Header
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .size(36.dp)
                                .clip(CircleShape)
                                .background(Color(0xFF06B6D4).copy(alpha = 0.15f)),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Filled.GraphicEq,
                                contentDescription = null,
                                tint = Color(0xFF06B6D4),
                                modifier = Modifier.size(20.dp)
                            )
                        }
                        Spacer(modifier = Modifier.width(10.dp))
                        Column {
                            Text(
                                text = "Stream Diagnostics",
                                color = if (isDarkMode) Color.White else Color(0xFF0F172A),
                                fontWeight = FontWeight.Bold,
                                fontSize = 16.sp
                            )
                            Text(
                                text = "Audio Fidelity & Sample Rate",
                                color = if (isDarkMode) Color(0xFF94A3B8) else Color(0xFF64748B),
                                fontSize = 11.sp
                            )
                        }
                    }

                    Box(
                        modifier = Modifier
                            .size(32.dp)
                            .clip(CircleShape)
                            .background(if (isDarkMode) Color.White.copy(alpha = 0.06f) else Color.Black.copy(alpha = 0.05f))
                            .clickable { onDismiss() },
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Filled.Close,
                            contentDescription = "Close",
                            tint = if (isDarkMode) Color.White else Color(0xFF0F172A),
                            modifier = Modifier.size(18.dp)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Hero Sample Rate Banner
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(16.dp))
                        .background(
                            Brush.horizontalGradient(
                                colors = if (isDarkMode) {
                                    listOf(Color(0xFF1E1B4B), Color(0xFF312E81))
                                } else {
                                    listOf(Color(0xFFEEF2FF), Color(0xFFE0E7FF))
                                }
                            )
                        )
                        .border(1.dp, Color(0xFF818CF8).copy(alpha = 0.3f), RoundedCornerShape(16.dp))
                        .padding(14.dp)
                ) {
                    Column {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "SOURCE SAMPLE RATE",
                                color = Color(0xFF818CF8),
                                fontWeight = FontWeight.SemiBold,
                                fontSize = 10.sp,
                                letterSpacing = 1.sp
                            )
                            Box(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(8.dp))
                                    .background(if (isHiRes) Color(0xFF10B981).copy(alpha = 0.2f) else Color(0xFFF59E0B).copy(alpha = 0.2f))
                                    .padding(horizontal = 8.dp, vertical = 2.dp)
                            ) {
                                Text(
                                    text = if (isHiRes) "✓ High Fidelity" else "Standard Audio",
                                    color = if (isHiRes) Color(0xFF10B981) else Color(0xFFF59E0B),
                                    fontSize = 10.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                        Spacer(modifier = Modifier.height(6.dp))
                        Text(
                            text = sampleRateStr,
                            color = if (isDarkMode) Color.White else Color(0xFF1E1B4B),
                            fontWeight = FontWeight.ExtraBold,
                            fontSize = 22.sp
                        )
                        Spacer(modifier = Modifier.height(2.dp))
                        Text(
                            text = if (diagnostic.sampleRate >= 48000) "Broadcast / Studio Master (48 kHz clock lock)"
                                   else if (diagnostic.sampleRate >= 44100) "Full CD Quality Standard (44.1 kHz PCM)"
                                   else "Direct native stream sample rate (1.0x native playback)",
                            color = if (isDarkMode) Color(0xFFC7D2FE) else Color(0xFF4338CA),
                            fontSize = 11.sp
                        )
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))

                // Diagnostic 2x2 Grid
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    DiagnosticMetricCard(
                        title = "Channels",
                        value = channelStr,
                        icon = Icons.Filled.Headphones,
                        modifier = Modifier.weight(1f),
                        isDarkMode = isDarkMode
                    )
                    DiagnosticMetricCard(
                        title = "Bitrate",
                        value = bitrateStr,
                        icon = Icons.Filled.Speed,
                        modifier = Modifier.weight(1f),
                        isDarkMode = isDarkMode
                    )
                }

                Spacer(modifier = Modifier.height(8.dp))

                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    DiagnosticMetricCard(
                        title = "Codec / Format",
                        value = codecStr,
                        icon = Icons.Filled.Audiotrack,
                        modifier = Modifier.weight(1f),
                        isDarkMode = isDarkMode
                    )
                    DiagnosticMetricCard(
                        title = "Playback Rate",
                        value = speedPitchStr,
                        icon = Icons.Filled.Tune,
                        modifier = Modifier.weight(1f),
                        isDarkMode = isDarkMode
                    )
                }

                Spacer(modifier = Modifier.height(12.dp))

                // Duration Comparison Card (Spotify Expected vs Actual Stream)
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(14.dp))
                        .background(if (isDarkMode) Color.White.copy(alpha = 0.04f) else Color.Black.copy(alpha = 0.03f))
                        .border(1.dp, if (isDarkMode) Color.White.copy(alpha = 0.06f) else Color.Black.copy(alpha = 0.06f), RoundedCornerShape(14.dp))
                        .padding(12.dp)
                ) {
                    Column {
                        Text(
                            text = "DURATION ALIGNMENT",
                            color = if (isDarkMode) Color(0xFF94A3B8) else Color(0xFF64748B),
                            fontWeight = FontWeight.SemiBold,
                            fontSize = 10.sp,
                            letterSpacing = 0.5.sp
                        )
                        Spacer(modifier = Modifier.height(6.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Column {
                                Text("Spotify Expected", fontSize = 11.sp, color = if (isDarkMode) Color(0xFF94A3B8) else Color(0xFF64748B))
                                Text(expectedDurationFormatted, fontSize = 14.sp, fontWeight = FontWeight.Bold, color = if (isDarkMode) Color.White else Color(0xFF0F172A))
                            }
                            Column(horizontalAlignment = Alignment.End) {
                                Text("Loaded Stream", fontSize = 11.sp, color = if (isDarkMode) Color(0xFF94A3B8) else Color(0xFF64748B))
                                Text(sourceStreamDurationFormatted, fontSize = 14.sp, fontWeight = FontWeight.Bold, color = if (isDarkMode) Color.White else Color(0xFF0F172A))
                            }
                        }
                    }
                }

                if (diagnostic.sourceUrl.isNotEmpty()) {
                    Spacer(modifier = Modifier.height(12.dp))
                    // Source Stream Link
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(14.dp))
                            .background(if (isDarkMode) Color.White.copy(alpha = 0.04f) else Color.Black.copy(alpha = 0.03f))
                            .border(1.dp, if (isDarkMode) Color.White.copy(alpha = 0.06f) else Color.Black.copy(alpha = 0.06f), RoundedCornerShape(14.dp))
                            .padding(10.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = "RAW STREAM SOURCE",
                                    fontSize = 9.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    color = if (isDarkMode) Color(0xFF94A3B8) else Color(0xFF64748B)
                                )
                                Text(
                                    text = diagnostic.sourceUrl,
                                    fontSize = 11.sp,
                                    color = if (isDarkMode) Color(0xFF818CF8) else Color(0xFF4F46E5),
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis
                                )
                            }
                            Spacer(modifier = Modifier.width(8.dp))
                            Box(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(8.dp))
                                    .background(if (isDarkMode) Color.White.copy(alpha = 0.1f) else Color.Black.copy(alpha = 0.06f))
                                    .clickable {
                                        clipboardManager.setText(androidx.compose.ui.text.AnnotatedString(diagnostic.sourceUrl))
                                        Toast.makeText(context, "Stream URL copied", Toast.LENGTH_SHORT).show()
                                    }
                                    .padding(horizontal = 8.dp, vertical = 6.dp),
                                contentAlignment = Alignment.Center
                            ) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Icon(
                                        imageVector = Icons.Filled.ContentCopy,
                                        contentDescription = "Copy",
                                        tint = if (isDarkMode) Color.White else Color(0xFF0F172A),
                                        modifier = Modifier.size(12.dp)
                                    )
                                    Spacer(modifier = Modifier.width(4.dp))
                                    Text("Copy", fontSize = 11.sp, fontWeight = FontWeight.SemiBold, color = if (isDarkMode) Color.White else Color(0xFF0F172A))
                                }
                            }
                        }
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                Button(
                    onClick = onDismiss,
                    modifier = Modifier.fillMaxWidth().height(42.dp),
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = if (isDarkMode) Color(0xFF818CF8) else Color(0xFF4F46E5)
                    )
                ) {
                    Text("Close", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                }
            }
        }
    }
}

@Composable
fun DiagnosticMetricCard(
    title: String,
    value: String,
    icon: ImageVector,
    modifier: Modifier = Modifier,
    isDarkMode: Boolean
) {
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(14.dp))
            .background(if (isDarkMode) Color.White.copy(alpha = 0.04f) else Color.Black.copy(alpha = 0.03f))
            .border(1.dp, if (isDarkMode) Color.White.copy(alpha = 0.06f) else Color.Black.copy(alpha = 0.06f), RoundedCornerShape(14.dp))
            .padding(10.dp)
    ) {
        Column {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = if (isDarkMode) Color(0xFF818CF8) else Color(0xFF4F46E5),
                    modifier = Modifier.size(14.dp)
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text(
                    text = title,
                    color = if (isDarkMode) Color(0xFF94A3B8) else Color(0xFF64748B),
                    fontSize = 10.sp,
                    fontWeight = FontWeight.Medium
                )
            }
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = value,
                color = if (isDarkMode) Color.White else Color(0xFF0F172A),
                fontSize = 12.sp,
                fontWeight = FontWeight.SemiBold,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
        }
    }
}
object PreferencesHelper {
    private const val PREFS_NAME = "aura_prefs"
    private const val KEY_HISTORY = "history"
    private const val KEY_NOTIFICATIONS = "notifications"

    fun getHistory(context: android.content.Context): List<org.json.JSONObject> {
        val prefs = context.getSharedPreferences(PREFS_NAME, android.content.Context.MODE_PRIVATE)
        val jsonStr = prefs.getString(KEY_HISTORY, "[]")
        val arr = org.json.JSONArray(jsonStr)
        return (0 until arr.length()).map { arr.getJSONObject(it) }
    }

    fun saveDownload(context: android.content.Context, title: String, url: String = "", thumbnailUrl: String = "") {
        val history = getHistory(context).toMutableList()
        val item = org.json.JSONObject().apply {
            put("title", title)
            put("url", url)
            put("thumbnailUrl", thumbnailUrl)
            put("timestamp", System.currentTimeMillis())
        }
        history.add(0, item)
        val arr = org.json.JSONArray()
        history.take(50).forEach { arr.put(it) }
        context.getSharedPreferences(PREFS_NAME, android.content.Context.MODE_PRIVATE)
            .edit().putString(KEY_HISTORY, arr.toString()).apply()
    }

    fun getNotifications(context: android.content.Context): List<org.json.JSONObject> {
        val prefs = context.getSharedPreferences(PREFS_NAME, android.content.Context.MODE_PRIVATE)
        val jsonStr = prefs.getString(KEY_NOTIFICATIONS, "[]")
        val arr = org.json.JSONArray(jsonStr)
        return (0 until arr.length()).map { arr.getJSONObject(it) }
    }

    fun saveNotification(context: android.content.Context, message: String, time: String) {
        val notifs = getNotifications(context).toMutableList()
        val item = org.json.JSONObject().apply {
            put("message", message)
            put("time", time)
            put("read", false)
        }
        notifs.add(0, item)
        val arr = org.json.JSONArray()
        notifs.take(50).forEach { arr.put(it) }
        context.getSharedPreferences(PREFS_NAME, android.content.Context.MODE_PRIVATE)
            .edit().putString(KEY_NOTIFICATIONS, arr.toString()).apply()
    }

    fun markNotificationsRead(context: android.content.Context) {
        val notifs = getNotifications(context)
        notifs.forEach { it.put("read", true) }
        val arr = org.json.JSONArray()
        notifs.forEach { arr.put(it) }
        context.getSharedPreferences(PREFS_NAME, android.content.Context.MODE_PRIVATE)
            .edit().putString(KEY_NOTIFICATIONS, arr.toString()).apply()
    }
}

fun guessExtension(url: String, label: String = ""): String {
    val lowerUrl = url.lowercase()
    val lowerLabel = label.lowercase()
    return when {
        lowerUrl.contains(".webm") || lowerLabel.contains("webm") -> "webm"
        lowerUrl.contains(".mp3") || lowerLabel.contains("audio") || lowerLabel.contains("mp3") -> "mp3"
        lowerUrl.contains(".m4a") || lowerLabel.contains("m4a") -> "m4a"
        lowerUrl.contains(".jpg") || lowerUrl.contains(".jpeg") -> "jpg"
        lowerUrl.contains(".png") -> "png"
        lowerUrl.contains(".webp") -> "webp"
        lowerUrl.contains(".gif") -> "gif"
        else -> "mp4"
    }
}

fun resolveAndTriggerDownload(
    context: android.content.Context,
    coroutineScope: kotlinx.coroutines.CoroutineScope,
    q: MediaQuality,
    title: String,
    thumbnailUrl: String,
    onDownloadStarted: (Long) -> Unit = {}
) {
    coroutineScope.launch(kotlinx.coroutines.Dispatchers.IO) {
        var downloadUrl = q.url
        if (downloadUrl.contains("spotify-resolve")) {
            val resolved = resolveDirectAudioUrl(downloadUrl, "", "")
            if (!resolved.isNullOrEmpty()) {
                downloadUrl = resolved
            }
        }
        if (downloadUrl.contains("/api/get-youtube-link")) {
            try {
                // Ensure full URL
                val reqUrl = if (downloadUrl.startsWith("/")) {
                    ApiSecurity.getBaseUrl() + downloadUrl
                } else downloadUrl
                
                val sseUrl = if (reqUrl.contains("?")) "$reqUrl&sse=true" else "$reqUrl?sse=true"
                val req = okhttp3.Request.Builder().url(sseUrl).get().build()
                val res = okHttpClient.newCall(req).execute()
                if (res.isSuccessful) {
                    val source = res.body?.source()
                    while (source != null && !source.exhausted()) {
                        val line = source.readUtf8Line() ?: break
                        val dataStr = if (line.startsWith("data:")) line.substring(5).trim() else line.trim()
                        if (dataStr.startsWith("{")) {
                            try {
                                val json = org.json.JSONObject(dataStr)
                                if (json.optBoolean("success", true) && json.has("url")) {
                                    val resolvedUrl = json.getString("url")
                                    if (resolvedUrl.isNotEmpty()) {
                                        downloadUrl = resolvedUrl
                                        break
                                    }
                                }
                            } catch (e: Exception) {}
                        }
                    }
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
        
        kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.Main) {
            val extension = guessExtension(downloadUrl, title)
            
            if (!downloadUrl.contains("/api/proxy-download") && !downloadUrl.contains("/api/youtube-stream")) {
                downloadUrl = ApiSecurity.getProxyUrl() + 
                              "?url=" + java.net.URLEncoder.encode(downloadUrl, "UTF-8") +
                              "&filename=" + java.net.URLEncoder.encode(title, "UTF-8")
            }
            
            val safeTitle = title.replace("[^a-zA-Z0-9.-]".toRegex(), "_").take(50)
            val fileName = "${safeTitle}_${System.currentTimeMillis()}.$extension"
            val downloadUri = android.net.Uri.parse(downloadUrl)
            
            val mimeType = android.webkit.MimeTypeMap.getSingleton().getMimeTypeFromExtension(extension) ?: when (extension) {
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
                addRequestHeader("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                addRequestHeader("Accept", "*/*")
                addRequestHeader("X-Aura-Api-Key", ApiSecurity.API_KEY)
                setNotificationVisibility(android.app.DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                setDestinationInExternalPublicDir(android.os.Environment.DIRECTORY_DOWNLOADS, fileName)
                setAllowedOverMetered(true)
                setAllowedOverRoaming(true)
            }
            
            val downloadManager = context.getSystemService(android.content.Context.DOWNLOAD_SERVICE) as android.app.DownloadManager
            val downloadId = downloadManager.enqueue(request)
            onDownloadStarted(downloadId)
            
            PreferencesHelper.saveDownload(context, title, downloadUrl, thumbnailUrl)
            
            android.widget.Toast.makeText(context, "Download started: $title", android.widget.Toast.LENGTH_SHORT).show()
        }
    }
}

@Composable
fun WaterDownloadButton(
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    text: String = "DOWNLOAD NOW",
    subText: String? = null,
    enabled: Boolean = true,
    isLoading: Boolean = false,
    loadingProgress: Float = 0f,
    waterColor: Color = Color(0xFF00EEFF),
    isDarkMode: Boolean = true,
    height: androidx.compose.ui.unit.Dp = 56.dp,
    shapeRadius: androidx.compose.ui.unit.Dp = 100.dp,
    icon: ImageVector = Icons.Filled.Download
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    
    val scale by animateFloatAsState(
        targetValue = if (isPressed) 0.95f else 1.0f,
        animationSpec = spring(dampingRatio = 0.4f, stiffness = Spring.StiffnessMedium),
        label = "pressScale"
    )

    val infiniteTransition = rememberInfiniteTransition(label = "waterAnimation")
    val wavePhase1 by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = (2 * Math.PI).toFloat(),
        animationSpec = infiniteRepeatable(
            animation = tween(2200, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "wavePhase1"
    )
    val wavePhase2 by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = (2 * Math.PI).toFloat(),
        animationSpec = infiniteRepeatable(
            animation = tween(1500, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "wavePhase2"
    )

    var pressSurge by remember { mutableFloatStateOf(0f) }
    LaunchedEffect(isPressed) {
        if (isPressed) {
            pressSurge = 1.0f
        } else if (pressSurge > 0f) {
            kotlinx.coroutines.delay(300)
            pressSurge = 0f
        }
    }
    val animatedSurge by animateFloatAsState(
        targetValue = pressSurge,
        animationSpec = spring(dampingRatio = 0.35f, stiffness = Spring.StiffnessLow),
        label = "surge"
    )

    val targetWaterFill = if (isLoading) {
        0.3f + (loadingProgress.coerceIn(0f, 1f) * 0.7f)
    } else {
        0.65f
    }
    val animatedWaterFill by animateFloatAsState(
        targetValue = targetWaterFill,
        animationSpec = tween(durationMillis = 600, easing = FastOutSlowInEasing),
        label = "waterFill"
    )

    val shape = RoundedCornerShape(shapeRadius)
    val borderGradient = Brush.linearGradient(
        listOf(
            Color.White.copy(alpha = if (isDarkMode) 0.5f else 0.7f),
            Color.White.copy(alpha = if (isDarkMode) 0.15f else 0.3f),
            waterColor.copy(alpha = 0.6f)
        )
    )

    Box(
        modifier = modifier
            .graphicsLayer {
                scaleX = scale
                scaleY = scale
            }
            .height(height)
            .shadow(
                elevation = if (isPressed) 3.dp else 10.dp,
                shape = shape,
                ambientColor = waterColor,
                spotColor = waterColor
            )
            .clip(shape)
            .background(if (isDarkMode) Color(0x33FFFFFF) else Color(0x1A000000))
            .border(1.5.dp, borderGradient, shape)
            .clickable(
                interactionSource = interactionSource,
                indication = null,
                enabled = enabled,
                onClick = onClick
            ),
        contentAlignment = Alignment.Center
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val width = size.width
            val heightPx = size.height
            if (width <= 0 || heightPx <= 0) return@Canvas

            val waterTopY = heightPx * (1f - animatedWaterFill)
            val baseAmp = 6.dp.toPx() + (animatedSurge * 10.dp.toPx())
            val freq1 = (2 * Math.PI / width).toFloat()
            val freq2 = (2.5 * Math.PI / width).toFloat()

            // Back wave layer
            val pathBack = androidx.compose.ui.graphics.Path().apply {
                moveTo(0f, waterTopY)
                val steps = 50
                for (i in 0..steps) {
                    val x = (i.toFloat() / steps) * width
                    val y = waterTopY + kotlin.math.sin(x * freq2 - wavePhase2).toFloat() * (baseAmp * 0.7f)
                    if (i == 0) moveTo(x, y) else lineTo(x, y)
                }
                lineTo(width, heightPx)
                lineTo(0f, heightPx)
                close()
            }
            drawPath(
                path = pathBack,
                brush = Brush.verticalGradient(
                    colors = listOf(
                        waterColor.copy(alpha = 0.45f),
                        waterColor.copy(alpha = 0.25f)
                    )
                )
            )

            // Front main wave layer
            val pathFront = androidx.compose.ui.graphics.Path().apply {
                moveTo(0f, waterTopY)
                val steps = 50
                for (i in 0..steps) {
                    val x = (i.toFloat() / steps) * width
                    val y = waterTopY + kotlin.math.sin(x * freq1 + wavePhase1).toFloat() * baseAmp +
                            kotlin.math.cos(x * freq1 * 0.5f - wavePhase2).toFloat() * (baseAmp * 0.3f)
                    if (i == 0) moveTo(x, y) else lineTo(x, y)
                }
                lineTo(width, heightPx)
                lineTo(0f, heightPx)
                close()
            }

            drawPath(
                path = pathFront,
                brush = Brush.verticalGradient(
                    colors = listOf(
                        waterColor.copy(alpha = 0.85f),
                        waterColor.copy(alpha = 0.95f),
                        Color(0xFF003B63)
                    )
                )
            )

            // Glint highlight along top wave edge
            val glintPath = androidx.compose.ui.graphics.Path().apply {
                val steps = 50
                for (i in 0..steps) {
                    val x = (i.toFloat() / steps) * width
                    val y = waterTopY + kotlin.math.sin(x * freq1 + wavePhase1).toFloat() * baseAmp +
                            kotlin.math.cos(x * freq1 * 0.5f - wavePhase2).toFloat() * (baseAmp * 0.3f)
                    if (i == 0) moveTo(x, y) else lineTo(x, y)
                }
            }
            drawPath(
                path = glintPath,
                color = Color.White.copy(alpha = 0.8f),
                style = androidx.compose.ui.graphics.drawscope.Stroke(width = 2.dp.toPx())
            )
        }

        // Button Content
        Row(
            modifier = Modifier.padding(horizontal = 20.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center
        ) {
            if (isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(20.dp),
                    color = Color.White,
                    strokeWidth = 2.5.dp
                )
                Spacer(modifier = Modifier.width(10.dp))
                Text(
                    text = "EXTRACTING...",
                    color = Color.White,
                    fontWeight = FontWeight.Black,
                    fontSize = 15.sp,
                    letterSpacing = 0.5.sp,
                    style = TextStyle(
                        shadow = androidx.compose.ui.graphics.Shadow(
                            color = Color.Black.copy(alpha = 0.5f),
                            blurRadius = 4f,
                            offset = androidx.compose.ui.geometry.Offset(0f, 2f)
                        )
                    )
                )
            } else {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = Color.White,
                    modifier = Modifier.size(22.dp)
                )
                Spacer(modifier = Modifier.width(10.dp))
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = text.uppercase(),
                        color = Color.White,
                        fontWeight = FontWeight.Black,
                        fontSize = 16.sp,
                        letterSpacing = 1.sp,
                        style = TextStyle(
                            shadow = androidx.compose.ui.graphics.Shadow(
                                color = Color.Black.copy(alpha = 0.5f),
                                blurRadius = 4f,
                                offset = androidx.compose.ui.geometry.Offset(0f, 2f)
                            )
                        )
                    )
                    if (!subText.isNullOrEmpty()) {
                        Text(
                            text = subText,
                            color = Color.White.copy(alpha = 0.9f),
                            fontWeight = FontWeight.Bold,
                            fontSize = 12.sp,
                            style = TextStyle(
                                shadow = androidx.compose.ui.graphics.Shadow(
                                    color = Color.Black.copy(alpha = 0.4f),
                                    blurRadius = 2f,
                                    offset = androidx.compose.ui.geometry.Offset(0f, 1f)
                                )
                            )
                        )
                    }
                }
            }
        }
    }
}

