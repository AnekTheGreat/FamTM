#!/usr/bin/env python3
"""FamTM 1.6.4 - a born date the page can show is a birthday it counts.

There is one forgiving date reader behind the Born box ([normDate]): "7/4", "4 Jul 1950", "21/7" and
"July 1950" all become a stored date. [bdOf] - the function that builds the birthday list, which is
both the Birthdays screen and the list handed to UJournal - had a pattern of its own, so a date that
reached the store any other way (typed before that reader existed, read out of a note, restored from
an older backup) was shown on the person's card and skipped here.

A person could therefore have "Born 4 Jul 1950" on their card, be absent from Birthdays, and leave
the journal with nothing to find.

bdOf now runs the stored date through normDate first, so any date this page can display is a date it
can count. A year on its own, or a month with no day, still has no day to keep and is left out.

Page only: it reaches an installed copy over the air, and the version moves to 1.6.4.

Usage: python3 dev/patch-164.py [--check]
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "app/src/main/assets/index.html"
NOTES = ROOT / "PATCH_NOTES.md"

BD_OLD = """const bdOf=p=>{const m=/^(?:([0-9]{4})[-/]|--)?([0-9]{1,2})[-/]([0-9]{1,2})$/.exec(str(p.birth).trim());if(!m)return null;
 const mo=+m[2],d=+m[3];return mo>=1&&mo<=12&&d>=1&&d<=31?{mo,d,y:m[1]?+m[1]:0}:null};"""

BD_NEW = """// 1.6.4 - a born date is read by the same reader the Born box uses. bdOf had a pattern of its own,
// so a date this page happily displays - "4 Jul 1950", "7/4", "21/7" - was skipped by this list and
// by the list handed to UJournal: a person could show a born date on their card and have no birthday
// anywhere. Every date now goes through normDate first, so what the page can show, it counts. A year
// on its own, or a month with no day, still has no day to keep and is left out.
const bdOf=p=>{const n=normDate(p.birth),m=n&&/^(?:([0-9]{4})-|--)([0-9]{2})-([0-9]{2})$/.exec(n);if(!m)return null;
 const mo=+m[2],d=+m[3];return mo>=1&&mo<=12&&d>=1&&d<=31?{mo,d,y:m[1]?+m[1]:0}:null};"""

VER_OLD = "const VER='1.6.3'"
VER_NEW = "const VER='1.6.4'"

UPD_OLD = '<script id="upd" type="application/json">['
UPD_NEW = ('<script id="upd" type="application/json">[{"v":"1.6.4","d":"2026-11-06",'
           '"t":"A born date this page can show is a birthday it counts",'
           '"x":["The birthdays here, and the short list this app hands to UJournal, are built by a '
           'date reader of their own. A born date written any other way - 4 Jul 1950, 7/4, 21/7, or one '
           'that came from a note or an older backup - was displayed on the person\'s card and quietly '
           'skipped here, so Birthdays could look empty while the family clearly had dates, and the '
           'journal was told nobody had a birthday.",'
           '"The list now runs every born date through the same reader the Born box uses, so any date '
           'this page can show is a date it counts. A year on its own, or a month with no day, still '
           'has no day to keep.",'
           '"The screen arrived with this; nothing to install."]},')

NOTE_OLD = "## 2026-11-06 — v1.6.3: a birthday written as 7/4 counts too"

NOTE_NEW = """## 2026-11-06 — v1.6.4: every born date the page can show is a birthday it counts

A page change: it arrives over the air, nothing to install. The page carries **v1.6.4** now.

### Fixed
- **A born date shown on a card could be missing from Birthdays.** The list is built by `bdOf`, which
  had its own date pattern, while the Born box writes through the forgiving `normDate`. A date that
  arrived any other way - `4 Jul 1950`, `7/4`, `21/7`, from a note, from an older backup - was
  displayed on the person's card and skipped by the list, so Birthdays could be empty, and UJournal
  was handed nothing to find.
- **One reader now.** `bdOf` runs the stored date through `normDate` first: what the page can show,
  it counts. A year on its own, or a month with no day, still has no day to keep.


## 2026-11-06 — v1.6.3: a birthday written as 7/4 counts too"""


def apply(path, pairs):
    text = path.read_text(encoding="utf-8")
    for old, new, done in pairs:
        if done in text:
            continue
        if old not in text:
            raise SystemExit("patch-164: %s: no such text to replace:\n  %r" % (path.name, old[:100]))
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")


def verify():
    problems = []
    page = PAGE.read_text(encoding="utf-8")
    notes = NOTES.read_text(encoding="utf-8")
    if VER_NEW not in page:
        problems.append("the page does not say 1.6.4")
    if '"v":"1.6.4"' not in page:
        problems.append("What is New has no 1.6.4 entry")
    if "const n=normDate(p.birth)" not in page:
        problems.append("bdOf still has a date pattern of its own")
    if "## 2026-11-06 — v1.6.4" not in notes:
        problems.append("PATCH_NOTES has no 1.6.4 entry")
    if problems:
        raise SystemExit("patch-164: " + "; ".join(problems))
    print("1.6.4: bdOf reads through normDate, so a displayed born date is a birthday")


if __name__ == "__main__":
    if "--check" in sys.argv:
        verify()
    else:
        for path, pairs in (
            (PAGE, ((BD_OLD, BD_NEW, "const n=normDate(p.birth)"),
                    (VER_OLD, VER_NEW, VER_NEW),
                    (UPD_OLD, UPD_NEW, '"v":"1.6.4"'))),
            (NOTES, ((NOTE_OLD, NOTE_NEW, "## 2026-11-06 — v1.6.4"),)),
        ):
            apply(path, pairs)
        verify()
