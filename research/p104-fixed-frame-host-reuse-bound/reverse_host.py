"""Exact host supports in gathered, fixed-prefix coordinates at unit bodies."""
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from math import gcd, lcm
from pathlib import Path
from signal import alarm

ROOT = Path(__file__).resolve().parent
N = 36
SELECTED = (0, 1, 2, 4, 6, 8, 10, 12, 14, 18, 19, 20, 22, 24, 26, 28, 30, 32, 34, 36)
PINS = {
    'inputs/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'inputs/R209-REVERSE.json': '3992ba3f17645e834f1d5aed3551d16e07a27e6234b2ef814e3dd87e1b00bb75',
}


def unit(i):
    return [Q(i == j) for j in range(N)]


def dot(a, b):
    return sum(x*y for x, y in zip(a, b, strict=True) if x and y)


def plus(a, b, k):
    return [x + k*y for x, y in zip(a, b, strict=True)] if k else a.copy()


def prefix(tape):
    rows = [unit(i) for i in range(N)]
    inverse_cols = [unit(i) for i in range(N)]
    factors, hosts = [], []

    def shear(dest, source, k):
        rows[dest] = plus(rows[dest], rows[source], k)
        inverse_cols[source] = plus(inverse_cols[source], inverse_cols[dest], -k)

    for clock, event in enumerate(tape):
        if event[0] == 'B':
            continue
        if event[0] == 'J':
            _, host, axes, _ = event
            a, b, c, d = axes
            assert len(set(axes)) == 4
            hosts.append((host, clock, len(factors), axes,
                          [inverse_cols[i].copy() for i in axes],
                          [rows[i].copy() for i in axes]))
            legs = ((b, a, 1), (c, d, -1))
        else:
            assert event[0] == 'A'
            _, op, r, *args = event
            if op == 'ADD':
                shear(r, args[0], Q(args[1]))
                continue
            if op == 'SWAP':
                s, = args
                rows[r], rows[s] = rows[s], rows[r]
                inverse_cols[r], inverse_cols[s] = inverse_cols[s], inverse_cols[r]
                continue
            if op == 'SCALE':
                scale = Q(args[0])
                rows[r] = [scale*v for v in rows[r]]
                inverse_cols[r] = [v/scale for v in inverse_cols[r]]
                continue
            if op in ('IDLE_ONE', 'LAMBDA'):
                continue
            assert op == 'QUERY' and args[1] == -1
            legs = ((r, args[0], 1),)
        for dest, source, coefficient in legs:
            image = [2*coefficient*v for v in inverse_cols[dest]]
            covector = rows[source].copy()
            assert not dot(covector, image)
            factors.append((image, covector))
            shear(dest, source, -coefficient)
    assert rows == inverse_cols == [[-x for x in unit(i)] for i in range(N)]
    assert len(factors) == 38 and [x[0] for x in hosts] == list(range(1, 18))
    return factors, hosts


def apply(factors, vec, inverse=False):
    for u, v in (reversed(factors) if inverse else factors):
        vec = plus(vec, u, (-1 if inverse else 1) * dot(v, vec))
    return vec


def carry_row(factors, row):
    # For S=A_j...A_i, row times S^{-1} applies A_i^{-1},...,A_j^{-1}
    # to the row from left to right.
    for u, v in factors:
        row = plus(row, v, -dot(row, u))
    return row


def primitive(vec):
    denominator = lcm(*(x.denominator for x in vec))
    values = [int(denominator*x) for x in vec]
    common = gcd(*values)
    return [x//common for x in values] if common else values


def basis(rows):
    echelon = {}
    for row in rows:
        row = primitive(row)
        for k, old in sorted(echelon.items()):
            if row[k]:
                row = primitive([x*old[k] - y*row[k] for x, y in zip(row, old, strict=True)])
        first = next((k for k, v in enumerate(row) if v), None)
        if first is not None:
            echelon[first] = row
    return echelon


def annihilator(rows):
    reduced = basis(rows)
    for free in sorted(set(range(N)) - reduced.keys()):
        x = unit(free)
        for pivot, row in sorted(reduced.items(), reverse=True):
            x[pivot] = -Q(dot(row, x))/row[pivot]
        assert all(not dot(x, row) for row in rows)
        yield x


def intersection_dimension(span, annihilating):
    # Coefficient vector c of the four old axes must satisfy K H c=0.
    equations = [[Q(dot(p, x)) for x in span] for p in annihilating]
    assert len(equations) == 17 and len(span) == 4
    return len(span) - len(basis(equations))


def main():
    assert __debug__
    alarm(30)
    src = {}
    for name, digest in PINS.items():
        raw = (ROOT / name).read_bytes()
        assert sha256(raw).hexdigest() == digest
        src[name] = loads(raw)
    tape = src['inputs/CALLER.json']['events']
    frozen = src['inputs/R209-REVERSE.json']
    assert len(tape) == 4783 and tuple(frozen['chosen']) == SELECTED
    assert frozen['head'] == 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
    assert frozen['caller'] == '07a76c5e2738882c0cb322278e56f6cae3c9885d'
    factors, hosts = prefix(tape)
    kept = [(j, v) for j, v in enumerate(factors) if j not in SELECTED]
    original_kept = [v for _, v in kept]
    target = [apply(factors, apply(original_kept, unit(i), inverse=True)) for i in range(N)]
    assert target == [[Q(x) for x in c] for c in frozen['target_columns']]
    delta = [plus(col, unit(i), -1) for i, col in enumerate(target)]
    gathered = (delta, list(zip(*delta, strict=True)))
    assert all(len(basis(rows)) == 19 for rows in gathered)
    annihilators = [list(annihilator(rows)) for rows in gathered]
    records = []
    for host, clock, first, axes, images, covectors in hosts[1:]:
        pair = set(range(first, first+2)) & set(SELECTED)
        assert len(pair) == 1
        index, = pair
        unselected_suffix = [v for j, v in kept if j > index]
        col = [apply(unselected_suffix, x) for x in images]
        row = [carry_row(unselected_suffix, x) for x in covectors]
        assert [[dot(v, u) for u in col] for v in row] == [[int(i == j) for j in range(4)] for i in range(4)]
        u, v = factors[index]
        old_u = apply(unselected_suffix, u)
        old_v = carry_row(unselected_suffix, v)
        assert len(basis([*col, old_u])) == len(basis([*row, old_v])) == 4
        bad_col = [x for i, x in enumerate(col) if dot(row[i], old_u) == 0]
        assert len(bad_col) < len(col) and len(basis([*bad_col, old_u])) > len(basis(bad_col))
        im, co = [intersection_dimension(span, ker) for span, ker in zip((col,row), annihilators, strict=True)]
        assert im == 23-len(basis([*gathered[0], *col]))
        assert co == 23-len(basis([*gathered[1], *row]))
        records.append({'host':host, 'clock':clock, 'axes':axes, 'selected_index':index,
                        'kept_suffix':[j for j, _ in kept if j>index],
                        'image_intersection':im, 'covector_intersection':co, 'supported':bool(im and co)})
    assert len(records) == 16
    alarm(0)
    print(dumps({'pins':PINS,'host_cap':16,'runner_cap_seconds':30,'sectors':[-1,1],
                 'rank':19,'chosen':SELECTED,'unit_bodies':True,'old_support_control':True,
                 'mutated_axis_control_rejected':True,'records':records,
                 'missing_hosts':[r['host'] for r in records if not r['supported']]},
                indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
