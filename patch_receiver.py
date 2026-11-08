import re

with open('app/src/main/java/com/example/DownloadReceiver.kt', 'r') as f:
    content = f.read()

target = """                        if (status == DownloadManager.STATUS_SUCCESSFUL) {
                            val titleIndex = cursor.getColumnIndex(DownloadManager.COLUMN_TITLE)"""

replace = """                        if (status == DownloadManager.STATUS_SUCCESSFUL) {
                            val prefs = context.getSharedPreferences("AuraPrefs", Context.MODE_PRIVATE)
                            val updateDownloadId = prefs.getLong("update_download_id", -1L)
                            
                            if (updateDownloadId == downloadId) {
                                val uriIndex = cursor.getColumnIndex(DownloadManager.COLUMN_LOCAL_URI)
                                if (uriIndex != -1) {
                                    val localUriString = cursor.getString(uriIndex)
                                    val localUri = android.net.Uri.parse(localUriString)
                                    
                                    val fileUri = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.N) {
                                        val file = java.io.File(localUri.path!!)
                                        androidx.core.content.FileProvider.getUriForFile(
                                            context,
                                            "${context.packageName}.provider",
                                            file
                                        )
                                    } else {
                                        localUri
                                    }
                                    
                                    val installIntent = Intent(Intent.ACTION_VIEW).apply {
                                        setDataAndType(fileUri, "application/vnd.android.package-archive")
                                        flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_GRANT_READ_URI_PERMISSION
                                    }
                                    try {
                                        context.startActivity(installIntent)
                                    } catch (e: Exception) {
                                        e.printStackTrace()
                                    }
                                }
                                cursor?.close()
                                return
                            }
                            
                            val titleIndex = cursor.getColumnIndex(DownloadManager.COLUMN_TITLE)"""

if target in content:
    content = content.replace(target, replace)
    
    # Check if FileProvider is used and imported (actually we used fully qualified name)
    with open('app/src/main/java/com/example/DownloadReceiver.kt', 'w') as f:
        f.write(content)
    print("Receiver patched")
else:
    print("Target not found in Receiver")
