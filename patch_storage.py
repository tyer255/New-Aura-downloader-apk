import re

with open('app/src/main/java/com/example/MainActivity.kt', 'r') as f:
    content = f.read()

launcher_target = '''    val notificationPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission(),
        onResult = { isGranted ->'''

launcher_replace = '''    var pendingDownloadAction by remember { mutableStateOf<(() -> Unit)?>(null) }
    val storagePermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission(),
        onResult = { isGranted ->
            if (isGranted) {
                pendingDownloadAction?.invoke()
                pendingDownloadAction = null
            } else {
                android.widget.Toast.makeText(context, "Storage permission is required to download on this device.", android.widget.Toast.LENGTH_LONG).show()
            }
        }
    )

    val notificationPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission(),
        onResult = { isGranted ->'''


download_target = '''                                        onClick = {
                                            try {
                                                val fullUrl = if (q.url.startsWith("http")) q.url else "https://aura-downloader-yg40.onrender.com${if (q.url.startsWith("/")) "" else "/"}${q.url}"
                                                val request = android.app.DownloadManager.Request(android.net.Uri.parse(fullUrl))
                                                request.setTitle(r.title.ifEmpty { "Aura Download" })
                                                request.setDescription("Downloading file...")
                                                request.setNotificationVisibility(android.app.DownloadManager.Request.VISIBILITY_VISIBLE)
                                                request.setAllowedOverMetered(true)
                                                request.setAllowedOverRoaming(true)
                                                
                                                val ext = guessExtension(fullUrl, q.label)
                                                val filename = "AuraDownloader_${System.currentTimeMillis()}.$ext"
                                                request.setDestinationInExternalPublicDir(android.os.Environment.DIRECTORY_DOWNLOADS, filename)
                                                
                                                val mimeType = android.webkit.MimeTypeMap.getSingleton().getMimeTypeFromExtension(ext) ?: "application/octet-stream"
                                                request.setMimeType(mimeType)
                                                
                                                val downloadManager = context.getSystemService(android.content.Context.DOWNLOAD_SERVICE) as android.app.DownloadManager
                                                downloadManager.enqueue(request)
                                                
                                                PreferencesHelper.saveDownload(context, r.title.ifEmpty { "Aura Download" }, r.thumbnailUrl)
                                                
                                                android.widget.Toast.makeText(context, "Download started...", android.widget.Toast.LENGTH_SHORT).show()
                                            } catch (e: Exception) {
                                                android.widget.Toast.makeText(context, "Download failed: ${e.message}", android.widget.Toast.LENGTH_SHORT).show()
                                            }
                                        },'''

download_replace = '''                                        onClick = {
                                            val action = {
                                                try {
                                                    val fullUrl = if (q.url.startsWith("http")) q.url else "https://aura-downloader-yg40.onrender.com${if (q.url.startsWith("/")) "" else "/"}${q.url}"
                                                    val request = android.app.DownloadManager.Request(android.net.Uri.parse(fullUrl))
                                                    request.setTitle(r.title.ifEmpty { "Aura Download" })
                                                    request.setDescription("Downloading file...")
                                                    request.setNotificationVisibility(android.app.DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                                                    request.setAllowedOverMetered(true)
                                                    request.setAllowedOverRoaming(true)
                                                    
                                                    val ext = guessExtension(fullUrl, q.label)
                                                    val filename = "AuraDownloader_${System.currentTimeMillis()}.$ext"
                                                    request.setDestinationInExternalPublicDir(android.os.Environment.DIRECTORY_DOWNLOADS, filename)
                                                    
                                                    val mimeType = android.webkit.MimeTypeMap.getSingleton().getMimeTypeFromExtension(ext) ?: "application/octet-stream"
                                                    request.setMimeType(mimeType)
                                                    
                                                    val downloadManager = context.getSystemService(android.content.Context.DOWNLOAD_SERVICE) as android.app.DownloadManager
                                                    downloadManager.enqueue(request)
                                                    
                                                    PreferencesHelper.saveDownload(context, r.title.ifEmpty { "Aura Download" }, r.thumbnailUrl)
                                                    
                                                    android.widget.Toast.makeText(context, "Download started...", android.widget.Toast.LENGTH_SHORT).show()
                                                } catch (e: Exception) {
                                                    android.widget.Toast.makeText(context, "Download failed: ${e.message}", android.widget.Toast.LENGTH_SHORT).show()
                                                }
                                            }
                                            if (android.os.Build.VERSION.SDK_INT <= 28 && androidx.core.content.ContextCompat.checkSelfPermission(context, android.Manifest.permission.WRITE_EXTERNAL_STORAGE) != android.content.pm.PackageManager.PERMISSION_GRANTED) {
                                                pendingDownloadAction = action
                                                storagePermissionLauncher.launch(android.Manifest.permission.WRITE_EXTERNAL_STORAGE)
                                            } else {
                                                action()
                                            }
                                        },'''

content = content.replace(launcher_target, launcher_replace)
content = content.replace(download_target, download_replace)

with open('app/src/main/java/com/example/MainActivity.kt', 'w') as f:
    f.write(content)
