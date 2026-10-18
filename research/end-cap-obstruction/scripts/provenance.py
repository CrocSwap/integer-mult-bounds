"""Step 0 of verify.sh (standard library only).  Prints one PASS/FAIL line per group and exits 1 on any mismatch.
  0.manifest  every file of the package matches MANIFEST.sha256 (sha256), none is missing and none is extra
  0.sources   every entry of SOURCES.json matches its pin: sha256 of the stored file; for copies of repository files also the git blob id
              of the source file; for the rebuilt #1018 word the sha256 of its canonical JSON, which must also equal the word hash that the
              vendored #1018 file SLOT-PINS-k8.json publishes (key 'published_key')
usage: python3 provenance.py [--write-manifest]   (--write-manifest is for the authors: it rewrites MANIFEST.sha256)"""
import gzip, hashlib, json, os, sys
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bad = 0
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest()
def listing():
    out = []
    for d, ds, fs in os.walk(PKG):
        ds[:] = sorted(x for x in ds if x != '__pycache__')
        for f in fs:
            if f.endswith('.pyc'): continue
            p = os.path.relpath(os.path.join(d, f), PKG)
            if p != 'MANIFEST.sha256': out.append(p)
    return sorted(out)
if '--write-manifest' in sys.argv:
    with open(os.path.join(PKG, 'MANIFEST.sha256'), 'w') as h:
        for p in listing(): h.write('%s  %s\n' % (sha(open(os.path.join(PKG, p), 'rb').read()), p))
    print('wrote MANIFEST.sha256 (%d files)' % len(listing())); sys.exit(0)
# 0.manifest
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
# 0.sources
S = json.load(open(os.path.join(PKG, 'SOURCES.json'))); b0 = bad; k = 0
for sect in ('files', 'derived', 'evidence'):
    for e in S[sect]:
        k += 1; f = os.path.join(PKG, e['file'])
        if not os.path.isfile(f): print('FAIL 0.sources missing ' + e['file']); bad += 1; continue
        raw = open(f, 'rb').read(); ok = sha(raw) == e['sha256']
        src = gzip.decompress(raw) if e['file'].endswith('.gz') and not e.get('source_path', '').endswith('.gz') else raw
        if 'blob' in e: ok = ok and blob(src) == e['blob']
        if 'bytes_sha256' in e: ok = ok and hashlib.sha256(src).hexdigest() == e['bytes_sha256']
        if 'content_sha256' in e:
            c = hashlib.sha256(json.dumps(json.loads(src), sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            ok = ok and c == e['content_sha256']
        if 'published_in' in e:
            pub = json.load(open(os.path.join(PKG, e['published_in'])))[e['published_key']]
            if pub != e['content_sha256']: print('FAIL 0.sources published hash differs: ' + e['file']); bad += 1
        if not ok: print('FAIL 0.sources pin differs: ' + e['file']); bad += 1
print('%s 0.sources  %d pinned files match SOURCES.json (blob ids / sha256 / content sha256)' % ('PASS' if bad == b0 else 'FAIL', k), flush=True)
sys.exit(1 if bad else 0)
