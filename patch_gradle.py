import re

with open('app/build.gradle.kts', 'r') as f:
    content = f.read()

prefix = """import java.util.Properties
import java.io.FileInputStream
import java.io.FileOutputStream

val versionPropsFile = rootProject.file("version.properties")
val versionProps = Properties()
if (versionPropsFile.exists()) {
    versionProps.load(FileInputStream(versionPropsFile))
}

var currentVersionCode = (versionProps["VERSION_CODE"] as? String)?.toIntOrNull() ?: 4
var currentVersionName = (versionProps["VERSION_NAME"] as? String) ?: "2.2.0"

val taskRequests = gradle.startParameter.taskRequests.flatMap { it.args }
if (taskRequests.any { it.contains("assemble") || it.contains("bundle") }) {
    currentVersionCode += 1
    versionProps["VERSION_CODE"] = currentVersionCode.toString()
    versionProps.store(FileOutputStream(versionPropsFile), null)
    println("===================================================")
    println("Is APK ka final VERSION CODE yeh hai: $currentVersionCode")
    println("===================================================")
}

"""

if "import java.util.Properties" not in content:
    content = prefix + content
    
    # replace versionCode = 4 with versionCode = currentVersionCode
    content = re.sub(r'versionCode\s*=\s*\d+', 'versionCode = currentVersionCode', content)
    content = re.sub(r'versionName\s*=\s*"[^"]+"', 'versionName = currentVersionName', content)
    
    with open('app/build.gradle.kts', 'w') as f:
        f.write(content)
    print("Gradle patched")
else:
    print("Already patched")
