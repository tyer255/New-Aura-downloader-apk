with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    code = f.read()

target = 'if (initialUrl.contains("/api/get-youtube-link") || initialUrl.contains("get-youtube-link")) {'
replacement = 'if (initialUrl.contains("/api/get-youtube-link") || initialUrl.contains("get-youtube-link") || initialUrl.contains("spotify-resolve")) {'

if target in code:
    code = code.replace(target, replacement)
    with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
        f.write(code)
    print("Updated resolveAndTriggerDownload to handle spotify-resolve")
else:
    print("Target string not found")
