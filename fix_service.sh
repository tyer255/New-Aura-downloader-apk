cat << 'INNER_EOF' >> app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt

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
                NotificationCompat.Action(R.drawable.ic_launcher_foreground, "Pause",
                    PendingIntent.getService(this@MusicPlaybackService, 1, Intent(this@MusicPlaybackService, MusicPlaybackService::class.java).apply { action = ACTION_PAUSE }, PendingIntent.FLAG_IMMUTABLE))
            } else {
                NotificationCompat.Action(R.drawable.ic_launcher_foreground, "Play",
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
                .setSmallIcon(R.drawable.ic_launcher_foreground)
                .setLargeIcon(bitmap)
                .setContentIntent(pendingIntent)
                .addAction(NotificationCompat.Action(R.drawable.ic_launcher_foreground, "Prev", PendingIntent.getService(this@MusicPlaybackService, 3, Intent(this@MusicPlaybackService, MusicPlaybackService::class.java).apply { action = ACTION_PREVIOUS }, PendingIntent.FLAG_IMMUTABLE)))
                .addAction(playPauseAction)
                .addAction(NotificationCompat.Action(R.drawable.ic_launcher_foreground, "Next", PendingIntent.getService(this@MusicPlaybackService, 4, Intent(this@MusicPlaybackService, MusicPlaybackService::class.java).apply { action = ACTION_NEXT }, PendingIntent.FLAG_IMMUTABLE)))
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
INNER_EOF
