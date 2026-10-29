#!/usr/bin/env python3
"""Step 0: every file listed in MANIFEST.sha256 exists with the recorded hash; no unlisted file."""
import hashlib, os, sys
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
listed = {}
for line in open(os.path.join(R, 'MANIFEST.sha256')):
    h, p = line.rstrip('\n').split('  ', 1); listed[p] = h
bad = 0
for p, h in listed.items():
    f = os.path.join(R, p)
    if not os.path.isfile(f): print('FAIL missing', p); bad += 1; continue
    if hashlib.sha256(open(f, 'rb').read()).hexdigest() != h: print('FAIL hash', p); bad += 1
for d, _, fs in os.walk(R):
    for n in fs:
        p = os.path.relpath(os.path.join(d, n), R)
        if p != 'MANIFEST.sha256' and p not in listed and '__pycache__' not in p: print('FAIL unlisted', p); bad += 1
print('FAIL manifest' if bad else 'PASS manifest: %d files pinned' % len(listed))
sys.exit(1 if bad else 0)
