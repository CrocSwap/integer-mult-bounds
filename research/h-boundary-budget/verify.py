#!/usr/bin/env python3
"""Boundary budget of the p3 H branch and three scoped closures of its decoder routes.

Checks, from pinned repository sources and with exact interval arithmetic:

1. The complex and BIT p3 H rank surpluses (616 and 645) and the largest number
   of extra rank-one calls each side can pay while its moment stays positive at the
   selected conditional kappa 0.00302015 (#4470): 322 complex, 397 BIT.
2. The saving root for each boundary-correction cost: free, one shared head
   conjugation (224/222), two (448/444), and the direct three (672/666).
3. rank(H - I) = 8 for the native complex H112, with all 112 rows and columns
   nonzero (no port can be skipped).
4. All 112 complex port query lines q and all 111 BIT port lines are distinct
   (no two ports' rank-one queries can share one call).

Controls: a budget one above the certified value is rejected; a mutated q list
with a duplicate is detected; a rank-8 check on a perturbed H fails.
Standard library only. Prepared by Matarener with Claude Code assistance.
Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import gzip
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KR = ROOT/'research/kappa-rebuild'
# kappa-rebuild imports research/kappa-next-regime; on main that tree is vendored here.
DEP = ROOT/'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime'
sys.path[:0] = [str(KR/'architecture'), str(KR/'bit'),
                str(DEP/'bit-compression/carrier-reuse/reference')]

RECORD = Q('0.00302015')        # selected conditional kappa, #4470
EXPECTED = {
    'complex': dict(margin=616, budget=322, one=224, direct=672,
                    roots={0: '0.0063799', 224: '0.0040422', 448: '0.0017248'}),
    'bit': dict(margin=645, budget=397, one=222, direct=666,
                roots={0: '0.0079333', 222: '0.0051761', 444: '0.0024471'}),
}


def need(ok, why):
    if not ok:
        raise SystemExit('FAIL: ' + why)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def bounds(signed, s, h_interval):
    lo = hi = Q(0)
    for r, n in signed.items():
        a, b = h_interval(r, s)
        lo += n*(a if n >= 0 else b)
        hi += n*(b if n >= 0 else a)
    return lo, hi


def budget(signed, s, h_interval):
    """Largest k with certified moment(s) - k > 0; each rank-one call weighs exactly 1."""
    lo, _ = bounds(signed, s, h_interval)
    need(lo > 0, 'moment positive before correction')
    k = lo.numerator//lo.denominator
    return int(k-1 if Q(k) == lo else k)


def root(signed, k, h_interval, steps=26):
    prof = Counter(signed)
    prof[1] -= k
    if bounds(prof, Q(0), h_interval)[0] <= 0:
        return None
    pos, neg = Q(0), Q('0.02')
    need(bounds(prof, neg, h_interval)[1] < 0, 'bracket')
    for _ in range(steps):
        mid = (pos+neg)/2
        lo, hi = bounds(prof, mid, h_interval)
        if lo > 0:
            pos = mid
        elif hi < 0:
            neg = mid
        else:
            break
    return pos, neg


def complex_profile():
    import controller_tariff as T
    import mixed_forest_search as F
    import mixed_target_probe as E
    windows, targets, _ = T.geometry(3, 43)
    case = F.verify(3, 6, T.simple_p3(), 'H', custom_windows=windows, custom_targets=targets)
    return Counter(case['signed']), E.h_interval


def bit_profile():
    import mixed_productive_bit as B
    probe = json.loads((KR/'bit/PR589-H-GLOBAL-PROBE.json').read_text())
    audit = json.loads((KR/'transfer-audit/h-branch/BIT-MINIMUM-COMPLETION-AUDIT.json').read_text())
    targets = Counter({int(r): n for r, n in probe['targets'].items()})
    nine = Counter({int(r): n for r, n in probe['raw_paid'].items()})
    three = Counter({int(r): n for r, n in audit['p3']['raw_paid'].items()})
    mass = lambda c: sum(r*n for r, n in c.items())
    need(mass(targets)-mass(nine) == 603, 'nine-row BIT surplus 603')
    need(mass(nine)-mass(three) == 42 and nine-three == Counter({1: 42}), 'three-row saves 42 rank-one calls')
    signed = Counter(targets)
    signed.subtract(three)
    return signed, B.h_interval


def side(name, signed, h_interval):
    e = EXPECTED[name]
    margin = sum(r*n for r, n in signed.items())
    need(margin == e['margin'], f'{name} raw surplus {e["margin"]}')
    b = budget(signed, RECORD, h_interval)
    need(b == e['budget'], f'{name} budget {e["budget"]} at {RECORD}')
    over = Counter(signed)
    over[1] -= b+1
    need(bounds(over, RECORD, h_interval)[1] < 0, f'{name}: budget+1 is certified negative (control)')
    roots = {}
    for k, prefix in e['roots'].items():
        r = root(signed, k, h_interval)
        need(r is not None and f'{float(r[0]):.7f}'.startswith(prefix[:8]), f'{name} root for k={k}')
        roots[str(k)] = dict(positive_at=f'{float(r[0]):.10f}', negative_at=f'{float(r[1]):.10f}')
    need(root(signed, e['direct'], h_interval) is None, f'{name}: direct correction fails at s=0')
    return dict(raw_surplus=int(margin), budget_at_record=b, roots=roots,
                direct_correction=e['direct'], one_shared_head=e['one'])


def rank(rows):
    rows = [list(r) for r in rows]
    r = 0
    for c in range(len(rows[0])):
        piv = next((i for i in range(r, len(rows)) if rows[i][c]), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        for i in range(len(rows)):
            if i != r and rows[i][c]:
                f = rows[i][c]/rows[r][c]
                rows[i] = [x-f*y for x, y in zip(rows[i], rows[r])]
        r += 1
    return r


def native_h():
    n = load(DEP/'direct-decoder/native_common.py', 'hbb_native_common')
    reb = load(KR/'complex/rebuild_native.py', 'hbb_rebuild_native')
    packet, _ = n.load_sources()
    geo = reb.geometry(packet)
    size = len(geo['H'])
    h = [[Q(row.get(j, 0)) for j in range(size)] for row in geo['H']]
    m = [[h[i][j]-(i == j) for j in range(size)] for i in range(size)]
    out = dict(ports=size, rank_H_minus_I=rank(m),
               nonzero_rows=sum(any(r) for r in m),
               nonzero_cols=sum(any(m[i][j] for i in range(size)) for j in range(size)))
    need(out == dict(ports=112, rank_H_minus_I=8, nonzero_rows=112, nonzero_cols=112),
         'H112: rank(H-I)=8 with full row and column support')
    hh = [[sum(h[i][k]*h[k][j] for k in range(size)) for j in range(size)] for i in range(size)]
    need(all(hh[i][j] == (i == j) for i in range(size) for j in range(size)), 'H^2 = I')
    bad = [row[:] for row in m]
    bad[0][0] += 1
    need(rank(bad) != 8, 'perturbed H is rejected (control)')
    return out


def distinct_lines():
    phases = json.loads((DEP/'direct-decoder/sources/DATA-PHASES.json').read_text())
    qs = [r['q'] for r in phases['recipes']]
    need([r['port'] for r in phases['recipes']] == list(range(112)), 'complex recipes per port')
    need(len(qs) == 112 and len(set(qs)) == 112 and all(0 < q < 512 for q in qs),
         'complex: 112 distinct nonzero 9-bit query lines')
    mutated = qs[:]
    mutated[1] = mutated[0]
    need(len(set(mutated)) == 111, 'duplicate line detected (control)')
    word = json.loads(gzip.decompress((KR/'bit/sources/pr589-regenerated/WORD.json.gz').read_bytes()))
    lines = [tuple(Q(x) for x in q) for q in word['lines']]
    need(len(lines) == 111 and all(sum(x*x for x in q) == 4 for q in lines), 'BIT root lines')
    canonical = {max(q, tuple(-x for x in q)) for q in lines}
    need(len(canonical) == 111, 'BIT: 111 distinct port lines up to sign')
    return dict(complex_ports=112, complex_distinct_q=112, bit_ports=111, bit_distinct_lines=111)


def main():
    result = dict(schema='h-boundary-budget/1', record_kappa=str(RECORD))
    signed, h = complex_profile()
    result['complex'] = side('complex', signed, h)
    signed, h = bit_profile()
    result['bit'] = side('bit', signed, h)
    result['native_H112'] = native_h()
    result['query_lines'] = distinct_lines()
    result['status'] = 'PASS_H_BOUNDARY_BUDGET_AND_SCOPED_DECODER_CLOSURES'
    result['new_kappa'] = False
    if len(sys.argv) > 2 and sys.argv[1] == '--out':
        Path(sys.argv[2]).write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(status=result['status'],
                          budgets=dict(complex=result['complex']['budget_at_record'],
                                       bit=result['bit']['budget_at_record'])), sort_keys=True))


if __name__ == '__main__':
    main()
