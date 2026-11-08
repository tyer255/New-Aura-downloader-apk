awk '
/    var isActualDownloading by remember \{ mutableStateOf\(false\) \}/ {
    print $0
    print "    var activeDownloadId by remember { mutableStateOf<Long?>(null) }"
    next
}
/    val coroutineScope = rememberCoroutineScope\(\)/ {
    print $0
    print ""
    print "    LaunchedEffect(activeDownloadId) {"
    print "        val id = activeDownloadId ?: return@LaunchedEffect"
    print "        isActualDownloading = true"
    print "        while (isActualDownloading) {"
    print "            val query = android.app.DownloadManager.Query().setFilterById(id)"
    print "            val downloadManager = context.getSystemService(android.content.Context.DOWNLOAD_SERVICE) as android.app.DownloadManager"
    print "            val cursor = downloadManager.query(query)"
    print "            if (cursor.moveToFirst()) {"
    print "                val statusIdx = cursor.getColumnIndex(android.app.DownloadManager.COLUMN_STATUS)"
    print "                val status = if (statusIdx != -1) cursor.getInt(statusIdx) else -1"
    print "                if (status == android.app.DownloadManager.STATUS_SUCCESSFUL || status == android.app.DownloadManager.STATUS_FAILED) {"
    print "                    isActualDownloading = false"
    print "                    if (status == android.app.DownloadManager.STATUS_SUCCESSFUL) {"
    print "                        actualDownloadProgress = 100"
    print "                    }"
    print "                    cursor.close()"
    print "                    break"
    print "                }"
    print "                val bytesDownloadedIdx = cursor.getColumnIndex(android.app.DownloadManager.COLUMN_BYTES_DOWNLOADED_SO_FAR)"
    print "                val bytesTotalIdx = cursor.getColumnIndex(android.app.DownloadManager.COLUMN_TOTAL_SIZE_BYTES)"
    print "                if (bytesDownloadedIdx != -1 && bytesTotalIdx != -1) {"
    print "                    val bytesDownloaded = cursor.getInt(bytesDownloadedIdx)"
    print "                    val bytesTotal = cursor.getInt(bytesTotalIdx)"
    print "                    if (bytesTotal > 0) {"
    print "                        actualDownloadProgress = ((bytesDownloaded * 100L) / bytesTotal).toInt()"
    print "                    }"
    print "                }"
    print "            }"
    print "            cursor.close()"
    print "            kotlinx.coroutines.delay(500)"
    print "        }"
    print "    }"
    next
}
{ print $0 }
' app/src/main/java/com/auradownloader/app/MainActivity.kt > tmp.kt && mv tmp.kt app/src/main/java/com/auradownloader/app/MainActivity.kt

perl -0777 -pi -e 's/resolveAndTriggerDownload\(context, coroutineScope, q, r\.title, item\.thumbnail \?\: ""\)/resolveAndTriggerDownload(context, coroutineScope, q, r.title, item.thumbnail ?: "") { id -> activeDownloadId = id }/g' app/src/main/java/com/auradownloader/app/MainActivity.kt

perl -0777 -pi -e 's/resolveAndTriggerDownload\(\n                                                    context,\n                                                    coroutineScope,\n                                                    q,\n                                                    r\.title,\n                                                    r\.thumbnail \?\: ""\n                                                \)/resolveAndTriggerDownload(\n                                                    context,\n                                                    coroutineScope,\n                                                    q,\n                                                    r.title,\n                                                    r.thumbnail ?: ""\n                                                ) { id -> activeDownloadId = id }/g' app/src/main/java/com/auradownloader/app/MainActivity.kt

