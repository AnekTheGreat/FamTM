package com.familytree.app

import android.annotation.SuppressLint
import android.app.AlertDialog
import android.net.Uri
import android.os.Bundle
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
    private val pickL = registerForActivityResult(ActivityResultContracts.GetContent()) { u ->
        chooser?.onReceiveValue(if (u == null) null else arrayOf(u)); chooser = null
    }

    private fun toast(s: String) = Toast.makeText(this, s, Toast.LENGTH_LONG).show()

    inner class Bridge {
        @JavascriptInterface
        fun save(name: String, b64: String) {
            data = Base64.decode(b64, Base64.DEFAULT)
            runOnUiThread { if (name.endsWith(".pdf")) pdfL.launch(name) else jsonL.launch(name) }
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

            override fun onShowFileChooser(w: WebView?, cb: ValueCallback<Array<Uri>>?, p: FileChooserParams?): Boolean {
                chooser?.onReceiveValue(null); chooser = cb; pickL.launch("*/*"); return true
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

    private fun checkOta() {
        Thread {
            try {
                val c = URL("$OTA_URL?t=${System.currentTimeMillis()}").openConnection() as HttpURLConnection
                c.connectTimeout = 8000; c.readTimeout = 8000
                if (c.responseCode != 200) return@Thread
                val bytes = c.inputStream.use { it.readBytes() }
                if (bytes.size < 2000 || !String(bytes).contains("familytree.v1")) return@Thread
                val current = if (otaFile.exists()) otaFile.readBytes() else assets.open("index.html").use { it.readBytes() }
                if (sha(bytes) == sha(current)) return@Thread
                val tmp = File(otaDir, "index.html.tmp")
                tmp.writeBytes(bytes); tmp.renameTo(otaFile)
                runOnUiThread { toast("Update downloaded – restart the app to apply") }
            } catch (e: Exception) { }
        }.start()
    }
}
