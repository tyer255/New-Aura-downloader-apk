import re

with open('app/build.gradle.kts', 'r') as f:
    content = f.read()

content = content.replace('if (taskRequests.any { it.contains("assemble") || it.contains("bundle") }) {',
                          'if (taskRequests.any { (it.contains("assemble") || it.contains("bundle")) && it.contains("Release") }) {')

with open('app/build.gradle.kts', 'w') as f:
    f.write(content)

print("Updated")
