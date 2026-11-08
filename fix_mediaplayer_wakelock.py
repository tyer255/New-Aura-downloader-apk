import re

with open("app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt", "r") as f:
    content = f.read()

# Add import if not present
if "import android.os.PowerManager" not in content:
    content = content.replace("import android.media.MediaPlayer", "import android.media.MediaPlayer\\nimport android.os.PowerManager")

old_mp = """        mediaPlayer = MediaPlayer().apply {
            setAudioAttributes("""

new_mp = """        mediaPlayer = MediaPlayer().apply {
            setWakeMode(applicationContext, PowerManager.PARTIAL_WAKE_LOCK)
            setAudioAttributes("""

content = content.replace(old_mp, new_mp)

with open("app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt", "w") as f:
    f.write(content)

