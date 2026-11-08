import kotlin.text.Regex

fun main() {
    val html = """<script id="__NEXT_DATA__" type="application/json">{"props":{"pageProps":{"state":{"data":{"entity":{"type":"track","name":"Never Gonna Give You Up","audioPreview":{"url":"https://p.scdn.co/mp3-preview/b4c682084c3fd05538726d0a126b7e14b6e92c83"}}}}}}"""
    val entityRegex = Regex(""""entity":(\{.*?\}),"*""")
    val entityMatch = entityRegex.find(html)
    println("Match: ${entityMatch?.groupValues?.getOrNull(1)}")
}
