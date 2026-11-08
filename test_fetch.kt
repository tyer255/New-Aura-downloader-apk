import org.json.JSONObject

fun main() {
    val jsonStr = """{"success":true,"title":"Up Ayush Counselling 2026 expected date | top 5 bams college in up","url":"/api/proxy-download?url=...","thumbnail":"...","mediaType":"video","source":"vreden","qualities":[{"label":"1080p (MP4)","url":"/api/get-youtube-link?url=...","ext":"mp4","size":"High Definition"}]}"""
    val json = JSONObject(jsonStr)
    val success = json.optBoolean("success", true)
    val title = json.optString("title", json.optString("filename", "Media Download"))
    val thumbnail = json.optString("thumbnail", json.optString("cover", json.optString("image", "")))
    
    println(title)
}
