sed -i '/\[versions\]/a\
lottieCompose = "6.4.0"' gradle/libs.versions.toml

sed -i '/\[libraries\]/a\
lottie-compose = { group = "com.airbnb.android", name = "lottie-compose", version.ref = "lottieCompose" }' gradle/libs.versions.toml

sed -i '/dependencies {/a\
    implementation(libs.lottie.compose)' app/build.gradle.kts
