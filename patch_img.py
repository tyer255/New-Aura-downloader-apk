import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

# Fix the label parsing in fetchBackendApi
old_label = r'val qLabel = item\.optString\("label", item\.optString\("resolution", item\.optString\("type", "Download"\)\)\)'
new_label = r'''var qLabel = item.optString("label", item.optString("resolution", item.optString("type", "Download")))
                    if (qLabel.equals("image", ignoreCase = true) && qUrl.contains(".mp4", ignoreCase = true)) {
                        qLabel = "Video (MP4)"
                    } else if (qLabel.equals("video", ignoreCase = true)) {
                        qLabel = "Video (MP4)"
                    } else if (qLabel.equals("image", ignoreCase = true) && (qUrl.contains(".jpg", ignoreCase = true) || qUrl.contains(".png", ignoreCase = true) || qUrl.contains("thumb", ignoreCase = true) || qUrl.contains("image", ignoreCase = true))) {
                        qLabel = "Image (JPG)"
                    }'''
content = content.replace(old_label, new_label)

# Ensure rootUrl gets added correctly even if the url matches one of the qualities,
# but we just want to avoid duplicate URLs. We can add it as "Download High Quality" ONLY if not present,
# but actually if it IS present, we might want to rename it?
# Actually, if qs already has it, it won't add it. BUT if the user wants MP4 and the only one is "Video (MP4)", that's fine! The issue was it was labeled "image" which confused the user.

# Fix the pre-fetching (replace `launch(Dispatchers.IO) { context.imageLoader.execute(request) }` with `context.imageLoader.execute(request)`)
content = content.replace("launch(Dispatchers.IO) { context.imageLoader.execute(request) }", "withContext(Dispatchers.IO) { context.imageLoader.execute(request) }")

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
