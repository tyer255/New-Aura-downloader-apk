import re

with open('app/src/main/java/com/example/MainActivity.kt', 'r') as f:
    content = f.read()

old_enum = """enum class Platform(
    val displayName: String,
    val brandColor: Color,
    val startColorDark: Color,
    val endColorDark: Color,
    val startColorLight: Color,
    val endColorLight: Color,
    val iconResId: Int
) {
    YOUTUBE("YouTube", Color(0xFFFF0000), Color(0xFF8B6464), Color(0xFF4A3434), Color(0xFFFEE2E2), Color(0xFFFFF1F2), R.drawable.ic_youtube),
    INSTAGRAM("Instagram", Color(0xFFE4405F), Color(0xFF836A87), Color(0xFF483A4C), Color(0xFFFCE7F3), Color(0xFFFDF2F8), R.drawable.ic_instagram),
    TIKTOK("TikTok", Color(0xFF00F2FE), Color(0xFF728489), Color(0xFF445155), Color(0xFFCFFAFE), Color(0xFFF0FDFA), R.drawable.ic_tiktok),
    FACEBOOK("Facebook", Color(0xFF1877F2), Color(0xFF656C80), Color(0xFF3C404D), Color(0xFFDBEAFE), Color(0xFFEFF6FF), R.drawable.ic_facebook),
    REDDIT("Reddit", Color(0xFFFF4500), Color(0xFF856C64), Color(0xFF4B3C37), Color(0xFFFFEDD5), Color(0xFFFFF7ED), R.drawable.ic_reddit),
    PINTEREST("Pinterest", Color(0xFFE60023), Color(0xFF8C646A), Color(0xFF4D3539), Color(0xFFFFE4E6), Color(0xFFFFF1F2), R.drawable.ic_pinterest),
    X("X (Twitter)", Color(0xFF1DA1F2), Color(0xFF76787B), Color(0xFF444547), Color(0xFFF3F4F6), Color(0xFFF9FAFB), R.drawable.ic_x),
    LINKEDIN("LinkedIn", Color(0xFF0A66C2), Color(0xFF64748B), Color(0xFF334155), Color(0xFFE0F2FE), Color(0xFFF0F9FF), R.drawable.ic_linkedin)
}"""

new_enum = """enum class Platform(
    val displayName: String,
    val brandColor: Color,
    val startColorDark: Color,
    val endColorDark: Color,
    val startColorLight: Color,
    val endColorLight: Color,
    val iconResId: Int
) {
    YOUTUBE("YouTube", Color(0xFFFF0000), Color(0xFF8B6464), Color(0xFF4A3434), Color(0xFFFEE2E2), Color(0xFFFFF1F2), R.drawable.ic_youtube),
    INSTAGRAM("Instagram", Color(0xFFE4405F), Color(0xFF836A87), Color(0xFF483A4C), Color(0xFFFCE7F3), Color(0xFFFDF2F8), R.drawable.ic_instagram),
    TIKTOK("TikTok", Color(0xFF00F2FE), Color(0xFF728489), Color(0xFF445155), Color(0xFFCFFAFE), Color(0xFFF0FDFA), R.drawable.ic_tiktok),
    FACEBOOK("Facebook", Color(0xFF1877F2), Color(0xFF656C80), Color(0xFF3C404D), Color(0xFFDBEAFE), Color(0xFFEFF6FF), R.drawable.ic_facebook),
    REDDIT("Reddit", Color(0xFFFF4500), Color(0xFF856C64), Color(0xFF4B3C37), Color(0xFFFFEDD5), Color(0xFFFFF7ED), R.drawable.ic_reddit),
    PINTEREST("Pinterest", Color(0xFFE60023), Color(0xFF8C646A), Color(0xFF4D3539), Color(0xFFFFE4E6), Color(0xFFFFF1F2), R.drawable.ic_pinterest),
    X("X (Twitter)", Color(0xFF1DA1F2), Color(0xFF76787B), Color(0xFF444547), Color(0xFFF3F4F6), Color(0xFFF9FAFB), R.drawable.ic_x),
    LINKEDIN("LinkedIn", Color(0xFF0A66C2), Color(0xFF64748B), Color(0xFF334155), Color(0xFFE0F2FE), Color(0xFFF0F9FF), R.drawable.ic_linkedin),
    SNAPCHAT("Snapchat", Color(0xFFFFFC00), Color(0xFF8B8A64), Color(0xFF4A4934), Color(0xFFFEFDE2), Color(0xFFFFFDF1), R.drawable.ic_snapchat),
    SPOTIFY("Spotify", Color(0xFF1DB954), Color(0xFF648B70), Color(0xFF344A3A), Color(0xFFE2FEEA), Color(0xFFF1FFF5), R.drawable.ic_spotify),
    THREADS("Threads", Color(0xFF000000), Color(0xFF777777), Color(0xFF444444), Color(0xFFF3F4F6), Color(0xFFF9FAFB), R.drawable.ic_threads)
}"""

if old_enum in content:
    content = content.replace(old_enum, new_enum)
    with open('app/src/main/java/com/example/MainActivity.kt', 'w') as f:
        f.write(content)
    print("Enum patched successfully.")
else:
    print("Enum not found.")

