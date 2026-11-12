"""Exact non-unit signed profile from literal sparse prefix applications."""
from ast import Assign, Name, literal_eval, parse
from fractions import Fraction as F
from hashlib import sha256
from json import dumps, loads
from math import prod
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import argv, implementation, version_info

N = 36
CAP = 30
HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
CHOSEN = (0, 1, 2, 4, 6, 8, 10, 12, 14, 18, 19, 20, 22, 24, 26, 28, 30, 32, 34, 36)
UNIT_SHA = '3992ba3f17645e834f1d5aed3551d16e07a27e6234b2ef814e3dd87e1b00bb75'
PINS = {
    'inputs/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'inputs/R195.json': 'f6091c7c63b21145077808bbdacc61431f641d0da37f9fa648aea4b7ead3b472',
    'inputs/7113-SHA256.json': '064e11ecfedce9937ea1782e5baee37e89b3c9eebabed5b4a9ba84f412bbe078',
    'inputs/7113-signed-child.py': 'ef03444360f02225138be9b38e2f9a85f313eeaa910d63a365de0f16d228cb8b',
}


def unique(items):
    out = dict(items)
    assert len(out) == len(items)
    return out


def pin(root, name):
    raw = (root / name).read_bytes()
    assert sha256(raw).hexdigest() == PINS[name], name
    return raw


def steps(caller, sign, omit_one_body=False):
    result, labels = [], []
    for clock, event in enumerate(caller['events']):
        if event[0] == 'B':
            continue
        if event[0] == 'J':
            _, host, (a, b, c, d), _ = event
            assert len({a, b, c, d}) == 4
            alpha = F(caller['types']['A']['alpha2'])
            assert alpha == -1
            for leg, (dst, src, coeff) in enumerate(((b, a, 1), (c, d, int(alpha)))):
                labels.append(([clock, host, leg, dst, src, coeff], len(result)))
                result.append(('add', dst, src, F(sign * coeff)))
            if host == 8:
                for row in (a, b, c, d):
                    if not (omit_one_body and row == a):
                        result.append(('scale', row, row, F(-1)))
            continue
        assert event[0] == 'A'
        _, op, dst, *args = event
        if op == 'ADD':
            src, coeff = args
            result.append(('add', dst, src, F(coeff)))
        elif op == 'QUERY':
            src, exp = args
            assert exp == -1
            labels.append(([clock, 0, 0, dst, src, 1], len(result)))
            result.append(('add', dst, src, F(sign)))
        elif op == 'SCALE':
            result.append(('scale', dst, dst, F(args[0])))
        elif op == 'SWAP':
            result.append(('swap', dst, args[0], F(1)))
        elif op == 'IDLE_ONE':
            if args[0].count(8) % 2:
                result.append(('scale', dst, dst, F(-1)))
        else:
            assert op == 'LAMBDA' and sign * sign == 1
    return result, labels


def replay(word, coordinate, inverse=False, pullback=False):
    assert not (inverse and pullback)
    out = [F(0)] * N
    out[coordinate] = F(1)
    for op, dst, src, factor in reversed(word) if inverse or pullback else word:
        if op == 'add':
            if pullback:
                dst, src = src, dst
            if out[src]:
                out[dst] += (-factor if inverse else factor) * out[src]
        elif op == 'swap':
            out[dst], out[src] = out[src], out[dst]
        elif out[dst]:
            out[dst] = out[dst] / factor if inverse else out[dst] * factor
    return out


def dot(u, v):
    return sum(a * b for a, b in zip(u, v, strict=True) if a and b)


def relative(word, column, inverse=False):
    for u, v in reversed(word) if inverse else word:
        coefficient = dot(v, column)
        if coefficient:
            sign = -coefficient if inverse else coefficient
            column = [a + sign*b for a, b in zip(column, u, strict=True)]
    return column


def minor(columns):
    pivots, col_ids = [], []
    reduced = []
    for j, column in enumerate(columns):
        x = column.copy()
        for p, basis in zip(pivots, reduced, strict=True):
            if x[p]:
                a = x[p] / basis[p]
                x = [s - a*t for s, t in zip(x, basis, strict=True)]
        pivot = next((i for i, value in enumerate(x) if value), None)
        if pivot is not None:
            pivots.append(pivot)
            col_ids.append(j)
            reduced.append(x)
    # Operations use earlier selected columns only and leave the determinant
    # of the recorded ordered square minor unchanged. The reduced minor is triangular.
    return pivots, col_ids, prod(x[p] for p, x in zip(pivots, reduced, strict=True))


def stop(*_):
    raise TimeoutError('R210 independent 30-second cap')


def main():
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3, 12)
    assert len(argv) == 3, 'pass exact #7435 package root and R209 independent RESULT.json'
    root = Path(argv[1]).resolve()
    signal(SIGALRM, stop)
    alarm(CAP)
    raw_caller, raw_receipt, raw_manifest, signed_child = (pin(root, path) for path in PINS)
    caller, prior, manifest = [loads(x, object_pairs_hook=unique) for x in (raw_caller, raw_receipt, raw_manifest)]
    assert manifest['expected/ODD-TYPE-AB-CALLER.json'] == PINS['inputs/CALLER.json']
    assert manifest['replay/supplier7112/short-caller/signed_child.py'] == PINS['inputs/7113-signed-child.py']
    assert (prior['head'], prior['caller']) == (HEAD, CALLER)
    unit_raw = Path(argv[2]).read_bytes()
    assert sha256(unit_raw).hexdigest() == UNIT_SHA
    unit_receipt = loads(unit_raw, object_pairs_hook=unique)
    assert tuple(unit_receipt['chosen']) == CHOSEN
    binary = next(literal_eval(n.value) for n in parse(signed_child).body
                  if isinstance(n, Assign) and isinstance(n.targets[0], Name) and n.targets[0].id == 'C')
    for sign, twice_eigen in ((1, (2, 0)), (-1, (0, 2))):
        for i in range(2):
            assert tuple(binary[i][0][k] + sign*binary[i][1][k] for k in range(2)) == tuple(sign**i*x for x in twice_eigen)
    assert len(caller['events']) == 4783 and caller['types']['A']['roles'] == N
    expected = {sign: [] for sign in (1, -1)}
    for q, z, *bits in caller['types']['A']['diagonal']:
        assert z == 0 and len(bits) == 17 and all(bit in (0, 1) for bit in bits)
        for sign in (1, -1):
            expected[sign].append(F(sign) ** q * (-1) ** bits[7])
    signed = {}
    for sign in (1, -1):
        word, labels = steps(caller, sign)
        assert [a for a, _ in labels] == prior['factor_labels'] and len(labels) == 38
        signed[sign] = (word, labels)
        for j in range(N):
            assert replay(word, j) == [F(i == j) * expected[sign][j] for i in range(N)]
    broken, _ = steps(caller, 1, omit_one_body=True)
    bad = next(j for j in range(N) if replay(broken, j) != replay(signed[1][0], j))
    neg, labels = signed[-1]
    original = []
    for (_, _, _, dst, src, coefficient), cut in labels:
        prefix = neg[:cut]
        u = [2 * coefficient * x for x in replay(prefix, dst, inverse=True)]
        v = replay(prefix, src, pullback=True)
        assert not dot(u, v) and any(u) and any(v)
        original.append((u, v))
    complement = [f for i, f in enumerate(original) if i not in CHOSEN]
    assert len(complement) == 18
    columns = []
    for j in range(N):
        unit = [F(i == j) for i in range(N)]
        assert relative(original, unit) == [-x for x in unit]
        inverse = relative(complement, unit, inverse=True)
        assert relative(complement, inverse) == unit
        columns.append([-x - y for x, y in zip(inverse, unit, strict=True)])
    rows, cols, determinant = minor(columns)
    unit_target = [[F(x) for x in col] for col in unit_receipt['target_columns']]
    flipped_roles = [i for i in range(N) if i % 18 >= 9]
    diag = [(-1 if i in flipped_roles else 1) for i in range(N)]
    changes = []
    for j, col in enumerate(columns):
        for i, value in enumerate(col):
            target = value + int(i == j)
            before = unit_target[j][i]
            assert target == diag[i] * before * diag[j]
            if target != before:
                changes.append([i, j, str(target - before)])
    assert len(changes) == 153 and changes[0] == [27, 1, '4']
    alarm(0)
    assert len(rows) == 19 and determinant == 524288
    assert determinant and len(rows) == len(cols)
    print(dumps({'head': HEAD, 'caller': CALLER, 'pins': PINS, 'profile': {'D8': -1, 'other_D': 1, 'signs': [1, -1]},
                 'chosen': CHOSEN, 'untouched_count': 18, 'endpoint': {s: list(map(str, d)) for s, d in expected.items()},
                 'unit_result_sha256': UNIT_SHA, 'gauge_negative_roles': flipped_roles,
                 'unit_target_changes': len(changes), 'first_unit_target_change': changes[0],
                 'changed_body_scale_rejected_basis': bad, 'rank': len(rows), 'minor_rows': rows,
                 'minor_cols': cols, 'minor_determinant': str(determinant), 'runner_cap_seconds': CAP,
                 'displacement_columns': [list(map(str, c)) for c in columns]}, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
