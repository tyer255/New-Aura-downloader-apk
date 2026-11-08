sed -i '/import androidx.compose.ui.zIndex.zIndex/d' app/src/main/java/com/auradownloader/app/MainActivity.kt
sed -i '/package com.auradownloader.app/a\
import androidx.compose.ui.zIndex.zIndex' app/src/main/java/com/auradownloader/app/MainActivity.kt
