#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact bounded search for a two-center R439 restoration relay."""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = HERE.relative_to(ROOT).as_posix()
BASE = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
SELECTED_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
CATALOGUE_SHA256 = "d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7"
CANDIDATE_PATH = "research/r439-bsection-stars-seed01/candidate.json.gz"
XCHECK_PATH = "research/e8-bit-p111-tuned/code/xcheck_p.py"
PROFILE_EXPECTED = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def load_word():
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    source_pins = {row["path"]: row["sha256"] for row in sources["files"]}
    raw = (ROOT / CANDIDATE_PATH).read_bytes()
    need(sha256(raw) == source_pins[CANDIDATE_PATH], "pinned PR1062 word SHA-256 mismatch")
    need(sha256((ROOT / XCHECK_PATH).read_bytes()) == source_pins[XCHECK_PATH],
         "pinned owner-profile checker SHA-256 mismatch")
    for path, expected in (("certificates/selected-result.json", SELECTED_SHA256),
                           ("docs/research/agent-task-catalog.json", CATALOGUE_SHA256)):
        need(source_pins[path] == expected, f"{path} manifest pin mismatch")
        pinned = subprocess.run(
            ["git", "show", f"{BASE}:{path}"], cwd=ROOT,
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        need(sha256(pinned) == expected, f"{path} base-commit SHA-256 mismatch")
    return json.loads(gzip.decompress(raw).decode("utf-8"))


def stream(word):
    out = [("add", d, s) for section in ("D", "A")
           for _, d, sources in word[section] for s in sources]
    n = 2 * word["v"] + word["R"]
    temporary = n
    for j, center in enumerate(word["ret"]):
        out.append(("copy", temporary, center))
        out.extend(("add", word["v"] + i, temporary)
                    for i, row in enumerate(word["scatter"]) if j in row)
        out.append(("erase", temporary, center))
    out.extend(("add", d, s) for section in ("B", "C")
                for _, d, sources in word[section] for s in sources)
    return out


def flipped(kind):
    if kind == "copy":
        return "erase"
    if kind == "erase":
        return "copy"
    return kind


def linear_map(word, reverse=False):
    n = 2 * word["v"] + word["R"]
    rows = [1 << i for i in range(n)] + [0]
    instructions = stream(word)
    if reverse:
        instructions = [(flipped(kind), d, s)
                        for kind, d, s in reversed(instructions)]
    for kind, d, s in instructions:
        if kind == "add":
            rows[d] ^= rows[s]
        elif kind == "copy":
            need(rows[d] == 0, "COPY into a live temporary")
            rows[d] = rows[s]
        else:
            need(rows[d] == rows[s], "ERASE of a modified temporary")
            rows[d] = 0
    need(rows[-1] == 0, "temporary not erased")
    return rows[:-1]


def integer_bill(word):
    n = 2 * word["v"] + word["R"]
    ins = stream(word)
    peaks = []
    for reverse in (False, True):
        values = [1] * (n + 1)
        peak = 1
        ordered = ins
        if reverse:
            ordered = [(flipped(kind), d, s)
                       for kind, d, s in reversed(ins)]
        for kind, d, s in ordered:
            if kind == "add":
                values[d] += values[s]
            elif kind == "copy":
                values[d] = values[s]
            else:
                values[d] = 0
            peak = max(peak, values[d])
        peaks.append(peak)
    F, B = peaks
    local = 64 * (F ** 3) * (B ** 2)
    nine = (1 << 18) * (F ** 5) * (B ** 4)
    need(local < (1 << 104), "local precision guard failed")
    need(nine < (1 << 192), "nine-stage precision guard failed")
    return {
        "native_ADDs": sum(1 for kind, _, _ in ins if kind == "add"),
        "D_adds": sum(len(gate[2]) for gate in word["D"]),
        "A_adds": sum(len(gate[2]) for gate in word["A"]),
        "F": F,
        "B": B,
        "local_bits": local.bit_length(),
        "nine_stage_bits": nine.bit_length(),
    }


def frame_paths(word):
    frame_sets = [frozenset(frame) for frame in word["frames"]]
    paths = [[frame] for frame in word["start"]]
    for section in ("D", "A", "B", "C"):
        for frame, dest, sources in word[section]:
            for reg in (dest, *sources):
                if paths[reg][-1] != frame:
                    need(frame_sets[paths[reg][-1]] < frame_sets[frame],
                         "nonmonotone frame path")
                    paths[reg].append(frame)
    for reg, frame in enumerate(word["final"]):
        if paths[reg][-1] != frame:
            need(frame_sets[paths[reg][-1]] < frame_sets[frame],
                 "nonmonotone final frame path")
            paths[reg].append(frame)
    return paths


def owner_profile(word):
    checker_path = ROOT / XCHECK_PATH
    spec = importlib.util.spec_from_file_location("r439_pinned_xcheck", checker_path)
    need(spec is not None and spec.loader is not None, "cannot load pinned xcheck_p.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    W, _, fl, hypotheses, conclusions, _ = module.check(word)
    profile = Counter()
    for path in frame_paths(word):
        for a, b in zip(path, path[1:]):
            profile[W.fdim[b] - W.fdim[a]] += 1
    profile.update(row["rank"] for row in fl["totals"])
    result = {int(k): int(profile[k]) for k in sorted(profile)}
    mass = sum(k * count for k, count in result.items())
    return result, mass, hypotheses, conclusions


def terminal_restorations(word):
    half = len(word["D"]) // 2
    out = []
    for index, gate in enumerate(word["D"]):
        frame, dest, sources = gate
        if index >= half and dest >= 2 * word["v"] and len(sources) == 1:
            out.append((dest, sources[0], index))
    return out


def reciprocal_pairs(word, by_center):
    first = {}
    for center in by_center:
        for i, (_, dest, sources) in enumerate(word["A"]):
            if center in sources:
                first[center] = (i, dest, list(sources))
                break
    pairs = []
    for a, (i, c, sources) in first.items():
        if sources != [a] or c not in first:
            continue
        j, dest, other_sources = first[c]
        if i < j and dest == a and other_sources == [c]:
            pairs.append((a, c, i, j))
    return sorted(set(pairs))


def omit_edges(word, edges):
    result = copy.deepcopy(word)
    half = len(result["D"]) // 2
    indices = []
    for a, b in edges:
        matches = [i for i, gate in enumerate(result["D"])
                   if i >= half and gate[1] == a and gate[2] == [b]]
        need(len(matches) == 1, f"expected one terminal restoration {a}^{b}")
        indices.extend(matches)
    need(len(set(indices)) == len(indices), "duplicate restoration edge in omission set")
    for index in sorted(indices, reverse=True):
        result["D"].pop(index)
    return result, sorted(indices)


def capture_a_snapshots(word):
    n = 2 * word["v"] + word["R"]
    rows = [1 << i for i in range(n)]
    frames = list(word["start"])
    for frame, dest, sources in word["D"]:
        for source in sources:
            rows[dest] ^= rows[source]
        for reg in (dest, *sources):
            frames[reg] = frame
    snapshots = []
    for frame, dest, sources in word["A"]:
        snapshots.append((rows.copy(), frames.copy()))
        for source in sources:
            rows[dest] ^= rows[source]
        for reg in (dest, *sources):
            frames[reg] = frame
    return snapshots


def gf2_basis(vectors):
    pivots = {}
    for vector in vectors:
        value = vector
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return pivots


def in_basis(value, pivots):
    value = int(value)
    while value:
        pivot = value.bit_length() - 1
        if pivot not in pivots:
            return False
        value ^= pivots[pivot]
    return True


def solve_two(value, first, second):
    return {0: (0, 0), first: (1, 0), second: (0, 1),
            first ^ second: (1, 1)}.get(value)


def impulse_supports(word):
    instructions = stream(word)
    n = 2 * word["v"] + word["R"]
    supports = []
    for gate_index, (_, dest, _) in enumerate(word["A"]):
        offset = sum(len(gate[2]) for gate in word["D"])
        offset += sum(len(gate[2]) for gate in word["A"][:gate_index + 1])
        coefficients = [0] * (n + 1)
        coefficients[dest] = 1
        for kind, d, s in instructions[offset:]:
            if kind == "add":
                coefficients[d] ^= coefficients[s]
            elif kind == "copy":
                coefficients[d] = coefficients[s]
            else:
                coefficients[d] = 0
        supports.append(sum(1 << i for i, bit in enumerate(coefficients[:n]) if bit))
    return supports


def impulse_to_source(word, earlier_gate, later_gate, source):
    n = 2 * word["v"] + word["R"]
    coefficients = [0] * n
    coefficients[word["A"][earlier_gate][1]] = 1
    for gate_index in range(earlier_gate + 1, later_gate):
        _, dest, sources = word["A"][gate_index]
        for s in sources:
            coefficients[dest] ^= coefficients[s]
    return coefficients[source]


def source_actions(word, gate_index, target, snapshots):
    _, dest, existing = word["A"][gate_index]
    values, _ = snapshots[gate_index]
    by_value = defaultdict(list)
    for reg, value in enumerate(values):
        by_value[value].append(reg)
    actions = []
    for old in existing:
        if values[old] == target:
            actions.append(("remove", old, None, -1))
        for new in by_value.get(values[old] ^ target, []):
            if new != dest and new not in existing:
                actions.append(("replace", old, new, 0))
    for new in by_value.get(target, []):
        if new != dest and new not in existing:
            actions.append(("add", None, new, 1))
    unique = {}
    for action in actions:
        unique[action[:3]] = action
    return list(unique.values())


def interaction_parity(word, action, earlier_gate, later_gate):
    operation, old, new, _ = action
    if operation == "remove":
        return impulse_to_source(word, earlier_gate, later_gate, old)
    if operation == "add":
        return impulse_to_source(word, earlier_gate, later_gate, new)
    return (impulse_to_source(word, earlier_gate, later_gate, old)
            ^ impulse_to_source(word, earlier_gate, later_gate, new))


def apply_actions(word, edges, actions):
    result, _ = omit_edges(word, edges)
    by_gate = defaultdict(list)
    for gate_index, action in actions:
        by_gate[gate_index].append(action)
    for gate_index, gate_actions in by_gate.items():
        sources = set(result["A"][gate_index][2])
        for operation, old, new, _ in gate_actions:
            if operation == "remove":
                need(old in sources, "removing a missing source tap")
                sources.remove(old)
            elif operation == "add":
                need(new not in sources, "adding an existing source tap")
                sources.add(new)
            else:
                need(old in sources and new not in sources,
                     "invalid source replacement")
                sources.remove(old)
                sources.add(new)
        result["A"][gate_index][2] = sorted(sources)
    return result


def one_edge_control(word):
    result = copy.deepcopy(word)
    half = len(result["D"]) // 2
    matches = [i for i, gate in enumerate(result["D"])
               if i >= half and gate[1] == 514 and gate[2] == [367]]
    need(len(matches) == 1, "positive-control restoration pin")
    result["D"].pop(matches[0])
    need(result["A"][304][1] == 514, "positive-control A writer pin")
    result["A"][304][2] = [360]
    return result


def wrong_one_edge_control(word):
    result = copy.deepcopy(word)
    half = len(result["D"]) // 2
    matches = [i for i, gate in enumerate(result["D"])
               if i >= half and gate[1] == 514 and gate[2] == [367]]
    need(len(matches) == 1, "negative-control restoration pin")
    result["D"].pop(matches[0])
    result["A"][304][2] = [361]
    return result


def build_report(word):
    base_forward = linear_map(word)
    base_reverse = linear_map(word, reverse=True)
    base_paths = frame_paths(word)
    base_bill = integer_bill(word)
    base_profile, base_mass, _, _ = owner_profile(word)
    need(base_profile == PROFILE_EXPECTED and base_mass == 5129,
         "pinned PR1062 parent paid profile")

    restorations = terminal_restorations(word)
    by_center = defaultdict(list)
    for center, leaf, index in restorations:
        by_center[center].append(leaf)
    pairs = reciprocal_pairs(word, by_center)
    expected_pairs = [(643, 525, 1517, 1525),
                      (648, 526, 1496, 1502),
                      (650, 534, 1576, 1583)]
    need(pairs == expected_pairs, "reciprocal singleton pair census changed")

    supports = impulse_supports(word)
    case_reports = []
    all_gate_pairs = 0
    all_factorizations = 0
    all_action_pairs = 0
    for a, c, first_a, first_c in pairs:
        for b in sorted(set(by_center[a])):
            for d in sorted(set(by_center[c])):
                edges = [(a, b), (c, d)]
                omitted, d_indices = omit_edges(word, edges)
                changed = [x ^ y for x, y in zip(base_forward, linear_map(omitted))]
                changed_reverse = [x ^ y for x, y in zip(base_reverse,
                                                        linear_map(omitted, reverse=True))]
                need(changed_reverse, "omission residual unexpectedly vanishes in reverse")
                nonzero_rows = [(i, value) for i, value in enumerate(changed) if value]
                columns = [sum(1 << i for i, row in enumerate(changed)
                               if (row >> col) & 1) for col in range(len(changed))]
                colspace = gf2_basis(columns)
                row_rank = len(gf2_basis(value for _, value in nonzero_rows))
                need(len(colspace) == 2 and row_rank == 2,
                     "two-restoration residual is not rank two")
                need(len({value for _, value in nonzero_rows}) == 3,
                     "residual nonzero row syndrome count changed")
                snapshots = capture_a_snapshots(omitted)
                gates = [j for j, support in enumerate(supports)
                         if support and in_basis(support, colspace)]
                support_values = sorted(set(supports[j] for j in gates))
                need(len(gates) == 6 and len(support_values) == 2,
                     "residual output-support gate census changed")
                gate_pairs = [(j, k) for j in gates for k in gates
                              if j < k and supports[j] != supports[k]]
                need(len(gate_pairs) == 5,
                     "candidate ordered gate-pair count changed")
                case_factorizations = 0
                case_action_pairs = 0
                factor_rows = []
                for j, k in gate_pairs:
                    uj, uk = supports[j], supports[k]
                    for alpha in (0, 1):
                        basis_one = uj ^ (uk if alpha else 0)
                        basis_two = uk
                        q1 = 0
                        q2 = 0
                        valid = True
                        for col, vector in enumerate(columns):
                            coeff = solve_two(vector, basis_one, basis_two)
                            if coeff is None:
                                valid = False
                                break
                            if coeff[0]:
                                q1 |= 1 << col
                            if coeff[1]:
                                q2 |= 1 << col
                        need(valid, "rank-two support factorization failed")
                        case_factorizations += 1
                        first_actions = source_actions(word, j, q1, snapshots)
                        second_actions = source_actions(word, k, q2, snapshots)
                        admissible = []
                        for first_action in first_actions:
                            for second_action in second_actions:
                                alpha_actual = interaction_parity(
                                    word, second_action, j, k)
                                cost = first_action[3] + second_action[3]
                                if alpha_actual == alpha and cost <= 1:
                                    admissible.append((first_action, second_action, cost))
                        case_action_pairs += len(admissible)
                        factor_rows.append({
                            "first_gate": j,
                            "second_gate": k,
                            "interaction_parity": alpha,
                            "required_first_input_hex": format(q1, "x"),
                            "required_second_input_hex": format(q2, "x"),
                            "first_actions": len(first_actions),
                            "second_actions": len(second_actions),
                            "charged_action_pairs": len(admissible),
                        })
                        for first_action, second_action, _cost in admissible:
                            candidate = apply_actions(
                                word, edges, [(j, first_action), (k, second_action)])
                            need(linear_map(candidate) == base_forward
                                 and linear_map(candidate, reverse=True) == base_reverse,
                                 "factorized source actions do not repair both boundaries")
                need(case_action_pairs == 0,
                     "a cost-admissible two-tap action pair exists")
                all_gate_pairs += len(gate_pairs)
                all_factorizations += case_factorizations
                all_action_pairs += case_action_pairs
                case_reports.append({
                    "centers": [a, c],
                    "omitted_edges": edges,
                    "omitted_D_indices": d_indices,
                    "first_singleton_reads": [first_a, first_c],
                    "residual_rank": row_rank,
                    "affected_output_rows": len(nonzero_rows),
                    "distinct_nonzero_row_syndromes": len({v for _, v in nonzero_rows}),
                    "residual_row_weights": dict(sorted(Counter(
                        value.bit_count() for _, value in nonzero_rows).items())),
                    "nonzero_residual_rows": [
                        {"output_register": i, "input_mask_hex": format(value, "x")}
                        for i, value in nonzero_rows],
                    "columnspace_basis_hex": [format(x, "x")
                                              for x in sorted(colspace.values())],
                    "candidate_A_gates": gates,
                    "candidate_gate_supports": [
                        {"gate": j, "output_registers": [i for i in range(len(changed))
                                                            if (supports[j] >> i) & 1]}
                        for j in gates],
                    "distinct_candidate_supports": len(support_values),
                    "ordered_distinct_support_gate_pairs": len(gate_pairs),
                    "interaction_factorizations": case_factorizations,
                    "cost_admissible_source_action_pairs": case_action_pairs,
                    "factorizations": factor_rows,
                    "scalar_budget": {
                        "two_D_restorations_removed": -2,
                        "maximum_A_tap_delta_for_strict_saving": 1,
                        "A_actions_tested": ["remove", "add", "replace"],
                        "frame_availability": "relaxed: every register label considered",
                    },
                })
    need(all_gate_pairs == 20 and all_factorizations == 40 and all_action_pairs == 0,
         "aggregate relay search counts changed")

    positive = one_edge_control(word)
    need(linear_map(positive) == base_forward, "known absorption positive control forward")
    need(linear_map(positive, reverse=True) == base_reverse,
         "known absorption positive control reverse")
    need(frame_paths(positive) == base_paths,
         "known absorption positive control frame paths")
    positive_bill = integer_bill(positive)
    need(positive_bill["native_ADDs"] == 11499 and positive_bill["D_adds"] == 5547,
         "known absorption positive-control scalar bill")
    positive_profile, positive_mass, _, _ = owner_profile(positive)
    need(positive_profile == base_profile and positive_mass == base_mass,
         "known absorption positive-control paid profile")

    wrong = wrong_one_edge_control(word)
    wrong_forward = linear_map(wrong)
    wrong_diffs = sum(x != y for x, y in zip(wrong_forward, base_forward))
    need(wrong_diffs > 0, "wrong-donor negative control unexpectedly preserves map")

    return {
        "schema_version": 1,
        "kind": "scoped two-center in-flight defect relay obstruction",
        "base_commit": BASE,
        "selected_record_sha256": SELECTED_SHA256,
        "catalogue_sha256": CATALOGUE_SHA256,
        "candidate_path": CANDIDATE_PATH,
        "candidate_sha256": sha256((ROOT / CANDIDATE_PATH).read_bytes()),
        "source_word": {
            "label": "PR1062 / r439-bsection-stars-seed01",
            "native_ADDs": base_bill["native_ADDs"],
            "D_adds": base_bill["D_adds"],
            "A_adds": base_bill["A_adds"],
            "formal_columns": len(base_forward),
            "paid_profile": base_profile,
            "paid_mass": base_mass,
            "F": base_bill["F"],
            "B": base_bill["B"],
            "local_bits": base_bill["local_bits"],
            "nine_stage_bits": base_bill["nine_stage_bits"],
        },
        "reciprocal_singleton_pairs": [
            {"centers": [a, c], "first_reads": [i, j],
             "terminal_leafs": [sorted(set(by_center[a])), sorted(set(by_center[c]))]}
            for a, c, i, j in pairs],
        "paired_omission_cases": case_reports,
        "totals": {
            "omission_cases": len(case_reports),
            "rank_two_cases": sum(c["residual_rank"] == 2 for c in case_reports),
            "gate_pairs": all_gate_pairs,
            "interaction_factorizations": all_factorizations,
            "cost_admissible_action_pairs": all_action_pairs,
            "accepted_new_constructions": 0,
            "scope_limit": "two restorations at one reciprocal pair; at most two A tap edits on distinct gates; total A tap delta <= +1",
        },
        "controls": {
            "known_absorption_positive": {
                "edge": [514, 367],
                "A_writer": 304,
                "new_sources": [360],
                "forward_and_reverse_equal_parent": True,
                "frame_paths_equal_parent": True,
                "native_ADDs": positive_bill["native_ADDs"],
                "D_adds": positive_bill["D_adds"],
                "F": positive_bill["F"],
                "B": positive_bill["B"],
                "local_bits": positive_bill["local_bits"],
                "nine_stage_bits": positive_bill["nine_stage_bits"],
                "profile": positive_profile,
                "paid_mass": positive_mass,
            },
            "wrong_source_negative": {
                "edge": [514, 367], "A_writer": 304, "wrong_sources": [361],
                "changed_forward_output_rows": wrong_diffs,
                "rejected": True,
            },
        },
        "claim_status": "No advance claim posted; report as FINDING/DONE per autoresearch.md.",
        "no_new_kappa": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", action="store_true")
    args = parser.parse_args()
    report = build_report(load_word())
    path = HERE / "CERTIFICATE.json"
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write_certificate:
        path.write_text(payload, encoding="utf-8")
    else:
        need(path.is_file(), "missing CERTIFICATE.json; run --write-certificate")
        need(path.read_text(encoding="utf-8") == payload,
             "certificate differs from deterministic replay")
    print("PASS_R439_TWO_CENTER_DEFECT_RELAY cases=4 rank2=4 gate_pairs=20 "
          "factorizations=40 admissible_pairs=0 positive_control=1 no_new_kappa")


if __name__ == "__main__":
    main()
