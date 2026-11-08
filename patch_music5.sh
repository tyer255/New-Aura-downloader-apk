perl -0777 -pi -e 's/\/\/ old startSimulatedBuffering.*?\n    \}//sg' app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt
perl -0777 -pi -e 's/        startSimulatedBuffering\(\)\n        _playbackState.value = _playbackState.value.copy\(\n            url = url,//g' app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt
