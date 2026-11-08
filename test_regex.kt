import kotlin.text.Regex

fun main() {
    val trackRegex = Regex("""(?:spotify\.com/(?:[a-zA-Z0-9-]+/)?track/|spotify:track:)([a-zA-Z0-9]{22})""")
    val url = "https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT"
    println(trackRegex.find(url)?.groupValues?.getOrNull(1))
}
