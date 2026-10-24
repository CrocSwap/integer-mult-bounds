#!/usr/bin/env python3
"""Owned-centre wire floor on the #4470 native word (answers #4534's retiming question; no new kappa).

#4534 (research/frame-aware-native, OWNED-C-RETIMING.md) allows the chart of every scalar contact,
including the owned C register, to be retimed provided every C transition is paid.  This script asks
whether that freedom can make the eight rank-8 centre transports of #4470 cheaper.

Model (as native.synthesize / joint-helper-lattice): chronological scalar order, coefficients, warps
and helper entrances/exits are fixed.  A persistent L role only climbs along nested frames (rank =
dimension difference).  The owned C wire may move along nested frames in either direction (rank =
|dimension difference|); the original centre is such a move (8 -> 0 forward, 0 -> 8 backward), and
after CLEAR its chart is free.  Non-nested C transitions are outside this model.

Checks:
1. Rebuild #4470's word with joint-helper-lattice/native_joint.construct and recover its complete
   local paid profile {1:2237,2:388,3:494,4:147,5:36,8:8} from contact charts in both orientations.
2. Centre structure: per orientation 8 blocks, each one source contact (copy / its dual), 22 target
   contacts in frame 0 and one rank-8 C transport.
3. Interval propagation over every scalar contact of every L role (any legal retiming): a forward
   pass gives the lowest possible chart of each contact (join of participants' running lower bounds,
   reset by warp outputs), a backward pass the highest (meet of running upper bounds, reset by warp
   inputs and final frames).  Every contact is consistent (low <= up).
4. Floor (PROOF.md): for a nested C path g_0 -> g_1 -> ... -> g_n the paid mass is at least
   dim g_0 - dim(g_0 & g_1 & ... & g_n).  With g_0 >= Low(source) and g_i <= Up(target i), and
   Low(source) & Up(t_1) & ... & Up(t_22) = 0, every block pays C mass >= dim Low(source) = 8, in both
   orientations; since r^t is subadditive for t < 1, its moment is >= 8^t, i.e. the current charge.
   Control: the single-target bound alone only gives 7, so the joint intersection is needed.
5. #4534's rejected candidate (56 rank-1 + 56 rank-4 -> 56 rank-5 per full call, no C charge) on
   #4470's complete invoice: certified raw roots of the baseline, the nominal candidate, and the
   candidate with 0.42 resp. 0.43 extra rank-1 C jobs per full call (break-even between them).
Standard library only.  Prepared by Matarener with Claude Code assistance.  Apache-2.0.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/joint-helper-lattice'))
sys.path.insert(0, str(ROOT / 'research/fresh-helper-boundary'))
DIRS = ('forward', 'backward')
WANT = {1: 2237, 2: 388, 3: 494, 4: 147, 5: 36, 8: 8}


def need(ok, why):
    if not ok:
        raise SystemExit('FAIL: ' + why)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------- subspaces of F_2^9 as point sets
def points(basis):
    out = {0}
    for x in basis:
        out |= {v ^ x for v in tuple(out)}
    return frozenset(out)


def dim(p):
    return len(p).bit_length() - 1


def join(a, b):
    if b <= a:
        return a
    if a <= b:
        return b
    out = set(a)
    for x in b:
        if x not in out:
            out |= {v ^ x for v in tuple(out)}
    return frozenset(out)


ALL = frozenset(range(512))


def c_contact(e):
    return e[0] == 'scalar' and any(isinstance(r, list) and r[0] == 'C' for r in e[1][1:3])


def l_roles(e):
    g = e[1]
    roles = g[1:3] if g[0] in ('add', 'copy') else g[1:2]
    return [r[1] for r in roles if r[0] == 'L']


def blocks(prog):
    """Centre blocks between CLEAR runs: (source contact index, [target contact indices])."""
    out, cur, last_clear = [], None, False
    for i, e in enumerate(prog):
        if e[0] == 'scalar' and e[1][0] == 'clear':
            if not last_clear:
                cur = {'src': None, 't': []}
                out.append(cur)
            last_clear = True
            continue
        last_clear = False
        if c_contact(e):
            if e[2] != 0:
                need(cur['src'] is None, 'one source contact per block')
                cur['src'] = i
            else:
                cur['t'].append(i)
    return [b for b in out if b['src'] is not None or b['t']]


def paid_profile(c, prog, P):
    """Local paid profile from contact charts: L climbs (nested up) and C moves (nested, either way)."""
    prof = Counter()
    cur = {r: f for r, f in enumerate(c['start'])}

    def step(a, b, two_way):
        if a == b:
            return
        if P[a] < P[b]:
            prof[dim(P[b]) - dim(P[a])] += 1
        elif two_way and P[b] < P[a]:
            prof[dim(P[a]) - dim(P[b])] += 1
        else:
            need(False, 'illegal transport in the rebuilt word')
    cchart = None
    for e in prog:
        if e[0] == 'scalar':
            for r in l_roles(e):
                step(cur[r], e[2], False)
                cur[r] = e[2]
            if c_contact(e):
                if e[1][0] == 'clear':
                    cchart = None
                else:
                    if cchart is not None:
                        step(cchart, e[2], True)
                    cchart = e[2]
        elif e[0] == 'warp':
            r = e[1][1]
            step(cur[r], e[3], False)
            cur[r] = e[4]
    for r, f in enumerate(c['final']):
        step(cur[r], f, False)
    return prof


def propagate(c, prog, P):
    """Lowest / highest chart of every L-touching scalar contact over all legal retimings."""
    low, up = {}, {}
    cur = {r: P[f] for r, f in enumerate(c['start'])}
    for i, e in enumerate(prog):
        if e[0] == 'scalar':
            rs = l_roles(e)
            lo = frozenset({0})
            for r in rs:
                lo = join(lo, cur[r])
            for r in rs:
                cur[r] = lo
            low[i] = lo
        elif e[0] == 'warp':
            r = e[1][1]
            need(cur[r] <= P[e[3]], 'warp input above every legal lower bound')
            cur[r] = P[e[4]]
    for r, f in enumerate(c['final']):
        need(cur[r] <= P[f], 'final frame above every legal lower bound')
    cur = {r: P[f] for r, f in enumerate(c['final'])}
    for i in range(len(prog) - 1, -1, -1):
        e = prog[i]
        if e[0] == 'scalar':
            rs = l_roles(e)
            u = ALL
            for r in rs:
                u = u & cur[r]
            for r in rs:
                cur[r] = u
            up[i] = u
        elif e[0] == 'warp':
            cur[e[1][1]] = P[e[3]]
    return low, up


# ---------------------------------------------------------------- certified roots (as productive-lever-reprice)
E = load(ROOT / 'research/kappa-rebuild/architecture/mixed_target_probe.py', 'cwire_probe')
SCALE = 2**128


def outward(x, upw):
    n = x * SCALE
    k = n.numerator // n.denominator
    return Q(k + (1 if upw and k != n else 0), SCALE)


def h_interval(r, c):
    if r in (0, 1):
        return Q(r), Q(r)
    a, b = E.log_interval(r)
    low, _ = E.exp_interval(outward(c * a, False))
    _, high = E.exp_interval(outward(c * b, True))
    return outward(Q(r) / high, False), outward(Q(r) / low, True)


def moment(prof, c):
    lo = hi = Q(0)
    for r, n in prof.items():
        if n:
            a, b = h_interval(r, c)
            lo += n * (a if n >= 0 else b)
            hi += n * (b if n >= 0 else a)
    return lo, hi


def surplus(T, P, c):
    a, b = moment(T, c), moment(P, c)
    return a[0] - b[1], a[1] - b[0]


def root(T, P, width=Q(1, 10**10)):
    lo, hi = 0.0, 1 / 6
    f = lambda c: sum(float(n) * r ** (1 - c) for r, n in T.items()) - sum(float(n) * r ** (1 - c) for r, n in P.items())
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(mid) > 0 else (lo, mid)
    guess = Q(lo).limit_denominator(10**13)
    pos, neg = guess - width / 2, guess + width / 2
    need(surplus(T, P, pos)[0] > 0 and surplus(T, P, neg)[1] < 0, 'certified root bracket')
    return pos, neg


def main():
    NJ = load(ROOT / 'research/joint-helper-lattice/native_joint.py', 'cwire_native_joint')
    c, programs, _, _, _ = NJ.construct()
    P = [points(b) for b in c['frames']]
    result = {'status': None, 'model': 'nested transports; L ascending only; owned C either way; '
              'chronology, coefficients, warps and helper boundaries fixed'}

    # 1. profile self-test
    for d in DIRS:
        prof = paid_profile(c, programs[d], P)
        need(dict(prof) == WANT, f'{d} paid profile reproduces #4470: {dict(sorted(prof.items()))}')
    rs = json.loads((ROOT / 'research/joint-helper-lattice/RESULT.json').read_text())
    need({int(k): v for k, v in rs['local_paid'].items()} == WANT, '#4470 RESULT local_paid')
    result['paid_profile_both_orientations'] = {str(k): v for k, v in sorted(WANT.items())}

    # 2-4. centre structure and floor
    floors = {}
    for d in DIRS:
        prog = programs[d]
        bl = blocks(prog)
        need(len(bl) == 8, f'{d}: eight centre blocks')
        centres = [e for e in prog if e[0] == 'center']
        need(len(centres) == 8 and all(e[4] == 8 for e in centres), f'{d}: eight rank-8 centre transports')
        low, up = propagate(c, prog, P)
        need(all(low[i] <= up[i] for i in low), f'{d}: every contact has a legal chart interval')
        rows = []
        for b in bl:
            need(len(b['t']) == 22, f'{d}: 22 target contacts per block')
            L = low[b['src']]
            common = L
            for t in b['t']:
                common = common & up[t]
            single = max(dim(L) - dim(L & up[t]) for t in b['t'])
            share = Counter(x for t in b['t'] for x in (L & up[t]) if x)
            rows.append({'dim_low_source': dim(L), 'dim_low_and_all_target_ups': dim(common),
                         'single_target_bound': single, 'joint_floor': dim(L) - dim(common),
                         'max_targets_sharing_a_line': max(share.values())})
            need(max(share.values()) == 8, f'{d}: at most 8 of 22 targets admit a common line')
            need(dim(L) == 8 and dim(common) == 0, f'{d}: joint floor 8')
            need(single == 7, f'{d}: control, single-target bound is weaker (7)')
        floors[d] = rows
    result['centre_floor'] = floors
    result['centre_floor_summary'] = ('every one of 8 blocks in both orientations: C mass >= 8 under any '
                                      'retiming of all scalar contacts; current charge 8 (one rank-8 job) is optimal')

    # negative control: the propagation rejects a word whose warp input is pushed below a forced chart
    prog = [list(e) for e in programs['forward']]
    zero = next(f for f, p in enumerate(P) if dim(p) == 0)
    src = blocks(prog)[0]['src']
    S = l_roles(prog[src])[0]
    nxt = next((i for i in range(src + 1, len(prog)) if prog[i][0] == 'warp' and prog[i][1][1] == S), None)
    bad_c = json.loads(json.dumps(c))
    if nxt is None:
        bad_c['final'][S] = zero
    else:
        prog[nxt] = list(prog[nxt]); prog[nxt][3] = zero
    try:
        propagate(bad_c, prog, P)
        rejected = False
    except SystemExit:
        rejected = True
    need(rejected, 'control: forcing the copy source back to frame 0 before its next warp is rejected')

    # 5. rejected #4534 candidate on the complete invoice
    T = Counter({int(k): v for k, v in rs['targets'].items()})
    P0 = Counter({int(k): v for k, v in rs['paid'].items()})
    calls = rs['full_calls']
    cand = Counter(P0)
    cand[1] -= 56 * calls
    cand[4] -= 56 * calls
    cand[5] += 56 * calls
    base = root(T, P0)
    nom = root(T, cand)
    need(nom[0] > base[1], 'nominal candidate raises the raw root')
    lo_extra, hi_extra = Q(42, 100), Q(43, 100)
    c_lo = Counter(cand); c_lo[1] += lo_extra * calls
    c_hi = Counter(cand); c_hi[1] += hi_extra * calls
    r_lo, r_hi = root(T, c_lo), root(T, c_hi)
    need(r_lo[0] > base[1] and r_hi[1] < base[0], 'break-even between 0.42 and 0.43 rank-1 C jobs per call')
    c8 = Counter(P0); c8[8] += calls
    r8 = root(T, c8)
    need(r8[1] < base[0], 'one extra rank-8 transport per call lowers the root')
    fmt = lambda b: [str(b[0]), str(b[1]), float(b[0])]
    result['candidate'] = {'baseline_root': fmt(base), 'nominal_candidate_root': fmt(nom),
                           'nominal_gain_percent': round(100 * (float(nom[0]) / float(base[0]) - 1), 4),
                           'with_0.42_rank1_per_call': fmt(r_lo), 'with_0.43_rank1_per_call': fmt(r_hi),
                           'baseline_plus_one_rank8_per_call': fmt(r8),
                           'break_even_extra_rank1_C_jobs_per_full_call': '(0.42, 0.43)'}
    result['status'] = 'PASS_OWNED_CENTRE_WIRE_FLOOR'
    out = json.dumps(result, indent=1, sort_keys=True) + '\n'
    if '--write' in sys.argv:
        with open(HERE / 'RESULT.json', 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(out)
    else:
        need((HERE / 'RESULT.json').read_text(encoding='utf-8') == out, 'RESULT.json reproduced exactly')
    print(json.dumps({'status': result['status'], 'candidate': result['candidate']['nominal_gain_percent']}))


if __name__ == '__main__':
    main()
