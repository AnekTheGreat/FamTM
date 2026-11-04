package com.familytree.app

import android.annotation.SuppressLint
import android.Manifest
import android.app.Activity
import android.app.AlertDialog
import android.content.ClipData
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.ImageDecoder
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.provider.MediaStore
import android.util.Base64
import android.view.ViewGroup
import android.webkit.JavascriptInterface
import android.webkit.JsResult
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.FrameLayout
import android.widget.Toast
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.FileProvider
import androidx.core.view.ViewCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.webkit.WebViewAssetLoader
import java.io.File
import java.io.FileOutputStream
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest

private const val HOST = "https://appassets.androidplatform.net"
// Where the page comes from: the newest release's tag, read from the repository's own feed, and then
// that tag's index.html. The screen on a phone is therefore always the page a release shipped - never
// whatever the branch says today - and the APK follows the same rule, changing only when this file does.
private const val REPO = "AnekTheGreat/FamTM"

class MainActivity : AppCompatActivity() {
    private lateinit var web: WebView
    private var data: ByteArray? = null
    private var chooser: ValueCallback<Array<Uri>>? = null
    private val otaDir by lazy { File(filesDir, "ota").apply { mkdirs() } }
    private val otaFile by lazy { File(otaDir, "index.html") }
    private var shot: File? = null                                            // a picture just taken
    private val shotDir by lazy { File(filesDir, "shots").apply { mkdirs() } }
    private var pickImage = false                                             // the open chooser is asking for a picture
    private val main = Handler(Looper.getMainLooper())
    private var drawn: Runnable? = null                                       // a stored page that never draws is put back

    private fun saver(mime: String) = registerForActivityResult(ActivityResultContracts.CreateDocument(mime)) { u ->
        if (u != null) try {
            contentResolver.openOutputStream(u)?.use { it.write(data ?: ByteArray(0)) }; toast("Saved")
        } catch (e: Exception) { toast("Save failed") }
    }
    private val pdfL = saver("application/pdf")
    private val jsonL = saver("application/json")
    // Android 13 and later asks the person before a notification may be shown, so the ask happens when
    // birthday reminders are turned on — never at install time.
    private val notifL = registerForActivityResult(ActivityResultContracts.RequestPermission()) {}
    private val pickL = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { r ->
        val u = r.data?.data ?: r.data?.clipData?.getItemAt(0)?.uri
        val cb = chooser
        chooser = null
        if (r.resultCode != Activity.RESULT_OK || u == null) cb?.onReceiveValue(null)
        else {
            // A picture is turned into a JPEG the page can always open, so a HEIC or HEIF photo — a format
            // no WebView will draw — becomes a photo like any other. Anything this phone cannot decode, or
            // a file that is not a picture at all, is handed over untouched: the page's own reader then has
            // its chance, and says so if it cannot open it either. A restore is never touched.
            val jpg = if (pickImage) toJpeg(u) else null
            if (jpg != null) {
                cb?.onReceiveValue(null)
                photoBack(jpg)
            } else cb?.onReceiveValue(arrayOf(u))
        }
    }

    // The camera answers here, and the picture is already on disk — so the page is only told where to
    // fetch it from, which is the same address the page itself is served from. That is why the page can
    // read it: nothing has to be pushed through JavaScript as one enormous string.
    private val shotL = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { r ->
        val f = shot
        shot = null
        if (r.resultCode == Activity.RESULT_OK && f != null && f.length() > 0) photoBack(f)
        else f?.delete()
    }

    // The page is only ever told where the picture is, which is an address it is allowed to read, so a
    // picture never has to be pushed through JavaScript as one enormous string.
    private fun photoBack(f: File) =
        web.evaluateJavascript("window.__photo&&window.__photo('$HOST/photos/${f.name}')", null)

    // Whatever the phone can read, as a JPEG in the app's own folder: HEIC/HEIF (iPhone and modern
    // Android photos), AVIF, WebP, PNG, GIF, BMP and a JPEG alike. The page keeps a 240px picture, so the
    // photo is scaled down while it is decoded rather than after — a 12 MP photo would otherwise need
    // ~48 MB for a picture that is about to be thrown away. Null when this phone cannot decode the file,
    // and nothing is left behind when that happens.
    private fun toJpeg(u: Uri): File? {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.P) return null   // no HEIF decoder before Android 9
        return try {
            val src = ImageDecoder.createSource(contentResolver, u)
            val bmp: Bitmap = ImageDecoder.decodeBitmap(src) { d, info, _ ->
                val long = maxOf(info.size.width, info.size.height)
                if (long > 1024) {
                    val s = 1024f / long
                    d.setTargetSize(Math.round(info.size.width * s).coerceAtLeast(1),
                                    Math.round(info.size.height * s).coerceAtLeast(1))   // never a zero side
                }
                d.allocator = ImageDecoder.ALLOCATOR_SOFTWARE     // a hardware bitmap cannot be drawn or scaled
            }
            shotDir.listFiles { f -> f.name.startsWith("pick-") }?.forEach { it.delete() }   // only the newest is kept
            val f = File(shotDir, "pick-${System.currentTimeMillis()}.jpg")
            FileOutputStream(f).use { bmp.compress(Bitmap.CompressFormat.JPEG, 90, it) }
            bmp.recycle()
            if (f.length() > 0) f else { f.delete(); null }
        } catch (e: Throwable) { null }
    }

    private fun toast(s: String) = Toast.makeText(this, s, Toast.LENGTH_LONG).show()

    /** A colour the theme already carries, so the strip behind the bars matches the app either way. */
    private fun themeColor(attr: Int): Int {
        val a = obtainStyledAttributes(intArrayOf(attr))
        val c = a.getColor(0, 0xFF000000.toInt())
        a.recycle()
        return c
    }

    inner class Bridge {
        @JavascriptInterface
        fun save(name: String, b64: String) {
            data = Base64.decode(b64, Base64.DEFAULT)
            runOnUiThread { if (name.endsWith(".pdf")) pdfL.launch(name) else jsonL.launch(name) }
        }

        // the "Take photo" button in the page: open the camera and put the picture into the form
        @JavascriptInterface
        fun photo() { runOnUiThread { takePhoto() } }

        // asked by the page before it blames a picture: this version reads HEIC/HEIF and every other
        // format the phone can decode itself, so a picture that still cannot be opened is the file's fault
        // and not an old app's — the page says which, instead of telling someone to update for nothing
        @JavascriptInterface
        fun pics() = 2

        // the Birthdays page hands over the birthdays to remind about — the day and month of each
        // living person — and whether reminders are wanted at all
        @JavascriptInterface
        fun bdays(on: Boolean, json: String) {
            Birthdays.save(this@MainActivity, json)
            runOnUiThread {
                Birthdays.set(this@MainActivity, on)
                if (on && Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
                    checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED)
                    notifL.launch(Manifest.permission.POST_NOTIFICATIONS)
            }
        }

        // the ⟳ button in the app: check for an OTA update and reload straight away
        @JavascriptInterface
        fun refresh() {
            Thread {
                val r = otaUpdate()
                runOnUiThread {
                    toast(when (r) {
                        "updated" -> "Update applied"
                        "current" -> "Already up to date"
                        "bad" -> "Update file looked wrong – kept this version"
                        else -> "Couldn't reach the update server"
                    })
                    web.loadUrl(if (otaFile.exists()) "$HOST/ota/index.html" else "$HOST/assets/index.html")
                }
            }.start()
        }

        // the ♥ button the app puts beside ⟳: the five amounts SideCut offers, each a Stripe page
        @JavascriptInterface
        fun tip() { runOnUiThread { support() } }
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // a newly installed APK always wins over an older OTA copy
        val installed = packageManager.getPackageInfo(packageName, 0).lastUpdateTime
        if (otaFile.exists() && otaFile.lastModified() < installed) otaFile.delete()
        shotDir.listFiles()?.forEach { it.delete() }        // a picture from an earlier run is never needed
        if (Birthdays.isOn(this)) Birthdays.schedule(this)   // reminders survive a restart; make sure the daily check is there
        val loader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .addPathHandler("/ota/", WebViewAssetLoader.InternalStoragePathHandler(this, otaDir))
            .addPathHandler("/photos/", WebViewAssetLoader.InternalStoragePathHandler(this, shotDir))
            .build()
        web = WebView(this)
        web.settings.javaScriptEnabled = true
        web.settings.domStorageEnabled = true
        web.settings.allowFileAccess = false
        web.addJavascriptInterface(Bridge(), "Android")
        web.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(v: WebView?, r: WebResourceRequest?): WebResourceResponse? =
                r?.let { loader.shouldInterceptRequest(it.url) }

            // Every copy of the page is served the same way — bundled, or fetched over OTA — so the tip
            // button is put into the top bar here, once per load, rather than written into index.html
            // where an older OTA copy would not have it.
            override fun onPageFinished(v: WebView?, url: String?) {
                injectTip()
                if (url != null && url.contains("/ota/")) watchDraw(v)
                else drawn?.let { main.removeCallbacks(it) }
            }

            override fun onReceivedError(v: WebView?, r: WebResourceRequest?, e: WebResourceError?) {
                if (r != null && r.isForMainFrame && r.url.path?.startsWith("/ota/") == true) {
                    otaFile.delete(); v?.loadUrl("$HOST/assets/index.html")   // bad OTA file: fall back to bundled
                }
            }
        }
        web.webChromeClient = object : WebChromeClient() {
            override fun onJsConfirm(v: WebView?, url: String?, msg: String?, r: JsResult?): Boolean {
                AlertDialog.Builder(this@MainActivity).setMessage(msg)
                    .setPositiveButton("OK") { _, _ -> r?.confirm() }
                    .setNegativeButton("Cancel") { _, _ -> r?.cancel() }
                    .setOnCancelListener { r?.cancel() }.show()
                return true
            }

            override fun onJsAlert(v: WebView?, url: String?, msg: String?, r: JsResult?): Boolean {
                AlertDialog.Builder(this@MainActivity).setMessage(msg)
                    .setPositiveButton("OK") { _, _ -> r?.confirm() }
                    .setOnCancelListener { r?.confirm() }.show()
                return true
            }

            // A picture does not only live in Files, so a page asking for an image is offered the phone's own
            // pictures as well: the system photo picker on Android 13+, and the gallery app on older phones.
            // Files stays on the sheet, so nothing that worked before is lost, and it is the fallback when a
            // phone has neither. The URI that comes back is read straight away (the picker grants that) and
            // handed to the page, which shrinks it to a 240px picture as before.
            override fun onShowFileChooser(w: WebView?, cb: ValueCallback<Array<Uri>>?, p: FileChooserParams?): Boolean {
                chooser?.onReceiveValue(null); chooser = cb
                val types = p?.acceptTypes?.toList() ?: emptyList()
                val wantsImages = types.isEmpty() || types.any { it.startsWith("image/") }
                pickImage = wantsImages
                // Files is offered every file when a picture is wanted, not only the ones it already calls
                // an image: a HEIC from a cloud app can arrive with no image type at all, and an image-only
                // list would then quietly leave it out. A file that is not a picture is refused on the way
                // back, with a message, so nothing is lost and nothing is opened as a photo by accident.
                val files = if (wantsImages) Intent(Intent.ACTION_GET_CONTENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = "*/*"
                } else p?.createIntent() ?: Intent(Intent.ACTION_GET_CONTENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = "*/*"
                }
                val sheet = mutableListOf<Intent>()
                if (wantsImages) {
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU)
                        sheet += Intent(MediaStore.ACTION_PICK_IMAGES).setType("image/*")
                    sheet += Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI).setType("image/*")
                }
                sheet += files
                val first = sheet.removeAt(0)
                // one choice (a restore, say, which only Files can serve): open it directly, no sheet in the way
                val ask = if (sheet.isEmpty()) first else
                    Intent(Intent.ACTION_CHOOSER)
                        .putExtra(Intent.EXTRA_INTENT, first)
                        .putExtra(Intent.EXTRA_INITIAL_INTENTS, sheet.toTypedArray())
                try { pickL.launch(ask) }
                catch (e: Exception) {                   // no gallery and no picker on this phone: Files alone
                    try { pickL.launch(files) }
                    catch (e2: Exception) { chooser?.onReceiveValue(null); chooser = null }
                }
                return true
            }
        }
        // From API 35 Android draws every app edge to edge whether it asks to or not, and from API 36
        // there is no opting out (the attribute is ignored), so the page would be drawn under the clock
        // and the gesture bar. The page fills the window inside a frame that is padded by the status bar,
        // the navigation bar and the keyboard, so its own top bar is not behind the status bar and a field
        // is never left under the keyboard when one is open.
        WindowCompat.setDecorFitsSystemWindows(window, false)
        val frame = FrameLayout(this).apply {
            // The strips the padding leaves behind the bars are painted with the theme's own background,
            // so light and dark mode both keep their edges instead of showing a wrong-coloured band.
            setBackgroundColor(themeColor(android.R.attr.colorBackground))
        }
        frame.addView(web, ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT)
        ViewCompat.setOnApplyWindowInsetsListener(frame) { v, insets ->
            val bars = insets.getInsets(
                WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.ime()
            )
            v.setPadding(bars.left, bars.top, bars.right, bars.bottom)
            WindowInsetsCompat.CONSUMED
        }
        setContentView(frame)
        web.loadUrl(if (otaFile.exists()) "$HOST/ota/index.html" else "$HOST/assets/index.html")
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                web.evaluateJavascript(
                    "(function(){var a=document.querySelectorAll('dialog[open]');if(a.length){a[a.length-1].close();return 1}return 0})()"
                ) { if (it != "1") finish() }
            }
        })
        checkOta()
    }

    /**
     * Add the tip button to the page's own top bar, right before ⟳, borrowing its class so it looks
     * like it was always there. It only reports a tap - the amounts are shown by the app, so an old
     * page and a new one behave identically.
     */
    private fun injectTip() {
        web.evaluateJavascript(
            """
            (function(){
              if (document.getElementById('tp')) return;
              var r = document.getElementById('rf');
              if (!r || !r.parentNode) return;
              var b = document.createElement('button');
              b.id = 'tp';
              b.className = r.className;
              b.setAttribute('aria-label', 'Support Family Tree');
              b.type = 'button';
              b.textContent = '\u2665';
              b.style.color = '#c0392b';
              b.addEventListener('click', function(){ if (window.Android && Android.tip) Android.tip(); });
              r.parentNode.insertBefore(b, r);
            })()
            """.trimIndent(), null
        )
    }

    /** The tip jar: the five amounts SideCut offers, each opening Stripe's own page. */
    private fun support() {
        val labels = Support.LINKS.map { Support.label(it.first) }.toTypedArray()
        AlertDialog.Builder(this)
            .setTitle("Support Family Tree")
            .setItems(labels) { _, which -> Support.open(this, Support.LINKS[which].second) }
            .setNegativeButton("Not now", null)
            .show()
    }

    // Take photo: the camera app is handed a one-off writable URI pointing into the app's own files, so
    // no camera permission and no storage permission is asked for, and the picture is never left lying
    // in the phone's photos. Only the newest one is kept.
    private fun takePhoto() {
        try {
            shotDir.listFiles()?.forEach { it.delete() }
            val f = File(shotDir, "shot-${System.currentTimeMillis()}.jpg")
            val u = FileProvider.getUriForFile(this, "$packageName.fileprovider", f)
            shot = f
            shotL.launch(Intent(MediaStore.ACTION_IMAGE_CAPTURE).apply {
                putExtra(MediaStore.EXTRA_OUTPUT, u)
                addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION or Intent.FLAG_GRANT_READ_URI_PERMISSION)
                clipData = ClipData.newRawUri("photo", u)
            })
        } catch (e: Exception) {                 // no camera app on this phone, or nowhere to write
            shot = null
            toast("No camera on this phone")
        }
    }

    private fun sha(b: ByteArray) = MessageDigest.getInstance("SHA-256").digest(b).joinToString("") { "%02x".format(it) }

    /** A request GitHub answers: no User-Agent is a 403, and the cache-buster keeps a stale copy out. */
    private fun open(u: String): HttpURLConnection =
        (URL(u).openConnection() as HttpURLConnection).apply {
            setRequestProperty("User-Agent", "FamTM")
            connectTimeout = 8000
            readTimeout = 8000
            instanceFollowRedirects = true
        }

    /**
     * The newest release's tag, from the repository's own feed rather than the API: the feed has no
     * anonymous limit and no key, and each entry names the tag the page is pinned to. Null when the
     * feed cannot be read, which is the phone being offline rather than anything being wrong.
     */
    private fun newestTag(): String? = try {
        val c = open("https://github.com/$REPO/releases.atom?t=${System.currentTimeMillis()}")
        if (c.responseCode != 200) null
        else {
            val xml = c.inputStream.bufferedReader().use { it.readText() }
            Regex("""/releases/tag/([^"<]+)""").find(xml)?.groupValues?.get(1)
        }
    } catch (e: Exception) { null }

    // "updated" / "current" / "bad" / "offline"
    private fun otaUpdate(): String = try {
        val tag = newestTag()
        if (tag == null) "offline"
        else {
            val c = open("https://raw.githubusercontent.com/$REPO/$tag/app/src/main/assets/index.html?t=${System.currentTimeMillis()}")
            if (c.responseCode != 200) "offline"
            else {
                val bytes = c.inputStream.use { it.readBytes() }
                if (bytes.size < 2000 || !String(bytes).contains("familytree.v1")) "bad"
                else {
                    val current = if (otaFile.exists()) otaFile.readBytes() else assets.open("index.html").use { it.readBytes() }
                    if (sha(bytes) == sha(current)) "current"
                    else {
                        val tmp = File(otaDir, "index.html.tmp")
                        tmp.writeBytes(bytes)
                        // A rename is the only way the file appears, so a half-written page is never served.
                        if (tmp.renameTo(otaFile)) "updated" else { tmp.delete(); "bad" }
                    }
                }
            }
        }
    } catch (e: Exception) { "offline" }

    /**
     * A stored page that loads but draws nothing is the one failure an over-the-air copy can hide, and
     * it is the one that matters: a family tree that opens blank. Nine seconds after a stored page says
     * it loaded, its own top bar has to be there and the page has to hold text; when it is not, the copy
     * is deleted and the bundled page is drawn instead, so the worst a bad update can do is put back
     * the screen the APK shipped with.
     */
    private fun watchDraw(v: WebView?) {
        drawn?.let { main.removeCallbacks(it) }
        val check = Runnable {
            v?.evaluateJavascript(
                "(document.getElementById('top')&&document.body&&document.body.innerText.length>40)?'y':'n'"
            ) { r ->
                if (r == null || !r.contains("y")) {
                    otaFile.delete()
                    v.loadUrl("$HOST/assets/index.html")
                    toast("FamTM went back to the screen it ships with")
                }
            }
        }
        drawn = check
        main.postDelayed(check, 9000L)
    }

    private fun checkOta() {
        Thread { if (otaUpdate() == "updated") runOnUiThread { toast("Update ready – tap ⟳ to apply") } }.start()
    }
}
