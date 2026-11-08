import re

with open('app/build.gradle.kts', 'r') as f:
    content = f.read()

# Remove the previously added prefix
bad_prefix = """import java.util.Properties
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

if bad_prefix in content:
    content = content.replace(bad_prefix, "")

# Ensure the proper imports are at the top
imports = """import java.util.Properties
import java.io.FileInputStream
import java.io.FileOutputStream
"""

if "import java.util.Properties" not in content:
    content = imports + content

# Insert the logic after plugins block
logic = """
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

if "val versionPropsFile =" not in content:
    # find plugins block end
    plugins_end = content.find("}")
    if plugins_end != -1:
        # Actually plugins block is:
        # plugins {
        #   ...
        # }
        # Let's find the closing brace of the plugins block
        plugins_start = content.find("plugins {")
        if plugins_start != -1:
            plugins_end = content.find("}", plugins_start)
            if plugins_end != -1:
                content = content[:plugins_end+1] + "\n" + logic + content[plugins_end+1:]

with open('app/build.gradle.kts', 'w') as f:
    f.write(content)
print("Fixed gradle")
