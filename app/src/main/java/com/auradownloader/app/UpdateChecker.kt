package com.auradownloader.app

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.content.pm.PackageInfo
import android.util.Log
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.URL
import androidx.compose.ui.graphics.Color
import androidx.compose.material3.MaterialTheme

@Composable
fun UpdateChecker(context: Context, isDarkMode: Boolean) {
    var showDialog by remember { mutableStateOf(false) }
    var updateUrl by remember { mutableStateOf("${ApiSecurity.getBaseUrl()}/") }

    LaunchedEffect(Unit) {
        withContext(Dispatchers.IO) {
            try {
                // Fetch the version info from the website
                val urlObj = URL("${ApiSecurity.getBaseUrl()}/update.json?t=${System.currentTimeMillis()}")
                val connection = urlObj.openConnection() as java.net.HttpURLConnection
                connection.requestMethod = "GET"
                connection.connectTimeout = 5000
                connection.readTimeout = 5000
                connection.useCaches = false
                connection.setRequestProperty("Cache-Control", "no-cache")
                connection.setRequestProperty("User-Agent", "Mozilla/5.0 (Android) AuraDownloader")
                connection.setRequestProperty("X-Aura-Api-Key", ApiSecurity.API_KEY)

                if (connection.responseCode == java.net.HttpURLConnection.HTTP_OK) {
                    val jsonString = connection.inputStream.bufferedReader().use { it.readText() }
                    try {
                        val json = JSONObject(jsonString)
                        val remoteVersion = json.optInt("versionCode", 0)
                        val fetchedUrl = json.optString("updateUrl", "${ApiSecurity.getBaseUrl()}/")
                        
                        // Get current app version
                        val pInfo: PackageInfo = context.packageManager.getPackageInfo(context.packageName, 0)
                        val currentVersion = if (android.os.Build.VERSION.SDK_INT >= 28) {
                            pInfo.longVersionCode.toInt()
                        } else {
                            @Suppress("DEPRECATION")
                            pInfo.versionCode
                        }

                        Log.d("UpdateChecker", "Remote: $remoteVersion, Current: $currentVersion")

                        if (remoteVersion > currentVersion) {
                            withContext(Dispatchers.Main) {
                                updateUrl = fetchedUrl
                                showDialog = true
                            }
                        }
                    } catch (e: org.json.JSONException) {
                        Log.w("UpdateChecker", "update.json is not valid JSON. Server returned: ${jsonString.take(50)}")
                    }
                } else {
                    Log.w("UpdateChecker", "update.json not found on server. Response code: ${connection.responseCode}")
                }
            } catch (e: Exception) {
                Log.e("UpdateChecker", "Failed to check for updates", e)
            }
        }
    }

    if (showDialog) {
        val textColor = if (isDarkMode) Color.White else Color.Black
        val dialogBg = if (isDarkMode) Color(0xFF1E293B) else Color.White

        AlertDialog(
            containerColor = dialogBg,
            titleContentColor = textColor,
            textContentColor = textColor.copy(alpha = 0.8f),
            onDismissRequest = { showDialog = false },
            title = { Text("Update Available") },
            text = { Text("A new version of the app is available. Please update to continue.") },
            confirmButton = {
                TextButton(onClick = {
                    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(updateUrl))
                    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    context.startActivity(intent)
                    showDialog = false
                }) {
                    Text("Update Now", color = Color(0xFF38BDF8))
                }
            },
            dismissButton = {
                TextButton(onClick = {
                    showDialog = false
                }) {
                    Text("Later", color = textColor.copy(alpha = 0.5f))
                }
            }
        )
    }
}
