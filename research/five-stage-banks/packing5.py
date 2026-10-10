"""Exact gauge charts and completed width-120 entrance banks for PR234's five-stage bit helper.

PR197/PR205's completed-bank construction (Evan McKinney; Rohan Arun) applied to the five-stage cover of
PR234 (hcg890; Jacob Sussman's five-stage layout). Each genuine independent entrance of rank a pays one
bundled exterior child of rank 5a in PR234. Here its five stage residuals I - P_sigma (rank 24 - a each) are
instead routed into completed banks of width m = 120, exactly as PR197 does for the three-stage cover with
width 72. Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from math import gcd
from pathlib import Path
import gzip, hashlib, json, sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from banks import inverse_integer, color_incidence, check_coloring   # PR197 helpers, byte-identical

H = 24          # local address dimension
STAGES = 5      # PR234 five-stage cover
M = STAGES * H  # bank width 120
COPIES = 12     # data copies; 12 makes the residual volume a whole number of banks
COLORS = STAGES * COPIES
SRC = 'research/five-stage-source-bound-v8/loader/source_inputs'


def kernel_basis(A, n):
    """Integer basis of {x in Q^n : A x = 0}, by exact RREF."""
    Mx = [[Q(x) for x in row] for row in A]; piv = []; r = 0
    for c in range(n):
        p = next((i for i in range(r, len(Mx)) if Mx[i][c]), None)
        if p is None: continue
        Mx[r], Mx[p] = Mx[p], Mx[r]; inv = 1 / Mx[r][c]; Mx[r] = [x * inv for x in Mx[r]]
        for i in range(len(Mx)):
            if i != r and Mx[i][c]: f = Mx[i][c]; Mx[i] = [x - f * y for x, y in zip(Mx[i], Mx[r])]
        piv.append(c); r += 1
        if r == len(Mx): break
    out = []
    for fcol in [c for c in range(n) if c not in piv]:
        v = [Q(0)] * n; v[fcol] = Q(1)
        for i, pc in enumerate(piv): v[pc] = -Mx[i][fcol]
        den = 1
        for x in v: den = den * x.denominator // gcd(den, x.denominator)
        iv = [int(x * den) for x in v]; g = 0
        for x in iv: g = gcd(g, abs(x))
        out.append([x // g for x in iv])
    return out


def annihilator(B):
    """Integer rows spanning the annihilator of row space B (i.e. A with A b = 0 for b in B)."""
    return kernel_basis(B, H)


def entrance_inventory(P234):
    """The genuine independent entrances PR234 bundles into rank-5a exterior children.

    PR200 rank-20 gauges that are not alias recipients, plus PR210's joint shared gauges of ranks 12, 13
    and 18. PR210's three rank-19 joint gauges are source-owned (gaugeb borrowing) and stay unbanked, as in
    PR234's own ledger.
    """
    src = P234 / SRC
    sel = src / 'base_bit/research/paired-cube-diagonal-bit-168/selected/bit'
    word = json.loads(gzip.decompress((sel / 'word_p12.json.gz').read_bytes()))
    frames = json.loads(gzip.decompress((sel / 'frames_p12.json.gz').read_bytes()))['frames']
    pr210 = src / 'pr210/research/coordinated-crossover-pr200'
    pairs = json.loads((pr210 / 'joint/pairs.json').read_text())
    recipients = {b for b, d in pairs}
    assert len(recipients) == len(pairs) == 1760
    entries = []   # (role, rank, annihilator rows)
    for z in word['gauges']:
        if z['role'] in recipients:
            assert z['dim'] == 21
            continue
        rec = frames[str(z['frame'])]
        assert z['dim'] == 20 and rec['dim'] == 20 and len(rec['a']) == 4
        entries.append((z['role'], 20, tuple(map(tuple, rec['a']))))
    owned = {r['role'] for r in json.loads((pr210 / 'gaugeb/selection.json').read_text())}
    joint = json.loads((pr210 / 'joint/joint-selection.json').read_text())
    seen_owned = set()
    for g in joint:
        B = g['gauge_basis']; rank = len(B)
        assert len(B) == rank
        A = tuple(map(tuple, annihilator(B)))
        assert len(A) == H - rank and all(sum(a * b for a, b in zip(x, y)) == 0 for x in A for y in B)
        for role in g['roles']:
            if role in owned:
                assert rank == 19; seen_owned.add(role); continue
            entries.append((role, rank, A))
    assert seen_owned == owned and len(owned) == 3
    ranks = Counter(r for _, r, _ in entries)
    assert dict(ranks) == {20: 2200, 12: 18, 13: 48, 18: 13}, ranks
    assert len({e[0] for e in entries}) == len(entries) == 2279
    return entries


def charts(entries):
    """Exact charts: G-orthogonal complement 15a - (sum a)1 for G = 9I - J, then a basis of sigma.

    Returns per-frame statistics; every chart's inverse identities and elementary-factor replay are checked.
    """
    inventory = Counter(A for _, _, A in entries)
    digest = hashlib.sha256(); maxops = maxnum = maxden = 0
    for A, count in sorted(inventory.items()):
        source = kernel_basis([list(a) for a in A], H)
        assert len(source) == H - len(A)
        assert all(sum(x * y for x, y in zip(a, s)) == 0 for a in A for s in source)
        residual = []
        for a in A:
            row = [15 * x - sum(a) for x in a]; d = gcd(*row); residual.append([x // d for x in row])
        assert all(9 * sum(x * y for x, y in zip(a, b)) - sum(a) * sum(b) == 0 for a in residual for b in source)
        B = list(map(list, zip(*(residual + source))))
        C, d, ops = inverse_integer(B)
        for left, right in ((B, C), (C, B)):
            assert all(sum(x * y for x, y in zip(row, col)) == d * int(i == j)
                       for i, row in enumerate(left) for j, col in enumerate(zip(*right)))
        replay = [list(map(Q, row)) for row in B]
        for op, i, j, num, den in ops:
            if op == 'swap': replay[i], replay[j] = replay[j], replay[i]
            elif op == 'scale': replay[i] = [Q(num, den) * x for x in replay[i]]
            else:
                assert op == 'add'; replay[i] = [x + Q(num, den) * y for x, y in zip(replay[i], replay[j])]
        assert all(x == int(i == j) for i, row in enumerate(replay) for j, x in enumerate(row))
        maxops = max(maxops, len(ops)); maxnum = max(maxnum, max(abs(op[3]) for op in ops))
        maxden = max(maxden, d, max(op[4] for op in ops))
        digest.update(json.dumps([A, count, B, C, d, ops], separators=(',', ':')).encode())
    assert max(maxnum, maxden) < 2 ** 80
    return dict(distinct_charts=len(inventory), chart_sha256=digest.hexdigest(), max_chart_factors=maxops,
                max_num=maxnum, max_den=maxden)


# Bank patterns of width 120 (residual rank -> multiplicity); every pattern has at most 60 items.
PATTERNS = {
    'r11x8+r4x8': {11: 8, 4: 8},
    'r12x10': {12: 10},
    'r6x20': {6: 20},
    'r4x30': {4: 30},
    'r24x5': {24: 5},
}


def banks(entries, physical_roles):
    """Allocate every residual occurrence (5 stages x 12 copies per physical chain) to a full bank and colour."""
    residual = {role: H - rank for role, rank, _ in entries}
    gauge_roles = sorted(residual)
    n_full = physical_roles - len(gauge_roles)
    assert n_full == 14364
    # chains: gauge chains first, then anonymous full-residual chains (one per remaining physical role)
    chain_res = [residual[r] for r in gauge_roles] + [H] * n_full
    by_res = defaultdict(list)
    for c, res in enumerate(chain_res): by_res[res].append(c)
    occ = {res: [c for c in cs for _ in range(COLORS)] for res, cs in by_res.items()}
    counts = {res: len(v) for res, v in occ.items()}
    plan = Counter()
    plan['r11x8+r4x8'] = counts[11] // 8
    plan['r12x10'] = counts[12] // 10
    plan['r6x20'] = counts[6] // 20
    plan['r4x30'] = (counts[4] - 8 * plan['r11x8+r4x8']) // 30
    plan['r24x5'] = counts[24] // 5
    use = Counter()
    for name, n in plan.items():
        for res, k in PATTERNS[name].items(): use[res] += n * k
    assert dict(use) == counts, (use, counts)
    assert all(sum(r * k for r, k in p.items()) == M and sum(p.values()) <= COLORS for p in PATTERNS.values())
    left = []; right = []; offsets = []; cursor = Counter(); bank = 0
    for name in ('r11x8+r4x8', 'r12x10', 'r6x20', 'r4x30', 'r24x5'):
        for _ in range(plan[name]):
            off = 0
            for res, k in sorted(PATTERNS[name].items(), reverse=True):
                for _ in range(k):
                    c = occ[res][cursor[res]]; cursor[res] += 1
                    left.append(c); right.append(bank); offsets.append(off); off += res
            assert off == M
            bank += 1
    assert all(cursor[r] == counts[r] for r in counts)
    nchains = len(chain_res)
    labels, stats = color_incidence(left, right, nchains, bank, COLORS)
    check_coloring(left, right, labels, nchains, bank, COLORS, full_left=True)
    # A deliberately duplicated colour at one chain must be rejected.
    first = {}; rejected = False
    for e, r in enumerate(left):
        if r not in first: first[r] = e; continue
        old = labels[e]; labels[e] = labels[first[r]]
        try: check_coloring(left, right, labels, nchains, bank, COLORS, full_left=True)
        except AssertionError: rejected = True
        finally: labels[e] = old
        break
    assert rejected
    inc = hashlib.sha256()
    for r, b, c, o in zip(left, right, labels, offsets): inc.update(f'{r},{b},{c},{o}\n'.encode())
    total_width = sum(r * n for r, n in counts.items())
    assert total_width == M * bank
    return dict(copies=COPIES, colors=COLORS, banks=bank, plan=dict(plan), residual_occurrences=counts,
                incidences=len(left), incidence_sha256=inc.hexdigest(), color_stats=stats,
                conflicting_assignment_rejected=rejected, gauge_chains=len(gauge_roles), full_chains=n_full)


def build(P234, physical_roles, v=1760):
    entries = entrance_inventory(P234)
    chart = charts(entries)
    bank = banks(entries, physical_roles)
    W = COPIES * (STAGES - 1) * v + bank['banks']
    K = 18 * ((W - 1) + physical_roles * M * (chart['max_chart_factors'] + M - 1))
    return dict(status='PASS exact charts and width-120 bank incidence', entrance_ranks={20: 2200, 12: 18, 13: 48, 18: 13},
                removed_exteriors={100: 2200, 60: 18, 65: 48, 90: 13}, W=W, m=M, **chart, **bank,
                conservative_selector_calls=K)


if __name__ == '__main__':
    import time; t = time.time()
    r = build(Path(sys.argv[1]), int(sys.argv[2]))
    print(json.dumps(r, indent=1), time.time() - t)
