awk '
/            \/\/ Close Button/ {
    print "            // Sync Controls"
    print "            Row("
    print "                modifier = Modifier"
    print "                    .align(Alignment.TopStart)"
    print "                    .padding(top = 48.dp, start = 16.dp)"
    print "                    .zIndex(10f)"
    print "                    .background(Color(0x33FFFFFF), RoundedCornerShape(20.dp))"
    print "                    .padding(horizontal = 8.dp, vertical = 4.dp),"
    print "                verticalAlignment = Alignment.CenterVertically"
    print "            ) {"
    print "                IconButton(onClick = { userLyricsOffsetMs -= 500L }, modifier = Modifier.size(32.dp)) {"
    print "                    Text(\"-\", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 20.sp)"
    print "                }"
    print "                Text("
    print "                    text = \"${if (userLyricsOffsetMs >= 0) \"+\" else \"\"}${userLyricsOffsetMs / 1000f}s\","
    print "                    color = Color.White,"
    print "                    fontSize = 14.sp,"
    print "                    fontWeight = FontWeight.Medium,"
    print "                    modifier = Modifier.padding(horizontal = 8.dp)"
    print "                )"
    print "                IconButton(onClick = { userLyricsOffsetMs += 500L }, modifier = Modifier.size(32.dp)) {"
    print "                    Text(\"+\", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 20.sp)"
    print "                }"
    print "            }\n"
}
{ print $0 }
' app/src/main/java/com/auradownloader/app/SyncedLyricsView.kt > tmp_lyrics.kt && mv tmp_lyrics.kt app/src/main/java/com/auradownloader/app/SyncedLyricsView.kt
