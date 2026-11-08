import java.net.URL
import java.net.URLEncoder

fun main() {
    val query = "Rick Astley Never Gonna Give You Up"
    val encoded = URLEncoder.encode(query, "UTF-8")
    val url = "https://www.youtube.com/results?search_query=\$encoded"
    val html = URL(url).readText()
    val regex = "\"videoId\":\"([a-zA-Z0-9_-]{11})\"".toRegex()
    val match = regex.find(html)
    println("Video ID: \${match?.groupValues?.get(1)}")
}
