"""Frame-only optimality check for the selected #626 complex provider words (jp8, ck).

For each word: check its content hash against the pin in complex-k492-owner-repair/data/SPEC.json, recompute the
native paid profile, price the greatest feasible frame lift, and solve the local-polytope LP over every feasible
frame assignment of the fixed gate sequence (frame_lp.py). Writes a JSON receipt.

usage: check.py --work REPLAY_COMPLEX_DIR --out RESULT.json
       (REPLAY_COMPLEX_DIR is the 'complex' directory of `make frontier626-verify`, or of
        research/complex-k492-owner-repair/verify.py --work DIR)
"""
import argparse, gzip, hashlib, json, sys
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import frame_lift as L
from least import least
from frame_exact import interval

ROOT = HERE.parents[1]
SPEC = ROOT / 'research/complex-k492-owner-repair/data/SPEC.json'
WORDS = {'jp8': 'jp8-step6-cold_end/FULL-WORD.json.gz', 'ck': 'ck-step7-cold_end/FULL-WORD.json.gz'}


def chain_terms(word):
    ch = L.chains(word); G, orig = L.greatest(word); lo, pos = least(word, ch, len(orig))
    assert all(a & ~b == 0 for a, b in zip(lo, orig)) and all(a & ~b == 0 for a, b in zip(orig, G))
    return ch, G, orig, lo


def chain_weight(ch, X):
    c = 0.0
    for chain in ch:
        vals = [X[x] if k == 'g' else x for k, x in chain if k != 'cap']
        c += sum(L.W(L.dim(b) - L.dim(a)) for a, b in zip(vals, vals[1:]) if a != b)
    return c


def lp_bound(ch, dom):
    idx = {}; c = []; ub = []
    def var(key, cost):
        idx[key] = len(c); c.append(cost); ub.append(1.0); return idx[key]
    for g, d in enumerate(dom):
        for s in d: var(('x', g, s), 0.0)
    rows, cols, vals, rhs = [], [], [], []; r = 0
    for g, d in enumerate(dom):
        for s in d: rows.append(r); cols.append(idx['x', g, s]); vals.append(1.0)
        rhs.append(1.0); r += 1
    const = 0.0
    for reg, chain in enumerate(ch):
        nodes = [nd for nd in chain if nd[0] != 'cap']
        for (k1, v1), (k2, v2) in zip(nodes, nodes[1:]):
            if k1 != 'g' and k2 != 'g':
                if v1 != v2: const += L.W(L.dim(v2) - L.dim(v1))
                continue
            if k1 != 'g':
                for s in dom[v2]:
                    j = idx['x', v2, s]
                    if v1 & ~s: ub[j] = 0.0
                    elif s != v1: c[j] += L.W(L.dim(s) - L.dim(v1))
                continue
            if k2 != 'g':
                for s in dom[v1]:
                    j = idx['x', v1, s]
                    if s & ~v2 or (k2 == 'a' and s != v2): ub[j] = 0.0
                    elif s != v2: c[j] += L.W(L.dim(v2) - L.dim(s))
                continue
            if v1 == v2: continue
            pv = {(s, t): var(('y', reg, v1, v2, s, t), L.W(L.dim(t) - L.dim(s)) if s != t else 0.0)
                  for s in dom[v1] for t in dom[v2] if s & ~t == 0}
            for s in dom[v1]:
                for (s2, _), j in pv.items():
                    if s2 == s: rows.append(r); cols.append(j); vals.append(1.0)
                rows.append(r); cols.append(idx['x', v1, s]); vals.append(-1.0); rhs.append(0.0); r += 1
            for t in dom[v2]:
                for (_, t2), j in pv.items():
                    if t2 == t: rows.append(r); cols.append(j); vals.append(1.0)
                rows.append(r); cols.append(idx['x', v2, t]); vals.append(-1.0); rhs.append(0.0); r += 1
    A = coo_matrix((vals, (rows, cols)), shape=(r, len(c))).tocsr()
    res = linprog(np.array(c), A_eq=A, b_eq=np.array(rhs), bounds=list(zip([0.0] * len(c), ub)), method='highs')
    assert res.status == 0, res.message
    return res.fun + const, len(c), r


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--work', type=Path, required=True); ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    spec = SPEC.read_text(); out = {}
    for pid, rel in WORDS.items():
        raw = json.load(gzip.open(a.work / rel))
        sha = hashlib.sha256(json.dumps(raw, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        assert sha in spec, (pid, 'word content hash is not pinned in SPEC.json', sha)
        prof = L.profile(raw)
        expected = json.loads(spec)['providers'][pid]['expected_profile']
        assert {str(k): n for k, n in sorted(prof.items())} == expected, (pid, prof)
        ch, G, orig, lo = chain_terms(raw)
        dom = [interval(l, g) for l, g in zip(lo, G)]
        L.EXACT = True
        x_in = chain_weight(ch, orig); x_bound, _, _ = lp_bound(ch, dom)
        L.EXACT = False
        w_in = chain_weight(ch, orig); w_great = chain_weight(ch, G)
        bound, nv, nr = lp_bound(ch, dom)
        gp = L.profile(raw, G)
        out[pid] = dict(content_sha256=sha, paid_profile={str(k): n for k, n in sorted(prof.items())},
                        gates=len(orig), domain_sizes={str(k): v for k, v in sorted(__import__('collections').Counter(map(len, dom)).items())},
                        input_chain_weight='%.9f' % w_in, lp_lower_bound='%.9f' % bound, lp_gap='%.3e' % (w_in - bound),
                        lp_variables=nv, lp_rows=nr,
                        exact_root_input_weight='%.9f' % x_in, exact_root_lp_optimum='%.9f' % x_bound, exact_root_lp_gap='%.3e' % (x_in - x_bound),
                        greatest_lift_profile={str(k): n for k, n in sorted(gp.items())}, greatest_lift_chain_weight='%.9f' % w_great)
        print(pid, json.dumps(out[pid]), flush=True)
        assert w_in - bound < 1e-3 and x_in - x_bound < 1e-3, (pid, 'LP bound below the input weight: a frame-only improvement may exist')
    out['status'] = 'PASS_FRAME_ONLY_LP_OPTIMAL_FOR_SELECTED_PROVIDERS'
    out['objective'] = ('linear: sum over paid climbs of d*ln(48/d) (a->0 recurrence weight); exact_root: sum of '
                        'd*((73/d)^a*-(73/48)^a*)/a* at the selected complex root a*, which (rank mass fixed per word) '
                        'decreases iff the complex root increases')
    out['scope'] = ('Relaxation of the native audit (hpe cone caps and cold_end allowlist conditions omitted, tail frames free); '
                    'fixed gate sequence; HiGHS floating LP, not an exact rational certificate.')
    a.out.write_text(json.dumps(out, indent=2) + '\n')


if __name__ == '__main__':
    main()
