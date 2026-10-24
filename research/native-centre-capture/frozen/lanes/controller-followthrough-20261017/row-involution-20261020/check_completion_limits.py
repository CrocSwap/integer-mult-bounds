#!/usr/bin/env python3
"""Check the row bound, uniqueness premise, and symmetric completion."""

from fractions import Fraction as F
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json


HERE = Path(__file__).resolve().parent
SOURCE_PIN = "a25551b3b99b82477fde561a742fabe1114acbfe6c67cd14284747aaac3dd95b"
CHECKER_PIN = "a675e5578de4bc264524f7c1a75c5685a1967a65f7d3cd020fb0dc19352d31e9"
HELPER_PIN = "ccf661107a790c3d858a3f2bd4d8adc5269f588bfd989bd2e2029e26cbb14081"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path, pin):
    raw = path.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == pin, "source pin: " + str(path))
    return raw


def module(path, pin, name):
    read(path, pin)
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def finite_rank(a, ports, prime):
    rows = [[int(row.get(j, 0).numerator) *
             pow(int(row.get(j, F(0)).denominator), -1, prime) % prime
             for j in ports] for row in (a[i] for i in ports)]
    pivot = 0
    for j in range(len(ports)):
        found = next((i for i in range(pivot, len(rows)) if rows[i][j]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        inverse = pow(rows[pivot][j], -1, prime)
        rows[pivot] = [x * inverse % prime for x in rows[pivot]]
        for i in range(pivot + 1, len(rows)):
            value = rows[i][j]
            if value:
                rows[i] = [(x - value * y) % prime
                           for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
    return pivot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "limits-normal")
    args = parser.parse_args()
    base = module(HERE / "check_row_involution.py", CHECKER_PIN, "frozen_involution")
    h = module(HERE.parent / "row-capture-20261020/check_row_capture.py",
               HELPER_PIN, "frozen_capture")
    data = json.loads(read(HERE / "run-normal/ROW-INVOLUTION.json", SOURCE_PIN))
    a = h.matrix(data["response"])
    at = h.matrix(data["response_transpose"])
    e = h.matrix(data["original_response"])
    c = h.matrix(data["row_code"])
    ci = h.matrix(data["row_code_inverse"])
    u = h.matrix(data["correction_U"])
    p = data["pivots"]
    rest = data["ordinary_ports"]
    large = sorted(j for block in data["blocks"] if block["size"] == 6
                   for j in block["ports"])
    small = sorted(set(range(112)) - set(large))
    need(len(large) == 48 and len(small) == 64, "component dimensions")
    need(all(set(e[i]) <= set(large) for i in large), "large component support")
    need(all(set(e[i]) <= set(small) for i in small), "small component support")
    ranks = {"large_mod_5": finite_rank(e, large, 5),
             "small_mod_7": finite_rank(e, small, 7)}
    need(ranks == {"large_mod_5": 40, "small_mod_7": 56}, "modular nullities")
    need(base.rank([u[i] for i in rest], 16) == 16, "ordinary factor rank")
    identity = h.identity(112)
    difference = [h.addrow(x, y, -1) for x, y in zip(a, e)]
    need(base.rank(difference, 112) == 16, "actual row update rank")
    signature = [{i: F(-1 if i in p else 1)} for i in range(112)]
    symmetric = h.mul(c, a)
    direct = [h.addrow(row, {i: F(1)}, -1) if i in p else row
              for i, row in enumerate(e)]
    need(symmetric == direct, "diagonal completion")
    need(symmetric == base.transpose(symmetric, 112), "symmetric response")
    need(symmetric == h.mul(h.mul(base.transpose(c, 112), signature), c),
         "symmetric congruence")
    symmetric_inverse = h.mul(h.mul(ci, signature), base.transpose(ci, 112))
    need(h.mul(symmetric, symmetric_inverse) == identity, "right inverse")
    need(h.mul(symmetric_inverse, symmetric) == identity, "left inverse")
    need(base.rank([h.addrow(x, y, -1)
                    for x, y in zip(symmetric, identity)], 112) == 32,
         "symmetric displacement rank")
    query = h.lower_query([symmetric[i] for i in p], p, 112)
    actual, query_price = h.replay(query, 224)
    expected = h.identity(224)
    for i in p:
        expected[i] = h.addrow(expected[i],
                              {112 + j: value for j, value in symmetric[i].items()})
    need(actual == expected and query_price == 1904, "symmetric query")
    flags = h.load("pairs")
    pair_word = []
    for record in flags["pair_codes"]:
        x, y = record["ports"]
        (aa, bb), (cc, dd) = record["matrix"]
        if aa != 1:
            pair_word.append(["scale", x, None, str(aa)])
        pair_word += [["add", x, y, str(bb)], ["scale", y, None, str(2 * dd)],
                      ["add", y, x, str(F(cc, aa))]]
    capture_mode_word = []
    for block in data["blocks"]:
        for port, sign in zip(block["ports"], block["signs"]):
            if port != block["pivot"]:
                capture_mode_word.append(["add", block["pivot"], port, sign])
    signs_word = [["scale", port, None, "-1"] for port in p]
    pair_inverse = base.inverse_word(pair_word)
    symmetric_word = (pair_word + capture_mode_word + signs_word +
                      base.transpose_word(capture_mode_word) + pair_inverse)
    inverse_word = base.inverse_word(symmetric_word)
    actual, scalar_price = h.replay(symmetric_word, 112)
    actual_inverse, inverse_price = h.replay(inverse_word, 112)
    need(actual == symmetric and actual_inverse == symmetric_inverse,
         "symmetric scalar words")
    need(scalar_price == inverse_price == 2508, "symmetric scalar tariff")
    metric = h.identity(112)
    for i in range(112):
        metric[i] = {i: F(-1)}
    for block in data["blocks"]:
        metric[block["pivot"]] = {block["pivot"]: F(block["size"] - 3)}
    metric_inverse = [{i: 1 / metric[i][i]} for i in range(112)]
    need(h.mul(h.mul(metric_inverse, a), metric) == at, "diagonal similarity")
    need(h.mul(h.mul(at, metric_inverse), a) == metric_inverse,
         "inverse metric preservation")
    need(h.mul(h.mul(a, metric), at) == metric, "metric preservation")
    payload = {
        "schema": "row-completion-limits-v1",
        "source_payload_sha256": SOURCE_PIN,
        "large_ports": large, "small_ports": small, "pivots": p,
        "symmetric_response": h.dumpmatrix(symmetric),
        "symmetric_response_inverse": h.dumpmatrix(symmetric_inverse),
        "symmetric_query_word": query,
        "symmetric_word": symmetric_word,
        "symmetric_inverse_word": inverse_word,
        "metric": h.dumpmatrix(metric),
        "metric_inverse": h.dumpmatrix(metric_inverse),
    }
    args.output.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    (args.output / "COMPLETION-LIMITS.json").write_bytes(raw)
    receipt = {
        "status": "PASS_ROW_COMPLETION_LIMITS",
        "payload_sha256": hashlib.sha256(raw).hexdigest(),
        "modular_ranks": ranks,
        "minimum_dyadic_unit_row_changes": 16,
        "ordinary_factor_rank": 16,
        "actual_rank_A_minus_E": 16,
        "symmetric_displacement_rank": 32,
        "symmetric_determinant": "1",
        "symmetric_query_scalar": query_price,
        "symmetric_word_and_inverse_scalar": scalar_price,
        "metric_values": ["-1", "3", "5"],
        "inverse_metric_contains_odd_denominators": True,
        "native_services_emitted_here": False,
        "supplier_terminal_closed": False,
    }
    (args.output / "CHECKS.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
