package com.auradownloader.app

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.drawable.BitmapDrawable
import android.media.AudioAttributes
import android.media.MediaPlayer
import android.net.Uri
import android.net.wifi.WifiManager
import android.os.Build
import android.os.IBinder
import android.os.PowerManager
import android.support.v4.media.MediaMetadataCompat
import android.support.v4.media.session.MediaSessionCompat
import android.support.v4.media.session.PlaybackStateCompat
import android.util.Log
import androidx.core.app.NotificationCompat
import androidx.core.app.ServiceCompat
import androidx.core.content.ContextCompat
import coil.ImageLoader
import coil.request.ImageRequest
import coil.request.SuccessResult
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.util.concurrent.TimeUnit

class MusicPlaybackService : Service() {

    companion object {
        private const val TAG = "MusicPlaybackService"
        private const val CHANNEL_ID = "media_playback_channel"
        private const val NOTIFICATION_ID = 1
        const val ACTION_PLAY = "com.auradownloader.app.ACTION_PLAY"
        const val ACTION_PAUSE = "com.auradownloader.app.ACTION_PAUSE"
        const val ACTION_NEXT = "com.auradownloader.app.ACTION_NEXT"
        const val ACTION_PREVIOUS = "com.auradownloader.app.ACTION_PREVIOUS"
        const val ACTION_STOP = "com.auradownloader.app.ACTION_STOP"
    }

    private var mediaPlayer: MediaPlayer? = null
    private var currentFileInputStream: FileInputStream? = null
    private var wifiLock: WifiManager.WifiLock? = null
    private lateinit var mediaSession: MediaSessionCompat
    private val serviceJob = SupervisorJob()
    private val serviceScope = CoroutineScope(Dispatchers.Main + serviceJob)
    private lateinit var imageLoader: ImageLoader
    private var downloadJob: Job? = null

    private val httpClient by lazy {
        OkHttpClient.Builder()
            .followRedirects(true)
            .followSslRedirects(true)
            .connectTimeout(20, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .build()
    }

    override fun onCreate() {
        super.onCreate()
        imageLoader = ImageLoader.Builder(applicationContext).build()
        createNotificationChannel()

        try {
            val wifiManager = applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
            wifiLock = wifiManager.createWifiLock(WifiManager.WIFI_MODE_FULL_HIGH_PERF, "MusicPlaybackServiceWifiLock").apply {
                setReferenceCounted(false)
            }
        } catch (e: Exception) {
            Log.w(TAG, "Could not create wifi lock: ${e.message}")
        }

        mediaSession = MediaSessionCompat(this, "MusicPlaybackService").apply {
            setCallback(mediaSessionCallback)
            isActive = true
        }

        // Observe the central music controller state
        serviceScope.launch {
            var lastState: MusicState? = null
            MusicController.playbackState.collect { state ->
                val isSeek = lastState != null && Math.abs(state.positionMs - (lastState?.positionMs ?: 0)) > 1500
                if (lastState?.url != state.url ||
                    lastState?.isPlaying != state.isPlaying ||
                    lastState?.isBuffering != state.isBuffering ||
                    lastState?.durationMs != state.durationMs ||
                    isSeek
                ) {
                    updateNotificationAndSession(state)
                    lastState = state
                }
            }
        }

        serviceScope.launch {
            MusicController.commandFlow.collect { cmd ->
                when (cmd) {
                    is MusicCommand.PlayUrl -> playUrl(cmd.url)
                    is MusicCommand.Play -> mediaPlayer?.let { mp ->
                        try {
                            if (MusicController.playbackState.value.isPrepared) {
                                if (mp.duration > 0 && mp.currentPosition >= mp.duration - 500) {
                                    mp.seekTo(0)
                                    MusicController.updatePosition(0, mp.duration)
                                }
                                mp.start()
                                acquireWifiLock()
                                MusicController.updatePosition(mp.currentPosition, mp.duration)
                                MusicController.updateIsPlaying(true)
                            } else {
                                MusicController.updateIsPlaying(true)
                            }
                        } catch (e: Exception) {
                            Log.e(TAG, "Error playing: ${e.message}")
                        }
                    }
                    is MusicCommand.Pause -> mediaPlayer?.let { mp ->
                        try {
                            if (MusicController.playbackState.value.isPrepared) {
                                mp.pause()
                            }
                            releaseWifiLock()
                            MusicController.updateIsPlaying(false)
                        } catch (e: Exception) {
                            Log.e(TAG, "Error pausing: ${e.message}")
                        }
                    }
                    is MusicCommand.Next -> mediaPlayer?.let { mp ->
                        try {
                            if (MusicController.playbackState.value.isPrepared) {
                                val newPos = (mp.currentPosition + 5000).coerceAtMost(mp.duration)
                                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                                    mp.seekTo(newPos.toLong(), MediaPlayer.SEEK_CLOSEST)
                                } else {
                                    mp.seekTo(newPos)
                                }
                                MusicController.updatePosition(newPos, mp.duration)
                            }
                        } catch (e: Exception) {}
                    }
                    is MusicCommand.Previous -> mediaPlayer?.let { mp ->
                        try {
                            if (MusicController.playbackState.value.isPrepared) {
                                val newPos = (mp.currentPosition - 5000).coerceAtLeast(0)
                                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                                    mp.seekTo(newPos.toLong(), MediaPlayer.SEEK_CLOSEST)
                                } else {
                                    mp.seekTo(newPos)
                                }
                                MusicController.updatePosition(newPos, mp.duration)
                            }
                        } catch (e: Exception) {}
                    }
                    is MusicCommand.SeekTo -> mediaPlayer?.let { mp ->
                        try {
                            if (MusicController.playbackState.value.isPrepared) {
                                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                                    mp.seekTo(cmd.position.toLong(), MediaPlayer.SEEK_CLOSEST)
                                } else {
                                    mp.seekTo(cmd.position)
                                }
                                MusicController.updatePosition(cmd.position, mp.duration)
                            }
                        } catch (e: Exception) {}
                    }
                    is MusicCommand.Stop -> stopSelf()
                    else -> {}
                }
            }
        }

        // Periodic playback position updater
        serviceScope.launch {
            while (isActive) {
                mediaPlayer?.let { mp ->
                    try {
                        if (MusicController.playbackState.value.isPrepared && mp.isPlaying) {
                            val pos = mp.currentPosition
                            val dur = mp.duration
                            MusicController.updatePosition(pos, dur)
                        }
                    } catch (e: Exception) {
                        // ignore position read exceptions during transition
                    }
                }
                delay(150L)
            }
        }
    }

    private fun acquireWifiLock() {
        try {
            wifiLock?.let {
                if (!it.isHeld) it.acquire()
            }
        } catch (e: Exception) {
            Log.w(TAG, "Error acquiring wifi lock: ${e.message}")
        }
    }

    private fun releaseWifiLock() {
        try {
            wifiLock?.let {
                if (it.isHeld) it.release()
            }
        } catch (e: Exception) {
            Log.w(TAG, "Error releasing wifi lock: ${e.message}")
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_PLAY -> MusicController.play()
            ACTION_PAUSE -> MusicController.pause()
            ACTION_NEXT -> MusicController.next()
            ACTION_PREVIOUS -> MusicController.previous()
            ACTION_STOP -> MusicController.stop()
        }
        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        downloadJob?.cancel()
        serviceJob.cancel()
        releasePlayer()
        releaseWifiLock()
        mediaSession.release()
        ServiceCompat.stopForeground(this, ServiceCompat.STOP_FOREGROUND_REMOVE)
    }

    private fun releasePlayer() {
        try {
            mediaPlayer?.stop()
            mediaPlayer?.release()
            mediaPlayer = null
        } catch (e: Exception) {}
        try {
            currentFileInputStream?.close()
            currentFileInputStream = null
        } catch (e: Exception) {}
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Media Playback",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Music playback control notification"
                setShowBadge(false)
            }
            val manager = getSystemService(NotificationManager::class.java)
            manager?.createNotificationChannel(channel)
        }
    }

    private val mediaSessionCallback = object : MediaSessionCompat.Callback() {
        override fun onPlay() { MusicController.play() }
        override fun onPause() { MusicController.pause() }
        override fun onSkipToNext() { MusicController.next() }
        override fun onSkipToPrevious() { MusicController.previous() }
        override fun onSeekTo(pos: Long) { MusicController.seekTo(pos.toInt()) }
    }

    private fun updateNotificationAndSession(state: MusicState) {
        val stateBuilder = PlaybackStateCompat.Builder()
            .setActions(
                PlaybackStateCompat.ACTION_PLAY or
                PlaybackStateCompat.ACTION_PAUSE or
                PlaybackStateCompat.ACTION_SKIP_TO_NEXT or
                PlaybackStateCompat.ACTION_SKIP_TO_PREVIOUS or
                PlaybackStateCompat.ACTION_SEEK_TO
            )
            .setState(
                if (state.isPlaying) PlaybackStateCompat.STATE_PLAYING else PlaybackStateCompat.STATE_PAUSED,
                state.positionMs.toLong(),
                1.0f
            )
        mediaSession.setPlaybackState(stateBuilder.build())

        serviceScope.launch(Dispatchers.IO) {
            var bitmap: Bitmap? = null
            if (state.thumbnailUrl.isNotEmpty()) {
                try {
                    val req = ImageRequest.Builder(this@MusicPlaybackService)
                        .data(state.thumbnailUrl)
                        .size(256)
                        .build()
                    val result = imageLoader.execute(req)
                    if (result is SuccessResult) {
                        bitmap = (result.drawable as? BitmapDrawable)?.bitmap
                    }
                } catch (e: Exception) {
                    Log.w(TAG, "Thumbnail load failed: ${e.message}")
                }
            }

            val metaBuilder = MediaMetadataCompat.Builder()
                .putString(MediaMetadataCompat.METADATA_KEY_TITLE, state.title)
                .putString(MediaMetadataCompat.METADATA_KEY_ARTIST, state.artist)
                .putLong(MediaMetadataCompat.METADATA_KEY_DURATION, state.durationMs.toLong())

            if (bitmap != null) {
                metaBuilder.putBitmap(MediaMetadataCompat.METADATA_KEY_ALBUM_ART, bitmap)
            }
            mediaSession.setMetadata(metaBuilder.build())

            val playPauseAction = if (state.isPlaying) {
                NotificationCompat.Action(
                    com.auradownloader.app.R.drawable.ic_launcher_foreground,
                    "Pause",
                    PendingIntent.getService(
                        this@MusicPlaybackService,
                        1,
                        Intent(this@MusicPlaybackService, MusicPlaybackService::class.java).apply { action = ACTION_PAUSE },
                        PendingIntent.FLAG_IMMUTABLE
                    )
                )
            } else {
                NotificationCompat.Action(
                    com.auradownloader.app.R.drawable.ic_launcher_foreground,
                    "Play",
                    PendingIntent.getService(
                        this@MusicPlaybackService,
                        2,
                        Intent(this@MusicPlaybackService, MusicPlaybackService::class.java).apply { action = ACTION_PLAY },
                        PendingIntent.FLAG_IMMUTABLE
                    )
                )
            }

            val intent = Intent(this@MusicPlaybackService, MainActivity::class.java)
            val pendingIntent = PendingIntent.getActivity(this@MusicPlaybackService, 0, intent, PendingIntent.FLAG_IMMUTABLE)

            val notification = NotificationCompat.Builder(this@MusicPlaybackService, CHANNEL_ID)
                .setStyle(
                    androidx.media.app.NotificationCompat.MediaStyle()
                        .setMediaSession(mediaSession.sessionToken)
                        .setShowActionsInCompactView(0, 1, 2)
                )
                .setContentTitle(state.title.ifEmpty { "Playing Music" })
                .setContentText(state.artist.ifEmpty { "Aura Downloader" })
                .setSmallIcon(com.auradownloader.app.R.drawable.ic_launcher_foreground)
                .setLargeIcon(bitmap)
                .setContentIntent(pendingIntent)
                .addAction(
                    NotificationCompat.Action(
                        com.auradownloader.app.R.drawable.ic_launcher_foreground,
                        "Prev",
                        PendingIntent.getService(
                            this@MusicPlaybackService,
                            3,
                            Intent(this@MusicPlaybackService, MusicPlaybackService::class.java).apply { action = ACTION_PREVIOUS },
                            PendingIntent.FLAG_IMMUTABLE
                        )
                    )
                )
                .addAction(playPauseAction)
                .addAction(
                    NotificationCompat.Action(
                        com.auradownloader.app.R.drawable.ic_launcher_foreground,
                        "Next",
                        PendingIntent.getService(
                            this@MusicPlaybackService,
                            4,
                            Intent(this@MusicPlaybackService, MusicPlaybackService::class.java).apply { action = ACTION_NEXT },
                            PendingIntent.FLAG_IMMUTABLE
                        )
                    )
                )
                .setOngoing(state.isPlaying)
                .build()

            try {
                if (state.isPlaying) {
                    startForeground(NOTIFICATION_ID, notification)
                } else {
                    ServiceCompat.stopForeground(this@MusicPlaybackService, ServiceCompat.STOP_FOREGROUND_DETACH)
                    val manager = getSystemService(NotificationManager::class.java)
                    manager?.notify(NOTIFICATION_ID, notification)
                }
            } catch (e: Exception) {
                Log.w(TAG, "Notification post failed: ${e.message}")
            }
        }
    }

    private fun playUrl(url: String) {
        if (url.isBlank()) {
            MusicController.updateIsError(true)
            MusicController.updateIsBuffering(false)
            return
        }

        downloadJob?.cancel()
        downloadJob = serviceScope.launch {
            try {
                MusicController.updateIsPrepared(false)
                MusicController.updateIsBuffering(true)
                MusicController.updateIsError(false)

                // If local file, play directly
                if (!url.startsWith("http://") && !url.startsWith("https://")) {
                    playLocalFileOrUri(url)
                    return@launch
                }

                // Remote stream handling: Cache stream to disk using OkHttp to bypass native MediaPlayer streaming bugs
                val cacheKey = Math.abs(url.hashCode()).toString()
                val cachedFile = File(cacheDir, "audio_stream_$cacheKey.mp3")
                val tempFile = File(cacheDir, "audio_stream_$cacheKey.tmp")

                if (cachedFile.exists() && cachedFile.length() > 1024) {
                    Log.d(TAG, "Playing from existing cache: ${cachedFile.absolutePath}")
                    playLocalFileOrUri(cachedFile.absolutePath)
                    return@launch
                }

                val ok = downloadToCache(url, tempFile, cachedFile)
                if (ok && cachedFile.exists() && cachedFile.length() > 0) {
                    playLocalFileOrUri(cachedFile.absolutePath)
                } else {
                    // Fallback to direct network URI if downloading fails
                    playDirectNetworkUri(url)
                }
            } catch (e: Exception) {
                Log.e(TAG, "playUrl exception: ${e.message}")
                MusicController.updateIsError(true)
                MusicController.updateIsBuffering(false)
                releaseWifiLock()
            }
        }
    }

    private suspend fun downloadToCache(url: String, tempFile: File, cachedFile: File): Boolean = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url(url)
                .header("User-Agent", "Mozilla/5.0 (Linux; Android 14; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")
                .header("Accept", "*/*")
                .build()

            val response = httpClient.newCall(request).execute()
            if (!response.isSuccessful) {
                Log.w(TAG, "OkHttp stream fetch failed with code: ${response.code}")
                return@withContext false
            }

            val body = response.body ?: return@withContext false
            val contentLength = body.contentLength()

            if (tempFile.exists()) tempFile.delete()
            val output = FileOutputStream(tempFile)
            val buffer = ByteArray(8192)
            var bytesRead: Int
            var totalRead = 0L

            body.byteStream().use { input ->
                output.use { out ->
                    while (input.read(buffer).also { bytesRead = it } != -1) {
                        if (!isActive) {
                            return@withContext false
                        }
                        out.write(buffer, 0, bytesRead)
                        totalRead += bytesRead
                        if (contentLength > 0) {
                            val percent = ((totalRead * 100) / contentLength).toInt().coerceIn(0, 100)
                            MusicController.updateBufferingPercent(percent)
                        }
                    }
                }
            }

            if (tempFile.length() > 0) {
                if (cachedFile.exists()) cachedFile.delete()
                tempFile.renameTo(cachedFile)
                return@withContext true
            }
            false
        } catch (e: Exception) {
            Log.w(TAG, "Download to cache error: ${e.message}")
            false
        }
    }

    private fun playLocalFileOrUri(filePath: String) {
        releasePlayer()
        try {
            mediaPlayer = MediaPlayer().apply {
                setWakeMode(applicationContext, PowerManager.PARTIAL_WAKE_LOCK)
                setAudioAttributes(
                    AudioAttributes.Builder()
                        .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                        .setUsage(AudioAttributes.USAGE_MEDIA)
                        .build()
                )

                if (filePath.startsWith("content://")) {
                    setDataSource(applicationContext, Uri.parse(filePath))
                } else {
                    val file = File(filePath)
                    val fis = FileInputStream(file)
                    currentFileInputStream = fis
                    setDataSource(fis.fd)
                }

                prepareAsync()

                setOnPreparedListener { mp ->
                    MusicController.updateIsPrepared(true)
                    MusicController.updateIsBuffering(false)
                    MusicController.updateIsError(false)
                    MusicController.updatePosition(0, mp.duration)
                    if (MusicController.playbackState.value.isPlaying) {
                        mp.start()
                        acquireWifiLock()
                    }
                }

                setOnBufferingUpdateListener { _, percent ->
                    MusicController.updateBufferingPercent(percent)
                }

                setOnSeekCompleteListener { mp ->
                    try {
                        MusicController.updatePosition(mp.currentPosition, mp.duration)
                    } catch (e: Exception) {}
                }

                setOnCompletionListener { mp ->
                    if (MusicController.playbackState.value.isLooping) {
                        try {
                            mp.seekTo(0)
                            mp.start()
                            acquireWifiLock()
                            MusicController.updatePosition(0, mp.duration)
                            MusicController.updateIsPlaying(true)
                        } catch (e: Exception) {
                            releaseWifiLock()
                            MusicController.updateIsPlaying(false)
                        }
                    } else {
                        try {
                            val dur = mp.duration
                            MusicController.updatePosition(dur, dur)
                        } catch (e: Exception) {}
                        releaseWifiLock()
                        MusicController.updateIsPlaying(false)
                    }
                }

                setOnErrorListener { mp, what, extra ->
                    Log.e(TAG, "Local MediaPlayer error: what=$what, extra=$extra")
                    MusicController.updateIsError(true)
                    MusicController.updateIsBuffering(false)
                    MusicController.updateIsPlaying(false)
                    releaseWifiLock()
                    try {
                        mp.reset()
                    } catch (e: Exception) {}
                    true
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "playLocalFileOrUri error: ${e.message}")
            MusicController.updateIsError(true)
            MusicController.updateIsBuffering(false)
        }
    }

    private fun playDirectNetworkUri(url: String) {
        releasePlayer()
        try {
            mediaPlayer = MediaPlayer().apply {
                setWakeMode(applicationContext, PowerManager.PARTIAL_WAKE_LOCK)
                setAudioAttributes(
                    AudioAttributes.Builder()
                        .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                        .setUsage(AudioAttributes.USAGE_MEDIA)
                        .build()
                )

                val headers = mapOf(
                    "User-Agent" to "Mozilla/5.0 (Linux; Android 14; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                    "Accept" to "*/*"
                )
                setDataSource(applicationContext, Uri.parse(url), headers)
                prepareAsync()

                setOnPreparedListener { mp ->
                    MusicController.updateIsPrepared(true)
                    MusicController.updateIsBuffering(false)
                    MusicController.updateIsError(false)
                    MusicController.updatePosition(0, mp.duration)
                    if (MusicController.playbackState.value.isPlaying) {
                        mp.start()
                        acquireWifiLock()
                    }
                }

                setOnBufferingUpdateListener { _, percent ->
                    MusicController.updateBufferingPercent(percent)
                }

                setOnSeekCompleteListener { mp ->
                    try {
                        MusicController.updatePosition(mp.currentPosition, mp.duration)
                    } catch (e: Exception) {}
                }

                setOnCompletionListener { mp ->
                    if (MusicController.playbackState.value.isLooping) {
                        try {
                            mp.seekTo(0)
                            mp.start()
                            acquireWifiLock()
                            MusicController.updatePosition(0, mp.duration)
                            MusicController.updateIsPlaying(true)
                        } catch (e: Exception) {
                            releaseWifiLock()
                            MusicController.updateIsPlaying(false)
                        }
                    } else {
                        try {
                            val dur = mp.duration
                            MusicController.updatePosition(dur, dur)
                        } catch (e: Exception) {}
                        releaseWifiLock()
                        MusicController.updateIsPlaying(false)
                    }
                }

                setOnErrorListener { mp, what, extra ->
                    Log.e(TAG, "Direct network MediaPlayer error: what=$what, extra=$extra")
                    MusicController.updateIsError(true)
                    MusicController.updateIsBuffering(false)
                    MusicController.updateIsPlaying(false)
                    releaseWifiLock()
                    try {
                        mp.reset()
                    } catch (e: Exception) {}
                    true
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "playDirectNetworkUri error: ${e.message}")
            MusicController.updateIsError(true)
            MusicController.updateIsBuffering(false)
        }
    }
}

data class MusicState(
    val url: String = "",
    val title: String = "",
    val artist: String = "",
    val thumbnailUrl: String = "",
    val isPlaying: Boolean = false,
    val isPrepared: Boolean = false,
    val isBuffering: Boolean = false,
    val bufferingPercent: Int = 0,
    val isError: Boolean = false,
    val positionMs: Int = 0,
    val durationMs: Int = 0,
    val isLooping: Boolean = false
)

sealed class MusicCommand {
    data class PlayUrl(val url: String) : MusicCommand()
    object Play : MusicCommand()
    object Pause : MusicCommand()
    object Next : MusicCommand()
    object Previous : MusicCommand()
    data class SeekTo(val position: Int) : MusicCommand()
    object Stop : MusicCommand()
    object None : MusicCommand()
}

object MusicController {
    private var bufferingJob: kotlinx.coroutines.Job? = null
    private val _playbackState = MutableStateFlow(MusicState())
    val playbackState: StateFlow<MusicState> = _playbackState.asStateFlow()

    private val _commandFlow = MutableStateFlow<MusicCommand>(MusicCommand.None)
    val commandFlow: StateFlow<MusicCommand> = _commandFlow.asStateFlow()

    fun playTrack(url: String, title: String, artist: String?, thumbnailUrl: String) {
        _playbackState.value = _playbackState.value.copy(isBuffering = true, bufferingPercent = 0, isError = false)
        startSimulatedBuffering()
        _playbackState.value = _playbackState.value.copy(
            url = url,
            title = title,
            artist = artist ?: "",
            thumbnailUrl = thumbnailUrl,
            isPlaying = true,
            isBuffering = true,
            isPrepared = false,
            isError = false,
            positionMs = 0
        )
        _commandFlow.value = MusicCommand.PlayUrl(url)
    }

    fun play() {
        val state = _playbackState.value
        if (state.durationMs > 0 && state.positionMs >= state.durationMs - 500) {
            _playbackState.value = state.copy(isPlaying = true, positionMs = 0, isError = false)
        } else {
            _playbackState.value = state.copy(isPlaying = true, isError = false)
        }
        _commandFlow.value = MusicCommand.Play
    }

    fun pause() {
        _playbackState.value = _playbackState.value.copy(isPlaying = false)
        _commandFlow.value = MusicCommand.Pause
    }

    fun toggleLooping() {
        _playbackState.value = _playbackState.value.copy(isLooping = !_playbackState.value.isLooping)
    }

    fun next() {
        _commandFlow.value = MusicCommand.Next
    }

    fun previous() {
        _commandFlow.value = MusicCommand.Previous
    }

    fun seekTo(position: Int) {
        _playbackState.value = _playbackState.value.copy(positionMs = position)
        _commandFlow.value = MusicCommand.SeekTo(position)
    }

    fun stop() {
        _playbackState.value = MusicState()
        _commandFlow.value = MusicCommand.Stop
    }

    fun updateIsPlaying(isPlaying: Boolean) {
        _playbackState.value = _playbackState.value.copy(isPlaying = isPlaying)
    }

    fun updatePosition(position: Int, duration: Int) {
        _playbackState.value = _playbackState.value.copy(positionMs = position, durationMs = duration)
    }

    fun updateIsPrepared(isPrepared: Boolean) {
        _playbackState.value = _playbackState.value.copy(isPrepared = isPrepared)
    }

    fun updateIsBuffering(isBuffering: Boolean) {
        _playbackState.value = _playbackState.value.copy(isBuffering = isBuffering)
        if (isBuffering) {
            startSimulatedBuffering()
        } else {
            bufferingJob?.cancel()
            _playbackState.value = _playbackState.value.copy(bufferingPercent = 100)
        }
    }

    fun updateBufferingPercent(percent: Int) {
        if (percent > _playbackState.value.bufferingPercent) {
            _playbackState.value = _playbackState.value.copy(bufferingPercent = percent)
        }
    }

    private fun startSimulatedBuffering() {
        bufferingJob?.cancel()
        bufferingJob = kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.IO).launch {
            var current = _playbackState.value.bufferingPercent.toFloat()
            while (_playbackState.value.isBuffering && current < 95f) {
                kotlinx.coroutines.delay(100)
                current += (100f - current) * 0.08f
                val p = current.toInt()
                if (p > _playbackState.value.bufferingPercent) {
                    _playbackState.value = _playbackState.value.copy(bufferingPercent = p)
                }
            }
        }
    }

    fun updateIsError(isError: Boolean) {
        _playbackState.value = _playbackState.value.copy(isError = isError)
    }
}
