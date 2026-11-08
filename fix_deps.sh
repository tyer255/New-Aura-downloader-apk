sed -i '/lottie-compose = "6.3.0"/d' gradle/libs.versions.toml
sed -i '/lottie-compose = { group = "com.airbnb.android", name = "lottie-compose", version.ref = "lottie-compose" }/d' gradle/libs.versions.toml
