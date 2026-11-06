#!/usr/bin/env python3
"""FamTM 1.6.8 - My Hub comes off the Other apps list.

The list points at the apps a tap can install, and every other row on it is a Play listing. My Hub is
a repository, so a tap left the app for a page with nothing to install. It comes off the list, off
the Guide line that describes the list, and the page says 1.6.8.

Idempotent: every change is guarded by the text that proves it is already there.
  python3 dev/patch-168.py           apply
  python3 dev/patch-168.py --check   report only
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "app" / "src" / "main" / "assets" / "index.html"
NOTES = ROOT / "PATCH_NOTES.md"
VERSION = "1.6.8"
OLD = "1.6.7"

CHECK = "--check" in sys.argv


def swap(src, old, new, marker, what):
    if marker in src:
        print(f"  already: {what}")
        return src
    n = src.count(old)
    if n != 1:
        raise SystemExit(f"!! {what}: text appears {n} times, expected 1")
    print(f"  changed: {what}")
    return src.replace(old, new, 1)


src = PAGE.read_text(encoding="utf-8")

src = swap(
    src,
    f"const VER='{OLD}',UPD=",
    f"const VER='{VERSION}',UPD=",
    f"const VER='{VERSION}',UPD=",
    f"page version -> {VERSION}",
)

# ---- the row, and the comment above the list that explained it ------------------------------
if "My-Hub" not in src:
    print("  already: My Hub off the Other apps list")
else:
    if src.count("My-Hub") != 1:
        raise SystemExit("!! My Hub: its address appears more than once")
    row = " ['My Hub','One screen that launches this family of apps.','https://github.com/AnekTheGreat/My-Hub'],\n"
    if src.count(row) != 1:
        raise SystemExit("!! My Hub: the row is not the one expected")
    old_comment = (
        "// The apps worth pointing at, one line each, and where each one is installed from: a Play listing\n"
        "// where there is one, and this account's own repository for My Hub, which is not on Play. Every one\n"
        "// is public and stays on this account, so a link in here can never point at something that is not\n"
        "// there.\n"
    )
    new_comment = (
        "// The apps worth pointing at, one line each, and where each one is installed from: a Play listing,\n"
        "// public and on this account, so a link in here can never point at something that is not there.\n"
    )
    if src.count(old_comment) != 1:
        raise SystemExit("!! the comment above the list is not the one expected")
    src = src.replace(old_comment, new_comment, 1).replace(row, "", 1)
    print("  changed: My Hub off the Other apps list")

# ---- the Guide's line for that tab --------------------------------------------------------
src = swap(
    src,
    "['Other apps','UJournal, SideCut, MeasureT and My Hub.']",
    "['Other apps','UJournal, SideCut and MeasureT.']",
    "['Other apps','UJournal, SideCut and MeasureT.']",
    "the Guide line for Other apps",
)

# ---- the changelog -------------------------------------------------------------------------
entry = {
    "v": VERSION,
    "d": "2026-11-06",
    "t": "My Hub is off the Other apps list",
    "x": [
        "Other apps lists the three apps beside this one that a tap can install: UJournal, SideCut and MeasureT. My Hub is a repository rather than a store listing, so tapping it left the app for a page that could not install anything.",
        "The Guide's own line for Other apps says the same three.",
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
heading = f"## 2026-11-06 — v{VERSION}"
if heading not in notes:
    section = (
        f"{heading}\n\n"
        "**My Hub is off the Other apps list.**\n\n"
        "- Other apps lists the three apps beside this one that a tap can install: UJournal,\n"
        "  SideCut and MeasureT. My Hub is a repository, not a store listing, so a tap on it left the\n"
        "  app for a page that could not install anything.\n"
        "- The Guide's own line for Other apps says the same three.\n"
        "- This one is in the page: it arrives the next time the app opens, with nothing to install.\n\n"
    )
    i = notes.find("## ")
    notes = notes[:i] + section + notes[i:] if i >= 0 else notes + "\n" + section
    print("  added:   PATCH_NOTES.md section")
else:
    print("  already: PATCH_NOTES.md section")

# ---- write ---------------------------------------------------------------------------------
if CHECK:
    print(f"page: {len(src)} bytes (version {VERSION}, My Hub present: {'My-Hub' in src})")
    print("check only - nothing written")
else:
    PAGE.write_text(src, encoding="utf-8")
    NOTES.write_text(notes, encoding="utf-8")
    print(f"wrote {PAGE.relative_to(ROOT)}: {len(src)} bytes")
