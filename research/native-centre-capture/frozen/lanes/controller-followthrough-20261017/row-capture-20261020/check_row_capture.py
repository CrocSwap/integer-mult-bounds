#!/usr/bin/env python3
"""Check the exact row capture and its local output interface."""

from fractions import Fraction as F
from pathlib import Path
import argparse
import gzip
import hashlib
import json


HERE = Path(__file__).resolve().parent
LANES = HERE.parent.parent
N = 112
P = [0, 27, 36, 111, 20, 7, 57, 46, 1, 3, 6, 8, 17, 18, 24, 23]
PINS = {
    "native": (
        "new-core-transfer-20261017/low-displacement-20261020/"
        "odd16-normal-v2/EXTENSION-PROGRAM.json.gz",
        "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4",
    ),
    "pairs": (
        "independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json",
        "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585",
    ),
}


def need(value, message):
    if not value:
        raise ValueError(message)


def load(name):
    path, pin = PINS[name]
    raw = (LANES / path).read_bytes()
    if path.endswith(".gz"):
        raw = gzip.decompress(raw)
    need(hashlib.sha256(raw).hexdigest() == pin, "source pin: " + name)
    return json.loads(raw)


def matrix(rows):
    return [{int(j): F(a) for j, a in row.items() if F(a)} for row in rows]


def identity(n):
    return [{i: F(1)} for i in range(n)]


def addrow(a, b, scale=F(1)):
    out = dict(a)
    for j, v in b.items():
        out[j] = out.get(j, F(0)) + scale * v
        if not out[j]:
            del out[j]
    return out


def mul(a, b):
    out = []
    for row in a:
        acc = {}
        for k, v in row.items():
            acc = addrow(acc, b[k], v)
        out.append(acc)
    return out


def inv(a):
    n = len(a)
    left = [[a[i].get(j, F(0)) for j in range(n)] for i in range(n)]
    right = [[F(i == j) for j in range(n)] for i in range(n)]
    determinant = F(1)
    for j in range(n):
        pivot = next((i for i in range(j, n) if left[i][j]), None)
        need(pivot is not None, "singular minor")
        if pivot != j:
            left[j], left[pivot] = left[pivot], left[j]
            right[j], right[pivot] = right[pivot], right[j]
            determinant *= -1
        value = left[j][j]
        determinant *= value
        left[j] = [x / value for x in left[j]]
        right[j] = [x / value for x in right[j]]
        for i in range(n):
            if i != j and left[i][j]:
                value = left[i][j]
                left[i] = [x - value * y for x, y in zip(left[i], left[j])]
                right[i] = [x - value * y for x, y in zip(right[i], right[j])]
    return [
        {j: v for j, v in enumerate(row) if v} for row in right
    ], determinant


def dumpmatrix(a):
    return [{str(j): str(v) for j, v in sorted(row.items())} for row in a]


def lower_shear(c, sign=1):
    word = []
    for p in P:
        row = dict(c[p])
        need(row.pop(p) == 1, "unit pivot coefficient")
        need(not (set(row) & set(P)), "pivot source in capture shear")
        half = any(v.denominator == 2 for v in row.values())
        scale = 2 if half else 1
        if half:
            word.append(["scale", p, None, "2"])
        for j, v in sorted(row.items()):
            value = sign * scale * v
            need(value in (-1, 1), "non-unit scaled capture coefficient")
            word.append(["add", p, j, str(value)])
        if half:
            word.append(["scale", p, None, "1/2"])
    return word


def lower_query(rows, targets, source_offset):
    word = []
    for p, row in zip(targets, rows):
        denominators = {v.denominator for v in row.values()}
        need(denominators <= {1, 2}, "query coefficient denominator")
        scale = 2 if 2 in denominators else 1
        if scale == 2:
            word.append(["scale", p, None, "2"])
        for j, v in sorted(row.items()):
            value = scale * v
            word.append(["add", p, source_offset + j, str(value)])
        if scale == 2:
            word.append(["scale", p, None, "1/2"])
    return word


def replay(word, size):
    rows = identity(size)
    price = 0
    for op, target, source, raw in word:
        value = F(raw)
        numerator, denominator = abs(value.numerator), value.denominator
        need(denominator & (denominator - 1) == 0, "dyadic tariff")
        if op == "add":
            rows[target] = addrow(rows[target], rows[source], value)
            price += 2 * (3 + numerator.bit_length() - 1
                          + numerator.bit_count() + denominator.bit_length() - 1)
        else:
            need(op == "scale", "opcode")
            need(numerator & (numerator - 1) == 0, "power-of-two scale")
            rows[target] = {j: v * value for j, v in rows[target].items()}
            price += 2 * (abs(numerator.bit_length() - denominator.bit_length())
                          + int(value < 0))
    return rows, price


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "run-normal")
    args = parser.parse_args()
    model = load("native")["model"]
    flags = load("pairs")
    e = matrix(model["response"])
    u = matrix(model["correction_U"])
    v = matrix(model["correction_V"])
    base = identity(N)
    uv = mul(u, v)
    need(e == [addrow(a, b) for a, b in zip(base, uv)], "E factor")
    vp = [{j: row.get(p, F(0)) for j, p in enumerate(P) if row.get(p)}
          for row in v]
    vpi, det_vp = inv(vp)
    w = mul(vpi, v)
    need(all(row.get(p, F(0)) == (i == j)
             for i, row in enumerate(w) for j, p in enumerate(P)),
         "normalized pivot minor")
    c = [dict(row) for row in base]
    ci = [dict(row) for row in base]
    for p, row in zip(P, w):
        c[p] = row
        ci[p] = addrow({p: F(2)}, row, -1)
    need(mul(c, ci) == base and mul(ci, c) == base, "capture inverse")
    h = mul(v, u)
    h = [addrow(a, b) for a, b in zip(identity(16), h)]
    need(h == [{i: F(-5 if i < 8 else -7)} for i in range(16)],
         "centre action")
    need(mul(h, vp) == mul(vp, h), "pivot minor and centre action")
    lower = mul(u, vp)
    k = [dict(row) for row in base]
    for i, p in enumerate(P):
        k[p] = {p: h[i][i]}
    for r in set(range(N)) - set(P):
        for j, value in lower[r].items():
            k[r][P[j]] = value
    need(mul(mul(c, e), ci) == k, "encoded response")
    ce = mul(c, e)
    need([ce[p] for p in P] == mul(h, w), "selected response")
    need(all(ce[r] == e[r] for r in set(range(N)) - set(P)),
         "ordinary response changed")
    pair = identity(N)
    for record in flags["pair_codes"]:
        ports = record["ports"]
        need(not (set(ports) & set(P)) or set(ports) <= set(P),
             "partial selected pair")
        for p, row in zip(ports, record["matrix"]):
            pair[p] = {q: F(a) for q, a in zip(ports, row) if a}
    pairi, _ = inv(pair)
    cmode = mul(mul(pair, c), pairi)
    emode = mul(mul(pair, e), pairi)
    cemode = mul(mul(pair, ce), pairi)
    need(mul(cmode, emode) == cemode, "mode response order")
    need({i for i, row in enumerate(cemode) if row.get(i)} == set(P),
         "selected diagonal support")
    code_word = lower_shear(c)
    inverse_word = lower_shear(c, -1)
    got, code_price = replay(code_word, N)
    goti, inverse_price = replay(inverse_word, N)
    need(got == c and goti == ci, "literal capture words")
    need(code_price == inverse_price == 1760, "capture invoice")
    query_word = lower_query([ce[p] for p in P], P, N)
    rows, query_price = replay(query_word, 2 * N)
    expected = identity(2 * N)
    for p in P:
        expected[p] = addrow(expected[p], {N+j: a for j, a in ce[p].items()})
    need(rows == expected, "arbitrary-baseline final query")
    need(query_price == 3424, "final query invoice")
    payload = {
        "schema": "row-only-rank16-capture-v1",
        "source_pins": PINS,
        "pivots": P,
        "ordinary_ports": sorted(set(range(N)) - set(P)),
        "pivot_minor": dumpmatrix(vp),
        "pivot_minor_inverse": dumpmatrix(vpi),
        "pivot_minor_determinant": str(det_vp),
        "centre_reader": dumpmatrix(w),
        "response": dumpmatrix(e),
        "code": dumpmatrix(c),
        "code_inverse": dumpmatrix(ci),
        "encoded_response": dumpmatrix(k),
        "selected_capture_response": dumpmatrix(ce),
        "mode_capture_response": dumpmatrix(cemode),
        "scalar_word": code_word,
        "inverse_scalar_word": inverse_word,
        "final_query_word": query_word,
        "final_query_field_convention": "Y=0..111; FULL X=112..223",
    }
    args.output.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    (args.output / "ROW-CAPTURE.json").write_bytes(raw)
    receipt = {
        "status": "PASS_EXACT_ROW_CAPTURE",
        "payload_sha256": hashlib.sha256(raw).hexdigest(),
        "pivot_minor_determinant": str(det_vp),
        "code_and_inverse_scalar_price": code_price,
        "code_native_children": 0,
        "code_extra_fields": 0,
        "code_fixed_odd_scans": 0,
        "final_query_scalar_price": query_price,
        "final_query_real_fixed_odd_scans": 0,
        "final_query_borrowed_baseline_columns_checked": 224,
        "changed_mode_diagonal_ports": P,
        "native_capture_emitted_here": False,
        "supplier_terminal_closed": False,
    }
    (args.output / "CHECKS.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
