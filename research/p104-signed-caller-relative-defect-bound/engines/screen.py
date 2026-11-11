"""Directed invoice and exact Type B idle-demotion obstruction."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import runpy
from signal import SIGALRM, alarm, signal

HEAD = 'ed090b57ed88f8859e5ff4643645099e6ba856ea'
PINS = {
    'round30/complex/audit.py': '67b006627fd4e07c349f48f31e6d541c62804416bdc85f664a3607dd1b386efb',
    'round30/complex/source/inputs/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'round30/complex/source/inputs/EARLY-RESULT.json': '691025fe95c7938a6da211244d4d5b6187d88a9de1acff0862eeb7f0ce7deaa7',
    'round30/complex/source/inputs/WORD.json.gz': '2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756',
    'round30/complex/source/powers.py': 'c0c460b464d7c836fb887010b57119be322aae686736b86820aae3544d380bee',
    'reference/check_odd_caller_exact_grid.py': 'abd5a5fd011b71e5b382cbc058855594d4f2fe7b049f375506675c0303180f54',
}
I = ((Q(1), Q(0)), (Q(0), Q(1)))
NEG_I = ((Q(-1), Q(0)), (Q(0), Q(-1)))


def authenticate(round30):
    roots = {'round30': round30, 'reference': Path(__file__).resolve().parent / 'references'}
    result = {}
    for name, expected in PINS.items():
        key, rel = name.split('/', 1)
        file = roots[key] / rel
        raw = file.read_bytes()
        assert sha256(raw).hexdigest() == expected, ('changed input', name)
        result[name] = file, raw
    return result


def decode(raw):
    def unique(pairs):
        data = dict(pairs)
        assert len(data) == len(pairs), 'duplicate JSON key'
        return data
    return json.loads(raw, object_pairs_hook=unique)


def write(out, name, value):
    tmp = out / (name + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    tmp.replace(out / name)


def mul(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(2)) for j in range(2)) for i in range(2))


def det(a):
    return a[0][0] * a[1][1] - a[0][1] * a[1][0]


def inv(a):
    n = det(a)
    assert n
    return ((a[1][1]/n, -a[0][1]/n), (-a[1][0]/n, a[0][0]/n))


def defect(a):
    return tuple(tuple(a[i][j] - I[i][j] for j in range(2)) for i in range(2))


def j_eval(alpha, beta, q):
    assert (alpha, beta) == (Q(-1), Q(1, 2)) and q in (-1, 1)
    # Literal #7113 Type B at body=1: s' = s + alpha q t,
    # t' = beta q^{-1} s + t/2. Coefficients pinned above are required.
    return ((Q(1), alpha * q), (beta / q, Q(1, 2)))


def stringify(a):
    return [[str(v) for v in row] for row in a]


def controls():
    plus, minus = (j_eval(Q(-1), Q(1, 2), q) for q in (1, -1))
    relative = mul(inv(plus), minus)
    assert relative == ((0, 1), (-1, 0)) and det(relative) == 1 and det(defect(relative)) == 2
    assert relative != NEG_I
    # Rank saturation is attainable when both factors act by -I on their defects.
    x, y = ((-1, 0), (0, 1)), ((1, 0), (0, -1))
    assert mul(y, x) == NEG_I and det(x) == det(y) == -1
    # Ordinary mixing, even though it cancels from its own relative, conjugates later factors.
    even = ((Q(1), Q(2)), (Q(0), Q(1)))
    lhs = mul(inv(mul(plus, even)), mul(minus, even))
    rhs = mul(mul(inv(even), relative), even)
    assert lhs == rhs and lhs != relative and det(defect(lhs)) == 2
    assert mul(inv(even), even) == I
    # Removing one sign flip changes determinant and removing two loses rank.
    assert det(y) != det(NEG_I) and det(defect(I)) == 0 and det(defect(NEG_I)) == 4
    return ['quarter_turn_rank_two_not_negative_identity', 'rank_saturation_positive_control',
            'even_mix_conjugacy_control', 'odd_and_all_demotion_controls']


def prepare(root, out):
    checked = controls()
    inputs = authenticate(root)
    caller = decode(inputs['round30/complex/source/inputs/CALLER.json'][1])
    early = decode(inputs['round30/complex/source/inputs/EARLY-RESULT.json'][1])
    audit = runpy.run_path(str(inputs['round30/complex/audit.py'][0]))
    power = runpy.run_path(str(inputs['round30/complex/source/powers.py'][0]))['power']
    _, _, _, edges, _, _, copies, paid, productive, _ = audit['read_model']()
    assert audit['HEAD'] == HEAD and copies == 17 and len(edges) == 137891
    k = Q(early['price']['independent_raw_bracket'][1])
    b = caller['types']['B']
    multiplicity = len(set(b['ports']))
    assert multiplicity == len(b['ports']) == 8
    idle = {}
    for t, e in enumerate(caller['events']):
        if e[:2] == ['B', 'IDLE_ODD']:
            _, _, role, selected, q_power = e
            assert len(selected) == 1 and q_power % 2 == 1
            idle[t] = dict(clock=t, role=role, stages=selected, q_power=q_power, old_rank=9, new_rank=8)
    assert len(idle) == 4 and paid[9] == len(idle) * multiplicity
    tariff = cache(lambda r: power(r, k))

    def price(hist):
        lo = hi = Q(0)
        for r, count in hist.items():
            a, b = tariff(r)
            lo += count * (a if count >= 0 else b)
            hi += count * (b if count >= 0 else a)
        return list(map(str, (lo, hi)))

    net = productive.copy()
    net.subtract(paid)
    baseline = price(net)
    assert Q(baseline[1]) < 0
    scenarios = []
    for size in range(1, 5):
        credit = {9: size * multiplicity, 8: -size * multiplicity}
        candidate = net.copy()
        candidate.update(credit)
        for clocks in combinations(idle, size):
            scenarios.append(dict(demote=list(clocks), changed_calls=size, paid_delta={r: -c for r, c in credit.items()},
                                  exact_saving_interval=price(credit), complete_margin_interval=price(candidate)))
    assert len(scenarios) == 15
    write(out, 'PRICE.json', dict(head=HEAD, pins=PINS, crossing_upper=str(k), copies=copies,
          type_b_ports=multiplicity, baseline_interval=baseline, original_paid=dict(paid),
          original_productive=dict(productive), idle_stock=list(idle.values()), scenarios=scenarios,
          grant='Credit the rank replacement only, with arbitrary additional ordinary costs free in the upper.'))

    n, offset = b['roles'], b['offset']
    assert n == 36 and offset == 36 and len(b['diagonal']) == n
    assert all(e[0] == -1 and e[1] == 0 and len(e) == copies + 2 and set(e[2:]) <= {0, 1} for e in b['diagonal'])
    allowed = range(offset, offset+n)
    j_receipts = []
    for clock, event in enumerate(caller['events']):
        if event[0] == 'J':
            _, stage, a_roles, (s, t, a, c) = event
            assert s != t and s in allowed and t in allowed and not set(a_roles) & set(allowed)
            plus, minus = (j_eval(Q(a), Q(c), q) for q in (1, -1))
            relative = mul(inv(plus), minus)
            assert det(plus) == det(minus) == det(relative) == 1
            assert det(defect(relative)) and relative[0][1] and relative[1][0] and relative != NEG_I
            j_receipts.append(dict(clock=clock, stage=stage, active_roles=[s,t], coefficients=[a,c],
                                   q_plus=stringify(plus), q_minus=stringify(minus), relative=stringify(relative),
                                   determinant=str(det(relative)), defect_rank=2, defect_det=str(det(defect(relative)))))
        elif event[0] == 'B':
            _, op, role, *args = event
            assert role in allowed
            assert op in ('SWAP', 'ADD', 'SCALE', 'LAMBDA', 'QUERY', 'IDLE_ONE', 'IDLE_ODD')
            if op in ('SWAP', 'ADD', 'QUERY'):
                assert args[0] in allowed and args[0] != role
            if op == 'QUERY':
                assert args[1] % 2 == 0
            if op == 'SCALE':
                assert Q(args[0])
    assert [r['stage'] for r in j_receipts] == list(range(1, 18))
    rows = []
    for s in scenarios:
        retained = len(idle) - s['changed_calls']
        determinant = (-1) ** retained
        rank_sum = sum(r['defect_rank'] for r in j_receipts) + retained
        if determinant != (-1) ** n:
            reason = 'determinant'
        elif rank_sum < n:
            reason = 'rank_deficit'
        else:
            assert rank_sum == n
            reason = 'rank_saturation_and_noninvolutive_J_defect_action'
        rows.append(dict(demote=s['demote'], changed_calls=s['changed_calls'], retained_odd=retained,
                         determinant=determinant, defect_rank_sum=rank_sum, exclusion=reason))
    assert Counter(r['exclusion'] for r in rows) == {
        'determinant': 8, 'rank_deficit': 1, 'rank_saturation_and_noninvolutive_J_defect_action': 6}
    write(out, 'SUPPORT.json', dict(head=HEAD, pins=PINS, controls=checked, status='all_subsets_excluded',
          price_sha256=sha256((out/'PRICE.json').read_bytes()).hexdigest(),
          dimension=n, q_specialization=[1,-1], body_specialization=1,
          target_relative='-I_36', endpoint_determinant=1, endpoint_defect_rank=36,
          j_blocks=j_receipts, cases=rows, checked_subsets=len(rows), unvisited_subsets=0,
          scope='Fixed Type B per-port J factors with arbitrary invertible q-even local mixing and no cross-port operations.'))


def main():
    p = ArgumentParser()
    p.add_argument('round30', type=Path, nargs='?')
    p.add_argument('out', type=Path, nargs='?')
    p.add_argument('--seconds', type=int, default=20, choices=range(2, 21), metavar='2..20')
    p.add_argument('--controls-only', action='store_true')
    a = p.parse_args()
    if a.controls_only:
        print(json.dumps(controls()))
        return
    if a.round30 is None or a.out is None:
        p.error('Round 30 dependency root and fresh output directory required')
    a.out.mkdir()

    def cap(*_):
        raise TimeoutError('hard runner deadline')

    signal(SIGALRM, cap)
    alarm(a.seconds)
    try:
        prepare(a.round30, a.out)
    except TimeoutError:
        write(a.out, 'TIMEOUT.json', dict(head=HEAD, status='capped', seconds_cap=a.seconds,
                                        price_saved=(a.out/'PRICE.json').exists(), unverified_subsets=15))
        raise SystemExit(2)
    finally:
        alarm(0)


if __name__ == '__main__':
    main()
