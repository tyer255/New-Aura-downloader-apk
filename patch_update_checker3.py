import re

with open('app/src/main/java/com/example/UpdateChecker.kt', 'r') as f:
    content = f.read()

target = """                TextButton(onClick = {
                    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(updateUrl))
                    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    context.startActivity(intent)
                }) {
                    Text("Update Now", color = Color(0xFF38BDF8))
                }"""

replace = """                TextButton(onClick = {
                    try {
                        val request = android.app.DownloadManager.Request(Uri.parse(updateUrl))
                        request.setTitle("Aura Downloader Update")
                        request.setDescription("Downloading new version...")
                        request.setNotificationVisibility(android.app.DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                        request.setDestinationInExternalPublicDir(android.os.Environment.DIRECTORY_DOWNLOADS, "AuraDownloader_Update.apk")
                        request.setMimeType("application/vnd.android.package-archive")
                        
                        val downloadManager = context.getSystemService(Context.DOWNLOAD_SERVICE) as android.app.DownloadManager
                        val downloadId = downloadManager.enqueue(request)
                        
                        val prefs = context.getSharedPreferences("AuraPrefs", Context.MODE_PRIVATE)
                        prefs.edit().putLong("update_download_id", downloadId).apply()
                        
                        android.widget.Toast.makeText(context, "Update downloading...", android.widget.Toast.LENGTH_SHORT).show()
                    } catch (e: Exception) {
                        Log.e("UpdateChecker", "Failed to start download", e)
                    }
                    showDialog = false
                }) {
                    Text("Update", color = Color(0xFF38BDF8))
                }"""

if target in content:
    content = content.replace(target, replace)
    with open('app/src/main/java/com/example/UpdateChecker.kt', 'w') as f:
        f.write(content)
    print("UpdateChecker patched")
else:
    print("Target not found in UpdateChecker")
