import re

with open('app/src/main/java/com/example/MainActivity.kt', 'r') as f:
    content = f.read()

target = '''fun SkeletonLoader(isDarkMode: Boolean, progress: Float) {
    val baseColor = if (isDarkMode) Color.White else Color.Black
    val textColor = if (isDarkMode) Color.White else Color.Black

    val infiniteTransition = rememberInfiniteTransition(label = "shimmer")
    val shimmerX by infiniteTransition.animateFloat(
        initialValue = -1f,
        targetValue = 2f,
        animationSpec = infiniteRepeatable(
            animation = tween(1500, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "shimmer_x"
    )
    val animatedProgress by animateFloatAsState(targetValue = progress, animationSpec = tween(500, easing = LinearOutSlowInEasing), label = "progress")

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(top = 16.dp, bottom = 16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Skeleton Box
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .aspectRatio(16f / 9f)
                .clip(RoundedCornerShape(24.dp))
                .background(baseColor.copy(alpha = 0.05f))
                .border(1.dp, baseColor.copy(alpha = 0.1f), RoundedCornerShape(24.dp))
        ) {
            // Shimmer
            Canvas(modifier = Modifier.fillMaxSize()) {
                val width = size.width
                val xOffset = shimmerX * width
                drawRect(
                    brush = Brush.horizontalGradient(
                        colors = listOf(Color.Transparent, baseColor.copy(alpha = 0.1f), Color.Transparent),
                        startX = xOffset,
                        endX = xOffset + width
                    )
                )
            }

            // Spinner
            CircularProgressIndicator(
                color = baseColor.copy(alpha = 0.2f),
                modifier = Modifier.align(Alignment.Center).size(32.dp),
                strokeWidth = 3.dp
            )
        }
    }
}'''

replacement = '''fun SkeletonLoader(isDarkMode: Boolean, progress: Float) {
    val baseColor = if (isDarkMode) Color.White else Color.Black
    val textColor = if (isDarkMode) Color.White else Color.Black

    val infiniteTransition = rememberInfiniteTransition(label = "shimmer")
    val shimmerX by infiniteTransition.animateFloat(
        initialValue = -1f,
        targetValue = 2f,
        animationSpec = infiniteRepeatable(
            animation = tween(1500, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "shimmer_x"
    )

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 16.dp)
            .clip(RoundedCornerShape(16.dp))
            .background(baseColor.copy(alpha = 0.05f))
            .border(1.dp, baseColor.copy(alpha = 0.1f), RoundedCornerShape(16.dp))
            .padding(16.dp)
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            CircularProgressIndicator(
                color = Color(0xFF38BDF8),
                modifier = Modifier.size(20.dp),
                strokeWidth = 2.dp
            )
            Spacer(modifier = Modifier.width(12.dp))
            Text(
                text = "Extracting media...",
                color = textColor,
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold
            )
        }
        Spacer(modifier = Modifier.height(16.dp))
        
        // Progress bar container
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(8.dp)
                .clip(RoundedCornerShape(4.dp))
                .background(baseColor.copy(alpha = 0.1f))
        ) {
            // Animated progress fill
            Box(
                modifier = Modifier
                    .fillMaxWidth(progress.coerceIn(0f, 1f))
                    .fillMaxHeight()
                    .clip(RoundedCornerShape(4.dp))
                    .background(
                        Brush.horizontalGradient(
                            listOf(Color(0xFFE842A1), Color(0xFF4C42E8))
                        )
                    )
            )
            // Shimmer over progress
            Canvas(modifier = Modifier.fillMaxSize()) {
                val width = size.width
                val xOffset = shimmerX * width
                drawRect(
                    brush = Brush.horizontalGradient(
                        colors = listOf(Color.Transparent, Color.White.copy(alpha = 0.5f), Color.Transparent),
                        startX = xOffset,
                        endX = xOffset + width * 0.5f
                    )
                )
            }
        }
        Spacer(modifier = Modifier.height(8.dp))
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text("Connecting to servers", color = textColor.copy(alpha = 0.6f), style = MaterialTheme.typography.labelSmall)
            Text("${(progress * 100).toInt()}%", color = textColor, style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Bold)
        }
    }
}'''

new_content = content.replace(target, replacement)
if new_content == content:
    print("Warning: SkeletonLoader replacement failed.")
else:
    with open('app/src/main/java/com/example/MainActivity.kt', 'w') as f:
        f.write(new_content)
    print("SkeletonLoader Patched.")
