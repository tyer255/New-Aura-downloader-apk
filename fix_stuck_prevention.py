import re

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    code = f.read()

# 1. Update extractWithCobalt call sites to use withTimeoutOrNull and try-catch-finally

old_extraction_block_1 = """                val extResult = extractWithCobalt(sharedUrl)
                                val pThumb = extResult.thumbnailUrl.ifEmpty { previewThumbnailUrl ?: "" }
                                if (pThumb.isNotEmpty()) {
                                    try {
                                        val request = coil.request.ImageRequest.Builder(context)
                                            .data(pThumb)
                                            .build()
                                        launch(Dispatchers.IO) { context.imageLoader.execute(request) }
                                    } catch (e: Exception) {}
                                }
                extractionProgress = 1.0f
                loadingStep = LOADING_STEPS.lastIndex
                kotlinx.coroutines.delay(300)
                isDownloading = false
                result = extResult"""

new_extraction_block_1 = """                try {
                    val extResult = kotlinx.coroutines.withTimeoutOrNull(12000L) {
                        extractWithCobalt(sharedUrl)
                    } ?: getFallbackResult(sharedUrl)
                    val pThumb = extResult.thumbnailUrl.ifEmpty { previewThumbnailUrl ?: "" }
                    if (pThumb.isNotEmpty()) {
                        try {
                            val request = coil.request.ImageRequest.Builder(context)
                                .data(pThumb)
                                .build()
                            launch(Dispatchers.IO) { context.imageLoader.execute(request) }
                        } catch (_: Exception) {}
                    }
                    result = extResult
                } catch (e: Exception) {
                    result = getFallbackResult(sharedUrl)
                } finally {
                    extractionProgress = 1.0f
                    loadingStep = LOADING_STEPS.lastIndex
                    isDownloading = false
                }"""

old_extraction_block_2 = """                                val extResult = extractWithCobalt(link)
                                val pThumb = extResult.thumbnailUrl.ifEmpty { previewThumbnailUrl ?: "" }
                                if (pThumb.isNotEmpty()) {
                                    try {
                                        val request = coil.request.ImageRequest.Builder(context)
                                            .data(pThumb)
                                            .build()
                                        launch(Dispatchers.IO) { context.imageLoader.execute(request) }
                                    } catch (e: Exception) {}
                                }
                                extractionProgress = 1.0f
                                loadingStep = LOADING_STEPS.lastIndex
                                kotlinx.coroutines.delay(300)
                                isDownloading = false
                                result = extResult"""

new_extraction_block_2 = """                                try {
                                    val extResult = kotlinx.coroutines.withTimeoutOrNull(12000L) {
                                        extractWithCobalt(link)
                                    } ?: getFallbackResult(link)
                                    val pThumb = extResult.thumbnailUrl.ifEmpty { previewThumbnailUrl ?: "" }
                                    if (pThumb.isNotEmpty()) {
                                        try {
                                            val request = coil.request.ImageRequest.Builder(context)
                                                .data(pThumb)
                                                .build()
                                            launch(Dispatchers.IO) { context.imageLoader.execute(request) }
                                        } catch (_: Exception) {}
                                    }
                                    result = extResult
                                } catch (e: Exception) {
                                    result = getFallbackResult(link)
                                } finally {
                                    extractionProgress = 1.0f
                                    loadingStep = LOADING_STEPS.lastIndex
                                    isDownloading = false
                                }"""

old_extraction_block_3 = """                            val extResult = extractWithCobalt(url)
                                val pThumb = extResult.thumbnailUrl.ifEmpty { previewThumbnailUrl ?: "" }
                                if (pThumb.isNotEmpty()) {
                                    try {
                                        val request = coil.request.ImageRequest.Builder(context)
                                            .data(pThumb)
                                            .build()
                                        launch(Dispatchers.IO) { context.imageLoader.execute(request) }
                                    } catch (e: Exception) {}
                                }
                            
                            extractionProgress = 1.0f
                            loadingStep = LOADING_STEPS.lastIndex
                            kotlinx.coroutines.delay(300)
                            isDownloading = false
                            result = extResult"""

new_extraction_block_3 = """                            try {
                                val extResult = kotlinx.coroutines.withTimeoutOrNull(12000L) {
                                    extractWithCobalt(url)
                                } ?: getFallbackResult(url)
                                val pThumb = extResult.thumbnailUrl.ifEmpty { previewThumbnailUrl ?: "" }
                                if (pThumb.isNotEmpty()) {
                                    try {
                                        val request = coil.request.ImageRequest.Builder(context)
                                            .data(pThumb)
                                            .build()
                                        launch(Dispatchers.IO) { context.imageLoader.execute(request) }
                                    } catch (_: Exception) {}
                                }
                                result = extResult
                            } catch (e: Exception) {
                                result = getFallbackResult(url)
                            } finally {
                                extractionProgress = 1.0f
                                loadingStep = LOADING_STEPS.lastIndex
                                isDownloading = false
                            }"""

code = code.replace(old_extraction_block_1, new_extraction_block_1)
code = code.replace(old_extraction_block_2, new_extraction_block_2)
code = code.replace(old_extraction_block_3, new_extraction_block_3)

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(code)

print("Extraction blocks updated with timeout & fallback safety.")
