import re

with open('app/src/main/java/com/example/UpdateChecker.kt', 'r') as f:
    content = f.read()

target = """            dismissButton = {
                TextButton(onClick = { 
                     showDialog = false 
                     val prefs = context.getSharedPreferences("AuraPrefs", Context.MODE_PRIVATE)
                    prefs.edit().putInt("IgnoredUpdateVersion", remoteVersionState).apply()
                }) {
                    Text("Skip this version", color = textColor.copy(alpha = 0.5f))
                }
            }"""

replace = """            dismissButton = {
                TextButton(onClick = { 
                     showDialog = false 
                }) {
                    Text("Cancel", color = textColor.copy(alpha = 0.5f))
                }
            }"""

if target in content:
    content = content.replace(target, replace)
    with open('app/src/main/java/com/example/UpdateChecker.kt', 'w') as f:
        f.write(content)
    print("UpdateChecker patched (cancel button)")
else:
    print("Target not found in UpdateChecker (cancel)")
