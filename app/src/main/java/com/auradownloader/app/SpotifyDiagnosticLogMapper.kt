package com.auradownloader.app

import android.util.Log
import org.json.JSONObject

/**
 * Diagnostic log mapper for the Spotify network layer.
 * Intercepts Spotify metadata responses, inspects for the presence/absence of 'preview_url' / 'audioPreview.url',
 * logs comprehensive diagnostics, and explicitly differentiates missing preview sources from general extraction failures.
 */
object SpotifyDiagnosticLogMapper {
    private const val TAG = "SpotifyDiagnostic"

    data class DiagnosticResult(
        val trackId: String,
        val trackTitle: String,
        val artistName: String,
        val hasPreviewUrl: Boolean,
        val previewUrl: String?,
        val source: String,
        val isReachable: Boolean?,
        val resolvedErrorMessage: String?
    )

    /**
     * Intercepts and logs Spotify metadata diagnostics.
     * If the preview_url field is missing, returns a specific error message stating that no preview source was found by the API.
     */
    fun logAndMapMetadata(
        trackId: String,
        title: String,
        artist: String,
        embedHtmlFound: Boolean,
        entityJsonParsed: Boolean,
        spotifyPreviewUrl: String?,
        backendAudioUrl: String?,
        isReachable: Boolean?
    ): DiagnosticResult {
        val hasSpotifyEmbedPreview = !spotifyPreviewUrl.isNullOrBlank()
        val hasBackendPreview = !backendAudioUrl.isNullOrBlank()
        val chosenPreviewUrl = if (hasSpotifyEmbedPreview) spotifyPreviewUrl else backendAudioUrl
        val hasAnyPreview = !chosenPreviewUrl.isNullOrBlank()

        val source = when {
            hasSpotifyEmbedPreview -> "Spotify Embed API (audioPreview.url)"
            hasBackendPreview -> "Backend Direct Audio Proxy"
            else -> "None"
        }

        Log.i(TAG, "================ [SPOTIFY DIAGNOSTIC LOG MAPPER] ================")
        Log.i(TAG, "Track ID: $trackId")
        Log.i(TAG, "Track Title: '$title' | Artist: '$artist'")
        Log.i(TAG, "Embed HTML Available: $embedHtmlFound | Entity JSON Parsed: $entityJsonParsed")
        Log.i(TAG, "Spotify 'preview_url' / 'audioPreview' field presence: ${if (hasSpotifyEmbedPreview) "PRESENT" else "ABSENT"}")
        if (hasSpotifyEmbedPreview) {
            Log.i(TAG, "Extracted preview_url: $spotifyPreviewUrl")
        } else {
            Log.w(TAG, "WARNING: 'preview_url' field is missing from the Spotify API / Embed response for track '$title' (ID: $trackId)")
        }
        if (hasBackendPreview) {
            Log.i(TAG, "Backend audio source: $backendAudioUrl")
        }
        Log.i(TAG, "Resolved Audio Source: $source")
        Log.i(TAG, "Audio Stream Reachable / Verified: ${isReachable ?: "Not Checked"}")

        val resolvedErrorMsg: String? = when {
            !hasAnyPreview -> {
                Log.w(TAG, "MAPPED ERROR: No preview source found by the Spotify API for track ID $trackId.")
                "No audio preview source was found by the Spotify API for this track."
            }
            isReachable == false -> {
                Log.w(TAG, "MAPPED ERROR: Preview URL was returned by Spotify API but failed verification/reachability.")
                "The audio preview source returned by Spotify is inaccessible or expired."
            }
            else -> {
                Log.i(TAG, "DIAGNOSTIC STATUS: Audio preview successfully validated for track '$title'.")
                null
            }
        }
        Log.i(TAG, "=================================================================")

        return DiagnosticResult(
            trackId = trackId,
            trackTitle = title,
            artistName = artist,
            hasPreviewUrl = hasAnyPreview,
            previewUrl = chosenPreviewUrl,
            source = source,
            isReachable = isReachable,
            resolvedErrorMessage = resolvedErrorMsg
        )
    }
}
