with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "r") as f:
    code = f.read()

# Replace `context.imageLoader.execute(request)` with `launch(Dispatchers.IO) { context.imageLoader.execute(request) }`
code = code.replace("context.imageLoader.execute(request)", "launch(Dispatchers.IO) { context.imageLoader.execute(request) }")

with open("app/src/main/java/com/auradownloader/app/MainActivity.kt", "w") as f:
    f.write(code)
