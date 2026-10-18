# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls on actual peer events and native classes, plus graph oracles.

Substantial OpenAI Codex assistance. These mutants deliberately bypass source
hashes to exercise semantic checks; they are not defects in the frozen word.
"""
import copy


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def rejects(name, callback, reason=None):
    try:
        callback()
    except (ValueError, KeyError) as exc:
        require(reason is None or reason in str(exc), "wrong rejection guard for " + name + ": " + str(exc))
        return {"name": name, "status": "EXPECTED_SEMANTIC_REJECTION", "reason": str(exc)}
    raise ValueError("accepted behavioral mutant: " + name)


def direct_projection(events):
    result, phase, clock = [], None, 0
    for event in events:
        tag = event[0]
        if tag == "phase":
            phase, clock = event[1], 0
            continue
        if tag == "scalar":
            op = event[1]
            roles = op[1:3] if op[0] in ("add", "copy") else op[1:2]
        elif tag in ("climb", "adapter", "residual_adapter", "zero_buffer"):
            roles = event[2:3]
        elif tag == "warp":
            roles = event[1:2]
        else:
            roles = []
        if set(roles) & {"L249", "Z249"}:
            result.append([phase, clock, event])
        if tag == "scalar":
            clock += 1
    return result


def source_controls(modules, data, events, included):
    source, cone = modules["source"], modules["cone"]
    word, can, program = data["word"], data["canonical_word"], data["programs"]["forward"]
    changed = copy.deepcopy(can)
    changed["warps"][0]["G_columns"][0] ^= changed["warps"][0]["G_columns"][1]
    result = [rejects("changed_peer_G_same_ID_and_events", lambda: source.bind_metadata(word, changed), "source-bound warp matrix")]
    kept, _, final, _ = source.metadata(word)
    for mode in ("literal_nonFULL", "post_exit_target_reused_at_FULL"):
        altered = copy.deepcopy(word)
        altered["cleanup"][0][1] = 112
        altered["cleanup"][0][-1] = list(final["L112"]) if mode == "literal_nonFULL" else list(source.FULL)
        trace = source.SourceTrace(altered, False)
        trace.entries()
        trace.current = dict(final)
        reason = "cleanup declared FULL" if mode == "literal_nonFULL" else "cleanup L operand has FULL"
        result.append(rejects(mode, trace.finish, reason))
    late = copy.deepcopy(events)
    free = next(i for i, e in enumerate(late) if e == ["zero_buffer", "free", "Z249"])
    late.insert(free + 1, ["scalar", ["add", "Z249", "L0", 1, 1], source.FULL])
    result.append(rejects("private_write_after_free", lambda: cone.records(late, ["L" + str(r) for r in kept]), "live private role"))
    result.append(peer_reorder(modules, data, events, included))
    result.append(center_geometry(source, word))
    return result


def center_geometry(source, word):
    chosen = None
    for k, (r, frame) in enumerate(zip(word["centers"], word["center_frames"])):
        terms = [g for g in word["cut"] if g[2] == r]
        if 1 < len(frame) < 9 and terms:
            chosen = (k, r, frame, terms)
            break
    require(chosen is not None, "derived nontrivial center geometry fixture")
    k, r, frame, terms = chosen
    positive = copy.deepcopy(word)
    positive.update(centers=[r], center_frames=[frame], cut=terms)
    target = terms[0][1]
    positive["target_levels"][str(target - 112)] = [frame[0]]
    good = center_trace(source, positive)
    good.centers()
    outside = next(x for x in range(1, 512) if len(source.basis([*frame, x])) > len(frame))
    altered = copy.deepcopy(positive)
    altered["target_levels"][str(target - 112)] = [outside]
    trace = center_trace(source, altered)
    result = rejects("derived_center_same_rank_nonnested_target", trace.centers, "nested center path")
    return dict(result, source_center_index=k, derived_center_only_fixture=True,
                positive_nested_path_pass=True, target_rank_both=1,
                positive_target_vector=frame[0], mutant_target_vector=outside)


def center_trace(source, word):
    levels = {112 + int(t): source.basis(f) for t, f in word["target_levels"].items()}
    trace = source.SourceTrace(word, False)
    trace.current.update({"L" + str(r): levels.get(r, ()) for r in range(112, 224)})
    trace.current.update({"L" + str(r): source.basis(f) for r, f in zip(word["centers"], word["center_frames"])})
    return trace


def peer_reorder(modules, data, events, included):
    source, native, kernel = modules["source"], modules["native"], modules["kernel"]
    can, program = data["canonical_word"], data["programs"]["forward"]
    for i in sorted(included):
        e = events[i]
        if e[0] != "warp" or e[1] in ("L249", "Z249") or i + 1 >= len(events):
            continue
        following = events[i + 1]
        if following[0] != "scalar" or following[1][0] != "add" or e[1] not in following[1][1:3]:
            continue
        if set(following[1][1:3]) & {"L249", "Z249"}:
            continue
        columns = can["warps"][abs(e[2]) - 1]["G_columns"]
        logical = native.warp(kernel, columns)
        if e[2] < 0:
            logical = kernel.adjoint(logical)
        reference = kernel.adjoint(kernel.canonical_frame(e[3])) + logical + kernel.canonical_frame(e[4])
        if kernel.same_operator(reference, []):
            continue
        changed = copy.deepcopy(program)
        changed[i], changed[i + 1] = changed[i + 1], changed[i]
        normalized = source.normalized(can, changed, source.metadata(data["word"])[0])
        require(source.identical(direct_projection(events), direct_projection(normalized)), "peer reorder preserves direct projection/clocks")
        result = rejects("peer_warp_crosses_noncommuting_ADD", lambda: source.bind(data["word"], can, changed, False), "complete source event mismatch")
        return dict(result, warp_event=i, add_event=i + 1, role=e[1], direct_projection_unchanged=True,
                    unary_operator_nonidentity_on_all_column_comparison=True)
    raise ValueError("no actual peer warp/ADD control found")


def phase_witness(kernel, candidate, reference):
    a, b = kernel.c_gates(candidate), kernel.c_gates(reference)
    total = max(a, b)
    beta = kernel.radix(total)
    left, right = kernel.run(candidate, beta), kernel.run(reference, beta)
    base, half = 1 << beta, 1 << (beta - 1)
    def digit(value):
        low = value & (base - 1)
        return low - base if low >= half else low
    for row in range(512):
        actual = [digit(side[row]) << (total - a) for side in left]
        expected = [digit(side[row]) << (total - b) for side in right]
        if actual != expected:
            return {"input_basis": 0, "output_row": row, "actual_Gaussian_numerator": actual,
                    "expected_Gaussian_numerator": expected, "denominator_power_of_two": total}
    raise ValueError("global phase mutant has no stated basis0 witness")


def native_controls(modules, data, events, included):
    native, kernel, audit = [modules[k] for k in ("native", "kernel", "audit")]
    can, recipes, adapters = data["canonical_word"], data["recipes"], data["adapters"]
    inventory = native.classes(events, included, can)
    key = next(k for k, indices in inventory.items() if k[0] == "child" and
               any(events[i][0] == "climb" and events[i][2] not in ("L249", "Z249") for i in indices))
    candidate, reference, record = native.selected(kernel, key, can, recipes, adapters)
    wrong = copy.deepcopy(record)
    wrong["left"]["phase"] = (wrong["left"]["phase"] + 1) % 4
    fixture = {"children": [wrong], "endpoint_adapters": [], "warps": []}
    first = rejects("actual_peer_child_wrong_global_phase", lambda: native.check(kernel, key, can, fixture, adapters, False), "exact native class mismatch")
    first.update(event_indices=inventory[key], class_key=list(key), witness=phase_witness(kernel, native.compiled(kernel, wrong), reference))
    changed = copy.deepcopy(record)
    changed["left"]["linear_Z4"][0] = (changed["left"]["linear_Z4"][0] + 2) % 4
    fixture2 = {"children": [changed], "endpoint_adapters": [], "warps": []}
    second = rejects("actual_peer_child_wrong_character", lambda: native.check(kernel, key, can, fixture2, adapters, False), "exact native class mismatch")
    payload = audit.identity_payload(candidate, reference, record, False)
    require(payload != audit.identity_payload(candidate, reference, wrong, False), "cache distinguishes selected phase")
    require(payload != audit.identity_payload(candidate, reference, record, True), "cache distinguishes dual orientation")
    return [first, second, dual_order_control(modules, data, inventory),
            {"name": "cache_same_local_ID_changed_phase_or_orientation", "status": "PASS_DISTINCT_EXACT_PAYLOADS"}]


def dual_order_control(modules, data, inventory):
    native, kernel = modules["native"], modules["kernel"]
    for key in inventory:
        if key[0] != "warp":
            continue
        candidate, _, _ = native.selected(kernel, key, data["canonical_word"], data["recipes"], data["adapters"])
        if not kernel.same_operator(native.conjugate(candidate), kernel.adjoint(candidate)):
            return {"name": "actual_peer_warp_dual_is_not_adjoint", "status": "EXPECTED_EXACT_OPERATOR_INEQUALITY",
                    "class_key": list(key), "columns_compared": 512}
    raise ValueError("no noncommuting actual warp distinguishes dual from adjoint")


def run(modules, data):
    source, cone, oracle = [modules[k] for k in ("source", "cone", "oracle")]
    graph = modules["graph_controls"].run(cone, oracle)
    events, metadata = source.bind(data["word"], data["canonical_word"], data["programs"]["forward"], False)
    records, initial = cone.records(events, metadata["start"])
    included = cone.reverse_demand(records, initial)["event_indices"]
    return {"status": "PASS_CLOSED_CONE_BEHAVIORAL_CONTROLS", "graph": graph,
            "source_and_lifetime": source_controls(modules, data, events, included),
            "native_and_cache": native_controls(modules, data, events, included),
            "mutants_bypass_hash_checks": True, "production_defect_claim": False}
