#!/usr/bin/env python3
"""Check the exact premises of the R480 boundary theorem and its limits."""
# SPDX-License-Identifier: Apache-2.0
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
PREFIX = "candidate/strict/global/base/providers/gauge44/"
ORDINARY = 704
SOURCES = 112
HELPERS = range(224, ORDINARY)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def identity(n):
    return [{i: Q(1)} for i in range(n)]


def scalar_matrix(gates, n=ORDINARY):
    rows = identity(n)
    for gate in gates:
        if gate[0] == "add":
            _, target, source, numerator, denominator, _ = gate
            require(target != source, "self addition")
            coefficient = Q(numerator, denominator)
            for column, value in rows[source].items():
                total = rows[target].get(column, Q(0)) + coefficient * value
                if total:
                    rows[target][column] = total
                else:
                    rows[target].pop(column, None)
        elif gate[0] == "scale":
            _, target, numerator, denominator, _ = gate
            coefficient = Q(numerator, denominator)
            require(coefficient != 0, "singular scale")
            rows[target] = {j: coefficient * x for j, x in rows[target].items()}
        else:
            raise ValueError("unknown cleanup gate")
    return rows


def inverse_gates(gates):
    result = []
    for gate in reversed(gates):
        item = list(gate)
        if item[0] == "add":
            item[3] = -item[3]
        else:
            item[2], item[3] = item[3], item[2]
        result.append(item)
    return result


def transpose(rows):
    out = [{} for _ in rows]
    for i, row in enumerate(rows):
        for j, value in row.items():
            out[j][i] = value
    return out


def multiply(left, right):
    out = []
    for row in left:
        values = {}
        for middle, a in row.items():
            for column, b in right[middle].items():
                values[column] = values.get(column, Q(0)) + a * b
        out.append({j: value for j, value in values.items() if value})
    return out


def emitted_cleanup(events):
    gates = []
    active = False
    for event in events:
        if event[0] == "phase":
            active = event[1] == "full_frame_cleanup"
        elif active and event[0] == "scalar":
            op = event[1]
            operands = op[1:3] if op[0] == "add" else op[1:2]
            require(all(register[0] == "L" for register in operands), "private cleanup operand")
            if op[0] == "add":
                gates.append(["add", op[1][1], op[2][1], op[3], op[4], event[2]])
            elif op[0] == "scale":
                gates.append(["scale", op[1][1], op[2], op[3], event[2]])
            else:
                raise ValueError("singular cleanup operation")
    return gates


def wire(register):
    bank, index = register
    require(bank in ("L", "C"), "unknown register bank")
    return index if bank == "L" else ORDINARY + index


def dyadic_replay(events, omitted=None):
    """Use integer row numerators and one power-of-two denominator per row."""
    rows = [({i: 1}, 0) for i in range(712)]
    before_cleanup = None
    for position, event in enumerate(events):
        if event == ["phase", "full_frame_cleanup"]:
            before_cleanup = [(dict(row), exponent) for row, exponent in rows]
        if event[0] != "scalar" or position == omitted:
            continue
        op = event[1]
        target = wire(op[1])
        if op[0] == "clear":
            rows[target] = ({}, 0)
        elif op[0] == "copy":
            row, exponent = rows[wire(op[2])]
            rows[target] = (dict(row), exponent)
        elif op[0] in ("add", "scale"):
            source = wire(op[2]) if op[0] == "add" else target
            numerator, denominator = op[-2:]
            if denominator < 0:
                numerator, denominator = -numerator, -denominator
            require(denominator > 0 and denominator & (denominator - 1) == 0, "non-dyadic gate")
            row, exponent = rows[source]
            extra = denominator.bit_length() - 1
            if op[0] == "scale":
                rows[target] = ({j: numerator * value for j, value in row.items()}, exponent + extra)
            else:
                dst, old = rows[target]
                new = max(old, exponent + extra)
                total = {j: value << (new - old) for j, value in dst.items()}
                for j, value in row.items():
                    total[j] = total.get(j, 0) + numerator * (value << (new - exponent - extra))
                rows[target] = ({j: value for j, value in total.items() if value}, new)
        else:
            raise ValueError("unknown scalar operation")
    def convert(data):
        return [{j: Q(value, 1 << exponent) for j, value in row.items()} for row, exponent in data]
    require(before_cleanup is not None, "missing cleanup boundary")
    return convert(rows), convert(before_cleanup)


def profile(indices, final):
    return {str(rank): count for rank, count in sorted(Counter(final[i]["rank"] for i in indices).items())}


def rejection(function, text):
    try:
        function()
    except ValueError as error:
        require(text in str(error), "control failed for another reason")
    else:
        raise ValueError("control was not rejected: " + text)


def transported_scale(cleanup, inverse, helper, scale):
    changed = [dict(row) for row in inverse]
    changed[helper] = {j: scale * value for j, value in changed[helper].items()}
    return multiply(cleanup, changed)


def fixes_source_axes(matrix):
    return all(matrix[i].get(s, Q(0)) == (1 if i == s else 0)
               for i in range(ORDINARY) for s in range(SOURCES))


def covariance_components(inverse, helpers):
    """Find all block-output covariances of the backward cleanup."""
    adjacency = {h: set() for h in helpers}
    adjacency[-1] = set()
    blocks = {}
    for name, output_rows in (("physical_X", set(range(SOURCES))), ("helpers", set(helpers))):
        vectors = {j: {i: x for i, x in inverse[j].items() if i in output_rows}
                   for j in list(range(SOURCES)) + helpers}
        pivots, selected = {}, []

        def coordinates(vector):
            row, result = dict(vector), {}
            for pivot, (basis, representation) in sorted(pivots.items()):
                factor = row.get(pivot, Q(0))
                if not factor:
                    continue
                for i, value in basis.items():
                    value = row.get(i, Q(0)) - factor * value
                    if value:
                        row[i] = value
                    else:
                        row.pop(i, None)
                for i, value in representation.items():
                    value = result.get(i, Q(0)) + factor * value
                    if value:
                        result[i] = value
                    else:
                        result.pop(i, None)
            return row, result

        for j, vector in vectors.items():
            row, coefficients = coordinates(vector)
            if row:
                pivot = min(row)
                scale = row[pivot]
                number = len(selected)
                selected.append(j)
                representation = {i: -value / scale for i, value in coefficients.items()}
                representation[number] = Q(1) / scale
                pivots[pivot] = ({i: value / scale for i, value in row.items()}, representation)
        require(len(selected) == len(output_rows), "output projection does not have full row rank")
        expansions = {}
        for h in helpers:
            remainder, coefficients = coordinates(vectors[h])
            require(not remainder, "column outside output basis")
            rebuilt = {}
            for number, coefficient in coefficients.items():
                for i, value in vectors[selected[number]].items():
                    rebuilt[i] = rebuilt.get(i, Q(0)) + coefficient * value
                other = -1 if selected[number] < SOURCES else selected[number]
                adjacency[h].add(other)
                adjacency[other].add(h)
            require({i: value for i, value in rebuilt.items() if value} == vectors[h], "column expansion")
            expansions[str(h)] = {str(selected[number]): str(value) for number, value in sorted(coefficients.items())}
        blocks[name] = {"basis_columns": selected, "fixed_anchor_rank": sum(j < SOURCES for j in selected),
                        "helper_column_expansions": expansions}
    reached, queue = {-1}, [-1]
    for h in queue:
        for other in sorted(adjacency[h] - reached):
            reached.add(other)
            queue.append(other)
    free = []
    for h in helpers:
        if h in reached:
            continue
        component = [h]
        reached.add(h)
        for other in component:
            for neighbor in sorted(adjacency[other] - reached):
                reached.add(neighbor)
                component.append(neighbor)
        free.append(sorted(component))
    return {"blocks": blocks, "free_components": free,
            "forced_helpers": sorted(set(helpers) - {h for component in free for h in component})}


def binary_span(vectors):
    pivots = {}
    for vector in vectors:
        while vector:
            pivot = vector.bit_length() - 1
            if pivot in pivots:
                vector ^= pivots[pivot]
            else:
                pivots[pivot] = vector
                break
    return sorted(pivots.values(), reverse=True)


def covariance_constraints(cleanup, inverse, helpers, components):
    """Check the dimension by direct off-block equations, without column bases."""
    left, right = transpose(inverse), transpose(cleanup)
    equations = {}
    block = lambda i: 0 if i < SOURCES else 1 if i < 2 * SOURCES else 2
    for i, row in enumerate(left):
        for h in helpers:
            if h not in row:
                continue
            for j, value in right[h].items():
                if block(i) != block(j):
                    equation = equations.setdefault((i, j), {})
                    equation[h] = row[h] * value
    pivots = {}
    for equation in equations.values():
        for component in components:
            require(sum(equation.get(h, Q(0)) for h in component) == 0, "free component violates off-block equation")
        row = dict(equation)
        while row:
            pivot = min(row)
            factor = row[pivot]
            if pivot not in pivots:
                pivots[pivot] = {j: x / factor for j, x in row.items()}
                break
            for j, value in pivots[pivot].items():
                value = row.get(j, Q(0)) - factor * value
                if value:
                    row[j] = value
                else:
                    row.pop(j, None)
    require(len(pivots) + len(components) == len(helpers), "covariance nullity")
    return {"off_block_equations": len(equations), "rank": len(pivots), "nullity": len(components)}


def covariance_native_evidence(word, cleanup, inverse, final, covariance, hosted):
    left, right = transpose(inverse), transpose(cleanup)
    components = covariance["free_components"]
    evidence, target_modes = [], []
    for component in components:
        middle = [dict(row) if i in component else {} for i, row in enumerate(right)]
        projector = multiply(left, middle)
        item = {"helpers": component, "omitted_ranks": [final[h]["rank"] for h in component], "modes": {}}
        for name, indices in (("physical_X", range(SOURCES)), ("helpers", HELPERS)):
            rows = {i: projector[i] for i in indices if projector[i]}
            if not rows:
                item["modes"][name] = {"rank": 0}
                continue
            p = next(i for i in rows if rows[i].get(i))
            v = rows[p]
            u = {i: row[p] / v[p] for i, row in rows.items() if row.get(p)}
            require(sum(u.get(j, Q(0)) * value for j, value in v.items()) == 1, "projector pairing")
            require(rows == {i: {j: value * u[i] for j, value in v.items()} for i in u}, "rank-one projector")
            mode = {"rank": 1, "pivot": p, "u": {str(i): str(x) for i, x in u.items()},
                    "v": {str(i): str(x) for i, x in v.items()},
                    "basis_and_inverse_adds": 2 * (len(u) + len(v) - 2),
                    "basis_and_inverse_scales": 0 if v[p] == 1 else 2}
            item["modes"][name] = mode
            if name == "physical_X":
                target_modes.append((u, v))
        require(item["modes"]["physical_X"]["rank"] == 1, "missing target response")
        if len(component) == 2:
            frames = [word["frames"][final[h]["from"]] for h in component]
            union = binary_span(frames[0] + frames[1])
            require([len(frame) for frame in frames] == [4, 7] and len(union) == 8, "pair frame dimensions")
            require(item["modes"]["helpers"]["rank"] == 1, "missing helper response")
            item["monotone_partial_tail"] = {"sum_frame": union, "intersection_rank": 3,
                "prefix_ranks": [4, 1], "target_repair_rank": 1, "helper_tail_rank": 1}
        else:
            require(item["omitted_ranks"] == [5] and item["modes"]["helpers"]["rank"] == 0, "singleton response")
            item["direct_target_repair_rank"] = 5
        evidence.append(item)
    for i, (_, v) in enumerate(target_modes):
        for j, (u, _) in enumerate(target_modes):
            require(sum(v.get(k, Q(0)) * x for k, x in u.items()) == (1 if i == j else 0), "independent target modes")
    slots = hosted["hosting"]["pooled_slots"]
    owned = {(p["family"], p["child"]) for p in slots}
    remainder = {(p["family"], p["child"]): p["rank"] for p in hosted["idle_children"]}
    slot_map = {(p["time"], p["helper"]): p for p in slots}
    ranks = Counter(remainder.get((p["family"], p["child"]), 0) for p in slots)
    require(set(ranks) == {0, 1, 3, 7}, "hosted remainder ranks")
    rank48 = [p for p in hosted["idle_children"] if p["rank"] == 48]
    require(len(rank48) == 4866 and all((p["family"], p["child"]) not in owned for p in rank48), "rank-48 owner exclusion")
    affected = Counter()
    for call in hosted["calls"]:
        if call["orientation"] != "backward":
            continue
        for item in evidence:
            if len(item["helpers"]) != 2:
                continue
            values = []
            for h in item["modes"]["helpers"]["u"]:
                slot = slot_map[call["time"], int(h) - 224]
                values.append(remainder.get((slot["family"], slot["child"]), 0))
            affected[tuple(values)] += 1
    require(sum(affected.values()) == 192 and all(set(key) <= {0, 1} for key in affected), "affected owner remainders")
    return {"components": evidence, "independent_target_modes": len(target_modes),
            "direct_off_block_rank": covariance_constraints(cleanup, inverse, sorted(final), components),
            "one_tail_cost_screen": {"baseline_ranks": [5, 2], "replacement_local_ranks": [4, 1, 1],
                "deferred_helper_rank": 1, "host_ranks_with_strictly_worse_moment": list(range(9)),
                "uniform_b_range": "0 < b < 1", "native_child_max_rank": max(map(int, word["local_profile"])),
                "all_hosted_remainder_ranks": {str(r): n for r, n in sorted(ranks.items())},
                "unhosted_rank48_children": len(rank48),
                "affected_pair_remainder_patterns": [{"ranks": list(key), "instances": n} for key, n in sorted(affected.items())],
                "not_covered": "Joint multi-call encodings, changed owners, or changed native cleanup maps."}}


def load_inputs():
    pins = json.loads((PACKAGE / "SOURCES.json").read_text())
    for item in pins["files"]:
        if item["usage"] == "input":
            actual = hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest()
            require(actual == item["sha256"], "source digest: " + item["path"])
    members = {}
    with tarfile.open(ROOT / ARCHIVE) as archive:
        for name, expected in pins["archive_members"].items():
            raw = archive.extractfile(PREFIX + name).read()
            require(hashlib.sha256(raw).hexdigest() == expected, "archive member digest")
            members[name] = json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)
        item = pins["hosted_archive_member"]
        raw = archive.extractfile(item["path"]).read()
        require(hashlib.sha256(raw).hexdigest() == item["sha256"], "hosted archive member digest")
        members["HOSTED"] = json.loads(gzip.decompress(raw))
    return members


def calculate():
    data = load_inputs()
    word = data["CANONICAL-WORD.json.gz"]
    programs = data["LOCAL-PROGRAMS.json.gz"]
    require((word["v"], word["R"], word["h"]) == (112, 480, 9), "wrong supplier")
    require(all(gate[-1] == 1 for gate in word["cleanup"]), "cleanup is not in the FULL frame")
    climbs = {direction: [event for event in events if event[0] == "climb"]
              for direction, events in programs.items()}
    require(climbs["forward"] == climbs["backward"] and len(climbs["forward"]) == 3486, "shared-word climb coupling")
    cleanup = scalar_matrix(word["cleanup"])
    inverse = scalar_matrix(inverse_gates(word["cleanup"]))
    require(multiply(cleanup, inverse) == identity(ORDINARY), "cleanup right inverse")
    require(multiply(inverse, cleanup) == identity(ORDINARY), "cleanup left inverse")
    matrices = {"forward": cleanup, "backward": transpose(inverse)}
    final = {}
    for direction, events in programs.items():
        require(scalar_matrix(emitted_cleanup(events)) == matrices[direction], "emitted cleanup map")
        current = {event[2]: {"from": event[3], "to": event[4], "rank": event[5]}
                   for event in events if event[:2] == ["climb", "final"] and event[2] in HELPERS}
        for item in current.values():
            require(item["to"] == 1 and item["rank"] == len(word["frames"][1]) - len(word["frames"][item["from"]]), "final rank")
        if final:
            require(current == final, "directional final climbs")
        final = current
        endpoint, prefix = dyadic_replay(events)
        expected = identity(712)
        for i in range(SOURCES):
            target, source, sign = (i + SOURCES, i, 1) if direction == "forward" else (i, i + SOURCES, -1)
            expected[target][source] = Q(sign)
        for i in range(ORDINARY, 712):
            expected[i] = {}
        require(endpoint == expected, "full 712-coordinate scalar endpoint")
        if direction == "forward":
            for i in range(ORDINARY):
                if SOURCES <= i < 2 * SOURCES:
                    continue
                require({j: x for j, x in prefix[i].items() if j < SOURCES} ==
                        {j: x for j, x in inverse[i].items() if j < SOURCES}, "independent source-column replay")
    require(len(final) == 402, "final helper inventory")
    nonfinal = sorted(set(HELPERS) - set(final))
    require(len(nonfinal) == 78, "non-final helper inventory")
    for h in nonfinal:
        require(cleanup[h] == {h: Q(1)} and inverse[h] == {h: Q(1)}, "non-final helper cleanup row")
        require(all(not row.get(h) for i, row in enumerate(cleanup) if i != h), "non-final helper cleanup column")
        require(all(not row.get(h) for i, row in enumerate(inverse) if i != h), "non-final helper inverse column")
    witnesses = []
    for helper in sorted(final):
        columns = sorted(j for j in inverse[helper] if j < SOURCES)
        require(columns, "helper has no source witness")
        source = columns[0]
        witnesses.append({"helper": helper, "source": source, "coefficient": str(inverse[helper][source]), **final[helper]})
    visible = {direction: sorted(h for h in final if any(matrix[s].get(h) for s in range(SOURCES)))
               for direction, matrix in matrices.items()}
    survivors = {direction: sorted(set(final) - set(indices)) for direction, indices in visible.items()}
    require(len(visible["forward"]) == 61 and not survivors["backward"], "source-dependent boundary classification")
    covariance = covariance_components(inverse, sorted(final))
    free_helpers = [h for component in covariance["free_components"] for h in component]
    require(len(free_helpers) == 22 and len(covariance["free_components"]) == 19, "backward target-covariance class")
    covariance["free_profile"] = profile(free_helpers, final)
    covariance["free_mass"] = sum(final[h]["rank"] for h in free_helpers)
    covariance["native_ranks_and_cost"] = covariance_native_evidence(word, cleanup, inverse, final, covariance, data["HOSTED"])
    require(covariance["native_ranks_and_cost"]["one_tail_cost_screen"]["native_child_max_rank"] == 8, "local child rank cap")
    for i in range(SOURCES, 2 * SOURCES):
        require(cleanup[i] == {i: Q(1)} and inverse[i] == {i: Q(1)}, "target cleanup row")
        require(all(not row.get(i) for j, row in enumerate(cleanup) if j != i), "target cleanup column")
    defects = []
    for witness in witnesses:
        h, s = witness["helper"], witness["source"]
        column = {i: row[h] * inverse[h][s] for i, row in enumerate(cleanup) if h in row}
        require(column, "zero omission defect")
        defects.append({"helper": h, "source": s, "nonzero_output_rows": len(column),
                        "source_rows_changed": sum(i < SOURCES for i in column)})
    controls = []
    bad = [dict(row) for row in inverse]
    bad[witnesses[0]["helper"]].pop(witnesses[0]["source"])
    rejection(lambda: require(multiply(cleanup, bad) == identity(ORDINARY), "inverse mismatch"), "inverse mismatch")
    controls.append("removed_source_coefficient_rejected")
    h = survivors["forward"][0]
    source = min(j for j in inverse[h] if j < SOURCES)
    escape = transported_scale(cleanup, inverse, h, Q(2))
    require(all(escape[s] == {s: Q(1)} for s in range(SOURCES)), "escape changes source outputs")
    require(any(row.get(source) for row in escape[224:]), "escape lacks source history")
    controls.append("source_dependent_forward_escape_attained")
    rejection(lambda: require(fixes_source_axes(escape), "source-independent boundary defect"), "source-independent boundary defect")
    controls.append("nonidentity_forward_frame_rejected_by_source_independence")
    backward_defect = transported_scale(matrices["backward"], transpose(cleanup), h, Q(2))
    rejection(lambda: require(all(backward_defect[s] == {s: Q(1)} for s in range(SOURCES)), "backward physical-X target defect"), "backward physical-X target defect")
    controls.append("same_frame_rejected_by_backward_physical_X_target_outputs")
    first_free = covariance["free_components"][0]
    changed = [dict(row) for row in transpose(cleanup)]
    for helper in first_free:
        changed[helper] = {j: 2 * value for j, value in changed[helper].items()}
    output = multiply(matrices["backward"], changed)
    for i, row in enumerate(output):
        block = 0 if i < SOURCES else 1 if i < 2 * SOURCES else 2
        require(all((0 if j < SOURCES else 1 if j < 2 * SOURCES else 2) == block for j in row), "target covariance mixes blocks")
    require(any(output[i] != {i: Q(1)} for i in range(SOURCES)), "target covariance control is trivial")
    controls.append("backward_target_covariance_escape_attained")
    unequal = transported_scale(matrices["backward"], transpose(cleanup), first_free[0], Q(2))
    rejection(lambda: require(all(not value for i, row in enumerate(unequal) for j, value in row.items()
                                  if (i < SOURCES) != (j < SOURCES)), "unequal paired frame mixes target and helpers"),
              "unequal paired frame mixes target and helpers")
    controls.append("unequal_paired_frame_rejected_by_output_block_contract")
    ended = next(h for h in HELPERS if h not in final and cleanup[h] == {h: Q(1)} and inverse[h] == {h: Q(1)})
    require(all(not row.get(ended) for i, row in enumerate(cleanup) if i != ended), "low-end isolation")
    controls.append("isolated_existing_low_end_can_carry_a_frame")
    first_clear = next(i for i, event in enumerate(programs["backward"])
                       if event[0] == "scalar" and event[1] == ["clear", ["C", 0]])
    dirty, _ = dyadic_replay(programs["backward"], omitted=first_clear)
    require(any(row.get(ORDINARY) for row in dirty[:ORDINARY]), "private-input control did not fail")
    controls.append("omitted_private_clear_detected_on_private_column")
    assembly = json.loads((ROOT / "research/community-frontier1094-audit/ASSEMBLY.json").read_text())
    local = {str(k): v for k, v in sorted((int(k), v) for k, v in word["local_profile"].items())}
    require(sum(int(r) * count for r, count in local.items()) == 5586, "local rank mass")
    require(assembly["provider_counts"] == {"gauge44": 144}, "selected call count")
    return {"status": "PASS_R480_SOURCE_INDEPENDENT_CLEANUP", "coordinates": 712,
            "cleanup_macros": len(word["cleanup"]), "cleanup_nonzeros": sum(map(len, cleanup)),
            "inverse_nonzeros": sum(map(len, inverse)), "final_helpers": len(final),
            "final_helper_profile": profile(final, final),
            "final_helper_mass": sum(item["rank"] for item in final.values()),
            "shared_word_identical_directional_climbs": len(climbs["forward"]),
            "isolated_nonfinal_helpers": nonfinal,
            "inverse_source_witnesses": witnesses, "rank_one_defects": defects,
            "source_dependent_survivors": {direction: {"helpers": indices, "profile": profile(indices, final),
                "mass": sum(final[h]["rank"] for h in indices)} for direction, indices in survivors.items()},
            "backward_separate_target_covariance": covariance,
            "source_dependent_escape": {"helper": h, "source": source, "coefficient": str(inverse[h][source])},
            "existing_low_end_control": ended, "negative_and_boundary_controls": controls,
            "private_clear_control_event": first_clear,
            "accounting": {"local_profile": local, "local_mass": 5586, "calls": 144,
                "global_profile": assembly["complex_profile"], "complex_lower": assembly["complex_lower"],
                "bit_lower": assembly["bit_lower"], "kappa": assembly["kappa"],
                "deferred_climbs_in_theorem_class": 0, "new_kappa": False}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", action="store_true")
    args = parser.parse_args()
    result = calculate()
    path = PACKAGE / "CERTIFICATE.json"
    if args.write_certificate:
        path.write_text(json.dumps(result, indent=2) + "\n")
    else:
        require(result == json.loads(path.read_text()), "certificate mismatch")
    print("PASS_R480_SOURCE_INDEPENDENT_CLEANUP helpers=402 mass=732 columns=712 forward_history_survivors=341 backward_canonical_history_survivors=0 backward_target_covariance_helpers=22 no_new_kappa")


if __name__ == "__main__":
    main()
