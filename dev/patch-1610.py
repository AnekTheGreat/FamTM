#!/usr/bin/env python3
"""FamTM 1.6.10 - My Hub belongs on the list, and every row answers.

1.6.9's note said the Other apps list named "this one, SideCut, MeasureT, UNote and UJournal, with My
Hub as the screen that opens them all" - but the list itself had no My Hub row, so the app the note
called the screen was the one app you could not open from it.

Every row also went to a Play listing, and four of the five packages in this family are not on Play
at all yet: the page they opened answered with Play's not-found. This makes the list the one the
whole family carries - FamTM, SideCut, MeasureT, UJournal and UNote beside this one, each with a
line, each at an address that answers today.

    python3 dev/patch-1610.py            # apply
    python3 dev/patch-1610.py --check    # verify only, writes nothing
"""

import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGE = "app/src/main/assets/index.html"

V = "1.6.10"
OLD = "1.6.9"

APPS_NEW = r"""const APPS=[
 ['My Hub','One screen that launches the rest, and keeps each one up to date.','https://github.com/AnekTheGreat/My-Hub/releases/latest'],
 ['SideCut','A music player with its own equaliser.','https://play.google.com/store/apps/details?id=com.SideCut.myapp'],
 ['MeasureT','Elevation, location, a level and a converter.','https://anekthegreat.github.io/Compass-EDC/'],
 ['UJournal','Keeps the days you write down, and marks the birthdays this family hands over.','https://github.com/AnekTheGreat/Journal/releases/latest'],
 ['UNote','Notes that link themselves, with a Vault behind a PIN.','https://anekthegreat.github.io/UNote/'],
 ['FamTM','This app: the family tree in your pocket.','https://github.com/AnekTheGreat/FamTM/releases/latest']
];"""

APPS_COMMENT_OLD = ("// The apps worth pointing at, one line each, and where each one is installed from: a Play listing,\n"
                    "// public and on this account, so a link in here can never point at something that is not there.")

APPS_COMMENT_NEW = ("// The apps worth pointing at, one line each, and where each one is installed from. Only SideCut is\n"
                    "// on Play: the rest open the release or the page the app installs from, so no row is a page\n"
                    "// that answers not-found.")

GUIDE_OLD = "['Other apps','FamTM, SideCut, MeasureT, UNote and UJournal - My Hub opens them all from one screen.']"
GUIDE_NEW = "['Other apps','SideCut, MeasureT, UJournal, UNote and My Hub - the rest of the shelf, and My Hub opens them all from one screen.']"

ENTRY = r"""{"v":"1.6.10","d":"2026-11-08","t":"My Hub is on the list, and every row answers","x":["Other apps now carries My Hub as well: SideCut, MeasureT, UJournal, UNote and My Hub, the same five rows in the same order the other apps use.","Four of the five store pages the list pointed at are not up yet, so those rows opened Play's not-found page. FamTM and UJournal now open the release they install from, MeasureT and UNote open their own page, and SideCut keeps its live listing.","Every row says one line about the app, so the shelf reads the same here as it does in the others."]},"""


def read(rel):
    with io.open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def write(rel, text):
    with io.open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="") as f:
        f.write(text)


def main():
    check = "--check" in sys.argv
    page = read(PAGE)
    touched = []

    if APPS_NEW not in page:
        if "const APPS=[" not in page:
            sys.exit("the page has no APPS list")
        i = page.index("const APPS=[")
        j = page.index("];", i) + 2
        page = page[:i] + APPS_NEW + page[j:]
        touched.append("the Other apps list")

    if APPS_COMMENT_NEW not in page and APPS_COMMENT_OLD in page:
        page = page.replace(APPS_COMMENT_OLD, APPS_COMMENT_NEW, 1)
        touched.append("the comment over the list")

    if GUIDE_NEW not in page:
        if GUIDE_OLD not in page:
            sys.exit("the guide line is neither the old one nor the new one")
        page = page.replace(GUIDE_OLD, GUIDE_NEW, 1)
        touched.append("the guide line")

    if "const VER='%s'" % V not in page:
        if "const VER='%s'" % OLD not in page:
            sys.exit("the page does not say %s" % OLD)
        page = page.replace("const VER='%s'" % OLD, "const VER='%s'" % V, 1)
        if '[{"v":"%s"' % OLD in page:
            page = page.replace('[{"v":"%s"' % OLD, "[" + ENTRY + '{"v":"%s"' % OLD, 1)
        else:
            sys.exit("the changelog does not start at %s" % OLD)
        touched.append("the version and the changelog")

    listed = page.split("const APPS=[")[1].split("];")[0] if "const APPS=[" in page else ""
    probes = [
        (APPS_NEW in page, "the six rows are not in the page"),
        ("My Hub" in listed, "My Hub is not on the list"),
        ("Compass EDC" not in listed, "the list still calls MeasureT Compass EDC"),
        (GUIDE_NEW in page, "the guide line still names the old five"),
        (page.count("https://play.google.com/store/apps/details?id=") == 1,
         "a row still points at a Play listing that is not there"),
        ("github.com/AnekTheGreat/My-Hub/releases/latest" in listed, "My Hub has no address"),
        ("github.com/AnekTheGreat/Journal/releases/latest" in listed, "UJournal has no address"),
        ("anekthegreat.github.io/Compass-EDC/" in listed, "MeasureT has no address"),
        ("anekthegreat.github.io/UNote/" in listed, "UNote has no address"),
        ("const VER='%s'" % V in page, "the page does not say %s" % V),
        ('{"v":"%s"' % V in page, "the changelog has no %s entry" % V),
        ("familytree.v1" in page, "the page lost its familytree.v1 marker"),
    ]
    bad = [why for ok, why in probes if not ok]
    if bad:
        sys.exit("; ".join(bad))

    if check:
        print("all %d checks pass - the tree carries FamTM %s" % (len(probes), V))
        print("untouched this run" if not touched else "applied: " + ", ".join(touched))
        return

    write(PAGE, page)
    print("FamTM %s written to the page" % V)
    print("next: the apply workflow commits it, then release.yml for %s" % V)


if __name__ == "__main__":
    main()
