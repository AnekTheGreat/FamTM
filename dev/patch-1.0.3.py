#!/usr/bin/env python3
"""Apply the v1.0.3 picture patch to a checkout of FamTM.

Run by .github/workflows/patch-1.0.3.yml on the runner, because the page itself is one
123 KB line and cannot be sent through the API. It applies the same edits that were made
and verified in the workspace, and it refuses to make a half-applied change: every
replacement has to land exactly once (or be visibly already applied).
"""
import io, json, sys

def read(p):
    return io.open(p, encoding='utf-8').read()

def write(p, s):
    io.open(p, 'w', encoding='utf-8').write(s)

def apply(path, subs):
    s = read(path)
    for i, (old, new) in enumerate(subs):
        n = s.count(old)
        if n == 1:
            s = s.replace(old, new)
        elif n == 0 and new in s:
            print('  %s [%d] already applied' % (path, i))
        else:
            sys.exit('FATAL: %s: replacement %d matched %d times' % (path, i, n))
    write(path, s)

PAGE = 'app/src/main/assets/index.html'

# ---- the page -------------------------------------------------------------------
page_subs = []

page_subs.append((
"const picBad=()=>say('That picture couldn\u2019t be opened \u2013 if it is a HEIC photo, pick it from Files as a JPEG instead');",
"// A picture is no longer the file the phone hands over, it is a picture the app has read: the app turns\n"
"// HEIC/HEIF (an iPhone's photo, a modern Android's) and every other format the phone can decode into a\n"
"// JPEG before the page sees it, so \"the browser cannot draw HEIC\" no longer means \"that picture cannot\n"
"// be opened\". What is left here is a browser, or an app older than this page.\n"
"const picCap=()=>{try{const A=window.Android;if(!A)return 'web';return typeof A.pics=='function'?'native':'old'}catch(e){return 'web'}};\n"
"const picBad=()=>say(picCap()=='old'?'Update the app first (\u27f3 in the top bar) \u2013 the version on this phone can\u2019t open that picture'"
":picCap()=='native'?'That picture couldn\u2019t be opened \u2013 try another copy of it'"
":'That picture couldn\u2019t be opened \u2013 try a JPEG or PNG copy of it');"))

page_subs.append((
"$('#fp').onclick=()=>$('#ff').click();",
"$('#fp').onclick=()=>{picFor=d=>{ph=d;pv()};$('#ff').click()};",))

page_subs.append((
"shrink(f,d=>{ph=d;pv()},()=>say('That picture couldn\u2019t be opened \u2013 if it is a HEIC photo, pick it from Files as a JPEG instead'))",
"shrink(f,d=>{ph=d;pv()},picBad)",))

page_subs.append(("const VER='1.0.2',UPD=", "const VER='1.0.3',UPD="))

note = {
 "v": "1.0.3", "d": "2026-10-26", "t": "A HEIC photo is a photo like any other",
 "x": [
  "A HEIC photo is a photo like any other. An iPhone\u2019s photo, or a modern Android\u2019s, is HEIC, and the page the app runs has no way to draw one \u2014 it was handed the file and gave up. The app now reads the picture itself, so a HEIC becomes the person\u2019s photo exactly as a JPEG does.",
  "Every other format too. Whatever this phone can decode is accepted \u2014 HEIC and HEIF, AVIF, WebP, PNG, GIF, BMP and JPEG \u2014 whether it comes from Photos, from the Gallery, from Files or from the camera, and the picture is still kept as the same small photo it always was.",
  "Files no longer hides a picture it does not recognise. When a picture is wanted, Files offers every file rather than only the ones it already calls an image: a HEIC from a cloud app can arrive with no image type at all, and an image-only list quietly left it out. A file that is not a picture is refused with a message when it comes back, so nothing is opened as a photo by accident.",
  "A picture that really cannot be opened says which kind of trouble it is. In a browser, or on a phone app older than this page, it says to update the app; on this version it says to try another copy, because the app has already done everything it can with it.",
  "This one needs the new APK. Version 1.3 (versionCode 4) \u2014 install it from Actions. The page itself still updates over the air as before, and a photo already saved is untouched."
 ]}

anchor = '<script id="upd" type="application/json">['
s = read(PAGE)
if '"v":"1.0.3"' in s:
    print('  %s [note] already applied' % PAGE)
else:
    if s.count(anchor) != 1:
        sys.exit('FATAL: the What\'s New anchor matched %d times' % s.count(anchor))
    s = s.replace(anchor, anchor + json.dumps(note, ensure_ascii=False, separators=(',', ':')) + ',')
    write(PAGE, s)
apply(PAGE, page_subs)

# the root copy is a mirror of the page and is kept identical to it
mirror = 'index.html'
if read(mirror) != read(PAGE):
    write(mirror, read(PAGE))
    print('  %s mirrored' % mirror)

# ---- the app --------------------------------------------------------------------
KT = 'app/src/main/java/com/familytree/app/MainActivity.kt'
kt_subs = [
("import android.content.pm.PackageManager\nimport android.net.Uri",
 "import android.content.pm.PackageManager\nimport android.graphics.Bitmap\nimport android.graphics.ImageDecoder\nimport android.net.Uri"),

("import java.io.File\nimport java.net.HttpURLConnection",
 "import java.io.File\nimport java.io.FileOutputStream\nimport java.net.HttpURLConnection"),

('    private val shotDir by lazy { File(filesDir, "shots").apply { mkdirs() } }',
 '    private val shotDir by lazy { File(filesDir, "shots").apply { mkdirs() } }\n'
 '    private var pickImage = false                                             // the open chooser is asking for a picture'),

("""    private val pickL = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { r ->
        val u = r.data?.data ?: r.data?.clipData?.getItemAt(0)?.uri
        chooser?.onReceiveValue(if (r.resultCode == Activity.RESULT_OK && u != null) arrayOf(u) else null)
        chooser = null
    }""",
"""    private val pickL = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { r ->
        val u = r.data?.data ?: r.data?.clipData?.getItemAt(0)?.uri
        val cb = chooser
        chooser = null
        if (r.resultCode != Activity.RESULT_OK || u == null) cb?.onReceiveValue(null)
        else {
            // A picture is turned into a JPEG the page can always open, so a HEIC or HEIF photo \u2014 a format
            // no WebView will draw \u2014 becomes a photo like any other. Anything this phone cannot decode, or
            // a file that is not a picture at all, is handed over untouched: the page's own reader then has
            // its chance, and says so if it cannot open it either. A restore is never touched.
            val jpg = if (pickImage) toJpeg(u) else null
            if (jpg != null) {
                cb?.onReceiveValue(null)
                photoBack(jpg)
            } else cb?.onReceiveValue(arrayOf(u))
        }
    }"""),

("""        if (r.resultCode == Activity.RESULT_OK && f != null && f.length() > 0)
            web.evaluateJavascript("window.__photo&&window.__photo('$HOST/photos/${f.name}')", null)
        else f?.delete()
    }
""",
"""        if (r.resultCode == Activity.RESULT_OK && f != null && f.length() > 0) photoBack(f)
        else f?.delete()
    }

    // The page is only ever told where the picture is, which is an address it is allowed to read, so a
    // picture never has to be pushed through JavaScript as one enormous string.
    private fun photoBack(f: File) =
        web.evaluateJavascript("window.__photo&&window.__photo('$HOST/photos/${f.name}')", null)

    // Whatever the phone can read, as a JPEG in the app's own folder: HEIC/HEIF (iPhone and modern
    // Android photos), AVIF, WebP, PNG, GIF, BMP and a JPEG alike. The page keeps a 240px picture, so the
    // photo is scaled down while it is decoded rather than after \u2014 a 12 MP photo would otherwise need
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
"""),

("""        @JavascriptInterface
        fun photo() { runOnUiThread { takePhoto() } }
""",
"""        @JavascriptInterface
        fun photo() { runOnUiThread { takePhoto() } }

        // asked by the page before it blames a picture: this version reads HEIC/HEIF and every other
        // format the phone can decode itself, so a picture that still cannot be opened is the file's fault
        // and not an old app's \u2014 the page says which, instead of telling someone to update for nothing
        @JavascriptInterface
        fun pics() = 2
"""),

("""                val wantsImages = types.isEmpty() || types.any { it.startsWith("image/") }
                val files = p?.createIntent() ?: Intent(Intent.ACTION_GET_CONTENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = if (wantsImages) "image/*" else "*/*"
                }""",
"""                val wantsImages = types.isEmpty() || types.any { it.startsWith("image/") }
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
                }"""),
]
apply(KT, kt_subs)

apply('app/build.gradle.kts', [('versionCode = 3', 'versionCode = 4'),
                               ('versionName = "1.2"', 'versionName = "1.3"')])

# ---- the patch notes -------------------------------------------------------------
PN = 'PATCH_NOTES.md'
notice = """## 2026-10-26 \u2014 v1.0.3: A HEIC photo is a photo like any other

This one is **both**: the page carries **v1.0.3** and arrives over the air as usual, but the picture is now
read by the app instead of by the page, so a phone still on an older APK keeps working exactly as it does
today and gains nothing until the new one is installed. The APK is **1.3 (versionCode 4)**.

### Changed
- **The app reads the picture, not the page.** An iPhone's photo, and a modern Android's, is HEIC \u2014 and a
  page running inside the app has no way to draw one, so it was handed the file, could not open it, and
  said so. The app now turns the picked picture into a JPEG itself (`ImageDecoder`, which knows HEIC/HEIF,
  AVIF, WebP, PNG, GIF, BMP and JPEG) and hands the page a picture it can always open. The page still
  keeps the same small photo it always did, so nothing stored changes shape.
- **A big photo is scaled down while it is decoded, not after.** The page keeps a 240px picture; a 12 MP
  photo would otherwise need about 48 MB of memory for something that is about to be thrown away. It is
  decoded at no more than 1024px on its long edge and written out as a JPEG at quality 90.
- **Files no longer hides a picture it does not recognise.** When a picture is wanted, the Files entry of
  the chooser offers every file rather than only the ones the file app already calls an image: a HEIC from
  a cloud app can arrive with no image type at all, and an image-only list quietly left it out. Photos and
  the Gallery are unchanged. A file that is not a picture is refused when it comes back, with a message.
- **"Add photo" in the Edit form now names the form as where the picture belongs.** It used to leave that
  to the file input's own change event, which is how a picture handed straight back by the app could land
  nowhere in that one form.

### Unchanged
- **An older app keeps working.** The page still fills the photo from the file input itself when the app
  cannot hand one back, so a phone on the old APK behaves exactly as before; it simply has no HEIC.
- Nothing about the stored family changes. A photo is still a data URL in the same field, a backup is
  byte-for-byte what it was, and a photo already saved is not touched or re-encoded.
- The camera path, the person's own page (Add photo / Change photo) and the 240px limit are all as they
  were \u2014 they go through the same door, so they gain the new formats too.
- Before Android 9 there is no HEIF decoder in the platform, so HEIC on such a phone is still refused,
  and the page now says which of the two it is instead of blaming HEIC in general.

### Verified
- **15 checks in a real browser** (Chromium, the page served over http, the app's bridge stubbed) \u2014
  **0 failed**: a picture handed back by the app lands in the Edit form and survives Save; "Add photo"
  points the form at that picture and opens the input; the page names the right kind of trouble for a new
  app, an older app and a plain browser; an older app still fills the photo through the input itself from
  a file with a `.HEIC` name and no type at all; the page carries v1.0.3, Settings shows it, and What's
  New leads with this update.
- **The APK builds** \u2014 `gradle assembleDebug` with the Android SDK, and the built APK is **versionCode 4 /
  versionName 1.3** with the v1.0.3 page inside it (`assets/index.html`).
- **Not verified here:** a HEIC being decoded on a real phone \u2014 there is no Android device in this
  environment. The decode is `ImageDecoder.decodeBitmap`, the platform's own reader, and the fallback if it
  refuses a file is the old path (the file goes to the page untouched, which says it cannot be opened), so
  a refusal cannot leave a broken photo behind.

"""
pn_anchor = "## 2026-10-13 \u2014 v1.0.2: What's New is a folded list of short notes"
s = read(PN)
if s.count(pn_anchor) == 1 and 'v1.0.3: A HEIC photo' not in s:
    write(PN, s.replace(pn_anchor, notice + pn_anchor))
    print('  %s note added' % PN)
elif 'v1.0.3: A HEIC photo' in s:
    print('  %s already applied' % PN)
else:
    sys.exit('FATAL: the patch-notes anchor matched %d times' % s.count(pn_anchor))

print('patched v1.0.3')
