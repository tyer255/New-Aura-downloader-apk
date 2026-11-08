import re
with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    content = f.read()

target = 'val finalPreviewAudio = if (previewUrl.isNotEmpty()) previewUrl else qualities.firstOrNull { it.url.isNotEmpty() }?.url'
replace = 'val finalPreviewAudio = qualities.firstOrNull { !it.label.contains("Preview", true) && !it.label.contains("Art", true) }?.url ?: previewUrl'

content = content.replace(target, replace)

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(content)
print("done")
