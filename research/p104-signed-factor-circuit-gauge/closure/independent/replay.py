"""Independent minimum-support replay using the positive signed prefix."""
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from math import gcd, lcm
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import argv, implementation, version_info

N = 36
CAP = 20
PINS = {
    'inputs/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'inputs/R195.json': 'f6091c7c63b21145077808bbdacc61431f641d0da37f9fa648aea4b7ead3b472',
    'inputs/7113-SHA256.json': '064e11ecfedce9937ea1782e5baee37e89b3c9eebabed5b4a9ba84f412bbe078',
}
HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'


def unique(items):
    obj = dict(items)
    assert len(items) == len(obj)
    return obj


def read(root, path):
    raw = (root / path).read_bytes()
    assert sha256(raw).hexdigest() == PINS[path], path
    return loads(raw, object_pairs_hook=unique)


def unit(j):
    return [Q(i == j) for i in range(N)]


def dot(u, v):
    return sum(a * b for a, b in zip(u, v, strict=True) if a and b)


def axpy(u, v, scale):
    return [a + scale * b for a, b in zip(u, v, strict=True)] if scale else u


def signed_prefix(tape, sign):
    rows, inverse_cols = [unit(i) for i in range(N)], [unit(i) for i in range(N)]
    factors, labels = [], []
    for clock, event in enumerate(tape):
        if event[0] == 'B':
            continue
        if event[0] == 'J':
            _, host, (a, b, c, d), _ = event
            assert len({a, b, c, d}) == 4
            legs = [(b, a, 1), (c, d, -1)]
        else:
            assert event[0] == 'A'
            _, operation, destination, *args = event
            if operation == 'QUERY':
                source, exponent = args
                assert exponent == -1
                host, legs = 0, [(destination, source, 1)]
            elif operation == 'ADD':
                source, weight = args
                weight = Q(weight)
                rows[destination] = axpy(rows[destination], rows[source], weight)
                inverse_cols[source] = axpy(inverse_cols[source], inverse_cols[destination], -weight)
                continue
            elif operation == 'SCALE':
                weight = Q(args[0])
                rows[destination] = [x * weight for x in rows[destination]]
                inverse_cols[destination] = [x / weight for x in inverse_cols[destination]]
                continue
            elif operation == 'SWAP':
                source, = args
                rows[destination], rows[source] = rows[source], rows[destination]
                inverse_cols[destination], inverse_cols[source] = inverse_cols[source], inverse_cols[destination]
                continue
            else:
                assert operation in ('IDLE_ONE', 'LAMBDA')
                continue
        for leg, (dst, src, weight) in enumerate(legs):
            image = [2 * weight * x for x in inverse_cols[dst]]
            covector = rows[src]
            assert any(image) and any(covector) and not dot(image, covector)
            factors.append((image, covector))
            labels.append([clock, host, leg, dst, src, weight])
            rows[dst] = axpy(rows[dst], rows[src], sign * weight)
            inverse_cols[src] = axpy(inverse_cols[src], inverse_cols[dst], -sign * weight)
    for i in range(N):
        expected = [sign * x for x in unit(i)]
        assert rows[i] == expected and inverse_cols[i] == expected
    return factors, labels


def apply(word, column, inverse=False):
    for image, covector in reversed(word) if inverse else word:
        coefficient = dot(covector, column)
        column = axpy(column, image, -coefficient if inverse else coefficient)
    return column


def primitive(row):
    g = gcd(*row)
    return [x // g for x in row] if g > 1 else row


def integral(row):
    denominator = lcm(*(x.denominator for x in row))
    return primitive([int(denominator * x) for x in row])


def echelon(rows):
    width = len(rows[0])
    basis = {}
    for row in rows:
        row = integral(row)
        for pivot, old in sorted(basis.items()):
            if row[pivot]:
                a, b = old[pivot], row[pivot]
                row = primitive([a * x - b * y for x, y in zip(row, old, strict=True)])
        pivot = next((i for i, v in enumerate(row) if v), None)
        if pivot is not None:
            basis[pivot] = row
    assert all(len(row) == width for row in basis.values())
    return basis


def min_support(vectors):
    equations = list(zip(*vectors, strict=True))
    basis = echelon(equations)
    free = sorted(set(range(len(vectors))) - basis.keys())
    assert len(free) == 2
    kernel = []
    for selected in free:
        vector = [Q(i == selected) for i in range(len(vectors))]
        for pivot, row in sorted(basis.items(), reverse=True):
            vector[pivot] = -Q(dot(row, vector)) / row[pivot]
        assert all(not dot(row, vector) for row in equations)
        kernel.append(integral(vector))
    # A minimum vector either has no cancellable coordinate or satisfies at
    # least one nontrivial coordinate-zero equation. Test every such equation.
    first, second = kernel
    supports = {}
    for a, b in [(1, 0), (0, 1), *((y, -x) for x, y in zip(first, second, strict=True) if x or y)]:
        vector = [a * x + b * y for x, y in zip(first, second, strict=True)]
        support = tuple(i for i, value in enumerate(vector) if value)
        assert support and all(not dot(row, vector) for row in equations)
        supports.setdefault(support, primitive(vector))
    minimum = min(map(len, supports))
    tied = sorted(key for key in supports if len(key) == minimum)
    return {'rank': len(basis), 'kernel': kernel, 'ties': tied,
            'witness': supports[tied[0]], 'supports_checked': len(supports)}


def literal_rank(original, conjugates, selected):
    selected = set(selected)
    kept = [factor for i, factor in enumerate(original) if i not in selected]
    # The product of increasing-index conjugates applies in reverse order.
    grouped = [factor for i, factor in reversed(list(enumerate(conjugates))) if i in selected]
    columns = []
    for j in range(N):
        base = unit(j)
        actual = apply(original, apply(kept, base, inverse=True))
        assert actual == apply(grouped, base), (sorted(selected), j)
        columns.append(axpy(actual, base, -1))
    return len(echelon(columns))


def stop(*_):
    raise TimeoutError(f'{CAP}-second replay cap')


def main():
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3, 12)
    assert len(argv) == 2, 'pass the pinned #7435 package root'
    root = Path(argv[1]).resolve()
    signal(SIGALRM, stop)
    alarm(CAP)
    caller = read(root, 'inputs/CALLER.json')
    manifest = read(root, 'inputs/7113-SHA256.json')
    predecessor = read(root, 'inputs/R195.json')
    assert manifest['expected/ODD-TYPE-AB-CALLER.json'] == PINS['inputs/CALLER.json']
    assert (predecessor['head'], predecessor['caller']) == (HEAD, CALLER)
    tape = caller['events']
    assert len(tape) == 4783 and caller['types']['A']['roles'] == N
    original, labels = signed_prefix(tape, -1)
    conjugates, positive_labels = signed_prefix(tape, 1)
    assert len(labels) == 38 and labels == positive_labels == predecessor['factor_labels']
    for i in range(N):
        assert apply(original, unit(i)) == [-x for x in unit(i)]
    image, covector = original[-1]
    mutation = [*original[:-1], ([2 * x for x in image], covector)]
    assert any(apply(mutation, unit(i)) != [-x for x in unit(i)] for i in range(N))
    image_receipt = min_support([u for u, _ in conjugates])
    covector_receipt = min_support([v for _, v in conjugates])
    tied = image_receipt['ties'] + covector_receipt['ties']
    best = min(tied, key=lambda key: (len(key), key))
    controls = [(0, 36), (0, 2, 36), (0, 1, 2, 36), tuple(range(38))]
    assert [literal_rank(original, conjugates, ids) for ids in controls] == [2, 3, 4, 36]
    rank = literal_rank(original, conjugates, best)
    assert rank < len(best)
    alarm(0)
    print(dumps({'head': HEAD, 'caller': CALLER, 'pins': PINS, 'runner_cap_seconds': CAP,
                 'labels': labels, 'images': image_receipt, 'covectors': covector_receipt,
                 'least_support': best, 'literal_rank': rank, 'corrupted_factor_rejected': True},
                indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
