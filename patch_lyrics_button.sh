cat << 'INNER_EOF' > patch_input.txt
                                Button(
                                    onClick = { showLyrics = r.lyrics },
                                        modifier = Modifier.fillMaxWidth().height(48.dp).neumorphic(isLightMode = !isDarkMode, cornerRadius = 12.dp, elevation = 4.dp),
                                    shape = RoundedCornerShape(12.dp),
                                        colors = ButtonDefaults.buttonColors(
                                            containerColor = if (isZip) Color(0xFF1DB954) else if (isDarkMode) Color.White.copy(0.1f) else Color.White,
                                            contentColor = if (isZip) Color.White else textColor
                                        ),
                                        contentColor = selectedPlatform.brandColor
                                    ),
                                    elevation = ButtonDefaults.buttonElevation(defaultElevation = 0.dp)
                                ) {
INNER_EOF
cat << 'INNER_EOF' > patch_output.txt
                                Button(
                                    onClick = { showLyrics = r.lyrics },
                                    modifier = Modifier.fillMaxWidth().height(48.dp).neumorphic(isLightMode = !isDarkMode, cornerRadius = 12.dp, elevation = 4.dp),
                                    shape = RoundedCornerShape(12.dp),
                                    colors = ButtonDefaults.buttonColors(
                                        containerColor = selectedPlatform.brandColor.copy(alpha = 0.15f),
                                        contentColor = selectedPlatform.brandColor
                                    ),
                                    elevation = ButtonDefaults.buttonElevation(defaultElevation = 0.dp)
                                ) {
INNER_EOF
perl -0777 -pi -e '
  $find = `cat patch_input.txt`;
  $replace = `cat patch_output.txt`;
  s/\Q$find\E/$replace/g;
' app/src/main/java/com/auradownloader/app/MainActivity.kt
