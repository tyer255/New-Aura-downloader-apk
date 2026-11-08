package com.auradownloader.app

import android.graphics.BlurMaskFilter
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Paint
import androidx.compose.ui.graphics.drawscope.drawIntoCanvas
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

fun Modifier.neumorphic(
    isLightMode: Boolean,
    cornerRadius: Dp = 16.dp,
    elevation: Dp = 6.dp,
    lightShadowColorLight: Color = Color.White,
    darkShadowColorLight: Color = Color.Black.copy(alpha = 0.15f),
    lightShadowColorDark: Color = Color.White.copy(alpha = 0.05f),
    darkShadowColorDark: Color = Color.Black.copy(alpha = 0.5f)
): Modifier = this.drawBehind {
    val lightShadow = if (isLightMode) lightShadowColorLight else lightShadowColorDark
    val darkShadow = if (isLightMode) darkShadowColorLight else darkShadowColorDark
    
    val blurRadius = elevation.toPx()
    val offset = elevation.toPx() / 2f
    val radius = cornerRadius.toPx()
    
    drawIntoCanvas { canvas ->
        val paint = Paint()
        val frameworkPaint = paint.asFrameworkPaint()
        frameworkPaint.maskFilter = BlurMaskFilter(blurRadius, BlurMaskFilter.Blur.NORMAL)
        
        // Draw dark shadow (bottom right)
        frameworkPaint.color = darkShadow.toArgb()
        canvas.drawRoundRect(
            left = offset,
            top = offset,
            right = size.width + offset,
            bottom = size.height + offset,
            radiusX = radius,
            radiusY = radius,
            paint = paint
        )
        
        // Draw light shadow (top left)
        frameworkPaint.color = lightShadow.toArgb()
        canvas.drawRoundRect(
            left = -offset,
            top = -offset,
            right = size.width - offset,
            bottom = size.height - offset,
            radiusX = radius,
            radiusY = radius,
            paint = paint
        )
    }
}
