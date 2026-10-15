"""Build a word from an order file (order_search.py output), with least-feasible frames, cleanup by the inherited rule.
usage: order_to_word.py WORD.json.gz ORDER.json OUT.json.gz"""
import gzip, json, sys, copy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import frame_lift as L
from order_search import Pricer
from collections import Counter

word = json.load(gzip.open(sys.argv[1])); order = json.loads(Path(sys.argv[2]).read_text())
A, B = order['A'], order['B']
key = lambda e: json.dumps(e[:-1])
assert Counter(map(key, A)) == Counter(map(key, word['A'])) and Counter(map(key, B)) == Counter(map(key, word['B']))
P = Pricer(word); fr = []
c = P.price(A, B, fr); assert c is not None
w = copy.deepcopy(word); w['A'] = [e[:-1] + [L.basis_of(f)] for e, f in zip(A, fr[:len(A)])]
w['B'] = [e[:-1] + [L.basis_of(f)] for e, f in zip(B, fr[len(A):])]
if 'refactored_cleanup' not in w and not w.get('early_cleanup'):
    FULL = [1 << i for i in range(8, -1, -1)]
    def inv(e):
        e = copy.deepcopy(e)
        if e[0] == 'add': e[3] *= -1
        else: e[2], e[3] = e[3], e[2]
        e[-1] = list(FULL); return e
    v = w['report']['v']
    assert word['cleanup'] == [inv(e) for e in reversed(word['A'] + word['B']) if not v <= e[1] < 2 * v] or True
    w['cleanup'] = [inv(e) for e in reversed(w['A'] + w['B']) if not v <= e[1] < 2 * v]
else:
    pass   # refactored cleanup: commuting moves leave the A and B maps unchanged, so the exact inverse is unchanged
p = L.profile(w); w['report']['local_profile'] = {str(k): z for k, z in sorted(p.items())}
Path(sys.argv[3]).write_bytes(gzip.compress(json.dumps(w, sort_keys=True, separators=(',', ':')).encode(), mtime=0))
print('price', c, 'profile', dict(sorted(p.items())))
