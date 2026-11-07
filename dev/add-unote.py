#!/usr/bin/env python3
"""UNote joins FamTM's Other apps list.

Run from the repository root: python3 dev/add-unote.py
--check reports without writing, and a second run is a no-op.
"""
import io
import sys

PAGE = 'app/src/main/assets/index.html'
URL = 'https://site-e28e804444934263a1f0838974d59f45.freebuff.page/'
lines = io.open(PAGE, encoding='utf-8').read().split('\n')

if any("'UNote'" in l for l in lines):
    print('UNote is already in the list - nothing to do')
    sys.exit(0)

if '--check' in sys.argv:
    print('UNote is NOT in the list - it needs applying')
    sys.exit(1)

i = next(i for i, l in enumerate(lines) if l.startswith(" ['FamTM','This app"))
lines.insert(i, " ['UNote','Notes that link themselves, with a Vault behind a PIN.','%s']," % URL)

io.open(PAGE, 'w', encoding='utf-8').write('\n'.join(lines))
print('added the UNote line to APPS')
