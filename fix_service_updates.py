import re

with open("app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt", "r") as f:
    content = f.read()

# We'll use a `lastUpdateState` to only update notification/session when necessary.
old_collect = """        // Observe the central music controller state
        serviceScope.launch {
            MusicController.playbackState.collect { state ->
                updateNotificationAndSession(state)
            }
        }"""

new_collect = """        // Observe the central music controller state
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
        }"""

content = content.replace(old_collect, new_collect)

with open("app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt", "w") as f:
    f.write(content)
