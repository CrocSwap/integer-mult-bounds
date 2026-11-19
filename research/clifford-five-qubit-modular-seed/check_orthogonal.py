"""Check the seed inside two orthogonal subgroups independently of Brauer data."""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from math import prod
from pathlib import Path
import tarfile


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pair_shear(point, i, j):
    """Add x_j e_i + x_i e_j to the z half."""
    return point ^ (((point >> j) & 1) << (5 + i)) ^ (((point >> i) & 1) << (5 + j))


def change_basis(point, i, k):
    """z_i += z_k, with the contragredient change x_k += x_i."""
    return point ^ (((point >> (5 + k)) & 1) << (5 + i)) ^ (((point >> i) & 1) << k)


def quadratic(point, sign):
    x, z = point & 31, point >> 5
    return ((x & z).bit_count() + (0 if sign == 1 else (x >> 4) + (z >> 4))) % 2


def gl_order(rank):
    return prod(2**rank - 2**i for i in range(rank))


def sp_order(half_rank):
    return 2**(half_rank**2) * prod(4**i - 1 for i in range(1, half_rank + 1))


def class_size(rank, sign=None):
    if sign is None:
        frames = prod(2**(10-j) - 2**j for j in range(rank))
    else:
        frames = prod(2**j * (2**(9-2*j) + sign*2**(4-j) - 1) for j in range(rank))
    # Each singular image carries |GL(r)|/|Sp(r)| nonsingular alternating shears.
    return Fraction(frames, gl_order(rank)) * Fraction(gl_order(rank), sp_order(rank // 2))


def check_geometry():
    points = range(1024)
    pairs = list(combinations(range(4), 2))
    require([sum(quadratic(v, e) == 0 for v in points) for e in (1, -1)] == [528, 496],
            "Wrong quadratic refinements")
    for i, j in pairs:
        k = next(h for h in range(4) if h not in (i, j))
        for v in points:
            # Both factors of [T, s_kj] are involutions in both orthogonal groups.
            t = change_basis(v, i, k)
            s = pair_shear(v, k, j)
            for e in (1, -1):
                require(quadratic(t, e) == quadratic(s, e) == quadratic(v, e),
                        "Commutator factor fails to preserve a quadratic form")
            w = change_basis(pair_shear(change_basis(s, i, k), k, j), i, k)
            require(w == pair_shear(v, i, j), "Incorrect commutator")
    ranks = Counter()
    elements = set()
    for mask in range(64):
        chosen = [p for b, p in enumerate(pairs) if mask & (1 << b)]
        images = []
        for v in points:
            w = v
            for i, j in chosen:
                w = pair_shear(w, i, j)
            images.append(w ^ v)
        rank = len(set(images)).bit_length() - 1
        require(len(set(images)) == 2**rank, "Nonlinear image size")
        elements.add(tuple(images[1 << i] for i in range(10)))
        ranks[rank] += 1
    require(len(elements) == 64 and ranks == {0: 1, 2: 35, 4: 28}, "Seed census")
    sizes = {sign: tuple(class_size(r, sign) for r in (2, 4)) for sign in (None, 1, -1)}
    require(sizes == {None: (86955, 21912660), 1: (23715, 1992060), -1: (19635, 706860)},
            "Singular frame and alternating form counts")
    return sizes


def first_list(text):
    start = text.index("[")
    depth = 0
    for i in range(start, len(text)):
        depth += (text[i] == "[") - (text[i] == "]")
        if depth == 0:
            return text[start:i + 1], text[i + 1:]
    raise ValueError("Unterminated CTblLib list")


def fusion(source, small, large):
    tail = source.split(f'ALF("{small}","{large}",', 1)[1]
    return json.loads(first_list(tail)[0])


def check_archive(path, sizes):
    totals = {"S10(2)": (None, (3, 6)), "O10+(2)": (1, (2, 4)), "O10-(2)": (-1, (2, 4))}
    require(sha256(path.read_bytes()).hexdigest() ==
            "f201e9da571c681a7bbfb1e4683bdb2c80a23b005099ed0453521f59cb443434",
            "Wrong CTblLib release")
    with tarfile.open(path, "r:gz") as t:
        symp, orth = [t.extractfile("ctbllib-1.3.11/data/" + name).read().decode("latin1")
                      for name in ("ctosymp1.tbl", "ctoorth3.tbl")]
    for name, (sign, indices) in totals.items():
        source = symp if sign is None else orth
        _, tail = first_list(source.split(f'MOT("{name}",', 1)[1])
        cs = json.loads(first_list(tail)[0])
        for size, index in zip(sizes[sign], indices, strict=True):
            hits = [i for i, c in enumerate(cs, 1) if c * size == cs[0]]
            # Symplectic columns 5 and 6 have equal size. Both subgroup fusions
            # below select column 6 from the unique orthogonal column.
            expected = [5, 6] if sign is None and index == 6 else [index]
            require(hits == expected, "Unexpected centralizer sizes")
        if sign is not None:
            to_full = fusion(orth, name, name + ".2")
            to_symp = fusion(orth, name + ".2", "S10(2)")
            mapped = [to_symp[i-1] for i in to_full]
            for col, target in zip(indices, (3, 6), strict=True):
                require([i for i, c in enumerate(mapped, 1) if c == target] == [col],
                        "Geometric column disagrees with the class fusion")
    print("PASS original CTblLib class sizes and both two-stage fusions")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", nargs="?", type=Path)
    args = parser.parse_args()
    computed = check_geometry()
    if args.archive:
        check_archive(args.archive, computed)
    print("PASS six explicit orthogonal commutators, 64 shears, two quadratic signs, six class sizes")
