"""Check the natural triple with separate local matrix and frame proofs."""

import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import gzip
import json
from pathlib import Path
import shutil


HERE = Path(__file__).resolve().parent
LANE = HERE.parents[1]
LANES = LANE.parent
PRODUCER = LANE / "no-reset-triple-20261020"
NATIVE = LANES / "new-core-transfer-20261017/low-displacement-20261020"
UNIT = tuple(1 << j for j in range(25))
ID = (UNIT, 0)
SOURCES = {
    "views": (
        LANES / "bridge-access-20261017/matched-stage-access-20261018/DIMENSION25-VIEWS.json",
        "125e74660e99d824f8699eed72c1facb59287976bf2c47fda533d654b8344473",
    ),
    "row_code": (
        NATIVE / "row-only-capture-20261020/run-normal/PRODUCTIVE-CAPTURE.json.gz",
        "7c3b8343ec04c65f98b7170c7f37c9f80605e28c95df00bcf2a189908461c8b2",
    ),
    "forward": (
        NATIVE / "clean-late-exchange-20261020/run-normal/CLEAN-LATE-EXCHANGE.json.gz",
        "b0432322c28ad3a03af8da550a0b7c7df048c7ff5a0664acc7f78efffcffd083",
    ),
    "dual": (
        NATIVE / "clean-late-exchange-20261020/dual-normal/CLEAN-DUAL.json.gz",
        "6c8869b1c1b45632635805e389899b83fa8348c9fe5b84e3c9c7821bcfd0568c",
    ),
}
PRODUCER_PINS = {
    "producer_proof": "e968dd64f34f8dd4422145ccea847d329886657e9e209682a49964d7faf60f3c",
    "producer_checker": "8612732e02b68495d6b0b95cbd216d1d0df43be2ffdd29cc7fc9033518ab1c48",
    "producer_phase_library": "70ca9ce2dff5256644f35ef65344c7e0dd9f78e3fb48c18436e9e5c20b4f9109",
    "producer_checks": "24741af6fabff0e09bc13518f79477a80f32f88bb49aabaf31f40afa070aa543",
    "producer_freeze": "089425bdf431d81456e1c988a1fd21a837baca43e510bc92dee98dc2ee571791",
}


def need(ok, label):
    if not ok:
        raise ValueError(label)


def digest(raw):
    return sha256(raw).hexdigest()


def act(columns, vector):
    result = 0
    for j, column in enumerate(columns):
        if vector & (1 << j):
            result ^= column
    return result


def transposed(columns, vector):
    return sum(((column & vector).bit_count() & 1) << j
               for j, column in enumerate(columns))


def compose(left, right):
    return tuple(act(left, column) for column in right)


def normal(word):
    """Apply the word from right to left and use input character coordinates."""
    matrix = UNIT
    terms = Counter()
    for kind, value, power in reversed(word):
        if kind == "R":
            matrix = compose(value, matrix)
        else:
            need(kind == "P", "Known phase operator")
            terms[transposed(matrix, value)] += power
    terms = [(v, c % 4) for v, c in terms.items() if c % 4]
    linear = tuple(sum(c * ((v >> j) & 1) for v, c in terms) % 4 for j in range(25))
    quadratic = []
    for i in range(25):
        for j in range(i + 1, 25):
            sample = (1 << i) | (1 << j)
            value = (sum(c * ((v & sample).bit_count() & 1) for v, c in terms) -
                     linear[i] - linear[j]) % 4
            if value:
                need(value == 2, "Even quadratic coefficient")
                quadratic.append((i, j, value))
    return matrix, linear, tuple(quadratic)


def route(columns):
    return [("R", tuple(columns), 0)]


def line(vector, power):
    return [("P", vector, power)]


def fourier(start, stop, power=1):
    return [("P", 1 << j, power) for j in range(start, stop)]


def plus(*terms):
    result = {}
    for coefficient, row in terms:
        for key, value in row.items():
            total = result.get(key, F(0)) + coefficient * value
            if total:
                result[key] = total
            else:
                result.pop(key, None)
    return result


def linear(matrix, rows):
    return [plus(*((c, rows[j]) for j, c in row.items())) for row in matrix]


def sparse(rows):
    return [{int(j): F(c) for j, c in row.items() if F(c)} for row in rows]


def transpose(matrix, columns):
    result = [{} for _ in range(columns)]
    for i, row in enumerate(matrix):
        for j, value in row.items():
            result[j][i] = value
    return result


def eye(size):
    return [{j: F(1)} for j in range(size)]


def add_price(value):
    a, b = abs(value.numerator), value.denominator
    need(a and b & (b - 1) == 0, "Nonzero dyadic ADD")
    return 2 * (3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1)


def local_invoice(item):
    profile = Counter()
    scalar = 0
    for event in item["events"]:
        if event[0] == "native":
            profile[event[4]] += 1
        else:
            need(event[0] == "scalar", "Known native word event")
            gate = event[1]
            value = F(gate[3])
            if gate[0] == "add":
                scalar += add_price(value)
            else:
                need(gate[0] == "scale", "Known native scalar event")
                a, b = abs(value.numerator), value.denominator
                need(a & (a - 1) == b & (b - 1) == 0, "Signed dyadic unit scale")
                scalar += 2 * (abs(a.bit_length() - b.bit_length()) + (value < 0))
    return {"profile": dict(sorted(profile.items())), "native_mass": sum(r * n for r, n in profile.items()),
            "native_children": sum(profile.values()), "real_scalar_primitives": scalar}


def source_matrix_checks(source, selected, ordinary, h, d):
    basis = eye(224)
    a, u = [basis[p] for p in selected], [basis[p] for p in ordinary]
    z, v = [basis[112 + p] for p in selected], [basis[112 + p] for p in ordinary]

    def joined(ap, ur, zp, vr):
        result = [None] * 224
        for ports, rows, offset in ((selected, ap, 0), (ordinary, ur, 0),
                                   (selected, zp, 112), (ordinary, vr, 112)):
            for p, row in zip(ports, rows):
                result[offset + p] = row
        return result

    alpha = [plus((1, x), (1, y)) for x, y in zip(a, linear(h, u))]
    lower = [plus((1, x), (1, y), (1, z0)) for x, y, z0 in zip(v, u, linear(d, alpha))]
    forward = joined([plus((-1, row)) for row in z], u, alpha, lower)
    need(forward == sparse(source["forward"]["content_map"]), "All 224 forward content columns")
    inverse = joined([plus((1, x), (-1, y)) for x, y in zip(z, linear(h, u))], u,
                     [plus((-1, row)) for row in a],
                     [plus((1, x), (-1, y), (-1, z0)) for x, y, z0 in zip(v, u, linear(d, z))])
    need(inverse == sparse(source["forward"]["inverse_content_map"]), "Stored forward inverse")
    need(linear(forward, inverse) == basis and linear(inverse, forward) == basis, "Forward inverse both orders")
    inverse_adjoint = transpose(inverse, 224)
    need(inverse_adjoint == sparse(source["dual"]["content_maps"]["inverse_adjoint"]), "Actual inverse transpose")
    permutation = list(range(224))
    for p in selected:
        permutation[p], permutation[112 + p] = 112 + p, p
    conjugate = [{permutation[j]: value for j, value in inverse_adjoint[permutation[i]].items()}
                 for i in range(224)]
    beta = [plus((1, x), (1, y)) for x, y in zip(z, linear(h, v))]
    middle = [plus((1, x), (1, y), (-1, z0)) for x, y, z0 in zip(u, linear(d, z), v)]
    backward = joined(beta, middle, [plus((-1, row)) for row in a], v)
    need(backward == conjugate == sparse(source["dual"]["content_maps"]["selected_swap_conjugate"]),
         "All 224 selected-swap inverse-adjoint columns")
    return forward, backward


def abstract_check():
    """Keep H0,H1,H2,D0,D1,D2 free and preserve every product order."""
    a, u, z, v = [{(i, ()): F(1)} for i in range(4)]

    def op(name, row):
        return {(source, (name,) + word): coefficient for (source, word), coefficient in row.items()}

    def forward(s, state):
        ap, ur, zp, vr = state
        alpha = plus((1, ap), (1, op("H" + str(s), ur)))
        return [plus((-1, zp)), ur, alpha,
                plus((1, vr), (1, ur), (1, op("D" + str(s), alpha)))]

    def backward(s, state):
        ap, ur, zp, vr = state
        return [plus((1, zp), (1, op("H" + str(s), vr))),
                plus((1, ur), (1, op("D" + str(s), zp)), (-1, vr)), plus((-1, ap)), vr]

    first = forward(0, [a, u, z, v])
    second = backward(1, first)
    endpoint = forward(2, second)
    alpha = plus((1, a), (1, op("H0", u)))
    k = plus((1, v), (1, u), (1, op("D0", alpha)))
    w = plus((-1, v), (1, op("D1", alpha)), (-1, op("D0", alpha)))
    beta = plus((1, alpha), (1, op("H1", k)), (1, op("H2", w)))
    r = plus((1, u), (1, op("D1", alpha)), (1, op("D2", beta)))
    need(first == [plus((-1, z)), u, alpha, k], "First stage endpoint")
    need(second == [plus((1, alpha), (1, op("H1", k))), w, z, k], "Second stage endpoint")
    need(endpoint == [plus((-1, z)), w, beta, r], "Third stage endpoint")
    recovered_k = plus((1, r), (-1, op("D2", beta)), (-1, w))
    recovered_alpha = plus((1, beta), (-1, op("H1", recovered_k)), (-1, op("H2", w)))
    recovered_u = plus((1, r), (-1, op("D1", recovered_alpha)), (-1, op("D2", beta)))
    recovered_a = plus((1, recovered_alpha), (-1, op("H0", recovered_u)))
    recovered_v = plus((-1, w), (1, op("D1", recovered_alpha)), (-1, op("D0", recovered_alpha)))
    need([recovered_alpha, recovered_a, recovered_u, recovered_v] == [alpha, a, u, v], "Ordered content inverse")
    state = list(endpoint)
    trace = [list(state)]
    # The first 96 positive lines change the ordinary Y frame to FULL.
    state[3] = plus((1, state[3]), (-1, op("D2", state[2])))
    trace.append(list(state))
    state[2] = plus((1, state[2]), (-1, op("H1", state[3])))
    trace.append(list(state))
    state[2] = plus((1, state[2]), (1, op("H1", state[1])), (-1, op("H2", state[1])))
    trace.append(list(state))
    state[1] = plus((-1, state[1]), (1, op("D1", state[2])), (-1, op("D0", state[2])))
    trace.append(list(state))
    state[3] = plus((1, state[3]), (-1, op("D1", state[2])))
    trace.append(list(state))
    state[2] = plus((1, state[2]), (-1, op("H0", state[3])))
    trace.append(list(state))
    state[0] = plus((-1, state[0]))
    trace.append(list(state))
    need(state == [z, v, a, u], "In-place terminal content and bank order")
    # The final 112 positive lines restore Q(a,u) on Y.
    def encode(rows):
        return [[{"source_group": source, "word": list(word), "coefficient": str(value)}
                 for (source, word), value in sorted(row.items())] for row in rows]
    return {"initial_groups": ["a", "u", "z", "v"], "first": encode(first),
            "second": encode(second), "endpoint": encode(endpoint),
            "terminal_trace_after_ordinary_Q": [encode(rows) for rows in trace],
            "endpoint_holes": "Only Y_R has the exterior q_R.",
            "operator_relations_used": "None between H_s and D_t; no inverse of I+H1 D2."}


def affine_product(left, right):
    matrix, shift = left
    other, translation = right
    return compose(matrix, other), shift ^ act(matrix, translation)


def terminal_shear(matrix, source_fields, target_fields, stage, sign, views):
    events = []
    if stage:
        for field in source_fields + target_fields:
            rho, shift = views[stage, field % 112]
            events.append(["MAP", field, list(rho), shift])
    for i, row in enumerate(matrix):
        for j, coefficient in sorted(row.items()):
            events.append(["ADD", target_fields[i], source_fields[j], str(sign * coefficient)])
    if stage:
        for field in target_fields + source_fields:
            rho, shift = views[stage, field % 112]
            events.append(["MAP", field, list(rho), shift])
    state = [{(j, UNIT, 0): F(1)} for j in range(224)]
    invoice = Counter()
    for event in events:
        invoice[event[0]] += 1
        if event[0] == "MAP":
            target, view = event[1], (tuple(event[2]), event[3])
            state[target] = {(source, new[0], new[1]): value
                             for (source, old, translation), value in state[target].items()
                             for new in [affine_product(view, (old, translation))]}
        else:
            target, source, coefficient = event[1], event[2], F(event[3])
            state[target] = plus((1, state[target]), (coefficient, state[source]))
            invoice["scalar_units"] += add_price(coefficient)
    expected = [{(j, UNIT, 0): F(1)} for j in range(224)]
    for i, row in enumerate(matrix):
        target = target_fields[i]
        left = views[stage, target % 112] if stage else ID
        for j, coefficient in row.items():
            source = source_fields[j]
            right = views[stage, source % 112] if stage else ID
            product = affine_product(left, right)
            expected[target][source, product[0], product[1]] = sign * coefficient
    need(state == expected, "Literal FULL shear on all 224 columns")
    return events, dict(sorted(invoice.items()))


def write_json(path, value):
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    path.write_bytes(raw)
    return digest(raw)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--producer-run", default="run-terminal-normal")
    args = parser.parse_args()
    need(shutil.disk_usage(HERE).free >= 3 * 1024**3, "At least 3 GiB free")
    args.out.mkdir(parents=True, exist_ok=False)
    source, manifest = {}, {}
    for name, (path, pin) in SOURCES.items():
        raw = path.read_bytes()
        decoded = gzip.decompress(raw) if path.suffix == ".gz" else raw
        need(digest(decoded) == pin, "Pinned source " + name)
        manifest[name] = {"path": str(path), "sha256": digest(raw), "payload_sha256": pin}
        source[name] = json.loads(decoded)
    extra = {
        "forward_proof": NATIVE / "clean-late-exchange-20261020/CLEAN-LATE-EXCHANGE.md",
        "dual_proof": NATIVE / "clean-late-exchange-20261020/CLEAN-DUAL.md",
        "producer_proof": PRODUCER / "NO-RESET.md",
        "producer_checker": PRODUCER / "check_no_reset.py",
        "producer_phase_library": LANE / "coupled-data-split-20261020/check_typed_split.py",
        "producer_checks": PRODUCER / args.producer_run / "CHECKS.json",
        "producer_freeze": PRODUCER / "FREEZE.json",
    }
    for name, path in extra.items():
        pin = digest(path.read_bytes())
        if name in PRODUCER_PINS:
            need(pin == PRODUCER_PINS[name], "Pinned " + name)
        manifest[name] = {"path": str(path), "sha256": pin}
    producer = json.loads(extra["producer_checks"].read_bytes())
    records = {(x["stage"], x["port"]): x for x in source["views"]["entries"]}
    need(len(source["views"]["entries"]) == 336 and
         set(records) == {(s, p) for s in range(3) for p in range(112)}, "Complete D25 view set")
    p, r = source["row_code"]["selected_ports"], source["row_code"]["ordinary_ports"]
    need(len(p) == 16 and len(r) == 96 and sorted(p + r) == list(range(112)), "Actual partition")
    for name in ("forward", "dual"):
        need(source[name]["selected_ports"] == p and source[name]["ports"] == source["row_code"]["ports"],
             "Native selected set and port order")
        need(source[name]["code"] == source["row_code"]["code"] and
             source[name]["response"] == source["row_code"]["response"], "Native response and row-code equality")
    q = [records[0, a]["q"] for a in range(112)]
    need(q == source["row_code"]["ports"], "Actual route port labels")
    c, e = sparse(source["row_code"]["code"]), sparse(source["row_code"]["response"])
    h = [{j: c[a][b] for j, b in enumerate(r) if b in c[a]} for a in p]
    d = [{j: e[a][b] for j, b in enumerate(p) if b in e[a]} for a in r]
    expected_c = eye(112)
    for i, a in enumerate(p):
        expected_c[a].update({r[j]: value for j, value in h[i].items()})
    need(c == expected_c, "C has the exact row-only form")
    need(d == [{i: -value for i, value in row.items()} for row in transpose(h, 96)], "D=-H transpose")
    dh = linear(d, h)
    for i, a in enumerate(r):
        expected = {p[j]: value for j, value in d[i].items()}
        for j, value in dh[i].items():
            expected[r[j]] = value
        expected = plus((1, expected), (1, {a: F(1)}))
        need(expected == e[a], "Actual ordinary response row is u+D(a+Hu)")
    source_matrix_checks(source, p, r, h, d)
    invoices = {}
    for name in ("forward", "dual"):
        for provider, variants in source[name]["providers"].items():
            for variant, item in variants.items():
                bill = local_invoice(item)
                need(bill["real_scalar_primitives"] == 8600 and bill["native_children"] == 1520,
                     "Native scalar and child counts")
                expected_profile = {1: 1392, 2: 64, 3: 48, 9 if variant == "I" else 8: 16}
                need(bill["profile"] == expected_profile, "Native profile")
                invoices[name + ":" + provider + ":" + variant] = bill
    views, counts, certificates = {}, Counter(), []
    identity_normal = normal([])
    for s in range(3):
        for a in range(112):
            row = records[s, a]
            matrix = tuple(row["route_columns"])
            need(row["q"] == q[a] and act(matrix, q[a]) == q[a], "Route fixes the matching line")
            need(compose(matrix, matrix) == UNIT and
                 all(transposed(matrix, matrix[j]) == (1 << j) for j in range(25)),
                 "Orthogonal involution")
            if s == 0:
                need(matrix == UNIT, "Stage zero route")
                continue
            alignment = row["literal_stage_alignment"]
            need(alignment["entry_X"] == alignment["entry_Y"] and
                 alignment["exit_X"] == alignment["exit_Y"], "Matched physical bank views")
            delta = act(matrix, alignment["entry_X"])
            entry = line(delta, 2) + route(matrix)
            exit_view = line(alignment["exit_X"], 2) + route(matrix)
            fprev = fourier(0, 9 + 8 * (s - 1))
            fnext = fourier(0, 9 + 8 * s)
            fext = fourier(9, 9 + 8 * s)
            checks = [
                (entry + fprev, fext + line(q[a], 1) + route(matrix)),
                (entry + fprev + line(q[a], -1), fext + route(matrix)),
                (exit_view + fnext, fnext + route(matrix)),
                (exit_view + fnext + line(q[a], -1), fnext + line(q[a], -1) + route(matrix)),
            ]
            for left, right in checks:
                need(normal(left) == normal(right), "Natural mixed frame identity")
                counts["natural_frame_identities"] += 1
            full_result = normal(exit_view + fourier(0, 25))
            need(full_result == normal(fourier(0, 25) + route(matrix)), "Past FULL view")
            need(normal(exit_view + exit_view) == identity_normal, "Physical FULL view is an involution")
            need(normal(exit_view + line(q[a], 1)) == normal(line(q[a], 1) + exit_view), "View commutes with its own Q")
            counts["past_FULL_views"] += 1
            counts["physical_view_inverse_orders"] += 1
            counts["omitted_entry_translation_rejected"] += normal(route(matrix) + fprev) != normal(checks[0][1])
            if a in r:
                counts["ordinary_Y_wrong_FULL_type_rejected"] += normal(entry + fprev) != normal(fext + route(matrix))
            view = matrix, alignment["exit_X"]
            views[s, a] = view
            certificates.append({"stage": s, "port": a, "entry_translation_after_route": delta,
                                 "FULL_translation_after_route": alignment["exit_X"],
                                 "route_columns": list(matrix), "FULL_input_character_normal": full_result})
    full = fourier(0, 25)
    for a in range(112):
        need(normal(line(q[a], 1) + full) == normal(full + line(q[a], 1)),
             "Positive final line preserves the common FULL exterior")
        counts["terminal_positive_line_frame_checks"] += 1
        if a in r:
            need(normal(line(q[a], 1) + full + line(q[a], -1)) == normal(full),
                 "Positive ordinary line removes its hole")
            counts["terminal_positive_line_frame_checks"] += 1
            counts["negative_ordinary_line_rejected"] += (
                normal(line(q[a], -1) + full + line(q[a], -1)) != normal(full))
    abstract = abstract_check()
    xp, xr = p, r
    yp, yr = [112 + a for a in p], [112 + a for a in r]
    specs = [
        ("minus_D2", d, yp, yr, 2, -1),
        ("minus_H1", h, yr, yp, 1, -1),
        ("plus_H1_W", h, xr, yp, 1, 1),
        ("minus_H2_W", h, xr, yp, 2, -1),
        ("plus_D1_alpha", d, yp, xr, 1, 1),
        ("minus_D0_alpha", d, yp, xr, 0, -1),
        ("minus_D1_alpha", d, yp, yr, 1, -1),
        ("minus_H0", h, yr, yp, 0, -1),
    ]
    word = [["LINE", field, q[field % 112], 1] for field in yr]
    shear_invoices = {}
    for index, (name, matrix, sources, targets, stage, sign) in enumerate(specs):
        if index == 4:
            word.extend([["NEG", field] for field in xr])
        events, bill = terminal_shear(matrix, sources, targets, stage, F(sign), views)
        word.extend(events)
        shear_invoices[name] = bill
    word.extend([["NEG", field] for field in xp])
    word.extend([["LINE", 112 + a, q[a], 1] for a in range(112)])
    word_counts = Counter(event[0] for event in word)
    need(word_counts == {"LINE": 208, "MAP": 1344, "ADD": 1728, "NEG": 112}, "Literal terminal counts")
    scalar = sum(bill["scalar_units"] for bill in shear_invoices.values()) + 2 * word_counts["NEG"]
    need(scalar == 16608 and all(bill["scalar_units"] == 2048 for bill in shear_invoices.values()),
         "Actual terminal scalar count")
    need(producer["status"] == "PASS_ACTUAL_D25_NATURAL_CLEAN_TRIPLE", "Completed producer receipt")
    need(producer["literal_route_phase_identities"] == counts["natural_frame_identities"] == 896,
         "Producer route count")
    need(producer["terminal_operator_word"]["positive_line_operations"] == 208 and
         producer["terminal_operator_word"]["direct_scalar_upper_bound"] == scalar and
         producer["terminal_operator_word"]["routed_shear_affine_map_calls"] == 1344,
         "Producer terminal invoice")
    for variant in ("I", "Q"):
        need(producer["variants"][variant]["content_inverse"] == "PASS" and
             producer["variants"][variant]["checked_arbitrary_columns"] == 224, "Completed producer variants")
    need(producer["variants"]["I"]["208_line_terminal_checked"], "Producer terminal passed")
    need(producer["local_native_mass_initial_I"] == 1808 + 2 * 1792 == 5392 and
         producer["local_scalar_initial_I"] == 3 * 8600 == 25800, "Producer local sum")
    need(all(digest(Path(item["path"]).read_bytes()) == item["sha256"] for item in manifest.values()),
         "Every source remains unchanged")
    pins = {
        "SOURCE-MANIFEST.json": write_json(args.out / "SOURCE-MANIFEST.json", manifest),
        "FRAME-CERTIFICATE.json": write_json(args.out / "FRAME-CERTIFICATE.json", certificates),
        "BLOCK-PROOF.json": write_json(args.out / "BLOCK-PROOF.json", abstract),
        "TERMINAL-WORD.json": write_json(args.out / "TERMINAL-WORD.json", word),
    }
    receipt = {
        "status": "PASS_INDEPENDENT_NATURAL_TRIPLE_REVIEW",
        "output_sha256": pins,
        "phase_checks": dict(sorted(counts.items())),
        "local_content_columns": 224,
        "local_inverse_both_orders": True,
        "inverse_adjoint_and_selected_swap_verified": True,
        "global_operator_proof": "Four-block free-operator composition plus exact natural-frame conjugation.",
        "expanded_global_column_replay_repeated": False,
        "H_coefficient_histogram": dict(sorted(Counter(str(x) for row in h for x in row.values()).items())),
        "local_invoices_from_literal_events": invoices,
        "terminal_counts": dict(sorted(word_counts.items())),
        "terminal_scalar_units": scalar,
        "terminal_shear_invoices": shear_invoices,
        "terminal_local_shear_columns": 224,
        "terminal_output": "X=F25 Y0, Y=F25 X0 for initial selected I entry.",
        "extra_selected_Q_entry_restoration_lines": 16,
        "new_fields": 0,
        "odd_divisions": 0,
        "native_line_recipes_or_global_host_supplied": False,
        "complete_supplier_or_kappa_claim": False,
    }
    write_json(args.out / "CHECKS.json", receipt)
    print(receipt["status"])
    print(json.dumps({"phase_checks": receipt["phase_checks"], "terminal_counts": receipt["terminal_counts"],
                      "scalar_units": scalar}, sort_keys=True))


if __name__ == "__main__":
    main()
