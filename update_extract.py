with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    code = f.read()

target = """                val mediaArr = json.optJSONArray("media")
                if (mediaArr != null) {
                    for (i in 0 until mediaArr.length()) {
                        val mObj = mediaArr.optJSONObject(i)
                        if (mObj != null) {
                            val tTitle = mObj.optString("title", "Track ${i+1}")
                            val tThumb = mObj.optString("thumbnail", thumbnail)
                            var tUrl = mObj.optString("url")
                            if (tUrl.startsWith("/")) tUrl = backendUrl.replace("/api/download", "") + tUrl

                            val innerQs = mObj.optJSONArray("qualities")
                            if (innerQs != null && innerQs.length() > 0) {
                                val q0 = innerQs.optJSONObject(0)
                                if (q0 != null) {
                                    var q0U = q0.optString("url")
                                    if (q0U.startsWith("/")) q0U = backendUrl.replace("/api/download", "") + q0U
                                    if (q0U.isNotEmpty()) tUrl = q0U
                                }
                            }

                            parsedTracks.add(SpotifyTrack(
                                name = tTitle,
                                artist = artistName,
                                trackNumber = i + 1,
                                resolveUrl = tUrl,
                                thumbnailUrl = tThumb
                            ))
                        }
                    }
                }"""

replacement = """                val mediaArr = json.optJSONArray("media")
                val carouselItems = mutableListOf<CarouselItem>()
                
                if (mediaArr != null) {
                    for (i in 0 until mediaArr.length()) {
                        val mObj = mediaArr.optJSONObject(i)
                        if (mObj != null) {
                            val tTitle = mObj.optString("title", "Track ${i+1}")
                            val tThumb = mObj.optString("thumbnail", thumbnail)
                            var tUrl = mObj.optString("url")
                            val tType = mObj.optString("type", "video")
                            if (tUrl.startsWith("/")) tUrl = backendUrl.replace("/api/download", "") + tUrl

                            val innerQs = mObj.optJSONArray("qualities")
                            if (innerQs != null && innerQs.length() > 0) {
                                val q0 = innerQs.optJSONObject(0)
                                if (q0 != null) {
                                    var q0U = q0.optString("url")
                                    if (q0U.startsWith("/")) q0U = backendUrl.replace("/api/download", "") + q0U
                                    if (q0U.isNotEmpty()) tUrl = q0U
                                }
                            }

                            if (isSpotify || mediaType == "audio" || isPlaylist) {
                                parsedTracks.add(SpotifyTrack(
                                    name = tTitle,
                                    artist = artistName,
                                    trackNumber = i + 1,
                                    resolveUrl = tUrl,
                                    thumbnailUrl = tThumb
                                ))
                            } else {
                                carouselItems.add(CarouselItem(
                                    url = tUrl,
                                    type = tType,
                                    thumbnail = tThumb
                                ))
                            }
                        }
                    }
                }"""

if target in code:
    code = code.replace(target, replacement)
    print("Replaced media parsing")

target_ret = """                    return@withContext DownloadResult(
                        success = true,
                        title = title,
                        thumbnailUrl = thumbnail,
                        qualities = resolvedQs,
                        isSpotify = isSpotify,
                        isPlaylist = isPlaylist,
                        artistName = artistName,
                        previewAudioUrl = firstAudio,
                        spotifyTracks = parsedTracks
                    )"""

replacement_ret = """                    return@withContext DownloadResult(
                        success = true,
                        title = title,
                        thumbnailUrl = thumbnail,
                        qualities = resolvedQs,
                        isSpotify = isSpotify,
                        isPlaylist = isPlaylist,
                        artistName = artistName,
                        previewAudioUrl = firstAudio,
                        spotifyTracks = parsedTracks,
                        mediaType = mediaType,
                        carouselItems = carouselItems
                    )"""

if target_ret in code:
    code = code.replace(target_ret, replacement_ret)
    print("Replaced DownloadResult creation")

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(code)
