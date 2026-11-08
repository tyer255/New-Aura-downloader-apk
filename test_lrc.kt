fun main() {
    val lrcText = "[00:19.51] Line 1\n[00:24.13] Line 2"
    val timeRegex = Regex("""\[(\d{1,3}):(\d{1,2})(?:[:.](\d{1,3}))?\]""")
    for (line in lrcText.split("\n")) {
        val matches = timeRegex.findAll(line).toList()
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
            println("Time: $timeMs")
        }
    }
}
