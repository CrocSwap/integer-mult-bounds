"""Literal scalar replay of #144's bit word after terminal elimination, over Z (exact integer readout coefficients)
and over F2, with arbitrary scratch and data (stdlib only).  Mirrors Swapnil Jain's check_word.py part D with #144's
read placement: every non-selected slot (non-deferred and the 2,022 omitted) is read in the zero prelude, the
selected slots after phase 1 in readout order; V gates keep the inherited early/late placement.  Eliminated slots:
their reads, output reads, inverse writes and V^-1 are deleted; every forward write into them goes to their target.
Expected: every slot restored and y_T = y_T(0) + (definition sums) over Z, y_T += x_T over F2.  Tamper controls (a
missing redirected update, a sign-flipped redirected update) must break the Z identity.
Usage: python3 research/bit-elim-144/replay144.py PLAN.json"""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from elim144 import schedule144  # noqa: E402


def main():
    plan = json.loads(Path(sys.argv[1]).read_text()); elim = set(plan['elim'])
    dr, W, D, S, selected, omitted, record = schedule144()
    orig_sel = set(S.sel); chosen = set(selected)
    trip, v, R, ops = S.trip, S.v, S.R, S.ops
    CZ = S.adjoint(); CF = [{t: 1 for t, c in d.items() if c % 2} for d in CZ]
    target_of = {u: S.tid[S.out[u][1]] for u in elim}
    prev = {}; pred = defaultdict(list); last = {}
    for i, op in enumerate(ops):
        for s in S.touch(op):
            if s in prev: pred[i].append(prev[s])
            prev[s] = i; last[s] = i
    Anc = set(); st = [last[s] for s in S.ret]
    while st:
        i = st.pop()
        if i in Anc: continue
        Anc.add(i); st.extend(pred[i])
    assert not any(set(S.touch(ops[i])) & orig_sel for i in Anc)
    ph1 = [i for i in range(len(ops)) if i in Anc and ops[i][0] != 'src']
    rest = [i for i in range(len(ops)) if i not in Anc and ops[i][0] != 'src']
    srcop = S.srcop
    early_V = sorted(set(srcop) - orig_sel, key=lambda s: (srcop[s], len(S.vstart[s]), s))
    outputs = {(c, tuple(T)): n for c, T, n in W['outputs']}
    def expected(x):
        want = [0] * v
        for (c, T), n in outputs.items():
            A_, B_ = [q for q in T if q != c]
            want[S.tid[T]] += sum(x[i] for i, Sx in enumerate(trip) if c in Sx and A_ not in Sx and B_ not in Sx)
        for c in range(S.h):
            tot = sum(x[i] for i, Sx in enumerate(trip) if c in Sx)
            for t, T in enumerate(trip):
                if c in T: want[t] += tot
        return want
    def word(ring, rng, tamper=None):
        mod = (lambda z: z & 1) if ring == 2 else (lambda z: z)
        co = CF if ring == 2 else CZ
        x = [rng.randrange(-10**6, 10**6) for _ in range(v)]
        a0 = [rng.randrange(-10**6, 10**6) for _ in range(R)]; y0 = [rng.randrange(-10**6, 10**6) for _ in range(v)]
        a = list(a0); y = list(y0); seen = [0]
        def redirected(t, value):
            seen[0] += 1
            if tamper == 'missing' and seen[0] == 1: return
            y[t] += (-value if tamper == 'sign' and seen[0] == 1 else value)
        def readout(s):
            for t, c in co[s].items(): y[t] -= c * a[s]
        for s in range(R):
            if s not in chosen and s not in elim: readout(s)          # zero prelude: non-deferred and omitted reads
        for s in early_V: a[s] += x[srcop[s] - 1]
        def runop(i, sign=1):
            op = ops[i]
            if op[0] == 'add':
                if op[1] in elim:
                    if sign == 1: redirected(target_of[op[1]], a[op[2]])
                    return
                a[op[1]] += sign * a[op[2]]
            elif op[0] == 'fan':
                for g in op[2]:
                    if g in elim:
                        if sign == 1: redirected(target_of[g], a[op[1]])
                        continue
                    a[g] += sign * a[op[1]]
        for i in ph1: runop(i)
        for s, c in S.ret.items():
            for t, T in enumerate(trip):
                if c in T: y[t] += a[s]
        for s in selected:
            if s not in elim: readout(s)
        for s in S.late_v:
            if s in elim: redirected(target_of[s], x[srcop[s] - 1])
            else: a[s] += x[srcop[s] - 1]
        for i in rest: runop(i)
        for s, (c, T) in S.out.items():
            if s not in elim: y[S.tid[T]] += a[s]
        for i in reversed(ph1 + rest): runop(i, -1)
        for s, n in srcop.items():
            if s not in elim: a[s] -= x[n - 1]
        if any(mod(a[s] - a0[s]) for s in range(R) if s not in elim): return False
        want = expected(x)
        if any(mod(y[t] - y0[t] - want[t]) for t in range(v)): return False
        if ring == 2 and any(mod(y[t] - y0[t] - x[t]) for t in range(v)): return False
        return True
    rng = random.Random(20261009)
    okF = all(word(2, rng) for _ in range(3)); okZ = word(0, rng)
    print('F2 replay (3 random scratch/data): %s; Z replay (exact integer coefficients): %s' % (okF, okZ))
    tm = not word(0, rng, 'missing'); ts = not word(0, rng, 'sign')
    print('tamper controls rejected: missing redirected update %s, sign-flipped redirected update %s' % (tm, ts))
    assert okF and okZ and tm and ts
    print('PASS literal scalar replay of the reduced word (%d eliminated, %d slots remain)' % (len(elim), R - len(elim)))


if __name__ == '__main__':
    main()
