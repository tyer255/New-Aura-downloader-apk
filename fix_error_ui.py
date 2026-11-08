with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'r') as f:
    code = f.read()

import re

# Let's find the 'else' block for !r.success
m = re.search(r'\} else \{\s*Box\(\s*modifier = Modifier\.fillMaxWidth\(\)\.clip\(RoundedCornerShape\(16\.dp\)\)\.background\(Color\(0xFFEF4444\)\.copy\(alpha = 0\.1f\)\).*?\)\s*\}\s*\}', code, re.DOTALL)
if m:
    print("Found error block!")
    
    old_error_block = m.group(0)
    
    new_error_block = """} else {
                val isNotice = r.error?.contains("Notice", ignoreCase = true) == true || r.error?.contains("supported", ignoreCase = true) == true
                
                val bgColor = if (isNotice) Color(0xFF3B82F6) else Color(0xFFEF4444) // Blue or Red
                val iconColor = if (isNotice) Color(0xFF60A5FA) else Color(0xFFEF4444)
                val titleText = if (isNotice) "Notice" else "Extraction Failed"
                val errorIcon = if (isNotice) Icons.Filled.Info else Icons.Filled.ErrorOutline
                
                Box(
                    modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(16.dp)).background(bgColor.copy(alpha = 0.1f)).border(1.dp, bgColor.copy(alpha = 0.3f), RoundedCornerShape(16.dp)).padding(16.dp)
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.fillMaxWidth()) {
                        Icon(errorIcon, null, tint = iconColor, modifier = Modifier.size(48.dp))
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(titleText, color = iconColor, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(r.error ?: "An unknown error occurred", color = textColor, textAlign = TextAlign.Center, style = MaterialTheme.typography.bodyMedium)
                    }
                }
            }"""
    code = code.replace(old_error_block, new_error_block)
    print("Replaced error block")

with open('app/src/main/java/com/auradownloader/app/MainActivity.kt', 'w') as f:
    f.write(code)
