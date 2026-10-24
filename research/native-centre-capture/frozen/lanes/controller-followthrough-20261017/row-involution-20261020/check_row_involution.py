#!/usr/bin/env python3
"""Check a dyadic involution that changes sixteen response rows."""

from fractions import Fraction as F
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "row-capture-20261020"
HELPER_PIN = "ccf661107a790c3d858a3f2bd4d8adc5269f588bfd989bd2e2029e26cbb14081"
CAPTURE_PIN = "4c98af5d7a1437a03f53e84f0f2cbc7cd2ac47d4c6d4ee1523c16bf469692eb7"
N = 112


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pinned(path, pin):
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == pin, "source pin: " + str(path))
    return raw


def transpose(a, width):
    result = [{} for _ in range(width)]
    for i, row in enumerate(a):
        for j, value in row.items():
            result[j][i] = value
    return result


def rank(a, width):
    rows = [[row.get(j, F(0)) for j in range(width)] for row in a]
    pivot_row = 0
    for j in range(width):
        found = next((i for i in range(pivot_row, len(rows)) if rows[i][j]), None)
        if found is None:
            continue
        rows[pivot_row], rows[found] = rows[found], rows[pivot_row]
        value = rows[pivot_row][j]
        rows[pivot_row] = [x / value for x in rows[pivot_row]]
        for i in range(pivot_row + 1, len(rows)):
            value = rows[i][j]
            if value:
                rows[i] = [x - value * y
                           for x, y in zip(rows[i], rows[pivot_row])]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def inverse_word(word):
    result = []
    for op, target, source, raw in reversed(word):
        value = F(raw)
        result.append([op, target, source,
                       str(-value if op == "add" else 1 / value)])
    return result


def transpose_word(word):
    return [[op, source, target, value] if op == "add"
            else [op, target, None, value]
            for op, target, source, value in reversed(word)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "run-normal")
    args = parser.parse_args()
    helper_path = SOURCE / "check_row_capture.py"
    pinned(helper_path, HELPER_PIN)
    spec = importlib.util.spec_from_file_location("frozen_row_capture", helper_path)
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    capture = json.loads(pinned(SOURCE / "run-normal/ROW-CAPTURE.json", CAPTURE_PIN))
    model = h.load("native")["model"]
    flags = h.load("pairs")
    p = capture["pivots"]
    pset = set(p)
    rest = sorted(set(range(N)) - pset)
    eye = h.identity(N)
    e = h.matrix(model["response"])
    u = h.matrix(model["correction_U"])
    v = h.matrix(model["correction_V"])
    vp = h.matrix(capture["pivot_minor"])
    vpi = h.matrix(capture["pivot_minor_inverse"])
    c = h.matrix(capture["code"])
    ci = h.matrix(capture["code_inverse"])
    modified_u = [dict(row) for row in u]
    ordinary_u = [dict(row) if i in rest else {} for i, row in enumerate(u)]
    vu_ordinary = h.mul(v, ordinary_u)
    desired = [h.addrow({i: F(-2)}, row, -1)
               for i, row in enumerate(vu_ordinary)]
    selected_u = h.mul(vpi, desired)
    for port, row in zip(p, selected_u):
        modified_u[port] = row
    require(h.mul(v, modified_u) == [{i: F(-2)} for i in range(16)],
            "centre contraction")
    correction = h.mul(modified_u, v)
    a = [h.addrow(x, y) for x, y in zip(eye, correction)]
    at = transpose(a, N)
    require(h.mul(a, a) == eye, "A squared")
    require(h.mul(at, at) == eye, "transpose squared")
    require(all(a[i] == e[i] for i in rest), "ordinary row preservation")
    require(all(at[i].get(j, F(0)) == e[i].get(j, F(0))
                for i in range(N) for j in rest), "ordinary column preservation")
    require(rank(correction, N) == 16, "displacement rank")
    require(all(x.denominator & (x.denominator - 1) == 0
                for row in a for x in row.values()), "dyadic entries")
    require(sum(a[i].get(i, F(0)) for i in range(N)) == 80, "trace")
    pair = h.identity(N)
    for record in flags["pair_codes"]:
        ports = record["ports"]
        require(not (set(ports) & pset) or set(ports) <= pset,
                "selected pair closure")
        for port, row in zip(ports, record["matrix"]):
            pair[port] = {q: F(x) for q, x in zip(ports, row) if x}
    pairi, _ = h.inv(pair)
    mode_e = h.mul(h.mul(pair, e), pairi)
    mode_a = h.mul(h.mul(pair, a), pairi)
    mode_at = h.mul(h.mul(pair, at), pairi)
    require(mode_at == transpose(mode_a, N), "physical transpose in mode chart")
    blocks = []
    for group in model["vertex_assignments"]:
        ports = group["ordered_carriers_a_b_c"]
        blocks.append((ports, list(map(F, group["signs"]))))
    blocks += [(ports, [F(1)] * len(ports)) for ports in model["small_cliques"]]
    direct = h.identity(N)
    expected_mode_e = h.identity(N)
    block_records = []
    for ports, signs in blocks:
        selected = pset & set(ports)
        require(len(selected) == 1, "one pivot per block")
        pivot = next(iter(selected))
        d = dict(zip(ports, signs))
        require(d[pivot] == 1, "positive pivot sign")
        k = len(ports)
        require(k in (6, 8), "block size")
        for i in ports:
            row_u = F(k - 2 if i == pivot else 0) - d[i]
            direct[i] = h.addrow({i: F(1)}, d, row_u)
            expected_mode_e[i] = h.addrow({i: F(1)}, d, -d[i])
        block_records.append({
            "ports": ports, "signs": [str(x) for x in signs],
            "pivot": pivot, "size": k,
            "pivot_column_transpose_multiplier": -(k - 3),
        })
    require(direct == mode_a, "independent signed block construction")
    require(expected_mode_e == mode_e, "original signed block response")
    require({i for i, row in enumerate(mode_a) if row.get(i)} == pset,
            "mode diagonal support")
    require({i for i, row in enumerate(a) if row.get(i)} == pset,
            "physical diagonal support")
    for block in block_records:
        pivot = block["pivot"]
        multiple = block["pivot_column_transpose_multiplier"]
        for i in block["ports"]:
            if i != pivot:
                require(mode_at[i][pivot] == multiple * mode_e[i][pivot],
                        "transpose weight slot")
    for direction, response in (("A", mode_a), ("AT", mode_at)):
        for i in rest:
            require(set(response[i]) == set(mode_e[i]),
                    direction + " ordinary native support")
    encoded = h.mul(h.mul(c, a), ci)
    expected_encoded = h.identity(N)
    fanout = h.mul(modified_u, vp)
    for i, port in enumerate(p):
        expected_encoded[port] = {port: F(-1)}
    for r in rest:
        expected_encoded[r] = h.addrow(
            expected_encoded[r], {p[j]: x for j, x in fanout[r].items()})
    require(encoded == expected_encoded, "lower triangular encoded response")
    queries = {}
    query_prices = {}
    for name, response in (("A", a), ("AT", at)):
        word = h.lower_query([response[port] for port in p], p, N)
        actual, price = h.replay(word, 2 * N)
        expected = h.identity(2 * N)
        for port in p:
            expected[port] = h.addrow(
                expected[port], {N + j: x for j, x in response[port].items()})
        require(actual == expected, name + " arbitrary baseline query")
        queries[name] = word
        query_prices[name] = price
    lower_word = []
    for r in rest:
        for j, value in sorted(fanout[r].items()):
            lower_word.append(["add", r, p[j], str(value)])
    gauge_word = list(capture["scalar_word"]) + lower_word
    gauge_word += [["scale", port, None, "-1"] for port in p]
    gauge_word += capture["inverse_scalar_word"]
    actual, gauge_price = h.replay(gauge_word, N)
    require(actual == a, "literal common frame involution")
    require(h.replay(gauge_word + gauge_word, N)[0] == eye, "literal gauge square")
    at_word = transpose_word(gauge_word)
    actual_at, transpose_price = h.replay(at_word, N)
    require(actual_at == at, "literal common frame transpose")
    require(gauge_price == transpose_price, "transpose scalar invoice")
    pair_word = []
    for record in flags["pair_codes"]:
        x, y = record["ports"]
        (aa, bb), (cc, dd) = record["matrix"]
        if aa != 1:
            pair_word.append(["scale", x, None, str(aa)])
        pair_word.append(["add", x, y, str(bb)])
        pair_word.append(["scale", y, None, str(2 * dd)])
        pair_word.append(["add", y, x, str(F(cc, aa))])
    require(h.replay(pair_word, N)[0] == pair, "literal pair code")
    pair_inverse_word = inverse_word(pair_word)
    require(h.replay(pair_inverse_word, N)[0] == pairi, "literal inverse pair code")
    mode_word = []
    for record in block_records:
        pivot = record["pivot"]
        signed = list(zip(record["ports"], record["signs"]))
        for port, sign in signed:
            if port != pivot:
                mode_word.append(["add", pivot, port, sign])
        for port, sign in signed:
            if port != pivot:
                mode_word.append(["add", port, pivot, str(-F(sign))])
        mode_word.append(["scale", pivot, None, "-1"])
        for port, sign in signed:
            if port != pivot:
                mode_word.append(["add", pivot, port, str(-F(sign))])
    require(h.replay(mode_word, N)[0] == mode_a, "literal signed block word")
    short_word = pair_word + mode_word + pair_inverse_word
    short_at_word = transpose_word(short_word)
    short_a, short_price = h.replay(short_word, N)
    short_at, short_at_price = h.replay(short_at_word, N)
    require(short_a == a and short_at == at, "short physical words")
    require(short_price == short_at_price < gauge_price, "short word tariff")
    require(h.replay(short_word + short_word, N)[0] == eye,
            "short word involution")
    payload = {
        "schema": "rank16-row-involution-v1",
        "source_pins": {
            "capture_checker": HELPER_PIN, "capture_payload": CAPTURE_PIN,
            **{name: item[1] for name, item in h.PINS.items()},
        },
        "pivots": p, "ordinary_ports": rest,
        "blocks": block_records,
        "response": h.dumpmatrix(a),
        "response_transpose": h.dumpmatrix(at),
        "response_inverse": h.dumpmatrix(a),
        "response_inverse_transpose": h.dumpmatrix(at),
        "original_response": h.dumpmatrix(e),
        "mode_response": h.dumpmatrix(mode_a),
        "mode_response_transpose": h.dumpmatrix(mode_at),
        "correction_U": h.dumpmatrix(modified_u),
        "correction_V": h.dumpmatrix(v),
        "row_code": h.dumpmatrix(c),
        "row_code_inverse": h.dumpmatrix(ci),
        "encoded_response": h.dumpmatrix(encoded),
        "final_query_words": queries,
        "query_field_convention": "Y=0..111; FULL X=112..223",
        "common_frame_words": {"A": short_word, "AT": short_at_word},
        "direct_physical_words": {"A": gauge_word, "AT": at_word},
    }
    args.output.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    (args.output / "ROW-INVOLUTION.json").write_bytes(raw)
    receipt = {
        "status": "PASS_EXACT_ROW_INVOLUTION",
        "payload_sha256": hashlib.sha256(raw).hexdigest(),
        "displacement_rank": 16,
        "determinant": "1",
        "trace": 80,
        "negative_eigenvalue_multiplicity": 16,
        "ordinary_rows_unchanged": 96,
        "ordinary_columns_unchanged_in_transpose": 96,
        "both_involution_orders": True,
        "mode_and_physical_transpose_match": True,
        "query_baseline_columns_each": 224,
        "final_query_scalar_prices": query_prices,
        "common_frame_scalar_price_each": short_price,
        "direct_physical_scalar_price_each": gauge_price,
        "all_arithmetic_dyadic": True,
        "owned_fields": 0,
        "native_service_emitted_here": False,
        "supplier_terminal_closed": False,
    }
    (args.output / "CHECKS.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
