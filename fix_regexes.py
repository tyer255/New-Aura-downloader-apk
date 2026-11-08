with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "val spotifyRegex =" in line:
        lines[i] = '    val spotifyRegex: kotlin.text.Regex = kotlin.text.Regex("(?:spotify\\\\.com\\\\/(?:[a-zA-Z0-9-]+\\\\/" + ")?|spotify:)(track|playlist|album|artist)[:\\\\/]([a-zA-Z0-9]{22})")\n'
    if "val nextDataRegex =" in line:
        lines[i] = '            val nextDataRegex: kotlin.text.Regex = kotlin.text.Regex("<script id=\\"__NEXT_DATA__\\" type=\\"application/json\\">(.*?)</script>", setOf(RegexOption.DOT_MATCHES_ALL))\n'

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.writelines(lines)

print("Replaced regex lines successfully")
