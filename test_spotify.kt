import java.util.regex.Pattern

fun main() {
    val cleanUrl = "https://open.spotify.com/track/0wHYuCTWPntEgWiUVED4wB?si=0Zy-UpIKTmOrdHhjN_4gSw"
    val trackRegex = Regex("""(?:spotify\.com/(?:[a-zA-Z0-9-]+/)?track/|spotify:track:)([a-zA-Z0-9]{22})""")
    val trackId = trackRegex.find(cleanUrl)?.groupValues?.getOrNull(1)
    println("Track ID extracted: " + trackId)
}
