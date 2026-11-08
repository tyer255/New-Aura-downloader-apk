sed -i '/import org.json.JSONObject/a\
import androidx.localbroadcastmanager.content.LocalBroadcastManager\
import android.content.BroadcastReceiver\
import android.content.IntentFilter\
import com.airbnb.lottie.compose.*' app/src/main/java/com/auradownloader/app/MainActivity.kt
