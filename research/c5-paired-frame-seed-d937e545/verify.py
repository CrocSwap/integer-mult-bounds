#!/usr/bin/env python3
"""Exact C5 frame schedule and dirty-echo certificate checker."""

import hashlib
import itertools
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
OUT = 5
WORK_PENTADS = 3
WORK = OUT * WORK_PENTADS
X0 = OUT + WORK
WIDTH = OUT + 2 * WORK
SELECTORS = (0, 1, 2, 0, 1)


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL_C5_PAIRED_FRAME " + message)


def add(target, source, sign=1):
    require(sign in (-1, 1), "invalid ADD sign")
    return (target, source, sign)


def plus_swap(a, b):
    # (a,b) -> (b,-a), using three signed ADDs.
    return [add(a, b), add(b, a, -1), add(a, b)]


def minus_swap(a, b):
    # (a,b) -> (-b,a), using three signed ADDs.
    return [add(b, a), add(a, b, -1), add(b, a)]


def cycle5(indices):
    """Emit (a,b,c,d,e) -> (e,a,b,c,d) with four signed swaps."""
    require(len(indices) == 5 and len(set(indices)) == 5, "cycle width")
    a, b, c, d, e = indices
    return (minus_swap(a, b) + plus_swap(a, c)
            + minus_swap(a, d) + plus_swap(a, e))


def inverse_word(word):
    return [(t, s, -sign) for t, s, sign in reversed(word)]


def lift(word, indices):
    return [(indices[t], indices[s], sign) for t, s, sign in word]


def cycle_power(indices, exponent):
    r = exponent % 5
    forward = cycle5(indices)
    backward = inverse_word(forward)
    if r <= 2:
        one, count = forward, r
    else:
        one, count = backward, 5 - r
    return one * count


def workspace_power(exponent):
    out = []
    for block in range(WORK_PENTADS):
        indices = list(range(OUT + 5 * block, OUT + 5 * (block + 1)))
        out += cycle_power(indices, exponent)
    return out


def output_power(exponent):
    return cycle_power(list(range(OUT)), exponent)


def child_word(block):
    require(block in range(WORK_PENTADS), "bad selector block")
    reader = [add(j, OUT + block * OUT + j) for j in range(OUT)]
    return reader + workspace_power(1)


def frame_counts():
    output = [len(output_power(r)) for r in range(5)]
    workspace = [len(workspace_power(r)) for r in range(5)]
    return workspace, output


def edge_cost(old, new, workspace, output):
    u = (new - old - 1) % 5
    v = (new - old) % 5
    return workspace[u] + output[v]


def shortest_path(children, workspace, output):
    """Exact Bellman recurrence on aligned C5 phases, including endpoints."""
    costs = [workspace[t] + output[t] for t in range(5)]
    paths = [(t,) for t in range(5)]
    for _ in range(children):
        next_costs, next_paths = [], []
        for new in range(5):
            candidates = [(costs[old] + edge_cost(old, new, workspace, output),
                           paths[old] + (new,)) for old in range(5)]
            cost, path = min(candidates)
            next_costs.append(cost)
            next_paths.append(path)
        costs, paths = next_costs, next_paths
    return costs[0], paths[0]


def exhaustive_path(children, workspace, output):
    """Independent enumeration of every aligned path for a short instance."""
    best = None
    checked = 0
    for prefix in itertools.product(range(5), repeat=children):
        states = prefix + (0,)
        cost = workspace[states[0]] + output[states[0]]
        for old, new in zip(states, states[1:]):
            cost += edge_cost(old, new, workspace, output)
        candidate = (cost, states)
        if best is None or candidate < best:
            best = candidate
        checked += 1
    return best, checked


def batch_word(states, blocks, omit_final_gap=False):
    require(len(states) == len(blocks) + 1, "batch path length")
    require(all(p in range(5) for p in states), "phase outside C5")
    word = workspace_power(states[0]) + output_power(states[0])
    for i, block in enumerate(blocks):
        word += child_word(block)
        if omit_final_gap and i == len(blocks) - 1:
            continue
        old, new = states[i], states[i + 1]
        word += workspace_power(new - old - 1)
        word += output_power(new - old)
    return word


def root_echo(states, blocks, omit_source_restore=False):
    body = batch_word(states, blocks)
    body_global = lift(body, list(range(OUT + WORK)))
    copy_in = [add(OUT + i, X0 + i) for i in range(WORK)]
    copy_out = [] if omit_source_restore else [
        add(OUT + i, X0 + i, -1) for i in range(WORK)
    ]
    return (copy_in + body_global + copy_out
            + lift(inverse_word(body), list(range(OUT + WORK))))


def identity(width):
    return [[int(i == j) for j in range(width)] for i in range(width)]


def apply_matrix(word, width):
    rows = identity(width)
    for target, source, sign in word:
        rows[target] = [a + sign * b for a, b in zip(rows[target], rows[source])]
    return rows


def expected_batch(blocks):
    rows = identity(OUT + WORK)
    for block in blocks:
        for j in range(OUT):
            rows[j][OUT + block * OUT + j] += 1
    return rows


def expected_root(blocks):
    rows = identity(WIDTH)
    for block in blocks:
        for j in range(OUT):
            rows[j][X0 + block * OUT + j] += 1
    return rows


def row_l1_peak(word, width):
    rows = identity(width)
    peak = max(sum(abs(x) for x in row) for row in rows)
    for target, source, sign in word:
        rows[target] = [a + sign * b for a, b in zip(rows[target], rows[source])]
        peak = max(peak, max(sum(abs(x) for x in row) for row in rows))
    return peak


def counts(word):
    # ADD and SUBTRACT are both one signed ADD; this construction uses no NEG.
    return {"ADD": len(word), "NEG": 0, "reads": 2 * len(word), "writes": len(word)}


def check_source_pins():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    for entry in manifest["files"]:
        if entry["usage"] != "input":
            continue
        path = ROOT / entry["path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == entry["sha256"], "live input SHA256 changed: " + entry["path"])
    selected = hashlib.sha256((ROOT / "certificates/selected-result.json").read_bytes()).hexdigest()
    require(selected == "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
            "selected record changed")


def build_certificate():
    check_source_pins()
    workspace, output = frame_counts()
    require(workspace == [0, 36, 72, 72, 36], "workspace C5 prices")
    require(output == [0, 12, 24, 24, 12], "output C5 prices")

    base_cycle = cycle5(list(range(5)))
    expected_cycle = identity(5)
    for i in range(5):
        expected_cycle[i] = [int(j == (i - 1) % 5) for j in range(5)]
    require(apply_matrix(base_cycle, 5) == expected_cycle, "signed swaps are not a pure C5 cycle")
    require(len(base_cycle) == 12 and len(inverse_word(base_cycle)) == 12,
            "explicit cycle invoice")

    for block in range(WORK_PENTADS):
        child = child_word(block)
        expected = identity(OUT + WORK)
        for j in range(OUT):
            expected[j][OUT + block * OUT + j] += 1
        for wblock in range(WORK_PENTADS):
            idx = [OUT + 5 * wblock + j for j in range(5)]
            local = apply_matrix(cycle5(idx), OUT + WORK)
            # Compare the workspace rows against the block-diagonal C5 action.
            for i in idx:
                expected[i] = local[i]
        require(apply_matrix(child, OUT + WORK) == expected, "child map block " + str(block))
        require(len(child) == 41, "complete child cost")

    g5, path5 = shortest_path(5, workspace, output)
    g10, path10 = shortest_path(10, workspace, output)
    brute5, paths5 = exhaustive_path(5, workspace, output)
    require((g5, path5, brute5, paths5) ==
            (60, (0, 1, 2, 3, 4, 0), (60, (0, 1, 2, 3, 4, 0)), 3125),
            "five-child shortest path and exhaustive comparison")
    require((g10, path10) == (120, (0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0)),
            "ten-child path")

    blocks5 = SELECTORS
    blocks10 = SELECTORS + SELECTORS
    eager5 = (0, 0, 0, 0, 0, 0)
    body5 = batch_word(path5, blocks5)
    body10 = batch_word(path10, blocks10)
    eager_body5 = batch_word(eager5, blocks5)
    require(apply_matrix(body5, OUT + WORK) == expected_batch(blocks5),
            "optimized five-child dirty batch map")
    require(apply_matrix(body10, OUT + WORK) == expected_batch(blocks10),
            "optimized ten-child dirty batch map")
    require(apply_matrix(eager_body5, OUT + WORK) == expected_batch(blocks5),
            "eager control batch map")

    root5 = root_echo(path5, blocks5)
    root10 = root_echo(path10, blocks10)
    separate = root5 + root5
    eager_root5 = root_echo(eager5, blocks5)
    expected10 = expected_root(blocks10)
    require(apply_matrix(root5, WIDTH) == expected_root(blocks5), "five-child dirty echo map")
    require(apply_matrix(root10, WIDTH) == expected10, "ten-child dirty echo map")
    require(apply_matrix(separate, WIDTH) == expected10, "separate echo composition map")
    require(apply_matrix(eager_root5, WIDTH) == expected_root(blocks5), "eager echo map")

    wrong_terminal = path5[:-1] + (1,)
    bad_terminal = batch_word(wrong_terminal, blocks5)
    omitted_gap = batch_word(path5, blocks5, omit_final_gap=True)
    bad_echo = root_echo(path5, blocks5, omit_source_restore=True)
    require(apply_matrix(bad_terminal, OUT + WORK) != expected_batch(blocks5),
            "unrestored terminal frame control escaped")
    require(apply_matrix(omitted_gap, OUT + WORK) != expected_batch(blocks5),
            "omitted final frame transition control escaped")
    require(apply_matrix(bad_echo, WIDTH) != expected_root(blocks5),
            "unrestored copied source control escaped")

    cost5 = counts(root5)
    eager_cost5 = counts(eager_root5)
    cost10 = counts(root10)
    separate_cost = counts(separate)
    require((cost5["ADD"], eager_cost5["ADD"], cost10["ADD"], separate_cost["ADD"])
            == (560, 800, 1090, 1120), "complete root invoices")
    require(cost5["ADD"] == 2 * (5 * 41 + g5) + 2 * WORK,
            "complete five-child formula")
    require(eager_cost5["ADD"] == 2 * (5 * 41 + 5 * workspace[4]) + 2 * WORK,
            "complete eager formula")
    require(cost10["ADD"] == 2 * (10 * 41 + g10) + 2 * WORK,
            "complete ten-child formula")

    return {
        "schema_version": 1,
        "result": "EXACT_C5_DIRTY_ECHO_CONSTRUCTION",
        "assignment": {
            "seed": "d937e5458b1c6e96dcdfc67cab6201d3",
            "track": "recursive-interfaces",
            "task_id": "persistent-boundary",
            "base_commit": "0b1cccf86e2f5132ed286a26ef0a681a495740ea",
            "selected_record_sha256": "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
            "catalog_sha256": "6686ad58f1fbdbc87134a78901b60fd53a20d3984355e91defbbebc9e9fa8075"
        },
        "model": {
            "field": "Z",
            "output_width": OUT,
            "workspace_width": WORK,
            "workspace_pentads": WORK_PENTADS,
            "source_width": WORK,
            "source_selectors": list(blocks5),
            "child_map": "(D,W) -> (D + R_i W, P W), R_i P = Q R_i",
            "dirty_state": "D, W, and X arbitrary; exact integer linear maps",
            "copy_restore_adds": 2 * WORK,
            "helpers_or_clean_scratch": 0,
            "precision_or_tape_admission": "not modeled"
        },
        "explicit_operations": {
            "C5_cycle": "T-(a,b), T+(a,c), T-(a,d), T+(a,e)",
            "signed_swap_cost": "3 ADD each; four compose to the pure five-cycle",
            "one_output_cycle_adds": 12,
            "one_workspace_cycle_adds": 36,
            "workspace_phase_adds": workspace,
            "output_phase_adds": output
        },
        "phase_recurrence": {
            "initial_cost": "A[t] + B[t]",
            "edge_cost": "A[(s-t-1) mod 5] + B[(s-t) mod 5]",
            "terminal_phase": 0,
            "k5": {"minimum": g5, "path": list(path5), "exhaustive_paths": paths5},
            "k10": {"minimum": g10, "path": list(path10), "exhaustive_paths": None},
            "eager_k5_phase_adds": 5 * workspace[4]
        },
        "complete_invoices": {
            "optimized_one_echo_k5": cost5,
            "eager_one_echo_k5": eager_cost5,
            "optimized_joint_echo_k10": cost10,
            "two_separate_optimized_echoes_k5": separate_cost,
            "savings_vs_eager_k5": 800 - 560,
            "savings_joint_vs_two_calls": 1120 - 1090
        },
        "dirty_maps": {
            "one_echo_k5_rows": apply_matrix(root5, WIDTH),
            "joint_echo_k10_rows": apply_matrix(root10, WIDTH),
            "separate_two_echoes_rows": apply_matrix(separate, WIDTH),
            "joint_matches_separate": True,
            "basis_columns_checked": WIDTH
        },
        "prefix_row_l1_peak": {
            "optimized_k5": row_l1_peak(root5, WIDTH),
            "eager_k5": row_l1_peak(eager_root5, WIDTH),
            "joint_k10": row_l1_peak(root10, WIDTH),
            "separate_two_k5": row_l1_peak(separate, WIDTH)
        },
        "negative_controls": {
            "noncanonical_terminal_phase": "REJECTED",
            "omitted_final_frame_transition": "REJECTED",
            "omitted_copied_source_restore": "REJECTED"
        },
        "limits": [
            "The macro cycle circuit is explicit, not claimed ADD-optimal among all circuits.",
            "The shortest path is exact only in the declared C5 whole-register power alphabet.",
            "No selected supplier, fixed-precision contract, tape bound, new frontier, or kappa is established."
        ]
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-certificate", action="store_true")
    args = parser.parse_args()
    result = build_certificate()
    path = PACKAGE / "CERTIFICATE.json"
    encoded = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.write_certificate:
        path.write_text(encoded)
    else:
        require(path.exists(), "missing CERTIFICATE.json")
        require(path.read_text() == encoded, "certificate differs; run verify.py --write-certificate")
    print("PASS_C5_PAIRED_FRAME k5=60/180 eager root=560/800 k10=120 paired=1090/1120 paths5=3125 basis=35")


if __name__ == "__main__":
    main()
