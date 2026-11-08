import java.util.regex.Pattern

fun main() {
    val lrcText = """[00:04.50] Ishq mein dil bana hai
[00:07.20] Ishq mein dil fanaa hai"""
    val timeRegex = Regex("""\[(\d{2}):(\d{2}(?:\.\d{1,3})?)]""")
    val lines = lrcText.split("\n")
    for (line in lines) {
        val matches = timeRegex.findAll(line)
        for (match in matches) {
            println("min: ${match.groupValues[1]}, sec: ${match.groupValues[2]}")
        }
    }
}
