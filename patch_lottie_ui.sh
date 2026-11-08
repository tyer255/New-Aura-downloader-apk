awk '
/    if \(showHistory\) {/ {
    print "    if (showSuccessAnimation) {"
    print "        Box(modifier = Modifier.fillMaxSize().zIndex(100f).background(Color.Black.copy(alpha = 0.5f)), contentAlignment = Alignment.Center) {"
    print "            val composition by rememberLottieComposition(LottieCompositionSpec.RawRes(com.auradownloader.app.R.raw.success_anim))"
    print "            LottieAnimation("
    print "                composition = composition,"
    print "                iterations = 1,"
    print "                modifier = Modifier.size(200.dp)"
    print "            )"
    print "        }"
    print "        LaunchedEffect(Unit) {"
    print "            kotlinx.coroutines.delay(2000)"
    print "            showSuccessAnimation = false"
    print "        }"
    print "    }\n"
    print $0
    next
}
{ print $0 }
' app/src/main/java/com/auradownloader/app/MainActivity.kt > tmp.kt && mv tmp.kt app/src/main/java/com/auradownloader/app/MainActivity.kt
