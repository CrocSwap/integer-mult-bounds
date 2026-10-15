#!/usr/bin/env python3
"""Exact rational rank-9 decomposition and conditional local-cost screen for Q[S3]."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import io
import itertools
import json
import tarfile
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
MEMBER = "candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz"
ARCHIVE_SHA256 = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBER_SHA256 = "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a"
SELECTED_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
CEILING_SHA256 = "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc"
BASE_PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
M, FAMILIES, STAGES, CENTRE = 73, 896, 9, 64
BASE_UPPER = Q(1690054109089, 10**15)
TARGET = BASE_UPPER * Q(21, 20)


def need(ok: bool, why: str) -> None:
    if not ok:
        raise AssertionError(why)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def add(x, y):
    return tuple(a + b for a, b in zip(x, y))


def sub(x, y):
    return tuple(a - b for a, b in zip(x, y))


def scale(c, x):
    return tuple(c * a for a in x)


def dot(x, y):
    return sum((a * b for a, b in zip(x, y)), Q(0))


def rational_rank(rows):
    a = [list(map(Q, row)) for row in rows]
    if not a:
        return 0
    pivot = 0
    for col in range(len(a[0])):
        row = next((i for i in range(pivot, len(a)) if a[i][col]), None)
        if row is None:
            continue
        a[pivot], a[row] = a[row], a[pivot]
        d = a[pivot][col]
        a[pivot] = [x / d for x in a[pivot]]
        for i in range(len(a)):
            if i != pivot and a[i][col]:
                d = a[i][col]
                a[i] = [x - d * y for x, y in zip(a[i], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def mmul(a, b):
    return tuple(tuple(sum((a[i][k] * b[k][j] for k in range(2)), Q(0))
                       for j in range(2)) for i in range(2))


def inv_perm(g):
    out = [0] * 3
    for i, j in enumerate(g):
        out[j] = i
    return tuple(out)


def compose(g, h):
    """Function composition g after h."""
    return tuple(g[h[i]] for i in range(3))


def sign(g):
    return -1 if sum(g[i] > g[j] for i in range(3) for j in range(i + 1, 3)) % 2 else 1


def rho(g):
    """Standard two-dimensional S3 representation on sum-zero Q^3.

    Basis b1=e0-e1, b2=e1-e2. Coordinates of v=(v0,v1,v2), sum(v)=0,
    are (v0,-v2).
    """
    basis = ((1, -1, 0), (0, 1, -1))
    cols = []
    for v in basis:
        image = [0, 0, 0]
        for i, coeff in enumerate(v):
            image[g[i]] += coeff
        cols.append((Q(image[0]), Q(-image[2])))
    return ((cols[0][0], cols[1][0]), (cols[0][1], cols[1][1]))


def fourier_forms():
    """Rows mapping group coefficients to (trivial, sign, standard matrix entries)."""
    gs = tuple(itertools.permutations(range(3)))
    rows = [tuple(Q(1) for _ in gs), tuple(Q(sign(g)) for g in gs)]
    for i in range(2):
        for j in range(2):
            rows.append(tuple(rho(g)[i][j] for g in gs))
    return gs, tuple(rows)


def linear_combination(rows, coeffs):
    out = [Q(0)] * len(rows[0])
    for c, row in zip(coeffs, rows):
        if c:
            out = [x + c * y for x, y in zip(out, row)]
    return tuple(out)


def strassen_forms(component_rows):
    """Return the seven left and right linear forms for 2x2 matrix multiplication."""
    a, b, c, d = component_rows
    left = (add(a, d), add(c, d), a, d, add(a, b), sub(c, a), sub(b, d))
    right = (add(a, d), a, sub(b, d), sub(c, a), d, add(a, b), add(c, d))
    return left, right


def strassen_products(A, B):
    a, b, c, d = A[0][0], A[0][1], A[1][0], A[1][1]
    e, f, g, h = B[0][0], B[0][1], B[1][0], B[1][1]
    p1 = (a + d) * (e + h)
    p2 = (c + d) * e
    p3 = a * (f - h)
    p4 = d * (g - e)
    p5 = (a + b) * h
    p6 = (c - a) * (e + f)
    p7 = (b - d) * (g + h)
    return (p1, p2, p3, p4, p5, p6, p7)


def strassen_recombine(p):
    p1, p2, p3, p4, p5, p6, p7 = p
    return ((p1 + p4 - p5 + p7, p3 + p5),
            (p2 + p4, p1 - p2 + p3 + p6))


def inverse_fourier(alpha, beta, Mx, g):
    R = rho(inv_perm(g))
    tr = sum((mmul(R, Mx)[i][i] for i in range(2)), Q(0))
    return (alpha + sign(g) * beta + 2 * tr) / 6


def rank9_terms():
    """Build u_i(x) v_i(y) w_i as nine rank-one tensors over Q."""
    gs, F = fourier_forms()
    alpha, beta = F[0], F[1]
    Mrows = F[2:]
    # Term 0: trivial representation; term 1: sign representation.
    left = [alpha, beta]
    right = [alpha, beta]
    # Standard 2x2 representation, then Strassen's seven products.
    left2, right2 = strassen_forms(Mrows)
    left.extend(left2)
    right.extend(right2)
    # Recombination coefficient of each Strassen product in each matrix entry.
    # Matrix entry coefficient rows are indexed p1..p7.
    rec = (
        ((1, 0, 0, 1, -1, 0, 1), (0, 0, 1, 0, 1, 0, 0)),
        ((0, 1, 0, 1, 0, 0, 0), (1, -1, 1, 0, 0, 1, 0)),
    )
    weights = []
    for j in range(9):
        if j == 0:
            weights.append(tuple(Q(1, 6) for _ in gs))
            continue
        if j == 1:
            weights.append(tuple(Q(sign(g), 6) for g in gs))
            continue
        coeff_matrix = [[Q(0), Q(0)], [Q(0), Q(0)]]
        pidx = j - 2
        for i in range(2):
            for k in range(2):
                coeff_matrix[i][k] = Q(rec[i][k][pidx])
        weights.append(tuple(inverse_fourier(Q(0), Q(0), coeff_matrix, g) for g in gs))
    return gs, tuple(left), tuple(right), tuple(weights)


def naive_product(x, y, gs):
    index = {g: i for i, g in enumerate(gs)}
    out = [Q(0)] * 6
    for i, g in enumerate(gs):
        for j, h in enumerate(gs):
            out[index[compose(g, h)]] += x[i] * y[j]
    return tuple(out)


def evaluate_terms(x, y, U, V, W):
    out = [Q(0)] * 6
    for u, v, w in zip(U, V, W):
        z = dot(u, x) * dot(v, y)
        out = [a + z * b for a, b in zip(out, w)]
    return tuple(out)


def source_profile():
    archive_bytes = ARCHIVE.read_bytes()
    need(digest(archive_bytes) == ARCHIVE_SHA256, "selected replay archive hash")
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
        member = archive.extractfile(MEMBER)
        need(member is not None, "selected local program member missing")
        compressed = member.read()
    need(digest(compressed) == MEMBER_SHA256, "selected local program member hash")
    program = json.loads(gzip.decompress(compressed))
    profiles = {}
    for orientation, events in program.items():
        counts = Counter(int(e[5]) for e in events if e and e[0] == "climb")
        counts[8] += sum(1 for e in events if e and e[0] == "center")
        profiles[orientation] = dict(sorted(counts.items()))
    need(profiles["forward"] == BASE_PROFILE, "forward selected profile changed")
    need(profiles["backward"] == BASE_PROFILE, "backward selected profile changed")
    return profiles


def load_ceiling():
    path = ROOT / "research/complex-local-word-ceiling/ceiling.py"
    raw = path.read_bytes()
    need(digest(raw) == CEILING_SHA256, "ceiling engine pin")
    spec = importlib.util.spec_from_file_location("pinned_ceiling", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="create RESULT.json; refuses overwrite")
    args = parser.parse_args()
    selected_bytes = (ROOT / "certificates/selected-result.json").read_bytes()
    need(digest(selected_bytes) == SELECTED_SHA256, "selected record pin")
    selected = json.loads(selected_bytes)
    need(selected["kappa"] == "836330098538459/500000000000000000", "selected kappa changed")
    profiles = source_profile()

    gs, U, V, W = rank9_terms()
    need(len(U) == len(V) == len(W) == 9, "rank-9 term count")
    # Representation law and inverse Fourier transform on all six group basis elements.
    for g in gs:
        for h in gs:
            need(mmul(rho(g), rho(h)) == rho(compose(g, h)), "standard representation homomorphism")
    for i in range(6):
        x = tuple(Q(int(j == i)) for j in range(6))
        for j in range(6):
            y = tuple(Q(int(k == j)) for k in range(6))
            need(evaluate_terms(x, y, U, V, W) == naive_product(x, y, gs),
                 "rank-9 formula failed on group basis pair")
    # Deterministic integer trials, arbitrary dirty outputs, and additive inverse restoration.
    fixtures = 0
    for trial in range(256):
        x = tuple(Q(((trial + 3) * (i + 5) ** 2) % 31 - 15) for i in range(6))
        y = tuple(Q(((trial + 7) * (i + 2) ** 3) % 37 - 18) for i in range(6))
        dirty = tuple(Q(((trial + 11) * (i + 1) ** 2) % 101 - 50) for i in range(6))
        value = evaluate_terms(x, y, U, V, W)
        need(value == naive_product(x, y, gs), "integer fixture mismatch")
        out = tuple(a + b for a, b in zip(dirty, value))
        restored = tuple(a - b for a, b in zip(out, value))
        need(restored == dirty, "dirty output restoration")
        need(all(v.denominator == 1 for v in value), "integer convolution output not integral")
        fixtures += 1
    # A semantic negative control: find a basis pair that detects an omitted term.
    omitted_detected = False
    for i in range(6):
        for j in range(6):
            x = tuple(Q(int(k == i)) for k in range(6))
            y = tuple(Q(int(k == j)) for k in range(6))
            bad = evaluate_terms(x, y, U[:-1], V[:-1], W[:-1])
            if bad != naive_product(x, y, gs):
                omitted_detected = True
                break
        if omitted_detected:
            break
    need(omitted_detected, "omitted-term control did not reject")

    ceiling = load_ceiling()
    baseline = ceiling.ceiling(BASE_PROFILE, M, FAMILIES, STAGES, CENTRE)
    need(baseline[1] == BASE_UPPER, "baseline ceiling changed")
    screens = {}
    for k in (7, 8):
        p = dict(BASE_PROFILE)
        p[1] -= 36 * k
        p[9] = k
        interval = ceiling.ceiling(p, M, FAMILIES, STAGES, CENTRE)
        at_target = ceiling.relax(p, M, FAMILIES, STAGES, CENTRE, TARGET)
        screens[k] = {"profile": p, "ceiling": [interval[0], interval[1]],
                      "moment_at_target": [at_target[0], at_target[1]]}
    need(screens[7]["moment_at_target"][0] > 1, "7-block negative boundary")
    need(screens[8]["moment_at_target"][1] < 1, "8-block positive boundary")
    need(screens[8]["moment_at_target"][1] < screens[7]["moment_at_target"][0],
         "adding one S3 block must lower the relaxed moment")
    need(screens[8]["ceiling"][0] > TARGET, "8-block ceiling not above target")
    # The threshold uses only the count ceiling, not an existence claim about source supports.
    max_blocks_by_count = BASE_PROFILE[1] // 36
    need(max_blocks_by_count == 67, "selected rank-one count capacity changed")

    # An exact child-rank overhead screen, in addition to the waived linear costs.
    extra_rank1 = 0
    for t in range(1, 100):
        p = dict(screens[8]["profile"])
        p[1] += t
        if ceiling.relax(p, M, FAMILIES, STAGES, CENTRE, TARGET)[1] < 1:
            extra_rank1 = t
        else:
            break
    need(extra_rank1 == 1, "rank-one-equivalent overhead boundary changed")

    def rows(A):
        return [[str(x) for x in row] for row in A]

    def profile_text(profile):
        return {str(r): n for r, n in sorted(profile.items())}

    supports = {name: [sum(x != 0 for x in row) for row in A]
                for name, A in (("left", U), ("right", V), ("output", W))}
    nonzero = {name: sum(x != 0 for row in A for x in row)
               for name, A in (("left", U), ("right", V), ("output", W))}
    output_terms_by_coordinate = [sum(W[i][j] != 0 for i in range(9)) for j in range(6)]
    transform_ranks = {name: rational_rank(A)
                       for name, A in (("left", U), ("right", V), ("output", W))}
    need(transform_ranks == {"left": 6, "right": 6, "output": 6},
         "input/output transform information rank")
    max_den = max(x.denominator for row in W for x in row)
    additions_per_side = sum(n - 1 for n in supports["left"])
    base_mass = sum(r * n for r, n in BASE_PROFILE.items())
    candidate_mass = sum(r * n for r, n in screens[8]["profile"].items())
    candidate_model = ceiling.model(screens[8]["profile"], M, FAMILIES, STAGES, CENTRE)
    result = {
        "schema_version": 1,
        "construction": "Q[S3] regular convolution via Q x Q x M2(Q) and Strassen",
        "group_order": [list(g) for g in gs],
        "tensor_terms": 9,
        "naive_pair_products": 36,
        "left_forms": rows(U),
        "right_forms": rows(V),
        "output_forms": rows(W),
        "linear_supports": supports,
        "linear_nonzero_entries": nonzero,
        "linear_transform_ranks": transform_ranks,
        "naive_linear_invoice": {
            "input_add_subtracts_per_side": additions_per_side,
            "input_nonunit_scalings_per_side": 1,
            "output_nonzero_scatter_terms": nonzero["output"],
            "output_terms_per_coordinate": output_terms_by_coordinate,
            "output_additions_after_zero_initialization": nonzero["output"] - 6,
            "output_common_denominator": 6,
            "output_exact_divisions_by_six": 6,
            "comment": "literal no-sharing count; scalar operations are separate from recursive child charges"
        },
        "selected_source": {
            "archive_sha256": ARCHIVE_SHA256,
            "member": MEMBER,
            "member_sha256": MEMBER_SHA256,
            "profiles_by_orientation": {k: profile_text(v) for k, v in profiles.items()},
            "rank1_count_per_orientation": BASE_PROFILE[1],
            "count_only_maximum_blocks": max_blocks_by_count,
            "matching_support_occurrences_established": 0
        },
        "cost_model": {
            "width": M, "families": FAMILIES, "stages": STAGES, "centre": CENTRE,
            "baseline_ceiling": [str(baseline[0]), str(baseline[1])],
            "target_a": str(TARGET),
            "baseline_local_rank_mass": base_mass,
            "eight_block_local_rank_mass": candidate_mass,
            "rank_mass_released_to_idle_per_eight_blocks": base_mass - candidate_mass,
            "eight_block_idle_mass": str(candidate_model["idle_mass"]),
            "eight_block_ceiling_gain_fraction_vs_baseline_upper":
                str(screens[8]["ceiling"][1] / baseline[1] - 1),
            "blocks": {str(k): {
                "profile": profile_text(screens[k]["profile"]),
                "ceiling": [str(screens[k]["ceiling"][0]), str(screens[k]["ceiling"][1])],
                "moment_at_target": [str(screens[k]["moment_at_target"][0]),
                                     str(screens[k]["moment_at_target"][1])]
            } for k in (7, 8)},
            "minimum_zero_overhead_blocks_to_pass_5pct": 8,
            "maximum_added_rank1_calls_after_8_blocks": extra_rank1,
            "assumptions_waived_for_screen": [
                "source and target support realization", "linear transforms", "copying",
                "frame changes", "scratch hosting", "output scattering", "precision",
                "dirty-state restoration", "interface transitions"
            ],
            "status": "conditional local screen only; no supplier or kappa"
        },
        "negative_control": "omitting one Strassen product is detected on a group-basis pair"
    }
    result_path = Path(__file__).resolve().parent / "RESULT.json"
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        need(not result_path.exists(), "refusing to overwrite RESULT.json")
        result_path.write_text(encoded, encoding="utf-8")
    else:
        need(result_path.is_file(), "RESULT.json missing; run verify.py --write once")
        need(result_path.read_text(encoding="utf-8") == encoded, "RESULT.json differs from exact replay")

    print("PASS_S3_GROUP_ALGEBRA_RANK9 basis_pairs=36 integer_dirty_fixtures="
          f"{fixtures} controls=1 rank1_capacity={BASE_PROFILE[1]} max_blocks={max_blocks_by_count} "
          f"zero_overhead_threshold=8 local_only")


if __name__ == "__main__":
    main()
