"""Min-diff helper: copy per-class mindiff_cls2.py results from an old cache to a new one for every changed class whose
stage-1 (x, y) is the same in the old and the new mindiff_cls1.py solution. Standard library only.
argv: OLD_STAGE1_JSON NEW_STAGE1_JSON OLD_CACHE NEW_CACHE"""
import sys, json, os, shutil
from collections import Counter
a, b, ca, cb = sys.argv[1:5]; A1 = json.load(open(a)); B1 = json.load(open(b)); os.makedirs(cb, exist_ok=True)
def key(d, ci): return (sorted((tuple(p), v) for c, p, v in d['x'] if c == ci), sorted((t, w, v) for c, t, w, v in d['y'] if c == ci))
n = 0
for ci in B1['changed']:
    f = f'{ca}/{ci}.json'
    if ci in A1['changed'] and key(A1, ci) == key(B1, ci) and os.path.exists(f):
        d = json.load(open(f)); ny = sum(v for c, t, w, v in B1['y'] if c == ci)
        if len(d['triples']) == ny: shutil.copy(f, f'{cb}/{ci}.json'); n += 1
print('reused', n, 'of', len(B1['changed']), 'changed classes')
