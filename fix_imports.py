import re

with open("app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt", "r") as f:
    content = f.read()

content = content.replace("import android.media.MediaPlayer\\nimport android.os.PowerManager", "import android.media.MediaPlayer\nimport android.os.PowerManager")

with open("app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt", "w") as f:
    f.write(content)
