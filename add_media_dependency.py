import re
with open("app/build.gradle.kts", "r") as f:
    content = f.read()

dep = "  implementation(\"androidx.media:media:1.7.0\")\n"
if dep not in content:
    content = content.replace("dependencies {", "dependencies {\n" + dep)
    with open("app/build.gradle.kts", "w") as f:
        f.write(content)
