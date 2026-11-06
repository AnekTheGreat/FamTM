#!/usr/bin/env python3
"""FamTM 1.6.3 - a birthday stored without zeroes is still a birthday.

[bdOf] read only the padded form the date field writes - 1950-07-04 or --07-04 - so a birth date
kept in any other shape (1950-7-4, 7/4, a backup made by hand, a record from before the padding) was
silently dropped from the birthday list. The list the phone hands to UJournal is built from that
same function, so a family whose dates are written that way published an empty list while Birthdays
in this app looked fully populated.

The function now reads one- or two-digit months and days, with or without a year, and still refuses
anything without a day to keep (1950, 1950-07).

Page only: it reaches an installed copy over the air, and the version moves to 1.6.3 so the notes
say what changed.

Usage: python3 dev/patch-163.py [--check]
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "app/src/main/assets/index.html"
NOTES = ROOT / "PATCH_NOTES.md"

BD_OLD = """const bdOf=p=>{const m=/^(?:([0-9]{4})-|--)([0-9]{2})-([0-9]{2})$/.exec(str(p.birth));if(!m)return null;
 const mo=+m[2],d=+m[3];return mo>=1&&mo<=12&&d>=1&&d<=31?{mo,d,y:m[1]?+m[1]:0}:null};"""

BD_NEW = """// 1.6.3 - a date is read however it was written. The old pattern wanted the padded shape the form
// writes (1950-07-04 or --07-04) and quietly dropped anything else: 1950-7-4, 7/4, a hand-made backup.
// The list handed to UJournal is made from this function, so those people were missing from it while
// Birthdays here showed them. A year or a month with no day still has no day to keep and is skipped.
const bdOf=p=>{const m=/^(?:([0-9]{4})[-/]|--)?([0-9]{1,2})[-/]([0-9]{1,2})$/.exec(str(p.birth).trim());if(!m)return null;
 const mo=+m[2],d=+m[3];return mo>=1&&mo<=12&&d>=1&&d<=31?{mo,d,y:m[1]?+m[1]:0}:null};"""

UPD = '[{"v":"1.6.3","d":"2026-11-06","t":"A birthday written as 7/4 counts too","x":["The list this app hands to UJournal was dropping people whose born date was not written in the padded form the date field produces. A date kept as 1950-7-4, or as 7/4, or one that came in from a hand-made backup, was skipped silently - so the journal could be told there was nobody with a birthday while Birthdays here showed a full list.","It is read however it is written now: one- or two-digit month and day, with or without a year, and with a dash or a slash. A year on its own, or a month without a day, still has no day to keep, so it is still left out - and Birthdays says so.","The screen arrived with this; nothing to install."]},'

NOTE = '''## 2026-11-06 — v1.6.3: a birthday written as 7/4 counts too

A page change: it arrives over the air, nothing to install. The page carries **v1.6.3** now.

### Fixed
- **The birthday list dropped dates that were not zero-padded.** The function that reads a born date
  wanted the exact shape the date field writes, `1950-07-04` or `--07-04`, and returned nothing for
  `1950-7-4`, `7/4` or a date from a hand-made backup. The list handed to UJournal is built from the
  same function, so UJournal was told there were no birthdays while Birthdays in this app showed a
  full list. One- or two-digit months and days are read now, with a dash or a slash, with or without
  a year.
- **A year or a month without a day is still skipped**, because there is no day to come round again.
  Birthdays already says so under the list.

### Unchanged
- The provider, the reminders and the family tree are untouched; only the reader of a date changed.


'''


def edit(path, pairs):
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if old not in text:
            raise SystemExit("patch-163: %s: no such text to replace:\n  %r" % (path.name, old[:90]))
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")


def main():
    check = "--check" in sys.argv
    page = PAGE.read_text(encoding="utf-8")
    done = (
        "const VER='1.6.3'" in page
        and '{"v":"1.6.3"' in page
        and "[0-9]{1,2})[-/]([0-9]{1,2})" in page
        and "## 2026-11-06 — v1.6.3" in NOTES.read_text(encoding="utf-8")
    )
    if check:
        print("1.6.3 already applied" if done else "1.6.3 not applied yet")
        return 0 if done else 1
    if done:
        print("1.6.3 already applied - nothing to do")
        return 0

    edit(PAGE, [
        ("const VER='1.6.2'", "const VER='1.6.3'"),
        (BD_OLD, BD_NEW),
        ('<script id="upd" type="application/json">[{"v":"1.6.2",', '<script id="upd" type="application/json">' + UPD + '{"v":"1.6.2",'),
    ])
    edit(NOTES, [('## 2026-11-06 — v1.6.2:', NOTE + '## 2026-11-06 — v1.6.2:')])

    print("1.6.3 applied: bdOf reads 7/4 and 1950-7-4, notes written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
