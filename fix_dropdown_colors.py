import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

# We need to make sure the dropdown menu text colors and background are visible in light mode.
# Right now, we used `modifier = Modifier.background(if(isDarkMode) glassBg else Color.White)` for DropdownMenu, which is good.
