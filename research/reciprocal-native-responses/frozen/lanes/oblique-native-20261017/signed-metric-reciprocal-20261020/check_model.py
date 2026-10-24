#!/usr/bin/env python3
"""Bind the signed metric and reciprocal response to the actual ports."""

import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
PINS = {
    "placement": (
        "new-core-transfer-20261017/low-displacement-20261020/metric-completion-20261020/signed-probe/METRIC-COMPLETION.json.gz",
        "88a9f75fa87b1a258d6465e309785c1aaec1be6393d46e51bc0a469e62f09e5e"),
    "cyclic": (
        "independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json",
        "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585"),
    "arithmetic": (
        "new-core-transfer-20261017/low-displacement-20261020/check_response.py",
        "c6d92104e4345816e86163f6c1dea24fbd9b6e9b133ffd2e0c646dca17ca00a8"),
}


def need(test, message):
    if not test:
        raise ValueError(message)


def read(name):
    relative, pin = PINS[name]
    path = LANES / relative
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, "Source pin " + name)
    return raw


read("arithmetic")
spec = importlib.util.spec_from_file_location("signed_metric_arithmetic", LANES / PINS["arithmetic"][0])
r = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r
spec.loader.exec_module(r)


def rows(value):
    return [{int(p): F(c) for p, c in row.items() if F(c)} for row in value]


def difference(a, b):
    out = [dict(row) for row in a]
    for left, right in zip(out, b):
        r.add(left, right, -1)
    return out


def diag(values):
    return [{i: F(c)} for i, c in enumerate(values)]


def substitute(local, ports, matrix):
    for i, p in enumerate(ports):
        matrix[p] = {ports[j]: c for j, c in local[i].items() if c}


def block(n):
    m = n - 4
    u = [F(1)] * (n - 2) + [F(m), F(0)]
    ell = [F(-1)] * (n - 2) + [F(1), F(0)]
    reflection = r.identity(n)
    for i in range(n):
        r.add(reflection[i], {j: c for j, c in enumerate(ell) if c}, u[i])
    permutation = r.identity(n)
    permutation[-2], permutation[-1] = permutation[-1], permutation[-2]
    metric = diag([F(1)] * (n - 2) + [F(-1, m), F(-1, m)])
    metric_inverse = diag([1 / row[i] for i, row in enumerate(metric)])
    response = r.product(permutation, reflection)
    inverse = r.product(reflection, permutation)
    need(r.product(reflection, reflection) == r.identity(n), "Local reflection square")
    need(r.product(response, inverse) == r.product(inverse, response) == r.identity(n),
         "Both local inverse orders")
    need(r.product(r.product(r.transpose(response, n), metric), response) == metric,
         "Local signed metric")
    need(sum(ell[i] * metric_inverse[i][i] * ell[i] for i in range(n)) == 2,
         "The centre has signed norm two")
    need(all(not response[i].get(i) and not inverse[i].get(i) for i in range(n)),
         "Both local native diagonals vanish")
    return response, inverse, reflection, permutation, metric, metric_inverse, u, ell


def swap_word(b, c):
    return [["add", b, c, "1"], ["add", c, b, "-1"],
            ["add", b, c, "1"], ["scale", c, None, "-1"]]


def reflection_word(ports):
    a, b = ports[:-2], ports[-2]
    return ([["add", b, p, "-1"] for p in a]
            + [["add", p, b, "1"] for p in a]
            + [["scale", b, None, "-1"]]
            + [["add", b, p, "1"] for p in a])


def pair_word(pairs):
    word = []
    for pair in pairs:
        a, b = pair["ports"]
        aa, ab = pair["matrix"][0]
        ba, bb = pair["matrix"][1]
        if aa != 1:
            word.append(["scale", a, None, str(aa)])
        word.extend([["add", a, b, str(ab)], ["scale", b, None, str(2 * bb)],
                     ["add", b, a, str(ba * aa)]])
    return word


def full_replay(word):
    state = r.identity(640)
    peak, height = F(1), 0
    for op, target, source, coefficient in word:
        c = F(coefficient)
        if op == "add":
            need(target != source, "Distinct scalar fields")
            r.add(state[target], state[source], c)
        else:
            need(op == "scale", "Scalar grammar")
            state[target] = {p: c * v for p, v in state[target].items() if c * v}
        peak = max(peak, sum(abs(v) for v in state[target].values()))
        for value in state[target].values():
            denominator = value.denominator
            need(not denominator & (denominator - 1), "No odd denominator")
            height = max(height, denominator.bit_length() - 1)
    need(state[112:] == r.identity(640)[112:], "All outside fields are unchanged")
    return state[:112], {
        "real_scalar_primitives": r.price(word), "instructions": len(word),
        "prefix_row_l1_bound": str(peak), "binary_height": height,
        "all_input_columns": 640, "untouched_arbitrary_fields": 528,
    }


def make_model():
    placement, cyclic = json.loads(read("placement")), json.loads(read("cyclic"))
    H, Hi = rows(placement["pair_code"]), rows(placement["pair_code_inverse"])
    need(r.product(H, Hi) == r.product(Hi, H) == r.identity(112), "Actual pair code inverse")
    names = ("E", "inverse_E", "R", "P", "J", "inverse_J")
    modes = {name: r.identity(112) for name in names}
    blocks, special, centres = [], [], []
    mode_u, mode_l = [{} for _ in range(112)], []
    eword, pword, rword = [], [], []
    for record in placement["mode_blocks"]:
        if record["kind"] == "large6":
            roles = record["roles"]
            ports = [roles[label] for label in (
                "centre", "pair_difference_a", "pair_difference_b",
                "negative_difference", "contrast", "negative")]
            need(set(ports) == set(cyclic["cyclic_carriers"][record["vertex"]]),
                 "The six carriers use the actual vertex")
        else:
            need(record["kind"] == "small8", "Known block kind")
            ports = record["ports"]
            need(all((placement["ports"][p] & placement["ports"][q]).bit_count() % 2
                     == int(p == q) for p in ports for q in ports),
                 "An actual orthonormal eight-clique")
        local = block(len(ports))
        for name, matrix in zip(names, local[:6]):
            substitute(matrix, ports, modes[name])
        index = len(blocks)
        for p, value in zip(ports, local[6]):
            if value:
                mode_u[p] = {index: value}
        mode_l.append({p: value for p, value in zip(ports, local[7]) if value})
        special.extend(ports[-2:])
        centres.append(ports[0])
        rw, pw = reflection_word(ports), swap_word(*ports[-2:])
        eword += rw + pw
        rword += rw
        pword += pw
        blocks.append({"kind": record["kind"], "index": index, "ports": ports,
                       "centre": ports[0], "b": ports[-2], "c": ports[-1],
                       "u": [str(c) for c in local[6]],
                       "ell": [str(c) for c in local[7]],
                       **({"vertex": record["vertex"]} if record["kind"] == "large6" else {})})
    need(sorted(p for b in blocks for p in b["ports"]) == list(range(112)),
         "The sixteen blocks partition all112 ports")
    need(len(set(special)) == 32, "Thirty-two special physical fields")
    special_set = set(special)
    need(all(not special_set.intersection(pair["ports"])
             or set(pair["ports"]) <= special_set for pair in cyclic["pair_codes"]),
         "The special large modes are complete physical pairs")
    physical = {name: r.product(Hi, r.product(matrix, H)) for name, matrix in modes.items()}
    I = r.identity(112)
    E, Ei, R, P, J, Ji = (physical[name] for name in names)
    for name in ("J", "inverse_J"):
        need(all(set(row) == {p} for p, row in enumerate(physical[name])),
             "The physical metric is diagonal")
    need(Counter(row[p] for p, row in enumerate(J)) == {F(1): 80, F(-1, 2): 16, F(-1, 4): 16},
         "Actual metric weights")
    need(r.product(E, Ei) == r.product(Ei, E) == I and r.product(P, R) == E
         and r.product(P, P) == r.product(R, R) == I, "Full112 reciprocal and reflection identities")
    need(r.product(r.product(r.transpose(E, 112), J), E) == J, "Full112 signed metric")
    dual = r.transpose(Ei, 112)
    need(dual == r.product(J, r.product(E, Ji)), "Exact inverse-adjoint diagonal conversion")
    need(all(not matrix[p].get(p) for p in range(112)
             for matrix in (E, Ei, dual, modes["E"], modes["inverse_E"])),
         "Both required physical and mode diagonals vanish")
    support = sorted(p for p in range(112) if P[p] != I[p])
    need(support == sorted(special) and all(P[p] == I[p] for p in range(112) if p not in special_set),
         "The physical P changes exactly32 fields")
    need(all(set(P[p]) <= special_set for p in special_set), "P is closed on its32 fields")
    U, L = r.product(Hi, mode_u), r.product(mode_l, H)
    need(r.product(U, L) == difference(R, I), "The physical rank16 reflection factor")
    need(r.rank(difference(E, P), 112) == r.rank(difference(R, I), 112) == 16
         and r.rank(difference(E, I), 112) == 32, "Both complete displacement ranks")
    need(r.product(L, r.product(Ji, r.transpose(L, 112)))
         == diag([4] * 8 + [2] * 8), "The physical centre Gram includes the pair-code normalization")
    need(all((cyclic["ports"][p] & cyclic["ports"][q]).bit_count() % 2 == 0
             for p, row in enumerate(E) for q in row), "Actual response support is orthogonal")
    hw = pair_word(cyclic["pair_codes"])
    need(r.replay(hw)[0] == H, "The paid physical pair code")
    words = {"E": hw + eword + r.inverse_word(hw),
             "R": hw + rword + r.inverse_word(hw)}
    selected_pairs = [pair for pair in cyclic["pair_codes"] if set(pair["ports"]) <= special_set]
    ph = pair_word(selected_pairs)
    words["P"] = ph + pword + r.inverse_word(ph)
    words["inverse_E"] = r.inverse_word(words["E"])
    words["inverse_adjoint_E"] = r.transpose_word(words["inverse_E"])
    jword = [["scale", p, None, str(J[p][p])] for p in special]
    jiword = r.inverse_word(jword)
    words["metric_inverse_adjoint_E"] = jiword + words["E"] + jword
    expected = dict(physical, inverse_adjoint_E=dual, metric_inverse_adjoint_E=dual)
    reports = {}
    for name, word in words.items():
        actual, reports[name] = full_replay(word)
        need(actual == expected[name], "Complete common-frame scalar map " + name)
    need(r.determinant(E) == 1 and r.determinant(R) == r.determinant(P) == 1,
         "Exact full determinants")
    payload = {
        "schema": "actual112-signed-metric-reciprocal-v1", "source_pins": PINS,
        "ports": cyclic["ports"], "blocks": blocks, "special_ports": sorted(special),
        "centre_ports": centres, "large_ports": sorted(cyclic["affected_ports"]),
        "small_ports": sorted(set(range(112)) - set(cyclic["affected_ports"])),
        "pair_codes": cyclic["pair_codes"], "pair_code": r.encoded(H), "pair_code_inverse": r.encoded(Hi),
        "mode": {name: r.encoded(matrix) for name, matrix in modes.items()},
        "physical": {**{name: r.encoded(matrix) for name, matrix in physical.items()},
                     "inverse_adjoint_E": r.encoded(dual)},
        "reflection_U": r.encoded(U), "reflection_L": r.encoded(L),
        "scalar_words": words, "metric_scale_word": jword,
        "metric_inverse_scale_word": jiword,
        "scope": "Exact112 response and common-frame scalar words. Native access and a complete caller require separate proofs.",
    }
    reports["summary"] = {
        "rank_E_minus_I": 32, "rank_E_minus_P": 16, "special_physical_fields": 32,
        "physical_metric_counts": {str(k): v for k, v in Counter(row[p] for p, row in enumerate(J)).items()},
        "metric_conversion_extra_scalar": r.price(jword) + r.price(jiword),
        "odd_divisions": 0, "nonzero_E": sum(map(len, E)), "nonzero_inverse_E": sum(map(len, Ei)),
        "nonzero_P": sum(map(len, P)), "determinant_E": "1",
    }
    return payload, reports


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    payload, reports = make_model()
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    (args.out / "RESPONSE.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    checks = {"status": "PASS_SIGNED_METRIC_ACTUAL112", "source_pins": PINS,
              "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
              "payload_decompressed_sha256": sha256(raw).hexdigest(), "reports": reports}
    (args.out / "CHECKS.json").write_text(json.dumps(checks, sort_keys=True, indent=2) + "\n")
    print(json.dumps(checks, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
