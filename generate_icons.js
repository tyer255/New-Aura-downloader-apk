const simpleIcons = require('simple-icons');
const icons = ['YouTube', 'Instagram', 'TikTok', 'Facebook', 'Reddit', 'Pinterest', 'X', 'LinkedIn'];

let kotlinCode = `package com.example.ui.theme

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathFillType
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.graphics.vector.path
import androidx.compose.ui.unit.dp

object BrandIcons {
`;

for (const name of icons) {
  const icon = simpleIcons['si' + name];
  if (!icon) {
      console.log('Icon not found for ' + name);
      continue;
  }
  
  kotlinCode += `
    val ${name}: ImageVector
        get() {
            if (_${name} != null) {
                return _${name}!!
            }
            _${name} = ImageVector.Builder(
                name = "${name}",
                defaultWidth = 24.dp,
                defaultHeight = 24.dp,
                viewportWidth = 24f,
                viewportHeight = 24f
            ).apply {
                path(
                    fill = SolidColor(Color(0xFFFFFFFF)),
                    fillAlpha = 1.0f,
                    stroke = null,
                    strokeAlpha = 1.0f,
                    strokeLineWidth = 1.0f,
                    strokeLineCap = StrokeCap.Butt,
                    strokeLineJoin = StrokeJoin.Miter,
                    strokeLineMiter = 1.0f,
                    pathFillType = PathFillType.NonZero
                ) {
                    // SVG Path: ${icon.path}
`;

   // We need to parse SVG path into compose path builder calls, which is hard.
   // Instead we can use vector drawables, or simpler: ImageVector.Builder().addPathNodes(icon.path) which doesn't exist directly... 
   // Wait! androidx.compose.ui.graphics.vector.VectorPath exist? Yes, we can just use the `addPathNodes` internal, or actually we can use `PathParser.createPathFromPathData` in Android?
   // Wait, ImageVector.Builder has a `path` method where you can pass the path data? No, there is `ImageVector.Builder.addPath` in some versions, or `VectorNode`.
   // A better way is to generate Android XML Vector Drawables for each icon! That's fully supported and natively parsed.
}
