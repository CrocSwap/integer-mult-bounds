"""Independent modular independence and exact signed-map census."""
from bisect import bisect_left
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import gzip
import json

PINS = {
    'native/WORD.json.gz': 'c1caec11ca3ee264ef03018dd91037eac10c3e28950c4c525ee1b4bf5ee210e2',
    'canonical/research/shared-wire-split-composition/frozen/native_verify.py': '3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38',
}
MOD = 65537


def checked(root, name):
    path = root / name
    data = path.read_bytes()
    if sha256(data).hexdigest() != PINS[name]:
        raise ValueError(f'SHA-256 mismatch: {name}')
    return path, data


def span(rows):
    result = {0}
    for x in rows:
        result.update(x ^ y for y in tuple(result))
    return frozenset(result)


@cache
def coefficient(raw):
    x = Q(raw)
    return x.numerator * pow(x.denominator, -1, MOD) % MOD


def push(basis, vector):
    v = vector.copy()
    while v:
        pivot = max(v)
        if pivot not in basis:
            inv = pow(v[pivot], -1, MOD)
            basis[pivot] = {j: x * inv % MOD for j, x in v.items()}
            return True
        c = v[pivot]
        for j, x in basis[pivot].items():
            if y := (v.get(j, 0) - c * x) % MOD:
                v[j] = y
            else:
                v.pop(j, None)
    return False


def run(inputs, deps, receipt):
    w = json.loads(gzip.decompress(checked(inputs, 'native/WORD.json.gz')[1]))
    path, _ = checked(deps, 'canonical/research/shared-wire-split-composition/frozen/native_verify.py')
    spec = spec_from_file_location('independent_native_verifier', path)
    interp = module_from_spec(spec)
    spec.loader.exec_module(interp)
    raw = receipt.read_bytes()
    report = json.loads(raw)
    rows = [{i: 1} for i in range(w['public'])] + [{} for _ in range(w['owned_fields'])]
    frames = [interp.frame(u, 9) for u in w['frames']]
    invs = [interp.adjoint(circuit) for circuit in frames]
    space = [span(frame) for frame in w['frames']]
    label = {x: i for i, x in reversed(list(enumerate(space)))}
    cosets = [span(x | (z << 9) for x, z, _ in interp.tableau(inv)[9:]) for inv in invs]
    touches = defaultdict(list)
    signed = defaultdict(list)
    targets = defaultdict(list)
    all_maps = {}
    hist = Counter()
    by_event = {e['event']: e for e in report['stock']}
    adjacent = 0
    for t, (op, j, *a) in enumerate(w['program']):
        if op == 'MOVE':
            f, g, owned = a
            e = by_event[t]
            assert (j, f, g, owned) == (e['role'], e['source'], e['target'], e['owned'])
            assert (label[space[f]], label[space[g]]) == (e['canonical_source'], e['canonical_target'])
            rank = abs(len(w['frames'][f]) - len(w['frames'][g]))
            assert rank == e['rank'] and rows[j]
            hist[rank] += 1
            if (f, g) not in all_maps:
                all_maps[f, g] = interp.tableau(invs[f] + frames[g])
            signed[all_maps[f, g]].append((t, rank, rows[j]))
            targets[cosets[g]].append((t, rank, rows[j]))
            if touches[j] and touches[j][-1] in by_event:
                adjacent += 1
        elif op == 'ADD':
            arow, brow = rows[j], rows[a[0]]
            c = coefficient(a[1])
            rows[j] = {k: v for k in arow.keys() | brow.keys() if (v := (arow.get(k, 0) + c * brow.get(k, 0)) % MOD)}
        elif op == 'SCALE':
            rows[j] = {k: (v * coefficient(a[0])) % MOD for k, v in rows[j].items()}
        elif op == 'COPY':
            assert not rows[j]
            rows[j] = {k: (v * coefficient(a[1])) % MOD for k, v in rows[a[0]].items()}
        else:
            assert op in ('INIT', 'CLEAR')
            rows[j] = {}
        touches[j].append(t)
        if op in ('ADD', 'COPY'):
            touches[a[0]].append(t)
    assert adjacent == len(report['serial_runs']) == 0
    for t, e in by_event.items():
        timeline = touches[e['role']]
        i = bisect_left(timeline, t)
        assert timeline[i] == t
        assert (timeline[i-1] + 1 if i else 0) == e['earliest_clock']
        assert (timeline[i+1] if i+1 < len(timeline) else len(w['program'])) == e['latest_clock']
    proved = {}
    for group, events in signed.items():
        basis = {}
        assert all(push(basis, v) for _, _, v in events)
        key = sha256(json.dumps(group, separators=(',', ':')).encode()).hexdigest()
        proved[key] = [t for t, _, _ in events]
    assert len(proved) == report['signed_quotient_classes']
    assert len(targets) == report['target_monomial_cosets']
    for events in targets.values():
        basis = {}
        assert all(push(basis, v) for _, _, v in events)
    assert report['target_coset_basis_size'] == len(by_event)
    assert not report['target_coset_all_clock_discarded'] and not report['target_coset_chronological_discarded']
    for row in report['class_report']['signed_quotient']:
        assert proved.pop(row['group']) == row['basis_events']
    assert not proved
    return dict(status='PASS_INDEPENDENT_SIGNED_OPERATOR_AND_MODULAR_INDEPENDENCE',
                quotient_classes=len(signed), target_cosets=len(targets), original_moves=sum(hist.values()),
                contact_free_adjacent_pairs=adjacent, modulus=MOD, exact_rational_rank_lower=sum(hist.values()),
                target_coset_rational_rank_lower=sum(hist.values()),
                source_pins=PINS, receipt_sha256=sha256(raw).hexdigest())


if __name__ == '__main__':
    assert __debug__
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('inputs', 'deps', 'receipt'):
        p.add_argument(name, type=Path)
    print(json.dumps(run(**vars(p.parse_args())), indent=2, sort_keys=True))
