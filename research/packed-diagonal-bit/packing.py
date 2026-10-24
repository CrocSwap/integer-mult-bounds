"""Exact gauge charts and completed-residual bank allocation on PR200's emitted bit word.

The chart, colouring and inventory method is PR197's (Evan McKinney, Apache-2.0); this file applies it to
PR200's terminal-modified bit word (Chafik Boukhalfa) instead of PR187's. Prepared by Rohan Arun with
Anthropic Claude assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from math import gcd
from pathlib import Path
import gzip, hashlib, json, sys
if hasattr(sys, "set_int_max_str_digits"): sys.set_int_max_str_digits(0)

HERE = Path(__file__).resolve().parent
PACKAGE = 'research/paired-cube-diagonal-bit-168'
sys.path.insert(0, str(HERE))
from banks import inverse_integer, color_incidence, check_coloring   # PR197's helpers, byte-identical


def kernel_basis(A, n):
    """Integer basis of {x in Q^n : A x = 0}, by exact RREF."""
    M = [[Q(x) for x in row] for row in A]; piv = []; r = 0
    for c in range(n):
        p = next((i for i in range(r, len(M)) if M[i][c]), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]; inv = 1 / M[r][c]; M[r] = [x * inv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c]: f = M[i][c]; M[i] = [x - f * y for x, y in zip(M[i], M[r])]
        piv.append(c); r += 1
        if r == len(M): break
    free = [c for c in range(n) if c not in piv]; out = []
    for fcol in free:
        v = [Q(0)] * n; v[fcol] = Q(1)
        for i, pc in enumerate(piv): v[pc] = -M[i][fcol]
        den = 1
        for x in v: den = den * x.denominator // gcd(den, x.denominator)
        iv = [int(x * den) for x in v]; g = 0
        for x in iv: g = gcd(g, abs(x))
        out.append([x // g for x in iv])
    return out


def build(BIT):
    pkg = BIT / PACKAGE
    word = json.loads((pkg / 'selected/bit/word_p12.json').read_text())
    frames = json.loads((pkg / 'selected/bit/frames_p12.json').read_text())['frames']
    sinks = json.loads((pkg / 'selected/bit/sinks.json').read_text())
    cert = json.loads((pkg / 'certificate.json').read_text())
    profile = cert['bit']['profile']
    word_sha = hashlib.sha256((pkg / 'selected/bit/word_p12.json').read_bytes()).hexdigest()
    h = 24
    R = 1 + max(max(o[0], o[1]) for o in word['ops'])
    assert R == profile['virtual_R'] == profile['scalar_role_reserve'] == 18908
    donors = {a for a, b in word['pairs']}; recipients = {b for a, b in word['pairs']}
    gauges = {z['role']: z for z in word['gauges']}
    assert len(donors) == len(recipients) == len(word['pairs']) == profile['reused_registers'] == 1760
    assert not donors & recipients and not donors & gauges.keys() and recipients <= gauges.keys()
    sink_roles = {word['rootroles'][z['root']] for z in sinks}
    assert len(sink_roles) == len(sinks) == profile['terminal_sinks'] == 34
    assert not sink_roles & (donors | recipients | gauges.keys())
    physical = sorted(set(range(R)) - recipients - sink_roles); ren = {r: i for i, r in enumerate(physical)}
    assert len(physical) == profile['R'] == 17114
    selected = set(gauges) - recipients
    assert len(selected) == 2200 and {gauges[r]['dim'] for r in selected} == {20}
    assert {gauges[r]['dim'] for r in recipients} == {21}
    assert profile['selected_rank_histogram'] == {'20': 2200}
    # Interior rank-21 recipient starts are paid splices, not entrance residuals.
    inventory = Counter(gauges[r]['frame'] for r in selected)
    digest = hashlib.sha256(); maxops = maxnum = maxden = 0
    for f, count in sorted(inventory.items()):
        rec = frames[str(f)]; A = rec['a']
        assert rec['dim'] == 20 and len(A) == 4
        source = kernel_basis(A, h)
        assert len(source) == 20 and all(sum(x * y for x, y in zip(a, s)) == 0 for a in A for s in source)
        residual = []
        for a in A:
            row = [15 * x - sum(a) for x in a]; d = gcd(*row); residual.append([x // d for x in row])
        # G-orthogonality for G = 9I - J (the bit Gram I - J/9, scaled by 9)
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
        digest.update(json.dumps([f, count, B, C, d, ops], separators=(',', ':')).encode())
    assert max(maxnum, maxden) < 2 ** 80
    families = {4: sorted(selected), 24: sorted(set(physical) - selected)}
    degree = 9; copies = 3; small = degree * len(selected) // 6
    assert 6 * small == degree * len(selected)
    large = (degree * len(families[24]) - 2 * small) // 3
    assert 3 * large + 2 * small == degree * len(families[24])
    left = []; right = []; offsets = []; counts = Counter(); bank = 0
    for pattern, n in (({4: 6, 24: 2}, small), ({24: 3}, large)):
        for _ in range(n):
            offset = 0
            for rank, mult in sorted(pattern.items()):
                for _ in range(mult):
                    role = families[rank][counts[rank] // degree]
                    left.append(ren[role]); right.append(bank); offsets.append(offset); counts[rank] += 1; offset += rank
            assert offset == 72
            bank += 1
    assert all(counts[r] == degree * len(rs) for r, rs in families.items())
    labels, stats = color_incidence(left, right, len(physical), bank, degree)
    check_coloring(left, right, labels, len(physical), bank, degree, full_left=True)
    first = {}; rejected = False
    for e, r in enumerate(left):
        if r not in first: first[r] = e; continue
        old = labels[e]; labels[e] = labels[first[r]]
        try: check_coloring(left, right, labels, len(physical), bank, degree, full_left=True)
        except AssertionError: rejected = True
        finally: labels[e] = old
        break
    assert rejected
    incidence = hashlib.sha256()
    for r, b, c, o in zip(left, right, labels, offsets): incidence.update(f'{r},{b},{c},{o}\n'.encode())
    H = Counter({int(r): copies * n for r, n in profile['child_histogram'].items()})
    assert H.pop(60) == copies * len(selected)
    assert not any(r > 22 for r in H)
    W = 2 * profile['v'] * copies + bank; mass = sum(r * n for r, n in H.items())
    assert 72 * W - mass == copies * profile['deficit_per_vertex'] == 5808
    K = 18 * ((W - 1) + len(physical) * 72 * (maxops + 71))
    return dict(status='PASS exact actual-chain chart and incidence checks', source_package=PACKAGE,
                word_sha256=word_sha, physical_roles=len(physical), interior_splices=len(recipients),
                terminal_sinks=len(sink_roles), gauge_roles=len(selected), distinct_gauges=len(inventory), copies=copies,
                banks=bank, patterns=[dict(rank4=6, rank24=2, count=small), dict(rank4=0, rank24=3, count=large)],
                incidences=len(left), W=W, m=72, rank_mass=mass, deficit=5808, maxchild=max(H),
                child_histogram=dict(sorted(H.items())), chart_sha256=digest.hexdigest(),
                incidence_sha256=incidence.hexdigest(), max_chart_factors=maxops, max_num=maxnum, max_den=maxden,
                conservative_selector_calls=K, color_stats=stats, conflicting_assignment_rejected=rejected)


if __name__ == '__main__':
    import time; t = time.time()
    r = build(Path(sys.argv[1]))
    print(json.dumps({k: v for k, v in r.items() if k != 'child_histogram'}, indent=1), time.time() - t)
