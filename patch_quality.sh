awk '
/modifier = Modifier\.fillMaxWidth\(\)\.height\(48\.dp\),/ {
    print "                                        modifier = Modifier.fillMaxWidth().height(48.dp).neumorphic(isLightMode = !isDarkMode, cornerRadius = 12.dp, elevation = 4.dp),"
    next
}
/colors = ButtonDefaults\.buttonColors\(/ {
    if (last_line ~ /shape = RoundedCornerShape\(12.dp\),/) {
        print "                                        colors = ButtonDefaults.buttonColors("
        print "                                            containerColor = if (isZip) Color(0xFF1DB954) else if (isDarkMode) Color.White.copy(0.1f) else Color.White,"
        print "                                            contentColor = if (isZip) Color.White else textColor"
        print "                                        ),"
        skip_to = "),"
        next
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
