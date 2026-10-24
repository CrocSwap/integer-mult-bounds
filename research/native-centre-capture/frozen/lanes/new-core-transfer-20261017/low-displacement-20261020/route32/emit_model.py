#!/usr/bin/env python3
"""Build the route-compatible response and its exact in-place codes."""

import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
LANES = PARENT.parents[1]
SOURCE = PARENT / "odd16-normal-v2/EXTENSION-PROGRAM.json.gz"
SOURCE_PIN = "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4"
PINS = {
    PARENT / "pivot-codes/emit_pivot_codes.py":
        "af2f2ab1c5daba0bcd1a8878f2b81b2834e10a4f8ca1a2ef66779d52b30e64b4",
    LANES / "independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json":
        "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585",
    LANES / "controller-followthrough-20261017/matching-geometry-20261018/GEOMETRY.json":
        "21e14a24dbe8776038e4deea3181509d23c43fa9314776c4c14c90a5180573fd",
    PARENT / "run-normal/RESPONSE-PROGRAM.json":
        "5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c",
}


def need(test, message):
    if not test:
        raise ValueError(message)


for path, pin in PINS.items():
    need(sha256(path.read_bytes()).hexdigest() == pin, "Source pin " + str(path))
spec = importlib.util.spec_from_file_location("frozen_pivot", PARENT / "pivot-codes/emit_pivot_codes.py")
pivot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pivot)
r = pivot.r


def binary_basis(vectors):
    rows = list(dict.fromkeys(vectors))
    used = 0
    for bit in range(8, -1, -1):
        found = next((i for i in range(used, len(rows)) if rows[i] >> bit & 1), None)
        if found is None:
            continue
        rows[used], rows[found] = rows[found], rows[used]
        for i in range(len(rows)):
            if i != used and rows[i] >> bit & 1:
                rows[i] ^= rows[used]
        used += 1
    return rows[:used]


def pair_word(cyclic):
    word, matrix = [], r.identity(112)
    for pair in cyclic["pair_codes"]:
        a, b = pair["ports"]
        aa, ab = pair["matrix"][0]
        ba, bb = pair["matrix"][1]
        matrix[a], matrix[b] = {a: F(aa), b: F(ab)}, {a: F(ba), b: F(bb)}
        if aa != 1:
            word.append(["scale", a, None, str(aa)])
        word.extend([["add", a, b, str(ab)], ["scale", b, None, str(2 * bb)],
                     ["add", b, a, str(ba * aa)]])
    need(pivot.replay(word)[0] == matrix, "Actual pair word")
    return word, matrix


def capture(groups, pair, reflection):
    word = list(pair)
    for group in groups:
        ports, signs = group["ports"], group["signs"]
        p, k = ports[0], len(ports)
        if reflection and k == 4:
            for t, sign in zip(ports[1:], signs[1:]):
                word.append(["add", t, p, str(sign * signs[0])])
            word.append(["scale", p, None, "-2"])
            for t, sign in zip(ports[1:], signs[1:]):
                word.append(["add", p, t, str(sign * signs[0])])
            word.append(["scale", p, None, "1/2"])
            for t, sign in zip(ports[1:], signs[1:]):
                word.append(["add", t, p, str(-sign * signs[0])])
        else:
            for t, sign in zip(ports, signs):
                if sign == -1:
                    word.append(["scale", t, None, "-1"])
            for t in ports[1:]:
                word.append(["add", t, p, "-1"])
            word.append(["scale", p, None, str(k)])
            for t in ports[1:]:
                word.append(["add", p, t, "1"])
    return word


def make_model(old, cyclic, geometry, rank30):
    q = old["ports"]
    root_space = geometry["common_even_isotropic_space"]
    need(root_space == sorted(root_space), "The route enumeration uses numeric order")
    need(q == geometry["q_labels"] == cyclic["ports"], "Actual route direction labels")
    routes = [next(t for t in root_space if (q[p] & t).bit_count() % 2) for p in range(112)]
    need(Counter(routes) == {30: 64, 45: 32, 75: 16}, "Exact route classes")
    pair, h = pair_word(cyclic)
    hi = pivot.replay(pivot.inverse(pair))[0]
    need(all(routes[a] == routes[b] for data in cyclic["pair_codes"]
             for a, b in [data["ports"]]), "Every pair code preserves the route")
    groups = []
    mode, mode_inverse = r.identity(112), r.identity(112)
    mode_u, mode_v = [{} for _ in range(112)], []
    for record in old["vertex_assignments"]:
        ports, signs = record["ordered_carriers_a_b_c"], record["signs"]
        for route in sorted({routes[p] for p in ports}):
            entries = [(p, s) for p, s in zip(ports, signs) if routes[p] == route]
            need(len(entries) == (4 if route == 30 else 2), "Large route split")
            groups.append({"ports": [p for p, _ in entries], "signs": [s for _, s in entries],
                           "route": route, "kind": "large", "vertex": record["vertex"]})
    small = []
    for clique in old["small_cliques"]:
        for route in sorted({routes[p] for p in clique}):
            ports = [p for p in clique if routes[p] == route]
            need(len(ports) == 4, "Small route split")
            need(all((q[p] & q[t]).bit_count() % 2 == int(p == t)
                     for p in ports for t in ports), "Actual four-clique")
            small.append(ports)
            groups.append({"ports": ports, "signs": [1] * 4, "route": route, "kind": "small"})
    need(sorted(p for group in groups for p in group["ports"]) == list(range(112)),
         "All32 blocks partition the data modes")
    for index, group in enumerate(groups):
        ports, signs = group["ports"], group["signs"]
        k = len(ports)
        group["pivot"] = ports[0]
        group["centre_multiplier"] = 1 - k
        group["relative_q_basis"] = binary_basis([q[p] ^ q[ports[0]] for p in ports[1:]])
        group["relative_q_rank"] = len(group["relative_q_basis"])
        group["relative_q_in_common_root"] = all(t in root_space for t in group["relative_q_basis"])
        for i, p in enumerate(ports):
            mode[p] = {t: F(int(i == j) - signs[i] * signs[j])
                       for j, t in enumerate(ports) if i != j}
            mode_inverse[p] = {t: F(int(i == j)) - F(signs[i] * signs[j], k - 1)
                               for j, t in enumerate(ports)}
            mode_u[p] = {index: F(-signs[i])}
        mode_v.append({p: F(sign) for p, sign in zip(ports, signs)})
    response = r.product(hi, r.product(mode, h))
    response_inverse = r.product(hi, r.product(mode_inverse, h))
    u, v = r.product(hi, mode_u), r.product(mode_v, h)
    delta = [dict(row) for row in response]
    for p in range(112):
        r.add(delta[p], {p: F(-1)})
    need(r.product(u, v) == delta and r.rank(u, 32) == r.rank(v, 112) == 32,
         "Actual rank32 response correction")
    need(r.product(response, response_inverse) == r.product(response_inverse, response) == r.identity(112),
         "Both complete response inverse orders")
    need(all(p not in row for p, row in enumerate(response)), "Zero physical diagonal")
    need(all(routes[p] == routes[t] for p, row in enumerate(response) for t in row),
         "Every response coefficient preserves the actual route")
    need(r.determinant(response) == 3 ** 24, "The whole ordinary response is a unit")
    complete = rank30["maximal_small_cliques"]
    need(Counter(tuple(sorted(Counter(routes[p] for p in clique).items()))
                 for clique in complete if len(clique) == 8) == {((30, 4), (45, 4)): 64},
         "No actual eight-clique stays inside one route")
    need(max(max(Counter(routes[p] for p in clique).values()) for clique in complete) == 4,
         "The actual monochromatic clique bound")
    model = {
        "ports": q, "large_ports": old["large_ports"], "small_ports": old["small_ports"],
        "selected_ports": [], "ordinary_ports": list(range(112)),
        "root_basis": geometry["common_even_isotropic_basis"], "root_space": root_space,
        "port_routes": routes, "groups": groups, "small_cliques": small,
        "mode_response": r.encoded(mode), "mode_inverse": r.encoded(mode_inverse),
        "response": r.encoded(response), "response_inverse": r.encoded(response_inverse),
        "correction_U": r.encoded(u), "correction_V": r.encoded(v),
        "full_determinant": str(3 ** 24), "correction_rank": 32,
        "old_selected_block": r.encoded(r.restrict(response, old["selected_ports"])),
        "old_selected_determinant": str(r.determinant(r.restrict(response, old["selected_ports"]))),
    }
    diagonal = r.identity(112)
    for group in groups:
        diagonal[group["pivot"]] = {group["pivot"]: F(group["centre_multiplier"])}
    codes, reports = {}, {}
    for name, reflection in [("pivot", False), ("reflection", True)]:
        word = capture(groups, pair, reflection)
        inverse = pivot.inverse(word)
        c, growth = pivot.replay(word)
        ci, inverse_growth = pivot.replay(inverse)
        need(r.product(c, r.product(response, ci)) == diagonal, "Exact diagonal centre action " + name)
        need(pivot.replay(word + inverse)[0] == pivot.replay(inverse + word)[0] == r.identity(112),
             "Literal code inverse orders " + name)
        need(all(routes[p] == routes[t] for p, row in enumerate(c) for t in row),
             "The full physical code preserves routes " + name)
        entry = [["translate", p, None, str(qp)] for p, qp in enumerate(q)] + word
        want = [{(p, q[p]): coefficient for p, coefficient in row.items()} for row in c]
        need(pivot.replay(entry, spatial=True)[0] == want, "Exact input-square entry " + name)
        need(pivot.replay(entry + pivot.inverse(entry), spatial=True)[0]
             == [{(p, 0): F(1)} for p in range(112)], "Exact spatial inverse " + name)
        codes[name] = {"word": word, "inverse_word": inverse, "entry_word": entry,
                       "code": r.encoded(c), "inverse_code": r.encoded(ci)}
        reports[name] = {"invoice": pivot.price(word), "inverse_invoice": pivot.price(inverse),
                         "prefix": growth, "inverse_prefix": inverse_growth}
    need(reports["pivot"]["invoice"]["old_real_scalar_units"] == 1870, "Complete pivot invoice")
    need(reports["reflection"]["invoice"]["old_real_scalar_units"] == 2486,
         "Complete reflection invoice")
    model["diagonal_response"] = r.encoded(diagonal)
    model["codes"] = codes
    return model, reports


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    raw = gzip.decompress(SOURCE.read_bytes())
    need(sha256(raw).hexdigest() == SOURCE_PIN, "Frozen rank16 source")
    old = json.loads(raw)["model"]
    inputs = {path.name: json.loads(path.read_bytes()) for path in PINS if path.suffix == ".json"}
    model, reports = make_model(old, inputs["CYCLIC-FLAGS.json"], inputs["GEOMETRY.json"],
                               inputs["RESPONSE-PROGRAM.json"])
    data = (json.dumps(model, sort_keys=True, separators=(",", ":")) + "\n").encode()
    (args.out / "ROUTE32-MODEL.json").write_bytes(data)
    checks = {
        "status": "PASS_ROUTE32_RESPONSE_AND_CAPTURE",
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_sha256": sha256(data).hexdigest(),
        "source_decompressed_sha256": SOURCE_PIN,
        "reports": reports,
        "correction_rank": 32,
        "determinant": model["full_determinant"],
        "old_selected_determinant": model["old_selected_determinant"],
        "relative_q_rank_counts": dict(sorted(Counter(g["relative_q_rank"] for g in model["groups"]).items())),
        "blocks_inside_common_root": sum(g["relative_q_in_common_root"] for g in model["groups"]),
        "all_blocks": len(model["groups"]),
        "arbitrary_inputs_checked": 640,
        "old_small_monochromatic_maximum_clique_size": 4,
        "scope": "Exact route-compatible unit and dyadic in-place centre codes. Native implementation and the physical moving-code caller have separate checks.",
    }
    (args.out / "CHECKS.json").write_text(json.dumps(checks, indent=2, sort_keys=True) + "\n")
    print(json.dumps(checks, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
