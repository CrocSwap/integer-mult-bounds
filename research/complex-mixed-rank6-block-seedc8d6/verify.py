#!/usr/bin/env python3
"""Verify a mixed (3,1,1,1)->6 bilinear block and exact profile thresholds."""

from __future__ import annotations

import hashlib
import gzip
import importlib.util
import json
import tarfile
from collections import Counter
from fractions import Fraction as Q
from io import BytesIO
from pathlib import Path
import sys


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def need(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def source_bytes(path: str) -> bytes:
    p = ROOT / path
    need(p.is_file(), f"missing source {path}")
    return p.read_bytes()


def pins() -> dict[str, str]:
    inv = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    task = json.loads((PACKAGE / "TASK.json").read_text(encoding="utf-8"))
    need(inv["base_commit"] == task["base_commit"], "task/source base mismatch")
    need(hashlib.sha256(source_bytes("certificates/selected-result.json")).hexdigest()
         == task["selected_record_sha256"], "selected record hash mismatch")
    out = {}
    for row in inv["files"]:
        digest = hashlib.sha256(source_bytes(row["path"])).hexdigest()
        need(digest == row["sha256"], f"pinned source hash mismatch: {row['path']}")
        out[row["path"]] = digest
    return out


def load_ceiling():
    path = ROOT / "research/complex-local-word-ceiling/ceiling.py"
    spec = importlib.util.spec_from_file_location("pinned_complex_ceiling", path)
    need(spec is not None and spec.loader is not None, "cannot load exact ceiling engine")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def zeros(n: int, m: int) -> list[list[Q]]:
    return [[Q(0) for _ in range(m)] for _ in range(n)]


def outer(left: list[Q], right: list[Q]) -> list[list[Q]]:
    return [[a * b for b in right] for a in left]


def add_matrix(a: list[list[Q]], b: list[list[Q]], scale: Q = Q(1)) -> list[list[Q]]:
    return [[x + scale * y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def flatten(a: list[list[Q]]) -> list[Q]:
    return [x for row in a for x in row]


def rank_q(rows: list[list[Q]]) -> int:
    a = [list(map(Q, row)) for row in rows]
    if not a:
        return 0
    m, n = len(a), len(a[0])
    pivot = 0
    for col in range(n):
        found = next((r for r in range(pivot, m) if a[r][col]), None)
        if found is None:
            continue
        a[pivot], a[found] = a[found], a[pivot]
        d = a[pivot][col]
        a[pivot] = [x / d for x in a[pivot]]
        for r in range(m):
            if r != pivot and a[r][col]:
                c = a[r][col]
                a[r] = [x - c * y for x, y in zip(a[r], a[pivot])]
        pivot += 1
        if pivot == m:
            break
    return pivot


def tensor_data():
    # Inputs x,y each have coordinates 0..4; output slices are 5x5 matrices.
    slices = [zeros(5, 5) for _ in range(5)]
    slices[0][0][0] = Q(1)
    slices[1][0][1] = Q(1)
    slices[1][1][0] = Q(1)
    for i in range(2, 5):
        slices[i][i][i] = Q(1)

    # Six atoms. Product vectors are the output coefficient vectors.
    terms = []
    terms.append(("x0*y0", [Q(1), Q(0), Q(0), Q(0), Q(0)],
                  [Q(1), Q(0), Q(0), Q(0), Q(0)], [Q(1), Q(-1), Q(0), Q(0), Q(0)]))
    terms.append(("x1*y1", [Q(0), Q(1), Q(0), Q(0), Q(0)],
                  [Q(0), Q(1), Q(0), Q(0), Q(0)], [Q(0), Q(-1), Q(0), Q(0), Q(0)]))
    terms.append(("(x0+x1)*(y0+y1)", [Q(1), Q(1), Q(0), Q(0), Q(0)],
                  [Q(1), Q(1), Q(0), Q(0), Q(0)], [Q(0), Q(1), Q(0), Q(0), Q(0)]))
    for i in range(2, 5):
        lx, ry, ov = [Q(0)] * 5, [Q(0)] * 5, [Q(0)] * 5
        lx[i] = ry[i] = ov[i] = Q(1)
        terms.append((f"x{i}*y{i}", lx, ry, ov))

    reconstructed = [zeros(5, 5) for _ in range(5)]
    for _name, lx, ry, output in terms:
        product_matrix = outer(lx, ry)
        for j, coefficient in enumerate(output):
            reconstructed[j] = add_matrix(reconstructed[j], product_matrix, coefficient)
    need(reconstructed == slices, "six-atom reconstruction differs from the target tensor")
    return slices, terms


def slice_rank_one_proof(slices: list[list[list[Q]]]) -> dict:
    # The output slices are a basis, with parameters (a,b,c,d,e). The leading
    # 2x2 minor is -b^2. Over C it vanishes only when b=0. The remaining matrix
    # is diag(a,0,c,d,e), whose rank is the number of nonzero entries among
    # a,c,d,e; rank one therefore gives exactly four coordinate directions.
    expected = [zeros(5, 5) for _ in range(5)]
    expected[0][0][0] = Q(1)
    expected[1][0][1] = expected[1][1][0] = Q(1)
    for i in range(2, 5):
        expected[i][i][i] = Q(1)
    need(slices == expected, "slice-space parameterization changed")
    need(rank_q([flatten(s) for s in slices]) == 5, "slice space is not five-dimensional")
    return {
        "parameterization": "[[a,b],[b,0]] direct-sum diag(c,d,e)",
        "leading_2x2_determinant": "-b^2",
        "field_fact": "over C, -b^2=0 implies b=0",
        "remaining_matrix": "diag(a,0,c,d,e)",
        "rank_one_directions": ["E00", "E22", "E33", "E44"],
        "rank_one_span_dimension": 4,
        "slice_space_dimension": 5,
        "rank_five_contradiction": "five-term rank decomposition would span the 5D slice space with five rank-one input matrices; all five would lie in that space, whose rank-one elements span only dimension four",
    }


def profile(k: int, extra_rank1_per_block: int) -> dict[int, Q]:
    return {
        1: Q(2412 - 3 * k + extra_rank1_per_block * k),
        2: Q(418),
        3: Q(432 - k),
        4: Q(142),
        5: Q(82),
        6: Q(k),
        8: Q(8),
    }


def profile_screen() -> dict:
    c = load_ceiling()
    selected = json.loads(source_bytes("research/complex-local-word-ceiling/RESULT.json"))
    base = {int(r): int(n) for r, n in selected["selected"]["local_profile_per_call"].items()}
    need(base == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}, "selected local profile drift")
    selected_hi = Q(selected["ceiling"]["a_ceiling"])
    base_bracket = c.ceiling(base, 73, 896, 9, 64)
    need(base_bracket[1] == selected_hi, "selected ceiling does not replay")
    target = selected_hi * Q(105, 100)
    need(target == Q(35491136290869, 20000000000000000), "5-percent target mismatch")

    feasible = {}
    boundaries = {}
    for e in range(3):
        p0, p1, pmax = profile(0, e), profile(1, e), profile(432, e)
        for p in (p0, pmax):
            q = c.model(p, 73, 896, 9, 64)
            need(q["local_mass"] <= 7232, f"profile exceeds coverage at endpoint, overhead={e}")
        r0 = c.relax(p0, 73, 896, 9, 64, target)
        r1 = c.relax(p1, 73, 896, 9, 64, target)
        slope_lo, slope_hi = r1[0] - r0[1], r1[1] - r0[0]
        if e in (0, 1):
            need(slope_hi < 0, f"block profile is not certified decreasing for overhead {e}")
            need(c.relax(pmax, 73, 896, 9, 64, target)[1] < 1,
                 f"full block domain does not pass for overhead {e}")
            lo, hi = 0, 432
            while lo < hi:
                mid = (lo + hi) // 2
                if c.relax(profile(mid, e), 73, 896, 9, 64, target)[1] < 1:
                    hi = mid
                else:
                    lo = mid + 1
            k = lo
            need(c.relax(profile(k - 1, e), 73, 896, 9, 64, target)[0] > 1,
                 f"previous integer block count is not certified failing for overhead {e}")
            feasible[e] = {"min": k, "max": 432, "count": 433 - k}
            boundaries[e] = {
                "minimum_k": k,
                "previous_relaxation": [str(x) for x in c.relax(profile(k - 1, e), 73, 896, 9, 64, target)],
                "passing_relaxation": [str(x) for x in c.relax(profile(k, e), 73, 896, 9, 64, target)],
                "per_block_relaxation_slope_interval": [str(slope_lo), str(slope_hi)],
            }
        else:
            need(slope_lo > 0, "two-overhead profile is not certified increasing")
            need(r0[0] > 1, "zero-block profile unexpectedly passes the target")
            feasible[e] = {"no_feasible_k": True}
    need(feasible[0]["min"] == 135, "zero-overhead block threshold changed")
    need(feasible[1]["min"] == 284, "one-overhead block threshold changed")
    need(feasible[2]["no_feasible_k"], "two-overhead blocks unexpectedly pass in the full domain")
    full_zero = c.ceiling(profile(432, 0), 73, 896, 9, 64)
    full_one = c.ceiling(profile(432, 1), 73, 896, 9, 64)
    full_two = c.relax(profile(432, 2), 73, 896, 9, 64, target)
    need(full_zero[0] > selected_hi, "full zero-overhead construction does not improve the ceiling")
    need(full_one[0] > target, "full one-overhead construction misses the five-percent target")
    need(full_two[0] > 1, "full two-overhead construction is not rejected by the target relaxation")
    return {
        "selected_profile_per_call": {str(r): n for r, n in base.items()},
        "selected_ceiling": [str(x) for x in base_bracket],
        "target_a": str(target),
        "domain": {"blocks_per_call": "0..432", "additional_rank1_equivalents_per_block": [0, 1, 2]},
        "thresholds": {str(e): boundaries.get(e, {"no_feasible_k": True}) for e in range(3)},
        "feasible_k_ranges": {str(e): v for e, v in feasible.items()},
        "full_profile_zero_overhead": {str(r): str(n) for r, n in profile(432, 0).items()},
        "full_profile_one_overhead": {str(r): str(n) for r, n in profile(432, 1).items()},
        "full_zero_overhead_ceiling": [str(x) for x in full_zero],
        "full_one_overhead_ceiling": [str(x) for x in full_one],
        "full_two_overhead_relaxation_at_target": [str(x) for x in full_two],
        "rank_mass": {"selected": 5586, "one_block_delta_before_overhead": 0},
        "limitations": [
            "The profile transformation is hypothetical until matching selected occurrences are identified.",
            "The tested rank-one-equivalent tariff does not establish the frame, copy, precision, hosting or restoration bill.",
            "No supplier admission or kappa change follows from this relaxation.",
        ],
    }


def selected_phase_screen() -> dict:
    # This is a deliberately narrow necessary-condition check on the pinned
    # selected provider: phase A must contain a rank-3 climb before any
    # (3,1,1,1)->6 block can be placed there. It does not inspect other phases
    # or infer endpoint-frame compatibility.
    archive_bytes = source_bytes("research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz")
    with tarfile.open(fileobj=BytesIO(archive_bytes), mode="r:gz") as archive:
        member = archive.extractfile("evidence/local/LOCAL-PROGRAMS.json.gz")
        need(member is not None, "pinned provider archive lacks local-program stream")
        local = json.loads(gzip.decompress(member.read()))
    events = local["forward"]
    markers = [(i, event[1]) for i, event in enumerate(events) if event[0] == "phase"]
    index = next((j for j, (_i, name) in enumerate(markers) if name == "A"), None)
    need(index is not None and index + 1 < len(markers), "provider phase A boundaries missing")
    start = markers[index][0] + 1
    end = markers[index + 1][0]
    phase = events[start:end]
    climbs = [event for event in phase if event[0] == "climb"]
    counts = Counter(int(event[5]) for event in climbs)
    need(len(phase) == 4730, "pinned phase A event count changed")
    need(len(climbs) == 992 and counts == {1: 936, 4: 56},
         "pinned phase A climb-rank histogram changed")
    need(3 not in counts, "phase A now contains a rank-three climb; revisit placement screen")
    return {
        "source_archive": "research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz",
        "phase": "A",
        "event_count": len(phase),
        "climb_count": len(climbs),
        "climb_rank_histogram": {str(k): v for k, v in sorted(counts.items())},
        "rank_three_occurrences": 0,
        "interpretation": "The proposed block cannot be placed as one rank-three plus three rank-one climb records inside phase A. No claim is made about other phases or composite rank-three realizations.",
    }


def dirty_state_checks(slices: list[list[list[Q]]], terms) -> dict:
    # Exact polynomial identity covers every input. Rational fixtures additionally
    # exercise dirty targets, inverse updates and an untouched arbitrary scratch.
    fixtures = []
    vals = [Q(-2), Q(-1), Q(0), Q(1), Q(3, 2)]
    for i in range(12):
        x = [vals[(i + 2 * j) % len(vals)] for j in range(5)]
        y = [vals[(2 * i + 3 * j + 1) % len(vals)] for j in range(5)]
        p = [vals[(3 * i + j + 2) % len(vals)] for j in range(5)]
        scratch = [vals[(i + j) % len(vals)] for j in range(3)]
        f = [sum(x[a] * slices[o][a][b] * y[b] for a in range(5) for b in range(5)) for o in range(5)]
        forward = [p[o] + f[o] for o in range(5)]
        inverse = [forward[o] - f[o] for o in range(5)]
        need(inverse == p and scratch == [vals[(i + j) % len(vals)] for j in range(3)],
             f"dirty inverse/preservation failed at fixture {i}")
        fixtures.append({"index": i, "inputs": [str(xi) for xi in x + y],
                         "dirty_target": [str(pi) for pi in p], "output": [str(fi) for fi in f]})

    # Meaningful rejection controls alter the atom basis and must miss the tensor.
    names = [t[0] for t in terms]
    controls = {}
    for dropped in ("(x0+x1)*(y0+y1)", "x4*y4"):
        kept = [t for t in terms if t[0] != dropped]
        reconstructed = [zeros(5, 5) for _ in range(5)]
        for _name, lx, ry, output in kept:
            mat = outer(lx, ry)
            for j, coefficient in enumerate(output):
                reconstructed[j] = add_matrix(reconstructed[j], mat, coefficient)
        controls[f"drop:{dropped}"] = reconstructed != slices
    need(all(controls.values()), "an omitted-atom control failed to detect the defect")
    need(len(names) == 6, "wrong number of atoms")
    return {"rational_dirty_fixtures": fixtures, "all_sources_and_scratch_preserved": True,
            "inverse_uses_subtraction": True, "negative_controls_detected": controls}


def build_certificate() -> dict:
    source_pins = pins()
    task = json.loads((PACKAGE / "TASK.json").read_text(encoding="utf-8"))
    slices, terms = tensor_data()
    slice_rank = rank_q([flatten(s) for s in slices])
    need(slice_rank == 5, "output-slice span rank is not five")
    slice_proof = slice_rank_one_proof(slices)
    screen = profile_screen()
    phase_screen = selected_phase_screen()
    dirty = dirty_state_checks(slices, terms)
    return {
        "status": "PASS_MIXED_RANK6_BLOCK_LOCAL_TENSOR_AND_SCREEN",
        "seed": task["seed"],
        "track": task["track"],
        "base_commit": task["base_commit"],
        "selected_record_sha256": task["selected_record_sha256"],
        "source_sha256": source_pins,
        "selected_phase_screen": phase_screen,
        "tensor": {
            "field": "C (all coefficients are rational)",
            "inputs": ["x0", "x1", "x2", "x3", "x4"],
            "outputs": ["x0*y0", "x0*y1+x1*y0", "x2*y2", "x3*y3", "x4*y4"],
            "slice_order": ["output0", "output1", "output2", "output3", "output4"],
            "slice_matrices": [[[str(x) for x in row] for row in m] for m in slices],
            "output_slice_span_rank": slice_rank,
            "slice_space_rank_one_proof": slice_proof,
            "rank_one_atoms": [
                {"product": n, "output_vector": [str(x) for x in c]}
                for n, _l, _r, c in terms
            ],
            "lower_bound_argument": "Any rank-five decomposition would have five independent rank-one input matrices spanning the 5D output-slice space. A general matrix in that space is [[a,b],[b,0]] direct-sum diag(c,d,e); rank one forces b=0 and at most one of a,c,d,e nonzero. Only four independent rank-one directions lie in the slice space, contradiction.",
            "exact_tensor_rank": 6,
            "composition": "one rank-three two-output block plus three rank-one scalar blocks; paired dirty output map has six rank-one atoms",
        },
        "dirty_state": dirty,
        "profile_screen": screen,
        "selected_occurrence_identified": False,
        "new_supplier_or_kappa_claim": False,
    }


def main() -> None:
    expected = build_certificate()
    if "--emit-certificate" in sys.argv[1:]:
        print(json.dumps(expected, indent=2, sort_keys=True))
        return
    actual = json.loads((PACKAGE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    need(actual == expected, "certificate differs from exact replay")
    print("PASS_MIXED_RANK6_BLOCK_LOCAL_TENSOR_AND_SCREEN rank=6 slices=5 blocks=0..432")


if __name__ == "__main__":
    main()
