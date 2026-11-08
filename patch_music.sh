sed -i 's/val isBuffering: Boolean = false,/val isBuffering: Boolean = false,\n    val bufferingPercent: Int = 0,/' app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt

sed -i '/fun updateIsBuffering/a\
    fun updateBufferingPercent(percent: Int) {\
        _playbackState.value = _playbackState.value.copy(bufferingPercent = percent)\
    }' app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt

