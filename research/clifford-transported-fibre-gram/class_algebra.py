"""Recognize native Sp(8,2) classes and multiply width-13 central kernels."""
from collections import Counter
from functools import cache
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
GROUP_ORDER = 47377612800
IDENTITY = tuple(1 << i for i in range(8))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def apply_columns(columns, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= columns[bit.bit_length()-1]
        vector ^= bit
    return result


def pairing(a, b):
    return (((a >> 4) & b) ^ ((b >> 4) & a)).bit_count() & 1


def signature(columns):
    """For each cyclic vector, record its minimal polynomial and pairings with its iterates."""
    require(len(columns) == 8 and all(type(x) is int and 0 <= x < 256 for x in columns),
            "Expected eight four-qubit Pauli-label columns")
    require(all(pairing(columns[i], columns[j]) == pairing(1 << i, 1 << j)
                for i in range(8) for j in range(i)), "Nonsymplectic input")
    action = [apply_columns(columns, v) for v in range(256)]
    types = Counter()
    for vector in range(256):
        current = vector
        pivots = {}
        pair_bits = 0
        for degree in range(9):
            pair_bits |= pairing(vector, current) << degree
            reduced, relation = current, 1 << degree
            while reduced and reduced.bit_length() in pivots:
                value, polynomial = pivots[reduced.bit_length()]
                reduced ^= value
                relation ^= polynomial
            if reduced == 0:
                break
            pivots[reduced.bit_length()] = (reduced, relation)
            current = action[current]
        require(reduced == 0, "No relation on nine eight-bit vectors")
        types[(relation, pair_bits)] += 1
    return tuple(sorted(types.items()))


@cache
def data():
    return json.loads((HERE / "CLASS-ALGEBRA.json").read_text())


@cache
def lookup():
    codebook = {signature(tuple(rep)): j for j, cl in enumerate(data()["classes"])
                for rep in cl["representatives"]}
    require(len(codebook) == 81, "Incomplete ordinary class recognition")
    return codebook


def class_index(columns):
    """Zero-based rational class index. The identity class has index zero."""
    return lookup()[signature(tuple(columns))]


def divisible(n, d):
    q, r = divmod(n, d)
    require(r == 0, "Nonintegral class-algebra coefficient")
    return q


@cache
def gram_class_matrix():
    """Integer M for convolution by F(s)=(-64)^dimFix(s) on rational class coefficients.

    Column l is the convolution of F with the indicator of rational class l.
    The normalized width-13 operator uses M/16^12.
    """
    classes = data()["classes"]
    rows = data()["characters"]
    sizes = [c["size"] for c in classes]
    shell = [(-64)**c["fixed"] for c in classes]
    require(len(rows) == len(classes) == 80 and sum(sizes) == GROUP_ORDER, "Class census")
    # Evaluating a class sum on an irreducible gives size*packet_value/packet_degree.
    # The inverse character transform has coefficients degree*packet_value/|G|,
    # where degree is the degree of one constituent. All packet sums are real.
    scaled = []
    for row in rows:
        orbit = divisible(sum(n*v*v for n, v in zip(sizes,row,strict=True)), GROUP_ORDER)
        degree = divisible(row[0], orbit)
        evaluations = [divisible(n*v, row[0]) for n,v in zip(sizes,row,strict=True)]
        eigenvalue = sum(a*b for a,b in zip(evaluations, shell, strict=True))
        scaled.append((row, [degree*eigenvalue*v for v in evaluations]))
    matrix = tuple(tuple(divisible(sum(row[i]*weighted[j] for row,weighted in scaled),
                                   GROUP_ORDER) for j in range(80)) for i in range(80))
    require([r[0] for r in matrix] == shell, "Convolution of F with identity")
    return matrix


def source_semantics(classes, characters):
    # Representatives may differ across GAP builds. Compare the invariants of
    # all representatives, in addition to the sizes and the complete packet table.
    return ([([signature(rep) for rep in c["representatives"]],c["size"],c["fixed"])
             for c in classes], characters)
