perl -0777 -pi -e 's/    val context = LocalContext\.current\n    DisposableEffect\(context\) \{/    DisposableEffect(context) {/g' app/src/main/java/com/auradownloader/app/MainActivity.kt

perl -0777 -pi -e 's/LocalBroadcastManager\.getInstance\(context\)\.registerReceiver\(receiver, IntentFilter\("com\.auradownloader\.DOWNLOAD_COMPLETED"\)\)/androidx.core.content.ContextCompat.registerReceiver(context, receiver, IntentFilter("com.auradownloader.DOWNLOAD_COMPLETED"), androidx.core.content.ContextCompat.RECEIVER_NOT_EXPORTED)/g' app/src/main/java/com/auradownloader/app/MainActivity.kt

perl -0777 -pi -e 's/LocalBroadcastManager\.getInstance\(context\)\.unregisterReceiver\(receiver\)/context.unregisterReceiver(receiver)/g' app/src/main/java/com/auradownloader/app/MainActivity.kt
