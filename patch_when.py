import re

with open('app/src/main/java/com/example/MainActivity.kt', 'r') as f:
    content = f.read()

old_brush_when = """    val backgroundBrush = when (platform) {
        Platform.YOUTUBE -> Brush.linearGradient(listOf(Color(0xFFFF4D4D), Color(0xFFFF0000), Color(0xFFB30000)))
        Platform.INSTAGRAM -> Brush.linearGradient(listOf(Color(0xFFF9CE34), Color(0xFFEE2A7B), Color(0xFFD82B7D), Color(0xFF6228D7)))
        Platform.TIKTOK -> Brush.linearGradient(listOf(Color(0xFF25282A), Color(0xFF121315), Color(0xFF000000)))
        Platform.FACEBOOK -> Brush.linearGradient(listOf(Color(0xFF18ACFE), Color(0xFF0062E0)))
        Platform.REDDIT -> Brush.linearGradient(listOf(Color(0xFFFF5700), Color(0xFFE63900)))
        Platform.PINTEREST -> Brush.linearGradient(listOf(Color(0xFFE60023), Color(0xFFAD081B)))
        Platform.X -> Brush.linearGradient(listOf(Color(0xFF2C2C2C), Color(0xFF0F0F0F)))
        Platform.LINKEDIN -> Brush.linearGradient(listOf(Color(0xFF00A0DC), Color(0xFF0077B5)))
    }"""

new_brush_when = """    val backgroundBrush = when (platform) {
        Platform.YOUTUBE -> Brush.linearGradient(listOf(Color(0xFFFF4D4D), Color(0xFFFF0000), Color(0xFFB30000)))
        Platform.INSTAGRAM -> Brush.linearGradient(listOf(Color(0xFFF9CE34), Color(0xFFEE2A7B), Color(0xFFD82B7D), Color(0xFF6228D7)))
        Platform.TIKTOK -> Brush.linearGradient(listOf(Color(0xFF25282A), Color(0xFF121315), Color(0xFF000000)))
        Platform.FACEBOOK -> Brush.linearGradient(listOf(Color(0xFF18ACFE), Color(0xFF0062E0)))
        Platform.REDDIT -> Brush.linearGradient(listOf(Color(0xFFFF5700), Color(0xFFE63900)))
        Platform.PINTEREST -> Brush.linearGradient(listOf(Color(0xFFE60023), Color(0xFFAD081B)))
        Platform.X -> Brush.linearGradient(listOf(Color(0xFF2C2C2C), Color(0xFF0F0F0F)))
        Platform.LINKEDIN -> Brush.linearGradient(listOf(Color(0xFF00A0DC), Color(0xFF0077B5)))
        Platform.SNAPCHAT -> Brush.linearGradient(listOf(Color(0xFFFFFC00), Color(0xFFE6E200)))
        Platform.SPOTIFY -> Brush.linearGradient(listOf(Color(0xFF1DB954), Color(0xFF19A34A)))
        Platform.THREADS -> Brush.linearGradient(listOf(Color(0xFF000000), Color(0xFF222222)))
    }"""

old_icon_when = """        when (platform) {
            Platform.INSTAGRAM -> {
                Box(modifier = Modifier.size(24.dp), contentAlignment = Alignment.Center) {
                    Box(modifier = Modifier.fillMaxSize().border(2.dp, Color.White, RoundedCornerShape(7.dp)))
                    Box(modifier = Modifier.size(10.dp).border(2.dp, Color.White, CircleShape))
                    Box(modifier = Modifier.size(3.dp).align(Alignment.TopEnd).offset(x = (-3.5).dp, y = 3.5.dp).background(Color.White, CircleShape))
                }
            }
            Platform.TIKTOK -> {
                Box(modifier = Modifier.size(24.dp), contentAlignment = Alignment.Center) {
                    Icon(painterResource(id = R.drawable.ic_tiktok), contentDescription = "TikTok", tint = Color(0xFF25F4EE).copy(alpha = 0.9f), modifier = Modifier.size(20.dp).offset(x = (-1).dp, y = (-1).dp))
                    Icon(painterResource(id = R.drawable.ic_tiktok), contentDescription = "TikTok", tint = Color(0xFFFE2C55).copy(alpha = 0.9f), modifier = Modifier.size(20.dp).offset(x = 1.dp, y = 1.dp))
                    Icon(painterResource(id = R.drawable.ic_tiktok), contentDescription = "TikTok", tint = Color.White, modifier = Modifier.size(20.dp))
                }
            }
            Platform.YOUTUBE -> Icon(painterResource(id = R.drawable.ic_youtube), contentDescription = "YouTube", tint = Color.White, modifier = Modifier.size(22.dp))
            Platform.FACEBOOK -> Icon(painterResource(id = R.drawable.ic_facebook), contentDescription = "Facebook", tint = Color.White, modifier = Modifier.size(22.dp))
            Platform.REDDIT -> Icon(painterResource(id = R.drawable.ic_reddit), contentDescription = "Reddit", tint = Color.Unspecified, modifier = Modifier.size(25.dp))
            Platform.PINTEREST -> Icon(painterResource(id = R.drawable.ic_pinterest), contentDescription = "Pinterest", tint = Color.White, modifier = Modifier.size(22.dp))
            Platform.X -> Icon(painterResource(id = R.drawable.ic_x), contentDescription = "X", tint = Color.White, modifier = Modifier.size(20.dp))
            Platform.LINKEDIN -> Icon(painterResource(id = R.drawable.ic_linkedin), contentDescription = "LinkedIn", tint = Color.White, modifier = Modifier.size(22.dp))
        }"""

new_icon_when = """        when (platform) {
            Platform.INSTAGRAM -> {
                Box(modifier = Modifier.size(24.dp), contentAlignment = Alignment.Center) {
                    Box(modifier = Modifier.fillMaxSize().border(2.dp, Color.White, RoundedCornerShape(7.dp)))
                    Box(modifier = Modifier.size(10.dp).border(2.dp, Color.White, CircleShape))
                    Box(modifier = Modifier.size(3.dp).align(Alignment.TopEnd).offset(x = (-3.5).dp, y = 3.5.dp).background(Color.White, CircleShape))
                }
            }
            Platform.TIKTOK -> {
                Box(modifier = Modifier.size(24.dp), contentAlignment = Alignment.Center) {
                    Icon(painterResource(id = R.drawable.ic_tiktok), contentDescription = "TikTok", tint = Color(0xFF25F4EE).copy(alpha = 0.9f), modifier = Modifier.size(20.dp).offset(x = (-1).dp, y = (-1).dp))
                    Icon(painterResource(id = R.drawable.ic_tiktok), contentDescription = "TikTok", tint = Color(0xFFFE2C55).copy(alpha = 0.9f), modifier = Modifier.size(20.dp).offset(x = 1.dp, y = 1.dp))
                    Icon(painterResource(id = R.drawable.ic_tiktok), contentDescription = "TikTok", tint = Color.White, modifier = Modifier.size(20.dp))
                }
            }
            Platform.YOUTUBE -> Icon(painterResource(id = R.drawable.ic_youtube), contentDescription = "YouTube", tint = Color.White, modifier = Modifier.size(22.dp))
            Platform.FACEBOOK -> Icon(painterResource(id = R.drawable.ic_facebook), contentDescription = "Facebook", tint = Color.White, modifier = Modifier.size(22.dp))
            Platform.REDDIT -> Icon(painterResource(id = R.drawable.ic_reddit), contentDescription = "Reddit", tint = Color.Unspecified, modifier = Modifier.size(25.dp))
            Platform.PINTEREST -> Icon(painterResource(id = R.drawable.ic_pinterest), contentDescription = "Pinterest", tint = Color.White, modifier = Modifier.size(22.dp))
            Platform.X -> Icon(painterResource(id = R.drawable.ic_x), contentDescription = "X", tint = Color.White, modifier = Modifier.size(20.dp))
            Platform.LINKEDIN -> Icon(painterResource(id = R.drawable.ic_linkedin), contentDescription = "LinkedIn", tint = Color.White, modifier = Modifier.size(22.dp))
            Platform.SNAPCHAT -> Icon(painterResource(id = R.drawable.ic_snapchat), contentDescription = "Snapchat", tint = Color.Black, modifier = Modifier.size(22.dp))
            Platform.SPOTIFY -> Icon(painterResource(id = R.drawable.ic_spotify), contentDescription = "Spotify", tint = Color.White, modifier = Modifier.size(22.dp))
            Platform.THREADS -> Icon(painterResource(id = R.drawable.ic_threads), contentDescription = "Threads", tint = Color.White, modifier = Modifier.size(22.dp))
        }"""

if old_brush_when in content and old_icon_when in content:
    content = content.replace(old_brush_when, new_brush_when)
    content = content.replace(old_icon_when, new_icon_when)
    with open('app/src/main/java/com/example/MainActivity.kt', 'w') as f:
        f.write(content)
    print("When blocks patched successfully.")
else:
    print("When blocks not found.")

