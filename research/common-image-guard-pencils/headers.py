"""Literal complete-header oracle, independent of the prefix counting proof."""
import hashlib
from collections import Counter
from fractions import Fraction
from math import prod

from finite import Field


def eliminate(field, square, inverse=False):
    """Ordinary row elimination on an actual square matrix."""
    n = len(square)
    a = [list(row) + ([int(i == j) for j in range(n)] if inverse else [])
         for i, row in enumerate(square)]
    det = 1
    for j in range(n):
        pivot = next((i for i in range(j, n) if a[i][j]), None)
        if pivot is None:
            return 0, None
        if pivot != j:
            a[j], a[pivot] = a[pivot], a[j]
            det = field.neg[det]
        v = a[j][j]
        det = field.mul[det][v]
        a[j] = [field.mul[field.inv[v]][x] for x in a[j]]
        for i in range(n):
            if i != j and a[i][j]:
                a[i] = list(field.axpy(a[i], field.neg[a[i][j]], a[j]))
    return det, tuple(tuple(row[n:]) for row in a) if inverse else None


def matrix_product(field, left, right):
    columns = list(zip(*right))
    return tuple(tuple(field.dot(row, col) for col in columns) for row in left)


def census(q, m, forms):
    field = Field(q)
    conjugands = []
    for form in forms:
        row = (*form, *(0 for _ in range(m - len(form))))
        conjugands.append(tuple(tuple(field.add[int(i == j)][field.neg[row[j]] if i == 0 else 0]
                                     for j in range(m)) for i in range(m)))
    digest = hashlib.sha256()
    masks = Counter()
    strata = [Counter() for _ in range(q)]
    for word in field.vectors(m*m):
        header = tuple(tuple(word[i:i + m]) for i in range(0, m*m, m))
        det, inv = eliminate(field, header, inverse=True)
        if not det:
            continue
        mask = 0
        for i, fixed in enumerate(conjugands):
            actual = matrix_product(field, matrix_product(field, header, fixed), inv)
            if all(eliminate(field, [row[:n] for row in actual[:n]])[0]
                   for n in range(1, m)):
                mask |= 1 << i
        masks[mask] += 1
        strata[det][mask] += 1
        digest.update(bytes((*word, det)))
        digest.update(mask.to_bytes((len(forms) + 7)//8, "little"))
    size = prod(q**m - q**j for j in range(m))
    if sum(masks.values()) != size:
        raise ValueError("complete GL cardinality")
    for det in range(1, q):
        if any((q - 1)*strata[det][mask] != count for mask, count in masks.items()):
            raise ValueError("determinant-conditioned histogram")
    return dict(q=q, m=m, forms=forms, headers=size, determinant_classes=q - 1,
                masks={str(mask): masks[mask] for mask in range(1 << len(forms)) if masks[mask]},
                word_det_mask_sha256=digest.hexdigest())


def check_expected(row, probabilities):
    masks = {int(i): n for i, n in row["masks"].items()}
    k = len(row["forms"])
    for mask in range(1 << k):
        observed = Fraction(sum(n for key, n in masks.items() if key & mask == mask),
                            row["headers"])
        if observed != probabilities(mask):
            raise ValueError(f"literal named guard subset q={row['q']}, m={row['m']}, mask={mask}")
