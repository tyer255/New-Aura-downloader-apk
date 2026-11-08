import re

with open('app/src/main/java/com/example/MainActivity.kt', 'r') as f:
    content = f.read()

target = '''fun guessExtension(url: String, label: String): String {
    val lowerUrl = url.lowercase()
    val lowerLabel = label.lowercase()
    return when {
        lowerUrl.contains(".mp4") || lowerLabel.contains("mp4") || lowerLabel.contains("video") -> "mp4"
        lowerUrl.contains(".mp3") || lowerLabel.contains("audio") || lowerLabel.contains("mp3") -> "mp3"
        lowerUrl.contains(".jpg") || lowerUrl.contains(".jpeg") -> "jpg"
        lowerUrl.contains(".png") -> "png"
        else -> "mp4"
    }
}'''

replace = '''fun guessExtension(url: String, label: String): String {
    val lowerUrl = url.lowercase()
    val lowerLabel = label.lowercase()
    return when {
        lowerLabel.contains("mp3") || lowerLabel.contains("audio") -> "mp3"
        lowerLabel.contains("jpg") || lowerLabel.contains("thumbnail") || lowerUrl.contains(".jpg") || lowerUrl.contains(".jpeg") -> "jpg"
        lowerLabel.contains("png") || lowerUrl.contains(".png") -> "png"
        lowerLabel.contains("mp4") || lowerLabel.contains("video") || lowerUrl.contains(".mp4") -> "mp4"
        else -> "mp4"
    }
}'''

with open('app/src/main/java/com/example/MainActivity.kt', 'w') as f:
    f.write(content.replace(target, replace))
