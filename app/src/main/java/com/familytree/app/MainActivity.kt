package com.familytree.app

import android.annotation.SuppressLint
import android.app.Activity
import android.app.AlertDialog
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.MediaStore
import android.util.Base64
import android.webkit.JavascriptInterface
import android.webkit.JsResult
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.webkit.WebViewAssetLoader
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest

private const val HOST = "https://appassets.androidplatform.net"
// OTA source: push a new index.html here and installed apps pick it up on next launch
private const val OTA_URL = "https://raw.githubusercontent.com/AnekTheGreat/FamTM/main/app/src/main/assets/index.html"

class MainActivity : AppCompatActivity() {
    private lateinit var web: WebView
    private var data: ByteArray? = null
    private var chooser: ValueCallback<Array<Uri>>? = null
    private val otaDir by lazy { File(filesDir, "ota").apply { mkdirs() } }
    private val otaFile by lazy { File(otaDir, "index.html") }

    private fun saver(mime: String) = registerForActivityResult(ActivityResultContracts.CreateDocument(mime)) { u ->
        if (u != null) try {
            contentResolver.openOutputStream(u)?.use { it.write(data ?: ByteArray(0)) }; toast("Saved")
        } catch (e: Exception) { toast("Save failed") }
    }
    private val pdfL = saver("application/pdf")
    private val jsonL = saver("application/json")
    private val pickL = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { r ->
        val u = r.data?.data ?: r.data?.clipData?.getItemAt(0)?.uri
        chooser?.onReceiveValue(if (r.resultCode == Activity.RESULT_OK && u != null) arrayOf(u) else null)
        chooser = null
    }

    private fun toast(s: String) = Toast.makeText(this, s, Toast.LENGTH_LONG).show()

    inner class Bridge {
        @JavascriptInterface
        fun save(name: String, b64: String) {
            data = Base64.decode(b64, Base64.DEFAULT)
            runOnUiThread { if (name.endsWith(".pdf")) pdfL.launch(name) else jsonL.launch(name) }
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
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // a newly installed APK always wins over an older OTA copy
        val installed = packageManager.getPackageInfo(packageName, 0).lastUpdateTime
        if (otaFile.exists() && otaFile.lastModified() < installed) otaFile.delete()
        val loader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .addPathHandler("/ota/", WebViewAssetLoader.InternalStoragePathHandler(this, otaDir))
            .build()
        web = WebView(this)
        web.settings.javaScriptEnabled = true
        web.settings.domStorageEnabled = true
        web.settings.allowFileAccess = false
        web.addJavascriptInterface(Bridge(), "Android")
        web.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(v: WebView?, r: WebResourceRequest?): WebResourceResponse? =
                r?.let { loader.shouldInterceptRequest(it.url) }

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
                val files = p?.createIntent() ?: Intent(Intent.ACTION_GET_CONTENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = if (wantsImages) "image/*" else "*/*"
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
        setContentView(web)
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

    private fun sha(b: ByteArray) = MessageDigest.getInstance("SHA-256").digest(b).joinToString("") { "%02x".format(it) }

    // "updated" / "current" / "bad" / "offline"
    private fun otaUpdate(): String = try {
        val c = URL("$OTA_URL?t=${System.currentTimeMillis()}").openConnection() as HttpURLConnection
        c.connectTimeout = 8000; c.readTimeout = 8000
        if (c.responseCode != 200) "offline"
        else {
            val bytes = c.inputStream.use { it.readBytes() }
            if (bytes.size < 2000 || !String(bytes).contains("familytree.v1")) "bad"
            else {
                val current = if (otaFile.exists()) otaFile.readBytes() else assets.open("index.html").use { it.readBytes() }
                if (sha(bytes) == sha(current)) "current"
                else { val tmp = File(otaDir, "index.html.tmp"); tmp.writeBytes(bytes); tmp.renameTo(otaFile); "updated" }
            }
        }
    } catch (e: Exception) { "offline" }

    private fun checkOta() {
        Thread { if (otaUpdate() == "updated") runOnUiThread { toast("Update ready – tap ⟳ to apply") } }.start()
    }
}
