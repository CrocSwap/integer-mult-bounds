#!/usr/bin/env python3
"""Exact bounded P112 term-gauge search and selected-profile screen.

Searches every rational Householder reflection with ternary normal in ten
term coordinates. Ordinary-transpose exactness follows from O O^T = I; the
base witness and the winning transformed identity are also checked directly.
"""
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import math
import sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WITNESS_PATH = HERE / "WITNESS.json"
RESULT_PATH = HERE / "RESULT.json"
SELECTED_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
CATALOG_SHA256 = "6686ad58f1fbdbc87134a78901b60fd53a20d3984355e91defbbebc9e9fa8075"
CEILING_SHA256 = "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc"
PRED_RESULT_SHA256 = "f62fbac3f31d088c9b81a7a01b2012145589b1bb5687f6c5e70be786b17745c2"
PRED_RESULT_BLOB = "0c1a85768b3e3dbb727149b3a8dbb345ff029f88"
PRED_HEAD = "652264fa1f70820139b2730363a0056b7fadc689"
WITNESS_SHA256 = "eb2d042139f4cc369389311b7ed0cea7bb523a112114fb5f767024aff34473b3"
BASE_PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
BASE_CENTRE = 64
BASE_A_HI = Q(1690054109089, 10**15)
TARGET_A = BASE_A_HI * Q(21, 20)
HOUSEHOLDERS = (3**10 - 1) // 2


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_ceiling():
    path = ROOT / "research/complex-local-word-ceiling/ceiling.py"
    spec = importlib.util.spec_from_file_location("p112_gauge_ceiling", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def roots_p112():
    lines = []
    for a, b in itertools.combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[a], row[b] = 2, sign * 2
            lines.append(tuple(row))
    for signs in itertools.product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            lines.append((1, *signs))
    removed = set()
    for a in range(0, 8, 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[a], row[a + 1] = 2, sign * 2
            removed.add(tuple(row))
    roots = sorted(set(lines) - removed)
    require(len(roots) == 112 and len(set(roots)) == 112, "P112 root construction")
    require(all(sum(r[a] * r[b] for r in roots) == 112 * (a == b)
                for a in range(8) for b in range(8)), "P112 Gram identity")
    return roots


def parse_witness():
    raw = WITNESS_PATH.read_bytes()
    record = json.loads(raw)
    origin = record["origin"]
    require(origin["pr"] == 1633 and origin["head"] == PRED_HEAD, "predecessor head pin")
    require(origin["path"] == "research/decoder-excess-rank/RESULT.json", "predecessor path pin")
    require(origin["git_blob"] == PRED_RESULT_BLOB and origin["sha256"] == PRED_RESULT_SHA256,
            "predecessor result pin")
    witness = record["representative"]
    require(witness["domain"] == "P112", "witness domain")
    require(witness["costs"] == [8] * 8 + [9, 9], "predecessor cost receipt")
    require(witness["mixed_costs"] == [9] * 10, "predecessor gauge control receipt")
    encoded = witness["D"]
    require(len(encoded) == 112 and all(len(row) == 10 for row in encoded), "witness shape")
    parsed = [[(Q(cell[0]), Q(cell[1])) for cell in row] for row in encoded]
    den = math.lcm(*(part.denominator for row in parsed for cell in row for part in cell))
    matrix = [[(int(cell[0] * den), int(cell[1] * den)) for cell in row] for row in parsed]
    return record, matrix, den


def pairing_rows(roots):
    return [sum(((((sum(x * y for x, y in zip(ra, rb)) // 4) + 1) % 2) << j)
                for j, rb in enumerate(roots)) for ra in roots]


def gf2_rank(mask_rows):
    pivots = {}
    rank = 0
    for value in mask_rows:
        while value:
            pivot = value.bit_length() - 1
            old = pivots.get(pivot)
            if old is None:
                pivots[pivot] = value
                rank += 1
                break
            value ^= old
    return rank


def support_bill(matrix, pair_rows, rank_cache):
    costs = []
    masks = []
    for k in range(10):
        support = 0
        for i, row in enumerate(matrix):
            if row[k] != (0, 0):
                support |= 1 << i
        masks.append(support)
        if support not in rank_cache:
            selected = []
            todo = support
            while todo:
                bit = todo & -todo
                i = bit.bit_length() - 1
                selected.append(pair_rows[i] & support)
                todo ^= bit
            rank_cache[support] = gf2_rank(selected)
        costs.append(rank_cache[support])
    return costs, masks


def identity(matrix, den, roots):
    for i, ri in enumerate(roots):
        for j, rj in enumerate(roots):
            re = im = 0
            for ar, ai in zip(matrix[i], matrix[j]):
                re += ar[0] * ai[0] - ar[1] * ai[1]
                im += ar[0] * ai[1] + ar[1] * ai[0]
            if im or 2 * re != den * den * sum(x * y for x, y in zip(ri, rj)):
                return False
    return True


def householder_numerator(matrix, s, scale=2):
    norm = sum(x * x for x in s)
    require(norm > 0, "zero Householder normal")
    total = []
    for row in matrix:
        total.append((sum(s[k] * row[k][0] for k in range(10)),
                      sum(s[k] * row[k][1] for k in range(10))))
    out = []
    for i, row in enumerate(matrix):
        outrow = []
        for j in range(10):
            c = scale * s[j]
            outrow.append((norm * row[j][0] - c * total[i][0],
                           norm * row[j][1] - c * total[i][1]))
        out.append(outrow)
    return out, norm


def is_canonical(s):
    first = next((x for x in s if x), 0)
    return first == 1


def orthogonal_numerator(s):
    norm = sum(x * x for x in s)
    mat = [[norm * (i == j) - 2 * s[i] * s[j] for j in range(10)] for i in range(10)]
    return norm, mat


def profile_for(costs):
    profile = dict(BASE_PROFILE)
    profile[8] -= 8
    for r, n in Counter(costs).items():
        profile[r] = profile.get(r, 0) + n
    return {r: n for r, n in profile.items() if n}


def screen_profile(profile, centre, model):
    return model.ceiling(profile, 73, 896, 9, centre, grid=Q(1, 10**18))


def run():
    require(sha256(ROOT / "certificates/selected-result.json") == SELECTED_SHA256,
            "selected record SHA-256")
    require(sha256(ROOT / "docs/research/agent-task-catalog.json") == CATALOG_SHA256,
            "priority catalogue SHA-256")
    require(sha256(ROOT / "research/complex-local-word-ceiling/ceiling.py") == CEILING_SHA256,
            "ceiling source SHA-256")
    require(sha256(WITNESS_PATH) == WITNESS_SHA256, "derived witness input SHA-256")

    record, base, den = parse_witness()
    roots = roots_p112()
    pairs = pairing_rows(roots)
    require(gf2_rank(pairs) == 9, "P112 label rank")
    require(identity(base, den, roots), "predecessor P112 identity")
    cache = {}
    base_costs, base_masks = support_bill(base, pairs, cache)
    require(base_costs == [8] * 8 + [9, 9], "exact predecessor support invoice")

    # Positive and negative controls.
    axis = (1,) + (0,) * 9
    axis_num, axis_norm = householder_numerator(base, axis)
    axis_costs, _ = support_bill(axis_num, pairs, cache)
    require(axis_norm == 1 and axis_costs == base_costs, "signed-column reflection control")
    ones = (1,) * 10
    ones_num, ones_norm = householder_numerator(base, ones)
    ones_costs, _ = support_bill(ones_num, pairs, cache)
    require(ones_norm == 10 and ones_costs == [9] * 10, "known dense-gauge control")
    bad_num, bad_norm = householder_numerator(base, axis, scale=3)
    require(not identity(bad_num, den * bad_norm, roots), "nonorthogonal coefficient control")
    omitted = [row[:9] for row in base]
    require(not identity(omitted, den, roots), "omitted isotropic-pair member control")
    mutated = [list(row) for row in base]
    mutated[0][0] = (mutated[0][0][0] + 1, mutated[0][0][1])
    require(not identity(mutated, den, roots), "mutated witness control")

    profiles = {}
    best_candidates = {}
    rank_cache = cache
    total = active = inactive = 0
    for s in itertools.product((-1, 0, 1), repeat=10):
        if not any(s) or not is_canonical(s):
            continue
        total += 1
        norm, m = orthogonal_numerator(s)
        require(all(sum(m[i][k] * m[j][k] for k in range(10)) ==
                    norm * norm * (i == j) for i in range(10) for j in range(10)),
                "Householder exact orthogonality")
        changed, scale = householder_numerator(base, s)
        require(scale == norm, "Householder common denominator")
        costs, masks = support_bill(changed, pairs, rank_cache)
        if not all(masks):
            inactive += 1
            continue
        active += 1
        hist = tuple(sorted(costs))
        profiles[hist] = profiles.get(hist, 0) + 1
        prior = best_candidates.get(hist)
        if prior is None or tuple(costs) < prior["ordered_costs"]:
            best_candidates[hist] = {"s": list(s), "ordered_costs": tuple(costs)}
    require(total == HOUSEHOLDERS, "Householder search coverage")
    require(active == total and inactive == 0, "all searched decoder terms stay active")
    require(sum(profiles.values()) == active, "rank-profile count coverage")
    require(all(set(hist) <= {8, 9} for hist in profiles), "unexpected support-rank class")
    require(min(map(sum, profiles)) == 82, "minimum support invoice in searched family")

    model = load_ceiling()
    screened = []
    for hist, count in sorted(profiles.items()):
        local = profile_for(hist)
        centre = sum(hist)
        lo, hi = screen_profile(local, centre, model)
        screened.append({
            "rank_histogram": dict(sorted(Counter(hist).items())),
            "candidate_count": count,
            "centre_rank_mass": centre,
            "profile": {str(r): n for r, n in sorted(local.items())},
            "a_cap_interval": [str(lo), str(hi)],
            "passes_five_percent_gate": lo >= TARGET_A,
            "example_normal": best_candidates[hist]["s"],
            "ordered_costs": list(best_candidates[hist]["ordered_costs"]),
        })
    screened.sort(key=lambda x: Q(x["a_cap_interval"][1]), reverse=True)
    require(all(Q(row["a_cap_interval"][1]) < TARGET_A for row in screened),
            "a Householder profile unexpectedly meets the 5% gate")
    best = screened[0]
    best_s = tuple(best["example_normal"])
    best_matrix, best_norm = householder_numerator(base, best_s)
    require(identity(best_matrix, den * best_norm, roots), "best candidate direct P112 identity")

    baseline = screen_profile(BASE_PROFILE, BASE_CENTRE, model)
    result = {
        "status": "PASS_P112_HOUSEHOLDER_GAUGE_SEARCH",
        "seed": "06ace58bfc2b63b47b02129f729e35d4",
        "track": "complex-mechanisms",
        "task_id": "complex-rank-shape-decoder",
        "priority_revision": 3,
        "base_commit": "0b1cccf86e2f5132ed286a26ef0a681a495740ea",
        "selected_record_sha256": SELECTED_SHA256,
        "predecessor": {"pr": 1633, "head": PRED_HEAD,
                        "result_git_blob": PRED_RESULT_BLOB,
                        "result_sha256": PRED_RESULT_SHA256},
        "domain": {"support": "P112", "terms": 10,
                   "householder_normals": "{-1,0,1}^10 minus zero, modulo s~-s",
                   "candidate_count": total,
                   "all_terms_active_candidates": active,
                   "inactive_candidates": inactive,
                   "distinct_rank_histograms": len(profiles)},
        "base": {"costs": base_costs, "centre_rank_mass": BASE_CENTRE,
                 "a_cap_interval": [str(x) for x in baseline]},
        "gate": {"target_a": str(TARGET_A),
                 "best_zero_extra_charge_a_cap_interval": best["a_cap_interval"],
                 "best_candidate_passes": best["passes_five_percent_gate"],
                 "best_rank_histogram": best["rank_histogram"],
                 "best_ordered_costs": best["ordered_costs"],
                 "best_normal": best["example_normal"],
                 "best_profile": best["profile"],
                 "best_centre_rank_mass": best["centre_rank_mass"]},
        "profiles": screened,
        "controls": ["signed-column reflection preserves the base invoice",
                     "all-ones Householder reproduces the 90-copy gauge",
                     "nonorthogonal coefficient fails the exact identity",
                     "omitted residual term fails the exact identity",
                     "mutated witness entry fails the exact identity"],
        "limitations": ["Only one symmetric ten-term witness orbit is searched.",
                        "Rational Householder coefficients have not been priced in a native supplier.",
                        "No physical frame, hosting, precision/tape, restoration or controller invoice is established.",
                        "No selected supplier adoption or new kappa is claimed."],
    }
    return result, roots, best_matrix, den * best_norm


def main():
    write = "--write" in sys.argv[1:]
    result, roots, matrix, den = run()
    if write:
        RESULT_PATH.write_text(json.dumps(result, indent=2) + "\n")
    else:
        expected = json.loads(RESULT_PATH.read_text())
        canonical = json.loads(json.dumps(result))
        require(canonical == expected, "stored bounded-search receipt mismatch")
    gate = result["gate"]
    print("PASS_P112_HOUSEHOLDER_GAUGE_SEARCH "
          f"candidates={result['domain']['candidate_count']} "
          f"active={result['domain']['all_terms_active_candidates']} "
          f"profiles={result['domain']['distinct_rank_histograms']} "
          f"best_costs={gate['best_ordered_costs']} "
          f"best_a_hi={gate['best_zero_extra_charge_a_cap_interval'][1]} "
          f"gate={gate['best_candidate_passes']} controls={len(result['controls'])}")


if __name__ == "__main__":
    main()
