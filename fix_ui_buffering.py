import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

# Replace the icon inside the Minimized player play/pause
min_icon_old = """                        Icon(
                            imageVector = if (isPlaying) Icons.Filled.Pause else Icons.Filled.PlayArrow,
                            contentDescription = if (isPlaying) "Pause" else "Play",
                            tint = textMain,
                            modifier = Modifier.size(24.dp).padding(start = if (isPlaying) 0.dp else 2.dp)
                        )"""

min_icon_new = """                        if (isBuffering) {
                            CircularProgressIndicator(modifier = Modifier.size(20.dp), color = textMain, strokeWidth = 2.dp)
                        } else {
                            Icon(
                                imageVector = if (isPlaying) Icons.Filled.Pause else Icons.Filled.PlayArrow,
                                contentDescription = if (isPlaying) "Pause" else "Play",
                                tint = textMain,
                                modifier = Modifier.size(24.dp).padding(start = if (isPlaying) 0.dp else 2.dp)
                            )
                        }"""

content = content.replace(min_icon_old, min_icon_new)

# Replace the icon inside the Expanded player play/pause
exp_icon_old = """                            Icon(
                                imageVector = if (isPlaying) Icons.Filled.Pause else Icons.Filled.PlayArrow,
                                contentDescription = if (isPlaying) "Pause" else "Play",
                                tint = textMain,
                                modifier = Modifier.size(40.dp).padding(start = if (isPlaying) 0.dp else 4.dp)
                            )"""

exp_icon_new = """                            if (isBuffering) {
                                CircularProgressIndicator(modifier = Modifier.size(32.dp), color = textMain, strokeWidth = 3.dp)
                            } else {
                                Icon(
                                    imageVector = if (isPlaying) Icons.Filled.Pause else Icons.Filled.PlayArrow,
                                    contentDescription = if (isPlaying) "Pause" else "Play",
                                    tint = textMain,
                                    modifier = Modifier.size(40.dp).padding(start = if (isPlaying) 0.dp else 4.dp)
                                )
                            }"""

content = content.replace(exp_icon_old, exp_icon_new)

# Also let's update the click listeners so they can pause while buffering
min_click_old = """                            .clickable {
                                    if (isPrepared) {
                                        if (isPlaying) { MusicController.pause() }
                                        else { MusicController.play() }
                                    }
                            }"""
min_click_new = """                            .clickable {
                                if (isPlaying) { MusicController.pause() }
                                else { MusicController.play() }
                            }"""
content = content.replace(min_click_old, min_click_new)

exp_click_old = """                                .clickable {
                                    if (isPrepared) {
                                        if (isPlaying) {
                                            MusicController.pause()
                                        } else {
                                            MusicController.play()
                                        }
                                    }
                                }"""
exp_click_new = """                                .clickable {
                                    if (isPlaying) {
                                        MusicController.pause()
                                    } else {
                                        MusicController.play()
                                    }
                                }"""
content = content.replace(exp_click_old, exp_click_new)


with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)
