awk '
/modifier = Modifier\.fillMaxWidth\(\)\.height\(56\.dp\)\.clip\(RoundedCornerShape\(16\.dp\)\)\.background\(Color\.Black\.copy\(alpha = 0\.6f\)\)\.border\(1\.dp, Color\.White\.copy\(alpha = 0\.2f\), RoundedCornerShape\(16\.dp\)\)/ {
    print "                modifier = Modifier.fillMaxWidth().height(56.dp).neumorphic(isLightMode = !isDarkMode, cornerRadius = 16.dp).clip(RoundedCornerShape(16.dp)).background(if(isDarkMode) Color.Black.copy(alpha = 0.6f) else Color.White).border(1.dp, if(isDarkMode) Color.White.copy(alpha = 0.2f) else Color.Transparent, RoundedCornerShape(16.dp)),"
    next
}
/colors = ButtonDefaults\.buttonColors\(/ {
    if (in_download == 1) {
        print "                colors = ButtonDefaults.buttonColors("
        print "                    containerColor = Color.Transparent,"
        print "                    contentColor = if (isDarkMode) Color.White else Color.Black"
        print "                ),"
        in_download = 0
        skip_to = "),"
        next
    }
    print $0
    next
}
/if \(isDownloading\) \{/ {
    if (in_button_row == 1) {
        print "                    if (isDownloading) {"
        print "                        CircularProgressIndicator(modifier = Modifier.size(20.dp), color = if (isDarkMode) Color.White else Color.Black, strokeWidth = 2.dp)"
        print "                        Spacer(modifier = Modifier.width(10.dp))"
        print "                        Text("
        print "                            \"Extracting...\","
        print "                            fontWeight = FontWeight.Bold,"
        print "                            color = if (isDarkMode) Color.White else Color.Black,"
        print "                            style = MaterialTheme.typography.titleMedium"
        print "                        )"
        print "                    } else {"
        print "                        Icon(Icons.Filled.Download, contentDescription = null, tint = if (isDarkMode) Color.White else Color.Black)"
        print "                        Spacer(modifier = Modifier.width(10.dp))"
        print "                        Text("
        print "                            \"Download Now\","
        print "                            fontWeight = FontWeight.Bold,"
        print "                            color = if (isDarkMode) Color.White else Color.Black,"
        print "                            style = MaterialTheme.typography.titleMedium"
        print "                        )"
        print "                    }"
        skip_to = "}"
        in_button_row = 0
        next
    }
}
/Button\(/ {
    if (last_line ~ /Spacer\(modifier = Modifier.height\(24.dp\)\)/) {
        in_download = 1
    }
    print $0
    next
}
/Row\(/ {
    if (last_line ~ /enabled = !isDownloading/) {
        in_button_row = 1
    }
    print $0
    next
}
{
    if (skip_to != "") {
        if ($0 ~ skip_to) {
            skip_to = ""
        }
        next
    }
    print $0
    last_line = $0
}
' app/src/main/java/com/auradownloader/app/MainActivity.kt > tmp.kt && mv tmp.kt app/src/main/java/com/auradownloader/app/MainActivity.kt
