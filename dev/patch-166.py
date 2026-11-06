#!/usr/bin/env python3
"""FamTM 1.6.6 - every app in the list, and a tab row that holds its place.

Two things are wrong with 1.6.5, both of them visible in the settings panel:

  * Other apps lists two apps. The family is five - this one, UJournal, SideCut,
    MeasureT and My Hub - and each has a place it installs from.
  * The row of tabs is a horizontal scroller, and every tap on a tab redraws the
    panel. The redraw also throws the row's scroll position away, so the strip
    snaps back to its first tab under your thumb.

Page only, so it arrives over the air. Run twice and the second run changes
nothing; --check only verifies.
"""
import json
import re
import sys

PAGE = "app/src/main/assets/index.html"
NOTES = "PATCH_NOTES.md"
CHECK = "--check" in sys.argv

NEW_VER = "1.6.6"
OLD_VER = "1.6.5"


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    if not CHECK:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)


def swap(text, old, new, what):
    """One exact replacement. Already there means nothing to do; missing means stop."""
    if new in text:
        return text, False
    if old not in text:
        sys.exit("could not find " + what)
    return text.replace(old, new, 1), True


APPS_OLD = """const APPS=[
 ['UJournal','Keeps the days you write down, and marks the birthdays this family hands over.','https://github.com/AnekTheGreat/Journal'],
 ['FamTM','This app: the family tree in your pocket.','https://github.com/AnekTheGreat/FamTM']
];"""

APPS_NEW = """const APPS=[
 ['UJournal','Keeps the days you write down, and marks the birthdays this family hands over.','https://play.google.com/store/apps/details?id=app.ujournal'],
 ['SideCut','A music player with its own equaliser.','https://play.google.com/store/apps/details?id=com.SideCut.myapp'],
 ['MeasureT','Elevation, location, a level and a converter.','https://play.google.com/store/apps/details?id=com.CompassEDC.myapp'],
 ['My Hub','One screen that launches this family of apps.','https://github.com/AnekTheGreat/My-Hub'],
 ['FamTM','This app: the family tree in your pocket.','https://play.google.com/store/apps/details?id=com.FamTM.app']
];"""

COMMENT_OLD = """// The apps worth pointing at, one line each. Both are public and stay on this account, so a link in
// here can never point at something that is not there."""

COMMENT_NEW = """// The apps worth pointing at, one line each, and where each one is installed from: a Play listing
// where there is one, and this account's own repository for My Hub, which is not on Play. Every one
// is public and stays on this account, so a link in here can never point at something that is not
// there."""

NOTE_OLD = "Made by the same person, and neither one asks you to sign in."
NOTE_NEW = "Made by the same person, and not one of them asks you to sign in."

MENU_HEAD_OLD = """function menu(sec){
 const s=TABS.some(t=>t[0]===sec)?sec:'tree',n=invented().length;"""

MENU_HEAD_NEW = """function menu(sec){
 const s=TABS.some(t=>t[0]===sec)?sec:'tree',n=invented().length;
 // Where the strip of tabs is scrolled to right now, so the redraw below can put it back.
 const prev=$('#dlg').querySelector('.tabs'),sx=prev?prev.scrollLeft:0;"""

SHOW = """ show(`<h2>Settings</h2><div class="tabs">${tabs}</div>${pane}<p class="m" style="margin-top:18px">Family Tree v${h(VER)}</p>`)
}"""

SHOW_NEW = """ show(`<h2>Settings</h2><div class="tabs">${tabs}</div>${pane}<p class="m" style="margin-top:18px">Family Tree v${h(VER)}</p>`)
 // The redraw above built a new strip, which starts at its first tab. Put the old position back,
 // then make sure the tab just picked is the one you can see - on a phone five tabs do not fit, so
 // the row is scrolled sideways to reach the last of them.
 const strip=$('#dlg').querySelector('.tabs');
 if(strip){
  strip.scrollLeft=sx;
  const on=strip.querySelector('.tab.on');
  if(on){
   const r=on.getBoundingClientRect(),b=strip.getBoundingClientRect();
   if(r.left<b.left)strip.scrollLeft=Math.max(0,strip.scrollLeft-(b.left-r.left)-10);
   else if(r.right>b.right)strip.scrollLeft+=r.right-b.right+10;
  }
 }
}"""

CSS_OLD = ".tabs{display:flex;gap:6px;overflow-x:auto;padding:4px 0 12px;scrollbar-width:none}"
CSS_NEW = ".tabs{display:flex;gap:6px;overflow-x:auto;overscroll-behavior-x:contain;padding:4px 0 12px;scrollbar-width:none}"

ENTRY = {
    "v": NEW_VER,
    "d": "2026-11-06",
    "t": "Every app in the list, and a tab row that holds its place",
    "x": [
        "Other apps now lists the whole family: UJournal, SideCut, MeasureT and My Hub beside this one, each with the page it installs from, instead of the two that were there.",
        "The row of tabs keeps the place you scrolled it to. Picking a tab further along used to redraw the panel and snap the row back to its first tab; now it stays where you left it and simply brings the tab you picked into view.",
    ],
}

NOTE_SECTION = """## 2026-11-06 — v1.6.6

Other apps is the whole family now - UJournal, SideCut, MeasureT and My Hub beside this one, each
with the page it installs from. The row of tabs also keeps the place you scrolled it to: picking a
tab further along used to snap the row back to the first tab, and now it stays put and brings the
tab you picked into view. Page only, so it arrives over the air.


"""


def main():
    page = read(PAGE)
    notes = read(NOTES)
    changed = []

    page, did = swap(page, COMMENT_OLD, COMMENT_NEW, "the comment above the app list")
    changed.append(did)
    page, did = swap(page, APPS_OLD, APPS_NEW, "the two-app list")
    changed.append(did)
    page, did = swap(page, NOTE_OLD, NOTE_NEW, "the line under Other apps")
    changed.append(did)
    page, did = swap(page, MENU_HEAD_OLD, MENU_HEAD_NEW, "the head of menu()")
    changed.append(did)
    page, did = swap(page, SHOW, SHOW_NEW, "the end of menu()")
    changed.append(did)
    page, did = swap(page, CSS_OLD, CSS_NEW, "the tab strip's style")
    changed.append(did)
    page, did = swap(page, "const VER='%s'" % OLD_VER, "const VER='%s'" % NEW_VER, "the version line")
    changed.append(did)

    block = re.search(r'(<script id="upd" type="application/json">)(.*?)(</script>)', page, re.S)
    if not block:
        sys.exit("could not find the changelog block")
    entries = json.loads(block.group(2))
    if not entries or entries[0]["v"] != NEW_VER:
        last = entries[0]["v"] if entries else "none"
        if last not in (NEW_VER, OLD_VER):
            sys.exit("the newest note is " + last)
        entries.insert(0, ENTRY)
        changed.append(True)
        packed = json.dumps(entries, ensure_ascii=False, separators=(",", ":"))
        page = page[: block.start(2)] + packed + page[block.end(2) :]
    else:
        changed.append(False)

    if "## 2026-11-06 — v%s" % NEW_VER not in notes:
        anchor = "## 2026-11-06 — v%s" % OLD_VER
        if anchor not in notes:
            sys.exit("could not find where the notes start")
        notes = notes.replace(anchor, NOTE_SECTION + anchor, 1)
        changed.append(True)
    else:
        changed.append(False)

    write(PAGE, page)
    write(NOTES, notes)

    if not any(changed):
        print("already at " + NEW_VER + " - nothing to do")
        return
    print("wrote " + NEW_VER)


if __name__ == "__main__":
    main()
