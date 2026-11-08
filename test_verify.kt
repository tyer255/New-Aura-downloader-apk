import java.net.HttpURLConnection
import java.net.URL

fun main() {
    val urlStr = "https://aura-downloader-yg40.onrender.com/api/spotify-resolve?trackId=5CEVkJ1Ggj0e1wa0IEOARc&title=Test&stream=true"
    val url = URL(urlStr)
    val conn = url.openConnection() as HttpURLConnection
    conn.requestMethod = "GET"
    conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    conn.setRequestProperty("Range", "bytes=0-1024")
    
    try {
        println("Code: ${conn.responseCode}")
        println("Content-Type: ${conn.contentType}")
    } catch (e: Exception) {
        println("Error: ${e.message}")
    }
}
