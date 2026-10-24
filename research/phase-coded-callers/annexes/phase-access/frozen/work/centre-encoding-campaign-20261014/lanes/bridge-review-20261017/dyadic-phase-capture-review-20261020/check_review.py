"""Check the actual dyadic capture without producer imports."""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import lcm
from pathlib import Path
import gzip
import json


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
PRODUCER = LANES / "independent-review-20261017/phase-class-dyadic-capture-20261020"
FREEZE_PIN = "3b7601e537cdd570295cde170a2491de876d7cae7814313b0c4a1f685c199ecd"
PINS = {
    "new-core-transfer-20261017/low-displacement-20261020/odd16-normal-v2/EXTENSION-PROGRAM.json.gz":
        "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4",
    "independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json":
        "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585",
    "controller-followthrough-20261017/matching-geometry-20261018/GEOMETRY.json":
        "21e14a24dbe8776038e4deea3181509d23c43fa9314776c4c14c90a5180573fd",
    "controller-followthrough-20261017/shared-root-eight-20261020/v2-normal/PROGRAM.json.gz":
        "71dec1d8e33625e301c8bfde37d8c08b0019124e1525500555fcc704530bf4a6",
    "coherent-port/isotropic-pair-gauge-20261018/GAUGE-PROGRAMS.json":
        "20f14f021623761160b0ef461904b38f82efdc7dd0c4008271620415bf747701",
    "independent-review-20261017/common-gauge-rank-20261020/FREEZE.json":
        "9523bfe7aaa2a1430d146727a328b03cf90f0ff4965dfdc2bc2640a58d92de57",
}


def need(value, reason):
    if not value:
        raise ValueError(reason)


def read(path, digest):
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == digest, "Source hash: " + path.name)
    return json.loads(raw)


def identity(n):
    return [{i: Q(1)} for i in range(n)]


def sparse(matrix):
    return [{int(j): Q(v) for j, v in row.items() if Q(v)} for row in matrix]


def add(left, right, coefficient=Q(1)):
    answer = dict(left)
    for j, value in right.items():
        answer[j] = answer.get(j, Q(0)) + coefficient * value
        if not answer[j]:
            del answer[j]
    return answer


def multiply(left, right):
    answer = []
    for row in left:
        result = {}
        for j, value in row.items():
            result = add(result, right[j], value)
        answer.append(result)
    return answer


def elimination(matrix):
    rows = [dict(row) for row in matrix]
    rank, determinant = 0, Q(1)
    for j in range(len(rows)):
        pick = next((i for i in range(rank, len(rows)) if rows[i].get(j)), None)
        if pick is None:
            continue
        if pick != rank:
            rows[pick], rows[rank] = rows[rank], rows[pick]
            determinant = -determinant
        pivot = rows[rank][j]
        determinant *= pivot
        rows[rank] = {k: v / pivot for k, v in rows[rank].items()}
        for i in range(rank + 1, len(rows)):
            if rows[i].get(j):
                rows[i] = add(rows[i], rows[rank], -rows[i][j])
        rank += 1
    return rank, determinant if rank == len(rows) else Q(0)


def put_pair(matrix, inverse, ports, block):
    p, t = ports
    a, b = map(Q, block[0])
    c, d = map(Q, block[1])
    determinant = a * d - b * c
    need(determinant != 0, "Pair unit")
    matrix[p], matrix[t] = {p: a, t: b}, {p: c, t: d}
    inverse[p], inverse[t] = {p: d / determinant, t: -b / determinant}, {p: -c / determinant, t: a / determinant}


def replay(word, n=640):
    rows = identity(n)
    norm, height, price = Q(1), 0, 0
    census = Counter()
    for op, target, source, value in word:
        c = Q(value)
        numerator, denominator = abs(c.numerator), c.denominator
        need(c and denominator & (denominator - 1) == 0 and 0 <= target < 224, "Dyadic scalar gate")
        if op == "add":
            need(isinstance(source, int) and 0 <= source < 224 and source != target, "Distinct data source")
            rows[target] = add(rows[target], rows[source], c)
            price += 2 * (1 + numerator.bit_length() + numerator.bit_count() + denominator.bit_length())
        else:
            need(op == "scale" and source is None and numerator & (numerator - 1) == 0, "Dyadic unit scale")
            rows[target] = {j: c * v for j, v in rows[target].items()}
            price += 2 * (abs(numerator.bit_length() - denominator.bit_length()) + int(c < 0))
        norm = max(norm, sum(map(abs, rows[target].values())))
        for value in rows[target].values():
            need(value.denominator & (value.denominator - 1) == 0, "Dyadic prefix coefficient")
            height = max(height, value.denominator.bit_length() - 1)
        census[op + ":" + str(c)] += 1
    return rows, {"price": price, "maximum_row_one_norm": str(norm), "binary_height": height,
                  "events": len(word), "census": dict(sorted(census.items()))}


def inverse_word(word):
    return [[op, target, source, str(-Q(value) if op == "add" else 1 / Q(value))]
            for op, target, source, value in reversed(word)]


def parity(value):
    return value.bit_count() & 1


def span(basis):
    result = {0}
    for v in basis:
        result |= {u ^ v for u in result}
    return result


def binary_rank(vectors):
    pivots = {}
    for v in vectors:
        while v:
            bit = v.bit_length()
            if bit in pivots:
                v ^= pivots[bit]
            else:
                pivots[bit] = v
                break
    return len(pivots)


def act(rows, value):
    return sum(parity(row & value) << i for i, row in enumerate(rows))


def transpose(rows):
    return [sum(((row >> j) & 1) << i for i, row in enumerate(rows)) for j in range(len(rows))]


def binary_inverse(rows):
    n = len(rows)
    left, right = list(rows), [1 << i for i in range(n)]
    for j in range(n):
        p = next(i for i in range(j, n) if left[i] >> j & 1)
        left[j], left[p], right[j], right[p] = left[p], left[j], right[p], right[j]
        for i in range(n):
            if i != j and left[i] >> j & 1:
                left[i] ^= left[j]
                right[i] ^= right[j]
    need(left == [1 << i for i in range(n)], "Invertible binary address map")
    return right


def inverse_circuit(word):
    result = []
    for gate in reversed(word):
        if gate[0] == "P":
            result.append(["P", binary_inverse(gate[1])])
        elif gate[0] == "D":
            result.append(["D", gate[1], [(-a) % 4 for a in gate[2]]])
        else:
            need(gate[0] == "C", "Frame circuit alphabet")
            result.append(["C", gate[1], -gate[2]])
    return result


def binary_pauli(word, x, z):
    for gate in word:
        if gate[0] == "P":
            x, z = act(gate[1], x), act(transpose(binary_inverse(gate[1])), z)
        elif gate[0] == "D":
            need(gate[1] == transpose(gate[1]), "Symmetric diagonal phase form")
            need(all(((row >> i) & 1) == gate[2][i] % 2 for i, row in enumerate(gate[1])),
                 "Diagonal phase parity")
            z ^= act(gate[1], x)
        else:
            need(gate[0] == "C", "Pure line operator")
            if parity(gate[1] & z):
                x ^= gate[1]
    return x, z


def fourier_rank(word):
    return binary_rank([binary_pauli(word, 0, 1 << j)[0] for j in range(9)])


def main():
    freeze = read(PRODUCER / "FREEZE.json", FREEZE_PIN)
    for name, pin in freeze["files"].items():
        need(sha256((PRODUCER / name).read_bytes()).hexdigest() == pin, "Frozen producer file")
    packet = read(PRODUCER / "verified-normal/CAPTURE-PROGRAM.json",
                  freeze["files"]["verified-normal/CAPTURE-PROGRAM.json"])
    receipt = read(PRODUCER / "verified-normal/CHECKS.json", freeze["files"]["verified-normal/CHECKS.json"])
    inputs = {name: read(LANES / name, pin) for name, pin in PINS.items()}
    for name, pin in receipt["source_pins"].items():
        need(sha256((LANES / name).read_bytes()).hexdigest() == pin, "Other declared source")
    common = inputs["independent-review-20261017/common-gauge-rank-20261020/FREEZE.json"]
    for name, pin in common["files"].items():
        need(sha256((LANES / "independent-review-20261017/common-gauge-rank-20261020" / name).read_bytes()).hexdigest()
             == pin, "Common gauge theorem file")
    model = inputs[next(k for k in PINS if k.endswith("EXTENSION-PROGRAM.json.gz"))]["model"]
    cyclic = inputs[next(k for k in PINS if k.endswith("CYCLIC-FLAGS.json"))]
    geometry = inputs[next(k for k in PINS if k.endswith("GEOMETRY.json"))]
    labels = model["ports"]
    need(labels == packet["ports"] == cyclic["ports"] == geometry["q_labels"], "Actual port labels")
    root = span([30, 45, 75, 384])
    need(len(root) == 16 and all(parity(u) == 0 for u in root), "Four-dimensional even root")
    need(root == set(packet["root_space"]) == set(geometry["common_even_isotropic_space"])
         and all(parity(u & v) == 0 for u in root for v in root), "Actual isotropic root space")
    classes = [min(q ^ u for u in root) for q in labels]
    need(classes == packet["phase_classes"] and Counter(Counter(classes).values()) == {8: 14}, "Actual phase classes")
    h, hi, p, pi = (identity(112) for _ in range(4))
    for pair in cyclic["pair_codes"]:
        need(len({classes[i] for i in pair["ports"]}) == 1, "H preserves phase classes")
        put_pair(h, hi, pair["ports"], pair["matrix"])

    source_groups = [(a["ordered_carriers_a_b_c"], a["signs"]) for a in model["vertex_assignments"]]
    source_groups += [(ports, [1] * 8) for ports in model["small_cliques"]]
    need(Counter(i for ports, _ in source_groups for i in ports) == Counter(range(112)), "Disjoint complete groups")
    s, e_mode, k_mode, reduced = (identity(112) for _ in range(4))
    active, all_pairs, group_checks = [], [], []
    for group_index, (ports, signs) in enumerate(source_groups):
        size = len(ports)
        need(size in (6, 8) and all(abs(d) == 1 for d in signs), "Signed actual group")
        d = dict(zip(ports, map(Q, signs)))
        pairs = [[i for i in ports if classes[i] == g] for g in sorted({classes[i] for i in ports})]
        need(all(len(pair) == 2 for pair in pairs), "Pairs within each group class")
        selected = pairs[0]
        for pair in pairs:
            a0, b0 = (d[i] for i in pair)
            put_pair(p, pi, pair, [[a0, b0], [-a0, b0]])
        a, b = {i: Q(0) for i in ports}, {i: Q(0) for i in ports}
        if size == 6:
            a[selected[0]] = 2 * d[selected[0]]
            b[selected[0]], b[selected[1]] = 3 * d[selected[0]], -d[selected[1]]
            u = {i: a[i] - d[i] for i in ports}
            v = {i: (d[i] - b[i]) / 4 for i in ports}
            chosen = [selected[1]] + [pair[0] for pair in pairs[1:]]
            ru, rv = [-2] * 3, [Q(1, 2), Q(1, 4), Q(1, 4)]
        else:
            for i in selected:
                a[i] = b[i] = 2 * d[i]
            u = {i: a[i] - d[i] for i in ports}
            v = {i: -u[i] / 4 for i in ports}
            chosen = [pair[0] for pair in pairs]
            ru, rv = [1, -1, -1, -1], [Q(-1, 2)] + [Q(1, 2)] * 3
        need(sum(v[i] * d[i] for i in ports) == 1 and sum(v[i] * u[i] for i in ports) == -2, "Rank-one involution identities")
        need(sum(b[i] * a[i] for i in ports) == size, "Conserved response eigenvalue")
        need(all(b[i] + sum(b[j] * u[j] for j in ports) * v[i] == d[i] for i in ports), "Captured query covector")
        for i in ports:
            s[i] = add(s[i], v, u[i])
            e_mode[i] = add(e_mode[i], d, -d[i])
            k_mode[i] = add(k_mode[i], b, -a[i])
        for i, ui in zip(chosen, ru):
            reduced[i] = add(reduced[i], dict(zip(chosen, rv)), ui)
        g = packet["groups"][group_index]
        need(g["ports"] == ports and g["signs"] == signs and g["pairs"] == pairs
             and g["active_ports"] == chosen, "Emitted group and active orientation")
        active.extend(chosen)
        all_pairs.extend(pairs)
        group_checks.append({"size": size, "selected_pair": selected, "active": chosen,
                             "pair_difference_rank": binary_rank([labels[i] ^ labels[j] for i, j in pairs])})

    unit = identity(112)
    need(multiply(h, hi) == multiply(hi, h) == multiply(p, pi) == multiply(pi, p) == unit, "Both pair inverse orders")
    e = multiply(hi, multiply(e_mode, h))
    c = multiply(hi, multiply(s, h))
    k = multiply(hi, multiply(k_mode, h))
    need(e == sparse(model["response"]) == sparse(packet["source_response"]), "Actual physical response")
    need(c == sparse(packet["capture"]) and k == sparse(packet["coded_response"]), "Independent capture and response")
    need(multiply(c, c) == unit and multiply(c, multiply(e, c)) == k, "Involution and response conjugation")
    need(multiply(p, multiply(s, pi)) == reduced, "Selected difference reduction")
    need(all(e[i].get(j, 0) == e[j].get(i, 0) for i in range(112) for j in range(112)), "Source symmetry")
    need(all(classes[i] == classes[j] for i, row in enumerate(k) for j in row), "K preserves global classes")
    need(active == packet["active_ports"] and len(set(active)) == 56
         and Counter(classes[i] for i in active) == {g: 4 for g in set(classes)}, "Exactly four active fields per class")
    delta = [add(row, {i: Q(1)}, -1) for i, row in enumerate(c)]
    need(elimination(delta)[0] == 16 and elimination(c) == (112, 1), "Displacement rank and determinant")
    need(elimination(k) == (112, Q(35**8)), "Non-dyadic-unit coded response")
    ei = sparse(model["response_inverse"])
    need(multiply(e, ei) == multiply(ei, e) == unit, "Actual response inverse")
    ki = multiply(c, multiply(ei, c))
    need(multiply(k, ki) == multiply(ki, k) == unit, "Both coded response inverse orders")
    inverse_denominator = lcm(*(v.denominator for row in ki for v in row.values()))
    need(inverse_denominator == 35, "Both odd inverse factors remain")

    word_names = ["H_word", "T_word", "reduced_word", "capture_word", "inverse_word",
                  "coded_forward_word", "coded_backward_word"]
    need(packet["capture_word"] == packet["H_word"] + packet["T_word"] + packet["reduced_word"]
         + inverse_word(packet["T_word"]) + inverse_word(packet["H_word"]),
         "The complete literal factor order")
    need(packet["inverse_word"] == inverse_word(packet["capture_word"]), "The complete literal reverse word")
    need(all(op != "add" or classes[target] == classes[source]
             for name in ("H_word", "T_word") for op, target, source, _ in packet[name]),
         "Every pair-code prefix preserves phase classes")
    need(all(target in active and (op != "add" or source in active)
             for op, target, source, _ in packet["reduced_word"]), "Every core prefix uses active fields only")
    reports, maps = {}, {}
    for name in word_names:
        maps[name], reports[name] = replay(packet[name])
    extra = [{i: Q(1)} for i in range(112, 640)]
    need(maps["H_word"] == h + extra and maps["T_word"] == p + extra, "Literal pair codes")
    need(maps["reduced_word"] == reduced + extra, "Literal reduced core")
    need(maps["capture_word"] == maps["inverse_word"] == c + extra, "All 640 arbitrary input columns")
    need(replay(packet["capture_word"] + packet["inverse_word"])[0] == identity(640)
         and replay(packet["inverse_word"] + packet["capture_word"])[0] == identity(640), "Both complete inverse orders")
    forward, backward = identity(640), identity(640)
    for i, row in enumerate(k):
        forward[112 + i] = add(forward[112 + i], row)
        backward[i] = add(backward[i], {112 + j: v for j, v in row.items()}, -1)
    need(maps["coded_forward_word"] == forward and maps["coded_backward_word"] == backward,
         "All 640 arbitrary additive-coupler columns")
    need(all(reports[name]["price"] == price for name, price in
             [("H_word", 470), ("T_word", 1016), ("reduced_word", 1072),
              ("capture_word", 4044), ("inverse_word", 4044),
              ("coded_forward_word", 1544), ("coded_backward_word", 1544)]), "Complete scalar invoices")
    need(all(reports[name]["maximum_row_one_norm"] == "10" and reports[name]["binary_height"] == 3
             for name in ("capture_word", "inverse_word")), "Exact scalar prefix bounds")
    passive = set(range(112)) - set(active)
    need(all(reduced[i] == {i: Q(1)} for i in passive), "All passive data remain arbitrary")
    need(all(j in active for i in active for j in reduced[i]), "The reduced core does not read passive data")

    # These controls separate the actual interface from two incorrect ones.
    selected_difference = packet["groups"][0]["selected_pair"][1]
    mutation = [gate for gate in packet["reduced_word"] if gate[1] != selected_difference]
    need(replay(mutation)[0] != maps["reduced_word"], "Reject omission of the selected difference")
    transpose_witness = next((i, j, str(k[i].get(j, 0)), str(k[j].get(i, 0)))
                             for i in range(112) for j in range(112) if k[i].get(j, 0) != k[j].get(i, 0))
    need(any(i != j for i, row in enumerate(k) for j in row), "K is not physically diagonal")

    w = inputs[next(k for k in PINS if "shared-root-eight" in k)]["W"]
    w45 = inputs[next(k for k in PINS if k.endswith("GAUGE-PROGRAMS.json"))]["W"]["circuit"]
    need(w == packet["W"] and fourier_rank(w) == 4 and fourier_rank(w45) == 1, "Actual carried frames")
    wi, w45i = inverse_circuit(w), inverse_circuit(w45)
    anchors = {g: min(labels[i] for i in range(112) if classes[i] == g) for g in set(classes)}
    need({int(g): q for g, q in packet["global_anchors"].items()} == anchors, "One actual global anchor per class")
    for i, q in enumerate(labels):
        anchor = anchors[classes[i]]
        need(q ^ anchor in root and parity(anchor), "Even difference and odd anchor")
        need(fourier_rank(wi + [["C", anchor, -1], ["C", q, 1]] + w) == 0, "Alignment is monomial in W_R")
        need(fourier_rank(wi + [["C", anchor, 1]] + w) == 1, "Anchor has Fourier rank one")
    wrong_ranks = [fourier_rank(w45i + [["C", labels[j], -1], ["C", labels[i], 1]] + w45)
                   for i, j in all_pairs]
    need(wrong_ranks == [2] * 56, "All actual pair ratios have rank two in W45")
    need(all(g["pair_difference_rank"] == 4 for g in group_checks if g["size"] == 8),
         "The four disjoint pair differences are independent")
    need(binary_rank([labels[i] ^ labels[j] for i, j in all_pairs]) == 4, "Exact common-gauge lower-bound rank")

    out = {
        "status": "PASS_INDEPENDENT_DYADIC_PHASE_CLASS_CAPTURE",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "producer_freeze_sha256": FREEZE_PIN, "source_pins": PINS,
        "producer_imports": 0, "scalar_input_columns": 640, "untouched_capture_fields": 528,
        "capture_displacement_rank": 16, "capture_determinant": "1",
        "coded_response_determinant": str(35**8), "coded_inverse_denominator_lcm": inverse_denominator,
        "K_not_transpose_witness": transpose_witness,
        "active_fields": len(active), "global_classes": 14, "group_checks": group_checks,
        "literal_scalar_reports": reports, "W_R_rank": 4, "W45_rank": 1,
        "word_level_phase_prefix_premises": True,
        "monomial_alignment_ranks_checked": 112, "rank_one_anchor_checks": 112,
        "W45_pair_ratio_ranks": wrong_ranks, "minimum_common_gauge_rank": 4,
        "scope": "Exact common-frame scalar word and binary phase geometry. The 112-H1 count is conditional on W_R. No phase recipes, complete routed caller, or supplier admission.",
    }
    (HERE / "REVIEW.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print("PASS_INDEPENDENT_DYADIC_PHASE_CLASS_CAPTURE: 640 inputs; 4044/1544 scalar costs; W_R rank4; W45 pair ratios rank2")


if __name__ == "__main__":
    main()
