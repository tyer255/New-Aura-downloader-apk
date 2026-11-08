package com.auradownloader.app

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.content.Intent
import android.view.View
import android.widget.RemoteViews

class AuraAppWidgetProvider : AppWidgetProvider() {
    override fun onUpdate(context: Context, appWidgetManager: AppWidgetManager, appWidgetIds: IntArray) {
        for (appWidgetId in appWidgetIds) {
            updateAppWidget(context, appWidgetManager, appWidgetId, STATE_DEFAULT)
        }
    }

    override fun onReceive(context: Context, intent: Intent) {
        super.onReceive(context, intent)
    }

    companion object {
        const val ACTION_WIDGET_PASTE = "com.auradownloader.app.ACTION_WIDGET_PASTE"
        const val ACTION_WIDGET_DOWNLOAD = "com.auradownloader.app.ACTION_WIDGET_DOWNLOAD"
        const val STATE_DEFAULT = 0
        const val STATE_LOADING = 1
        const val STATE_QUALITIES = 2

        fun updateAppWidget(context: Context, appWidgetManager: AppWidgetManager, appWidgetId: Int, state: Int) {
            val views = RemoteViews(context.packageName, R.layout.widget_aura)

            when (state) {
                STATE_DEFAULT -> {
                    views.setViewVisibility(R.id.widget_state_default, View.VISIBLE)
                    views.setViewVisibility(R.id.widget_state_loading, View.GONE)
                    views.setViewVisibility(R.id.widget_state_qualities, View.GONE)
                }
                STATE_LOADING -> {
                    views.setViewVisibility(R.id.widget_state_default, View.GONE)
                    views.setViewVisibility(R.id.widget_state_loading, View.VISIBLE)
                    views.setViewVisibility(R.id.widget_state_qualities, View.GONE)
                }
            }

            // Set up paste intent
            val pasteIntent = Intent(context, WidgetActionActivity::class.java).apply {
                action = ACTION_WIDGET_PASTE
                putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, appWidgetId)
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            }
            val pastePendingIntent = PendingIntent.getActivity(
                context, appWidgetId, pasteIntent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )

            views.setOnClickPendingIntent(R.id.btn_widget_paste_chip, pastePendingIntent)
            views.setOnClickPendingIntent(R.id.btn_widget_paste_bar, pastePendingIntent)
            views.setOnClickPendingIntent(R.id.btn_widget_download, pastePendingIntent) // Download before paste acts as paste

            // Launch app when logo clicked
            val openAppIntent = Intent(context, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            }
            val openAppPendingIntent = PendingIntent.getActivity(
                context, appWidgetId, openAppIntent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
            views.setOnClickPendingIntent(R.id.widget_app_logo, openAppPendingIntent)

            appWidgetManager.updateAppWidget(appWidgetId, views)
        }

        fun updateAppWidgetQualities(context: Context, appWidgetManager: AppWidgetManager, appWidgetId: Int, result: DownloadResult) {
            val views = RemoteViews(context.packageName, R.layout.widget_aura)
            views.setViewVisibility(R.id.widget_state_default, View.GONE)
            views.setViewVisibility(R.id.widget_state_loading, View.GONE)
            views.setViewVisibility(R.id.widget_state_qualities, View.VISIBLE)

            // Hide all buttons first
            views.setViewVisibility(R.id.widget_btn_q1, View.GONE)
            views.setViewVisibility(R.id.widget_btn_q2, View.GONE)
            views.setViewVisibility(R.id.widget_btn_q3, View.GONE)

            val buttons = listOf(R.id.widget_btn_q1, R.id.widget_btn_q2, R.id.widget_btn_q3)
            
            for (i in 0 until minOf(result.qualities.size, 3)) {
                val q = result.qualities[i]
                val btnId = buttons[i]
                views.setViewVisibility(btnId, View.VISIBLE)
                views.setTextViewText(btnId, q.label)
                
                val downloadIntent = Intent(context, WidgetActionActivity::class.java).apply {
                    action = ACTION_WIDGET_DOWNLOAD
                    putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, appWidgetId)
                    putExtra("url", q.url)
                    putExtra("label", q.label)
                    putExtra("title", result.title)
                    putExtra("thumbnailUrl", result.thumbnailUrl)
                    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
                }
                val downloadPendingIntent = PendingIntent.getActivity(
                    context, appWidgetId * 10 + i, downloadIntent,
                    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
                )
                views.setOnClickPendingIntent(btnId, downloadPendingIntent)
            }

            appWidgetManager.updateAppWidget(appWidgetId, views)
        }
    }
}
