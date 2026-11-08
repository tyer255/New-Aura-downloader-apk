object PreferencesHelper {
    private const val PREFS_NAME = "aura_prefs"
    private const val KEY_HISTORY = "history"
    private const val KEY_NOTIFICATIONS = "notifications"

    fun getHistory(context: android.content.Context): List<org.json.JSONObject> {
        val prefs = context.getSharedPreferences(PREFS_NAME, android.content.Context.MODE_PRIVATE)
        val jsonStr = prefs.getString(KEY_HISTORY, "[]")
        val arr = org.json.JSONArray(jsonStr)
        return (0 until arr.length()).map { arr.getJSONObject(it) }
    }

    fun saveDownloadHistory(context: android.content.Context, title: String, url: String, thumbnailUrl: String) {
        val history = getHistory(context).toMutableList()
        val item = org.json.JSONObject().apply {
            put("title", title)
            put("url", url)
            put("thumbnailUrl", thumbnailUrl)
            put("timestamp", System.currentTimeMillis())
        }
        history.add(0, item)
        val arr = org.json.JSONArray()
        history.take(50).forEach { arr.put(it) }
        context.getSharedPreferences(PREFS_NAME, android.content.Context.MODE_PRIVATE)
            .edit().putString(KEY_HISTORY, arr.toString()).apply()
    }

    fun getNotifications(context: android.content.Context): List<org.json.JSONObject> {
        val prefs = context.getSharedPreferences(PREFS_NAME, android.content.Context.MODE_PRIVATE)
        val jsonStr = prefs.getString(KEY_NOTIFICATIONS, "[]")
        val arr = org.json.JSONArray(jsonStr)
        return (0 until arr.length()).map { arr.getJSONObject(it) }
    }

    fun saveNotification(context: android.content.Context, message: String, time: String) {
        val notifs = getNotifications(context).toMutableList()
        val item = org.json.JSONObject().apply {
            put("message", message)
            put("time", time)
            put("read", false)
        }
        notifs.add(0, item)
        val arr = org.json.JSONArray()
        notifs.take(50).forEach { arr.put(it) }
        context.getSharedPreferences(PREFS_NAME, android.content.Context.MODE_PRIVATE)
            .edit().putString(KEY_NOTIFICATIONS, arr.toString()).apply()
    }

    fun markNotificationsRead(context: android.content.Context) {
        val notifs = getNotifications(context)
        notifs.forEach { it.put("read", true) }
        val arr = org.json.JSONArray()
        notifs.forEach { arr.put(it) }
        context.getSharedPreferences(PREFS_NAME, android.content.Context.MODE_PRIVATE)
            .edit().putString(KEY_NOTIFICATIONS, arr.toString()).apply()
    }
}

fun guessExtension(url: String): String {
    val lowerUrl = url.lowercase()
    return when {
        lowerUrl.contains(".webm") -> "webm"
        lowerUrl.contains(".mp3") -> "mp3"
        lowerUrl.contains(".m4a") -> "m4a"
        lowerUrl.contains(".jpg") || lowerUrl.contains(".jpeg") -> "jpg"
        lowerUrl.contains(".png") -> "png"
        lowerUrl.contains(".webp") -> "webp"
        lowerUrl.contains(".gif") -> "gif"
        else -> "mp4"
    }
}

fun resolveAndTriggerDownload(
    context: android.content.Context,
    coroutineScope: kotlinx.coroutines.CoroutineScope,
    quality: MediaQuality,
    title: String,
    thumbnailUrl: String
) {
    coroutineScope.launch {
        val extension = guessExtension(quality.url)
        val safeTitle = title.replace("[^a-zA-Z0-9.-]".toRegex(), "_").take(50)
        val fileName = "${safeTitle}_${System.currentTimeMillis()}.$extension"
        val downloadUri = android.net.Uri.parse(quality.url)
        
        val request = android.app.DownloadManager.Request(downloadUri).apply {
            setTitle(title)
            setDescription("Downloading $title")
            setNotificationVisibility(android.app.DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
            setDestinationInExternalPublicDir(android.os.Environment.DIRECTORY_DOWNLOADS, fileName)
            setAllowedOverMetered(true)
            setAllowedOverRoaming(true)
        }
        
        val downloadManager = context.getSystemService(android.content.Context.DOWNLOAD_SERVICE) as android.app.DownloadManager
        downloadManager.enqueue(request)
        
        PreferencesHelper.saveDownloadHistory(context, title, quality.url, thumbnailUrl)
        
        android.widget.Toast.makeText(context, "Download started: $title", android.widget.Toast.LENGTH_SHORT).show()
    }
}
