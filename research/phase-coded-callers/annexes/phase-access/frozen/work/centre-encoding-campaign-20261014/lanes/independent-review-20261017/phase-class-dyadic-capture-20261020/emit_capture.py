#!/usr/bin/env python3
"""Build a dyadic capture with one active field in each group class."""

import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
OLD = LANES / "new-core-transfer-20261017/low-displacement-20261020/odd16-normal-v2/EXTENSION-PROGRAM.json.gz"
OLD_PIN = "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4"
PINS = {
    "independent-review-20261017/route32-capture-review-20261020/check_review.py":
        "c419f63a47d655c4d2a789cf52f0a00d5186cb7728cdd58aac73ceb21845aa89",
    "independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json":
        "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585",
    "controller-followthrough-20261017/matching-geometry-20261018/GEOMETRY.json":
        "21e14a24dbe8776038e4deea3181509d23c43fa9314776c4c14c90a5180573fd",
    "independent-review-20261017/common-gauge-rank-20261020/FREEZE.json":
        "9523bfe7aaa2a1430d146727a328b03cf90f0ff4965dfdc2bc2640a58d92de57",
}
W_SOURCE = LANES / "controller-followthrough-20261017/shared-root-eight-20261020/v2-normal/PROGRAM.json.gz"
W_PIN = "71dec1d8e33625e301c8bfde37d8c08b0019124e1525500555fcc704530bf4a6"


def need(test, label):
    if not test:
        raise ValueError(label)


def encoded(rows):
    return [{str(j): str(c) for j, c in sorted(row.items()) if c} for row in rows]


def price(word):
    total = 0
    for kind, target, origin, text in word:
        c = F(text)
        a, b = abs(c.numerator), c.denominator
        need(c and b & (b - 1) == 0, "Dyadic nonzero gate")
        need(0 <= target < 224, "Actual target")
        if kind == "add":
            need(isinstance(origin, int) and 0 <= origin < 224 and origin != target,
                 "Distinct actual source")
            total += 2 * (1 + a.bit_length() + a.bit_count() + b.bit_length())
        else:
            need(kind == "scale" and origin is None and a & (a - 1) == 0,
                 "Power-of-two unit scale")
            total += 2 * (abs(a.bit_length() - b.bit_length()) + int(c < 0))
    return total


def pair_word(ports, matrix):
    p, q = ports
    a, b = matrix[0]
    c, d = matrix[1]
    need(d == -a * b * c and all(abs(v) == 1 for row in matrix for v in row),
         "Signed pair factor")
    word = [] if a == 1 else [["scale", p, None, str(a)]]
    return word + [["add", p, q, str(b)], ["scale", q, None, str(2 * d)],
                   ["add", q, p, str(c * a)]]


def rank_one_word(ports, u, v):
    p = ports[0]
    need(1 + sum(a * b for a, b in zip(u, v)) == -1, "Rank-one involution")
    word = [["add", port, p, str(-a / u[0])] for port, a in zip(ports[1:], u[1:])]
    word += [["scale", p, None, "-1"]]
    word += [["add", p, port, str(u[0] * b)] for port, b in zip(ports[1:], v[1:])]
    word += [["add", port, p, str(a / u[0])] for port, a in zip(ports[1:], u[1:])]
    return word


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    for path, pin in PINS.items():
        need(sha256((LANES / path).read_bytes()).hexdigest() == pin, "Source pin " + path)
    helper_path = LANES / next(p for p in PINS if p.endswith("check_review.py"))
    spec = importlib.util.spec_from_file_location("review_algebra", helper_path)
    r = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(r)
    old_raw = gzip.decompress(OLD.read_bytes())
    need(sha256(old_raw).hexdigest() == OLD_PIN, "Rank16 source")
    old = json.loads(old_raw)["model"]
    w_raw = gzip.decompress(W_SOURCE.read_bytes())
    need(sha256(w_raw).hexdigest() == W_PIN, "Common-root frame")
    w_data = json.loads(w_raw)
    cyclic = json.loads((LANES / next(p for p in PINS if p.endswith("CYCLIC-FLAGS.json"))).read_text())
    geometry = json.loads((LANES / next(p for p in PINS if p.endswith("GEOMETRY.json"))).read_text())
    q = old["ports"]
    need(q == cyclic["ports"] == geometry["q_labels"], "Actual source directions")
    root = set(geometry["common_even_isotropic_space"])
    need(root == r.binary_span([30, 45, 75, 384]) and len(root) == 16, "Root space")
    classes = [min(v ^ z for z in root) for v in q]
    need(Counter(Counter(classes).values()) == {8: 14}, "Fourteen actual classes")
    anchors = {c: min(q[p] for p in range(112) if classes[p] == c) for c in set(classes)}
    need(all(q[p] ^ anchors[classes[p]] in root and q[p].bit_count() % 2
             for p in range(112)), "Monomial ratio directions and rank-one anchors")
    h_word = []
    for pair in cyclic["pair_codes"]:
        h_word += pair_word(pair["ports"], pair["matrix"])
        need(len({classes[p] for p in pair["ports"]}) == 1, "H preserves global classes")

    def h_apply(x, inverse=False):
        y = list(x)
        for item in cyclic["pair_codes"]:
            ps, h = item["ports"], item["matrix"]
            for i, p in enumerate(ps):
                y[p] = sum((F(h[j][i], 2) if inverse else F(h[i][j])) * x[ps[j]]
                           for j in range(2))
        return y

    source_groups = [(item["ordered_carriers_a_b_c"], item["signs"], "large")
                     for item in old["vertex_assignments"]]
    source_groups += [(ps, [1] * len(ps), "small") for ps in old["small_cliques"]]
    groups, t_word, core_word, active = [], [], [], []
    for index, (ps, signs, kind) in enumerate(source_groups):
        k = len(ps)
        need(k == (6 if kind == "large" else 8), "Group size")
        sign = dict(zip(ps, signs))
        pairs = [[p for p in ps if classes[p] == c] for c in sorted({classes[p] for p in ps})]
        need(all(len(pair) == 2 for pair in pairs), "Two fields per group class")
        for pair in pairs:
            a, b = [sign[p] for p in pair]
            t_word += pair_word(pair, [[a, b], [-a, b]])
        selected = pairs[0]
        a, b = {p: F(0) for p in ps}, {p: F(0) for p in ps}
        if k == 6:
            a[selected[0]] = 2 * sign[selected[0]]
            b[selected[0]] = 3 * sign[selected[0]]
            b[selected[1]] = -sign[selected[1]]
            u = {p: a[p] - sign[p] for p in ps}
            v = {p: (F(sign[p]) - b[p]) / 4 for p in ps}
            active_ports = [selected[1]] + [pair[0] for pair in pairs[1:]]
            small_u = list(map(F, [-2, -2, -2]))
            small_v = [F(1, 2), F(1, 4), F(1, 4)]
        else:
            for p in selected:
                a[p] = 2 * sign[p]
                b[p] = 2 * sign[p]
            u = {p: (sign[p] if p in selected else -sign[p]) for p in ps}
            v = {p: -F(u[p], 4) for p in ps}
            active_ports = [pair[0] for pair in pairs]
            small_u = list(map(F, [1, -1, -1, -1]))
            small_v = [F(-1, 2)] + [F(1, 2)] * 3
        need(sum(v[p] * u[p] for p in ps) == -2, "Actual involution")
        need(sum(v[p] * sign[p] for p in ps) == 1, "Actual centre input")
        need(all(sign[p] + u[p] == a[p] for p in ps), "Actual centre image")
        need(sum(b[p] * a[p] for p in ps) == k, "Correct eigenvalue")
        need(all(b[p] + sum(b[t] * u[t] for t in ps) * v[p] == sign[p] for p in ps),
             "Actual centre output covector")
        local = rank_one_word(active_ports, small_u, small_v)
        need(price(local) == (54 if k == 6 else 80), "Reduced scalar cost")
        core_word += local
        active += active_ports
        groups.append({"index": index, "kind": kind, "ports": ps, "signs": signs,
                       "pairs": pairs, "selected_pair": selected,
                       "active_ports": active_ports,
                       "active_selected_type": "negative_signed_difference" if k == 6 else "sum",
                       "u": {str(p): str(u[p]) for p in ps},
                       "v": {str(p): str(v[p]) for p in ps},
                       "a": {str(p): str(a[p]) for p in ps if a[p]},
                       "b": {str(p): str(b[p]) for p in ps if b[p]},
                       "reduced_u": list(map(str, small_u)), "reduced_v": list(map(str, small_v)),
                       "core_word": local})
    need(len(active) == len(set(active)) == 56, "Exactly56 active fields")
    need(Counter(classes[p] for p in active) == {c: 4 for c in set(classes)}, "Four active fields per global class")
    passive = sorted(set(range(112)) - set(active))
    hi_word, ti_word = r.inverse_word(h_word), r.inverse_word(t_word)
    word = h_word + t_word + core_word + ti_word + hi_word
    inverse = r.inverse_word(word)

    def s_apply(x):
        y = list(x)
        for group in groups:
            u, v = {int(p): F(c) for p, c in group["u"].items()}, {int(p): F(c) for p, c in group["v"].items()}
            query = sum(v[p] * x[p] for p in group["ports"])
            for p in group["ports"]:
                y[p] += u[p] * query
        return y

    def capture(x):
        return h_apply(s_apply(h_apply(x)), True)

    def k_apply(x):
        z = h_apply(x)
        y = list(z)
        for group in groups:
            a, b = {int(p): F(c) for p, c in group["a"].items()}, {int(p): F(c) for p, c in group["b"].items()}
            query = sum(c * z[p] for p, c in b.items())
            for p, coefficient in a.items():
                y[p] -= coefficient * query
        return h_apply(y, True)

    c_rows = r.rows_from_columns([capture(r.unit(112, j)) for j in range(112)])
    k_rows = r.rows_from_columns([k_apply(r.unit(112, j)) for j in range(112)])
    e_rows = r.sparse(old["response"])
    need(all(e_rows[p].get(t, F(0)) == e_rows[t].get(p, F(0))
             for p in range(112) for t in range(112)), "Original response symmetry")
    for j in range(112):
        x = r.unit(112, j)
        need(capture(capture(x)) == x, "C involution columns")
        need(capture(r.apply(e_rows, capture(x))) == k_apply(x), "Exact coded response columns")
    need(all(classes[p] == classes[t] for p, row in enumerate(k_rows) for t in row),
         "K is supported in global phase classes")
    delta = [dict(row) for row in c_rows]
    for p, row in enumerate(delta):
        r.add(row, p, F(-1))
    need(r.eliminate(delta, 112)[0] == 16, "Rank16 physical capture displacement")
    need(r.eliminate(c_rows, 112)[1] == 1, "Physical capture determinant")
    for i in range(640):
        expected = {(p, 0): coefficient for p, coefficient in c_rows[i].items()} if i < 112 else {(i, 0): F(1)}
        need(r.reverse_output(word, i) == r.reverse_output(inverse, i) == expected,
             "All640 capture outputs and inverse outputs")
        need(r.reverse_output(word + word, i) == {(i, 0): F(1)}, "All640 involution outputs")
        if i in passive or i >= 112:
            need(r.reverse_output(core_word, i) == {(i, 0): F(1)}, "Passive coordinate identity")
    for i in range(112):
        original = r.reverse_output(h_word, i)
        need(all(classes[p] == classes[i] for p, _ in original), "H literal class support")
        original = r.reverse_output(t_word, i)
        need(all(classes[p] == classes[i] for p, _ in original), "T literal class support")
    selected_differences = {group["selected_pair"][1] for group in groups if group["kind"] == "large"}
    need(len(selected_differences) == 8 and selected_differences <= set(active),
         "All eight selected differences are active")
    mutation = [event for event in core_word if event[1] != min(selected_differences)]
    need(any(r.reverse_output(mutation, i) != r.reverse_output(core_word, i) for i in range(112)),
         "Reject loss of an active selected difference")

    additive = [["add", 112 + p, t, str(coefficient)]
                for p, row in enumerate(k_rows) for t, coefficient in sorted(row.items())]
    subtractive = [["add", p, 112 + t, str(-coefficient)]
                   for p, row in enumerate(k_rows) for t, coefficient in sorted(row.items())]
    for i in range(640):
        forward = {(i, 0): F(1)}
        backward = {(i, 0): F(1)}
        if 112 <= i < 224:
            forward.update({(p, 0): coefficient for p, coefficient in k_rows[i - 112].items()})
        if i < 112:
            backward.update({(112 + p, 0): -coefficient for p, coefficient in k_rows[i].items()})
        need(r.reverse_output(additive, i) == forward and r.reverse_output(subtractive, i) == backward,
             "All640 coded additive maps")
    bills = {name: price(events) for name, events in
             [("H", h_word), ("T", t_word), ("core", core_word), ("capture", word),
              ("inverse", inverse), ("coded_forward", additive), ("coded_backward", subtractive)]}
    need(bills["capture"] == bills["inverse"]
         == 2 * bills["H"] + 2 * bills["T"] + bills["core"], "Complete capture invoice")
    bounds = {"capture": r.prefix_bounds(word), "inverse": r.prefix_bounds(inverse)}
    packet = {
        "schema": "dyadic-phase-class-capture-v1", "ports": q,
        "root_basis": [30, 45, 75, 384], "root_space": sorted(root),
        "phase_classes": classes, "global_anchors": anchors, "W": w_data["W"],
        "groups": groups, "active_ports": active, "passive_ports": passive,
        "H_word": h_word, "T_word": t_word, "reduced_word": core_word,
        "capture_word": word, "inverse_word": inverse,
        "coded_forward_word": additive, "coded_backward_word": subtractive,
        "capture": encoded(c_rows), "coded_response": encoded(k_rows),
        "source_response": old["response"], "source_inverse": old["response_inverse"],
        "invoices": bills, "prefix_bounds": bounds,
        "phase_conjugation_contract": {
            "gauge": "rank4 W_R",
            "active_forward_phase_calls": 56, "active_inverse_phase_calls": 56,
            "native_mass": 112, "alignment_maps": 224,
            "native_side_map_upper_bound": 224,
            "compiled_phase_recipes": False,
            "scope": "Exact ordered factorization. This packet does not emit native phase recipes or establish a routed caller.",
        },
    }
    data = (json.dumps(packet, sort_keys=True, separators=(",", ":")) + "\n").encode()
    (args.out / "CAPTURE-PROGRAM.json").write_bytes(data)
    receipt = {
        "status": "PASS_DYADIC_PHASE_CLASS_CAPTURE", "source_pins": PINS,
        "source_response_raw_sha256": OLD_PIN, "W_source_raw_sha256": W_PIN,
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_sha256": sha256(data).hexdigest(), "invoices": bills,
        "prefix_bounds": bounds, "arbitrary_field_outputs": 640, "unchanged_fields": 528,
        "active_fields": 56, "passive_fields": 56, "physical_capture_displacement_rank": 16,
        "capture_determinant": "1", "capture_inverse": "capture",
        "global_phase_classes": 14, "phase_native_mass_in_W_R": 112,
        "phase_recipes_emitted": False, "odd_divisions_or_multiplications_in_capture": 0,
        "scope": "Actual dyadic scalar capture and class-supported coded additive response. Rank4 carried gauge, compiled phase maps, routing, and recursive closure are separate obligations.",
    }
    raw = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
    (args.out / "CHECKS.json").write_bytes(raw)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
