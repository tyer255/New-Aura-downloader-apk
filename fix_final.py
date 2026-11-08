with open('app/src/main/java/com/auradownloader/app/MainActivity.kt') as f:
    code = f.read()

target = """                }
            }

            Spacer(modifier = Modifier.height(48.dp))"""
replacement = """                }
            }
            }

            Spacer(modifier = Modifier.height(48.dp))"""

if target in code:
    code = code.replace(target, replacement)
    print("Fixed missing AnimatedVisibility closing brace!")
else:
    print("Not found")

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(code)
