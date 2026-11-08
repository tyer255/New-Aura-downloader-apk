val url = "http://localhost:3000/api/local-audio/test.mp3"
val baseBackend = "https://backend-url.com"
val fixed = url.replace(Regex("^http://(localhost|127\\.0\\.0\\.1)(:\\d+)?"), baseBackend)
println(fixed)
