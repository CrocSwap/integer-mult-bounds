#!/usr/bin/env python3
"""Exact QQ16 odd-prime obstruction in Z[zeta_8,1/2]. Apache-2.0."""

import argparse
import gzip
import json
from fractions import Fraction as Q
from hashlib import sha256
from io import BytesIO
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PACKET = "research/joint-query/certificate.json.gz"
PAYLOAD_HASH = "2efe83c59978aa9c0db2c3e4eccc14cbfdcd3c9ce499432601b5dd34083472ef"
GOOD = (1, 2, 3, 4, 5, 6, 8, 12)
BAD = (1, 25, 3, 4, 5, 6, 8, 12)
Z = (1, 2, 1, 1, 1, 1, 3, -2)
SELECT_A = (0, 7, 20, 27, 36, 46, 57, 111)
SELECT_T = (21, 37, 47, 76, 81, 87, 92, 110)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dyadic(value):
    d = Q(value).denominator
    return d & (d - 1) == 0


def scalar(value):
    value = Q(value)
    require(dyadic(value), "coefficient outside Z[zeta_8,1/2]")
    return (value, Q(0), Q(0), Q(0))


def add(a, b):
    return tuple(a[j] + b[j] for j in range(4))


def multiply(a, b):
    # Exact cyclotomic product; zeta^4 = -1.
    out = [Q(0)] * 4
    for i in range(4):
        for j in range(4):
            degree = i + j
            out[degree % 4] += (-1 if degree >= 4 else 1) * a[i] * b[j]
    return tuple(out)


def residue(a, p):
    require(p in (3, 5), "finite checker supports only primes 3 and 5")
    return tuple(int(x.numerator * pow(x.denominator, -1, p) % p) for x in a)


def quotient_product(a, b, p):
    # Separate polynomial convolution and monic long division over F_p.
    work = [0] * 7
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            work[i + j] += x * y
    for degree in range(6, 3, -1):
        work[degree - 4] -= work[degree]
        work[degree] = 0
    return tuple(x % p for x in work[:4])


def ring_checks():
    one, zero = scalar(1), scalar(0)
    zeta = (Q(0), Q(1), Q(0), Q(0))
    imag = multiply(zeta, zeta)
    half_root = (Q(0), Q(1, 2), Q(0), Q(-1, 2))
    require(multiply(imag, imag) == scalar(-1), "i squared differs")
    require(multiply(half_root, half_root) == scalar(Q(1, 2)), "H normalization differs")
    require(multiply(zeta, zeta) == (Q(0), Q(0), Q(1), Q(0)), "zeta basis differs")
    examples = [tuple(Q(c, 2) if j == k else Q(0) for j in range(4))
                for k in range(4) for c in (-2, -1, 1, 2)] + [half_root]
    comparisons = 0
    for p in (3, 5):
        require(residue(one, p) != residue(zero, p), "quotient collapses 1 to 0")
        for a in examples:
            require(residue(multiply(scalar(p), a), p) == (0, 0, 0, 0), "p ideal leaks")
            for b in examples:
                ra, rb = residue(a, p), residue(b, p)
                require(residue(add(a, b), p) == tuple((ra[j] + rb[j]) % p
                                                      for j in range(4)), "add map differs")
                require(residue(multiply(a, b), p) == quotient_product(ra, rb, p),
                        "multiplicative reduction differs")
                comparisons += 1
    return half_root, zeta, imag, comparisons


def gate(state, name, qubit, generators):
    require(len(state) in (2, 4, 8) and 0 <= qubit < len(state).bit_length() - 1,
            "gate outside bounded tensor example")
    h, zeta, imag = generators
    require(name in ("H", "S", "Si", "T", "Ti", "bad_H"), "unsupported gate")
    factor = {"S": imag, "Si": multiply(scalar(-1), imag), "T": zeta,
              "Ti": (Q(0), Q(0), Q(0), Q(-1))}.get(name)
    out = list(state)
    for low in range(len(state)):
        if low & (1 << qubit):
            continue
        high = low | (1 << qubit)
        if name in ("H", "bad_H"):
            normalization = scalar(1) if name == "bad_H" else h
            out[low] = multiply(normalization, add(state[low], state[high]))
            out[high] = multiply(normalization, add(state[low], multiply(scalar(-1), state[high])))
        else:
            out[high] = multiply(factor, state[high])
    return out


def tensor_checks(generators):
    h, zeta, imag = generators
    one, zero = scalar(1), scalar(0)
    require(gate([one, zero], "H", 0, generators) == [h, h], "H basis column differs")
    require(gate([zero, one], "H", 0, generators) == [h, multiply(scalar(-1), h)],
            "H sign differs")
    require(gate([one, one], "S", 0, generators) == [one, imag], "S phase differs")
    require(gate([one, one], "Si", 0, generators) == [one, multiply(scalar(-1), imag)],
            "inverse S phase differs")
    require(gate([one, one], "T", 0, generators) == [one, zeta], "T phase differs")
    require(gate([one, one], "Ti", 0, generators) == [one, (Q(0), Q(0), Q(0), Q(-1))],
            "inverse T phase differs")
    columns = 0
    inverse = {"H": "H", "S": "Si", "T": "Ti"}
    for qubits in range(1, 4):
        program = [("H", q) for q in range(qubits)]
        program += [("T", q) for q in range(qubits)] + [("S", 0)]
        for column in range(1 << qubits):
            initial = [scalar(5 * (j == column)) for j in range(1 << qubits)]
            state = initial[:]
            for name, q in program:
                state = gate(state, name, q, generators)
                require(all(residue(x, 5) == (0, 0, 0, 0) for x in state),
                        "normalized gate escaped ideal")
            for name, q in reversed(program):
                state = gate(state, inverse[name], q, generators)
            require(state == initial, "tensor circuit inverse differs")
            columns += 1
    return columns


def bounded_read(path, limit):
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    require(len(data) <= limit, "input exceeds resource bound: " + str(path))
    return data


def load_source(root):
    manifest = json.loads(bounded_read(PACKAGE / "SOURCES.json", 32_000))
    require(len(manifest["files"]) <= 16, "too many source pins")
    for entry in manifest["files"]:
        if entry["usage"] == "input":
            raw = bounded_read(root / entry["path"], 1_000_000)
            require(sha256(raw).hexdigest() == entry["sha256"],
                    "source pin differs: " + entry["path"])
    raw = bounded_read(root / PACKET, 1_000_000)
    with gzip.GzipFile(fileobj=BytesIO(raw)) as stream:
        payload = stream.read(11_000_001)
    require(len(payload) <= 11_000_000, "decompressed packet exceeds bound")
    require(sha256(payload).hexdigest() == PAYLOAD_HASH, "packet payload differs")
    packet = json.loads(payload)
    require(len(packet["R_rows"]) == 8, "query dimension differs")
    matrix = [[Q(row.get(str(p), "0")) for p in range(112)] for row in packet["R_rows"]]
    require(all(x in (-1, 0, 1) for row in matrix for x in row), "matrix alphabet differs")
    require(tuple(packet["A_ports"]) == SELECT_A and tuple(packet["T_ports"]) == SELECT_T,
            "selected ports differ")
    ordinary = tuple(p for p in range(112) if p not in SELECT_A + SELECT_T)
    require(tuple(packet["U_ports"]) == ordinary, "ordinary partition differs")
    for ports, diagonal in ((SELECT_A, 4), (SELECT_T, 4), (ordinary, 48)):
        gram = [[sum(matrix[i][p] * matrix[j][p] for p in ports)
                 for j in range(8)] for i in range(8)]
        require(gram == [[diagonal * (i == j) for j in range(8)] for i in range(8)],
                "selected/ordinary Gram differs")
    return matrix, ordinary


def invert(matrix):
    require(len(matrix) == 8 and all(len(row) == 8 for row in matrix), "inverse needs 8x8")
    work = [list(row) + [Q(i == j) for j in range(8)] for i, row in enumerate(matrix)]
    determinant = Q(1)
    for col in range(8):
        pivot = next((j for j in range(col, 8) if work[j][col]), None)
        require(pivot is not None, "singular minor")
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            determinant = -determinant
        value = work[col][col]
        determinant *= value
        work[col] = [x / value for x in work[col]]
        for row in range(8):
            if row != col:
                factor = work[row][col]
                work[row] = [work[row][k] - factor * work[col][k] for k in range(16)]
    return determinant, [row[8:] for row in work]


def minors(matrix):
    result = {}
    for name, ports, expected in (("original", GOOD, -32), ("alternative", BAD, -80)):
        m = [[row[p] for p in ports] for row in matrix]
        determinant, inv = invert(m)
        require(determinant == expected, "minor determinant differs")
        for left, right in ((m, inv), (inv, m)):
            require([[sum(left[i][k] * right[k][j] for k in range(8)) for j in range(8)]
                     for i in range(8)] == [[Q(i == j) for j in range(8)] for i in range(8)],
                    "minor inverse order differs")
        if name == "original":
            require(all(dyadic(x) for row in inv for x in row), "positive minor not admitted")
        else:
            require(inv[0][1] == Q(1, 10), "odd-denominator inverse entry differs")
        result[name] = {"ports": list(ports), "determinant": str(determinant),
                        "inverse": [[str(x) for x in row] for row in inv]}
    return result


def query(matrix, values):
    return [sum(row[p] * values[p] for p in range(112)) for row in matrix]


def section(matrix, values, port):
    return sum(matrix[k][port] * values[k] for k in range(8)) / 4


def observation_witness(matrix, ordinary):
    x, y = [Q(0)] * 112, [Q(0)] * 112
    for port, value in zip(BAD, Z, strict=True):
        x[port] = Q(value)
    q = query(matrix, x)
    require(q == [0, 10, 0, 0, 0, 0, 0, 0], "integer witness image differs")
    for port in SELECT_A:
        y[port] = section(matrix, q, port)
        x[port] = -y[port]
    f = query(matrix, x)
    require(f == [0] * 8, "F0 driver differs")
    c = query(matrix, [x[p] if p in SELECT_T else Q(0) for p in range(112)])
    x1, y1 = [Q(0)] * 112, [Q(0)] * 112
    for p in ordinary:
        x1[p] = x[p] - section(matrix, f, p)
        y1[p] = y[p] + x1[p]
    for p in SELECT_A + SELECT_T:
        x1[p] = section(matrix, c if p in SELECT_A else f, p)
        y1[p] = x[p] + y[p] - x1[p]
    future = query(matrix, y1)
    y2_a = [section(matrix, future, p) for p in SELECT_A]
    observed = ([x1[p] for p in ordinary if p not in BAD]
                + [x1[p] for p in SELECT_A + SELECT_T]
                + [y1[p] for p in SELECT_A + SELECT_T]
                + y2_a + [x1[p] - y1[p] for p in ordinary])
    require(y2_a == [Q(5, 2), Q(-5, 2), 0, Q(5, 2), 0, 0, Q(-5, 2), 0],
            "B1 logger differs")
    require(len(observed) == 224 and x[1] == 1, "observation/output dimensions differ")
    require(sum(bool(v) for v in observed) == 4, "unintended nonzero observation")
    require(all(residue(scalar(v), 5) == (0, 0, 0, 0) for v in observed),
            "observation escaped ideal")
    require(residue(scalar(x[1]), 5) == (1, 0, 0, 0), "required output is invisible")
    return {"observations": 224, "nonzero_observations": 4,
            "y2_A": [str(v) for v in y2_a], "required_original_X_1": "1",
            "observation_residues_zero": True, "required_residue": [1, 0, 0, 0]}


def controls(matrix, generators):
    try:
        scalar(Q(1, 5))
    except ValueError:
        pass
    else:
        raise ValueError("odd-denominator gate accepted")
    require(Q(2, 5) * Q(5, 2) == 1, "rational escape control differs")
    changed = list(Z)
    changed[0] += 1
    image = [sum(row[p] * v for p, v in zip(BAD, changed, strict=True)) for row in matrix]
    require(any(v % 5 for v in image), "perturbed witness remains modular kernel")
    initial = [scalar(1), scalar(0)]
    malformed = gate(gate(initial, "bad_H", 0, generators), "bad_H", 0, generators)
    require(malformed == [scalar(2), scalar(0)] and malformed != initial,
            "missing normalization control failed")
    require(residue(scalar(1), 5) != (0, 0, 0, 0), "collapsed quotient accepted")
    # Unlike a field, B_5 has nonzero zero divisors. Never invert arbitrary residues.
    a, b = (2, 0, 1, 0), (3, 0, 1, 0)
    require(quotient_product(a, b, 5) == (0, 0, 0, 0), "quotient field-assumption control failed")
    return ["odd-denominator gate rejected", "rational division escapes ideal",
            "perturbed QQ16 witness rejected", "missing H normalization rejected",
            "collapsed quotient rejected", "B_5 is not assumed a field"]


def report(root):
    matrix, ordinary = load_source(root)
    h, zeta, imag, comparisons = ring_checks()
    generators = (h, zeta, imag)
    return {"status": "PASS_QQ16_CLIFFORD_DENOMINATOR", "schema_version": 1,
            "coefficient_ring": "Z[zeta_8,1/2]", "quotient_primes_checked": [3, 5],
            "product_reduction_comparisons": comparisons,
            "tensor_basis_columns": tensor_checks(generators),
            "minors": minors(matrix), "two_cut_witness": observation_witness(matrix, ordinary),
            "controls": controls(matrix, generators), "packet_payload_sha256": PAYLOAD_HASH,
            "scope": ("Exact affine complete-input decoding at the fixed PR2443 cuts; "
                      "no supplier or kappa.")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--receipt", type=Path, default=PACKAGE / "RESULT.json")
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = report(args.repo)
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.emit:
        print(encoded, end="")
        return
    expected = json.loads(bounded_read(args.receipt, 32_000))
    require(json.dumps(expected, sort_keys=True, indent=2) + "\n" == encoded,
            "receipt differs from full recomputation")
    print(result["status"] + " observations=224 tensor_columns=14 primes=3,5 controls=6")


if __name__ == "__main__":
    main()
