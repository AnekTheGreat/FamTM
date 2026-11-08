#!/usr/bin/env python3
"""FamTM 1.6.9 - the Other apps line names all five apps.

    python3 dev/patch-169.py           apply
    python3 dev/patch-169.py --check   exit 1 if it is not in place

The page has carried SideCut, MeasureT, UNote and this app itself for a while, but
the line describing them under Other apps still said three apps, so the page read
as if two of them were missing. This says all five. Idempotent.
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = 'app/src/main/assets/index.html'
VER = '1.6.9'
DATE = '2026-11-08'
TITLE = 'Every app is on the Other apps list'
LINE = " ['Other apps','FamTM, SideCut, MeasureT, UNote and UJournal - My Hub opens them all from one screen.']"
NOTES = [
    'Other apps names every app beside this one: this one, SideCut, MeasureT, UNote and UJournal, with My Hub as the screen that opens them all.',
    'The list itself was already complete - the line that described it was not, and a list that describes itself short reads as a list that is short.',
]


def read(rel):
    return io.open(os.path.join(ROOT, rel), encoding='utf-8').read()


def page_after(page):
    out = re.sub(r"[ ]*\['Other apps','[^']*'\]", lambda m: LINE, page, count=1)
    out = re.sub(r"const VER\s*=\s*'[\d.]+'", "const VER='%s'" % VER, out, count=1)
    m = re.search(r'(<script id="upd" type="application/json">)(.*?)(</script>)', out, re.S)
    if not m:
        raise SystemExit('the changelog block is not where it was')
    try:
        data = json.loads(m.group(2))
    except ValueError:
        raise SystemExit('the changelog is not readable JSON')
    data = [e for e in data if e.get('v') != VER]
    data.insert(0, {'v': VER, 'd': DATE, 't': TITLE, 'x': NOTES})
    out = out[:m.start(2)] + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + out[m.end(2):]
    for must in ('familytree.v1', 'UNote', 'SideCut'):
        if must not in out:
            raise SystemExit('the page lost ' + must + ' - refusing to write it')
    if abs(len(out) - len(page)) > 4000:
        raise SystemExit('the page changed size by more than a line or two - refusing')
    return out


def main():
    path = os.path.join(ROOT, PAGE)
    page = read(PAGE)
    out = page_after(page)
    if '--check' in sys.argv:
        if out == page:
            print('%s is in place' % VER)
            return 0
        print('not applied yet - run python3 dev/patch-169.py')
        return 1
    if out != page:
        io.open(path, 'w', encoding='utf-8', newline='').write(out)
        print('wrote ' + PAGE)
    else:
        print('already applied')
    return 0


if __name__ == '__main__':
    sys.exit(main())
