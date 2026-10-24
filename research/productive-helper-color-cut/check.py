#!/usr/bin/env python3
"""Exact source-bound color-cut obstruction to an ascending scalar encoder.

Standard library only: reconstructs the full 24-input transfer and boundary
charts from the pinned word, without solver output or generated matrix inputs.
The general normal-form argument is in PROOF.md; this checks its source data.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

SOURCE_BYTES_SHA256 = "6caa29e474375298847fac8a53508f65037dc45e64d2ea0125ece9faf32b2ce4"
SOURCE_JSON_SHA256 = "aa4a8241da76abd2c06e6576a3ac09e77781321deaac3ad7d3ce4519342a36e6"
LO, HI = 9961, 10111
HOT = [13, 16, 43, 44, 51, 78, 99, 104]
LOCAL = HOT + list(range(416, 432))
CLEAN = [13, 51, 78, 99, 427, 429, 425, 431, 416]
DIRTY = [r for r in LOCAL if r not in CLEAN]
PAIRS = [(13, 51), (78, 99), (16, 44), (43, 104)]
MASKS = [()] + [(r,) for r in HOT] + PAIRS
NORMAL = [Q(x) for x in (2, 0, -1, 0, 0, -1, -1, 1)]
IX = {r: i for i, r in enumerate(LOCAL)}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def mm(a, b):
    return [[sum(x * b[k][j] for k, x in enumerate(row) if x)
             for j in range(len(b[0]))] for row in a]


def rref(rows, width):
    rows = [[Q(x) for x in row] for row in rows if any(row)]
    pivots = []
    for column in range(width):
        k = len(pivots)
        pivot = next((i for i in range(k, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[k], rows[pivot] = rows[pivot], rows[k]
        value = rows[k][column]
        rows[k] = [x / value for x in rows[k]]
        for i in range(len(rows)):
            if i != k and rows[i][column]:
                value = rows[i][column]
                rows[i] = [x - value * y for x, y in zip(rows[i], rows[k])]
        pivots.append(column)
        if len(pivots) == len(rows):
            break
    return rows[:len(pivots)], pivots


def rank(rows, width):
    return len(rref(rows, width)[1])


def nullspace(rows, width):
    reduced, pivots = rref(rows, width)
    basis = []
    for c in range(width):
        if c in pivots:
            continue
        v = [Q(0)] * width
        v[c] = Q(1)
        for row, p in zip(reduced, pivots):
            v[p] = -row[c]
        need(all(sum(x * y for x, y in zip(row, v)) == 0 for row in rows), "nullspace equation")
        basis.append(v)
    need(len(basis) + len(pivots) == width, "nullspace dimension")
    return basis


def inverse(matrix):
    n = len(matrix)
    reduced, pivots = rref([row[:] + unit for row, unit in zip(matrix, eye(n))], 2 * n)
    need(pivots == list(range(n)), "matrix singular")
    answer = [row[n:] for row in reduced]
    need(mm(matrix, answer) == eye(n) and mm(answer, matrix) == eye(n), "both inverse products")
    return answer


def sparse(row, labels):
    return {str(label): str(x) for label, x in zip(labels, row) if x}


def matrix_hash(matrix, rows, columns):
    return digest({"rows": rows, "columns": columns, "coefficients": [[str(x) for x in row] for row in matrix]})


def span(vectors):
    result = {0}
    for v in vectors:
        result |= {x ^ v for x in tuple(result)}
    return frozenset(result)


def basis(space):
    rows, seen = [], {0}
    for v in sorted(space):
        if v not in seen:
            rows.append(v)
            seen |= {x ^ v for x in tuple(seen)}
    return rows


def refs(event):
    gate = event[1]
    return gate[1:3] if gate[0] == "add" else gate[1:2]


def scalar_matrix(events):
    matrix = eye(len(LOCAL))
    for event in events:
        need(event[0] == "scalar", "local interval must be scalar")
        gate = event[1]
        need(gate[0] in ("add", "scale"), "unrecognized or noninvertible gate")
        need(all(kind == "L" and r in IX for kind, r in refs(event)), "local role binding")
        target = IX[gate[1][1]]
        if gate[0] == "add":
            source, coefficient = IX[gate[2][1]], Q(*gate[3:5])
            need(source != target, "self-add excluded")
            matrix[target] = [x + coefficient * y for x, y in zip(matrix[target], matrix[source])]
        else:
            coefficient = Q(*gate[2:4])
            need(coefficient != 0, "singular scale")
            matrix[target] = [coefficient * x for x in matrix[target]]
    return matrix


def load_source(data):
    need(hashlib.sha256(data).hexdigest() == SOURCE_BYTES_SHA256, "compressed source byte hash")
    word = json.loads(gzip.decompress(data))
    need(digest(word) == SOURCE_JSON_SHA256, "canonical source JSON hash")
    return word


def reconstruct(word):
    program = [event for event in word["programs"]["forward"] if event[0] != "climb"]
    need(len(program) == 18061, "source event census")
    segment = program[LO:HI]
    need(sorted({r for e in segment for _, r in refs(e)}) == LOCAL, "local role census")
    M = scalar_matrix(segment)
    inverse(M)
    # T: 419 += 417/2; 417 -= 419. P swaps output416 and417.
    H = [row[:] for row in M]
    H[IX[419]] = [x + y / 2 for x, y in zip(H[IX[419]], H[IX[417]])]
    H[IX[417]] = [x - y for x, y in zip(H[IX[417]], H[IX[419]])]
    H[IX[416]], H[IX[417]] = H[IX[417]], H[IX[416]]
    need(H[IX[416]] == [Q(r in (13, 416)) for r in LOCAL], "protected output row")
    inverse(H)
    maps = {x["op"]: x for x in word["canonical"]["warps"]}
    need(maps[34]["lender"] == 417 and maps[35]["lender"] == 419, "native role binding")
    need(maps[34]["G_columns"] == maps[35]["G_columns"], "equal native maps34/35 motivation")
    need(maps[36]["lender"] == 421, "third native role binding")
    need(sorted(op for op, row in maps.items()
                if row["G_columns"] == maps[34]["G_columns"]) == [34, 35, 36],
         "complete common native-map class")
    return M, H, program, segment


def source_boundaries(word, program):
    canonical = word["canonical"]
    need(canonical["h"] == 9 and len(canonical["start"]) == 632, "source dimension/register census")
    frames = list(map(span, canonical["frames"]))
    current = canonical["start"][:]
    for ordinal, event in enumerate(program[:HI]):
        if ordinal == LO:
            entry_labels = {r: current[r] for r in LOCAL}
        if event[0] == "scalar":
            for kind, role in refs(event):
                if kind == "L":
                    current[role] = event[2]
        elif event[0] == "warp":
            current[event[1][1]] = event[4]
        elif event[0] == "adapter":
            need(current[event[2]] == event[3], "adapter preserves current canonical chart")
        else:
            need(event[0] == "phase", "unexpected chart-changing prefix instruction")
    source_exits = {r: current[r] for r in LOCAL}
    entries = {r: frames[entry_labels[r]] for r in LOCAL}
    need(all(len(entries[r]) == 2 for r in HOT), "eight hot entry lines")
    need(all(entries[r] == frozenset({0}) for r in LOCAL if r not in HOT), "sixteen arbitrary cold entries")
    expected_lines = {13: 73, 16: 49, 43: 386, 44: 28, 51: 100, 78: 506, 99: 471, 104: 431}
    need(all(entries[r] == span([v]) for r, v in expected_lines.items()), "source input line binding")
    fixed_exits = {r: frames[source_exits[r]] for r in LOCAL}
    fixed_exits[417] = frames[source_exits[416]]
    fixed_exits[416] = entries[13]
    need(all(entries[r] <= fixed_exits[r] for r in LOCAL), "physical entry contained in fixed exit")
    return frames, entries, fixed_exits, entry_labels, source_exits


def colors(chart, entries):
    return [i for i, pair in enumerate(PAIRS) if any(entries[r] <= chart for r in pair)]


def check_clean_caps(exits, entries):
    expected = {13: 0, 51: 0, 78: 1, 99: 1, 427: 2, 429: 2, 425: 3, 431: 3, 416: 0}
    answer = {str(r): colors(exits[r], entries) for r in CLEAN}
    need(all(answer[str(r)] == [color] for r, color in expected.items()), "nine fixed output caps are monochrome")
    return answer


def pair_dimensions(G):
    total = rank(G, len(HOT))
    return [total - rank([[row[k] for k, r in enumerate(HOT) if r not in pair] for row in G], 6)
            for pair in PAIRS]


def analyze(H):
    G = [[H[IX[r]][IX[s]] for s in HOT] for r in DIRTY]
    need(rank(G, 8) == 7, "dirty-hot block rank7")
    need(nullspace(G, 8) == [NORMAL], "unique coupled hot-column relation")
    need(H[IX[43]][IX[13]] == 1, "nonzero hot13 coefficient")
    parts = pair_dimensions(G)
    need(parts == [1, 1, 2, 1], "one-pair rowspace dimensions")
    masks, all_rows = [], []
    for mask in MASKS:
        outside = [k for k, r in enumerate(HOT) if r not in mask]
        equations = [[G[j][k] for j in range(len(DIRTY))] for k in outside]
        vectors = nullspace(equations, len(DIRTY))
        all_rows.extend(vectors)
        masks.append({"hot_support_mask": list(mask), "nullspace_dimension": len(vectors),
                      "complete_nullspace_basis_w": [sparse(v, DIRTY) for v in vectors]})
    need(rank(all_rows, 15) == 13, "allowed capture preimage span rank13")
    annihilators = nullspace(all_rows, 15)
    need(len(annihilators) == 2, "two independent common annihilators")
    return G, parts, masks, annihilators


def source_positive_control(M, segment, frames, entries, source_exits):
    current = dict(entries)
    mono, mixed, classified = [], [], []
    for event in segment:
        touched = {r for _, r in refs(event)}
        chart = frames[event[2]]
        need(all(current[r] <= chart for r in touched), "original scalar source is ascending")
        multi = len(colors(chart, entries)) >= 2
        (mixed if multi else mono).append(event)
        classified.append((multi, touched))
        for r in touched:
            current[r] = chart
    inversions = 0
    for i, (multi, touched) in enumerate(classified):
        if multi:
            for later_multi, later_touched in classified[i + 1:]:
                if not later_multi:
                    need(touched.isdisjoint(later_touched), "out-of-order source gates must commute")
                    inversions += 1
    J, L = scalar_matrix(mono), scalar_matrix(mixed)
    need(mm(L, J) == M, "source full24 normal-form matrix identity")
    source_clean = [r for r in CLEAN if r != 416]
    source_dirty = [r for r in LOCAL if r not in source_clean]
    need(all(len(colors(frames[source_exits[r]], entries)) == 1 for r in source_clean), "source clean caps")
    need(all(r not in source_clean for event in mixed for _, r in refs(event)), "source mixed suffix excludes clean outputs")
    for r in source_dirty:
        support = [s for s in HOT if J[IX[r]][IX[s]]]
        need(any(set(support) <= set(pair) for pair in PAIRS), "source prefix hot support is one-pair")
    G0 = [[M[IX[r]][IX[s]] for s in HOT] for r in source_dirty]
    need(rank(G0, 8) == 8 and pair_dimensions(G0) == [2, 2, 2, 2], "original source passes rowspace test")
    need((len(mono), len(mixed), inversions) == (40, 110, 72), "source normal-form census")
    return {"status": "PASS", "mono_gates": len(mono), "mixed_gates": len(mixed),
            "disjoint_commuting_inversions": inversions, "full24_matrix_identity": True,
            "dirty_output_count": 16, "dirty_hot_rank": 8, "pair_intersection_dimensions": [2, 2, 2, 2]}


def rejected(action):
    try:
        action()
    except (ValueError, KeyError, IndexError, ZeroDivisionError):
        return True
    return False


def corruption_controls(raw, H, G, exits, entries):
    controls = {"changed_source_bytes_rejected": rejected(lambda: load_source(raw + b" "))}
    wrong = [row[:] for row in H]
    wrong[IX[43]][IX[13]] += 1
    controls["changed_target_coefficient_rejected"] = rejected(lambda: analyze(wrong))
    bad_normal = NORMAL[:]
    bad_normal[0] *= -1
    controls["wrong_relation_sign_rejected"] = bool(any(sum(x * y for x, y in zip(row, bad_normal)) for row in G))
    bad_caps = dict(exits)
    bad_caps[13] = span(exits[13] | entries[78])
    controls["cross_color_clean_cap_rejected"] = rejected(lambda: check_clean_caps(bad_caps, entries))
    need(all(controls.values()), "a corruption control was accepted")
    def union_rank(masks):
        vectors = []
        for mask in masks:
            equations = [[G[j][k] for j in range(15)] for k, r in enumerate(HOT) if r not in mask]
            vectors.extend(nullspace(equations, 15))
        return rank(vectors, 15)
    controls["one_cross_pair_relaxation_rank"] = union_rank(MASKS + [(13, 43)])
    controls["two_cross_pair_relaxations_rank"] = union_rank(MASKS + [(13, 43), (13, 78)])
    need(controls["one_cross_pair_relaxation_rank"] == 14, "one cross-pair scope control")
    need(controls["two_cross_pair_relaxations_rank"] == 15, "two cross-pair scope controls")
    return controls


def run(source_path=None, *, controls=True):
    path = (Path(source_path) if source_path is not None else
            Path(__file__).resolve().parent.parent / "productive-helper-fusion-certificate" / "COMBINED-WORD.json.gz")
    raw = path.read_bytes()
    word = load_source(raw)
    M, H, program, segment = reconstruct(word)
    frames, entries, exits, entry_labels, source_exits = source_boundaries(word, program)
    clean_colors = check_clean_caps(exits, entries)
    G, parts, masks, annihilators = analyze(H)
    family_spec = importlib.util.spec_from_file_location("productive_color_family", Path(__file__).with_name("check_family.py"))
    family = importlib.util.module_from_spec(family_spec)
    family_spec.loader.exec_module(family)
    family_result = family.verify(G, DIRTY, HOT)
    Hi = inverse(H)
    for output in LOCAL:
        for input_role in LOCAL:
            if H[IX[output]][IX[input_role]] or Hi[IX[input_role]][IX[output]]:
                need(entries[input_role] <= exits[output], "two-sided ordinary support containment")
    positive = source_positive_control(M, segment, frames, entries, source_exits)
    receipt = {
        "status": "PASS_DIRECT_ENCODER_ASCENDING_OBSTRUCTION",
        "source_bytes_sha256": SOURCE_BYTES_SHA256, "source_json_sha256": SOURCE_JSON_SHA256,
        "source_orientation": "forward", "climb_stripped_scalar_interval": [LO, HI],
        "source_segment_sha256": digest(segment), "local_roles": LOCAL,
        "hot_inputs": HOT, "arbitrary_cold_inputs": [r for r in LOCAL if r not in HOT],
        "monochrome_outputs": CLEAN, "remaining_outputs": DIRTY,
        "M_sha256": matrix_hash(M, LOCAL, LOCAL), "H_sha256": matrix_hash(H, LOCAL, LOCAL),
        "both_M_and_H_inverse_products": True, "native34_35_equal_source_maps": True,
        "complete_equal_native_map_class": {"operators": [34, 35, 36], "lenders": [417, 419, 421]},
        "all_forward_and_inverse_support_containments": True,
        "protected_output_row": {"13": "1", "416": "1"},
        "source_entry_frames": {str(r): value for r, value in entry_labels.items()},
        "source_exit_frames": {str(r): value for r, value in source_exits.items()},
        "entry_chart_bases": {str(r): basis(entries[r]) for r in LOCAL},
        "fixed_exit_chart_bases": {str(r): basis(exits[r]) for r in LOCAL},
        "monochrome_output_colors": clean_colors, "source_hot_pairs": [list(pair) for pair in PAIRS],
        "G_sha256": matrix_hash(G, DIRTY, HOT), "G_rank": 7,
        "G_rows": {str(r): sparse(row, HOT) for r, row in zip(DIRTY, G)},
        "unique_G_column_relation": sparse(NORMAL, HOT), "G_row43_column13": "1",
        "pair_supported_rowspace_dimensions": parts,
        "pair_supported_rowspace_span_dimension": sum(parts),
        "allowed_capture_preimage_span_rank": 13,
        "common_annihilators": [sparse(v, DIRTY) for v in annihilators], "masks": masks,
        "original_source_positive_control": positive,
        "common_native_basis_family": family_result,
        "scope": "No ascending canonical-chart ADD/SCALE circuit on these24 registers realizes H=P*T*M from the source entry charts to the fixed exit charts. Arbitrary rational coefficients and arbitrary intermediate charts/interleavings are allowed. No preparation prefix is assumed. No new registers or native maps inside the scalar interval; enlarged boundaries, nonascending transports and different target words are not excluded. No tariff or improved-bound claim.",
    }
    if controls:
        receipt["corruption_and_scope_controls"] = corruption_controls(raw, H, G, exits, entries)
        family_result["corruption_controls"] = family.controls(G, DIRTY, HOT)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run(args.source)
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "G_rank": result["G_rank"],
                      "pair_span_dimension": result["pair_supported_rowspace_span_dimension"],
                      "capture_span_rank": result["allowed_capture_preimage_span_rank"],
                      "controls": result.get("corruption_and_scope_controls")}, sort_keys=True))
