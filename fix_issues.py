import re
with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    code = f.read()

# Fix 1: Update the condition for the Audio player to not show for non-audio media
target_audio_player = 'if (r.isSpotify || r.mediaType == "audio" || !r.previewAudioUrl.isNullOrEmpty()) {'
replacement_audio_player = 'if (r.isSpotify || r.mediaType == "audio") {'
if target_audio_player in code:
    code = code.replace(target_audio_player, replacement_audio_player)
    print("Fixed audio player check")
else:
    # Just in case it's slightly different
    m = re.search(r'if \(r\.isSpotify \|\|.*?previewAudioUrl.*?\) \{', code)
    if m:
        code = code.replace(m.group(0), replacement_audio_player)
        print("Fixed audio player check (regex)")
    else:
        print("Could not find audio player check")

# Fix 2: Wrap result?.let in AnimatedVisibility
target_result = '''            result?.let { r ->
                if (r.success) {'''

replacement_result = '''            AnimatedVisibility(
                visible = result != null && !isDownloading,
                enter = androidx.compose.animation.expandVertically() + androidx.compose.animation.fadeIn(),
                exit = androidx.compose.animation.shrinkVertically() + androidx.compose.animation.fadeOut()
            ) {
                result?.let { r ->
                    if (r.success) {'''

target_result_end = '''                }
            }

            Spacer(modifier = Modifier.weight(1f))'''

replacement_result_end = '''                }
                }
            }

            Spacer(modifier = Modifier.weight(1f))'''

if target_result in code and target_result_end in code:
    code = code.replace(target_result, replacement_result)
    code = code.replace(target_result_end, replacement_result_end)
    print("Wrapped result in AnimatedVisibility")
else:
    print("Could not wrap result in AnimatedVisibility")

# Fix 3: Simulate extraction progress
# Replace the coroutine block
target_coroutine1 = '''                launch {
                    val fm = fetchFastMeta(sharedUrl)
                    if (fm != null) {
                        if (fm.thumbnailUrl.isNotEmpty()) previewThumbnailUrl = fm.thumbnailUrl
                        if (fm.title.isNotEmpty()) previewTitle = fm.title
                    }
                }

                val extResult = extractWithCobalt(sharedUrl)
                extractionProgress = 1.0f
                kotlinx.coroutines.delay(200)
                isDownloading = false
                result = extResult'''

replacement_coroutine1 = '''                launch {
                    val fm = fetchFastMeta(sharedUrl)
                    if (fm != null) {
                        if (fm.thumbnailUrl.isNotEmpty()) previewThumbnailUrl = fm.thumbnailUrl
                        if (fm.title.isNotEmpty()) previewTitle = fm.title
                    }
                }
                
                launch {
                    extractionProgress = 0.05f
                    loadingStep = 0
                    while (isDownloading && extractionProgress < 0.95f) {
                        kotlinx.coroutines.delay(800)
                        extractionProgress += 0.15f
                        if (extractionProgress > 0.95f) extractionProgress = 0.95f
                        loadingStep = (loadingStep + 1).coerceAtMost(LOADING_STEPS.lastIndex)
                    }
                }

                val extResult = extractWithCobalt(sharedUrl)
                extractionProgress = 1.0f
                loadingStep = LOADING_STEPS.lastIndex
                kotlinx.coroutines.delay(300)
                isDownloading = false
                result = extResult'''

if target_coroutine1 in code:
    code = code.replace(target_coroutine1, replacement_coroutine1)
    print("Fixed progress simulation 1")

target_coroutine2 = '''                                launch {
                                    val fm = fetchFastMeta(link)
                                    if (fm != null) {
                                        if (fm.thumbnailUrl.isNotEmpty()) previewThumbnailUrl = fm.thumbnailUrl
                                        if (fm.title.isNotEmpty()) previewTitle = fm.title
                                    }
                                }

                                val extResult = extractWithCobalt(link)
                                extractionProgress = 1.0f
                                kotlinx.coroutines.delay(200)
                                isDownloading = false
                                result = extResult'''

replacement_coroutine2 = '''                                launch {
                                    val fm = fetchFastMeta(link)
                                    if (fm != null) {
                                        if (fm.thumbnailUrl.isNotEmpty()) previewThumbnailUrl = fm.thumbnailUrl
                                        if (fm.title.isNotEmpty()) previewTitle = fm.title
                                    }
                                }
                                
                                launch {
                                    extractionProgress = 0.05f
                                    loadingStep = 0
                                    while (isDownloading && extractionProgress < 0.95f) {
                                        kotlinx.coroutines.delay(800)
                                        extractionProgress += 0.15f
                                        if (extractionProgress > 0.95f) extractionProgress = 0.95f
                                        loadingStep = (loadingStep + 1).coerceAtMost(LOADING_STEPS.lastIndex)
                                    }
                                }

                                val extResult = extractWithCobalt(link)
                                extractionProgress = 1.0f
                                loadingStep = LOADING_STEPS.lastIndex
                                kotlinx.coroutines.delay(300)
                                isDownloading = false
                                result = extResult'''

if target_coroutine2 in code:
    code = code.replace(target_coroutine2, replacement_coroutine2)
    print("Fixed progress simulation 2")

target_coroutine3 = '''                            launch {
                                val fm = fetchFastMeta(url)
                                if (fm != null) {
                                    if (fm.thumbnailUrl.isNotEmpty()) previewThumbnailUrl = fm.thumbnailUrl
                                    if (fm.title.isNotEmpty()) previewTitle = fm.title
                                }
                            }
                            
                            val extResult = extractWithCobalt(url)
                            
                            extractionProgress = 1.0f
                            kotlinx.coroutines.delay(200)
                            isDownloading = false
                            result = extResult'''

replacement_coroutine3 = '''                            launch {
                                val fm = fetchFastMeta(url)
                                if (fm != null) {
                                    if (fm.thumbnailUrl.isNotEmpty()) previewThumbnailUrl = fm.thumbnailUrl
                                    if (fm.title.isNotEmpty()) previewTitle = fm.title
                                }
                            }
                            
                            launch {
                                extractionProgress = 0.05f
                                loadingStep = 0
                                while (isDownloading && extractionProgress < 0.95f) {
                                    kotlinx.coroutines.delay(800)
                                    extractionProgress += 0.15f
                                    if (extractionProgress > 0.95f) extractionProgress = 0.95f
                                    loadingStep = (loadingStep + 1).coerceAtMost(LOADING_STEPS.lastIndex)
                                }
                            }
                            
                            val extResult = extractWithCobalt(url)
                            
                            extractionProgress = 1.0f
                            loadingStep = LOADING_STEPS.lastIndex
                            kotlinx.coroutines.delay(300)
                            isDownloading = false
                            result = extResult'''

if target_coroutine3 in code:
    code = code.replace(target_coroutine3, replacement_coroutine3)
    print("Fixed progress simulation 3")

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(code)
