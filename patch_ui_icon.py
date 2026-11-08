import re

with open('app/src/main/java/com/example/MainActivity.kt', 'r') as f:
    content = f.read()

target = '''                                                Icon(if (q.label.contains("Audio")) Icons.Filled.Audiotrack else Icons.Filled.VideoFile, null, modifier = Modifier.size(18.dp), tint = selectedPlatform.brandColor)'''

replace = '''                                                val iconVector = when {
                                                    q.label.contains("Audio", true) || q.label.contains("mp3", true) -> Icons.Filled.Audiotrack
                                                    q.label.contains("Thumbnail", true) || q.label.contains("jpg", true) -> Icons.Filled.Image
                                                    else -> Icons.Filled.VideoFile
                                                }
                                                Icon(iconVector, null, modifier = Modifier.size(18.dp), tint = selectedPlatform.brandColor)'''

content = content.replace(target, replace)
with open('app/src/main/java/com/example/MainActivity.kt', 'w') as f:
    f.write(content)
