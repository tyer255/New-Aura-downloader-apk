with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    code = f.read()

target = """            val downloadManager = context.getSystemService(Context.DOWNLOAD_SERVICE) as android.app.DownloadManager
            downloadManager.enqueue(request)

            PreferencesHelper.saveDownload(context, title.ifEmpty { "Aura Download" }, thumbnailUrl)

            withContext(Dispatchers.Main) {
                Toast.makeText(context, "Download started: $filename", Toast.LENGTH_LONG).show()
            }"""

replacement = """            try {
                val downloadManager = context.getSystemService(Context.DOWNLOAD_SERVICE) as? android.app.DownloadManager
                if (downloadManager != null) {
                    downloadManager.enqueue(request)
                    PreferencesHelper.saveDownload(context, title.ifEmpty { "Aura Download" }, thumbnailUrl)
                    withContext(Dispatchers.Main) {
                        Toast.makeText(context, "Download started: $filename", Toast.LENGTH_LONG).show()
                    }
                } else {
                    throw IllegalStateException("DownloadManager unavailable")
                }
            } catch (e: Exception) {
                e.printStackTrace()
                withContext(Dispatchers.Main) {
                    try {
                        val browserIntent = Intent(Intent.ACTION_VIEW, android.net.Uri.parse(finalDirectUrl)).apply {
                            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                        }
                        context.startActivity(browserIntent)
                        Toast.makeText(context, "Opening in browser to download...", Toast.LENGTH_LONG).show()
                    } catch (err: Exception) {
                        Toast.makeText(context, "Download failed: ${e.message}", Toast.LENGTH_LONG).show()
                    }
                }
            }"""

if target in code:
    code = code.replace(target, replacement)
    with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
        f.write(code)
    print("Download fallback applied successfully!")
else:
    print("Target not found for download fallback.")
