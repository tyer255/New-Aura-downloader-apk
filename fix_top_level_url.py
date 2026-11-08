with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    code = f.read()

target = """                val arr = json.optJSONArray("qualities")
                if (arr != null) {"""
replacement = """                val topLevelUrl = json.optString("url", "")
                if (topLevelUrl.isNotEmpty()) {
                    var finalUrl = topLevelUrl
                    if (finalUrl.startsWith("/")) finalUrl = backendUrl.replace("/api/download", "") + finalUrl
                    qs.add(MediaQuality(if (mediaType == "audio") "Download Audio" else "Download File", null, finalUrl))
                }

                val arr = json.optJSONArray("qualities")
                if (arr != null) {"""

if target in code:
    code = code.replace(target, replacement)
    print("Added top-level url parsing")

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(code)
