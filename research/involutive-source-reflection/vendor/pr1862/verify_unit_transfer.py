"""Check the ordered source code and both complete unit-transfer words.

This checker uses the published independent scalar and native
interpreters. It does not import the unit-transfer producer.
Research used OpenAI Codex under the user's direction.
"""

from collections import Counter
from fractions import Fraction as Q


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return [{i: Q(1)} for i in range(n)]


def sum_rows(left, right, scale, algebra):
    result = [row.copy() for row in left]
    for row, other in zip(result, right):
        algebra.plus(row, other, scale)
    return result


def ordered_instance(R, K, P, L, algebra):
    mul = algebra.multiply
    unit, small = identity(len(K)), identity(len(R))
    require(mul(R, P) == mul(L, K) == small and not any(mul(L, P)),
            "An ordered-ring hypothesis fails")
    M = mul(R, K)
    query = sum_rows(R, L, -1, algebra)
    Z = sum_rows(K, mul(P, sum_rows(M, small, -1, algebra)), -1, algebra)
    J = sum_rows(unit, mul(K, R), -1, algebra)
    G = sum_rows(sum_rows(unit, mul(Z, query), 1, algebra), mul(P, R), -1, algebra)
    inverse = sum_rows(sum_rows(unit, mul(P, L), 1, algebra), mul(Z, R), -1, algebra)
    correction = [{j: -value for j, value in row.items()}
                  for row in mul(P, sum_rows(R, mul(sum_rows(M, small, -1, algebra), query), 1, algebra))]
    require(mul(R, Z) == mul(L, Z) == mul(query, P) == small and not any(mul(query, Z)),
            "The two query coordinates do not split")
    require(mul(L, G) == R and mul(R, G) == query, "The two source queries have the wrong action")
    require(mul(J, G) == sum_rows(unit, correction, 1, algebra), "The target residual has the wrong order")
    require(mul(G, inverse) == mul(inverse, G) == unit, "A source inverse order fails")
    require(mul(correction, Z) == [{j: -value for j, value in row.items()} for row in P],
            "The selected correction loses a source direction")
    projection = sum_rows(mul(P, query), mul(Z, L), 1, algebra)
    complement = sum_rows(unit, projection, -1, algebra)
    require(mul(projection, projection) == projection and not any(mul(query, complement))
            and not any(mul(L, complement)), "The source decomposition is not a direct projection")
    require(mul(G, complement) == complement and mul(G, P) == Z
            and mul(G, Z) == sum_rows(Z, P, -1, algebra), "The order-six block action fails")
    return {"R": R, "K": K, "P": P, "L": L, "M": M, "Q": query, "Z": Z,
            "J": J, "G": G, "G_inverse": inverse, "JG_minus_I": correction,
            "projection": projection, "complement": complement}


def ring_checks(algebra):
    def rows(values):
        return [{j: Q(value) for j, value in enumerate(row) if value} for row in values]

    R = rows([[1, 0, 0, 1, 1, 0], [0, 1, 1, 0, 1, 1]])
    K = rows([[1, -2], [-2, -1], [1, 0], [0, 1], [1, 2], [0, 1]])
    P = [{0: Q(1)}, {1: Q(1)}, {}, {}, {}, {}]
    L = [{2: Q(1)}, {3: Q(1)}]
    noncentral = ordered_instance(R, K, P, L, algebra)
    swap = rows([[0, 1], [1, 0]])
    require(algebra.multiply(noncentral["M"], swap) != algebra.multiply(swap, noncentral["M"]),
            "The ordered-ring example has a central M")
    power = identity(6)
    for _ in range(6):
        power = algebra.multiply(noncentral["G"], power)
    require(power == identity(6), "Order six fails for noncentral M")
    small_R, small_P, small_L = rows([[1, 1]]), rows([[1], [0]]), rows([[0, 1]])
    for small_K in (rows([[-1], [1]]), rows([[0], [1]])):
        ordered_instance(small_R, small_K, small_P, small_L, algebra)
    failures = ((rows([[0, 1]]), rows([[0], [1]]), small_P, small_L),
                (small_R, rows([[0], [1]]), small_P, rows([[1, 1]])),
                (small_R, rows([[0], [0]]), small_P, small_L))
    for instance in failures:
        rejected = False
        try:
            ordered_instance(*instance, algebra)
        except ValueError:
            rejected = True
        require(rejected, "A missing ordered-ring hypothesis was admitted")
    G = rows([[0, -1], [1, 1]])
    inverse = rows([[1, 1], [-1, 0]])
    require(any(sum_rows(G, inverse, -1, algebra)), "The same-chart FBF residual vanished")
    F = [{0: Q(1), 1: Q(1)}, {0: Q(-1)}, {0: Q(1), 1: Q(1), 2: Q(1)}, {0: Q(-1), 3: Q(1)}]
    B = [{0: Q(1), 2: Q(-1)}, {1: Q(1), 3: Q(-1)}, {3: Q(-1)}, {2: Q(1), 3: Q(1)}]
    shortcut = algebra.multiply(F, algebra.multiply(B, F))
    require(any(j >= 2 and value for row in shortcut[2:] for j, value in row.items()),
            "The FBF shortcut became a signed exchange")
    changed_chart = rows([[0, -2], [Q(1, 2), 1]])
    power = identity(2)
    for _ in range(6):
        power = algebra.multiply(changed_chart, power)
    require(power == identity(2), "The second chart does not have order six")
    product = algebra.multiply(G, changed_chart)
    power = identity(2)
    for _ in range(6):
        power = algebra.multiply(product, power)
    require(power != identity(2), "The changing-chart counterexample has sixth power identity")
    return {"noncentral_M": noncentral["M"],
            "singular_M_and_M_minus_I": True, "three_hypothesis_controls": True,
            "same_chart_FBF_is_not_signed_exchange": True,
            "order_six_does_not_imply_changing_chart_product_order_six": True}


def boundary_frames(events, word, ports, output, algebra):
    full = word["final"][0]
    if output:
        persistent = [("FULL",)] * 112 + [("hole", p) for p in range(112)] + [("helper", p) for p in range(480)]
        physical = {0: ("I",), full: ("FULL",)}
        physical.update({word["final"][112 + p]: ("hole", p) for p in ports})
    else:
        persistent = [("input", p) for p in range(112)] + [("I",)] * 112 + [("helper", p) for p in range(480)]
        physical = {0: ("I",)}
        physical.update({word["start"][p]: ("input", p) for p in ports})
    require(len(physical) == len(ports) + (2 if output else 1), "Selected boundary frame IDs collide")
    state, used = persistent + [("I",)] * 8, []
    for event in events:
        if event[0] == "phase":
            continue
        if event[0] == "unit_transfer_input_line":
            _, port, label, old, new, child_rank = event
            require(not output and port in ports and label == word["ports"][port]
                    and old == 0 and new == word["start"][port] and child_rank == 1
                    and state[704] == ("I",), "A positive input-line binding changed")
            state[704] = ("input", port)
            used.append(port)
            continue
        if event[0] == "unit_transfer_exit_line":
            _, port, label, sign, old, new, child_rank = event
            require(output and port in ports and label == word["ports"][port] and sign == -1
                    and old == full and new == word["final"][112 + port] and child_rank == 1
                    and state[704] == ("FULL",), "An inverse exit-line binding changed")
            state[704] = ("hole", port)
            used.append(port)
            continue
        require(event[0] == "scalar", "A boundary word has an unknown event")
        gate, common = event[1:]
        target = algebra.register(gate[1])
        require(common in physical, "An added scalar uses an unbound physical boundary frame")
        if gate[0] == "clear":
            require(target == 704 and common in ((0, full) if output else (0,)), "Only C0 can be cleared at this boundary")
            state[target] = physical[common]
            continue
        require(gate[0] == "add", "A boundary word has an unpriced scalar gate")
        source = algebra.register(gate[2])
        require(target != source and state[target] == state[source] == physical[common],
                "An added scalar crosses physical boundary frames")
        bank = range(112) if output else range(112, 224)
        other = range(112, 224) if output else range(112)
        require((target == 704 and source in bank) or (target in bank and (source in bank or source == 704))
                or (target in other and source == 704), "A boundary word accesses a borrowed helper or another private field")
    require(state[:704] == persistent and state[704:] == [("I",)] * 8,
            "A boundary word does not restore its physical private endpoint")
    return used


def source_queries(events, bank, expected, algebra):
    state, snapshots, active = identity(712), 0, False
    for event in events:
        require(event[0] == "scalar", "A source code contains a native operation")
        gate = event[1]
        if gate[0] == "clear":
            active = False
        elif gate[1][0] == "L" and gate[2] == ["C", 0] and not active:
            require(snapshots < 8 and state[704] == {bank + j: value for j, value in expected[snapshots].items()},
                    "A serial source query has the wrong chronological value")
            snapshots += 1
            active = True
        elif gate[1] == ["C", 0]:
            require(not active, "A source scatter starts before its query read is complete")
        state = algebra.forward([event], state)
    require(snapshots == 8 and not state[704], "A source query or its clearing is missing")


def scalar_bill(events, algebra):
    gates = [event[1] for event in events if event[0] == "scalar"]
    return {"real_primitives": sum(algebra.scalar_cost(gate) for gate in gates),
            "operations": dict(sorted(Counter(gate[0] for gate in gates).items()))}


def prefix_bound(events, algebra):
    values, peak = [Q(1)] * 712, Q(1)
    for event in events:
        if event[0] != "scalar":
            continue
        gate = event[1]
        target = algebra.register(gate[1])
        if gate[0] == "clear":
            values[target] = Q(0)
        elif gate[0] == "scale":
            values[target] *= abs(Q(gate[2], gate[3]))
        else:
            require(gate[0] == "add", "Unknown prefix-bound scalar gate")
            source = algebra.register(gate[2])
            value = Q(gate[3], gate[4])
            peak = max(peak, abs(value.numerator) * values[source])
            values[target] += abs(value) * values[source]
        peak = max(peak, values[target])
    bits = 0
    while Q(2) ** bits < peak:
        bits += 1
    return {"formal_scalar_triangle_bound": str(peak), "ceiling_log2": bits}


def check_exit_native(data, certificate, extension, native):
    word = data["word"]
    records = extension["inverse_exit_recipes"]
    require([record["port"] for record in records] == certificate["compensation_ports"],
            "The inverse exit recipe inventory changed")
    positive = {record["port"]: record for record in certificate["input_recipes"]}
    full = native.fourier(9)
    for item in records:
        port, label, record = item["port"], item["label"], item["recipe"]
        require(item["sign"] == -1 and label == word["ports"][port] and record["rank"] == 1,
                "An exit recipe label, sign or rank changed")
        reference = positive[port]["recipe"]
        for side in ("left", "right"):
            require({key: value for key, value in record[side].items() if key != "offset"}
                    == {key: value for key, value in reference[side].items() if key != "offset"}
                    and record[side]["offset"] == (label if side == "left" else 0),
                    "An exit wrapper is not the reviewed positive wrapper with left translation")
        actual, expected = native.recipe(record), (("C", label, -1),)
        native.equal(actual, expected, "Inverse inherited exit line")
        native.equal(full + actual, expected + full, "Exact FULL-to-hole boundary")
        for basis in range(512):
            require(native.state(actual, basis) == native.state(expected, basis), "An inverse native Gaussian column differs")
        require(native.state(native.recipe(reference)) != native.state(expected), "The positive exit-line control was not rejected")
        phased = actual + (("phase", 1),)
        require(native.tableau(phased) == native.tableau(actual) and native.state(phased) != native.state(expected),
                "An exit phase-only mutation was not rejected")
        span = {0}
        for vector in word["frames"][word["final"][112 + port]]:
            span |= {value ^ vector for value in tuple(span)}
        require(span == {value for value in range(512) if (value & label).bit_count() % 2 == 0},
                "An output frame ID has the wrong hole subspace")
    return {"inverse_exit_recipes": 8, "exact_inverse_gaussian_columns": 4096,
            "exact_FULL_to_hole_identities": 8, "positive_line_controls": 8, "phase_only_controls": 8}


def verify(data, certificate, extension, payload, algebra, native):
    word, R = data["word"], data["R"]
    A, T = certificate["compensation_ports"], certificate["query_ports"]
    K = [{k: R[k][p] / 4 for k in range(8) if p in R[k]} for p in range(112)]
    P = [row.copy() if p in A else {} for p, row in enumerate(K)]
    L = [{p: value for p, value in row.items() if p in T} for row in R]
    values = ordered_instance(R, K, P, L, algebra)
    require(values["J"] == data["J"] and values["M"] == [{k: Q(14)} for k in range(8)],
            "The ordered theorem is not bound to the actual supplier")
    require(set(payload["matrices"]) == {"R", "K", "P", "L", "Q", "Z", "G", "G_inverse", "JG_minus_I"},
            "The matrix certificate inventory changed")
    for name, rows in payload["matrices"].items():
        require(name in values and algebra.decode(rows) == values[name], "A producer matrix differs from the independent derivation")
    G, inverse, correction = [values[name] for name in ("G", "G_inverse", "JG_minus_I")]
    require([p for p, row in enumerate(correction) if row] == A,
            "The correction does not have exactly the selected eight rows")
    require(all(Counter(abs(value) for value in correction[p].values()) == {Q(14): 1, Q(7): 48, Q(1, 2): 4}
                for p in A), "A selected correction coefficient ledger differs")
    require(sum(row.get(p, 0) for p, row in enumerate(values["projection"])) == 16,
            "The exact section projection has the wrong dimension")
    power, identity_powers = identity(112), []
    for step in range(1, 7):
        power = algebra.multiply(G, power)
        if power == identity(112):
            identity_powers.append(step)
    require(identity_powers == [6], "The actual source code does not have exact order six")
    blocks, programs = payload["blocks"], payload["programs"]
    require(set(blocks) == {"backward_input", "source_G", "source_G_inverse", "forward_source", "forward_output"}
            and set(programs) == {"backward", "forward"}, "The unit-transfer block inventory changed")
    initial, owned_identity = identity(712), identity(712)
    owned_identity[704] = {}
    for name, bank, matrix, queries in (("source_G", 112, G, values["Q"]),
                                        ("source_G_inverse", 112, inverse, R),
                                        ("forward_source", 0, inverse, R)):
        expected = [row.copy() for row in owned_identity]
        expected[bank:bank + 112] = [{bank + j: value for j, value in row.items()} for row in matrix]
        require(algebra.forward(blocks[name], initial) == expected
                and algebra.transpose(algebra.adjoint(blocks[name]), 712) == expected,
                "A complete source word differs on a formal input column")
        source_queries(blocks[name], bank, queries, algebra)
        require(scalar_bill(blocks[name], algebra)["real_primitives"] == 9056, "A complete source invoice changed")
    a, b = blocks["source_G"], blocks["source_G_inverse"]
    require(algebra.transpose(algebra.adjoint(a + b), 712) == owned_identity
            and algebra.transpose(algebra.adjoint(b + a), 712) == owned_identity,
            "A literal source inverse order fails")
    require(algebra.transpose(algebra.adjoint(a * 6), 712) == owned_identity,
            "Six literal source words do not restore the complete source")
    full = word["final"][0]
    require(word["final"][:112] == [full] * 112, "The source lacks its common FULL output frame")
    receipts = {}
    for orientation in ("backward", "forward"):
        core = data["clean_programs"][orientation]
        program = programs[orientation]
        before = blocks["backward_input"] + [["phase", "unit_transfer_source_G"]] + blocks["source_G"]
        after = [["phase", "unit_transfer_source_G_inverse"]] + blocks["forward_source"] + blocks["forward_output"]
        require(program == (before + core if orientation == "backward" else core + after),
                "A retained event or its boundary placement changed")
        added = before if orientation == "backward" else after
        require(boundary_frames(added, word, A, orientation == "forward", algebra) == A,
                "The eight native boundary copies changed")
        base_profile = algebra.frame_check_core(core, word)
        profile = base_profile + Counter({1: 8})
        require(profile == Counter({1: 2420, 2: 418, 3: 432, 4: 142, 5: 82}), "The complete native profile changed")
        expected = identity(712)
        if orientation == "backward":
            for p in range(112):
                expected[p][112 + p] = Q(-1)
                expected[112 + p] = {112 + j: value for j, value in G[p].items()}
        else:
            expected[:112] = [row.copy() for row in inverse]
            for p in range(112):
                algebra.plus(expected[112 + p], inverse[p])
        expected[704:] = [{} for _ in range(8)]
        require(algebra.forward(program, initial) == expected
                and algebra.transpose(algebra.adjoint(program), 712) == expected,
                "A full unit-transfer word differs on an arbitrary input column")
        require(expected[224:704] == initial[224:704], "An arbitrary helper changed")
        target_block = blocks["backward_input" if orientation == "backward" else "forward_output"]
        require(scalar_bill(target_block, algebra)["real_primitives"] == 6704, "The selected target invoice changed")
        bill = scalar_bill(program, algebra)
        require(bill == {"real_primitives": 217898, "operations": {"add": 20694, "clear": 48, "scale": 707}},
                "The literal full scalar invoice changed")
        bound = prefix_bound(program, algebra)
        require(bound["ceiling_log2"] == (100 if orientation == "backward" else 86), "The formal scalar prefix bound changed")
        missing = [event for event in added if event[0] not in ("unit_transfer_input_line", "unit_transfer_exit_line")]
        rejected = False
        try:
            boundary_frames(missing, word, A, orientation == "forward", algebra)
        except ValueError:
            rejected = True
        require(rejected, "A missing boundary native line was not rejected")
        if orientation == "backward":
            source = blocks["source_G"]
            last_clear = max(i for i, event in enumerate(source) if event[1][0] == "clear")
            reverse_factors = source[last_clear + 1:] + source[:last_clear + 1]
            bad_words = [source + core, blocks["backward_input"] + core + source,
                         blocks["backward_input"] + reverse_factors + core]
        else:
            source, target = blocks["forward_source"], blocks["forward_output"]
            bad_words = [core + source, source + core + target, core + target + source]
            require(algebra.forward(program[:-1], initial)[704], "The final CLEAR is not necessary")
        require(all(algebra.transpose(algebra.adjoint(bad), 712) != expected for bad in bad_words),
                "An omitted correction or chronological mutation was not detected")
        receipts[orientation] = {"formal_input_columns": 712, "arbitrary_helpers_restored": 480,
                                 "private_outputs_zero": 8, "existing_owned_private_fields_used": 1,
                                 "new_fields": 0, "added_rank_one_children": 8, "added_monomial_maps": 16,
                                 "complete_native_profile": dict(sorted(profile.items())), "native_mass": 5530,
                                 "complete_scalar_invoice": bill, "formal_scalar_prefix_bound": bound,
                                 "missing_native_line_control": True, "chronology_and_missing_correction_controls": True}
    restored = identity(712)
    restored[704:] = [{} for _ in range(8)]
    require(algebra.transpose(algebra.adjoint(programs["backward"] + programs["forward"]), 712)
            != restored, "The forward companion was treated as the inverse backward call")
    ring = ring_checks(algebra)
    ring["noncentral_M"] = [{str(j): str(value) for j, value in row.items()} for row in ring["noncentral_M"]]
    return {"status": "PASS_EXACT_UNIT_TRANSFERS", "source_order": 6,
            "source_section_dimension": 16, "fixed_source_complement_dimension": 96,
            "literal_source_inverse_orders": True, "literal_sixth_power": True,
            "general_ring_examples_and_controls": ring, "words": receipts,
            "new_exit_native_checks": check_exit_native(data, certificate, extension, native),
            "scope": "Exact local B/F companions and fixed-chart source code. Routed controller closure, endpoint decoding, recursive hosting, full precision and kappa remain open."}
