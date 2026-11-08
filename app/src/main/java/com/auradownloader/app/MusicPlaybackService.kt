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
import android.net.wifi.WifiManager
import android.net.Uri
import android.os.Build
import android.os.IBinder
import android.util.Log
import android.support.v4.media.MediaMetadataCompat
import android.support.v4.media.session.MediaSessionCompat
import android.support.v4.media.session.PlaybackStateCompat
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import androidx.media3.common.AudioAttributes
import androidx.media3.common.C
import androidx.media3.common.MediaItem
import androidx.media3.common.MimeTypes
import androidx.media3.common.PlaybackException
import androidx.media3.common.PlaybackParameters
import androidx.media3.common.Player
import androidx.media3.datasource.DefaultHttpDataSource
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.source.ProgressiveMediaSource
import coil.ImageLoader
import coil.request.ImageRequest
import coil.request.SuccessResult
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow

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

    private var exoPlayer: ExoPlayer? = null
    private var wifiLock: WifiManager.WifiLock? = null
    private lateinit var mediaSession: MediaSessionCompat
    private val serviceJob = SupervisorJob()
    private val serviceScope = CoroutineScope(Dispatchers.Main + serviceJob)

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        try {
            startForeground(NOTIFICATION_ID, createInitialNotification())
        } catch (e: Exception) {
            Log.e(TAG, "Initial startForeground error: ${e.message}")
        }

        try {
            val wifiManager = applicationContext.getSystemService(Context.WIFI_SERVICE) as? WifiManager
            wifiLock = wifiManager?.createWifiLock(WifiManager.WIFI_MODE_FULL_HIGH_PERF, "MusicPlaybackServiceWifiLock")
            wifiLock?.acquire()
        } catch (_: Exception) {}

        mediaSession = MediaSessionCompat(this, "MusicPlaybackService").apply {
            setCallback(mediaSessionCallback)
            isActive = true
        }

        initializeExoPlayer()

        // Observe the central music controller state
        serviceScope.launch {
            var lastState: MusicState? = null
            MusicController.playbackState.collect { state ->
                val isSeek = lastState != null && Math.abs(state.positionMs - (lastState!!.positionMs)) > 1500
                if (lastState?.url != state.url || 
                    lastState?.isPlaying != state.isPlaying || 
                    lastState?.isBuffering != state.isBuffering || 
                    lastState?.durationMs != state.durationMs ||
                    isSeek) {
                    
                    updateNotificationAndSession(state)
                    lastState = state
                }
            }
        }
        
        serviceScope.launch {
            MusicController.commandFlow.collect { cmd ->
                when (cmd) {
                    is MusicCommand.PlayUrl -> playUrl(cmd.url)
                    is MusicCommand.Play -> exoPlayer?.let { player ->
                        try {
                            if (MusicController.playbackState.value.isPrepared) {
                                val dur = player.duration
                                if (dur > 0 && player.currentPosition >= dur - 500) {
                                    player.seekTo(0)
                                    MusicController.updatePosition(0, dur.toInt())
                                }
                                player.play()
                                MusicController.updateIsPlaying(true)
                                MusicController.updatePosition(player.currentPosition.toInt(), dur.toInt())
                            } else {
                                // Just ensure the intention is to play once prepared.
                                // It might be in the middle of resolving/buffering right now.
                                player.playWhenReady = true
                                MusicController.updateIsPlaying(true)
                                
                                val currentUrl = MusicController.playbackState.value.url
                                if (currentUrl.isNotBlank() && !MusicController.playbackState.value.isBuffering) {
                                    playUrl(currentUrl)
                                }
                            }
                        } catch (e: Exception) {
                            Log.e(TAG, "Error playing: ${e.message}")
                        }
                    }
                    is MusicCommand.Pause -> exoPlayer?.let { player ->
                        try {
                            player.pause()
                            MusicController.updateIsPlaying(false)
                        } catch (e: Exception) {
                            Log.e(TAG, "Error pausing: ${e.message}")
                        }
                    }
                    is MusicCommand.Next -> exoPlayer?.let { player ->
                        try {
                            if (MusicController.playbackState.value.isPrepared) {
                                val dur = player.duration
                                val newPos = (player.currentPosition + 5000).coerceAtMost(if (dur > 0) dur else Long.MAX_VALUE)
                                player.seekTo(newPos)
                                MusicController.updatePosition(newPos.toInt(), dur.toInt())
                            }
                        } catch (e: Exception) {
                            Log.e(TAG, "Error seeking next: ${e.message}")
                        }
                    }
                    is MusicCommand.Previous -> exoPlayer?.let { player ->
                        try {
                            if (MusicController.playbackState.value.isPrepared) {
                                val newPos = (player.currentPosition - 5000).coerceAtLeast(0)
                                player.seekTo(newPos)
                                MusicController.updatePosition(newPos.toInt(), player.duration.toInt())
                            }
                        } catch (e: Exception) {
                            Log.e(TAG, "Error seeking previous: ${e.message}")
                        }
                    }
                    is MusicCommand.SeekTo -> exoPlayer?.let { player ->
                        try {
                            if (MusicController.playbackState.value.isPrepared) {
                                player.seekTo(cmd.position.toLong())
                                MusicController.updatePosition(cmd.position, player.duration.toInt())
                            }
                        } catch (e: Exception) {
                            Log.e(TAG, "Error seeking: ${e.message}")
                        }
                    }
                    is MusicCommand.Stop -> {
                        try {
                            exoPlayer?.stop()
                            exoPlayer?.clearMediaItems()
                            stopForeground(true)
                            stopSelf()
                        } catch (e: Exception) {
                            Log.e(TAG, "Error stopping: ${e.message}")
                        }
                    }
                    else -> {}
                }
            }
        }
        
        // Continuous position updater loop
        serviceScope.launch {
            while (isActive) {
                exoPlayer?.let { player ->
                    try {
                        if (MusicController.playbackState.value.isPrepared && player.isPlaying) {
                            val pos = player.currentPosition.toInt()
                            val dur = player.duration.takeIf { it > 0 }?.toInt() ?: MusicController.playbackState.value.durationMs
                            MusicController.updatePosition(pos, dur)
                        }
                    } catch (e: Exception) {
                        Log.e(TAG, "Position loop error: ${e.message}")
                    }
                }
                delay(100L)
            }
        }
    }

    private fun initializeExoPlayer() {
        try {
            exoPlayer?.release()
            val loadControl = androidx.media3.exoplayer.DefaultLoadControl.Builder()
                .setBufferDurationsMs(
                    /* minBufferMs = */ 15000,
                    /* maxBufferMs = */ 50000,
                    /* bufferForPlaybackMs = */ 1000,
                    /* bufferForPlaybackAfterRebufferMs = */ 2000
                )
                .build()

            exoPlayer = ExoPlayer.Builder(this)
                .setAudioAttributes(
                    AudioAttributes.Builder()
                        .setUsage(C.USAGE_MEDIA)
                        .setContentType(C.AUDIO_CONTENT_TYPE_MUSIC)
                        .build(),
                    /* handleAudioFocus = */ true
                )
                .setLoadControl(loadControl)
                .setWakeMode(C.WAKE_MODE_NETWORK)
                .build().apply {
                    playbackParameters = PlaybackParameters(1.0f, 1.0f)
                    
                    addListener(object : Player.Listener {
                        @Deprecated("Deprecated in Java")
                        override fun onPlayerStateChanged(playWhenReady: Boolean, playbackState: Int) {
                            val stateName = when (playbackState) {
                                Player.STATE_IDLE -> "STATE_IDLE"
                                Player.STATE_BUFFERING -> "STATE_BUFFERING"
                                Player.STATE_READY -> "STATE_READY"
                                Player.STATE_ENDED -> "STATE_ENDED"
                                else -> "UNKNOWN($playbackState)"
                            }
                            val pos = currentPosition
                            val dur = duration
                            val bufferedPos = bufferedPosition
                            val bufPct = bufferedPercentage
                            Log.d(TAG, "[DIAGNOSTIC] onPlayerStateChanged: playWhenReady=$playWhenReady, state=$stateName, pos=${pos}ms, dur=${dur}ms, buffered=${bufferedPos}ms ($bufPct%)")
                        }

                        override fun onPlaybackStateChanged(playbackState: Int) {
                            val stateName = when (playbackState) {
                                Player.STATE_IDLE -> "STATE_IDLE"
                                Player.STATE_BUFFERING -> "STATE_BUFFERING"
                                Player.STATE_READY -> "STATE_READY"
                                Player.STATE_ENDED -> "STATE_ENDED"
                                else -> "UNKNOWN($playbackState)"
                            }
                            val pos = currentPosition
                            val dur = duration.takeIf { it > 0 } ?: MusicController.playbackState.value.durationMs.toLong()
                            val bufferedPos = bufferedPosition
                            val bufPct = bufferedPercentage
                            Log.d(TAG, "[DIAGNOSTIC] onPlaybackStateChanged: state=$stateName, pos=${pos}ms, dur=${dur}ms, buffered=${bufferedPos}ms ($bufPct%), isPlaying=$isPlaying")

                            when (playbackState) {
                                Player.STATE_READY -> {
                                    try {
                                        wifiLock?.let { if (!it.isHeld) it.acquire() }
                                    } catch (_: Exception) {}

                                    val playerDur = duration.takeIf { it > 0 }?.toInt() ?: MusicController.playbackState.value.durationMs
                                    Log.d(TAG, "ExoPlayer Ready: duration=$playerDur ms, targetDuration=${MusicController.playbackState.value.durationMs} ms, buffered=$bufPct%")
                                    
                                    MusicController.updateIsPrepared(true)
                                    MusicController.updateIsBuffering(false)
                                    MusicController.updateBufferingPercent(100)
                                    MusicController.updateIsError(false)
                                    if (playerDur > 0) {
                                        MusicController.updatePosition(currentPosition.toInt(), playerDur)
                                    }

                                    if (MusicController.playbackState.value.isPlaying || playWhenReady) {
                                        play()
                                        MusicController.updateIsPlaying(true)
                                        updateNotificationAndSession(MusicController.playbackState.value)
                                    }
                                    extractAndPostDiagnostic(currentTracks)
                                }
                                Player.STATE_BUFFERING -> {
                                    Log.d(TAG, "[DIAGNOSTIC] Playback buffering: pos=${pos}ms, buffered=${bufferedPos}ms ($bufPct%)")
                                    MusicController.updateIsBuffering(true)
                                    MusicController.updateBufferingPercent(bufPct)
                                }
                                Player.STATE_ENDED -> {
                                    val expectedDur = MusicController.playbackState.value.durationMs.toLong()
                                    if (expectedDur > 30000 && pos < (expectedDur - 5000)) {
                                        Log.w(TAG, "[DIAGNOSTIC] Premature playback termination detected! Stream ended at ${pos}ms, but expected full duration is ${expectedDur}ms. (Source stream ended or buffer limitation).")
                                    } else {
                                        Log.d(TAG, "[DIAGNOSTIC] Playback ended naturally at ${pos}ms / ${dur}ms")
                                    }

                                    if (MusicController.playbackState.value.isLooping) {
                                        seekTo(0)
                                        play()
                                        MusicController.updatePosition(0, duration.toInt())
                                        MusicController.updateIsPlaying(true)
                                    } else {
                                        val finalDur = duration.takeIf { it > 0 }?.toInt() ?: MusicController.playbackState.value.durationMs
                                        MusicController.updatePosition(finalDur, finalDur)
                                        MusicController.updateIsPlaying(false)
                                    }
                                }
                                Player.STATE_IDLE -> {
                                    Log.d(TAG, "[DIAGNOSTIC] Player entered STATE_IDLE")
                                }
                            }
                        }

                        override fun onPlayWhenReadyChanged(playWhenReady: Boolean, reason: Int) {
                            val reasonStr = when (reason) {
                                Player.PLAY_WHEN_READY_CHANGE_REASON_USER_REQUEST -> "USER_REQUEST"
                                Player.PLAY_WHEN_READY_CHANGE_REASON_AUDIO_FOCUS_LOSS -> "AUDIO_FOCUS_LOSS"
                                Player.PLAY_WHEN_READY_CHANGE_REASON_AUDIO_BECOMING_NOISY -> "AUDIO_BECOMING_NOISY"
                                Player.PLAY_WHEN_READY_CHANGE_REASON_REMOTE -> "REMOTE"
                                Player.PLAY_WHEN_READY_CHANGE_REASON_END_OF_MEDIA_ITEM -> "END_OF_MEDIA_ITEM"
                                else -> "REASON($reason)"
                            }
                            Log.d(TAG, "[DIAGNOSTIC] onPlayWhenReadyChanged: playWhenReady=$playWhenReady, reason=$reasonStr")
                        }

                        override fun onIsLoadingChanged(isLoading: Boolean) {
                            val bufPct = bufferedPercentage
                            Log.d(TAG, "[DIAGNOSTIC] onIsLoadingChanged: isLoading=$isLoading, bufferedPct=$bufPct%, bufferedPos=${bufferedPosition}ms")
                            if (isLoading) {
                                MusicController.updateBufferingPercent(bufPct)
                            }
                        }

                        override fun onTimelineChanged(timeline: androidx.media3.common.Timeline, reason: Int) {
                            val dur = duration.takeIf { it > 0 }?.toInt() ?: 0
                            Log.d(TAG, "[DIAGNOSTIC] onTimelineChanged: duration=$dur ms, windowCount=${timeline.windowCount}")
                            if (dur > 0) {
                                MusicController.updatePosition(currentPosition.toInt(), dur)
                            }
                        }

                        override fun onTracksChanged(tracks: androidx.media3.common.Tracks) {
                            val dur = duration.takeIf { it > 0 }?.toInt() ?: 0
                            Log.d(TAG, "[DIAGNOSTIC] onTracksChanged: groups=${tracks.groups.size}, duration=$dur ms")
                            if (dur > 0) {
                                MusicController.updatePosition(currentPosition.toInt(), dur)
                            }
                            extractAndPostDiagnostic(tracks)
                        }

                        override fun onPlaybackParametersChanged(playbackParameters: PlaybackParameters) {
                            Log.d(TAG, "[DIAGNOSTIC] onPlaybackParametersChanged: speed=${playbackParameters.speed}, pitch=${playbackParameters.pitch}")
                            extractAndPostDiagnostic(currentTracks)
                        }

                        override fun onIsPlayingChanged(isPlaying: Boolean) {
                            Log.d(TAG, "[DIAGNOSTIC] onIsPlayingChanged: isPlaying=$isPlaying, pos=${currentPosition}ms")
                            MusicController.updateIsPlaying(isPlaying)
                            if (isPlaying) {
                                MusicController.updateIsPrepared(true)
                                MusicController.updateIsBuffering(false)
                                MusicController.updateBufferingPercent(100)
                                val dur = duration.takeIf { it > 0 }?.toInt() ?: MusicController.playbackState.value.durationMs
                                if (dur > 0) {
                                    MusicController.updatePosition(currentPosition.toInt(), dur)
                                }
                            }
                        }

                        override fun onPlayerError(error: PlaybackException) {
                            Log.e(TAG, "[DIAGNOSTIC] onPlayerError: errorCode=${error.errorCodeName} (${error.errorCode}), msg=${error.message}, cause=${error.cause?.message}", error)
                            MusicController.updateIsError(true)
                            MusicController.updateIsBuffering(false)
                            MusicController.updateIsPlaying(false)
                            try {
                                wifiLock?.let { if (it.isHeld) it.release() }
                            } catch (_: Exception) {}
                        }
                    })
                }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to init ExoPlayer: ${e.message}", e)
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
        serviceJob.cancel()
        exoPlayer?.release()
        exoPlayer = null
        wifiLock?.takeIf { it.isHeld }?.release()
        mediaSession.release()
        stopForeground(true)
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Media Playback",
                NotificationManager.IMPORTANCE_LOW
            )
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

    private fun createInitialNotification(): Notification {
        val intent = Intent(this, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(this, 0, intent, PendingIntent.FLAG_IMMUTABLE)
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Aura Downloader")
            .setContentText("Media Playback")
            .setSmallIcon(com.auradownloader.app.R.drawable.ic_launcher_foreground)
            .setContentIntent(pendingIntent)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setOngoing(false)
            .build()
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
                    val loader = coil.Coil.imageLoader(this@MusicPlaybackService)
                    val req = ImageRequest.Builder(this@MusicPlaybackService)
                        .data(state.thumbnailUrl)
                        .size(256)
                        .allowHardware(false)
                        .bitmapConfig(Bitmap.Config.ARGB_8888)
                        .build()
                    val result = loader.execute(req)
                    if (result is SuccessResult) {
                        bitmap = (result.drawable as? BitmapDrawable)?.bitmap
                    }
                } catch (_: Exception) {}
            }

            val metaBuilder = MediaMetadataCompat.Builder()
                .putString(MediaMetadataCompat.METADATA_KEY_TITLE, state.title.ifEmpty { "Media Track" })
                .putString(MediaMetadataCompat.METADATA_KEY_ARTIST, state.artist.ifEmpty { "Aura Player" })
                .putLong(MediaMetadataCompat.METADATA_KEY_DURATION, state.durationMs.toLong())
            
            if (bitmap != null) {
                metaBuilder.putBitmap(MediaMetadataCompat.METADATA_KEY_ALBUM_ART, bitmap)
            }
            mediaSession.setMetadata(metaBuilder.build())

            val playPauseAction = if (state.isPlaying) {
                NotificationCompat.Action(com.auradownloader.app.R.drawable.ic_launcher_foreground, "Pause",
                    PendingIntent.getService(this@MusicPlaybackService, 1, Intent(this@MusicPlaybackService, MusicPlaybackService::class.java).apply { action = ACTION_PAUSE }, PendingIntent.FLAG_IMMUTABLE))
            } else {
                NotificationCompat.Action(com.auradownloader.app.R.drawable.ic_launcher_foreground, "Play",
                    PendingIntent.getService(this@MusicPlaybackService, 2, Intent(this@MusicPlaybackService, MusicPlaybackService::class.java).apply { action = ACTION_PLAY }, PendingIntent.FLAG_IMMUTABLE))
            }

            val intent = Intent(this@MusicPlaybackService, MainActivity::class.java)
            val pendingIntent = PendingIntent.getActivity(this@MusicPlaybackService, 0, intent, PendingIntent.FLAG_IMMUTABLE)

            val notification = NotificationCompat.Builder(this@MusicPlaybackService, CHANNEL_ID)
                .setStyle(androidx.media.app.NotificationCompat.MediaStyle()
                    .setMediaSession(mediaSession.sessionToken)
                    .setShowActionsInCompactView(0, 1, 2)
                )
                .setContentTitle(state.title.ifEmpty { "Media Track" })
                .setContentText(state.artist.ifEmpty { "Aura Downloader" })
                .setSmallIcon(com.auradownloader.app.R.drawable.ic_launcher_foreground)
                .setLargeIcon(bitmap)
                .setContentIntent(pendingIntent)
                .addAction(NotificationCompat.Action(com.auradownloader.app.R.drawable.ic_launcher_foreground, "Prev", PendingIntent.getService(this@MusicPlaybackService, 3, Intent(this@MusicPlaybackService, MusicPlaybackService::class.java).apply { action = ACTION_PREVIOUS }, PendingIntent.FLAG_IMMUTABLE)))
                .addAction(playPauseAction)
                .addAction(NotificationCompat.Action(com.auradownloader.app.R.drawable.ic_launcher_foreground, "Next", PendingIntent.getService(this@MusicPlaybackService, 4, Intent(this@MusicPlaybackService, MusicPlaybackService::class.java).apply { action = ACTION_NEXT }, PendingIntent.FLAG_IMMUTABLE)))
                .setOngoing(state.isPlaying)
                .build()

            try {
                val manager = getSystemService(Context.NOTIFICATION_SERVICE) as? NotificationManager
                if (state.isPlaying) {
                    startForeground(NOTIFICATION_ID, notification)
                } else {
                    stopForeground(false)
                    manager?.notify(NOTIFICATION_ID, notification)
                }
            } catch (e: Exception) {
                Log.e(TAG, "Notification update error: ${e.message}")
            }
        }
    }

    private var playJob: Job? = null

    private fun playUrl(url: String) {
        if (url.isBlank()) {
            MusicController.updateIsError(true)
            MusicController.updateIsBuffering(false)
            return
        }

        playJob?.cancel()
        playJob = serviceScope.launch {
            try {
                MusicController.updateIsPrepared(false)
                MusicController.updateIsBuffering(true)
                MusicController.updateBufferingPercent(10)
                MusicController.updateIsError(false)

                val baseBackend = ApiSecurity.getBaseUrl()
                var targetUrl = url

                if (targetUrl.startsWith("/")) {
                    targetUrl = baseBackend + targetUrl
                }

                if (targetUrl.isBlank()) {
                    MusicController.updateIsError(true)
                    MusicController.updateIsBuffering(false)
                    return@launch
                }

                MusicController.updateBufferingPercent(100)
                setupAndPreparePlayer(targetUrl)
            } catch (e: Exception) {
                Log.e(TAG, "Error in playUrl: ${e.message}")
                MusicController.updateIsError(true)
                MusicController.updateIsBuffering(false)
            }
        }
    }

    private fun setupAndPreparePlayer(dataSource: String) {
        try {
            val baseBackend = ApiSecurity.getBaseUrl()
            val finalSource = if (dataSource.startsWith("/")) baseBackend + dataSource else dataSource

            if (finalSource.isBlank()) {
                Log.e(TAG, "Cannot prepare player: blank dataSource")
                MusicController.updateIsError(true)
                MusicController.updateIsBuffering(false)
                return
            }

            val player = exoPlayer ?: run {
                initializeExoPlayer()
                exoPlayer
            } ?: return

            val httpDataSourceFactory = DefaultHttpDataSource.Factory()
                .setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                .setConnectTimeoutMs(30000)
                .setReadTimeoutMs(30000)
                .setAllowCrossProtocolRedirects(true)
                .setDefaultRequestProperties(mapOf(
                    "Accept" to "*/*",
                    "Icy-MetaData" to "1",
                    "X-Aura-Api-Key" to ApiSecurity.API_KEY
                ))

            val mediaItemBuilder = MediaItem.Builder().setUri(Uri.parse(finalSource))
            if (finalSource.contains(".mp3") || finalSource.contains("audio/mpeg") || finalSource.contains("savetube")) {
                mediaItemBuilder.setMimeType(MimeTypes.AUDIO_MPEG)
            } else if (finalSource.contains(".m4a") || finalSource.contains(".mp4") || finalSource.contains("audio/mp4")) {
                mediaItemBuilder.setMimeType(MimeTypes.AUDIO_MP4)
            } else if (finalSource.contains(".aac")) {
                mediaItemBuilder.setMimeType(MimeTypes.AUDIO_AAC)
            }
            val mediaItem = mediaItemBuilder.build()

            val extractorsFactory = androidx.media3.extractor.DefaultExtractorsFactory()

            val mediaSource = androidx.media3.exoplayer.source.ProgressiveMediaSource.Factory(httpDataSourceFactory, extractorsFactory)
                .createMediaSource(mediaItem)

            player.playbackParameters = PlaybackParameters(1.0f, 1.0f)
            player.setMediaSource(mediaSource)
            player.playWhenReady = true
            player.prepare()
            player.play()
        } catch (e: Exception) {
            Log.e(TAG, "ExoPlayer setup failed: ${e.message}", e)
            MusicController.updateIsError(true)
            MusicController.updateIsBuffering(false)
        }
    }

    private fun extractAndPostDiagnostic(tracks: androidx.media3.common.Tracks?) {
        val player = exoPlayer ?: return
        var sampleRate = 0
        var channelCount = 0
        var bitrate = 0
        var mimeType = ""
        var codecs = ""

        if (tracks != null) {
            for (group in tracks.groups) {
                if (group.type == C.TRACK_TYPE_AUDIO && group.isSelected) {
                    for (i in 0 until group.length) {
                        if (group.isTrackSelected(i)) {
                            val format = group.getTrackFormat(i)
                            if (format.sampleRate > 0) sampleRate = format.sampleRate
                            if (format.channelCount > 0) channelCount = format.channelCount
                            val b = if (format.bitrate > 0) format.bitrate else format.averageBitrate
                            if (b > 0) bitrate = b
                            mimeType = format.sampleMimeType ?: format.containerMimeType ?: mimeType
                            codecs = format.codecs ?: codecs
                        }
                    }
                }
            }
        }

        val realDuration = player.duration.takeIf { it > 0 } ?: 0L
        val speed = player.playbackParameters.speed
        val pitch = player.playbackParameters.pitch
        val currentUrl = MusicController.playbackState.value.url

        val container = when {
            mimeType.contains("mp4", ignoreCase = true) || mimeType.contains("aac", ignoreCase = true) -> "AAC (MP4)"
            mimeType.contains("opus", ignoreCase = true) || mimeType.contains("webm", ignoreCase = true) -> "Opus (WebM)"
            mimeType.contains("mpeg", ignoreCase = true) || mimeType.contains("mp3", ignoreCase = true) -> "MPEG Layer-3 (MP3)"
            mimeType.isNotEmpty() -> mimeType
            currentUrl.contains(".mp3") -> "MP3 Audio"
            currentUrl.contains(".m4a") -> "M4A / AAC"
            currentUrl.contains("savetube") -> "High-Res Stream"
            else -> "Audio Stream"
        }

        MusicController.updateStreamDiagnostic(
            StreamDiagnostic(
                sampleRate = sampleRate,
                channelCount = channelCount,
                bitrate = bitrate,
                mimeType = mimeType,
                codecs = codecs,
                playbackSpeed = speed,
                playbackPitch = pitch,
                sourceUrl = currentUrl,
                realStreamDurationMs = realDuration,
                rawContainer = container
            )
        )
    }
}

data class StreamDiagnostic(
    val sampleRate: Int = 0,
    val channelCount: Int = 0,
    val bitrate: Int = 0,
    val mimeType: String = "",
    val codecs: String = "",
    val playbackSpeed: Float = 1.0f,
    val playbackPitch: Float = 1.0f,
    val sourceUrl: String = "",
    val realStreamDurationMs: Long = 0L,
    val rawContainer: String = ""
)

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
    val isLooping: Boolean = false,
    val diagnostic: StreamDiagnostic = StreamDiagnostic()
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

    private val _commandFlow = kotlinx.coroutines.flow.MutableSharedFlow<MusicCommand>(
        replay = 1,
        extraBufferCapacity = 64,
        onBufferOverflow = kotlinx.coroutines.channels.BufferOverflow.DROP_OLDEST
    )
    val commandFlow: kotlinx.coroutines.flow.SharedFlow<MusicCommand> = _commandFlow.asSharedFlow()

    fun playTrack(url: String, title: String, artist: String?, thumbnailUrl: String, durationMs: Int = 0) {
        _playbackState.value = _playbackState.value.copy(
            url = url,
            title = title,
            artist = artist ?: "",
            thumbnailUrl = thumbnailUrl,
            isPlaying = true,
            isBuffering = true,
            isPrepared = false,
            bufferingPercent = 0,
            isError = false,
            positionMs = 0,
            durationMs = durationMs
        )
        startSimulatedBuffering()
        _commandFlow.tryEmit(MusicCommand.PlayUrl(url))
    }

    fun play() {
        val state = _playbackState.value
        if (state.url.isNotEmpty() && (!state.isPrepared || state.isError)) {
            if (state.isBuffering && !state.isError) {
                // Already trying to prepare. Just make sure the UI reflects it's supposed to be playing.
                _playbackState.value = state.copy(isPlaying = true)
                _commandFlow.tryEmit(MusicCommand.Play)
            } else {
                _playbackState.value = state.copy(isPlaying = true, isBuffering = true, isError = false)
                _commandFlow.tryEmit(MusicCommand.PlayUrl(state.url))
            }
        } else {
            if (state.durationMs > 0 && state.positionMs >= state.durationMs - 500) {
                _playbackState.value = state.copy(isPlaying = true, positionMs = 0)
            } else {
                _playbackState.value = state.copy(isPlaying = true)
            }
            _commandFlow.tryEmit(MusicCommand.Play)
        }
    }

    fun pause() {
        _playbackState.value = _playbackState.value.copy(isPlaying = false)
        _commandFlow.tryEmit(MusicCommand.Pause)
    }

    fun toggleLooping() {
        _playbackState.value = _playbackState.value.copy(isLooping = !_playbackState.value.isLooping)
    }

    fun next() {
        _commandFlow.tryEmit(MusicCommand.Next)
    }

    fun previous() {
        _commandFlow.tryEmit(MusicCommand.Previous)
    }

    fun seekTo(position: Int) {
        _playbackState.value = _playbackState.value.copy(positionMs = position)
        _commandFlow.tryEmit(MusicCommand.SeekTo(position))
    }

    fun stop() {
        bufferingJob?.cancel()
        _playbackState.value = MusicState()
        _commandFlow.tryEmit(MusicCommand.Stop)
    }

    fun reset() {
        bufferingJob?.cancel()
        _playbackState.value = MusicState()
        _commandFlow.tryEmit(MusicCommand.Stop)
    }

    fun onExtractionFailed() {
        bufferingJob?.cancel()
        _playbackState.value = MusicState(
            isError = true,
            isPlaying = false,
            isPrepared = false,
            isBuffering = false,
            positionMs = 0,
            durationMs = 0
        )
        _commandFlow.tryEmit(MusicCommand.Stop)
    }

    fun updateIsPlaying(isPlaying: Boolean) {
        _playbackState.value = _playbackState.value.copy(isPlaying = isPlaying)
    }

    fun updatePosition(position: Int, duration: Int) {
        _playbackState.value = _playbackState.value.copy(
            positionMs = position,
            durationMs = if (duration > 0) duration else _playbackState.value.durationMs
        )
    }

    fun updateIsPrepared(isPrepared: Boolean) {
        _playbackState.value = _playbackState.value.copy(isPrepared = isPrepared)
        if (isPrepared) {
            bufferingJob?.cancel()
            _playbackState.value = _playbackState.value.copy(isBuffering = false, bufferingPercent = 100)
        }
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
        val p = percent.coerceIn(0, 100)
        _playbackState.value = _playbackState.value.copy(bufferingPercent = p)
        if (p >= 100) {
            bufferingJob?.cancel()
        }
    }

    private fun startSimulatedBuffering() {
        bufferingJob?.cancel()
        bufferingJob = kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.IO).launch {
            var current = _playbackState.value.bufferingPercent.toFloat().coerceAtLeast(10f)
            while (_playbackState.value.isBuffering && !_playbackState.value.isPrepared && current < 98f) {
                kotlinx.coroutines.delay(80)
                current += (100f - current) * 0.10f
                val p = current.toInt()
                if (p > _playbackState.value.bufferingPercent) {
                    _playbackState.value = _playbackState.value.copy(bufferingPercent = p)
                }
            }
        }
    }

    fun updateIsError(isError: Boolean) {
        if (isError) {
            bufferingJob?.cancel()
            _playbackState.value = _playbackState.value.copy(
                isError = true,
                isBuffering = false,
                isPlaying = false,
                isPrepared = false,
                positionMs = 0,
                durationMs = 0
            )
        } else {
            _playbackState.value = _playbackState.value.copy(isError = false)
        }
    }

    fun updateStreamDiagnostic(diagnostic: StreamDiagnostic) {
        _playbackState.value = _playbackState.value.copy(diagnostic = diagnostic)
    }
}

