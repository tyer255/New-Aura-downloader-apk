echo 'lottie-compose = "6.3.0"' >> gradle/libs.versions.toml
sed -i 's/\[libraries\]/\[libraries\]\nlottie-compose = \{ group = "com.airbnb.android", name = "lottie-compose", version.ref = "lottie-compose" \}/g' gradle/libs.versions.toml
sed -i '/dependencies {/a\
    implementation(libs.lottie.compose)' app/build.gradle.kts
