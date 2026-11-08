with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    code = f.read()

# Fix Build.VERSION_CODES.21
code = code.replace("Build.VERSION_CODES.21", "Build.VERSION_CODES.LOLLIPOP")

# Fix previewRegexes
regex_block_old = """            val previewRegexes = listOf(
                kotlin.text.Regex("\"audioPreview\":\\s*\\{\\"url\":\\s*\"([^\"]+)\""),
                kotlin.text.Regex("\"preview_url\":\\s*\"([^\"]+)\""),
                kotlin.text.Regex("\"audio_preview_url\":\\s*\"([^\"]+)\""),
                kotlin.text.Regex("(https://p\\.scdn\\.co/mp3-preview/[a-zA-Z0-9]+)")
            )"""

regex_block_new = """            val previewRegexes = listOf(
                Regex("\"audioPreview\":\\\\s*\\\\{\\\\s*\"url\":\\\\s*\"([^\"]+)\""),
                Regex("\"preview_url\":\\\\s*\"([^\"]+)\""),
                Regex("\"audio_preview_url\":\\\\s*\"([^\"]+)\""),
                Regex("(https://p\\\\.scdn\\\\.co/mp3-preview/[a-zA-Z0-9]+)")
            )"""

if regex_block_old in code:
    code = code.replace(regex_block_old, regex_block_new)
    print("Replaced previewRegexes")
else:
    # Fallback replacement if exact whitespace differs
    s_marker = "// Try to extract audio preview from HTML regexes"
    e_marker = "for (pr in previewRegexes)"
    s_idx = code.find(s_marker)
    e_idx = code.find(e_marker)
    if s_idx != -1 and e_idx != -1:
        replacement_chunk = """// Try to extract audio preview from HTML regexes
            val previewRegexes = listOf(
                Regex("\"audioPreview\":\\\\s*\\\\{\\\\s*\"url\":\\\\s*\"([^\"]+)\""),
                Regex("\"preview_url\":\\\\s*\"([^\"]+)\""),
                Regex("\"audio_preview_url\":\\\\s*\"([^\"]+)\""),
                Regex("(https://p\\\\.scdn\\\\.co/mp3-preview/[a-zA-Z0-9]+)")
            )
            """
        code = code[:s_idx] + replacement_chunk + code[e_idx:]
        print("Replaced previewRegexes via marker")

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(code)

print("Saved syntax fixes")
