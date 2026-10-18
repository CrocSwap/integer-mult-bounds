"""Step 0 of verify.sh (standard library only): every file of the package matches MANIFEST.sha256 (sha256), none is missing and none is extra.
Prints PASS/FAIL and exits 1 on any mismatch.  usage: python3 provenance.py [--write-manifest]   (the flag is for the authors)
Ignored: __pycache__, *.pyc, .DS_Store, a bin/ directory of compiled programs, and lean/.lake, lean/build (Lean build products)."""
import hashlib, os, sys
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def sha(b): return hashlib.sha256(b).hexdigest()
def listing():
    out = []
    for d, ds, fs in os.walk(PKG):
        ds[:] = sorted(x for x in ds if x not in ('__pycache__', 'bin', '.lake', 'build'))
        for f in fs:
            if f.endswith('.pyc') or f == '.DS_Store': continue
            p = os.path.relpath(os.path.join(d, f), PKG)
            if p != 'MANIFEST.sha256': out.append(p)
    return sorted(out)
if '--write-manifest' in sys.argv:
    with open(os.path.join(PKG, 'MANIFEST.sha256'), 'w') as h:
        for p in listing(): h.write('%s  %s\n' % (sha(open(os.path.join(PKG, p), 'rb').read()), p))
    print('wrote MANIFEST.sha256 (%d files)' % len(listing())); sys.exit(0)
bad = 0; want = {}
try:
    for l in open(os.path.join(PKG, 'MANIFEST.sha256'), encoding='utf-8'):
        h, p = l.rstrip('\n').split('  ', 1); want[p] = h
except OSError:
    print('FAIL 0.manifest MANIFEST.sha256 missing'); sys.exit(1)
have = listing(); n = 0
for p in sorted(set(want) | set(have)):
    f = os.path.join(PKG, p)
    if p not in want: print('FAIL 0.manifest extra file not in MANIFEST: ' + p); bad += 1
    elif not os.path.isfile(f): print('FAIL 0.manifest missing file: ' + p); bad += 1
    elif sha(open(f, 'rb').read()) != want[p]: print('FAIL 0.manifest hash differs: ' + p); bad += 1
    else: n += 1
print('%s 0.manifest  %d files match MANIFEST.sha256' % ('PASS' if not bad else 'FAIL', n), flush=True)
sys.exit(1 if bad else 0)
