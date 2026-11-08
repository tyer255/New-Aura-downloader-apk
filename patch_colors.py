import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

# Main button gradient
content = content.replace("Brush.horizontalGradient(listOf(Color(0xFFE842A1), Color(0xFF4C42E8)))", "Brush.horizontalGradient(listOf(Color(0xFF2563EB), Color(0xFF1D4ED8)))")

# FeatureCard colors
content = content.replace("Color(0xFFF472B6)", "Color(0xFF3B82F6)") # Pink -> Blue
content = content.replace("Color(0xFFA78BFA)", "Color(0xFF10B981)") # Purple -> Emerald
content = content.replace("Color(0xFF34D399)", "Color(0xFFF59E0B)") # Light Emerald -> Amber

# Top bar icon (was gradient of pink to pink?) wait, line 1446: Brush.linearGradient(listOf(Color(0xFFFCA5A5), Color(0xFFF472B6)))
content = content.replace("Brush.linearGradient(listOf(Color(0xFFFCA5A5), Color(0xFFF472B6)))", "SolidColor(Color(0xFF2563EB))")

# Quick actions (Pasted link, etc)
# Line 1536 border: Color(0xFF38BDF8).copy(alpha = 0.5f) -> 38BDF8 is Sky Blue, which is fine and natural.
# Line 1666: we fixed this above.

# Download progress gradient
content = content.replace("colors = listOf(Color(0xFFE842A1), Color(0xFF38BDF8))", "colors = listOf(Color(0xFF3B82F6), Color(0xFF2563EB))")

# Also the logo gradient in `Title()` or somewhere?
content = content.replace("listOf(Color(0xFFE842A1), Color(0xFF38BDF8))", "listOf(Color(0xFF3B82F6), Color(0xFF2563EB))")

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(content)

