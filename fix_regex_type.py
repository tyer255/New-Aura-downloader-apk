with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    code = f.read()

target1 = 'val spotifyRegex = "(?:spotify\\.com\\/(?:[a-zA-Z0-9-]+\\/" + ")?|spotify:)(track|playlist|album|artist)[:\\/]([a-zA-Z0-9]{22})".toRegex()'
replace1 = 'val spotifyRegex: kotlin.text.Regex = kotlin.text.Regex("(?:spotify\\\\.com\\\\/(?:[a-zA-Z0-9-]+\\\\/" + ")?|spotify:)(track|playlist|album|artist)[:\\\\/]([a-zA-Z0-9]{22})")'

target2 = 'val nextDataRegex = "<script id=\\"__NEXT_DATA__\\" type=\\"application/json\\">(.*?)</script>".toRegex(RegexOption.DOT_MATCHES_ALL)'
replace2 = 'val nextDataRegex: kotlin.text.Regex = kotlin.text.Regex("<script id=\\"__NEXT_DATA__\\" type=\\"application/json\\">(.*?)</script>", setOf(RegexOption.DOT_MATCHES_ALL))'

code = code.replace(target1, replace1)
code = code.replace(target2, replace2)

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(code)

print("Regex type fix applied!")
