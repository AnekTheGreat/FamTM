#!/usr/bin/env python3
"""FamTM 1.6.2 - the other half of the exchange, and the asking that was missing on both sides.

UJournal's Sync birthdays was refused because Android 11 and later hide one app from another unless
the first names it in <queries>. That is fixed in UJournal 1.9.2. This is this app's own half:

  * it names the journal, so the birthdays kept there can be read at all;
  * it reads them (read-only, names and days) and shows them in Birthdays under From UJournal;
  * it hands its own list over on every launch, not only when reminders happen to be on, so the
    journal has something to import the first time either app is opened.

Usage: python3 dev/patch-162.py [--check]
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "app/src/main/AndroidManifest.xml"
GRADLE = ROOT / "app/build.gradle.kts"
ACTIVITY = ROOT / "app/src/main/java/com/familytree/app/MainActivity.kt"
JOURNAL = ROOT / "app/src/main/java/com/familytree/app/JournalBirthdays.kt"
PAGE = ROOT / "app/src/main/assets/index.html"
NOTES = ROOT / "PATCH_NOTES.md"

QUERIES = '''    <!-- Android 11 and later hide one app from another unless the first names it, and a hidden app
         cannot be reached at all - not its package, not its provider. This names the journal, so the
         birthdays kept there can be read the same way UJournal reads these. Only that one provider is
         named, and it is read-only. -->
    <queries>
        <package android:name="app.ujournal" />
        <provider android:authorities="app.ujournal.birthdays" />
    </queries>
'''

JOURNAL_KT = '''package com.familytree.app

import android.content.Context
import android.net.Uri
import org.json.JSONArray
import org.json.JSONObject

/**
 * The birthdays UJournal keeps, read through the read-only provider it publishes at
 * `content://app.ujournal.birthdays/list`.
 *
 * The journal hands over the same short list this app hands to it - a name, a month and a day for
 * each birthday it holds, plus the year when one was given - in exactly the shape [BirthdayProvider]
 * answers with, so one reader of either is the same code. It answers a query and refuses every
 * write, so this is a read and nothing more: nothing here can add, change or remove a birthday in
 * the journal.
 *
 * Everything fails quietly. The journal may not be installed, may be older than its provider, or may
 * have no birthdays in it; each of those is an empty list, which is what the page draws.
 */
object JournalBirthdays {

    private val URI: Uri = Uri.parse("content://app.ujournal.birthdays/list")

    /**
     * The journal's birthdays as `[{"n":name,"m":month,"d":day,"y":year}]`, already checked: a row
     * with no name or no real day is dropped rather than drawn as a blank one.
     */
    fun list(ctx: Context): String = try {
        val raw = ctx.contentResolver.query(URI, null, null, null, null)?.use { cur ->
            if (!cur.moveToFirst()) null else {
                val i = cur.getColumnIndex("json")
                if (i < 0) null else cur.getString(i)
            }
        } ?: "[]"
        val arr = JSONArray(raw)
        val out = JSONArray()
        for (k in 0 until arr.length()) {
            val o = arr.optJSONObject(k) ?: continue
            val name = o.optString("n").trim().take(80)
            val m = o.optInt("m")
            val d = o.optInt("d")
            if (name.isEmpty() || m !in 1..12 || d !in 1..31) continue
            out.put(
                JSONObject()
                    .put("n", name)
                    .put("m", m)
                    .put("d", d)
                    .put("y", o.optInt("y"))
            )
        }
        out.toString()
    } catch (e: Exception) {
        "[]"
    }
}
'''

BRIDGE_ADD = '''
        // The Birthdays page asks for the ones the journal keeps. It is a read of UJournal's own
        // read-only provider; nothing is written back through it.
        @JavascriptInterface
        fun journalBirthdays(): String = JournalBirthdays.list(this@MainActivity)
'''

JS_ADD = '''// ---- birthdays kept in UJournal ----
// UJournal publishes its birthdays read-only at content://app.ujournal.birthdays/list, in the shape
// this app publishes its own. They are shown here and nothing is written: the journal owns them, and
// the reminders still fire from the list this app keeps for itself.
const jdList=()=>{try{const A=window.Android;if(!A||typeof A.journalBirthdays!=='function')return [];
 const r=JSON.parse(A.journalBirthdays()||'[]');return Array.isArray(r)?r:[]}catch(e){return []}};
const jdDate=x=>{try{return new Date(2000,x.m-1,x.d).toLocaleDateString(undefined,{day:'numeric',month:'short'})}catch(e){return x.m+'/'+x.d}};
function jdBlock(){const J=jdList();if(!J.length)return '';
 return `<h3>From UJournal</h3><p class="m">The birthdays kept in the journal on this phone. They are read from it and shown as they are – nothing here is added to the family and nothing in the journal is changed.</p>`+
  `<div class="tscroll">${J.slice(0,40).map(x=>`<div class="card" style="cursor:default"><span class="grow"><b>${h(x.n)}</b><br><small>${jdDate(x)}${x.y>0?' · '+x.y:''}</small></span></div>`).join('')}</div>`}
'''

UPD = '[{"v":"1.6.2","d":"2026-11-06","t":"UJournal\\u2019s birthdays show up here too","x":["The exchange is both ways now, and the missing half was Android\'s. Android 11 and later hide one app from another unless it is named, so UJournal asked this app for its birthdays and was told it was not installed. Both apps now name each other: UJournal brings these birthdays across, and the birthdays it keeps are read here.","UJournal\'s birthdays are in Birthdays, under From UJournal: the name and the day of each one, read from the journal and shown as they are. Nothing is added to the family and nothing is changed in the journal \\u2013 the reminders here still fire from this app\'s own list.","The list is handed over on every launch now, not only when reminders happen to be on, so a birthday recorded here reaches the journal the next time either app is opened.","This one is in the app itself, so install the update; the page arrived with it."]},'

NOTE = '''## 2026-11-06 — v1.6.2: UJournal's birthdays show up here, and both apps name each other

An app change: it needs the new APK. The page that came with it carries **v1.6.2**.

### Fixed
- **UJournal could not read this app's list, and said so as "FamTM is not installed".** Android 11 and
  later hide one app from another unless the first names it, and neither app named the other: the
  query for this app's birthdays was refused before it reached `BirthdayProvider`. UJournal 1.9.2
  declares this app; this release declares UJournal, so each can see the other's list.
- **The list went over only when reminders were on.** The page handed its birthdays to the phone on
  every family change, but on launch only if reminders had been turned on, so a journal opened on a
  phone that never turned reminders on found nothing. It is handed over on every launch now.

### Added
- **Birthdays → From UJournal.** The birthdays UJournal keeps, with the day each comes round and the
  year when it was given, read from the journal's own read-only provider. They are shown, not copied:
  nothing is added to the family, the tree is untouched, and the reminders still fire from this app's
  own list.

### Unchanged
- `BirthdayProvider` still answers with names and days only, still refuses every write, and the
  family tree, the reminders and the people are exactly as they were.


'''


def edit(path, pairs):
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if old not in text:
            raise SystemExit("patch-162: %s: no such text to replace:\n  %r" % (path.name, old[:90]))
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")


def main():
    check = "--check" in sys.argv
    page = PAGE.read_text(encoding="utf-8")
    done = (
        '<provider android:authorities="app.ujournal.birthdays" />' in MANIFEST.read_text(encoding="utf-8")
        and JOURNAL.exists()
        and "fun journalBirthdays()" in ACTIVITY.read_text(encoding="utf-8")
        and "const VER='1.6.2'" in page
        and 'jdBlock()+' in page
        and '{"v":"1.6.2"' in page
        and "## 2026-11-06 — v1.6.2" in NOTES.read_text(encoding="utf-8")
    )
    if check:
        print("1.6.2 already applied" if done else "1.6.2 not applied yet")
        return 0 if done else 1
    if done:
        print("1.6.2 already applied - nothing to do")
        return 0

    # 1. The asking, on this side.
    edit(MANIFEST, [(
        '    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />\n',
        '    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />\n' + QUERIES,
    )])

    # 2. The reader, and the one line that lets the page ask for it.
    JOURNAL.write_text(JOURNAL_KT, encoding="utf-8")
    edit(ACTIVITY, [(
        '                    notifL.launch(Manifest.permission.POST_NOTIFICATIONS)\n'
        '            }\n'
        '        }\n',
        '                    notifL.launch(Manifest.permission.POST_NOTIFICATIONS)\n'
        '            }\n'
        '        }\n' + BRIDGE_ADD,
    )])

    # 3. The page: its version, the block in Birthdays, and the list handed over on every launch.
    edit(PAGE, [
        ("const VER='1.6.1'", "const VER='1.6.2'"),
        ('function bdaysView(){', JS_ADD + 'function bdaysView(){'),
        ("  `<h3>Remind me on the day</h3>`+(bdCap()=='native'", "  jdBlock()+`<h3>Remind me on the day</h3>`+(bdCap()=='native'"),
        ('index();render();if(bdOn())bdPush();', 'index();render();bdPush();'),
        ('<script id="upd" type="application/json">[{"v":"1.6.1",', '<script id="upd" type="application/json">' + UPD + '{"v":"1.6.1",'),
    ])

    # 4. The version in the build file, so a build from main without a version in the env is 1.6.2.
    edit(GRADLE, [('VERSION_NAME") ?: "1.6.1"', 'VERSION_NAME") ?: "1.6.2"')])

    # 5. The notes.
    edit(NOTES, [('## 2026-11-05 — v1.6.1:', NOTE + '## 2026-11-05 — v1.6.1:')])

    print("1.6.2 applied: UJournal named, JournalBirthdays added, Birthdays shows From UJournal, notes written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
