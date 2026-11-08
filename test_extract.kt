import java.util.regex.Pattern

fun extractYouTubeVideoId(url: String): String? {
    val regex = Regex("""(?<=v=|v/|vi=|vi/|youtu.be/|/shorts/|/e/|/embed/|/v/|/watch\?v=|&v=)([a-zA-Z0-9_-]{11})""")
    return regex.find(url)?.groupValues?.getOrNull(1) ?: Regex("""[a-zA-Z0-9_-]{11}""").find(url)?.value
}
fun main() {
    println(extractYouTubeVideoId("https://youtube.com/shorts/xYrbyhSWJt0?si=rlFztgzP7ahNJn2Q"))
}
