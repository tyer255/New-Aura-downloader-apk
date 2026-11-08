import re

with open("app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt", "r") as f:
    content = f.read()

# 1. Update playback state actions
old_actions = """        val playbackStateBuilder = PlaybackStateCompat.Builder()
            .setActions(
                PlaybackStateCompat.ACTION_PLAY or
                PlaybackStateCompat.ACTION_PAUSE or
                PlaybackStateCompat.ACTION_SKIP_TO_NEXT or
                PlaybackStateCompat.ACTION_SKIP_TO_PREVIOUS or
                PlaybackStateCompat.ACTION_STOP
            )"""

new_actions = """        val playbackStateBuilder = PlaybackStateCompat.Builder()
            .setActions(
                PlaybackStateCompat.ACTION_PLAY or
                PlaybackStateCompat.ACTION_PAUSE or
                PlaybackStateCompat.ACTION_SKIP_TO_NEXT or
                PlaybackStateCompat.ACTION_SKIP_TO_PREVIOUS or
                PlaybackStateCompat.ACTION_STOP or
                PlaybackStateCompat.ACTION_SEEK_TO
            )"""

content = content.replace(old_actions, new_actions)

# 2. Add duration to metadata
old_metadata = """            val metadataBuilder = MediaMetadataCompat.Builder()
                .putString(MediaMetadataCompat.METADATA_KEY_TITLE, state.title)
                .putString(MediaMetadataCompat.METADATA_KEY_ARTIST, state.artist)"""

new_metadata = """            val metadataBuilder = MediaMetadataCompat.Builder()
                .putString(MediaMetadataCompat.METADATA_KEY_TITLE, state.title)
                .putString(MediaMetadataCompat.METADATA_KEY_ARTIST, state.artist)
                .putLong(MediaMetadataCompat.METADATA_KEY_DURATION, state.durationMs.toLong())"""

content = content.replace(old_metadata, new_metadata)

# 3. Handle onSeekTo in callback
old_callback = """        override fun onStop() {
            MusicController.stop()
        }
    }"""

new_callback = """        override fun onStop() {
            MusicController.stop()
        }

        override fun onSeekTo(pos: Long) {
            MusicController.seekTo(pos.toInt())
        }
    }"""

content = content.replace(old_callback, new_callback)

with open("app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt", "w") as f:
    f.write(content)
