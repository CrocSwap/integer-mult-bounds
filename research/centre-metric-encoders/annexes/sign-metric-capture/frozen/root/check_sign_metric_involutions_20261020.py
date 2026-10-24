#!/usr/bin/env python3
"""Check a Gaussian dyadic response with a diagonal sign metric."""

from fractions import Fraction as F
from pathlib import Path
import argparse
import hashlib
import json


HERE = Path(__file__).resolve().parent
LANES = HERE.parent / "lanes"
N = 112
PINS = {
    "rows": (
        "controller-followthrough-20261017/row-involution-20261020/"
        "run-normal/ROW-INVOLUTION.json",
        "a25551b3b99b82477fde561a742fabe1114acbfe6c67cd14284747aaac3dd95b",
    ),
    "pairs": (
        "independent-review-20261017/cyclic-pair-flags-20261018/"
        "CYCLIC-FLAGS.json",
        "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585",
    ),
}
ZERO = (F(0), F(0))
ONE = (F(1), F(0))


def need(condition, text):
    if not condition:
        raise ValueError(text)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def neg(a):
    return -a[0], -a[1]


def times(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def conjugate(a):
    return a[0], -a[1]


def real(x):
    return F(x), F(0)


def eye(n):
    return [{j: ONE} for j in range(n)]


def put(row, j, value):
    value = add(row.get(j, ZERO), value)
    if value == ZERO:
        row.pop(j, None)
    else:
        row[j] = value


def multiply(a, b):
    result = []
    for row in a:
        out = {}
        for j, x in row.items():
            for k, y in b[j].items():
                put(out, k, times(x, y))
        result.append(out)
    return result


def adjoint(a, width):
    out = [{} for _ in range(width)]
    for i, row in enumerate(a):
        for j, value in row.items():
            out[j][i] = conjugate(value)
    return out


def serialize(a):
    return [{str(j): [str(x), str(y)] for j, (x, y) in sorted(row.items())}
            for row in a]


def encoded(x):
    return (json.dumps(x, sort_keys=True, indent=2) + "\n").encode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=HERE / "sign-metric-normal-20261020")
    args = parser.parse_args()
    sources = {}
    for key, (path, pin) in PINS.items():
        raw = (LANES / path).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == pin, "source pin: " + key)
        sources[key] = json.loads(raw)
    rows, pairs = sources["rows"], sources["pairs"]
    blocks = rows["blocks"]
    old_p = set(rows["pivots"])
    extra = {2, 25, 13, 51, 11, 63, 42, 105}
    selected = old_p | extra
    need(len(selected) == 24, "selected count")
    h, hi = eye(N), eye(N)
    for record in pairs["pair_codes"]:
        p, q = record["ports"]
        need((p in selected) == (q in selected), "selected physical pair closure")
        m = [[F(v) for v in row] for row in record["matrix"]]
        determinant = m[0][0] * m[1][1] - m[0][1] * m[1][0]
        inverse = [[m[1][1] / determinant, -m[0][1] / determinant],
                   [-m[1][0] / determinant, m[0][0] / determinant]]
        for port, row, inverse_row in zip((p, q), m, inverse):
            h[port] = {j: real(v) for j, v in zip((p, q), row) if v}
            hi[port] = {j: real(v) for j, v in zip((p, q), inverse_row) if v}
    need(multiply(h, hi) == multiply(hi, h) == eye(N), "physical pair inverses")
    metric = [{p: real(-1 if p in selected else 1)} for p in range(N)]
    need(multiply(h, metric) == multiply(metric, h), "metric and pair code commute")
    mode = eye(N)
    u = [{} for _ in range(N)]
    v = []
    records = []
    for index, block in enumerate(blocks):
        ports = block["ports"]
        d = {p: F(x) for p, x in zip(ports, block["signs"])}
        pivots = sorted(set(ports) & selected)
        need(len(pivots) == (2 if len(ports) == 6 else 1), "block pivot count")
        w = {p: real(d[p]) for p in ports}
        if len(ports) == 8:
            p = pivots[0]
            w[p] = (d[p], 2 * d[p])
        contraction = ZERO
        reader = {}
        for p in ports:
            sigma = -1 if p in selected else 1
            term = times(conjugate(w[p]), real(sigma))
            contraction = add(contraction, times(term, w[p]))
            reader[p] = neg(term)
            u[p][index] = w[p]
        need(contraction == real(2), "block metric norm")
        v.append(reader)
        for p in ports:
            for q in ports:
                put(mode[p], q, times(w[p], reader[q]))
        records.append({"ports": ports, "selected": pivots,
                        "w": {str(p): [str(a), str(b)] for p, (a, b) in w.items()}})
    need(multiply(v, u) == [{i: real(-2)} for i in range(16)],
         "rank-sixteen contraction")
    physical = multiply(multiply(hi, mode), h)
    up = multiply(hi, u)
    vp = multiply(v, h)
    displacement = multiply(up, vp)
    expected = eye(N)
    for i, row in enumerate(displacement):
        for j, value in row.items():
            put(expected[i], j, value)
    need(expected == physical, "physical displacement factorization")
    need(multiply(physical, physical) == eye(N), "physical involution")
    star = adjoint(physical, N)
    need(star == multiply(multiply(metric, physical), metric), "sign-metric adjoint")
    need(multiply(multiply(star, metric), physical) == metric, "metric preservation")
    need({p for p in range(N) if physical[p].get(p, ZERO) != ZERO} == selected,
         "physical diagonal support")
    need(sum(physical[p].get(p, ZERO)[0] for p in range(N)) == 80, "trace")
    old = [{int(j): real(x) for j, x in row.items()}
           for row in rows["original_response"]]
    old_mode = multiply(multiply(h, old), hi)
    ordinary = set(range(N)) - selected
    for p in ordinary:
        need(set(mode[p]) == set(old_mode[p]), "ordinary mode support")
        for q in ordinary:
            need(mode[p].get(q, ZERO) == old_mode[p].get(q, ZERO),
                 "ordinary-to-ordinary coefficients")
    for row in physical:
        for value in row.values():
            for component in value:
                den = component.denominator
                need(den & (den - 1) == 0, "Gaussian dyadic coefficient")
    payload = {
        "schema": "sign-metric-rank16-response-v1",
        "source_pins": {name: pin for name, (_, pin) in PINS.items()},
        "selected": sorted(selected),
        "extra_selected": sorted(extra),
        "blocks": records,
        "mode_response": serialize(mode),
        "response": serialize(physical),
        "response_adjoint": serialize(star),
        "metric": serialize(metric),
        "correction_U": serialize(up),
        "correction_V": serialize(vp),
    }
    raw = encoded(payload)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "RESPONSE.json").write_bytes(raw)
    receipt = {
        "status": "PASS_EXACT_SIGN_METRIC_RESPONSE",
        "payload_sha256": hashlib.sha256(raw).hexdigest(),
        "data_ports": N,
        "selected_ports": 24,
        "correction_rank": 16,
        "trace": 80,
        "determinant": 1,
        "large_blocks": 8,
        "small_blocks": 8,
        "all_coefficients_gaussian_dyadic": True,
        "metric_diagonal_signs_only": True,
        "ordinary_mode_support_unchanged": True,
        "native_word_emitted": False,
        "native_invoice_established": False,
        "complete_caller_closed": False,
    }
    (args.output / "CHECKS.json").write_bytes(encoded(receipt))
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
