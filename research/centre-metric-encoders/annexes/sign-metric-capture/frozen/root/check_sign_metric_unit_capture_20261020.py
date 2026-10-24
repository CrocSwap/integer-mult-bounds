#!/usr/bin/env python3
"""Check the dyadic centre minor of the thirty-two-carrier variant."""

from pathlib import Path
import argparse
import hashlib
import importlib.util
import json


HERE = Path(__file__).resolve().parent
HELPER = HERE / "check_sign_metric_involutions_20261020.py"
HELPER_SHA = "4c053a9fbc5da82ec1ef39c6740256f3fc0f6d5784df630130b1110a7efae863"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=HERE / "sign-metric-unit-normal-20261020")
    args = parser.parse_args()
    if hashlib.sha256(HELPER.read_bytes()).hexdigest() != HELPER_SHA:
        raise ValueError("helper pin")
    spec = importlib.util.spec_from_file_location("frozen_gaussian_helpers", HELPER)
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    sources = {}
    for key, (path, pin) in g.PINS.items():
        raw = (g.LANES / path).read_bytes()
        g.need(hashlib.sha256(raw).hexdigest() == pin, "source pin: " + key)
        sources[key] = json.loads(raw)
    blocks = sources["rows"]["blocks"]
    pivots = sources["rows"]["pivots"]
    selected = set(pivots) | {2, 25, 13, 51, 11, 63, 42, 105}
    for block in blocks:
        if block["size"] == 8:
            selected.add(next(p for p in block["ports"] if p != block["pivot"]))
    g.need(len(selected) == 32, "thirty-two selected fields")
    h, hi = g.eye(112), g.eye(112)
    for record in sources["pairs"]["pair_codes"]:
        p, q = record["ports"]
        g.need((p in selected) == (q in selected), "full pair closure")
        g.need((p in pivots) == (q in pivots), "centre pair closure")
        m = [[g.F(x) for x in row] for row in record["matrix"]]
        determinant = m[0][0] * m[1][1] - m[0][1] * m[1][0]
        inv = [[m[1][1] / determinant, -m[0][1] / determinant],
               [-m[1][0] / determinant, m[0][0] / determinant]]
        for port, row, inverse in zip((p, q), m, inv):
            h[port] = {j: g.real(x) for j, x in zip((p, q), row) if x}
            hi[port] = {j: g.real(x) for j, x in zip((p, q), inverse) if x}
    metric = [{p: g.real(-1 if p in selected else 1)} for p in range(112)]
    u, v, section = [{} for _ in range(112)], [], [{} for _ in range(112)]
    for index, block in enumerate(blocks):
        d = {p: g.F(s) for p, s in zip(block["ports"], block["signs"])}
        sel = selected & set(block["ports"])
        g.need(len(sel) == 2, "two selected ports per block")
        w = {p: (d[p], d[p] if block["size"] == 8 and p in sel else g.F(0))
             for p in block["ports"]}
        reader = {}
        for p in block["ports"]:
            u[p][index] = w[p]
            reader[p] = g.times(g.conjugate(w[p]), g.real(1 if p in selected else -1))
        v.append(reader)
        a, b = reader[block["pivot"]]
        norm = a * a + b * b
        section[block["pivot"]][index] = (a / norm, -b / norm)
    g.need(g.multiply(v, u) == [{i: g.real(-2)} for i in range(16)],
           "metric contraction")
    g.need(g.multiply(v, section) == g.eye(16), "mode dyadic section")
    up, vp = g.multiply(hi, u), g.multiply(v, h)
    jp = g.multiply(hi, section)
    g.need(g.multiply(vp, jp) == g.eye(16), "physical dyadic section")
    g.need(all(not row for p, row in enumerate(jp) if p not in pivots),
           "section supported on sixteen centre carriers")
    response = g.eye(112)
    for i, row in enumerate(g.multiply(up, vp)):
        for j, value in row.items():
            g.put(response[i], j, value)
    inverse_minor = [jp[p] for p in pivots]
    minor = [{j: row[p] for j, p in enumerate(pivots) if p in row} for row in vp]
    g.need(g.multiply(minor, inverse_minor) == g.eye(16), "minor right inverse")
    g.need(g.multiply(inverse_minor, minor) == g.eye(16), "minor left inverse")
    reader = g.multiply(inverse_minor, vp)
    g.need([{j: row[p] for j, p in enumerate(pivots) if p in row}
            for row in reader] == g.eye(16), "normalized centre reader")
    code, inverse_code = g.eye(112), g.eye(112)
    for p, row in zip(pivots, reader):
        code[p] = dict(row)
        inverse_code[p] = {j: (value if j == p else g.neg(value))
                           for j, value in row.items()}
    g.need(g.multiply(code, inverse_code) == g.multiply(inverse_code, code) == g.eye(112),
           "both centre code inverse orders")
    g.need(g.multiply(reader, response) ==
           [{j: g.neg(value) for j, value in row.items()} for row in reader],
           "centre action is minus identity")
    g.need(g.multiply(response, response) == g.eye(112), "response involution")
    g.need(g.adjoint(response, 112) == g.multiply(g.multiply(metric, response), metric),
           "sign-metric adjoint")
    g.need({p for p in range(112) if response[p].get(p, g.ZERO) != g.ZERO} == selected,
           "exact diagonal support")
    for matrix in (response, inverse_minor, reader, code, inverse_code):
        for row in matrix:
            for value in row.values():
                for x in value:
                    g.need(x.denominator & (x.denominator - 1) == 0, "Gaussian dyadic entry")
    payload = {
        "schema": "sign-metric-rank16-unit-centre-v1",
        "source_pins": {"helper": HELPER_SHA, **{k: p for k, (_, p) in g.PINS.items()}},
        "full_ports": sorted(selected),
        "centre_ports": pivots,
        "response": g.serialize(response),
        "metric": g.serialize(metric),
        "correction_U": g.serialize(up),
        "correction_V": g.serialize(vp),
        "centre_minor": g.serialize(minor),
        "centre_minor_inverse": g.serialize(inverse_minor),
        "centre_reader": g.serialize(reader),
        "row_code": g.serialize(code),
        "row_code_inverse": g.serialize(inverse_code),
    }
    raw = g.encoded(payload)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "RESPONSE.json").write_bytes(raw)
    receipt = {
        "status": "PASS_EXACT_SIGN_METRIC_UNIT_CAPTURE",
        "payload_sha256": hashlib.sha256(raw).hexdigest(),
        "data_ports": 112, "full_ports": 32, "centre_ports": 16,
        "correction_rank": 16, "centre_minor_is_gaussian_dyadic_unit": True,
        "code_displacement_square_is_zero": True,
        "native_word_emitted": False, "scalar_invoice_established": False,
        "full_caller_closed": False,
    }
    (args.output / "CHECKS.json").write_bytes(g.encoded(receipt))
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
