#!/usr/bin/env python3
"""Exact finite screen for a compensated isotropic null-pair shear on PR717 P104."""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TASK_SEED = "318bd5e5f93c401334e29c6764720302"
BASE = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
SELECTED = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
INPUT = ROOT / "research/complex-frame-pair-decoders/inputs/pr717/P104_HIT_flip_3a.txt"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def e8_roots():
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (1, -1):
            for sj in (1, -1):
                v = [0] * 8
                v[i], v[j] = 2 * si, 2 * sj
                roots.append(tuple(v))
    for s in itertools.product((1, -1), repeat=8):
        if s.count(-1) % 2 == 0:
            roots.append(tuple(s))
    return roots


def ip(x, y):
    d = sum(a * b for a, b in zip(x, y))
    require(d % 4 == 0, "nonintegral E8 inner product")
    return d // 4


def rank_q(rows):
    rows = [[Q(x) for x in row] for row in rows]
    rank = 0
    for col in range(len(rows[0]) if rows else 0):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        p = rows[rank][col]
        rows[rank] = [x / p for x in rows[rank]]
        for i in range(len(rows)):
            if i != rank and rows[i][col]:
                q = rows[i][col]
                rows[i] = [x - q * z for x, z in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def solve_square(a, y):
    n = len(a)
    m = [[Q(x) for x in row] + [Q(v)] for row, v in zip(a, y)]
    for col in range(n):
        pivot = next(i for i in range(col, n) if m[i][col])
        m[col], m[pivot] = m[pivot], m[col]
        q = m[col][col]
        m[col] = [x / q for x in m[col]]
        for i in range(n):
            if i != col and m[i][col]:
                q = m[i][col]
                m[i] = [x - q * z for x, z in zip(m[i], m[col])]
    return tuple(m[i][-1] for i in range(n))


def load_hit(path):
    d, t = [], []
    for line in path.read_text().splitlines():
        s = line.strip()
        if s.startswith("d:"):
            d.append([int(x) for x in s[2:].split()])
        elif s.startswith("t:"):
            t.append([int(x) for x in s[2:].split()])
    return [list(x) for x in zip(*d)], [list(x) for x in zip(*t)]


def gauss_add(x, y):
    return tuple((a[0] + b[0], a[1] + b[1]) for a, b in zip(x, y))


def gauss_sub(x, y):
    return tuple((a[0] - b[0], a[1] - b[1]) for a, b in zip(x, y))


def gauss_i(x):
    return tuple((-a[1], a[0]) for a in x)


def gauss_dot(root, x):
    re = sum(Q(a, 4) * v[0] for a, v in zip(root, x))
    im = sum(Q(a, 4) * v[1] for a, v in zip(root, x))
    return re, im


def recover(live, col, line_table):
    selected = []
    for idx in range(len(live)):
        cand = selected + [idx]
        if rank_q([line_table[live[j]] for j in cand]) == len(cand):
            selected.append(idx)
        if len(selected) == 8:
            break
    require(len(selected) == 8, "P104 live labels do not span the 8-space")
    mat = [[Q(x, 4) for x in line_table[live[j]]] for j in selected]
    v = solve_square(mat, [col[j] for j in selected])
    require(all(sum(Q(x, 4) * y for x, y in zip(line_table[idx], v)) == col[p]
                for p, idx in enumerate(live)), "decoder column is not a linear form on E8")
    return tuple((x, Q(0)) for x in v)


def e8_data():
    line_table, seen = [], set()
    for r in e8_roots():
        neg = tuple(-x for x in r)
        key = r if r > neg else neg
        if key not in seen:
            seen.add(key)
            line_table.append(r)
    index = {v: i for i, v in enumerate(line_table)}
    f0 = []
    for a in range(4):
        for s in (1, -1):
            v = [0] * 8
            v[2 * a], v[2 * a + 1] = 2, 2 * s
            f0.append(index[tuple(v)])
    p112 = [i for i in range(120) if i not in f0]
    puncture = [p112[q] for q in (9, 15, 24, 46, 52, 66, 94, 104)]
    live = [i for i in range(120) if i not in f0 and i not in puncture]
    require(len(line_table) == 120 and len(live) == 104, "E8 / P104 census")
    iptab = [[ip(line_table[i], line_table[j]) for j in range(120)] for i in range(120)]
    nrow = [sum(((iptab[i][j] + 1) & 1) << j for j in range(120)) for i in range(120)]
    return line_table, f0, puncture, live, iptab, nrow


def candidates():
    units = ((1, 0), (-1, 0), (0, 1), (0, -1))
    zero = (0, 0)
    out = set()
    for k in (1, 2):
        for pos in itertools.combinations(range(8), k):
            for coeff in itertools.product(units, repeat=k):
                v = [zero] * 8
                for j, c in zip(pos, coeff):
                    v[j] = c
                out.add(tuple((Q(a), Q(b)) for a, b in v))
    return tuple(sorted(out))


def matrix_errors(terms, live, line_table, iptab):
    errors = 0
    for i in live:
        for j in live:
            re, im = Q(0), Q(0)
            for x, y in terms:
                gx, gy = gauss_dot(line_table[i], x), gauss_dot(line_table[j], y)
                re += gx[0] * gy[0] - gx[1] * gy[1]
                im += gx[0] * gy[1] + gx[1] * gy[0]
            errors += (re, im) != (2 * iptab[i][j], 0)
    return errors


def run():
    selected_path = ROOT / "certificates/selected-result.json"
    selected = json.loads(selected_path.read_text())
    require(sha(selected_path) == SELECTED, "selected record pin changed")
    sources = json.loads((HERE / "SOURCES.json").read_text())
    e8_model = sources["e8_model"]
    pins = {
        "P104 decoder": (INPUT, "8e0178db02c14e1b29058cdbdbd50aac22f2b55a1ba21dc82f417610c9932526"),
        "ceiling engine": (ROOT / "research/complex-local-word-ceiling/ceiling.py",
                           "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc"),
        "ceiling result": (ROOT / "research/complex-local-word-ceiling/RESULT.json",
                           "d91d6c46509875abf1f61de67c2609656d3dc685451299f83caa6f922493692d"),
        # Pairwise-era bytes live in the production package baseline after
        # research/frame-pair-enumeration-production/; live verify.py ships the
        # eight-bit neighborhood enumerator and no longer matches this digest.
        "frame-pair predecessor": (ROOT / e8_model["path"], e8_model["sha256"]),
    }
    for name, (path, expected) in pins.items():
        require(sha(path) == expected, f"{name} SHA-256 changed: {sha(path)}")

    line_table, _, _, live, iptab, nrow = e8_data()
    dcols, tcols = load_hit(INPUT)
    require(len(dcols) == len(tcols) == 104 and len(dcols[0]) == 8, "P104 decoder dimensions")
    old_errors = 0
    for i in range(104):
        for j in range(104):
            old_errors += sum(dcols[i][k] * tcols[j][k] for k in range(8)) != 2 * iptab[live[i]][live[j]]
    require(old_errors == 0, "PR717 source decoder does not satisfy the P104 identity")
    old_terms = []
    for k in range(8):
        a = recover(live, [dcols[p][k] for p in range(104)], line_table)
        b = recover(live, [tcols[p][k] for p in range(104)], line_table)
        old_terms.append((a, b))

    @lru_cache(None)
    def support(v):
        mask = 0
        for idx in live:
            if gauss_dot(line_table[idx], v) != (0, 0):
                mask |= 1 << idx
        return mask

    def rank_rows(rows):
        basis, rank = {}, 0
        for v in rows:
            while v:
                bit = v.bit_length() - 1
                if bit in basis:
                    v ^= basis[bit]
                else:
                    basis[bit] = v
                    rank += 1
                    break
        return rank

    @lru_cache(None)
    def pair_rank(rowmask, colmask):
        rows = [idx for idx in live if (rowmask >> idx) & 1]
        return rank_rows([nrow[idx] & colmask for idx in rows])

    old_costs = [pair_rank(support(a), support(b)) for a, b in old_terms]
    require(old_costs == [7] * 8, f"PR717 P104 floor input changed: {old_costs}")

    # Exact P104 optimistic profile: eight port cuts and eight rank-8 to rank-7 units.
    local = {1: 2356, 2: 418, 3: 432, 4: 134, 5: 74, 7: 8}
    sys.path.insert(0, str(ROOT / "research/complex-local-word-ceiling"))
    import ceiling  # pylint: disable=import-outside-toplevel
    # Reuse the exact transcendental enclosures for repeated candidate histograms.
    original_child_cost = ceiling.child_cost
    child_cost_cache = {}
    def cached_child_cost(r, m, a):
        key = (r, m, a)
        if key not in child_cost_cache:
            child_cost_cache[key] = original_child_cost(r, m, a)
        return child_cost_cache[key]
    ceiling.child_cost = cached_child_cost
    result = json.loads((ROOT / "research/complex-local-word-ceiling/RESULT.json").read_text())
    target = Q(result["ceiling"]["a_ceiling"]) * Q(105, 100)
    p104_lo, p104_hi = ceiling.ceiling(local, 73, 832, 9, 56)
    require(p104_lo == Q(1781965480167, 10**15) and p104_hi == Q(222745685021, 125000000000000),
            "P104 baseline ceiling does not match the pinned exact model")
    require(p104_hi > target, "the existing P104 eight-term profile fails the 5% planning gate")

    @lru_cache(None)
    def screen(triple):
        hist = local.copy()
        hist[7] -= 1
        for r in triple:
            if r:
                hist[r] = hist.get(r, 0) + 1
        hist[1] += 6  # prepare z,w; form the shear; clear z,w
        lo, hi = ceiling.relax(hist, 73, 832, 9, 56, target)
        return str(lo), str(hi), hi < 1

    family = candidates()
    require(len(family) == 480, "two-coordinate Gaussian-unit alphabet size")
    domain = len(family) * (len(family) - 1) * 8
    triple_hist, pass_hist, block_hist = Counter(), Counter(), Counter()
    min_block, min_examples, qualifying = 999, [], []
    for pivot, (a, b) in enumerate(old_terms):
        sb = support(b)
        for z in family:
            sz = support(z)
            c1 = pair_rank(support(gauss_add(a, z)), sb)
            for w in family:
                if z == w:
                    continue
                c2 = pair_rank(sz, support(gauss_sub(w, b)))
                c3 = pair_rank(sz, support(w))
                triple = tuple(sorted((c1, c2, c3)))
                triple_hist[triple] += 1
                passed = screen(triple)[2]
                if passed:
                    pass_hist[triple] += 1
                block = c1 + c2 + c3
                block_hist[block] += 1
                record = (pivot, z, w, (c1, c2, c3))
                if block < min_block:
                    min_block, min_examples = block, [record]
                elif block == min_block and len(min_examples) < 16:
                    min_examples.append(record)
                if block < 7 and passed and len(qualifying) < 16:
                    qualifying.append(record)

    require(sum(triple_hist.values()) == domain, "search domain count")
    chosen = qualifying[0] if qualifying else min_examples[0]
    pivot, z, w, chosen_ranks = chosen
    a, b = old_terms[pivot]
    terms = list(old_terms)
    terms.pop(pivot)
    terms.extend(((gauss_add(a, z), b), (z, gauss_sub(w, b)), (gauss_i(z), gauss_i(w))))
    errors = matrix_errors(terms, live, line_table, iptab)
    require(errors == 0, "compensated 10-term decoder failed the 104x104 identity")

    # Negative control: use the wrong sign in the inverse target shear.
    unit_vectors = [v for v in family if sum(x != (0, 0) for x in v) == 1]
    zc, wc = unit_vectors[0], unit_vectors[-1]
    ac, bc = old_terms[0]
    bad = list(old_terms)
    bad.pop(0)
    bad.extend(((gauss_add(ac, zc), bc), (zc, gauss_add(wc, bc)), (gauss_i(zc), gauss_i(wc))))
    bad_errors = matrix_errors(bad, live, line_table, iptab)
    require(bad_errors > 0, "wrong-sign control unexpectedly exact")

    # Centre +1 control with the best possible replacement ranks (1,1,1).
    hist57 = local.copy()
    hist57[7] -= 1
    hist57[1] += 9  # three rank-one children plus six setup children
    _, hi57 = ceiling.relax(hist57, 73, 832, 9, 57, target)
    require(hi57 > 1, "centre+1 negative control unexpectedly clears the target")

    block_best_pass = any(sum(t) < 7 and screen(t)[2] for t in triple_hist)
    out = {
        "status": "completed_scoped_construction" if qualifying else "completed_scoped_negative",
        "seed": TASK_SEED,
        "track": "complex-mechanisms",
        "task_id": "complex-new-helper-inventory",
        "base_commit": BASE,
        "selected_record_sha256": SELECTED,
        "source_sha256": {name: expected for name, (_, expected) in pins.items()},
        "mechanism": "append one exact complex null pair (z,w),(iz,iw) and apply a compensated one-pivot 3-column shear",
        "domain": {
            "live_lines": 104,
            "pivots": 8,
            "coordinate_axes": 8,
            "nonzero_coefficients": ["1", "-1", "i", "-i"],
            "support_per_vector_at_most": 2,
            "distinct_ordered_z_w": len(family) * (len(family) - 1),
            "total_pivot_pairs": domain,
            "stopping_rule": "exhaust the stated Gaussian-unit two-coordinate family over all eight pivot terms",
        },
        "algebra": {
            "identity": "(a+z)b^T + z(w-b)^T + (iz)(iw)^T = ab^T",
            "input_decoder_entries_checked": 104 * 104,
            "input_identity_errors": old_errors,
            "transformed_identity_entries_checked": 104 * 104,
            "transformed_identity_errors": errors,
            "wrong_sign_control_errors": bad_errors,
        },
        "cost": {
            "baseline_term_ranks": old_costs,
            "baseline_copied_rank": sum(old_costs),
            "p104_base_ceiling_bracket": [str(p104_lo), str(p104_hi)],
            "five_percent_target_a": str(target),
            "minimum_replacement_block_rank": min_block,
            "minimum_total_copied_rank": 49 + min_block,
            "block_rank_histogram": {str(k): v for k, v in sorted(block_hist.items())},
            "profile_classes": len(triple_hist),
            "profiles_clearing_5_percent_screen": sum(pass_hist.values()),
            "profiles_with_strict_copy_saving_that_clear_screen": block_best_pass,
            "qualifying_candidate_count_capped_at_16": len(qualifying),
            "minimum_block_examples": [{"pivot": k, "z": [[str(a), str(b)] for a, b in zz],
                                        "w": [[str(a), str(b)] for a, b in ww], "term_ranks": list(rs)}
                                       for k, zz, ww, rs in min_examples],
            "profile_model": "P104 ports=8, centre=56; replace one rank-7 child by the three exact pairing ranks; add six rank-one preparation/use/cleanup charges",
            "five_percent_target_a": str(target),
            "best_case_centre_plus_one_moment_upper": str(hi57),
            "unpriced_physical_obligations": ["phase-frame legality", "whole-call hosting", "precision", "native dirty-state boundary"],
        },
        "notes": [
            "Every changed term's copied-information charge is its exact F2 rank of the live-line label-pairing matrix.",
            "The six rank-one charges cover two sparse-vector preparations, two shear forms, and clearing both scratch vectors.",
            "The P104 screen retains the existing eight ports and centre=56; any extra centre unit fails the target control.",
            "No selected supplier, kappa, or frontier change is claimed.",
        ],
    }
    return out


def main():
    out = run()
    cert = HERE / "CERTIFICATE.json"
    if "--write" in sys.argv:
        cert.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    else:
        require(cert.exists(), "missing CERTIFICATE.json; run verify.py --write")
        require(json.loads(cert.read_text()) == out, "CERTIFICATE.json is stale")
    print("PASS_P104_NULLPAIR_COMPENSATED_SHEAR",
          "domain=" + str(out["domain"]["total_pivot_pairs"]),
          "min_block_rank=" + str(out["cost"]["minimum_replacement_block_rank"]),
          "saving_pass=" + str(out["cost"]["profiles_with_strict_copy_saving_that_clear_screen"]),
          "identity_errors=" + str(out["algebra"]["transformed_identity_errors"]),
          "no_new_kappa")


if __name__ == "__main__":
    main()
