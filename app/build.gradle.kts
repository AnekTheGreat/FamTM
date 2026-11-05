plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

// Signing comes from the environment: the keystore is rebuilt from the KEYSTORE_BASE64 secret in
// CI and pointed at by SIGNING_STORE_FILE. Without it the debug build still works and the release
// build is simply unsigned. The locals are not named storePassword/keyAlias on purpose - inside
// signingConfigs those are the DSL's own properties.
val signingStorePath: String? = System.getenv("SIGNING_STORE_FILE")
val signingStorePass: String? = System.getenv("SIGNING_STORE_PASSWORD")
val signingAlias: String = System.getenv("SIGNING_KEY_ALIAS") ?: "famtm"

android {
    // The sources stay under com.familytree.app: that is the package the Kotlin files declare and
    // the one the manifest's ".MainActivity" resolves against, and it never leaves the build. The
    // name the phone and Play see is the applicationId below, and that one had to move: a package
    // name is unique per store, com.familytree.app is already someone else's listing, and a build
    // under it could never be uploaded.
    namespace = "com.familytree.app"
    // API 36 is not a preference: Play has refused an upload that targets less since 31 August 2026,
    // and AGP 8.10.1 is the oldest plugin that can compile against it.
    compileSdk = 36
    defaultConfig {
        applicationId = "com.FamTM.app"
        minSdk = 24
        targetSdk = 36
        // 1.4 (5) installs over 1.3 (4) as an ordinary update, so the family on the phone is kept.
        versionCode = (System.getenv("VERSION_CODE") ?: "5").toInt()
        versionName = System.getenv("VERSION_NAME") ?: "1.5.0"
    }

    signingConfigs {
        if (signingStorePath != null && signingStorePass != null) {
            create("release") {
                storeFile = file(signingStorePath)
                storeType = "PKCS12"
                storePassword = signingStorePass
                keyAlias = signingAlias
                keyPassword = signingStorePass
            }
        }
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.findByName("release")
        }
    }

    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = "17" }
}
dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("com.google.android.material:material:1.12.0")
    implementation("androidx.webkit:webkit:1.11.0")
    implementation("androidx.activity:activity-ktx:1.9.2")
    implementation("androidx.work:work-runtime-ktx:2.9.1")   // one quiet daily check for birthdays
}
