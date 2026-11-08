cat << 'INNER_EOF' > app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt
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
import android.os.PowerManager
import android.net.wifi.WifiManager
import android.net.Uri
import android.os.Build
import android.os.IBinder
import android.support.v4.media.MediaMetadataCompat
import android.support.v4.media.session.MediaSessionCompat
import android.support.v4.media.session.PlaybackStateCompat
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import coil.ImageLoader
import coil.request.ImageRequest
import coil.request.SuccessResult
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class MusicPlaybackService : Service() {
    companion object {
        private const val CHANNEL_ID = "media_playback_channel"
        private const val NOTIFICATION_ID = 1
        const val ACTION_PLAY = "com.auradownloader.app.ACTION_PLAY"
        const val ACTION_PAUSE = "com.auradownloader.app.ACTION_PAUSE"
        const val ACTION_NEXT = "com.auradownloader.app.ACTION_NEXT"
        const val ACTION_PREVIOUS = "com.auradownloader.app.ACTION_PREVIOUS"
        const val ACTION_STOP = "com.auradownloader.app.ACTION_STOP"
    }

    private var mediaPlayer: MediaPlayer? = null
    private var wifiLock: WifiManager.WifiLock? = null
    private lateinit var mediaSession: MediaSessionCompat
    private val serviceJob = SupervisorJob()
    private val serviceScope = CoroutineScope(Dispatchers.Main + serviceJob)

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        val wifiManager = applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
        wifiLock = wifiManager.createWifiLock(WifiManager.WIFI_MODE_FULL_HIGH_PERF, "MusicPlaybackServiceWifiLock")
        mediaSession = MediaSessionCompat(this, "MusicPlaybackService").apply {
            setCallback(mediaSessionCallback)
            isActive = true
        }

        // Observe the central music controller state
        serviceScope.launch {
            var lastState: MusicState? = null
            MusicController.playbackState.collect { state ->
                // Update notification only if essential fields change or position jumped by a lot (user seek)
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
                    is MusicCommand.Play -> mediaPlayer?.let { mp ->
                        if (mp.duration > 0 && mp.currentPosition >= mp.duration - 500) {
                            mp.seekTo(0)
                            MusicController.updatePosition(0, mp.duration)
                        }
                        mp.start()
                        MusicController.updatePosition(mp.currentPosition, mp.duration)
                    }
                    is MusicCommand.Pause -> mediaPlayer?.pause()
                    is MusicCommand.Next -> mediaPlayer?.let { mp ->
                        val newPos = (mp.currentPosition + 5000).coerceAtMost(mp.duration)
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                            mp.seekTo(newPos.toLong(), MediaPlayer.SEEK_CLOSEST)
                        } else {
                            mp.seekTo(newPos)
                        }
                        MusicController.updatePosition(newPos, mp.duration)
                    }
                    is MusicCommand.Previous -> mediaPlayer?.let { mp ->
                        val newPos = (mp.currentPosition - 5000).coerceAtLeast(0)
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                            mp.seekTo(newPos.toLong(), MediaPlayer.SEEK_CLOSEST)
                        } else {
                            mp.seekTo(newPos)
                        }
                        MusicController.updatePosition(newPos, mp.duration)
                    }
                    is MusicCommand.SeekTo -> mediaPlayer?.let { mp ->
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                            mp.seekTo(cmd.position.toLong(), MediaPlayer.SEEK_CLOSEST)
                        } else {
                            mp.seekTo(cmd.position)
                        }
                        MusicController.updatePosition(cmd.position, mp.duration)
                    }
                    is MusicCommand.Stop -> stopSelf()
                    else -> {}
                }
            }
        }
        
        // Start updating position
        serviceScope.launch {
            while (isActive) {
                mediaPlayer?.let { mp ->
                    try {
                        if (mp.isPlaying) {
                            val pos = mp.currentPosition
                            val dur = mp.duration
                            MusicController.updatePosition(pos, dur)
                        }
                    } catch (e: Exception) {
                        e.printStackTrace()
                    }
                }
                delay(100L)
            }
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
        mediaPlayer?.release()
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
                val loader = ImageLoader(this@MusicPlaybackService)
                val req = ImageRequest.Builder(this@MusicPlaybackService)
                    .data(state.thumbnailUrl)
                    .size(256)
                    .build()
                val result = loader.execute(req)
                if (result is SuccessResult) {
                    bitmap = (result.drawable as? BitmapDrawable)?.bitmap
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
                .setContentTitle(state.title)
                .setContentText(state.artist)
                .setSmallIcon(com.auradownloader.app.R.drawable.ic_launcher_foreground)
                .setLargeIcon(bitmap)
                .setContentIntent(pendingIntent)
                .addAction(NotificationCompat.Action(com.auradownloader.app.R.drawable.ic_launcher_foreground, "Prev", PendingIntent.getService(this@MusicPlaybackService, 3, Intent(this@MusicPlaybackService, MusicPlaybackService::class.java).apply { action = ACTION_PREVIOUS }, PendingIntent.FLAG_IMMUTABLE)))
                .addAction(playPauseAction)
                .addAction(NotificationCompat.Action(com.auradownloader.app.R.drawable.ic_launcher_foreground, "Next", PendingIntent.getService(this@MusicPlaybackService, 4, Intent(this@MusicPlaybackService, MusicPlaybackService::class.java).apply { action = ACTION_NEXT }, PendingIntent.FLAG_IMMUTABLE)))
                .setOngoing(state.isPlaying)
                .build()

            try {
                startForeground(NOTIFICATION_ID, notification)
                if (!state.isPlaying) {
                    stopForeground(false)
                }
            } catch (e: Exception) {}
        }
    }

    private fun playUrl(url: String) {
        try {
            mediaPlayer?.release()
            mediaPlayer = MediaPlayer().apply {
                setWakeMode(applicationContext, PowerManager.PARTIAL_WAKE_LOCK)
                setAudioAttributes(AudioAttributes.Builder()
                    .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                    .setUsage(AudioAttributes.USAGE_MEDIA)
                    .build())
                setDataSource(url)
                prepareAsync()
                
                setOnPreparedListener { mp ->
                    MusicController.updateIsPrepared(true)
                    MusicController.updateIsBuffering(false)
                    MusicController.updatePosition(0, mp.duration)
                    if (MusicController.playbackState.value.isPlaying) {
                        mp.start()
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
                            MusicController.updatePosition(0, mp.duration)
                            MusicController.updateIsPlaying(true)
                        } catch (e: Exception) {
                            MusicController.updateIsPlaying(false)
                        }
                    } else {
                        try {
                            val dur = mp.duration
                            MusicController.updatePosition(dur, dur)
                        } catch (e: Exception) {}
                        MusicController.updateIsPlaying(false)
                    }
                }
                setOnErrorListener { _, _, _ ->
                    MusicController.updateIsError(true)
                    MusicController.updateIsPlaying(false)
                    true
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
            MusicController.updateIsError(true)
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
        _playbackState.value = _playbackState.value.copy(isBuffering = true, bufferingPercent = 0)
        startSimulatedBuffering()
        _playbackState.value = _playbackState.value.copy(
            url = url,
            title = title,
            artist = artist ?: "",
            thumbnailUrl = thumbnailUrl,
            isPlaying = true,
            isBuffering = true,
            positionMs = 0
        )
        _commandFlow.value = MusicCommand.PlayUrl(url)
    }

    fun play() {
        val state = _playbackState.value
        if (state.durationMs > 0 && state.positionMs >= state.durationMs - 500) {
            _playbackState.value = state.copy(isPlaying = true, positionMs = 0)
        } else {
            _playbackState.value = state.copy(isPlaying = true)
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
INNER_EOF
