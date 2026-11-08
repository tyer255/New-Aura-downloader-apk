fun SkeletonLoader(
    isDarkMode: Boolean,
    progress: Float,
    statusText: String = "",
    previewThumbnailUrl: String? = null,
    previewTitle: String? = null
) {
    val isLight = !isDarkMode
    
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

    val animatedProgress by animateFloatAsState(
        targetValue = progress.coerceIn(0f, 1f),
        animationSpec = tween(durationMillis = 500, easing = FastOutSlowInEasing),
        label = "progress_line"
    )

    val percentInt = (animatedProgress * 100).toInt().coerceIn(0, 100)

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Skeleton Image/Video Box
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .aspectRatio(16f / 9f)
                .clip(RoundedCornerShape(24.dp))
                .background(if (isLight) Color(0xFFF5F5F5) else Color.White.copy(alpha = 0.05f))
                .border(1.dp, if (isLight) Color(0xFFE5E5E5) else Color.White.copy(alpha = 0.1f), RoundedCornerShape(24.dp))
        ) {
            if (!previewThumbnailUrl.isNullOrEmpty()) {
                val context = LocalContext.current
                AsyncImage(
                    model = coil.request.ImageRequest.Builder(context)
                        .data(previewThumbnailUrl)
                        .build(),
                    contentDescription = "Preview Thumbnail",
                    contentScale = ContentScale.Crop,
                    modifier = Modifier.fillMaxSize()
                )
                // Gradient scrim overlay
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(
                            Brush.verticalGradient(
                                colors = listOf(Color.Transparent, Color.Black.copy(alpha = 0.85f))
                            )
                        )
                )
                if (!previewTitle.isNullOrEmpty()) {
                    Column(
                        modifier = Modifier
                            .align(Alignment.BottomStart)
                            .padding(16.dp)
                    ) {
                        Text(
                            text = previewTitle,
                            color = Color.White,
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold,
                            maxLines = 2,
                            overflow = TextOverflow.Ellipsis
                        )
                    }
                }
            } else {
                // Moving Shimmer Effect
                Canvas(modifier = Modifier.fillMaxSize()) {
                    val width = size.width
                    val xOffset = shimmerX * width
                    drawRect(
                        brush = Brush.horizontalGradient(
                            colors = listOf(
                                Color.Transparent,
                                if (isLight) Color(0xFFE5E5E5).copy(alpha = 0.5f) else Color.White.copy(alpha = 0.1f),
                                Color.Transparent
                            ),
                            startX = xOffset,
                            endX = xOffset + width
                        )
                    )
                }
            }

            // Centered Spinner
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator(
                    color = if (isLight) Color(0xFFA3A3A3) else Color.White.copy(alpha = 0.2f),
                    modifier = Modifier.size(32.dp),
                    strokeWidth = 3.dp
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Progress Bar Area
        Column(
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "Progress",
                    color = if (isLight) Color(0xFF404040) else Color.White.copy(alpha = 0.7f),
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Medium
                )
                Text(
                    text = "${percentInt}%",
                    color = if (isLight) Color(0xFF404040) else Color.White.copy(alpha = 0.7f),
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Medium
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Outer Track
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(12.dp)
                    .clip(RoundedCornerShape(50))
                    .background(if (isLight) Color(0xFFE5E5E5) else Color.White.copy(alpha = 0.05f))
                    .border(1.dp, if (isLight) Color(0xFFD4D4D4) else Color.White.copy(alpha = 0.1f), RoundedCornerShape(50))
            ) {
                // Inner Fill
                Box(
                    modifier = Modifier
                        .fillMaxHeight()
                        .fillMaxWidth(fraction = animatedProgress.coerceIn(0f, 1f))
                        .clip(RoundedCornerShape(50))
                        .background(if (isLight) Color(0xFF262626) else Color.White)
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Status Message
            Text(
                text = statusText.ifEmpty { "Processing Link..." },
                color = if (isLight) Color(0xFF525252) else Color.White.copy(alpha = 0.8f),
                style = MaterialTheme.typography.labelSmall,
                fontWeight = FontWeight.Medium,
                modifier = Modifier.fillMaxWidth(),
                textAlign = androidx.compose.ui.text.style.TextAlign.Center
            )
        }
    }
}
