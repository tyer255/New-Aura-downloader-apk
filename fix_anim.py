import re
with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    code = f.read()

target_start = """            result?.let { r ->
                if (r.success) {"""
replacement_start = """            androidx.compose.animation.AnimatedVisibility(
                visible = result != null && !isDownloading,
                enter = androidx.compose.animation.expandVertically() + androidx.compose.animation.fadeIn(),
                exit = androidx.compose.animation.shrinkVertically() + androidx.compose.animation.fadeOut()
            ) {
                result?.let { r ->
                    if (r.success) {"""

if target_start in code:
    code = code.replace(target_start, replacement_start)
    print("Replaced start")

target_end = """                        Text(r.error ?: "An unknown error occurred", color = textColor, textAlign = TextAlign.Center, style = MaterialTheme.typography.bodyMedium)
                    }
                }
            }
        }
    }

    if (showNotificationsSheet) {"""

replacement_end = """                        Text(r.error ?: "An unknown error occurred", color = textColor, textAlign = TextAlign.Center, style = MaterialTheme.typography.bodyMedium)
                    }
                }
            }
                }
            }
        }
    }

    if (showNotificationsSheet) {"""

if target_end in code:
    code = code.replace(target_end, replacement_end)
    print("Replaced end")
else:
    # Try finding another way to inject closing brackets
    m = re.search(r'Text\(r\.error \?\: "An unknown error occurred".*?\}\s*\}\s*\}\s*\}\s*\}\s*if \(showNotificationsSheet\) \{', code, re.DOTALL)
    if m:
        code = code.replace(m.group(0), m.group(0).replace('if (showNotificationsSheet) {', '}\n}\nif (showNotificationsSheet) {'))
        print("Replaced end with regex")

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(code)
