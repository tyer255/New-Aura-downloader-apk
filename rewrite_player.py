import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

start_idx = content.find("@Composable\nfun SpotifyMusicPlayer")
if start_idx != -1:
    brackets = 0
    in_fun = False
    for i in range(start_idx, len(content)):
        if content[i] == '{':
            brackets += 1
            in_fun = True
        elif content[i] == '}':
            brackets -= 1
        
        if in_fun and brackets == 0:
            end_idx = i + 1
            break
            
old_player = content[start_idx:end_idx]

# We need to replace the old_player with our new implementation.
# But wait, we should also fix the white box issue on the Album Art and the DropdownMenu!

new_player_start = """@Composable
fun SpotifyMusicPlayer(
    title: String,
    artist: String?,
    thumbnailUrl: String,
    audioUrl: String,
    isDarkMode: Boolean
) {
    val context = LocalContext.current
    
    var isLooping by remember { mutableStateOf(false) }
    var isMuted by remember { mutableStateOf(false) }
    var isUserScrubbing by remember { mutableStateOf(false) }
    var sliderPositionMs by remember { mutableFloatStateOf(0f) }
    
    var isMinimized by remember { mutableStateOf(false) }
    var showOptionsMenu by remember { mutableStateOf(false) }
    
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
    
    var activeAudioUrl by remember { mutableStateOf<String?>(null) }
    
    LaunchedEffect(audioUrl, title, artist) {
        activeAudioUrl = resolveSpotifyUrl(audioUrl, title, artist)
    }
    
    val playbackState by MusicController.playbackState.collectAsState()
    
    LaunchedEffect(activeAudioUrl) {
        if (!activeAudioUrl.isNullOrEmpty() && activeAudioUrl != playbackState.url) {
            val intent = Intent(context, MusicPlaybackService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                ContextCompat.startForegroundService(context, intent)
            } else {
                context.startService(intent)
            }
            MusicController.playTrack(activeAudioUrl!!, title, artist, thumbnailUrl)
        }
    }
    
    val isPlaying = playbackState.isPlaying
    val isPrepared = playbackState.isPrepared
    val isBuffering = playbackState.isBuffering
    val isError = playbackState.isError
    val currentPositionMs = playbackState.positionMs
    val durationMs = playbackState.durationMs
    
    val displayMs = if (isUserScrubbing) sliderPositionMs.toInt() else currentPositionMs
"""

# Let's write the whole file manually.
