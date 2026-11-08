val lrcText = """
[00:19.32] We're no strangers to love
[00:23.21] You know the rules and so do I
"""

val lines = lrcText.split("\n")
val result = mutableListOf<Pair<Long, String>>()

val timeRegex = Regex("""\[(\d{1,3}):(\d{1,2})(?:[:.](\d{1,3}))?\]""")

for (line in lines) {
    val matches = timeRegex.findAll(line).toList()
    if (matches.isNotEmpty()) {
        val cleanText = line.replace(timeRegex, "").trim()
        if (cleanText.isNotEmpty()) {
            for (match in matches) {
                val min = match.groupValues[1].toLong()
                val sec = match.groupValues[2].toLong()
                val fracStr = match.groupValues.getOrNull(3) ?: ""
                val ms = when (fracStr.length) {
                    1 -> fracStr.toLong() * 100
                    2 -> fracStr.toLong() * 10
                    3 -> fracStr.toLong()
                    else -> 0L
                }
                val timeMs = (min * 60000 + sec * 1000 + ms).coerceAtLeast(0L)
                result.add(Pair(timeMs, cleanText))
            }
        }
    }
}
println(result)
