import re

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    content = f.read()

# Revert LaunchedEffect(isDownloading)
pattern_effect = re.compile(r'    LaunchedEffect\(isDownloading\) \{.*?        \}\n    \}(?:\n    LaunchedEffect\(isDownloading\) \{.*?\})?', re.DOTALL)
replacement_effect = '''    LaunchedEffect(isDownloading) {
        if (isDownloading) {
            loadingStep = 0
            while (isDownloading) {
                kotlinx.coroutines.delay((800..2000).random().toLong())
                if (loadingStep < LOADING_STEPS.size - 1) {
                    loadingStep++
                }
            }
        }
    }'''

new_content = pattern_effect.sub(replacement_effect, content, 1)

# Remove extra LaunchedEffect(isDownloading) if exists
new_content = re.sub(r'\n    LaunchedEffect\(isDownloading\) \{\n        if \(isDownloading\) \{\n            extractionProgress = 0f\n            val steps = 50\n            val delayMs = 5000L / steps\n            for \(i in 1\.\.steps\) \{\n                delay\(delayMs\)\n                extractionProgress = \(i\.toFloat\(\) / steps\) \* 0\.9f\n            \}\n        \} else \{\n            extractionProgress = 1f\n        \}\n    \}', '', new_content)

# Revert SkeletonLoader call
new_content = new_content.replace('SkeletonLoader(isDarkMode = isDarkMode, progress = extractionProgress)', 'SkeletonLoader(isDarkMode = isDarkMode, progress = ((loadingStep + 1) / LOADING_STEPS.size.toFloat()).coerceIn(0f, 1f))')

# Revert SkeletonLoader function
pattern_skeleton = re.compile(r'fun SkeletonLoader\(isDarkMode: Boolean, progress: Float\) \{.*', re.DOTALL)
replacement_skeleton = '''fun SkeletonLoader(isDarkMode: Boolean, progress: Float) {
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

new_content = pattern_skeleton.sub(replacement_skeleton, new_content, 1)

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(new_content)
