"""Exact binary middle-factor witnesses. Standard library; read-only by default."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

LABELS = tuple(t for t in itertools.product(range(2), repeat=3) if any(t))
MIXED = {
    (0, 1, 0): ((0, 0, 1, 0, 1), (0, 1, 0, 3, 1)),
    (0, 1, 1): ((0, 0, 1, 2, 3), (0, 1, 0, 3, 1)),
    (1, 0, 0): ((0, 0, 1, 0, 3), (0, 1, 1, 0, 0)),
    (1, 0, 1): ((0, 0, 1, 0, 3), (0, 1, 3, 2, 2)),
    (1, 1, 0): ((0, 0, 1, 0, 3), (0, 1, 1, 2, 0)),
    (1, 1, 1): ((0, 0, 1, 0, 3), (0, 1, 3, 0, 2)),
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rank(vectors):
    pivots = {}
    for value in vectors:
        for bit in range(value.bit_length() - 1, -1, -1):
            if value >> bit & 1:
                if bit in pivots:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    return len(pivots)


def pairing(a, b):
    return (a & b).bit_count() % 2


def product_rows(left, right, r):
    """Multiply a column list by a row list, returning binary matrix rows."""
    result = [0] * r
    for x, y in zip(left, right, strict=True):
        for i in range(r):
            if x >> i & 1:
                result[i] ^= y
    return tuple(result)


def pure_block(d):
    """Only the inherited dimension-two/three pure blocks are needed."""
    need(d in (1, 2, 3), 'pure block dimension')
    if d == 1:
        return (1,) * 4, (1,) * 4, (1, 0, 0, 1), (1, 0, 1, 0)
    x = (1, 1, 2, 2, 3, 3) if d == 2 else tuple(range(1, 8)) + (1, 1)
    n = len(x)
    rows = tuple(sum(((v >> i) & 1) << j for j, v in enumerate(x)) for i in range(d))
    basis = list(rows)
    representatives = []
    for value in range(1 << n):
        if all(pairing(value, row) == 0 for row in rows):
            if rank(basis + [value]) > len(basis):
                basis.append(value)
                representatives.append(value)
                if len(representatives) == d:
                    break
    need(len(representatives) == d, 'quotient dimension')
    duals = []
    for i in range(d):
        candidates = [v for v in range(1 << n)
                      if all(pairing(v, row) == 0 for row in rows)
                      and all(pairing(v, rep) == int(i == j)
                              for j, rep in enumerate(representatives))]
        need(bool(candidates), 'dual existence')
        duals.append(candidates[0])
    u = tuple(sum(((row >> j) & 1) << i for i, row in enumerate(duals)) for j in range(n))
    v = tuple(sum(((row >> j) & 1) << i for i, row in enumerate(representatives)) for j in range(n))
    return x, x, u, v


PURE = {d: pure_block(d) for d in (1, 2, 3)}


def singleton(label):
    s, t, h = label
    for u in itertools.product(range(2), repeat=2):
        for v in itertools.product(range(2), repeat=2):
            if sum(u) % 2 == s and sum(v) % 2 == t and sum(a*b for a, b in zip(u, v)) % 2 == h:
                return (1, 1), (1, 1), u, v
    raise ValueError('pure singleton needs four columns')


def embed(block, indices):
    return tuple(tuple(sum(((value >> i) & 1) << index
                           for i, index in enumerate(indices)) for value in family)
                 for family in block)


def construct(labels, dirty=0):
    need(type(dirty) is int and 0 <= dirty <= 2, 'dirty range')
    need(isinstance(labels, tuple) and len(labels) <= 64, 'label count')
    need(all(type(t) is tuple and len(t) == 3
             and all(type(v) is int and v in (0, 1) for v in t)
             and t in LABELS for t in labels), 'active labels')
    pure = [i for i, t in enumerate(labels) if t == (0, 0, 1)]
    other = [i for i, t in enumerate(labels) if t != (0, 0, 1)]
    blocks = []
    if len(pure) == 1:
        if other:
            j = other.pop(0)
            u, v = MIXED[labels[j]]
            block = ((1, 1, 1, 2, 3), (1, 1, 2, 2, 2), u, v)
            blocks.append(embed(block, (pure.pop(), j)))
        else:
            blocks.append(embed(PURE[1], (pure.pop(),)))
    if len(pure) % 2:
        blocks.append(embed(PURE[3], tuple(pure[:3])))
        pure = pure[3:]
    for i in range(0, len(pure), 2):
        blocks.append(embed(PURE[2], tuple(pure[i:i+2])))
    for i in other:
        blocks.append(embed(singleton(labels[i]), (i,)))
    return tuple(tuple(v for block in blocks for v in block[j]) for j in range(4))


def inspect(labels, dirty, witness):
    d = len(labels)
    r = d + dirty
    x, y, u, v = witness
    n = len(x)
    need(all(len(f) == n for f in witness), 'family lengths')
    need(all(type(a) is int and 0 <= a < (1 << r) for f in witness for a in f), 'binary vectors')
    need(all(x) and all(y), 'nonzero paid coupling')
    need(rank(x) == d and rank(y) == d, 'active spans')
    need(all(a < (1 << d) for a in x + y), 'active coordinate support')
    zero = (0,) * r
    targets = tuple(tuple(((labels[i][j] << i) if i < d else 0)
                          for i in range(r)) for j in range(3))
    actual = (product_rows(x, y, r), product_rows(u, y, r),
              product_rows(x, v, r), product_rows(u, v, r))
    need(actual == (zero,) + targets, 'four coefficient equations')
    k = labels.count((0, 0, 1))
    need(n == 2*d + k + int(d == k == 1), 'optimum column count')
    return n


def scalar_minima():
    observed = {}
    for n in range(1, 5):
        if n % 2:
            continue  # nonzero scalar X,Y force XY=n modulo two.
        for u in itertools.product(range(2), repeat=n):
            for v in itertools.product(range(2), repeat=n):
                label = (sum(u) % 2, sum(v) % 2,
                         sum(a*b for a, b in zip(u, v)) % 2)
                if label in LABELS:
                    observed.setdefault(label, n)
    need(observed == {t: 4 if t == (0, 0, 1) else 2 for t in LABELS}, 'scalar exhaustive optimum')
    return observed


def dense_template_controls():
    """Independent entrywise arithmetic for every block used in the proof."""
    families = [(label,) for label in MIXED]
    families += [((0, 0, 1), label) for label in MIXED]
    families += [((0, 0, 1),)*q for q in (1, 2, 3)]
    entries = 0
    for labels in families:
        x, y, u, v = construct(labels)
        d = len(labels)
        for equation, (left, right) in enumerate(((x, y), (u, y), (x, v), (u, v))):
            for i in range(d):
                for j in range(d):
                    observed = sum(((left[k] >> i) & 1) * ((right[k] >> j) & 1)
                                   for k in range(len(x))) % 2
                    target = int(i == j) * (labels[i][equation-1] if equation else 0)
                    need(observed == target, 'independent dense template')
                    entries += 1
    return len(families), entries


def rejection_controls():
    labels = ((0, 0, 1), (1, 0, 0))
    witness = construct(labels)
    bad = list(witness)
    bad[2] = (bad[2][0] ^ 1,) + bad[2][1:]
    jobs = [lambda: construct(((True, 0, 1),)), lambda: construct(((0, 0, 0),)),
            lambda: construct(((1, 0, 0),), -1), lambda: construct(((1, 0, 0),), True),
            lambda: construct(((1, 0, 0),)*65), lambda: inspect(labels, 0, tuple(bad)),
            lambda: inspect(labels, 0, tuple(f[:-1] for f in witness)),
            lambda: inspect(tuple(reversed(labels)), 0, witness)]
    for job in jobs:
        try:
            job()
        except ValueError:
            continue
        raise ValueError('negative control accepted')
    return len(jobs)


def scientific_result():
    digest = hashlib.sha256()
    cases = 0
    columns = 0
    for d in range(5):
        for labels in itertools.product(LABELS, repeat=d):
            for dirty in (0, 2):
                witness = construct(labels, dirty)
                columns += inspect(labels, dirty, witness)
                digest.update(repr((labels, dirty, witness)).encode())
                cases += 1
    larger = 0
    for d in range(5, 33):
        for k in range(d + 1):
            labels = ((0, 0, 1),)*k + tuple(tuple(MIXED)[j % 6] for j in range(d-k))
            for dirty in (0, 2):
                witness = construct(labels, dirty)
                inspect(labels, dirty, witness)
                digest.update(repr((labels, dirty, witness)).encode())
                larger += 1
    for k in (0, 1, 2, 3, 63, 64):
        labels = ((0, 0, 1),)*k + ((1, 1, 1),)*(64-k)
        witness = construct(labels, 2)
        inspect(labels, 2, witness)
        digest.update(repr((labels, witness)).encode())
        larger += 1
    scalar_minima()
    templates, entries = dense_template_controls()
    return {'exhaustive_mixed_fixtures': cases, 'columns_in_exhaustive_fixtures': columns,
            'larger_fixtures': larger, 'scalar_labels': 7,
            'dense_templates': templates, 'dense_entries': entries,
            'rejection_controls': rejection_controls(), 'transcript_sha256': digest.hexdigest()}


def authenticated_result():
    package = Path(__file__).resolve().parent
    root = package.parent.parent
    sources = json.loads((package / 'SOURCES.json').read_text())
    for item in sources['files']:
        if item['usage'] == 'input':
            need(hashlib.sha256((root / item['path']).read_bytes()).hexdigest() == item['sha256'], 'source hash')
    result = scientific_result()
    result['source_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sorted(package.iterdir()) if p.is_file() and p.name != 'RESULT.json'}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit', type=Path)
    args = parser.parse_args()
    result = authenticated_result()
    if args.emit:
        with args.emit.open('x') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    else:
        expected = json.loads((Path(__file__).parent / 'RESULT.json').read_text())
        need(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True), 'generated receipt mismatch')
    print('PASS_UT4_MIXED_RELAXATION_OPTIMUM', json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
