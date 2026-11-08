package com.auradownloader.app

import android.Manifest
import android.app.Activity
import android.appwidget.AppWidgetManager
import android.content.ClipboardManager
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.Toast
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class WidgetActionActivity : Activity() {
    
    private var pendingDownloadAction: (() -> Unit)? = null
    private var isProcessed = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
    }
    
    override fun onResume() {
        super.onResume()
        if (isProcessed) return
        isProcessed = true
        
        val appWidgetId = intent.getIntExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, AppWidgetManager.INVALID_APPWIDGET_ID)
        val action = intent.action

        if (action == AuraAppWidgetProvider.ACTION_WIDGET_PASTE) {
            handlePaste(appWidgetId)
        } else if (action == AuraAppWidgetProvider.ACTION_WIDGET_DOWNLOAD) {
            handleDownload(appWidgetId)
        } else {
            finish()
        }
    }

    private fun handlePaste(appWidgetId: Int) {
        val appWidgetManager = AppWidgetManager.getInstance(this)
        
        val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        val clip = clipboard.primaryClip
        val url = if (clip != null && clip.itemCount > 0) {
            clip.getItemAt(0).text?.toString() ?: ""
        } else {
            ""
        }
        
        if (url.isEmpty() || (!url.startsWith("http://") && !url.startsWith("https://"))) {
            AuraAppWidgetProvider.updateAppWidget(this, appWidgetManager, appWidgetId, AuraAppWidgetProvider.STATE_DEFAULT)
            Toast.makeText(this, "No valid URL in clipboard", Toast.LENGTH_SHORT).show()
            finish()
            return
        }
        
        AuraAppWidgetProvider.updateAppWidget(this, appWidgetManager, appWidgetId, AuraAppWidgetProvider.STATE_LOADING)
        
        CoroutineScope(Dispatchers.IO).launch {
            try {
                var extResult = kotlinx.coroutines.withTimeoutOrNull(60000L) {
                    extractWithCobalt(url)
                } ?: getFallbackResult(url)
                
                if (!extResult.success || extResult.qualities.isEmpty()) {
                    val fallback = getFallbackResult(url)
                    if (fallback.qualities.isNotEmpty()) extResult = fallback
                }
                
                withContext(Dispatchers.Main) {
                    if (extResult.qualities.isNotEmpty()) {
                        AuraAppWidgetProvider.updateAppWidgetQualities(this@WidgetActionActivity, appWidgetManager, appWidgetId, extResult)
                    } else {
                        AuraAppWidgetProvider.updateAppWidget(this@WidgetActionActivity, appWidgetManager, appWidgetId, AuraAppWidgetProvider.STATE_DEFAULT)
                        Toast.makeText(this@WidgetActionActivity, "Could not extract link", Toast.LENGTH_SHORT).show()
                    }
                    finish()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    AuraAppWidgetProvider.updateAppWidget(this@WidgetActionActivity, appWidgetManager, appWidgetId, AuraAppWidgetProvider.STATE_DEFAULT)
                    Toast.makeText(this@WidgetActionActivity, "Error fetching media", Toast.LENGTH_SHORT).show()
                    finish()
                }
            }
        }
    }

    private fun handleDownload(appWidgetId: Int) {
        val url = intent.getStringExtra("url") ?: return
        val label = intent.getStringExtra("label") ?: "Download"
        val title = intent.getStringExtra("title") ?: "Aura Download"
        val thumbnailUrl = intent.getStringExtra("thumbnailUrl") ?: ""
        
        val downloadAction = {
            CoroutineScope(Dispatchers.IO).launch {
                try {
                    withContext(Dispatchers.Main) {
                        Toast.makeText(this@WidgetActionActivity, "Preparing high quality download...", Toast.LENGTH_SHORT).show()
                    }
                    var initialUrl = if (url.startsWith("http")) url else "${ApiSecurity.getBaseUrl()}${if (url.startsWith("/")) "" else "/"}${url}"
                    var finalDirectUrl = initialUrl

                    if (initialUrl.contains("spotify-resolve")) {
                        if (title.isNotEmpty()) {
                            try {
                                val encT = java.net.URLEncoder.encode(title, "UTF-8")
                                if (initialUrl.contains("title=&")) initialUrl = initialUrl.replace("title=&", "title=$encT&")
                                else if (initialUrl.endsWith("title=")) initialUrl += encT
                                else if (!initialUrl.contains("title=")) initialUrl += "&title=$encT"
                            } catch (e: Exception) { e.printStackTrace() }
                        }
                    }
                    if (initialUrl.contains("/api/get-youtube-link") || initialUrl.contains("get-youtube-link") || initialUrl.contains("spotify-resolve")) {
                        try {
                            val req = okhttp3.Request.Builder()
                                .url(initialUrl)
                                .addHeader("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                                .addHeader("X-Aura-Api-Key", ApiSecurity.API_KEY)
                                .build()
                            val res = okHttpClient.newCall(req).execute()
                            if (res.isSuccessful) {
                                val body = res.body?.string() ?: ""
                                if (body.trim().startsWith("{")) {
                                    val json = org.json.JSONObject(body)
                                    if (json.optBoolean("success", true) && json.has("url")) {
                                        val extractedUrl = json.getString("url")
                                        if (extractedUrl.isNotEmpty()) {
                                            finalDirectUrl = extractedUrl
                                        }
                                    }
                                }
                            }
                        } catch (e: Exception) {
                            e.printStackTrace()
                        }
                    }

                    if (!finalDirectUrl.startsWith("http")) {
                        finalDirectUrl = "${ApiSecurity.getBaseUrl()}${if (finalDirectUrl.startsWith("/")) "" else "/"}$finalDirectUrl"
                    }

                    val ext = guessExtension(finalDirectUrl, label)
                    val sanitizedTitle = title.replace(Regex("""[\\/:*?"<>|]"""), "_").take(40).ifEmpty { "Aura_Media" }
                    val filename = "Aura_${sanitizedTitle}_${System.currentTimeMillis()}.$ext"

                    val request = android.app.DownloadManager.Request(android.net.Uri.parse(finalDirectUrl))
                    request.setTitle(title.ifEmpty { "Aura Download" })
                    request.setDescription("Downloading $ext file...")
                    request.addRequestHeader("X-Aura-Api-Key", ApiSecurity.API_KEY)
                    request.setNotificationVisibility(android.app.DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                    request.setAllowedOverMetered(true)
                    request.setAllowedOverRoaming(true)
                    
                    request.setDestinationInExternalPublicDir(android.os.Environment.DIRECTORY_DOWNLOADS, filename)
                    
                    val mimeType = android.webkit.MimeTypeMap.getSingleton().getMimeTypeFromExtension(ext) ?: "application/octet-stream"
                    request.setMimeType(mimeType)
                    
                    val downloadManager = getSystemService(Context.DOWNLOAD_SERVICE) as android.app.DownloadManager
                    downloadManager.enqueue(request)
                    
                    PreferencesHelper.saveDownload(this@WidgetActionActivity, title.ifEmpty { "Aura Download" }, finalDirectUrl, thumbnailUrl)
                    
                } catch (e: Exception) {
                    withContext(Dispatchers.Main) {
                        Toast.makeText(this@WidgetActionActivity, "Download failed: ${e.message}", Toast.LENGTH_SHORT).show()
                    }
                } finally {
                    val appWidgetManager = AppWidgetManager.getInstance(this@WidgetActionActivity)
                    withContext(Dispatchers.Main) {
                        AuraAppWidgetProvider.updateAppWidget(this@WidgetActionActivity, appWidgetManager, appWidgetId, AuraAppWidgetProvider.STATE_DEFAULT)
                        finish()
                    }
                }
            }
        }

        if (Build.VERSION.SDK_INT <= 28 && ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
            pendingDownloadAction = { downloadAction() }
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.WRITE_EXTERNAL_STORAGE), 100)
        } else {
            downloadAction()
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == 100) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                pendingDownloadAction?.invoke()
            } else {
                Toast.makeText(this, "Permission denied. Cannot download file.", Toast.LENGTH_SHORT).show()
                finish()
            }
        }
    }
}
