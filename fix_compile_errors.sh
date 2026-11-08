sed -i '/import androidx.localbroadcastmanager.content.LocalBroadcastManager/d' app/src/main/java/com/auradownloader/app/MainActivity.kt
sed -i '/import androidx.compose.ui.window.DialogProperties/a\
import androidx.compose.ui.zIndex.zIndex' app/src/main/java/com/auradownloader/app/MainActivity.kt
sed -i 's/    val context = LocalContext\.current//g' app/src/main/java/com/auradownloader/app/MainActivity.kt
awk '
/    var unreadCount by remember { mutableIntStateOf\(0\) }/ {
    print $0
    print "    val context = LocalContext.current"
    next
}
{ print $0 }
' app/src/main/java/com/auradownloader/app/MainActivity.kt > tmp.kt && mv tmp.kt app/src/main/java/com/auradownloader/app/MainActivity.kt
