with open('app/src/main/java/com/example/MainActivity.kt', 'r') as f:
    content = f.read()

target1 = '''                                        AsyncImage(
                                            model = coil.request.ImageRequest.Builder(context).data(r.thumbnailUrl).crossfade(true).build(),'''
replace1 = '''                                        AsyncImage(
                                            model = coil.request.ImageRequest.Builder(context).data(r.thumbnailUrl).decoderFactory(coil.decode.VideoFrameDecoder.Factory()).crossfade(true).build(),'''

target2 = '''                                        AsyncImage(
                                            model = coil.request.ImageRequest.Builder(context).data(thumb).crossfade(true).build(),'''
replace2 = '''                                        AsyncImage(
                                            model = coil.request.ImageRequest.Builder(context).data(thumb).decoderFactory(coil.decode.VideoFrameDecoder.Factory()).crossfade(true).build(),'''

new_content = content.replace(target1, replace1).replace(target2, replace2)

with open('app/src/main/java/com/example/MainActivity.kt', 'w') as f:
    f.write(new_content)
