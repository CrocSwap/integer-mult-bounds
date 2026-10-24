#!/usr/bin/env python3
"""Check the route response and capture words from exact input columns."""

import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import gzip
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
SOURCE = LANES / "new-core-transfer-20261017/low-displacement-20261020"
PINS = {
    "route32/FREEZE.json": "28354cf747adc5c2a10393f02035a936e0e0fa3f666717b419f4eaaeed1814af",
    "route32/ROUTE32.md": "ae02183f0b8e83baab893d9c9db915abe476bf9704edf23e593eef796af3fc28",
    "route32/emit_model.py": "6e93a21f04305c5061c9979acaba3588e3dfbb229471dd9bb780486768d15711",
    "route32/model-normal/ROUTE32-MODEL.json": "85d44223697700a916e4cffeb334c8f82179f6535f7b0db64a37eddf37bedf52",
    "route32/model-normal/CHECKS.json": "69ee6905c99ab4d93f48d828c378f6c902d5e8a9844df68acbc8971158d76502",
    "run-normal/RESPONSE-PROGRAM.json": "5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c",
}
INHERITED = {
    "independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json":
        "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585",
    "controller-followthrough-20261017/matching-geometry-20261018/GEOMETRY.json":
        "21e14a24dbe8776038e4deea3181509d23c43fa9314776c4c14c90a5180573fd",
    "independent-review-20261017/rank-thirty-review-20261020/FREEZE.json":
        "15c54c0f0d0f33bdcf420a4c7610d55fff6104fe22d2c4ade8ae9255a3ff8189",
}
OLD_PIN = "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4"


def need(test, label):
    if not test:
        raise ValueError(label)


def sparse(rows):
    return [{int(j): F(c) for j, c in row.items() if F(c)} for row in rows]


def unit(n, j):
    return [F(i == j) for i in range(n)]


def apply(rows, x):
    return [sum((c * x[j] for j, c in row.items()), F(0)) for row in rows]


def rows_from_columns(columns):
    return [{j: c for j, c in enumerate(row) if c} for row in zip(*columns)]


def eliminate(rows, width):
    a = [dict(row) for row in rows]
    count, determinant = 0, F(1)
    for column in range(width):
        found = next((i for i in range(count, len(a)) if a[i].get(column)), None)
        if found is None:
            continue
        if found != count:
            a[found], a[count] = a[count], a[found]
            determinant = -determinant
        pivot = a[count][column]
        determinant *= pivot
        for i in range(count + 1, len(a)):
            factor = a[i].get(column, F(0)) / pivot
            if factor:
                for j, coefficient in a[count].items():
                    value = a[i].get(j, F(0)) - factor * coefficient
                    if value:
                        a[i][j] = value
                    else:
                        a[i].pop(j, None)
        count += 1
        if count == len(a):
            break
    return count, determinant if count == width == len(a) else None


def binary_span(values):
    out = {0}
    for v in values:
        out |= {x ^ v for x in out}
    return out


def add(row, key, value):
    value += row.get(key, F(0))
    if value:
        row[key] = value
    else:
        row.pop(key, None)


def reverse_output(word, output):
    row = {(output, 0): F(1)}
    for kind, target, origin, text in reversed(word):
        c = F(text)
        terms = [(key, value) for key, value in row.items() if key[0] == target]
        if kind == "add":
            for (_, mask), value in terms:
                add(row, (origin, mask), c * value)
        elif kind == "scale":
            for key, value in terms:
                add(row, key, (c - 1) * value)
        else:
            need(kind == "translate" and c.denominator == 1, "Translation type")
            for key, _ in terms:
                del row[key]
            for (_, mask), value in terms:
                add(row, (target, mask ^ int(c)), value)
    return row


def inverse_word(word):
    return [[kind, target, origin,
             str(-F(text) if kind == "add" else 1 / F(text) if kind == "scale" else F(text))]
            for kind, target, origin, text in reversed(word)]


def word_invoice(word, routes):
    price, maps = 0, 0
    for kind, target, origin, text in word:
        need(isinstance(target, int) and 0 <= target < 112, "Data field target")
        c = F(text)
        if kind == "translate":
            need(origin is None and c.denominator == 1 and 0 <= c < 512, "Translation label")
            maps += 1
            continue
        a, b = abs(c.numerator), c.denominator
        need(c and b & (b - 1) == 0, "Dyadic nonzero coefficient")
        if kind == "add":
            need(isinstance(origin, int) and 0 <= origin < 112 and origin != target,
                 "Data field source")
            need(routes[origin] == routes[target], "Every scalar meeting preserves route")
            price += 2 * (1 + a.bit_length() + a.bit_count() + b.bit_length())
        else:
            need(kind == "scale" and origin is None and a & (a - 1) == 0, "Dyadic unit scale")
            price += 2 * (abs(a.bit_length() - b.bit_length()) + int(c < 0))
    return {"scalar_units": price, "translation_maps": maps, "native_children": 0,
            "owned_fields": 0}


def prefix_bounds(word):
    rows = [{j: F(1)} for j in range(112)]
    norm, height = F(1), 0
    for kind, target, origin, text in word:
        c = F(text)
        if kind == "scale":
            rows[target] = {j: value * c for j, value in rows[target].items()}
        else:
            need(kind == "add", "Scalar prefix type")
            for j, value in rows[origin].items():
                add(rows[target], j, c * value)
        norm = max(norm, sum(map(abs, rows[target].values()), F(0)))
        for value in rows[target].values():
            b = value.denominator
            need(b & (b - 1) == 0, "Dyadic prefix")
            height = max(height, b.bit_length() - 1)
    return {"maximum_row_one_norm": str(norm), "binary_height": height}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    for name, pin in PINS.items():
        need(sha256((SOURCE / name).read_bytes()).hexdigest() == pin, "Producer pin " + name)
    for name, pin in INHERITED.items():
        need(sha256((LANES / name).read_bytes()).hexdigest() == pin, "Source pin " + name)
    raw = gzip.decompress((SOURCE / "odd16-normal-v2/EXTENSION-PROGRAM.json.gz").read_bytes())
    need(sha256(raw).hexdigest() == OLD_PIN, "Rank-sixteen source pin")
    old = json.loads(raw)["model"]
    model = json.loads((SOURCE / "route32/model-normal/ROUTE32-MODEL.json").read_text())
    cyclic = json.loads((LANES / next(k for k in INHERITED if k.endswith("CYCLIC-FLAGS.json"))).read_text())
    geometry = json.loads((LANES / next(k for k in INHERITED if k.endswith("GEOMETRY.json"))).read_text())
    rank30 = json.loads((SOURCE / "run-normal/RESPONSE-PROGRAM.json").read_text())
    q = cyclic["ports"]
    need(q == model["ports"] == old["ports"] == geometry["q_labels"], "Actual q labels")
    root = binary_span([30, 45, 75, 384])
    need(sorted(root) == model["root_space"] == geometry["common_even_isotropic_space"],
         "Actual root space")
    routes = [min(r for r in root if (r & v).bit_count() % 2) for v in q]
    need(routes == model["port_routes"] and Counter(routes) == {30: 64, 45: 32, 75: 16},
         "Actual route labels")
    need(model["selected_ports"] == [] and model["ordinary_ports"] == list(range(112)),
         "Empty selection")

    def pair(x, inverse=False):
        y = list(x)
        for record in cyclic["pair_codes"]:
            ports, h = record["ports"], record["matrix"]
            need(routes[ports[0]] == routes[ports[1]], "Pair route")
            for i, p in enumerate(ports):
                y[p] = sum((F(h[j][i], 2) if inverse else F(h[i][j])) * x[ports[j]]
                           for j in range(2))
        return y

    groups = []
    for vertex, carriers in enumerate(cyclic["cyclic_carriers"]):
        selected = [p for p in carriers if set(map(int, cyclic["mode_rows"][str(p)]))
                    & set(old["selected_ports"])]
        need(len(selected) == 2, "Original selected modes")
        ports = selected + [p for p in carriers if p not in selected]
        signs = [1, (-1) ** vertex, 1, 1, 1, 1]
        for route in sorted({routes[p] for p in ports}):
            group = [(p, d) for p, d in zip(ports, signs) if routes[p] == route]
            groups.append(([p for p, _ in group], [d for _, d in group], route, "large"))
    for clique in old["small_cliques"]:
        need(len(clique) == 8, "Original small clique size")
        for route in sorted({routes[p] for p in clique}):
            ports = [p for p in clique if routes[p] == route]
            groups.append((ports, [1] * len(ports), route, "small"))
    need(sorted(p for ps, _, _, _ in groups for p in ps) == list(range(112)), "Mode partition")
    need(Counter((kind, len(ps)) for ps, _, _, kind in groups)
         == {("large", 4): 8, ("large", 2): 8, ("small", 4): 16}, "Group counts")
    relative = Counter()
    inside = 0
    for (ps, signs, route, kind), record in zip(groups, model["groups"]):
        need((ps, signs, route, kind) == (record["ports"], record["signs"],
                                       record["route"], record["kind"]), "Actual group binding")
        need(record["pivot"] == ps[0] and record["centre_multiplier"] == 1 - len(ps),
             "Pivot placement")
        span = binary_span([q[p] ^ q[ps[0]] for p in ps])
        need(binary_span(record["relative_q_basis"]) == span, "Relative q space")
        dim = len(span).bit_length() - 1
        relative[dim] += 1
        inside += span <= root
        need(record["relative_q_rank"] == dim
             and record["relative_q_in_common_root"] == (span <= root), "Relative q claims")
        if kind == "small":
            need(all((q[p] & q[t]).bit_count() % 2 == (p == t) for p in ps for t in ps),
                 "Actual small orthonormal clique")
    need(relative == {1: 8, 3: 24} and inside == 8, "Root membership scope")

    def mode_action(x, inverse=False):
        y = list(x)
        for ps, signs, _, _ in groups:
            total = sum(d * x[p] for p, d in zip(ps, signs))
            if inverse:
                total /= len(ps) - 1
            for p, d in zip(ps, signs):
                y[p] -= d * total
        return y

    def response(x, inverse=False):
        return pair(mode_action(pair(x), inverse), True)

    e, ei = sparse(model["response"]), sparse(model["response_inverse"])
    u, v = sparse(model["correction_U"]), sparse(model["correction_V"])
    need(len(u) == 112 and len(v) == 32, "Correction dimensions")
    for j in range(112):
        x = unit(112, j)
        a, b = response(x), response(x, True)
        need(apply(e, x) == a and apply(ei, x) == b, "Independent response column")
        need(response(a, True) == response(b) == x, "Both response inverse orders")
        need(apply(u, apply(v, x)) == [a_i - x_i for a_i, x_i in zip(a, x)], "UV correction")
        need(apply(sparse(model["mode_response"]), x) == mode_action(x), "Mode response")
        need(apply(sparse(model["mode_inverse"]), x) == mode_action(x, True), "Mode inverse")
    need(eliminate(u, 32)[0] == eliminate(v, 112)[0] == 32, "Rank32 factors")
    need(eliminate(e, 112)[1] == 3 ** 24 == int(model["full_determinant"]), "Full determinant")
    need(all(not row.get(p) for p, row in enumerate(e)), "Physical zero diagonal")
    need(all(e[p].get(t, F(0)) == e[t].get(p, F(0)) for p in range(112) for t in range(112)),
         "Physical response symmetry")
    need(all(routes[p] == routes[t] for p, row in enumerate(e) for t in row), "Response route")
    old_selected = old["selected_ports"]
    need(all(not e[p].get(t) for p in old_selected for t in old_selected), "Old selected block is zero")
    need(sparse(model["old_selected_block"]) == [{} for _ in range(8)]
         and model["old_selected_determinant"] == "0", "Old selected report")
    need(set(c.denominator for row in ei for c in row.values()) <= {1, 2, 3, 6},
         "Only odd inverse denominator three")
    diagonal = [F(1)] * 112
    for ps, _, _, _ in groups:
        diagonal[ps[0]] = 1 - len(ps)
    need(sparse(model["diagonal_response"]) == [{p: c} for p, c in enumerate(diagonal)],
         "Actual diagonal response")

    def code_formula(x, reflection=False):
        z = pair(x)
        result = list(z)
        for ps, d, _, _ in groups:
            p = ps[0]
            if reflection and len(ps) == 4:
                s = [-d[0]] + d[1:]
                total = sum(s_i * z[t] for t, s_i in zip(ps, s)) / 2
                for t, s_i in zip(ps, s):
                    result[t] = z[t] - s_i * total
            else:
                result[p] = sum(d_i * z[t] for t, d_i in zip(ps, d))
                for t, d_i in zip(ps[1:], d[1:]):
                    result[t] = d_i * z[t] - d[0] * z[p]
        return result

    receipts = {}
    for name, code in model["codes"].items():
        word, inverse, entry = code["word"], code["inverse_word"], code["entry_word"]
        need(inverse == inverse_word(word), "Literal scalar inverse " + name)
        need(entry[:112] == [["translate", p, None, str(q[p])] for p in range(112)]
             and entry[112:] == word, "Ordered entry code " + name)
        expected = rows_from_columns([code_formula(unit(112, j), name == "reflection") for j in range(112)])
        need(expected == sparse(code["code"]), "Formula code " + name)
        literal = [{p: c for (p, mask), c in reverse_output(word, i).items() if mask == 0}
                   for i in range(112)]
        need(literal == expected, "Independent reverse scalar outputs " + name)
        inverse_rows = [{p: c for (p, mask), c in reverse_output(inverse, i).items() if mask == 0}
                        for i in range(112)]
        need(inverse_rows == sparse(code["inverse_code"]), "Independent reverse inverse outputs")
        for j in range(112):
            x = unit(112, j)
            need(apply(expected, apply(e, apply(inverse_rows, x))) == [diagonal[i] * x[i] for i in range(112)],
                 "Conjugated centre diagonal")
        for order in (word + inverse, inverse + word):
            need(all(reverse_output(order, i) == {(i, 0): 1} for i in range(640)),
                 "All640 literal inverse outputs")
        for i in range(640):
            want = {(p, q[p]): c for p, c in expected[i].items()} if i < 112 else {(i, 0): F(1)}
            need(reverse_output(entry, i) == want, "All640 ordered entry outputs")
            need(reverse_output(entry + inverse_word(entry), i) == {(i, 0): 1},
                 "All640 spatial inverse outputs")
        need(any(reverse_output(word + entry[:112], i) != reverse_output(entry, i) for i in range(112)),
             "Reject free Q-square commutation")
        mutation = list(word)
        mutation.pop(next(i for i, event in enumerate(word) if event[0] == "add"))
        need(any(reverse_output(mutation, i) != reverse_output(word, i) for i in range(112)),
             "Reject omitted scalar transfer")
        invoice, inverse_invoice = word_invoice(word, routes), word_invoice(inverse, routes)
        entry_invoice = word_invoice(entry, routes)
        need(invoice["scalar_units"] == inverse_invoice["scalar_units"] == (1870 if name == "pivot" else 2486),
             "Independent scalar invoice")
        need(entry_invoice["translation_maps"] == 112 and entry_invoice["scalar_units"] == invoice["scalar_units"],
             "Entry translation invoice")
        forward_bounds, backward_bounds = prefix_bounds(word), prefix_bounds(inverse)
        need(forward_bounds == {"maximum_row_one_norm": "8", "binary_height": int(name == "reflection")}
             and backward_bounds == {"maximum_row_one_norm": "4", "binary_height": 3 - int(name == "reflection")},
             "Exact prefix bounds")
        receipts[name] = {"events": len(word), "invoice": invoice, "inverse_invoice": inverse_invoice,
                          "entry_invoice": entry_invoice, "prefix": forward_bounds,
                          "inverse_prefix": backward_bounds, "all_output_rows": 640}

    reflection_checks = 0
    for ps, d, _, _ in groups:
        if len(ps) != 4:
            continue
        s = [-d[0]] + d[1:]
        matrix = [{j: F(i == j) - F(s[i] * s[j], 2) for j in range(4)} for i in range(4)]
        need(apply(matrix, d) == [2 * d[0], 0, 0, 0], "Signed reflection query")
        delta = [{j: c - (i == j) for j, c in row.items() if c != (i == j)} for i, row in enumerate(matrix)]
        need(eliminate(delta, 4)[0] == 1, "Reflection displacement rank")
        for j in range(4):
            x = unit(4, j)
            need(apply(matrix, apply(matrix, x)) == x, "Reflection involution")
        reflection_checks += 1

    maxima = rank30["maximal_small_cliques"]
    need(Counter(map(len, maxima)) == {4: 896, 8: 64}, "Reviewed clique list")
    need(all(Counter(routes[p] for p in clique) == {30: 4, 45: 4}
             for clique in maxima if len(clique) == 8), "All64 eight-cliques cross routes")
    need(max(max(Counter(routes[p] for p in clique).values()) for clique in maxima) == 4,
         "Restricted monochromatic clique bound")
    route_columns = {}
    for stage in (1, 2):
        for route in sorted(set(routes)):
            direction = (511 ^ route) ^ (1 << (8 + stage))
            need(direction.bit_count() % 2 == 0, "Even transvection direction")
            columns = [(1 << j) ^ (direction if (direction >> j) & 1 else 0) for j in range(11)]
            need(all((a & b).bit_count() % 2 == (i == j)
                     for i, a in enumerate(columns) for j, b in enumerate(columns)), "Orthogonal route")
            route_columns[f"{stage}:{route}"] = columns
    receipt = {
        "status": "PASS_INDEPENDENT_ROUTE32_RESPONSE_AND_CAPTURE",
        "producer_pins": PINS, "inherited_pins": INHERITED, "rank16_raw_sha256": OLD_PIN,
        "response_columns_per_direction": 112, "response_symmetric": True,
        "correction_rank": 32, "determinant": str(3 ** 24),
        "selection": [], "old_selected_block": "zero",
        "centre_multipliers": {"-3": 24, "-1": 8, "1": 80},
        "reflection_blocks": reflection_checks, "code_receipts": receipts,
        "relative_q_rank_counts": dict(sorted(relative.items())), "blocks_inside_root": inside,
        "route_classes": dict(sorted(Counter(routes).items())), "actual_kappa_columns": route_columns,
        "restricted_monochromatic_maximum_clique": 4,
        "scope": "Exact response, scalar capture words, and route binding. Native phases and a complete caller have separate reviews.",
    }
    data = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
    (args.out / "CHECKS.json").write_bytes(data)
    print(receipt["status"])
    print("receipt_sha256=" + sha256(data).hexdigest())


if __name__ == "__main__":
    main()
