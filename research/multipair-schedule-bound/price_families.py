#!/usr/bin/env python3
"""Price every multi-pair / mixed / alternative-rho schedule family on the T74 local words.

Inputs (read, never modified): inputs/T74-WORDS.json (per-call paid profiles of the two T74 local
words, their 480 helper widths and the 417/249 call split, extracted from PR #1800's provider
registry; see its `source` pin), the retained exact moment engine
research/complex-k492-owner-repair/vendor/multicold/engines/moment.py and the packing-ceiling tool
research/complex-local-word-ceiling/ceiling.py.

Per replica a family is (K pairs, s stages, N local-word invocations = pair-calls, cst per
invocation). Identities (README, Corollary):
    W = 2 K v (v = 112),  m = 1 + 8 s (k = 1, h - k = 8 per stage),
    coverage: paid mass = (m - 1) W + cst_inv * N_inv,   D = W - cst_inv * N_inv,
    each pair-call carries the T74 local profile (active climbs 1792, centre 8 x rank 8,
    480 hosted helpers of total width ~3736, all in its paid children),
    idle remainder = coverage mass - local mass, paid as children of rank
    min(largest idle window, R_max(m)) with R_max the outer halving guard (m^2 > 2 R^2).
If the idle remainder is negative (hosting wall) the excess helper mass is paid on top of the
coverage law (unhosted), which lowers D one for one; the moment engine then sees D = mW - mass.

Also evaluates the packing ceiling (ceiling.ceiling) for each family: the best b over ALL idle
histograms and hostings at the stated (local, m, W, N, cst).

usage: python -B price_families.py [--write]     (writes profiles/*.json, grader/*.json, FAMILIES.json)
       python -B price_families.py --check       (recomputes and compares with the committed files)
"""
import importlib.util
import json
import sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
WORDS = HERE / 'inputs/T74-WORDS.json'
sys.path.insert(0, str(REPO / 'research/complex-local-word-ceiling'))
import ceiling as C  # noqa: E402


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOMENT = _load(REPO / 'research/complex-k492-owner-repair/vendor/multicold/engines/moment.py', 'retained_moment')

V, A, CST, T = 112, 8, 64, 74
T74_M, T74_W = 73, 896 * 74


def words(data=None):
    data = data or json.loads(WORDS.read_text())
    w = data['words']
    split = {k: w[k]['calls'] for k in w}
    prof = {k: {int(r): n for r, n in w[k]['actual_paid_profile'].items()} for k in w}
    helpers = {k: w[k]['helper_width_total'] for k in w}
    assert split == {'extra': 417, 'gauge44': 249}, split
    assert split['extra'] + split['gauge44'] == T * 9
    for k in w:
        mass = sum(r * n for r, n in prof[k].items())
        assert mass == 2 * V * A + CST + helpers[k], (k, mass)       # 1792 + 64 + helper widths
        assert prof[k][8] == 8                                           # the 8 rank-8 centre copies
        hist = {int(x): c for x, c in w[k]['helper_width_histogram'].items()}
        assert sum(hist.values()) == w[k]['helper_count'] == 480 and sum(x * c for x, c in hist.items()) == helpers[k]
    # the two words plus the published idle children recompose the published global profile exactly
    glob = {}
    for k in w:
        for r, n in prof[k].items():
            glob[r] = glob.get(r, 0) + n * split[k]
    for r, n in data['idle_children'].items():
        glob[int(r)] = glob.get(int(r), 0) + n
    assert {str(r): n for r, n in sorted(glob.items())} == data['published_global_profile'], glob
    return prof, split, helpers


def bracket(H, m, W):
    r = MOMENT.certify(Counter(H), m, W, False)
    return Q(r['lower']), Q(r['upper'])


def r_max(m):
    return C.max_idle_rank(m)


def bk_largest_window(k):
    """B_k idle windows per port (format-limits (Sch)): pair 0 [(2k-2)a]; pair p [2pa, a, (2k-2p-2)a]."""
    return (2 * k - 2) * A


def bk_windows(k):
    w = {}
    def add(x):
        if x > 0:
            w[x] = w.get(x, 0) + 2      # X and Y bank
    add((2 * k - 2) * A)
    for p in range(1, k):
        add(2 * p * A); add(A); add((2 * k - 2 * p - 2) * A)
    return dict(sorted(w.items()))


def build(fam, prof, split):
    """Integer global profile over T replicas."""
    K, s, N, cst_inv, pairs_per_inv = fam['K'], fam['s'], fam['N'], fam['cst_inv'], fam.get('pairs_per_inv', 1)
    m, W = 1 + A * s, 2 * K * V
    n_inv = N // pairs_per_inv
    assert n_inv * pairs_per_inv == N
    total_pair_calls = N * T
    n_extra = round(total_pair_calls * split['extra'] / (split['extra'] + split['gauge44']))
    n_g = total_pair_calls - n_extra
    H = {}
    for word, n in (('extra', n_extra), ('gauge44', n_g)):
        for r, c in prof[word].items():
            H[r] = H.get(r, 0) + c * n
    # a shared-centre invocation pays ONE centre path for its pairs_per_inv local words
    H[8] -= 8 * (pairs_per_inv - 1) * n_inv * T
    local_mass = sum(r * c for r, c in H.items())
    coverage = (m - 1) * W * T + cst_inv * n_inv * T
    idle = coverage - local_mass
    Rcap = min(fam.get('largest_window') or 10 ** 9, r_max(m))
    if idle > 0:
        q, rem = divmod(idle, Rcap)
        H[Rcap] = H.get(Rcap, 0) + q
        if rem:
            H[rem] = H.get(rem, 0) + 1
    H = {str(r): c for r, c in sorted(H.items()) if c}
    return dict(m=m, W=W * T, H=H, label=fam['label']), dict(m=m, W_rep=W, R_cap=Rcap, R_max=r_max(m),
                coverage_rep=Q(coverage, T), local_rep=Q(local_mass, T), idle_rep=Q(idle, T),
                hosting_wall=idle < 0, D_rep=Q(W * T - cst_inv * n_inv * T + min(idle, 0), T))


def grade(prof_json, base):
    """Exact 1e-24 bracket of the complex exponent with the retained moment engine."""
    H = {int(r): c for r, c in prof_json['H'].items()}
    m, W = prof_json['m'], prof_json['W']
    mass = sum(r * c for r, c in H.items())
    if m * W - mass <= 0 or any(not 0 < r < m for r in H):
        return {'error': 'non-positive deficit (hosting wall) or rank outside (0, m)'}
    try:
        lo, hi = bracket(H, m, W)
    except AssertionError:
        return {'error': 'outside the engine search window [0, 0.003]'}
    return dict(label=prof_json['label'], m=m, W=W, mass=mass, deficit=m * W - mass,
                b_lower=MOMENT.decimal(lo), b_upper=MOMENT.decimal(hi),
                b_gain_over_T74_percent=float((lo / base[0] - 1) * 100), beats_T74=lo > base[1])


def ceiling(fam, prof, split):
    """Packing ceiling: all idle mass at R_max(m); None if the local word overflows the coverage law."""
    K, s, N, cst_inv, ppi = fam['K'], fam['s'], fam['N'], fam['cst_inv'], fam.get('pairs_per_inv', 1)
    tot = split['extra'] + split['gauge44']
    local = {}
    for word in ('extra', 'gauge44'):
        for r, c in prof[word].items():
            local[r] = local.get(r, 0) + Q(c * split[word] * ppi, tot)
    local[8] -= 8 * (ppi - 1)
    m = 1 + A * s
    try:
        lo, hi = C.ceiling(local, m, 2 * K * V, N // ppi, cst_inv)
    except ValueError as e:
        return {'error': str(e)}
    return {'a_hi': float(hi), 'a_hi_exact': str(hi)}


def families():
    fams = []
    for k in (3, 4, 5, 6, 7):
        s = 2 * k + 1
        fams.append(dict(label='B_%d chain (s=%d); t parallel B_%d chains (rank-tv calls, any orientation mix) '
                               'have the same per-wire profile' % (k, s, k), K=k, s=s,
                         N=2 * k + 1, cst_inv=CST, largest_window=bk_largest_window(k),
                         status='attained (chains_replay.py); Theorem S frontier at odd s'))
    fams.append(dict(label='B_4 || B_4 mixed orientation, s=9, K=8 (every stage = one forward + one backward '
                           'local word, rank 2v)', K=8, s=9, N=18, cst_inv=CST, largest_window=48,
                     status='attained (chains_replay.py); equals two T74 replicas'))
    fams.append(dict(label='B_4 || B_3 unequal chains, s=9, K=7, N=16', K=7, s=9, N=16, cst_inv=CST,
                     largest_window=48, status='attained (chains_replay.py); Theorem S tight (ceil)'))
    fams.append(dict(label='s=8 by chains: B_3 plus one idle stage (best chain ratio N/K = 7/3), K=3, N=7', K=3, s=8, N=7,
                     cst_inv=CST, largest_window=40, status='attained (s=7 schedule padded by one stage)'))
    for s, K, N, R, note in ((8, 7, 16, 40, 'idle children <= 40 (window multiple of a=8 under the guard)'),
                             (8, 7, 16, None, 'idle children at R_max = 45 (ceiling-favorable)'),
                             (10, 9, 20, None, 'idle children at R_max = 57'),
                             (6, 5, 12, None, 'idle children at R_max = 34')):
        k = (s - 1) // 2
        fams.append(dict(label='even s=%d at the Theorem S bound (K=%d, N=%d), %s; attainment open' % (s, K, N, note),
                         K=K, s=s, N=N, cst_inv=CST, largest_window=R,
                         status='HYPOTHETICAL: only the lower bound is proved; chains need N=%d; F2 search '
                                'refutes the bound at (K=3, s=4)' % (2 * K + -(-K // k))))
    fams.append(dict(label='excluded: waste-free parallel s=9, K=8, N=17', K=8, s=9, N=17, cst_inv=CST,
                     largest_window=None, status='EXCLUDED by Theorem S (N >= 18)'))
    fams.append(dict(label='excluded: s=9, K=8, two pairs per invocation, ONE centre path per invocation',
                     K=8, s=9, N=18, cst_inv=CST, pairs_per_inv=2, largest_window=48,
                     status='EXCLUDED: the two pairs carry independent totals (README Q1); the grader '
                            'window stops at b = 0.003, so only the ceiling is reported'))
    return fams


def main():
    write = '--write' in sys.argv
    check = '--check' in sys.argv
    prof, split, helpers = words()
    data = json.loads(WORDS.read_text())
    base = bracket({int(r): n for r, n in data['published_global_profile'].items()}, T74_M, T74_W)
    assert MOMENT.decimal(base[0]).startswith(data['published_complex_endpoint_prefix'][:-2]), base
    mismatches = []
    rows = []
    (HERE / 'profiles').mkdir(exist_ok=True)
    (HERE / 'grader').mkdir(exist_ok=True)
    for i, fam in enumerate(families()):
        prof_json, info = build(fam, prof, split)
        slug = 'F%02d' % i
        p = HERE / 'profiles' / (slug + '.json')
        g = grade(prof_json, base)
        if write:
            p.write_text(json.dumps(prof_json, indent=1) + '\n')
            (HERE / 'grader' / (slug + '.json')).write_text(json.dumps(g, indent=1) + '\n')
        if check:
            for path, obj in ((p, prof_json), (HERE / 'grader' / (slug + '.json'), g)):
                if json.loads(path.read_text()) != json.loads(json.dumps(obj)):
                    mismatches.append(str(path.relative_to(HERE)))
        ce = ceiling(fam, prof, split)
        row = dict(id=slug, **{k: v for k, v in fam.items()}, **{k: (str(v) if isinstance(v, Q) else v)
                   for k, v in info.items()}, b_lower=g.get('b_lower'), gain_percent=g.get('b_gain_over_T74_percent'),
                   beats_T74=g.get('beats_T74'), grader_error=g.get('error'), ceiling=ce)
        if fam['label'].startswith('B_'):
            row['idle_windows_per_port'] = bk_windows(fam['K'])
        rows.append(row)
        print(json.dumps({k: row[k] for k in ('id', 'label', 'm', 'W_rep', 'D_rep', 'idle_rep', 'R_cap',
                                                 'hosting_wall', 'b_lower', 'gain_percent', 'ceiling')}))
    fam = dict(T74_b_bracket=[MOMENT.decimal(base[0]), MOMENT.decimal(base[1])], helpers_per_call=helpers,
               call_split=split, families=rows)
    if write:
        (HERE / 'FAMILIES.json').write_text(json.dumps(fam, indent=1) + '\n')
    if check:
        if json.loads((HERE / 'FAMILIES.json').read_text()) != json.loads(json.dumps(fam)):
            mismatches.append('FAMILIES.json')
        assert not mismatches, mismatches
        print('PASS_F1_PRICES families=%d' % len(rows))
    return fam


if __name__ == '__main__':
    main()
