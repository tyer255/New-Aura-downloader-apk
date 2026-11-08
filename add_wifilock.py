import re

with open("app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt", "r") as f:
    content = f.read()

if "android.net.wifi.WifiManager" not in content:
    content = content.replace("import android.os.PowerManager", "import android.os.PowerManager\nimport android.net.wifi.WifiManager")

if "private var wifiLock: WifiManager.WifiLock? = null" not in content:
    content = content.replace("private var mediaPlayer: MediaPlayer? = null", "private var mediaPlayer: MediaPlayer? = null\n    private var wifiLock: WifiManager.WifiLock? = null")

if "val wifiManager" not in content:
    create_old = """    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()"""
    create_new = """    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        val wifiManager = applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
        wifiLock = wifiManager.createWifiLock(WifiManager.WIFI_MODE_FULL_HIGH_PERF, "MusicPlaybackServiceWifiLock")
"""
    content = content.replace(create_old, create_new)

if "wifiLock?.release()" not in content:
    destroy_old = """    override fun onDestroy() {
        super.onDestroy()
        serviceJob.cancel()
        mediaSession.isActive = false
        mediaSession.release()
        mediaPlayer?.release()
        mediaPlayer = null
    }"""
    destroy_new = """    override fun onDestroy() {
        super.onDestroy()
        serviceJob.cancel()
        mediaSession.isActive = false
        mediaSession.release()
        mediaPlayer?.release()
        mediaPlayer = null
        if (wifiLock?.isHeld == true) {
            wifiLock?.release()
        }
    }"""
    content = content.replace(destroy_old, destroy_new)

if "wifiLock?.acquire()" not in content:
    play_old = """    private fun playUrl(url: String) {
        mediaPlayer?.release()"""
    play_new = """    private fun playUrl(url: String) {
        if (wifiLock?.isHeld == false) {
            wifiLock?.acquire()
        }
        mediaPlayer?.release()"""
    content = content.replace(play_old, play_new)

with open("app/src/main/java/com/auradownloader/app/MusicPlaybackService.kt", "w") as f:
    f.write(content)
