// These three numbers move together: API 36 is what Play has required of every upload since
// 31 August 2026, AGP 8.10.1 is the oldest plugin that can compile against it, and that plugin wants
// Gradle 8.11.1 (pinned in CI, which the wrapper would otherwise have to carry). Kotlin follows to
// 2.0.21; the app has no Compose and nothing here is sensitive to the Kotlin version.
plugins {
    id("com.android.application") version "8.10.1" apply false
    id("org.jetbrains.kotlin.android") version "2.0.21" apply false
}
