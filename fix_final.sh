sed -i 's/fun SettingsScreen(isDarkMode: Boolean, onToggleDarkMode: () -> Unit) {/fun SettingsScreen(isDarkMode: Boolean, onToggleDarkMode: () -> Unit) {\n    val context = androidx.compose.ui.platform.LocalContext.current/g' app/src/main/java/com/auradownloader/app/MainActivity.kt

sed -i 's/fun SpotifyMusicPlayer(/fun SpotifyMusicPlayer(\n    val context = androidx.compose.ui.platform.LocalContext.current,/g' app/src/main/java/com/auradownloader/app/MainActivity.kt

sed -i '1s/^/import androidx.compose.ui.zIndex.zIndex\n/' app/src/main/java/com/auradownloader/app/MainActivity.kt
