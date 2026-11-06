#!/usr/bin/env python3
"""FamTM 1.6.7 - a welcome on the first launch, a tour, and a Guide under the gear.

The page is the app. This writes the welcome that meets a new phone, the five-step tour that walks
the tabs and the settings the app has, and a Guide tab in Settings holding the same tour plus every
feature in one list.

Idempotent: every insertion is guarded by a marker, so a second run writes the same bytes.
  python3 dev/patch-167.py           apply
  python3 dev/patch-167.py --check   report only
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "app" / "src" / "main" / "assets" / "index.html"
NOTES = ROOT / "PATCH_NOTES.md"
VERSION = "1.6.7"
OLD = "1.6.6"

CHECK = "--check" in sys.argv


def insert_before(src, anchor, addition, marker, what):
    if marker in src:
        print(f"  already: {what}")
        return src
    n = src.count(anchor)
    if n != 1:
        raise SystemExit(f"!! {what}: anchor appears {n} times, expected 1")
    print(f"  added:   {what}")
    return src.replace(anchor, addition + anchor, 1)


def insert_after(src, anchor, addition, marker, what):
    if marker in src:
        print(f"  already: {what}")
        return src
    n = src.count(anchor)
    if n != 1:
        raise SystemExit(f"!! {what}: anchor appears {n} times, expected 1")
    print(f"  added:   {what}")
    return src.replace(anchor, anchor + addition, 1)


def swap(src, old, new, marker, what):
    if marker in src:
        print(f"  already: {what}")
        return src
    n = src.count(old)
    if n != 1:
        raise SystemExit(f"!! {what}: old text appears {n} times, expected 1")
    print(f"  changed: {what}")
    return src.replace(old, new, 1)


src = PAGE.read_text(encoding="utf-8")

# ---- the version ---------------------------------------------------------------------------
src = swap(
    src,
    f"const VER='{OLD}',UPD=",
    f"const VER='{VERSION}',UPD=",
    f"const VER='{VERSION}',UPD=",
    f"page version -> {VERSION}",
)

# ---- the Guide tab -------------------------------------------------------------------------
src = swap(
    src,
    "const TABS=[['tree','Family'],['transfer','Transfer'],['updates','Updates'],['support','Support'],['apps','Other apps']];",
    "const TABS=[['tree','Family'],['transfer','Transfer'],['updates','Updates'],['support','Support'],['apps','Other apps'],['guide','Guide']];",
    "['apps','Other apps'],['guide','Guide']]",
    "the Guide tab",
)

GUIDE_PANE = (
    r'''  guide:`<div class="menu"><button class="btn p" data-act="tourgo" data-step="0">Walk through the app</button><button class="btn" data-act="hello">Show the welcome again</button><button class="btn" data-act="close">Close</button></div><p class="m">Everything this app does, in the order it is worth knowing:</p>${GUIDE.map(([t,d])=>`<p class="m" style="margin:10px 0 0"><b>${h(t)}</b><br>${h(d)}</p>`).join('')}`,
'''
)
# The pane object's last entry (Other apps) carries no comma, so the new one is added with the comma
# that belongs in front of it.
src = swap(
    src,
    "`\n }[s];\n",
    "`,\n" + GUIDE_PANE + " }[s];\n",
    'data-act="hello">Show the welcome again',
    "the Guide pane",
)

# ---- the welcome and the tour --------------------------------------------------------------
TOUR_JS = r'''// ---- the welcome, and the tour that goes with it ----
// A first launch is the one moment the app can explain itself without being in the way. The welcome
// says what the tree is for; the tour walks the screens a new person has to find; and the same tour
// sits in Settings > Guide, so nothing here is a thing seen once and then lost.
const TOUR=[
 {t:'Every tab is the same family',b:'People is the list of everyone. Tree draws the family. Notes is a scratchpad: names and dates copied from anywhere that can become people in one tap.'},
 {t:'Adding someone takes one screen',b:'The + button adds a person: a name or just a nickname, born and died dates written however you like, a photo, a note. Parents, partners and children can be set on the same screen.'},
 {t:'The tree does the hard part',b:'Tree draws everyone and joins couples. Drag to move, pinch or + and - to zoom, Fit to see the whole family, and tap anyone to open them.'},
 {t:'Nothing leaves this phone',b:'No account and no server. Transfer holds one backup file with every person, every note and your settings, and a PDF of the tree you can print.'},
 {t:'The screen keeps itself new',b:"A newer screen puts itself in place the next time the app opens. Updates, Check for updates asks right away, and What's New lists every change this app has had."}
];
const GUIDE=[
 ['People','The whole family in one list, with a search box and a pencil on every row.'],
 ['Tree','Everyone drawn: couples joined, parents above their children, photos in the cards.'],
 ['Notes','Names and dates waiting to become people, one tap each.'],
 ['Birthdays','Everyone alive, soonest first, with reminders if you want them.'],
 ['Transfer','One backup file, and a PDF of the tree.'],
 ['Updates','New screens arrive on open. What\'s New holds every change.'],
 ['Support','The tip, and the release notes in a browser.'],
 ['Other apps','UJournal, SideCut, MeasureT and My Hub.']
];
const helloSeen=()=>{try{return localStorage.getItem(KEY+'.hello')=='1'}catch(e){return true}};
const helloMark=()=>{try{localStorage.setItem(KEY+'.hello','1')}catch(e){}};
let tstep=0;
// The welcome is marked seen the moment it is shown rather than when it is closed: a phone put down
// mid-screen should not open on the same screen again tomorrow.
const welcome=()=>{helloMark();markVer();
 show(`<h2>Welcome</h2><p class="m">The family tree in your pocket: everyone, their dates, their photos, and how they are related &mdash; on this phone, with nobody to sign in to.</p><div class="menu"><button class="btn p" data-act="tourgo" data-step="0">Show me around</button><button class="btn" data-act="close">Skip &mdash; I will find my way</button></div>`)}
const tourStep=i=>{tstep=Math.max(0,Math.min(TOUR.length-1,i));const s=TOUR[tstep],n=TOUR.length;
 show(`<h2>Show me around</h2><p class="m">Step ${tstep+1} of ${n}</p><h3>${h(s.t)}</h3><p>${h(s.b)}</p><div class="bar">${tstep>0?`<button class="btn" data-act="tourgo" data-step="${tstep-1}">Back</button>`:'<span></span>'}<button class="btn p" data-act="tourgo" data-step="${tstep+1}">${tstep==n-1?'Done':'Next'}</button></div><button class="btn" style="display:block;width:100%;margin-top:8px" data-act="tourskip">Skip the tour</button>`)}
const tourSkip=()=>{try{localStorage.setItem(KEY+'.tour',VER)}catch(e){}$('#dlg').close()};
'''
src = insert_before(
    src,
    "// The way out of a tab is the tab, so Back to settings lands on the first one.",
    TOUR_JS,
    "const tourStep=",
    "the welcome and the tour",
)

# ---- the taps they use ---------------------------------------------------------------------
src = swap(
    src,
    "close:()=>D.close(),menu:()=>menu(),",
    "close:()=>D.close(),menu:()=>menu(),"
    "tourgo:()=>{const i=+d.step||0;i>=TOUR.length?tourSkip():tourStep(i)},"
    "tourskip:()=>tourSkip(),hello:()=>welcome(),",
    "tourskip:()=>tourSkip()",
    "the tour's buttons",
)

# ---- first launch --------------------------------------------------------------------------
src = swap(
    src,
    "if(seenVer()!==VER)whatsNew();",
    "// A new phone is met by the welcome; anyone else gets the notes for a screen they have not seen\n"
    "// yet. Never both at once: two popups over each other is the opposite of a welcome.\n"
    "if(!helloSeen())welcome();else if(seenVer()!==VER)whatsNew();",
    "if(!helloSeen())welcome();",
    "the first launch",
)

# ---- the changelog -------------------------------------------------------------------------
entry = {
    "v": VERSION,
    "d": "2026-11-06",
    "t": "A welcome, a tour, and a Guide under the gear",
    "x": [
        "A first launch opens on a welcome now: one line on what the tree is for, and two buttons, Show me around and Skip. It comes up once, on the launch after the update, and never again.",
        "The tour walks five screens - the three tabs, adding someone, the tree's own gestures, the backup and the updates - with Next, Back and Skip, and Done on the last one closes it where it stands.",
        "Settings has a Guide tab. It holds the same tour, the welcome, and every feature of the app in one list, so a feature learned once is never a thing you have to remember where it was.",
        "What's New waits until after the welcome, so a new phone is not met by two popups at once.",
        "This one is in the page: it arrives the next time the app opens, with nothing to install.",
    ],
}
packed = json.dumps(entry, ensure_ascii=False, separators=(",", ":"))
changelog = '<script id="upd" type="application/json">['
if f'"v":"{VERSION}"' in src:
    print("  already: changelog entry")
elif src.count(changelog) != 1:
    raise SystemExit("!! changelog: the list start appears more than once")
else:
    src = src.replace(changelog, changelog + packed + ",", 1)
    print("  added:   changelog entry")

# ---- notes ---------------------------------------------------------------------------------
notes = NOTES.read_text(encoding="utf-8")
if f"## {VERSION}" not in notes:
    section = (
        f"## 2026-11-06 — v{VERSION}\n\n"
        "**A welcome, a tour, and a Guide under the gear.**\n\n"
        "- A first launch opens on a welcome: one line on what the tree is for, and two buttons,\n"
        "  Show me around and Skip. Shown once, marked seen when it appears rather than when it closes.\n"
        "- The tour is five steps - the tabs, adding someone, the tree's gestures, the backup, the\n"
        "  updates - with Next, Back and Skip. It draws in the app's own dialog, so it looks like the\n"
        "  rest of the app and needs no new chrome.\n"
        "- Settings gains a Guide tab: the same tour, the welcome, and every feature in one list.\n"
        "- What's New waits behind the welcome, so a new phone is not met by two popups at once.\n\n"
    )
    i = notes.find("## ")
    notes = notes[:i] + section + notes[i:] if i >= 0 else notes + "\n" + section
    print("  added:   PATCH_NOTES.md section")
else:
    print("  already: PATCH_NOTES.md section")

# ---- write ---------------------------------------------------------------------------------
if CHECK:
    print(f"page: {len(src)} bytes (version {VERSION}, tour present: {'const tourStep=' in src})")
    print("check only - nothing written")
else:
    PAGE.write_text(src, encoding="utf-8")
    NOTES.write_text(notes, encoding="utf-8")
    print(f"wrote {PAGE.relative_to(ROOT)}: {len(src)} bytes")
