"""Independently check the R211 IDLE_ONE fusion reflection gate."""
from ast import Assign, Name, literal_eval, parse
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from math import prod
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import argv, implementation, version_info

N = 36
CAP = 30
NEGATIVE = {8, 9}
PINS = {
    'inputs/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'inputs/7113-SHA256.json': '064e11ecfedce9937ea1782e5baee37e89b3c9eebabed5b4a9ba84f412bbe078',
    'inputs/7113-signed-child.py': 'ef03444360f02225138be9b38e2f9a85f313eeaa910d63a365de0f16d228cb8b',
}
HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'


def no_duplicates(items):
    out = dict(items)
    assert len(out) == len(items)
    return out


def read(root, name):
    raw = (root / name).read_bytes()
    assert sha256(raw).hexdigest() == PINS[name], name
    return loads(raw, object_pairs_hook=no_duplicates)


def lower(caller, omitted=()):
    atoms, idle = [], []
    alpha = Q(caller['types']['A']['alpha2'])
    assert alpha == -1
    for clock, event in enumerate(caller['events']):
        if event[0] == 'B':
            continue
        if event[0] == 'J':
            _, stage, (a, b, c, d), _ = event
            assert len({a, b, c, d}) == 4
            atoms.extend([('add', b, a, Q(1)), ('add', c, d, alpha)])
            if stage in NEGATIVE:
                atoms.extend(('scale', row, row, Q(-1)) for row in (a, b, c, d))
            continue
        assert event[0] == 'A'
        _, op, row, *args = event
        if op == 'ADD':
            atoms.append(('add', row, args[0], Q(args[1])))
        elif op == 'SCALE':
            atoms.append(('scale', row, row, Q(args[0])))
        elif op == 'SWAP':
            atoms.append(('swap', row, args[0], Q(1)))
        elif op == 'QUERY':
            src, exp = args
            assert exp == -1
            atoms.append(('add', row, src, Q(1)))
        elif op == 'IDLE_ONE':
            stages, = args
            assert len(set(stages)) == len(stages)
            body = prod(-1 if i in NEGATIVE else 1 for i in stages)
            idle.append((clock, row, tuple(stages), len(atoms), body))
            if body != 1 and clock not in omitted:
                atoms.append(('scale', row, row, Q(body)))
        else:
            assert op == 'LAMBDA'  # Common q²=1 specialization.
    return atoms, idle


def vector(word, coordinate, mode):
    x = {coordinate: Q(1)}
    for kind, dest, source, a in word if mode == 'forward' else reversed(word):
        if kind == 'add':
            if mode == 'row':
                dest, source = source, dest
            c = x.get(source)
            if c:
                y = x.get(dest, 0) + (-a if mode == 'inverse' else a) * c
                if y:
                    x[dest] = y
                else:
                    x.pop(dest, None)
        elif kind == 'swap':
            u, v = x.pop(dest, None), x.pop(source, None)
            if u:
                x[source] = u
            if v:
                x[dest] = v
        elif dest in x:
            x[dest] = x[dest] / a if mode == 'inverse' else x[dest] * a
    return x


def projector(word, entry):
    clock, row, stages, index, sign = entry
    assert sign == -1
    prefix = word[:index]
    u, v = vector(prefix, row, 'inverse'), vector(prefix, row, 'row')
    assert sum(x * v.get(i, 0) for i, x in u.items()) == 1
    return {(i, j): x * y for i, x in u.items() for j, y in v.items()}


def reflection(p, x):
    out = x.copy()
    for (i, j), value in p.items():
        if j in x:
            out[i] = out.get(i, 0) - 2 * value * x[j]
    return {i: v for i, v in out.items() if v}


def stop(*_):
    raise TimeoutError('R211 independent 30-second cap')


def main():
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3, 12)
    assert len(argv) == 2, 'pass the authenticated #7435 package root'
    root = Path(argv[1]).resolve()
    signal(SIGALRM, stop)
    alarm(CAP)
    caller = read(root, 'inputs/CALLER.json')
    manifest = read(root, 'inputs/7113-SHA256.json')
    assert manifest['expected/ODD-TYPE-AB-CALLER.json'] == PINS['inputs/CALLER.json']
    child_path = 'inputs/7113-signed-child.py'
    child = (root / child_path).read_bytes()
    assert sha256(child).hexdigest() == PINS[child_path] == manifest['replay/supplier7112/short-caller/signed_child.py']
    binary = next(literal_eval(n.value) for n in parse(child).body
                  if isinstance(n, Assign) and isinstance(n.targets[0], Name) and n.targets[0].id == 'C')
    for sign, twice_eigen in ((1, (2, 0)), (-1, (0, 2))):
        for i in range(2):
            assert tuple(binary[i][0][k] + sign*binary[i][1][k] for k in range(2)) == tuple(sign**i*x for x in twice_eigen)
    assert len(caller['events']) == 4783 and caller['types']['A']['roles'] == N
    word, entries = lower(caller)
    early = [e for e in entries if 8 in e[2]]
    late = [e for e in entries if 9 in e[2]]
    assert (len(entries), len(early), len(late)) == (30, 14, 16)
    assert all(a[0] < b[0] and set(a[2]).isdisjoint(b[2]) and a[4] == b[4] == -1 for a in early for b in late)
    diag = []
    for q, z, *bits in caller['types']['A']['diagonal']:
        assert len(bits) == 17 and z == 0 and all(b in (0, 1) for b in bits)
        diag.append(Q((-1) ** (bits[7] + bits[8])))
    for j in range(N):
        assert vector(word, j, 'forward') == {j: diag[j]}
    projectors = {e[0]: projector(word, e) for e in entries}
    cases = []
    for a in early:
        for b in late:
            left, right = projectors[a[0]], projectors[b[0]]
            first = next((p for p in sorted(left.keys() | right.keys()) if left.get(p, 0) != right.get(p, 0)), None)
            cases.append({'clocks': [a[0], b[0]], 'roles': [a[1], b[1]], 'ranks': [8*len(a[2]), 8*len(b[2])],
                          'masks': [a[2], b[2]],
                          'witness': None if first is None else [*first, str(left.get(first, 0)), str(right.get(first, 0))]})
    assert len(cases) == 224
    # H(r)+H(s)-H(r+s) is strictly increasing in either positive input
    # for H(r)=r^(1−κ), 0<κ<1. Break ties by chronological clocks.
    best = min(cases, key=lambda c: (-c['ranks'][0], -c['ranks'][1], c['clocks']))
    first, second = best['clocks']
    omitted, _ = lower(caller, (first, second))
    first_wrong = None
    for j in range(N):
        literal = vector(omitted, j, 'forward')
        grouped = reflection(projectors[second], reflection(projectors[first], {j: Q(1)}))
        assert literal == {i: diag[i] * x for i, x in grouped.items()}
        if literal != {j: diag[j]} and first_wrong is None:
            i = min(i for i in literal.keys() | {j} if literal.get(i, 0) != (diag[j] if i == j else 0))
            first_wrong = [i, j, str(diag[j] if i == j else 0), str(literal.get(i, 0))]
    assert (first_wrong is None) == (best['witness'] is None)
    alarm(0)
    print(dumps({'head': HEAD, 'caller': CALLER, 'pins': PINS, 'profile': {'q': 1, 'negative_D': sorted(NEGATIVE)},
                 'endpoint': list(map(str, diag)), 'early': len(early), 'late': len(late), 'cases': cases,
                 'survivors': [c for c in cases if c['witness'] is None], 'best': best,
                 'literal_omission_first_wrong': first_wrong, 'runner_cap_seconds': CAP}, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
