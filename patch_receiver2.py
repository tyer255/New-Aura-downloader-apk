import re

with open('app/src/main/java/com/example/DownloadReceiver.kt', 'r') as f:
    content = f.read()

# Let's just completely replace the onReceive block because it's simpler
new_content = """package com.example

import android.app.DownloadManager
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.util.Log

class DownloadReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == DownloadManager.ACTION_DOWNLOAD_COMPLETE) {
            val downloadId = intent.getLongExtra(DownloadManager.EXTRA_DOWNLOAD_ID, -1)
            if (downloadId != -1L) {
                val prefs = context.getSharedPreferences("AuraPrefs", Context.MODE_PRIVATE)
                val updateDownloadId = prefs.getLong("update_download_id", -1L)
                
                val downloadManager = context.getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
                
                if (updateDownloadId == downloadId) {
                    val uri = downloadManager.getUriForDownloadedFile(downloadId)
                    if (uri != null) {
                        val installIntent = Intent(Intent.ACTION_VIEW).apply {
                            setDataAndType(uri, "application/vnd.android.package-archive")
                            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_GRANT_READ_URI_PERMISSION
                        }
                        try {
                            context.startActivity(installIntent)
                        } catch (e: Exception) {
                            Log.e("DownloadReceiver", "Error installing update", e)
                        }
                    }
                    return
                }
                
                // Normal download
                val query = DownloadManager.Query().setFilterById(downloadId)
                val cursor = downloadManager.query(query)
                if (cursor != null && cursor.moveToFirst()) {
                    val statusIndex = cursor.getColumnIndex(DownloadManager.COLUMN_STATUS)
                    if (statusIndex != -1) {
                        val status = cursor.getInt(statusIndex)
                        if (status == DownloadManager.STATUS_SUCCESSFUL) {
                            val titleIndex = cursor.getColumnIndex(DownloadManager.COLUMN_TITLE)
                            val title = if (titleIndex != -1) cursor.getString(titleIndex) else "File"
                            
                            val mimeTypeIndex = cursor.getColumnIndex(DownloadManager.COLUMN_MEDIA_TYPE)
                            val mimeType = if (mimeTypeIndex != -1) cursor.getString(mimeTypeIndex) ?: "" else ""
                            
                            val message = when {
                                mimeType.startsWith("video/") -> "Your video is downloaded."
                                mimeType.startsWith("audio/") -> "Your MP3 file is downloaded."
                                mimeType.startsWith("image/") -> "Your photo is downloaded."
                                else -> "Your file is downloaded."
                            }
                            
                            PreferencesHelper.saveNotification(context, message, "Just now")
                        }
                    }
                }
                cursor?.close()
            }
        }
    }
}
"""

with open('app/src/main/java/com/example/DownloadReceiver.kt', 'w') as f:
    f.write(new_content)
print("Receiver patched with getUriForDownloadedFile")
