"""Step 0 of verify.sh (standard library only).  Prints one PASS/FAIL line per group and exits 1 on any mismatch.
  0.manifest  every file of the package matches MANIFEST.sha256 (sha256), none is missing and none is extra
  0.sources   every pin of SOURCES.json holds: the sha256 of each pinned package file (checks and libraries)
usage: python3 provenance.py [--write-manifest]   (--write-manifest is for the authors: it rewrites MANIFEST.sha256; SOURCES.json is written by --write-sources)"""
import hashlib, json, os, sys
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bad = 0
def sha(b): return hashlib.sha256(b).hexdigest()
def listing():
    out = []
    for d, ds, fs in os.walk(PKG):
        ds[:] = sorted(x for x in ds if x != '__pycache__' and x != 'bin')
        for f in fs:
            if f.endswith('.pyc') or f == '.DS_Store': continue
            p = os.path.relpath(os.path.join(d, f), PKG)
            if p != 'MANIFEST.sha256': out.append(p)
    return sorted(out)
if '--write-manifest' in sys.argv:
    with open(os.path.join(PKG, 'MANIFEST.sha256'), 'w') as h:
        for p in listing(): h.write('%s  %s\n' % (sha(open(os.path.join(PKG, p), 'rb').read()), p))
    print('wrote MANIFEST.sha256 (%d files)' % len(listing())); sys.exit(0)
if '--write-sources' in sys.argv:
    S = json.load(open(os.path.join(PKG, 'SOURCES.json')))
    for sect in ('files', 'evidence'):
        for e in S[sect]: e['sha256'] = sha(open(os.path.join(PKG, e['file']), 'rb').read())
    json.dump(S, open(os.path.join(PKG, 'SOURCES.json'), 'w'), indent=1); print('wrote SOURCES.json pins'); sys.exit(0)
want = {}
for l in open(os.path.join(PKG, 'MANIFEST.sha256'), encoding='utf-8'):
    h, p = l.rstrip('\n').split('  ', 1); want[p] = h
have = listing(); n = 0
for p in sorted(set(want) | set(have)):
    f = os.path.join(PKG, p)
    if p not in want: print('FAIL 0.manifest extra file not in MANIFEST: ' + p); bad += 1
    elif not os.path.isfile(f): print('FAIL 0.manifest missing file: ' + p); bad += 1
    elif sha(open(f, 'rb').read()) != want[p]: print('FAIL 0.manifest hash differs: ' + p); bad += 1
    else: n += 1
print('%s 0.manifest  %d files match MANIFEST.sha256' % ('PASS' if not bad else 'FAIL', n), flush=True)
S = json.load(open(os.path.join(PKG, 'SOURCES.json'))); b0 = bad; k = 0
for sect in ('files', 'evidence'):
    for e in S[sect]:
        k += 1; f = os.path.join(PKG, e['file'])
        if not os.path.isfile(f): print('FAIL 0.sources missing ' + e['file']); bad += 1
        elif sha(open(f, 'rb').read()) != e['sha256']: print('FAIL 0.sources pin differs: ' + e['file']); bad += 1
print('%s 0.sources  %d pins hold (checks and libraries)' % ('PASS' if bad == b0 else 'FAIL', k - (bad - b0)), flush=True)
sys.exit(1 if bad else 0)
