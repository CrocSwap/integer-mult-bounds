#!/usr/bin/env python3
"""Finite F2 routines for the five-plane P112 port construction."""
from __future__ import annotations
import hashlib, importlib.util, json, random, tarfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PORTS, DIM = 112, 9
SEED = "1f7fdfe435b7ba318188ae826892153b"
ARCHIVE_MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
def need(ok: bool, why: str) -> None:
    if not ok: raise ValueError(why)
def dot(a: int, b: int) -> int: return (a & b).bit_count() & 1
def rank_rows(rows: list[int], width: int) -> int:
    pivots = {}
    for value0 in rows:
        value = value0
        while value:
            p = value.bit_length() - 1
            if p in pivots: value ^= pivots[p]
            else: pivots[p] = value; break
    return len(pivots)
def indices(mask: int, n: int = PORTS) -> list[int]:
    return [i for i in range(n) if (mask >> i) & 1]
def load_sources() -> tuple[list[int], dict]:
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    for row in manifest["files"]:
        if row["usage"] == "input":
            path = ROOT / row["path"]
            need(path.is_file(), "missing pinned input: " + row["path"])
            need(hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
                 "live input hash mismatch: " + row["path"])
    archive = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
    with tarfile.open(archive, "r:gz") as tf:
        member = tf.extractfile(ARCHIVE_MEMBER)
        need(member is not None, "selected DATA-PHASES member missing")
        data = json.loads(member.read())
    need(data["ports"] == PORTS, "selected port count")
    recipes = sorted(data["recipes"], key=lambda x: x["port"])
    need(len(recipes) == PORTS and [x["port"] for x in recipes] == list(range(PORTS)),
         "selected recipe order/count")
    labels = [x["q"] for x in recipes]
    need(len(set(labels)) == PORTS and all(0 < q < (1 << DIM) for q in labels),
         "selected labels distinct 9-bit values")
    need(all(q.bit_count() in (3, 7) for q in labels), "selected label weight")
    # Positive control: the pinned predecessor's 56 zero-dot pairs still cover P112.
    cert = json.loads((ROOT / "research/paired-plane-port-matching-seed6c563a/CERTIFICATE.json").read_text())
    pairs = cert["matching"]
    used = []
    for pair in pairs:
        need(len(pair) == 2 and pair[0] != pair[1], "paired-plane control edge")
        need(dot(labels[pair[0]], labels[pair[1]]) == 0, "paired-plane control orthogonality")
        used.extend(pair)
    need(len(pairs) == PORTS // 2 and sorted(used) == list(range(PORTS)),
         "paired-plane control is not a perfect matching")
    return labels, data
def orthogonal_pair(mask: int, labels: list[int]) -> bool:
    pair = indices(mask, len(labels))
    return len(pair) == 2 and dot(labels[pair[0]], labels[pair[1]]) == 0
def five_frame_incidence(labels: list[int]) -> tuple[list[list[int]], int]:
    """Enumerate all five-cliques in the selected-label orthogonality graph."""
    n = len(labels); adjacency = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if dot(labels[i], labels[j]) == 0:
                adjacency[i] |= 1 << j; adjacency[j] |= 1 << i
    by_port = [[] for _ in labels]; total = 0
    def visit(prefix: list[int], candidates: int) -> None:
        nonlocal total
        if len(prefix) == 5:
            mask = sum(1 << i for i in prefix); total += 1
            for i in prefix: by_port[i].append(mask)
            return
        while candidates:
            bit = candidates & -candidates; i = bit.bit_length() - 1; candidates ^= bit
            visit(prefix + [i], candidates & adjacency[i])
    visit([], (1 << n) - 1)
    return by_port, total
def find_cover(labels: list[int], max_attempts: int = 10_000) -> dict | None:
    """Seeded randomized greedy cover; stops at the first exact 5-frame cover."""
    by_port, frame_count = five_frame_incidence(labels)
    rng = random.Random(int(SEED, 16))
    full = (1 << len(labels)) - 1
    nodes = 0
    for attempt in range(1, max_attempts + 1):
        remaining = full
        groups: list[list[int]] = []
        while remaining.bit_count() > 2:
            nodes += 1
            if remaining.bit_count() == 7:
                candidates = []
                for i in indices(remaining, len(labels)):
                    for frame in by_port[i]:
                        if (frame & remaining) == frame and (remaining ^ frame).bit_count() == 2 \
                                and orthogonal_pair(remaining ^ frame, labels):
                            candidates.append(frame)
            else:
                i = (remaining & -remaining).bit_length() - 1
                candidates = [frame for frame in by_port[i] if (frame & remaining) == frame]
            if not candidates:
                break
            chosen = rng.choice(candidates)
            groups.append(indices(chosen, len(labels)))
            remaining ^= chosen
        if remaining.bit_count() == 2 and orthogonal_pair(remaining, labels):
            return {"groups": groups, "residual": indices(remaining, len(labels)),
                    "attempt": attempt, "greedy_steps": nodes,
                    "five_frame_count": frame_count, "attempt_cap": max_attempts}
    return None

def xor_selected(values: list[int], mask: int) -> int:
    result = 0
    for i, value in enumerate(values):
        if (mask >> i) & 1: result ^= value
    return result

def solve_identity(blocks: list[list[int]], labels: list[int]) -> list[list[list[int]]] | None:
    """Deterministic column-echelon solution of sum A_g M_g A_g^T = I_9 over F2."""
    variables = [(g, a, b) for g in blocks for a in range(len(g)) for b in range(len(g))]
    basis: list[tuple[int, int] | None] = [None] * (DIM * DIM)
    for z, (g, a, b) in enumerate(variables):
        value = 0
        for r in range(DIM):
            if (labels[g[a]] >> r) & 1:
                for c in range(DIM):
                    if (labels[g[b]] >> c) & 1: value |= 1 << (r * DIM + c)
        coefficients = 1 << z
        while value:
            pivot = value.bit_length() - 1
            if basis[pivot] is None:
                basis[pivot] = (value, coefficients); break
            vector, combo = basis[pivot]; value ^= vector; coefficients ^= combo
    target = sum(1 << (r * DIM + r) for r in range(DIM)); solution = 0
    while target:
        pivot = target.bit_length() - 1
        if basis[pivot] is None: return None
        vector, combo = basis[pivot]; target ^= vector; solution ^= combo
    matrices = []; z = 0
    for g in blocks:
        d = len(g); matrix = [[0] * d for _ in range(d)]
        for a in range(d):
            for b in range(d): matrix[a][b] = (solution >> z) & 1; z += 1
        matrices.append(matrix)
    need(z == len(variables), "internal coefficient count")
    return matrices

def factor_matrix(group: list[int], matrix: list[list[int]], labels: list[int], block: int) -> list[dict]:
    d = len(group)
    columns = [sum((matrix[r][c] & 1) << r for r in range(d)) for c in range(d)]
    basis: list[int] = []
    for col in columns:
        if rank_rows(basis + [col], d) > len(basis): basis.append(col)
    terms = []
    for k, left_coeff in enumerate(basis):
        coordinates = []
        for col in columns:
            match = next((mask for mask in range(1 << len(basis))
                          if xor_selected(basis, mask) == col), None)
            need(match is not None, "matrix column outside its basis"); coordinates.append(match)
        right_coeff = sum(1 << j for j, coords in enumerate(coordinates) if (coords >> k) & 1)
        left_label = xor_selected([labels[i] for i in group], left_coeff)
        right_label = xor_selected([labels[i] for i in group], right_coeff)
        left_support = [i for i, q in enumerate(labels) if dot(q, left_label)]
        right_support = [i for i, q in enumerate(labels) if dot(q, right_label)]
        pair_rows = [sum(dot(labels[i], labels[j]) << k for k, j in enumerate(right_support))
                     for i in left_support]
        copy_rank = rank_rows(pair_rows, len(right_support))
        terms.append({"block": block, "group": group, "left_coeff": left_coeff,
                      "right_coeff": right_coeff, "left_label": left_label,
                      "right_label": right_label, "left_support": left_support,
                      "right_support": right_support, "copy_rank": copy_rank})
    for r in range(d):
        for c in range(d):
            got = 0
            for term in terms:
                got ^= ((term["left_coeff"] >> r) & 1) & ((term["right_coeff"] >> c) & 1)
            need(got == matrix[r][c], "rank-one factors do not reconstruct their block")
    return terms
def load_ceiling():
    path = ROOT / "research/complex-local-word-ceiling/ceiling.py"
    spec = importlib.util.spec_from_file_location("pinned_complex_ceiling", path)
    need(spec is not None and spec.loader is not None, "ceiling module load")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

def profile_for(copy_hist: dict[int, int]) -> tuple[dict[int, int], int]:
    profile = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
    profile[8] -= 8
    for rank, count in copy_hist.items(): profile[rank] = profile.get(rank, 0) + count
    return profile, sum(rank * count for rank, count in copy_hist.items())

def moment_screen(profile: dict[int, int], centre: int) -> dict:
    from fractions import Fraction
    module = load_ceiling(); a = Fraction(1, 99)
    moment = module.relax(profile, 73, 896, 9, centre, a, unpaid=5)
    cap = module.ceiling(profile, 73, 896, 9, centre, unpaid=5)
    return {"moment_lower": str(moment[0]), "moment_upper": str(moment[1]),
            "moment_lower_decimal": float(moment[0]), "moment_upper_decimal": float(moment[1]), "ceiling_lower": str(cap[0]),
            "ceiling_upper": str(cap[1]), "ceiling_upper_decimal": float(cap[1])}

def all_in_rank1_threshold(profile: dict[int, int], centre: int) -> dict:
    from fractions import Fraction
    module = load_ceiling(); lo, hi = centre, 1000
    while hi - lo > 1:
        mid = (lo + hi) // 2; trial = profile.copy(); trial[1] += mid - centre
        if module.relax(trial, 73, 896, 9, mid, Fraction(1, 99), unpaid=5)[1] < 1:
            lo = mid
        else: hi = mid
    values = []
    for total in (lo, hi):
        trial = profile.copy(); trial[1] += total - centre
        values.append({"total_rank1_equivalent_charge": total,
                       "extra_rank1_equivalent_charge": total - centre,
                       **moment_screen(trial, total)})
    return {"largest_passing": values[0], "first_failing": values[1]}

def make_candidate(cover: dict, labels: list[int]) -> dict:
    groups = cover["groups"]; blocks = groups + [cover["residual"]]
    matrices = solve_identity(blocks, labels)
    need(matrices is not None, "cover does not span the identity equation")
    terms = [term for b, (g, matrix) in enumerate(zip(blocks, matrices))
             for term in factor_matrix(g, matrix, labels, b)]
    histogram: dict[int, int] = {}
    for term in terms:
        charge = term["copy_rank"]
        need(charge > 0, "zero-copy term is outside this priced interface")
        histogram[charge] = histogram.get(charge, 0) + 1
    copy_charge = sum(rank * count for rank, count in histogram.items())
    profile, centre = profile_for(histogram)
    need(centre == copy_charge, "centre charge mismatch")
    shift_blocks = len(blocks)
    shifted_profile = profile.copy(); shifted_profile[1] += shift_blocks
    return {**cover, "blocks": blocks, "coefficient_matrices": matrices, "terms": terms,
            "term_count": len(terms),
            "copy_rank_histogram": {str(k): v for k, v in sorted(histogram.items())},
            "copy_charge": copy_charge,
            "local_profile": {str(k): v for k, v in sorted(profile.items()) if v},
            "local_mass": sum(k * v for k, v in profile.items()),
            "moment_screen_u5": moment_screen(profile, centre),
            "aggregate_translation_count": shift_blocks,
            "one_unit_per_aggregate_translation_screen": moment_screen(
                shifted_profile, centre + shift_blocks),
            "all_in_rank1_overhead_threshold": all_in_rank1_threshold(profile, centre)}
