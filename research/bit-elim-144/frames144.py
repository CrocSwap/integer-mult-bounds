"""Exact integer bases of every frame the elimination check needs, rebuilt from #144's pinned PR97 sources with
Swapnil Jain's exact machinery (check_lifted.py), exactly as check_frames.py derives them: the chain frames of every
elimination candidate and the output frames t_T^perp.  Stdlib only (~3-4 minutes).
Usage: python3 research/bit-elim-144/frames144.py OUT.json.gz"""
import gzip
import json
import sys
from collections import Counter
from fractions import Fraction
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from elim144 import schedule144  # noqa: E402


def prim(r):
    r = [Fraction(x) for x in r]; den = 1
    for x in r: den = den * x.denominator // gcd(den, x.denominator)
    z = [int(x * den) for x in r]; g = 0
    for x in z: g = gcd(g, x)
    return [x // g for x in z] if g else z


def build():
    dr, W, D, S, selected, omitted, record = schedule144()
    folder = Path(dr.__file__).parent
    sys.path.insert(0, str(folder))
    import check_lifted as cl
    pr = cl.Prog(W); bas, dn = cl.spans(pr); users = cl.users_of(pr, dn)
    fr = cl.Frames(pr, dn, bas, users); fr.cobases(); d, _ = fr.dims(); ld, _ = cl.late_frames(fr, pr, users)
    assert all(S.node_dims[n] == d[n] for n in pr.act)
    _eb = {}
    def ukey(n, k):
        u = users[n][k]; return ('n', u[1]) if u[0] == 'gate' else cl.root_key(u)
    def exact(key):
        if key not in _eb:
            if key[0] == 'c':
                n, lt = key[1], key[2]
                B = exact(ukey(n, lt[-1]))
                for kk in reversed(lt[:-1]): B = fr.intersect_exact(exact(ukey(n, kk)), B)
                B = [prim(r) for r in B]
            else: B = [prim(r) for r in fr.exact_basis(key)]
            assert len(B) == S.dim(key)
            _eb[key] = B
        return _eb[key]
    src = Counter()
    for op in S.ops:
        if op[0] == 'add': src[op[2]] += 1
        elif op[0] == 'fan': src[op[1]] += 1
    want = set()
    for u in S.out:
        if u in S.sel and src[u] == 0:
            for k in S.chain_keys(u):
                if k[0] in ('n', 'c'): want.add(k)
        c, T = S.out[u]; want.add(('out', c, T))
    return {json.dumps(k): exact(k) for k in sorted(want, key=str)}


if __name__ == '__main__':
    out = build()
    with gzip.open(sys.argv[1], 'wt') as f: json.dump(out, f)
    print('exact bases', len(out))
