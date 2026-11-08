with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    code = f.read()

# Replace timeout from 12000L to 40000L
code = code.replace("withTimeoutOrNull(12000L)", "withTimeoutOrNull(40000L)")

# Replace outdated aura-download.ai.studio domains with working aura-downloader-yg40.onrender.com
code = code.replace("https://aura-download.ai.studio", "https://aura-downloader-yg40.onrender.com")

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(code)

print("MainActivity.kt updated successfully!")
