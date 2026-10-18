"""Shared helpers of bundle B checks (standard library only). Inputs are read from ../inputs relative to the package root."""
import gzip, hashlib, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INP = os.path.join(ROOT, 'inputs')
FAILS = []
def path(*p): return os.path.join(INP, *p)
def load_json(*p):
    f = path(*p)
    with (gzip.open(f) if f.endswith('.gz') else open(f, 'rb')) as h: return json.load(h)
def raw(*p):
    f = path(*p)
    with open(f, 'rb') as h: b = h.read()
    return gzip.decompress(b) if f.endswith('.gz') else b
def blob_id(b): return hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest()
def content_sha(obj): return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def check(name, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ') + name + (' | ' + str(detail) if detail != '' else ''), flush=True)
    if not ok: FAILS.append(name)
def finish():
    if FAILS:
        print('FAILED: %d' % len(FAILS)); sys.exit(1)
