"""One-shot: the FamTM 1.6.1 page change, applied where the files really are.

Every step is anchored and asserted, so a file that is not the shape this script expects stops
the run before anything is written. Deleted by the runner that calls it.
"""
import json, re, shutil, subprocess, sys, tempfile

PAGE = "app/src/main/assets/index.html"


def read(p):
    return open(p, encoding="utf-8").read()


def write(p, s):
    open(p, "w", encoding="utf-8").write(s)


def rep(path, old, new, count=1):
    s = read(path)
    n = s.count(old)
    if n != count:
        sys.exit("%s: expected %d of %r, found %d" % (path, count, old[:70], n))
    write(path, s.replace(old, new, count))


# ---- 1. the page says which version it is, and its What's New names this update ----

MARK = '<script id="upd" type="application/json">'
s = read(PAGE)
if s.count(MARK) != 1:
    sys.exit("the notes block is not in the page exactly once")
start = s.index(MARK) + len(MARK)
end = s.index("</script>", start)
upd = json.loads(s[start:end])
if upd[0]["v"] != "1.0.3":
    sys.exit("the newest note is %r, not 1.0.3 - this has already run" % upd[0]["v"])

notes = [
    "UJournal can see the birthdays. With UJournal installed, its Plans tab carries one button "
    "that brings over the name and the day of everyone alive in the family, and marks each one on "
    "its calendar every year. One tap, and nobody is typed in twice.",
    "It is the same short list the reminders keep: a name, a month, a day, and the year when one "
    "was given. No photo, no note and no date of death is in it, the family tree is not reachable "
    "from outside, and the list is only ever read, so no app can change a person through it.",
    "A backup can be added instead of replacing the family. Import a backup now offers to add the "
    "people and notes in the file beside the family already on the phone - anyone the phone "
    "already has is left alone rather than added twice - and it carries your settings with it. "
    "Replace everything is still there, and it asks first.",
    "The page now says which version it is. It had been calling itself v1.0.3 since 26 October "
    "while the app was on 1.5.0 and 1.6.0, so What's New had nothing to say about the birthdays and "
    "stayed silent after an update that changed something.",
]
entry = {
    "v": "1.6.1",
    "d": "2026-11-05",
    "t": "The birthdays go to UJournal, and a backup can be added to your family",
    "x": notes,
}
block = "[" + json.dumps(entry, ensure_ascii=False, separators=(",", ":")) \
    .replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026") + "," + s[start + 1:end]
json.loads(block)                       # the block that will ship really parses
write(PAGE, s[:start] + block + s[end:])
rep(PAGE, "const VER='1.0.3'", "const VER='1.6.1'")

# ---- 2. the page is read from main, with the newest tag as the fallback ----

OTA = '''    /**
     * The page is read from `main` first, and from the newest release tag only if the branch cannot
     * be read.
     *
     * It used to be the tag alone, which meant a page-only change could not reach a phone at all
     * until somebody cut a release for it - the one thing an over-the-air screen exists to avoid.
     * A page change is a commit on `main`, and this is where it lands; the tag stays as the fallback
     * so a phone still gets the last published page when the branch is unreachable.
     */
    // "updated" / "current" / "bad" / "offline"
    private fun otaUpdate(): String = try {
        takeFrom("main") ?: newestTag()?.let { takeFrom(it) } ?: "offline"
    } catch (e: Exception) { "offline" }

    /**
     * One ref, read and, when it really is newer, swapped in. Null means there is nothing to say
     * about this ref: it is not there, or it answered with something that is not the family tree, so
     * the caller can try the next source instead of calling it offline.
     */
    private fun takeFrom(ref: String): String? = try {
        val c = open("https://raw.githubusercontent.com/$REPO/$ref/app/src/main/assets/index.html?t=${System.currentTimeMillis()}")
        if (c.responseCode != 200) null
        else {
            val bytes = c.inputStream.use { it.readBytes() }
            // A page that is not the family tree is not an update, whatever the server answered.
            if (bytes.size < 2000 || !String(bytes).contains("familytree.v1")) null
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
    } catch (e: Exception) { null }'''

MAIN = "app/src/main/java/com/familytree/app/MainActivity.kt"
s = read(MAIN)
old = re.compile(
    r'    // "updated" / "current" / "bad" / "offline"\n'
    r'    private fun otaUpdate\(\): String = try \{.*?\n    \} catch \(e: Exception\) \{ "offline" \}', re.S)
hits = old.findall(s)
if len(hits) != 1:
    sys.exit("the OTA function is not in MainActivity exactly once (%d)" % len(hits))
write(MAIN, old.sub(lambda m: OTA, s, count=1))
if "private fun takeFrom(" not in read(MAIN):
    sys.exit("takeFrom did not land")

# ---- 3. the version the build names, and the two copies of the page stay one page ----

rep("app/build.gradle.kts",
    'versionName = System.getenv("VERSION_NAME") ?: "1.5.0"',
    'versionName = System.getenv("VERSION_NAME") ?: "1.6.1"')
shutil.copyfile(PAGE, "index.html")

# ---- 4. the patch notes this page is written from ----

NOTES = """## 2026-11-05 — v1.6.1: the notes catch up, a backup can be added, and the page follows `main`

A page change: it arrives over the air, nothing to install. The page carries **v1.6.1** now.

### Changed
- **The page finally says which version it is.** It had been calling itself **v1.0.3** since 26 October while
the app was on 1.5.0 and 1.6.0, so What's New had nothing to say about the birthdays — the popup stayed silent
after an update that changed something. The page carries **v1.6.1** and its notes name the birthday hand-off,
so the popup appears on the first launch after this update, once.
- **The page is read from `main`, not from the last release tag.** The app used to fetch the page the newest
release was tagged with, so a page-only change could not reach a phone until a release was cut for it — the one
thing an over-the-air screen exists to avoid. `main` is read first now and the newest tag is kept as the
fallback, so a phone still gets the last published page when the branch cannot be reached. A page that is not
the family tree is still refused, and a bad copy still falls back to the screen the APK ships with.
- **A backup can be added to the family instead of replacing it.** *Import a backup* used to have one answer —
replace everything — so a file from another phone could only be restored over the family already here. It now
asks: **Add to my family** brings the people and the notes in beside the ones you have, and anyone this phone
already has is the same person and is left exactly as they were, so the same file cannot be added twice.
**Replace everything** is still there, unchanged.
- **Your settings travel with the file.** *Export everything* writes the birthday reminders, the automatic
parent linking and the update you have already read into the backup, and restoring one puts them back, so a
new phone opens the way the old one did.
- **The menu says what the buttons do** — *Export everything* and *Import a backup* — instead of *Backup
(JSON)* and *Restore from backup*, which read as though the file were the app rather than the family in it.

### Unchanged
- Nothing about the family is stored differently: the shape is the same, only with a settings block added, so a
backup made here restores into any earlier version and an older backup still restores into this one.
- The tree, the reminders and the people are exactly as they were.

### Verified
- The page's What's New block is read back out of the delivered page and parsed, and its newest entry is
**v1.6.1**; the page names **v1.6.1** in its own version constant; and the two copies of the page
(`index.html` and `app/src/main/assets/index.html`) are byte-for-byte identical.
- **Not verified here:** the Android half (reading the page from `main`, falling back to the tag) is reviewed
rather than compiled — CI builds the APK on push.

## 2026-11-05 — v1.5.0: the birthdays are shared with UJournal"""

rep("PATCH_NOTES.md", "## 2026-11-05 — v1.5.0: the birthdays are shared with UJournal", NOTES)
rep("PATCH_NOTES.md",
    "opened. Only native changes require a new APK.",
    "opened (the newest release tag is read only when `main` cannot be). Only native changes\nrequire a new APK.")

# ---- 5. say what was done, and refuse to finish if the page that will ship is not one page ----

page = read(PAGE)
i = page.index(MARK) + len(MARK)
d = json.loads(page[i:page.index("</script>", i)])
assert d[0]["v"] == "1.6.1" and "const VER='1.6.1'" in page
assert read("index.html") == page
print("FamTM 1.6.1 applied: newest note %s, %d notes, VER 1.6.1, both page copies identical"
      % (d[0]["v"], len(d[0]["x"])))
