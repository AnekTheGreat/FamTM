#!/usr/bin/env python3
"""FamTM 1.6.12 - the second birthday sits quietly in the form.

The box came with a paragraph under it explaining itself, and on a phone that paragraph was five
lines of body text sitting in the middle of the form, pushing Notes off the screen. The box says
what it is - "Second birthday", with "as on a passport" where the date goes - so the paragraph is
gone and the row is a row again.

    python3 dev/patch-1612.py            # apply
    python3 dev/patch-1612.py --check    # verify only, writes nothing
"""

import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGE = "app/src/main/assets/index.html"

V = "1.6.12"
OLD = "1.6.11"

FORM_OLD = """ <div class="g2"><label>Second birthday<input id="fb2" value="${h(fmt(p.birth2))}" placeholder="optional"></label><span></span></div><p class="m" style="margin:-2px 0 8px">Only when it is not the same day: the date on a passport or another paper, kept beside the real one. An age is counted from the birthday above, not from this.</p>
"""

FORM_NEW = """ <div class="g2"><label>Second birthday<input id="fb2" value="${h(fmt(p.birth2))}" placeholder="as on a passport"></label><span></span></div>
"""

ENTRY = """{"v":"1.6.12","d":"2026-11-12","t":"The second birthday keeps quiet in the form","x":[\
"The box under Born and Died no longer carries a paragraph under it. On a phone that paragraph was five lines of body text in the middle of the form, pushing Notes and the buttons down behind the keyboard; the label and the hint in the box say the same thing in the space they already take.\
","The box reads <i>Second birthday</i> with <i>as on a passport</i> where the date goes, so an empty box still says what it is for. The date is written the way every other date is - 4 Jul, 7/4/1986, 1986 - and an age is still counted from the real birthday above it.\
"]},"""


def read(rel):
    with io.open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def write(rel, text):
    with io.open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="") as f:
        f.write(text)


def one(text, old, what):
    if text.count(old) != 1:
        sys.exit("patch-1612: %s appears %d times, expected exactly 1" % (what, text.count(old)))
    return text


def patched(page):
    if ("const VER='%s'" % V) in page and 'placeholder="as on a passport"' in page:
        return page
    one(page, "const VER='%s'" % OLD, "the version")
    one(page, FORM_OLD, "the second birthday row")
    one(page, '[{"v":"%s"' % OLD, "the top of the What's New list")
    out = page.replace("const VER='%s'" % OLD, "const VER='%s'" % V, 1)
    out = out.replace(FORM_OLD, FORM_NEW, 1)
    return out.replace('[{"v":"%s"' % OLD, "[" + ENTRY + '{"v":"%s"' % OLD, 1)


def main():
    check = "--check" in sys.argv
    page = read(PAGE)
    new = patched(page)
    if new == page:
        print("already on the page")
        return 0
    if check:
        print("not applied yet")
        return 1
    write(PAGE, new)
    print("page at v%s, the second birthday row without its paragraph" % V)
    return 0


if __name__ == "__main__":
    sys.exit(main())
