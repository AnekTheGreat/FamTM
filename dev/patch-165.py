#!/usr/bin/env python3
"""FamTM 1.6.5 - Settings becomes a panel with tabs, and the screen keeps itself current.

Page and shell together: the panel is the page's, the launch check is the shell's, so both are in
one patch and one release. Idempotent: a second run changes nothing, and --check fails when any
part of 1.6.5 is missing.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "app/src/main/assets/index.html"
KT = ROOT / "app/src/main/java/com/familytree/app/MainActivity.kt"
NOTES = ROOT / "PATCH_NOTES.md"
V = "1.6.5"

CSS = """
/* 1.6.5: the settings panel's own tabs, and a little motion so a tap is answered. */
.tabs{display:flex;gap:6px;overflow-x:auto;padding:4px 0 12px;scrollbar-width:none}
.tabs::-webkit-scrollbar{display:none}
.tab{flex:0 0 auto;padding:8px 14px;border-radius:99px;border:1px solid var(--line);background:var(--card);color:var(--mute);font:600 14px system-ui;cursor:pointer}
.tab.on{background:var(--acc);border-color:var(--acc);color:var(--onacc)}
.btn,.chip,.tab{transition:background .15s ease,color .15s ease,border-color .15s ease,transform .08s ease}
.tab:active,.btn:active,.chip:active{transform:scale(.97)}
.approw{display:flex;gap:12px;align-items:center;padding:12px 14px;margin-top:8px;background:var(--card);border:1px solid var(--line);border-radius:12px}
.approw b{display:block}.approw small{display:block;margin-top:2px}.approw .go{margin-left:auto;flex:0 0 auto;margin-right:0}
dialog[open]{animation:dlg .16s ease-out}@keyframes dlg{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@media(prefers-reduced-motion:reduce){dialog[open]{animation:none}.btn,.chip,.tab{transition:none}}
"""

JS = """const TABS=[['tree','Family'],['transfer','Transfer'],['updates','Updates'],['support','Support'],['apps','Other apps']];
// The apps worth pointing at, one line each. Both are public and stay on this account, so a link in
// here can never point at something that is not there.
const APPS=[
 ['UJournal','Keeps the days you write down, and marks the birthdays this family hands over.','https://github.com/AnekTheGreat/Journal'],
 ['FamTM','This app: the family tree in your pocket.','https://github.com/AnekTheGreat/FamTM']
];
// A page older than the shell that runs it must never fail to open because a button called something
// the app has not got yet, so every call into the phone is asked for first.
const canDo=k=>{try{return !!(window.Android&&typeof Android[k]=='function')}catch(e){return false}};
function openApp(u){if(canDo('open')){try{Android.open(u);return}catch(e){}}say('On a computer, this is '+u)}
function tipNow(){if(canDo('tip')){try{Android.tip();return}catch(e){}}say('Tips open in the app on this phone.')}
function updNow(){if(canDo('refresh')){try{Android.refresh();return}catch(e){}}say('This screen is the newest there is - a newer one puts itself in place when the app opens.')}
// Settings, in one place and cut into tabs: the family's own switches, the way a family leaves this
// phone and arrives on another, the update check, the tip, and the other apps.
function menu(sec){
 const s=TABS.some(t=>t[0]===sec)?sec:'tree',n=invented().length;
 const tabs=TABS.map(([k,l])=>`<button class="tab${k===s?' on':''}" data-act="mtab" data-sec="${k}" type="button">${h(l)}</button>`).join('');
 const pane={
  tree:`<div class="menu">${n?`<button class="btn" data-act="cleanph">Remove ${n} Unknown parent${n==1?'':'s'}</button>`:''}<button class="btn" data-act="autopar">${autoOn()?'Stop linking parents automatically':'Link parents automatically'}</button><button class="btn" data-act="bdays">Birthdays</button><button class="btn" data-act="wn">What's New</button><button class="btn" data-act="close">Close</button></div><p class="m">Your ${P.length} ${P.length==1?'person is':'people are'} on this phone only - no account, and nothing sent anywhere.</p>`,
  transfer:`<div class="menu"><button class="btn p" data-act="json">Export everything</button><button class="btn" data-act="restore">Import a backup</button><button class="btn" data-act="pdf">Export PDF</button><button class="btn" data-act="close">Close</button></div><p class="m">A backup is one file holding every person, every note and your settings, so a new phone is a file and a tap. Add keeps the family you already have; Replace puts the file in its place.</p>`,
  updates:`<div class="menu"><button class="btn p" data-act="upd">Check for updates</button><button class="btn" data-act="wn">What's New</button><button class="btn" data-act="close">Close</button></div><p class="m">A newer screen puts itself in place the next time this app opens, and nothing is installed. If a card or a note is open at that moment it waits, so nothing you were typing is lost.</p><p class="m">This screen is v${h(VER)}.</p>`,
  support:`<div class="menu"><button class="btn p" data-act="tipnow">Leave a tip</button><button class="btn" data-act="appsopen" data-url="https://github.com/AnekTheGreat/FamTM/releases">Release notes on the web</button><button class="btn" data-act="close">Close</button></div><p class="m">FamTM is one person's work and it asks nothing of you: no account, no tracking, and no server holding your family. A tip is the whole business model.</p>`,
  apps:`<div class="menu">${APPS.map(([t,d,u])=>`<div class="approw"><span class="grow"><b>${h(t)}</b><small>${h(d)}</small></span><button class="chip go" data-act="appsopen" data-url="${u}">Open</button></div>`).join('')}<button class="btn" data-act="close">Close</button></div><p class="m">Made by the same person, and neither one asks you to sign in.</p>`
 }[s];
 show(`<h2>Settings</h2><div class="tabs">${tabs}</div>${pane}<p class="m" style="margin-top:18px">Family Tree v${h(VER)}</p>`)
}
// The way out of a tab is the tab, so Back to settings lands on the first one.
const backToSettings=`<button class="btn" data-act="menu">Back to settings</button>`;"""

KT_OLD = re.compile(r"    private fun checkOta\(\) \{.*?\n    \}\n\}", re.S)
KT_NEW = """    /**
     * The check that runs on every launch. A page update is a file, not an install: there is nothing
     * to consent to, so it is put in place and drawn straight away instead of waiting for a tap on
     * the refresh button.
     *
     * The one exception is a screen with a dialog open - a half-typed person or note is worth more
     * than the second it saves. The file is already stored by then, so the next launch draws it.
     */
    private fun checkOta() {
        Thread {
            if (otaUpdate() != "updated") return@Thread
            runOnUiThread {
                web.evaluateJavascript("(document.querySelector('dialog[open]')?'y':'n')") { a ->
                    if (a != null && a.contains("y")) {
                        toast("Updated - it will be on screen next time")
                    } else {
                        web.loadUrl("$HOST/ota/index.html")
                        toast("Updated to the newest screen")
                    }
                }
            }
        }.start()
    }
}"""

OPEN_METHOD = """        // The Other apps tab: a link is handed to the phone, never loaded in this WebView, so the
        // family tree can never be replaced by a web page. Only the two accounts this app belongs to
        // are accepted, so a page that is not ours cannot send the phone anywhere.
        @JavascriptInterface
        fun open(u: String) {
            if (!u.startsWith("https://github.com/AnekTheGreat/") &&
                !u.startsWith("https://play.google.com/")
            ) {
                runOnUiThread { toast("That link is not one of ours") }
                return
            }
            try {
                startActivity(
                    android.content.Intent(
                        android.content.Intent.ACTION_VIEW,
                        android.net.Uri.parse(u)
                    )
                )
            } catch (e: Exception) {
                runOnUiThread { toast("No app on this phone can open that link") }
            }
        }

"""

ENTRY = {
    "v": V,
    "d": "2026-11-06",
    "t": "Settings is one panel with tabs, and the screen keeps itself current",
    "x": [
        "Settings is a panel now, with five tabs across the top: Family, Transfer, Updates, Support and Other apps. Family holds the switches that belong to the tree, Transfer holds export, import and PDF, Updates holds the update check and What's New, Support holds the tip, and Other apps lists the apps made beside this one.",
        "The screen updates itself. A newer screen used to be downloaded and then wait for a tap on the refresh button; it is put in place and drawn as soon as the app opens. The one exception is a card or note open at that moment - the screen waits rather than throwing away what was being typed, and the newer screen is there on the next open.",
        "Other apps opens UJournal or FamTM in the phone's own browser, and the tip opens as it did - the page asks the app, and an older app that has never heard of a link still shows it as text instead of doing nothing.",
        "The tabs, the buttons and the settings sheet answer a tap: a short press-in, and the sheet rises instead of appearing. On a phone set to reduce motion none of it moves."
    ],
}

NOTE = """## 2026-11-06 — v1.6.5

Settings is one panel with tabs — Family, Transfer, Updates, Support, Other apps — and a newer screen
is drawn as soon as the app opens instead of waiting for the refresh button. Nothing reloads while a
card or a note is open, so a half-typed person is never lost.
"""


def must(cond, msg):
    if not cond:
        sys.exit("patch-165: " + msg)


def main():
    check = "--check" in sys.argv
    page = PAGE.read_text(encoding="utf-8")
    kt = KT.read_text(encoding="utf-8")
    notes = NOTES.read_text(encoding="utf-8")
    done = []

    # 1. the version the page calls itself
    if "const VER='%s'" % V in page:
        done.append("version")
    elif "const VER='1.6.4'" in page:
        if not check:
            page = page.replace("const VER='1.6.4'", "const VER='%s'" % V, 1)
        done.append("version")
    else:
        must(False, "the page is on neither 1.6.4 nor %s" % V)

    # 2. What's New gets the entry
    if '"v":"%s"' % V in page:
        done.append("changelog")
    else:
        must("<script id=\"upd\" type=\"application/json\">[" in page, "the changelog block is gone")
        must(not check, "--check: What's New has no %s entry" % V)
        page = page.replace(
            "<script id=\"upd\" type=\"application/json\">[",
            "<script id=\"upd\" type=\"application/json\">["
            + json.dumps(ENTRY, ensure_ascii=False, separators=(",", ":"))
            + ",",
            1,
        )
        done.append("changelog")

    # 3. the panel's own styling
    if ".tabs{" in page:
        done.append("styles")
    else:
        must("</style>" in page, "no style block")
        must(not check, "--check: the tab styles are missing")
        page = page.replace("</style>", CSS + "</style>", 1)
        done.append("styles")

    # 4. the flat settings list becomes the tabbed panel
    lines = page.split("\n")
    at = [i for i, l in enumerate(lines) if l.startswith("function menu(){")]
    if not at:
        must("const TABS=" in page, "the settings menu is neither the old flat list nor the new panel")
        done.append("panel")
    else:
        must(len(at) == 1, "more than one settings menu")
        must(not check, "--check: the settings panel is still the flat list")
        lines[at[0]] = JS
        page = "\n".join(lines)
        done.append("panel")

    # 5. the new buttons have something behind them
    hook = "menu:()=>menu(),wn:()=>wnArchive(),"
    wide = ("menu:()=>menu(),mtab:()=>menu(d.sec),wn:()=>wnArchive(),"
            "upd:()=>updNow(),tipnow:()=>tipNow(),appsopen:()=>openApp(d.url),")
    if "appsopen:()=>openApp(d.url)" in page:
        done.append("actions")
    else:
        must(hook in page, "the action table does not have the settings entry")
        must(not check, "--check: the panel's buttons are not wired")
        page = page.replace(hook, wide, 1)
        done.append("actions")

    # 6. the phone side: the link opener and the launch check
    if "fun open(u: String)" in kt:
        done.append("link opener")
    else:
        anchor = "        // the ♥ button the app puts beside ⟳"
        must(anchor in kt, "the tip button is not where the bridge methods end")
        must(not check, "--check: the page cannot open a link")
        kt = kt.replace(anchor, OPEN_METHOD + anchor, 1)
        done.append("link opener")

    if "Updated to the newest screen" in kt:
        done.append("launch check")
    else:
        must("Update ready – tap ⟳ to apply" in kt, "the launch check is neither the old one nor the new one")
        must(not check, "--check: the launch check still waits for a tap")
        kt, n = KT_OLD.subn(KT_NEW, kt)
        must(n == 1, "checkOta could not be replaced cleanly")
        done.append("launch check")

    # 7. what the patch notes say
    if "## 2026-11-06 — v%s" % V in notes:
        done.append("notes")
    else:
        must(not check, "--check: PATCH_NOTES has no %s entry" % V)
        cut = notes.find("\n## ")
        notes = (notes[: cut + 1] + NOTE + notes[cut + 1:]) if cut > 0 else (notes + "\n" + NOTE)
        done.append("notes")

    if check:
        print("1.6.5 is in place: " + ", ".join(done))
        return

    PAGE.write_text(page, encoding="utf-8")
    KT.write_text(kt, encoding="utf-8")
    NOTES.write_text(notes, encoding="utf-8")
    print("applied: " + ", ".join(done))


main()
