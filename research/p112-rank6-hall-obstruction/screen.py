# SPDX-License-Identifier: Apache-2.0
"""Exact necessary coefficient equations on saturated orthogonal frames."""
from collections import Counter
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "credited_rank6_geometry", ROOT / "research/p112-rank6-frame-coverage/engine.py")
engine = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(engine)


def frame_screen(data, frames, terms):
    """Terms are support upper bounds, not claimed nonzero coefficients."""
    masks = [sum(1 << root for root in frame) for frame in frames]
    diagonal = {i: sum(bool(left & right & (1 << i)) for left, right in terms)
                for i in data["live"]}
    counts, trace_empty, saturated = [], [], []
    for index, mask in enumerate(masks):
        active = [k for k, (left, right) in enumerate(terms) if left & mask and right & mask]
        counts.append(len(active))
        if len(active) == 8:
            saturated.append((index, active))
            for k in active:
                if not terms[k][0] & terms[k][1] & mask:
                    trace_empty.append([index, k])
    return dict(frame_hit_histogram=dict(sorted(Counter(counts).items())),
                minimum_frame_hits=min(counts),
                diagonal_hit_histogram=dict(sorted(Counter(diagonal.values()).items())),
                uncovered_diagonals=[i for i, value in diagonal.items() if not value],
                saturated_frames=len(saturated), empty_trace_constraints=trace_empty), saturated


def clique_masks(data):
    """Every nonempty orthogonal clique, including ones with no live 8-frame."""
    roots = data["lines"]
    adjacency = [sum(1 << j for j in data["live"]
                     if i != j and sum(x*y for x, y in zip(roots[i], roots[j])) == 0)
                 for i in range(len(roots))]
    cliques = []

    def visit(chosen, possible):
        while possible:
            bit = possible & -possible
            possible ^= bit
            i = bit.bit_length() - 1
            cliques.append(chosen | bit)
            visit(chosen | bit, possible & adjacency[i])

    visit(0, sum(1 << i for i in data["live"]))
    return sorted(cliques, key=lambda value: (value.bit_count(), value))


def all_clique_screen(data, terms):
    """Every principal orthogonal-clique rank count, not just eight-frames."""
    counts, failures = Counter(), []
    for mask in clique_masks(data):
        size = mask.bit_count()
        counts[size] += 1
        active = sum(bool(left & mask and right & mask) for left, right in terms)
        if active < size:
            failures.append([list(engine.bits(mask)), active])
    return dict(cliques_by_size=dict(sorted(counts.items())),
                failed_cliques=len(failures), first_failure=failures[0] if failures else None)




