#!/usr/bin/env python3
"""Separate the four V45 width drops inside the recorded idle histogram.

The search is a deterministic equality-form simplex. Its vertex is then solved
exactly. The same search recovers the parent and stage-1 certificate histograms.
The exact dual enclosure is not rebuilt.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
DATA = ROOT / "research/rank7-joint-endframes/certificates/RELAX-STAGES.json"
BINS = (8, 16, 32, 48)
BIN_COUNT = {8: 672, 16: 448, 32: 448, 48: 448}
CALLS = 9
WIDTH_DROP = 4
MARKER = (
    "PASS_RANK7_V45_WIDTH_IDLE helpers=4 mass=36 "
    "calibrated=parent,stage1 dual_enclosure=false no_new_kappa"
)


def fail(message):
    raise SystemExit("FAIL_RANK7_V45_WIDTH_IDLE " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def patterns(widths):
    widths = tuple(sorted(widths))
    found = []
    for cap in BINS:
        counts = [0] * len(widths)

        def walk(index, used):
            if index == len(widths):
                found.append((cap, tuple(counts), cap - used))
                return
            room = (cap - used) // widths[index]
            for count in range(room + 1):
                counts[index] = count
                walk(index + 1, used + count * widths[index])
            counts[index] = 0

        walk(0, 0)
    return widths, found


def column(pattern):
    cap, counts, _rank = pattern
    return [1.0 if cap == item else 0.0 for item in BINS] + [float(count) for count in counts]


def price(rank, saving):
    if rank == 0:
        return 0.0
    return rank * (73.0 / rank) ** saving


def solve(found, rhs, saving):
    row_count = len(rhs)
    column_count = len(found)
    cost = [price(pattern[2], saving) for pattern in found]
    columns = [column(pattern) for pattern in found]
    tableau = []
    for row in range(row_count):
        original = [columns[index][row] for index in range(column_count)]
        artificial = [1.0 if row == index else 0.0 for index in range(row_count)]
        tableau.append(original + artificial + [float(rhs[row])])
    basis = list(range(column_count, column_count + row_count))

    def pivot(row, col):
        scale = tableau[row][col]
        tableau[row] = [value / scale for value in tableau[row]]
        for other in range(row_count):
            if other == row:
                continue
            factor = tableau[other][col]
            if factor != 0.0:
                tableau[other] = [left - factor * right for left, right in zip(tableau[other], tableau[row])]
        basis[row] = col

    def reduced(phase):
        if phase == 1:
            basic = [1.0 if basis[row] >= column_count else 0.0 for row in range(row_count)]
        else:
            basic = [cost[basis[row]] for row in range(row_count)]
        limit = column_count + row_count if phase == 1 else column_count
        costs = []
        for col in range(limit):
            value = 1.0 if phase == 1 and col >= column_count else (cost[col] if phase == 2 else 0.0)
            for row in range(row_count):
                value -= basic[row] * tableau[row][col]
            costs.append(value)
        return costs

    for phase in (1, 2):
        while True:
            costs = reduced(phase)
            enter = min(range(len(costs)), key=lambda index: (costs[index], index))
            if costs[enter] >= -1e-9:
                break
            leave = None
            best = None
            for row in range(row_count):
                if tableau[row][enter] <= 1e-12:
                    continue
                ratio = tableau[row][-1] / tableau[row][enter]
                if best is None or ratio < best - 1e-12 or (abs(ratio - best) <= 1e-12 and basis[row] < basis[leave]):
                    best = ratio
                    leave = row
            require(leave is not None, "the packing is unbounded")
            pivot(leave, enter)
        if phase == 1:
            leftover = sum(tableau[row][-1] for row in range(row_count) if basis[row] >= column_count)
            require(leftover <= 1e-7, "the packing is infeasible")
            for row in range(row_count):
                if basis[row] < column_count:
                    continue
                for col in range(column_count):
                    if abs(tableau[row][col]) > 1e-9:
                        pivot(row, col)
                        break
    support = {basis[row]: tableau[row][-1] for row in range(row_count) if basis[row] < column_count and tableau[row][-1] > 1e-8}
    require(len(support) == row_count, "the vertex is degenerate")
    require(min(reduced(2)) >= -1e-7, "a negative reduced cost survived")
    return support


def exact_vertex(found, widths, rhs, support):
    chosen = sorted(support)
    matrix = []
    for row in range(len(rhs)):
        matrix.append([Fraction(column(found[index])[row]) for index in chosen] + [Fraction(int(row == col)) for col in range(len(rhs))])
    for col in range(len(rhs)):
        pivot = next((row for row in range(col, len(rhs)) if matrix[row][col] != 0), None)
        require(pivot is not None, "the vertex basis is singular")
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        scale = matrix[col][col]
        matrix[col] = [value / scale for value in matrix[col]]
        for row in range(len(rhs)):
            if row != col and matrix[row][col] != 0:
                factor = matrix[row][col]
                matrix[row] = [left - factor * right for left, right in zip(matrix[row], matrix[col])]
    target = [Fraction(value) for value in rhs]
    values = [sum(matrix[col][len(rhs) + row] * target[row] for row in range(len(rhs))) for col in range(len(rhs))]
    require(all(value >= 0 for value in values), "the exact vertex is not feasible")
    idle = {}
    shown = []
    for index, pattern_index in enumerate(chosen):
        cap, counts, rank = found[pattern_index]
        shown.append({
            "capacity": cap,
            "widths": [width for width, count in zip(widths, counts) for _ in range(count)],
            "count_per_replica": str(values[index]),
        })
        if rank and values[index] != 0:
            idle[rank] = idle.get(rank, 0) + values[index]
    return {str(rank): str(count) for rank, count in sorted(idle.items())}, shown


def idle_mass(idle):
    return sum(int(rank) * Fraction(count) for rank, count in idle.items())


def rhs_for(inventory, widths):
    return [BIN_COUNT[cap] for cap in BINS] + [CALLS * inventory[width] for width in widths]


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    require(set(pinned) == {"research/rank7-joint-endframes/certificates/RELAX-STAGES.json"}, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def recover(inventory, saving):
    widths, found = patterns(inventory)
    support = solve(found, rhs_for(inventory, widths), saving)
    return exact_vertex(found, widths, rhs_for(inventory, widths), support) + (len(found),)


def evaluate():
    authenticate()
    stages = json.loads(DATA.read_text(encoding="utf-8"))
    parent = stages["parent"]
    stage1 = stages["stage1"]
    parent_inventory = {int(rank): int(count) for rank, count in parent["inventory_per_call"].items()}
    stage_inventory = {int(rank): int(count) for rank, count in stage1["inventory_per_call"].items()}
    moved = dict(parent_inventory)
    moved[8] -= WIDTH_DROP
    moved[7] += WIDTH_DROP
    parent_saving = float(Fraction(parent["cap_lower"]))
    stage_saving = float(Fraction(stage1["cap_lower"]))
    parent_idle, _parent_basis, parent_patterns = recover(parent_inventory, parent_saving)
    stage_idle, _stage_basis, stage_patterns = recover(stage_inventory, parent_saving)
    moved_idle, moved_basis, moved_patterns = recover(moved, parent_saving)
    again, again_basis, _count = recover(moved, stage_saving)
    stored_parent = {rank: str(Fraction(count)) for rank, count in parent["idle_per_replica"].items()}
    stored_stage = {rank: str(Fraction(count)) for rank, count in stage1["idle_per_replica"].items()}
    require(parent_patterns == parent["patterns"] and stage_patterns == stage1["patterns"], "pattern counts left the certificates")
    require(parent_idle == stored_parent and stage_idle == stored_stage, "the search missed a certificate histogram")
    require(moved_idle == again and moved_basis == again_basis, "the four-width vertex moved between the recorded caps")
    require(idle_mass(moved_idle) - idle_mass(parent_idle) == WIDTH_DROP * CALLS, "the idle-mass increase is not one width per call")
    require(moved_patterns == parent_patterns, "the four-width move introduced a width")
    return {
        "helpers": WIDTH_DROP,
        "parent_width": 8,
        "shipped_width": 7,
        "calls_per_replica": CALLS,
        "idle_rank_mass_increase": str(WIDTH_DROP * CALLS),
        "parent_idle": parent_idle,
        "width_only_idle": moved_idle,
        "stage1_idle": stage_idle,
        "width_only_basis": moved_basis,
        "same_vertex_at_both_caps": True,
        "certificate_histograms_recovered": True,
        "local_profile": "parent",
        "dual_enclosure_resolved": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
