import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    content = f.read()

pattern = re.compile(
    r'modifier = Modifier\.fillMaxWidth\(\)\.height\(60\.dp\)\.background\(Brush\.horizontalGradient\(listOf\(Color\(0xFF2563EB\), Color\(0xFF1D4ED8\)\)\), RoundedCornerShape\(30\.dp\)\)\.drawWithContent \{\s*'
    r'drawContent\(\)\s*'
    r'if \(url\.isNotEmpty\(\) && !isDownloading && result == null\) \{\s*'
    r'val canvasWidth = size\.width\s*'
    r'val xOffset = flowX \* canvasWidth\s*'
    r'drawRect\(\s*'
    r'brush = Brush\.horizontalGradient\(\s*'
    r'colors = listOf\(Color\.Transparent, Color\.White\.copy\(alpha = 0\.3f\), Color\.Transparent\),\s*'
    r'startX = xOffset,\s*'
    r'endX = xOffset \+ canvasWidth \* 0\.5f\s*'
    r'\)\s*'
    r'\)\s*'
    r'\}\s*'
    r'\},\s*'
    r'shape = RoundedCornerShape\(30\.dp\),\s*'
    r'colors = ButtonDefaults\.buttonColors\(containerColor = Color\.Transparent\),\s*'
    r'contentPadding = PaddingValues\(0\.dp\),\s*'
    r'enabled = !isDownloading\s*'
    r'\) \{\s*'
    r'Row\(modifier = Modifier\.fillMaxSize\(\)\.padding\(horizontal = 24\.dp\), horizontalArrangement = Arrangement\.SpaceBetween, verticalAlignment = Alignment\.CenterVertically\) \{\s*'
    r'Row\(verticalAlignment = Alignment\.CenterVertically, modifier = Modifier\.weight\(1f\), horizontalArrangement = Arrangement\.Center\) \{\s*'
    r'Icon\(Icons\.Filled\.Download, null, tint = Color\.White\)\s*'
    r'Spacer\(modifier = Modifier\.width\(12\.dp\)\)\s*'
    r'Text\("Download Now", fontWeight = FontWeight\.Bold, style = MaterialTheme\.typography\.titleMedium, color = Color\.White\)\s*'
    r'\}\s*'
    r'Box\(modifier = Modifier\.size\(40\.dp\)\.clip\(CircleShape\)\.background\(Color\.White\.copy\(0\.2f\)\), contentAlignment = Alignment\.Center\) \{\s*'
    r'Icon\(Icons\.Filled\.ChevronRight, null, tint = Color\.White\)\s*'
    r'\}\s*'
    r'\}\s*'
    r'\}', re.MULTILINE
)

replacement = """modifier = Modifier.fillMaxWidth().height(56.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (isDarkMode) Color.White else Color(0xFF0F172A),
                    contentColor = if (isDarkMode) Color(0xFF0F172A) else Color.White
                ),
                elevation = ButtonDefaults.buttonElevation(defaultElevation = 2.dp),
                enabled = !isDownloading
            ) {
                Row(
                    modifier = Modifier.fillMaxSize(),
                    horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Filled.Download, contentDescription = null)
                    Spacer(modifier = Modifier.width(10.dp))
                    Text(
                        "Download Now",
                        fontWeight = FontWeight.SemiBold,
                        style = MaterialTheme.typography.titleMedium
                    )
                }
            }"""

new_content = pattern.sub(replacement, content)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(new_content)

print(f"Replaced {len(pattern.findall(content))} occurrences.")
