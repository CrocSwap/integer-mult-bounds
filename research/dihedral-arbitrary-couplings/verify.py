"""Finite corroboration of README's arbitrary-rank dihedral theorem."""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

def require(ok, message):
    if not ok:
        raise ValueError(message)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)

def source_check():
    for item in json.loads((HERE / "SOURCES.json").read_bytes())["files"]:
        if item["usage"] == "input":
            data = (ROOT / item["path"]).read_bytes()
            require(hashlib.sha256(data).hexdigest() == item["sha256"], "source SHA mismatch")
            blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            require(blob == item["git_blob"], "source blob mismatch")

def rank(rows):
    pivots = {}
    for x in rows:
        while x:
            p = x.bit_length() - 1
            if p not in pivots:
                pivots[p] = x
                break
            x ^= pivots[p]
    return len(pivots)

def eye(n):
    return tuple(1 << i for i in range(n))

def add(a, b):
    return tuple(x ^ y for x, y in zip(a, b))

def xor(xs):
    out = 0
    for x in xs:
        out ^= x
    return out

def mul(a, b):
    return tuple(xor(b[j] for j in range(len(b)) if row >> j & 1) for row in a)

def outer(u, v, n):
    return tuple(v if u >> i & 1 else 0 for i in range(n))

def factor(rows):
    """Column-basis factorization, independently recomposed below."""
    n = len(rows)
    columns = [sum(((rows[i] >> j) & 1) << i for i in range(n)) for j in range(n)]
    basis = []
    for col in columns:
        if rank(basis + [col]) > len(basis):
            basis.append(col)
    lookup = {xor(basis[i] for i in range(len(basis)) if mask >> i & 1): mask
              for mask in range(1 << len(basis))}
    coordinates = [lookup[col] for col in columns]
    return [(u, sum(((c >> i) & 1) << j for j, c in enumerate(coordinates)))
            for i, u in enumerate(basis)]

def pair_mul(a, b):
    """Full F2[C2] convolution with binary-matrix coefficients."""
    return (add(mul(a[0], b[0]), mul(a[1], b[1])),
            add(mul(a[0], b[1]), mul(a[1], b[0])))

def poly_mul(a, b):
    result = 0
    while b:
        if b & 1:
            result ^= a
        a <<= 1
        b >>= 1
    return result

def determinant(matrix):
    """Subset expansion in F2[t], independent of the binary rank calculation."""
    n = len(matrix)
    values = [0] * (1 << n)
    values[0] = 1
    for mask in range(1, 1 << n):
        row = mask.bit_count() - 1
        values[mask] = xor(poly_mul(values[mask ^ (1 << j)], matrix[row][j])
                           for j in range(n) if mask >> j & 1)
    return values[-1]

def represented(rows):
    """Return t*(I+N tensor (I+V)); integer bit j is coefficient of t^j."""
    n = len(rows)
    result = [[2 if i == j else 0 for j in range(2*n)] for i in range(2*n)]
    for i, row in enumerate(rows):
        for j in range(n):
            if row >> j & 1:
                result[2*i][2*j] ^= 2
                result[2*i][2*j+1] ^= 4
                result[2*i+1][2*j] ^= 1
                result[2*i+1][2*j+1] ^= 2
    return result

def minor_degree(matrix):
    size = len(matrix)
    best, tested = 0, 0
    for k in range(1, size+1):
        for rr in itertools.combinations(range(size), k):
            for cc in itertools.combinations(range(size), k):
                value = determinant([[matrix[i][j] for j in cc] for i in rr])
                tested += 1
                if value:
                    best = max(best, value.bit_length()-1-k)
    return best, tested

def basis_program(u, v, n):
    """Row additions taking column basis S to I, hence applying S^-1."""
    theta = (u & v).bit_count() % 2
    columns = [u]
    if not theta:
        columns.append(next(w for w in range(1, 1 << n) if (v & w).bit_count() % 2))
    for w in range(1, 1 << n):
        if not (v & w).bit_count() % 2 and rank(columns + [w]) > len(columns):
            columns.append(w)
    require(len(columns) == n, "basis completion")
    matrix = [sum(((columns[j] >> i) & 1) << j for j in range(n)) for i in range(n)]
    ops = []
    def row_add(i, j):
        matrix[i] ^= matrix[j]
        ops.append(("xor", i, j))
    for j in range(n):
        pivot = next(i for i in range(j, n) if matrix[i] >> j & 1)
        if pivot != j:
            row_add(j, pivot)
            row_add(pivot, j)
            row_add(j, pivot)
        for i in range(n):
            if i != j and matrix[i] >> j & 1:
                row_add(i, j)
    require(tuple(matrix) == eye(n), "basis elimination")
    require(len(ops) <= n*(n-1)+3*(n-1), "basis invoice")
    return ops, theta

def compile_rank_one(u, v, n):
    before, theta = basis_program(u, v, n)
    middle = [("g", 0, 0)] if theta else [
        ("xor", 0, 1), ("g", 1, 0), ("xor", 0, 1), ("g", 1, 0)]
    return before + middle + list(reversed(before)), theta

def identity_data(n, width=2):
    return [[1 << (i*width+j) for j in range(width)] for i in range(n)]

def run(ops, n, width=2):
    data = identity_data(n, width)
    for kind, i, j in ops:
        if kind == "xor":
            data[i] = [a ^ b for a, b in zip(data[i], data[j])]
        else:
            require(kind == "g", "unknown primitive")
            data[i] = [data[i][a ^ 1] for a in range(width)]
    return data

def expected(rows, width=2):
    n = len(rows)
    data = identity_data(n, width)
    return [[data[i][a] ^ xor(data[j][a] ^ data[j][a ^ 1]
                             for j in range(n) if rows[i] >> j & 1)
             for a in range(width)] for i in range(n)]

def normal_word(word):
    k, e = 0, 0
    for label in word:
        k += (1 if e else -1) if label == "s" else 0
        e ^= 1
    return k, e

def reduce_word(word):
    out = []
    for x in word:
        if out and out[-1] == x:
            out.pop()
        else:
            out.append(x)
    return out

def evidence():
    counts = dict(binary_matrices=0, minor_determinants=0, rank_factorizations=0,
                  rank_one_programs=0, nilpotent_programs=0, coefficient_columns=0,
                  target_words=0, controls=0)
    for n in range(1, 4):
        for rows in itertools.product(range(1 << n), repeat=n):
            r = rank(rows)
            d, tested = minor_degree(represented(rows))
            require(d == r, "Laurent minor degree differs from coupling rank")
            counts["minor_determinants"] += tested
            factors = factor(rows)
            require(len(factors) == r, "factor rank invoice")
            combined = (eye(n), (0,)*n)
            reconstructed = (0,)*n
            ops = []
            for u, v in factors:
                one = outer(u, v, n)
                reconstructed = add(reconstructed, one)
                combined = pair_mul((add(eye(n), one), one), combined)
                word, _ = compile_rank_one(u, v, n)
                ops.extend(word)
            require(reconstructed == rows, "rank factorization changed coupling")
            require(combined == (add(eye(n), rows), rows), "rank factors changed formal gate")
            gate = (add(eye(n), rows), rows)
            require(pair_mul(gate, gate) == (eye(n), (0,)*n), "coupling not involutory")
            require(run(ops, n) == expected(rows), "compiled arbitrary coupling endpoint")
            counts["binary_matrices"] += 1
            counts["rank_factorizations"] += 1
    for n in range(1, 5):
        for u, v in itertools.product(range(1, 1 << n), repeat=2):
            word, theta = compile_rank_one(u, v, n)
            require(run(word, n, 4) == expected(outer(u, v, n), 4), "rank-one dirty endpoint")
            require(sum(x[0] == "g" for x in word) == (1 if theta else 2), "address invoice")
            counts["rank_one_programs"] += 1
            counts["nilpotent_programs"] += 1-theta
            counts["coefficient_columns"] += 4*n
    for k in range(-8, 9):
        for e in (0, 1):
            word = reduce_word(list(("rs" if k >= 0 else "sr") * abs(k) + "r"*e))
            require(normal_word(word) == (k, e), "attaining formal endpoint")
            require(word.count("r") == abs(k+e) and word.count("s") == abs(k), "target tariff")
            counts["target_words"] += 1
    nil = (2, 0)
    require(mul(nil, nil) == (0, 0) and mul(nil, nil) != nil, "nilpotent control")
    counts["controls"] += 1
    require(minor_degree(represented(eye(3)))[0] == 3, "rank underpricing control")
    counts["controls"] += 1
    shear = [("xor", 0, 1), ("g", 1, 0), ("xor", 0, 1), ("g", 1, 0)]
    require(run(shear[:-1], 2) != expected(nil), "missing dirty restoration accepted")
    require(run(shear[1:], 2) != expected(nil), "missing identity summand accepted")
    counts["controls"] += 2
    exposed = False
    for u, v in itertools.product(range(1, 8), repeat=2):
        before, theta = basis_program(u, v, 3)
        middle = [("g", 0, 0)] if theta else shear
        exposed |= run(list(reversed(before)) + middle + before, 3) != expected(outer(u, v, 3))
    require(exposed, "wrong basis orientation not exposed")
    counts["controls"] += 1
    return {"status": "PASS_DIHEDRAL_ARBITRARY_COUPLINGS", **counts}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="explicitly replace RESULT.json")
    args = parser.parse_args()
    source_check()
    actual = evidence()
    target = HERE / "RESULT.json"
    if args.write:
        target.write_text(json.dumps(actual, indent=2)+"\n", encoding="utf-8", newline="\n")
    else:
        require(canonical(json.loads(target.read_bytes())) == canonical(actual), "receipt mismatch")
    print(canonical(actual))

if __name__ == "__main__":
    main()
