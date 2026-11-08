sed -i '/lottieCompose/d' gradle/libs.versions.toml
sed -i '/lottie-compose/d' gradle/libs.versions.toml

sed -i '/\[versions\]/a\
lottieCompose = "6.4.0"' gradle/libs.versions.toml

sed -i '/\[libraries\]/a\
lottie-compose = { group = "com.airbnb.android", name = "lottie-compose", version.ref = "lottieCompose" }' gradle/libs.versions.toml
