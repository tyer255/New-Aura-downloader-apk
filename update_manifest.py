import re

with open("app/src/main/AndroidManifest.xml", "r") as f:
    content = f.read()

permissions = """
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK" />
"""

service = """
        <service android:name=".MusicPlaybackService"
                 android:exported="false"
                 android:foregroundServiceType="mediaPlayback">
        </service>
"""

if "FOREGROUND_SERVICE" not in content:
    content = content.replace("<uses-permission android:name=\"android.permission.INTERNET\" />", "<uses-permission android:name=\"android.permission.INTERNET\" />" + permissions)

if "MusicPlaybackService" not in content:
    content = content.replace("</application>", service + "\n    </application>")

with open("app/src/main/AndroidManifest.xml", "w") as f:
    f.write(content)
