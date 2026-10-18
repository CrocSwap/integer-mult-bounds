"""pricex.py -- exact bit-c harness for E8 bit words of any port count V (R480 family; helpers enter at frame 0, width 8).
  word  -> local histogram (forward replay exactly as code/eleven/emit.py: MOVE ranks + copy ranks), V, R, cst
  hist  -> per-stage idle windows (eleven-stage: PR #445/#472 recipe generalised to K pairs; nine-stage: the reconstructed 9-window table that
           reproduces R480 s=9 exactly) -> whole-residual hosting by the integer programme (hosting_core.solve, no banks)
        -> profile = L*T*hist + idle remainders -> mass identity check -> exact rational certificate (moment.certify, bad envelope on).
usage:  pricex.py WORD.json.gz [s ...]            (s in 7 9 11 13; default 9 11 13 7)
        pricex.py --hist 'R:{rank:count,..}:V:cst' s ...
Validation targets (run  pricex.py --validate):  R489 s=11 0.001565442026981656908596 ; R480 s=11 0.001574753352953808650916 ; R480 s=9 0.001587447106092548137108"""
import sys, json, gzip, importlib.util, time
from collections import Counter
from fractions import Fraction as Fr
sys.dont_write_bytecode = True
import os
PKG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'e8-bit-carrier-skeleton')   # PR #493's package
sys.path.insert(0, PKG + '/code/hub/idle-axis-hosting')
import hosting_core as HC
_sp = importlib.util.spec_from_file_location('moment', PKG + '/code/pricing/moment.py'); MOM = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(MOM)
H = 8
# ---------------------------------------------------------------- word -> local histogram
def rank_dim(rows):
    rows = [[Fr(x) for x in r] for r in rows]; r = 0
    for c in range(len(rows[0]) if rows else 0):
        p = next((i for i in range(r, len(rows)) if rows[i][c] != 0), None)
        if p is None: continue
        rows[r], rows[p] = rows[p], rows[r]
        for i in range(r + 1, len(rows)):
            if rows[i][c] != 0:
                f = rows[i][c] / rows[r][c]; rows[i] = [a - f * b for a, b in zip(rows[i], rows[r])]
        r += 1
    return r
def word_hist(w):
    """returns dict(V, R, hist, cst, copies, ENT)"""
    V, R, h = w['v'], w['R'], w['h']; assert h == H
    lines = w['lines']; assert len(lines) == V
    dims = [rank_dim([lines[i] for i in idx]) for idx in w['frames']]
    ZERO = [k for k, d in enumerate(dims) if d == 0]; assert len(ZERO) == 1; ZERO = ZERO[0]
    cur = list(w['start']); hist = Counter(); copies = []
    def move(r, f):
        if cur[r] != f:
            d = dims[f] - dims[cur[r]]; assert d >= 0, ('non-nested', r, cur[r], f)
            hist[d] += 1; cur[r] = f
    def run(gates):
        for f, d, srcs in gates:
            for r in [d] + list(srcs): move(r, f)
    run(w['D']); run(w['A'])
    for q in w['ret']:
        rk = dims[cur[q]] - dims[ZERO]; hist[rk] += 1; copies.append(rk)
    run(w['B']); run(w['C'])
    for r in range(len(cur)): move(r, w['final'][r])
    hist.pop(0, None)
    n = len(cur)
    ENT = sum(dims[w['start'][i]] for i in range(2 * V, n))        # = sum (H - width) of helper entrances (0 if all start at frame 0)
    return dict(V=V, R=R, hist=dict(sorted(hist.items())), cst=sum(copies), copies=copies, ENT=ENT, mass=sum(r * c for r, c in hist.items()))
# ---------------------------------------------------------------- schedules / windows
def recipe(K):
    out = [dict(kind='local', stage=0, pair=0)]; stage = 1
    for j in range(K):
        out.append(dict(kind='local', stage=stage, pair=j)); stage += 1
        if j < K - 1: out.append(dict(kind='bridge', dst=j, src=j + 1))
        out.append(dict(kind='local', stage=stage, pair=j)); stage += 1
        if j < K - 1: out.append(dict(kind='bridge', dst=j, src=j + 1))
    for j in reversed(range(K - 1)): out.append(dict(kind='bridge', dst=j + 1, src=j))
    return out
def schedule(K):
    levels = [-1] * K; sched = []; idx = 0
    for e in recipe(K):
        if e['kind'] == 'local':
            s, p = e['stage'], e['pair']; levels[p] = s; sched.append(dict(kind='local', stage=s, pair=p)); idles = []
            if s in range(1, 2 * K - 1, 2): j = (s + 1) // 2; levels[j] = s; idles.append((j, 7 * (s + 1)))
            elif s in range(2, 2 * K, 2): j = s // 2; levels[j] = s; idles.append((j, 7))
            elif s == 2 * K:
                for j in range(K): idles.append((j, 7 * (2 * K - levels[j]))); levels[j] = 2 * K
            for j, r in idles: sched.append(dict(kind='idle', idx=idx, pair=j, rank=r)); idx += 1
        else: sched.append(e)
    return sched
NINE = [(14, (0, 1)), (7, (2,)), (28, (0, 1, 2, 3)), (7, (4,)), (42, tuple(range(6))), (7, (6,)), (42, tuple(range(3, 9))), (28, tuple(range(5, 9))), (14, (7, 8))]
def stage_cfg(s):
    """(K, L, M, T, windows{idx:(pair,rank,stages)}, idle_events[(idx,rank)]).  s=9 uses the reconstructed nine-stage table (T = 32)."""
    if s == 9:
        win = {i: (i, r, frozenset(st)) for i, (r, st) in enumerate(NINE)}
        return 4, 9, 64, 32, win, [(i, r) for i, (r, st) in enumerate(NINE)]
    K = (s - 1) // 2; L = s; M = 7 * s + 1; T = 8
    sch = schedule(K)
    win = {i: x for i, x in HC.windows(sch).items() if x[1] and x[2]}
    idle = [(e['idx'], e['rank']) for e in sch if e['kind'] == 'idle' and e['rank']]
    return K, L, M, T, win, idle
# ---------------------------------------------------------------- pricing
def price(V, R, hist, cst, s, check=True):
    K, L, M, T, win, idle = stage_cfg(s)
    avail = Counter({(st, H): R * T for st in range(L)})
    t0 = time.time()
    try:
        ys, zs, val = HC.solve(win, 2 * V * T, dict(avail), M, pad_value=0.0, group={H: 10 ** 9})
    except AssertionError as e:
        return dict(s=s, feasible=False, why='hosting infeasible: %s' % str(e)[:60])
    used = Counter()
    for (i, wd, st), n in zs.items(): used[st, wd] += n
    if any(used[k] != a for k, a in avail.items()): return dict(s=s, feasible=False, why='unhosted residuals')
    paid = Counter({r: n * L * T for r, n in hist.items() if r})
    hosted = Counter()                                         # remainder per idle window copy
    for i, (r) in idle:
        if i not in win:                                       # window with no residual access: full idle child paid
            paid[r] += 2 * V * T
            continue
        got = Counter()
        for (ii, pat), cnt in ys.items():
            if ii == i: got[r - sum(pat)] += cnt
        assert sum(got.values()) == 2 * V * T, (i, got)
        for rem, cnt in got.items():
            if rem: paid[rem] += cnt
    LIVE = 2 * K * V * T
    mass = sum(r * n for r, n in paid.items())
    gap = M * LIVE - mass - (2 * K * V - L * cst) * T
    if check: assert gap == 0, ('mass identity violated', s, gap)
    cert = MOM.certify(dict(paid), M, LIVE, True)
    return dict(s=s, feasible=True, c=cert['lower'], cf=float(cert['lower']), profile=dict(sorted(paid.items())), gap=gap, R=R, V=V, cst=cst, sec=round(time.time() - t0, 1), M=M, T=T, K=K)
def main():
    a = sys.argv[1:]
    if a and a[0] == '--validate':
        ref = {('R489', 11): '0.001565442026981656908596', ('R480', 11): '0.001574753352953808650916', ('R480', 9): '0.001587447106092548137108'}
        cases = {'R489': (489, {1: 1200, 2: 1440, 4: 180, 6: 120, 8: 18}), 'R480': (480, {1: 1200, 2: 1440, 4: 180, 6: 120, 8: 9})}
        for (name, s), want in ref.items():
            R, h = cases[name]; r = price(120, R, h, 72, s)
            print(name, 's=%d' % s, r['c'][:26], 'want', want, 'EXACT' if r['c'].startswith(want[:24]) else 'DIFF (%s)' % r['c'][:30], 'profile', r['profile'], flush=True)
        return
    if a and a[0] == '--hist':
        R, rest0 = a[1].split(':', 1); h, V, cst = rest0.rsplit(':', 2); hist = {int(k): v for k, v in json.loads(h).items()}; rest = a[2:]
        d = dict(V=int(V), R=int(R), hist=hist, cst=int(cst))
    else:
        w = json.loads(gzip.open(a[0], 'rt').read()); d = word_hist(w); rest = a[1:]
        print('word: V=%d R=%d cst=%d local hist %s ENT=%d mass %d' % (d['V'], d['R'], d['cst'], d['hist'], d['ENT'], d['mass']))
        assert d['ENT'] == 0
        assert d['mass'] == H * d['R'] + d['cst'] + 2 * d['V'] * (H - 1), 'local mass identity'
    for s in (list(map(int, rest)) or [9, 11, 13, 7]):
        r = price(d['V'], d['R'], d['hist'], d['cst'], s)
        print(json.dumps(r), flush=True)
if __name__ == '__main__': main()
