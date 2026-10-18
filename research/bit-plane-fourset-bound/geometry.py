"""Exact geometry, independently reconstructed from the selected word.

Prepared for commdata2338, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
import gzip
import itertools
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def positive_root(x):
    return x if next(a for a in x if a) > 0 else tuple(-a for a in x)


def rank2(rows):
    pivots = {}
    for value in rows:
        while value:
            p = value.bit_length() - 1
            if p in pivots:
                value ^= pivots[p]
            else:
                pivots[p] = value
                break
    return len(pivots)


def inverse2(rows):
    n = len(rows)
    work = [r | (1 << (n + i)) for i, r in enumerate(rows)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if work[i] >> col & 1), None)
        need(pivot is not None, 'singular binary form')
        work[col], work[pivot] = work[pivot], work[col]
        for i in range(n):
            if i != col and work[i] >> col & 1:
                work[i] ^= work[col]
    return [r >> n for r in work]


def matvec2(matrix, vector):
    return sum(((r & vector).bit_count() % 2) << i for i, r in enumerate(matrix))


def outer2(x, y):
    return sum((y if x >> i & 1 else 0) << (9 * i) for i in range(9))


def rank_q(rows):
    matrix = [[Fraction(x) for x in row] for row in rows]
    if not matrix:
        return 0
    r = 0
    for col in range(len(matrix[0])):
        pivot = next((i for i in range(r, len(matrix)) if matrix[i][col]), None)
        if pivot is None:
            continue
        matrix[r], matrix[pivot] = matrix[pivot], matrix[r]
        lead = matrix[r][col]
        matrix[r] = [x / lead for x in matrix[r]]
        for i in range(r + 1, len(matrix)):
            factor = matrix[i][col]
            matrix[i] = [x - factor * y for x, y in zip(matrix[i], matrix[r])]
        r += 1
        if r == len(matrix):
            break
    return r


def reconstruct():
    live = [tuple(x) for x in json.loads(gzip.decompress((ROOT / WORD).read_bytes()))['lines']]
    need(len(live) == 111 and len(set(live)) == 111, 'selected label inventory')
    need(all(dot(x, x) == 4 for x in live), 'root norms')
    roots = set(live) | {tuple(-a for a in x) for x in live}
    while True:
        before = len(roots)
        for x in tuple(roots):
            for y in tuple(roots):
                d = dot(x, y)
                need(d in (-4, -2, 0, 2, 4), 'unexpected root pairing')
                roots.add(tuple(a - (d // 2) * b for a, b in zip(x, y)))
        if len(roots) == before:
            break
        need(len(roots) <= 240, 'root closure overflow')
    need(len(roots) == 240, 'E8 closure cardinality')
    puncture = sorted({positive_root(x) for x in roots} - {positive_root(x) for x in live})
    need(len(puncture) == 9, 'puncture cardinality')
    lines = live + puncture
    gram = [[dot(x, y) // 2 for y in lines] for x in lines]
    pairing = [[(1 + entry) % 2 for entry in row] for row in gram]
    labels = [sum(pairing[t][111 + j] << j for j in range(9)) for t in range(120)]
    form = inverse2(labels[111:])
    need(rank2(labels) == 9, 'label rank')
    for i in range(120):
        for j in range(120):
            need((labels[i] & matvec2(form, labels[j])).bit_count() % 2 == pairing[i][j],
                 'binary form does not represent pairing')
    return lines, gram, pairing, labels, form


def foursets(gram):
    """Direct enumeration, independent of the predecessor's maximal-set search."""
    result = {}
    for r in range(111, 120):
        perpendicular = [a for a in range(111) if gram[a][r] == 0]
        for subset in itertools.combinations(perpendicular, 4):
            if all(gram[a][b] != 0 for a, b in itertools.combinations(subset, 2)):
                result.setdefault(subset, []).append(r)
    return result


def basis_mod3(indices, lines, dimension):
    pivots, chosen = {}, []
    for i in indices:
        row = [x % 3 for x in lines[i]]
        for col in range(8):
            if not row[col]:
                continue
            if col in pivots:
                factor = row[col]
                row = [(a - factor * b) % 3 for a, b in zip(row, pivots[col])]
            else:
                scale = pow(row[col], -1, 3)
                pivots[col] = [x * scale % 3 for x in row]
                chosen.append(i)
                break
        if len(chosen) == dimension:
            break
    return chosen


def robust_reader_bases(lines, gram, labels, form):
    """Five disjoint bases certify the span after ANY four line deletions.

    Modular rank gives a rational lower bound, also checked with Fractions.
    Root normals supply the matching upper bound for the exceptional readers.
    """
    root_functionals = {matvec2(form, labels[x]): x for x in range(120)}
    need(len(root_functionals) == 120, 'distinct root functionals')
    certificates = []
    for functional in range(1, 512):
        root = root_functionals.get(functional)
        readers = [i for i in range(111)
                   if (labels[i] & functional).bit_count() % 2 and i != root]
        dimension = 7 if root is not None else 8
        if root is not None:
            need(all(gram[i][root] == 0 for i in readers), 'root normal')
        for attempt in range(100):
            remaining = readers[:]
            if attempt:
                random.Random(1000 * functional + attempt).shuffle(remaining)
            bases = []
            for _ in range(5):
                basis = basis_mod3(remaining, lines, dimension)
                if len(basis) != dimension:
                    break
                bases.append(basis)
                remaining = [i for i in remaining if i not in basis]
            if len(bases) == 5:
                break
        need(len(bases) == 5, 'five disjoint reader bases absent')
        flat = [i for basis in bases for i in basis]
        need(len(flat) == len(set(flat)), 'reader bases overlap')
        need(all(rank_q([lines[i] for i in basis]) == dimension for basis in bases),
             'independent rational basis check')
        certificates.append([functional, root, bases])
    return certificates


def robust_target_blocks(gram, labels):
    """One of five disjoint equation blocks survives any four line deletions."""
    order = list(range(111))
    random.Random(0).shuffle(order)
    blocks = [order[i::5] for i in range(5)]
    need(len(set(itertools.chain.from_iterable(blocks))) == 111, 'equation blocks overlap')
    for block in blocks:
        rows = [outer2(labels[a], labels[b]) for a in block for b in block
                if a == b or gram[a][b] % 2]
        need(rank2(rows) == 81, 'masked equations do not force the form')
    return blocks
