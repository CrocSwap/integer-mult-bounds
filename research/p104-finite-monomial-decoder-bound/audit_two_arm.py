"""Independent primitive-row, Clifford support and price recount."""
from bisect import bisect_right
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import gzip
import json


PRIOR_AUDIT = '7270c06773d17a0d5ac80dd17e53eca076a5dfe92a87659ea345845fb594dc61'


def synthetic_control(interp):
    returned = (('C', 1, 1),)
    target = returned + (('C', 2, 1),)
    # C_2 = ((1+i) I + (1-i) X_2)/2 on the second bit.
    for j in range(4):
        src, den = interp.state(returned, j)
        want, power = interp.state(target, j)
        got = defaultdict(lambda: (0, 0))
        for k, (a, b) in src.items():
            for address, pair in ((k, (a - b, a + b)), (k ^ 2, (a + b, b - a))):
                old = got[address]
                got[address] = (old[0] + pair[0], old[1] + pair[1])
        assert {k: (Q(a, 2 ** (den + 1)), Q(b, 2 ** (den + 1))) for k, (a, b) in got.items()} == {
            k: (Q(a, 2 ** power), Q(b, 2 ** power)) for k, (a, b) in want.items()}
    returned3 = tuple(('C', 1 << (2 * j), 1) for j in range(3))
    target3 = returned3 + tuple(('C', 2 << (2 * j), 1) for j in range(3))
    r = len(interp.state(interp.adjoint(returned3))[0])
    s = len(interp.state(interp.adjoint(target3))[0])
    assert (r, s) == (8, 64) and 2 * r + 1 < s
    return {'width_one_signed_columns_equal': 4, 'tensor_3_target_row_support': s,
            'tensor_3_two_returned_plus_source_support_upper': 2 * r + 1}


def run(root):
    path = root / 'prior/audit.py'
    assert sha256(path.read_bytes()).hexdigest() == PRIOR_AUDIT
    spec = spec_from_file_location('prior_audit', path)
    a = module_from_spec(spec)
    spec.loader.exec_module(a)
    word = json.loads(gzip.decompress(a.checked(root, 'inputs/native/WORD.json.gz')[1]))
    frozen = json.loads(a.checked(root, 'inputs/native/RESULT.json')[1])
    independent = a.load(root, 'deps/canonical/research/shared-wire-split-composition/frozen/native_verify.py')
    price = a.load(root, 'deps/round11/frontier/independent_adapter_price.py')
    typed = json.loads((root / 'prior/TYPED.json').read_bytes())
    raw = (root / 'TWO-ARM.json').read_bytes()
    report = json.loads(raw)
    frames = [independent.frame(x, 9) for x in word['frames']]
    inverse = [independent.adjoint(f) for f in frames]
    cosets = [a.span(x | (z << 9) for x, z, _ in independent.tableau(u)[9:]) for u in inverse]
    wanted = defaultdict(set)
    claimed = {}
    for group in typed['eligible_group_details']:
        line = a.primitive({j: Q(q) for j, q in group['projective_row']})
        claimed[line] = [e['event'] for e in group['members']]
        for e in group['members']:
            wanted[cosets[e['source']], len(line)].add(line)

    public = word['public']
    resident = [{i: Q(1)} for i in range(public)] + [{} for _ in range(word['owned_fields'])]
    chart = [*word['initial'], *([None] * word['owned_fields'])]
    first = defaultdict(dict)
    touches = defaultdict(list)
    moves = {}
    by_line = defaultdict(list)

    def observe(j, cut):
        row = resident[j]
        if row:
            coset = cosets[chart[j]]
            match = wanted.get((coset, len(row)))
            if match:
                line = a.primitive(row)
                if line in match:
                    first[coset, line].setdefault(j, cut)

    for j in range(public):
        observe(j, 0)
    for cut, (op, j, *args) in enumerate(word['program']):
        touches[j].append(cut)
        if op == 'MOVE':
            f, g, owned = args
            assert chart[j] == f and owned == (j >= public) and resident[j]
            r = abs(len(word['frames'][g]) - len(word['frames'][f]))
            by_line[a.primitive(resident[j])].append(cut)
            moves[cut] = (j, f, g, r)
            chart[j] = g
        elif op == 'ADD':
            k, c, f = args
            assert chart[k] == chart[j] == f
            touches[k].append(cut)
            p, q = resident[j], resident[k]
            factor = Q(c)
            resident[j] = {i: v for i in p.keys() | q.keys() if (v := p.get(i, 0) + factor * q.get(i, 0))}
        elif op == 'COPY':
            k, c, f = args
            assert chart[k] == chart[j] == f and not resident[j]
            touches[k].append(cut)
            resident[j] = {i: Q(c) * v for i, v in resident[k].items()}
        elif op == 'SCALE':
            c, f = args
            assert chart[j] == f
            resident[j] = {i: Q(c) * v for i, v in resident[j].items()}
        else:
            assert op in ('INIT', 'CLEAR') and j >= public
            chart[j] = args[0] if op == 'INIT' else None
            resident[j] = {}
        observe(j, cut + 1)
    assert chart == [*word['final'], *([None] * word['owned_fields'])]
    groups = {k: v for k, v in by_line.items() if len({cosets[moves[e][2]] for e in v}) > 1}
    assert claimed == groups and len(moves) == 6281

    @cache
    def direction(f, g):
        return a.span(x for x, _, _ in independent.tableau(inverse[g] + frames[f])[9:])

    stats = Counter()
    width_positive = set()
    width_hist = Counter()
    for line, group in groups.items():
        candidates = set()
        assert len({cosets[moves[e][2]] for e in group}) == len(group)
        for e in group:
            _, f, g, r = moves[e]
            d = direction(f, g)
            assert len(d) == 2 ** r > 1
            for omitted in group:
                if e == omitted:
                    continue
                stats['ordered_pairs'] += 1
                role, _, h, _ = moves[omitted]
                want = direction(f, h)
                between = direction(g, h)
                assert len(between) > 1
                stats['three_distinct_tensor_rejected' if len(want) > 1 else 'source_monomial_bypass'] += 1
                if len(want) > 2 * len(d & want):
                    stats['width_one_direction_fail'] += 1
                    continue
                stats['width_one_direction_pass'] += 1
                clock = touches[role]
                i = bisect_right(clock, omitted)
                deadline = clock[i] if i < len(clock) else len(word['program'])
                possible = first[cosets[f], line]
                independent_source = any(cut <= deadline and (j != role or cut <= omitted) for j, cut in possible.items())
                if len(want) == 1:
                    assert not independent_source
                    stats['source_bypass_unavailable'] += 1
                if independent_source:
                    assert len(want) > 1
                    stats['width_one_independent_pass'] += 1
                    candidates.add(omitted)
                    width_positive.add((e, omitted))
        if len(candidates) == len(group):
            candidates.remove(min(candidates, key=lambda e: (moves[e][3], e)))
        width_hist.update(moves[e][3] for e in candidates)
    assert report['tested_pairs'] == stats.pop('ordered_pairs') == 2602
    assert report['stats'] == dict(stats)
    assert {(e['kept'], e['omitted']) for e in report['survivors']['width_one_independent']} == width_positive
    assert not report['survivors']['tensor_finite_arms_independent']
    assert {str(k): v for k, v in width_hist.items()} == report['width_one_independent']['savings_hist']
    assert width_hist == {1: 685}
    paid = Counter({int(k): v for k, v in frozen['price']['after']['P'].items()})
    productive = Counter({int(k): v for k, v in frozen['price']['after']['T'].items()})
    productive.subtract(paid)
    upper = sum(n * price.price(r)[n > 0] for r, n in productive.items() if n)
    assert upper <= Q(report['tensor_independent']['raw_margin_upper']) < 0
    assert upper + 17 * width_hist[1] > 0
    return dict(status='PASS_INDEPENDENT_CLIFFORD_PROJECTIVE_AVAILABILITY_AND_PRICE',
                moves=len(moves), groups=len(groups), ordered_pairs=report['tested_pairs'],
                source_bypasses_independent=0, identical_output_cosets=0,
                width_one_paid_savings_upper=17 * width_hist[1], stats=dict(stats),
                audited_tensor_raw_upper=price.encode((upper, upper))[1],
                synthetic_control=synthetic_control(independent),
                pins={'prior/audit.py': PRIOR_AUDIT, 'TWO-ARM.json': sha256(raw).hexdigest(), **a.PINS})


if __name__ == '__main__':
    assert __debug__
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    print(json.dumps(run(**vars(p.parse_args())), indent=2, sort_keys=True))
