import re

with open("app/src/main/AndroidManifest.xml", "r") as f:
    content = f.read()

old_perms = """    <uses-permission android:name="android.permission.INTERNET" />"""
new_perms = """    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />"""
content = content.replace(old_perms, new_perms)

with open("app/src/main/AndroidManifest.xml", "w") as f:
    f.write(content)
