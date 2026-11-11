"""Independent primitive-row, signed-tableau and source-availability audit."""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from math import gcd, lcm
from pathlib import Path
import argparse
import gzip
import json

PINS = {
    'inputs/native/WORD.json.gz': '75061d1e4b354e4cf36b690f30ddb2b257ed2f4e86509f87e17bb0f63eca126f',
    'inputs/native/RESULT.json': '75f34132b5b12b1a92f13b7a7c47ea3857f1955403090ae06b38dd9cf18aeb49',
    'deps/canonical/research/shared-wire-split-composition/frozen/native_verify.py': '3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38',
    'deps/round11/frontier/independent_adapter_price.py': '2a46157d156bdfc0e892289005fd3fb7c23708de48c9abd90c1914b0372bc726',
}


def checked(root, key):
    p = root / key
    raw = p.read_bytes()
    assert sha256(raw).hexdigest() == PINS[key]
    return p, raw


def load(root, key):
    path, _ = checked(root, key)
    spec = spec_from_file_location(path.stem, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def span(vectors):
    out = {0}
    for x in vectors:
        out.update(x ^ y for y in tuple(out))
    return frozenset(out)


def primitive(row):
    den = lcm(*(x.denominator for x in row.values()))
    z = [(i, x.numerator * (den // x.denominator)) for i, x in sorted(row.items())]
    g = gcd(*(v for _, v in z)) * (1 if z[0][1] > 0 else -1)
    return tuple((i, v // g) for i, v in z)


def run(root):
    w = json.loads(gzip.decompress(checked(root, 'inputs/native/WORD.json.gz')[1]))
    frozen = json.loads(checked(root, 'inputs/native/RESULT.json')[1])
    interp = load(root, 'deps/canonical/research/shared-wire-split-composition/frozen/native_verify.py')
    price = load(root, 'deps/round11/frontier/independent_adapter_price.py')
    typed_raw = (root / 'TYPED.json').read_bytes()
    gate_raw = (root / 'GATE.json').read_bytes()
    typed, gate = json.loads(typed_raw), json.loads(gate_raw)
    frames = [interp.frame(f, 9) for f in w['frames']]
    inverses = [interp.adjoint(f) for f in frames]
    cosets = [span(x | (z << 9) for x, z, _ in interp.tableau(f)[9:]) for f in inverses]
    target_rows = defaultdict(set)
    claimed = {}
    for group in typed['eligible_group_details']:
        row = primitive({j: Q(c) for j, c in group['projective_row']})
        claimed[row] = [e['event'] for e in group['members']]
        for e in group['members']:
            target_rows[cosets[e['source']], len(row)].add(row)
    positions = [*w['initial'], *([None] * w['owned_fields'])]
    rows = [{j: Q(1)} for j in range(w['public'])] + [{} for _ in range(w['owned_fields'])]
    earliest = defaultdict(dict)
    by_row = defaultdict(list)
    by_event = {}
    touches = defaultdict(list)

    def record(j, cut):
        if not rows[j]:
            return
        f = cosets[positions[j]]
        choices = target_rows.get((f, len(rows[j])))
        if choices:
            k = primitive(rows[j])
            if k in choices:
                earliest[f, k].setdefault(j, cut)

    for j in range(w['public']):
        record(j, 0)
    for t, (op, j, *a) in enumerate(w['program']):
        touches[j].append(t)
        if op == 'MOVE':
            f, g, own = a
            assert positions[j] == f and rows[j] and own == (j >= w['public'])
            k = primitive(rows[j])
            by_row[k].append(t)
            by_event[t] = (j, f, g, abs(len(w['frames'][g]) - len(w['frames'][f])))
            positions[j] = g
        elif op == 'ADD':
            source = a[0]
            assert positions[j] == positions[source] == a[-1]
            touches[source].append(t)
            c = Q(a[1]); x, y = rows[j], rows[source]
            rows[j] = {i: v for i in x.keys() | y.keys() if (v := x.get(i, 0) + c * y.get(i, 0))}
        elif op == 'COPY':
            source = a[0]
            assert not rows[j] and positions[j] == positions[source] == a[-1]
            touches[source].append(t)
            rows[j] = {i: Q(a[1]) * x for i, x in rows[source].items()}
        elif op == 'SCALE':
            rows[j] = {i: Q(a[0]) * x for i, x in rows[j].items()}
        else:
            assert op in ('INIT', 'CLEAR')
            rows[j] = {}
            positions[j] = a[0] if op == 'INIT' else None
        record(j, t + 1)
    assert len(by_event) == 6281
    target = {k: v for k, v in by_row.items() if len({cosets[by_event[e][2]] for e in v}) > 1}
    assert claimed == target and len(by_row) == typed['row_groups']
    deadline = {a: b for trace in touches.values() for a, b in zip(trace, trace[1:]) if a in by_event}

    @cache
    def direction(f, g):
        return span(x for x, _, _ in interp.tableau(inverses[g] + frames[f])[9:])

    circular = 0
    total = 0
    credit = Counter()
    for k, members in target.items():
        keep = min(members, key=lambda e: (by_event[e][3], e))
        credit.update(by_event[e][3] for e in members if e != keep)
        for keep in members:
            _, f, g, _ = by_event[keep]
            for remove in members:
                if keep == remove:
                    continue
                total += 1
                j, _, h, _ = by_event[remove]
                wanted = direction(f, h)
                if wanted != {0} and wanted != direction(f, g):
                    continue
                close = deadline.get(remove, len(w['program']))
                sources = earliest[cosets[f], k]
                assert min(sources.values()) <= close and wanted == {0}
                assert min(sources.items(), key=lambda z: (z[1], z[0])) == (j, remove + 1)
                assert all(t > close or (role == j and t > remove) for role, t in sources.items())
                circular += 1
    assert total == gate['tested_pairs'] and circular == gate['passed_by_mode']['support_any_original_resident']
    assert not gate['survivors']['support_independent_original_resident']
    assert {str(k): n for k, n in credit.items()} == typed['skipped_child_hist']
    p = Counter({int(k): n for k, n in frozen['price']['after']['P'].items()})
    t = Counter({int(k): n for k, n in frozen['price']['after']['T'].items()})
    t.subtract(p)
    upper = sum(n * price.price(r)[n > 0] for r, n in t.items() if n)
    assert upper <= Q(typed['baseline'][1]) < 0
    return dict(status='PASS_INDEPENDENT_PROJECTIVE_AND_TYPED_AVAILABILITY', moves=len(by_event),
                row_classes=len(by_row), eligible_groups=len(target), tested_pairs=total,
                circular_rank_zero_pairs=circular, independent_pairs=0, source_pins=PINS,
                audited_baseline_upper=price.encode((upper, upper))[1],
                receipts={'TYPED.json': sha256(typed_raw).hexdigest(), 'GATE.json': sha256(gate_raw).hexdigest()})


if __name__ == '__main__':
    assert __debug__
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    print(json.dumps(run(**vars(p.parse_args())), indent=2, sort_keys=True))
