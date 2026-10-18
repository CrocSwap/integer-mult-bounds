#!/usr/bin/env python3
"""Independent exterior certificates for the pinned R420 frame geometry.

Standard library only. No producer, elimination, determinant or prime-witness
code is imported. See README.md for the specialization argument and scope.
Prepared for Ishan (@ishan-1729) with substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0
"""

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from functools import reduce
import gzip
import hashlib
import json
from math import gcd
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 78
H = 8


class Reject(ValueError):
    """A failed mathematical obligation or source/receipt binding."""


def need(condition, message):
    # Deliberately not an assert: the checker also runs under python -O.
    if not condition:
        raise Reject(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def counts(counter):
    return {str(k): v for k, v in sorted(counter.items())}


def power_of_two(n):
    return type(n) is int and n > 0 and n & (n - 1) == 0


def wedge(blade, vector):
    """Append a vector; bit masks encode increasing exterior basis indices."""
    result = defaultdict(int)
    for mask, coefficient in blade.items():
        for i, value in enumerate(vector):
            if value and not (mask >> i) & 1:
                sign = -1 if (mask >> (i + 1)).bit_count() % 2 else 1
                result[mask | (1 << i)] += sign * coefficient * value
    return {mask: x for mask, x in result.items() if x}


def spanning_blade(lines, ids, seed=SEED):
    """Greedy independent roots, with primitive integer normalization."""
    blade, selected, contents = {0: 1}, [], []
    for root in sorted(ids, key=lambda i: (i - seed) % len(lines)):
        extended = wedge(blade, lines[root])
        if extended:
            content = reduce(gcd, extended.values(), 0)
            sign = 1 if extended[min(extended)] > 0 else -1
            blade = {mask: sign * x // content for mask, x in extended.items()}
            selected.append(root)
            contents.append(content)
    return blade, selected, contents


def projection_numerator(blade, h=H):
    """N_ij = <contraction(e_i, B), contraction(e_j, B)>; P=N/||B||^2."""
    contractions = []
    for i in range(h):
        contractions.append({
            mask ^ (1 << i): x * (-1 if (mask & ((1 << i) - 1)).bit_count() % 2 else 1)
            for mask, x in blade.items() if (mask >> i) & 1
        })
    return [[sum(x * contractions[j].get(mask, 0)
                 for mask, x in contractions[i].items())
             for j in range(h)] for i in range(h)]


def check_projector(matrix, norm, dimension):
    h = len(matrix)
    need(type(norm) is int and norm > 0, "nonpositive blade norm")
    need(all(len(row) == h and all(type(x) is int for x in row) for row in matrix),
         "projector shape or entry type")
    need(all(matrix[i][j] == matrix[j][i] for i in range(h) for j in range(h)),
         "projector symmetry")
    need(sum(matrix[i][i] for i in range(h)) == dimension * norm, "projector trace")
    need(all(sum(matrix[i][k] * matrix[k][j] for k in range(h)) == norm * matrix[i][j]
             for i in range(h) for j in range(h)), "projector idempotence")


def frame_certificate(lines, ids, seed=SEED):
    """Rational frame obligations, before imposing any prime restrictions."""
    h = len(lines[0])
    need(all(type(i) is int and 0 <= i < len(lines) for i in ids), "root index")
    need(len(ids) == len(set(ids)), "duplicate root in frame")
    blade, selected, contents = spanning_blade(lines, ids, seed)
    dimension = len(selected)
    need(all(mask.bit_count() == dimension for mask in blade), "blade degree")
    norm = sum(x * x for x in blade.values())
    matrix = projection_numerator(blade, h)
    check_projector(matrix, norm, dimension)
    outside = Counter()
    members = set(ids)
    for k, vector in enumerate(lines):
        residual = [sum(matrix[i][j] * vector[j] for j in range(h)) - norm * vector[i]
                    for i in range(h)]
        divisor = reduce(gcd, residual)
        # Wedge membership and contraction membership are independently evaluated.
        need((divisor == 0) == (not wedge(blade, vector)), "wedge/projector membership")
        need((divisor == 0) == (k in members), "root closure")
        if divisor:
            outside[divisor] += 1
    denominator = norm // reduce(gcd, (x for row in matrix for x in row), norm)
    record = {
        "dimension": dimension,
        "basis_root_ids": selected,
        "normalization_contents": contents,
        "blade": [[mask, x] for mask, x in sorted(blade.items())],
        "norm_squared": norm,
        "projector_denominator": denominator,
        "root_members": len(ids),
        "outside_residual_gcds": counts(outside),
    }
    return record, matrix


def check_dyadic(record):
    need(power_of_two(record["norm_squared"]), "blade norm has an odd prime factor")
    need(all(power_of_two(n) for n in record["normalization_contents"]),
         "basis normalization has an odd prime factor")
    need(all(power_of_two(int(n)) for n in record["outside_residual_gcds"]),
         "outside residual has an odd prime factor")


def validate_labels(word):
    need((word["h"], word["v"], word["R"], word["form"]) == (8, 120, 420, "<x,y>/2"),
         "R420 header")
    lines = word["lines"]
    need(len(lines) == 120, "root count")
    need(all(len(v) == H and all(type(x) is int for x in v) for v in lines), "root shape")
    need(all(sum(x * x for x in v) == 4 for v in lines), "root norm")
    need(all(abs(sum(x * y for x, y in zip(a, b))) <= 2
             for i, a in enumerate(lines) for b in lines[i + 1:]), "distinct root lines")
    need(all(sum(x * y for x, y in zip(a, b)) % 2 == 0 for a in lines for b in lines),
         "integral E8 form")
    need(len(word["frames"]) == 672, "frame count")
    need(len({tuple(sorted(ids)) for ids in word["frames"]}) == 672, "duplicate frames")


def geometry(word):
    validate_labels(word)
    lines, frames = word["lines"], word["frames"]
    records, matrices = [], []
    for frame_id, ids in enumerate(frames):
        record, matrix = frame_certificate(lines, ids)
        check_dyadic(record)
        record["frame_id"] = frame_id
        records.append(record)
        matrices.append(matrix)

    lookup = {tuple(sorted(ids)): i for i, ids in enumerate(frames)}
    for frame_id, ids in enumerate(frames):
        perpendicular = tuple(i for i, v in enumerate(lines)
                              if all(sum(x * y for x, y in zip(v, lines[j])) == 0 for j in ids))
        need(perpendicular in lookup, "perpendicular frame absent")
        other = lookup[perpendicular]
        a, b = records[frame_id], records[other]
        need(a["dimension"] + b["dimension"] == H, "complement dimension")
        s, t = a["norm_squared"], b["norm_squared"]
        need(all(t * matrices[frame_id][i][j] + s * matrices[other][i][j] == s * t * (i == j)
                 for i in range(H) for j in range(H)), "complement projectors")
        a["perpendicular_frame"] = other

    sets = [set(ids) for ids in frames]
    inclusions = 0
    for i, a in enumerate(sets):
        for j, b in enumerate(sets):
            if a <= b:
                need(i == j or records[i]["dimension"] < records[j]["dimension"],
                     "proper inclusion dimension")
                inclusions += 1
    summary = {
        "frames": len(records),
        "root_membership_obligations": len(records) * len(lines),
        "inside_memberships": sum(len(ids) for ids in frames),
        "outside_memberships": sum(len(lines) - len(ids) for ids in frames),
        "ordered_inclusions_including_equalities": inclusions,
        "ordered_noninclusions": len(frames) ** 2 - inclusions,
        "perpendicular_pairs": len(records) // 2,
        "projector_entry_identities": len(records) * H * H,
        "complement_entry_identities": len(records) * H * H,
        "dimensions": counts(Counter(r["dimension"] for r in records)),
        "primitive_blade_norms": counts(Counter(r["norm_squared"] for r in records)),
        "projector_denominators": counts(Counter(r["projector_denominator"] for r in records)),
        "normalization_contents": counts(Counter(n for r in records for n in r["normalization_contents"])),
        "outside_residual_gcds": counts(sum((Counter({int(k): v for k, v in r["outside_residual_gcds"].items()})
                                             for r in records), Counter())),
    }
    return records, matrices, summary


def negative_controls(word, records, matrices):
    """Exercise mathematical predicates directly, bypassing all input hashes."""
    lines = word["lines"]
    rejected = []

    def reject(name, expected_reason, action):
        try:
            action()
        except Reject as error:
            need(str(error) == expected_reason, name + ": unexpected rejection: " + str(error))
            rejected.append({"name": name, "reason": str(error)})
        else:
            raise Reject("negative control accepted: " + name)

    # The remaining 119 lines still span all eight dimensions.
    reject("missing_redundant_root", "root closure",
           lambda: frame_certificate(lines, [i for i in range(120) if i != SEED]))
    selected_frame = next(i for i, ids in enumerate(word["frames"]) if ids == [SEED])
    record, matrix = records[selected_frame], matrices[selected_frame]
    norm = record["norm_squared"]
    broken = deepcopy(matrix)
    broken[0][0] += norm
    reject("projector_diagonal_changed", "projector trace",
           lambda: check_projector(broken, norm, 1))
    reject("projector_denominator_doubled", "projector trace",
           lambda: check_projector(matrix, 2 * norm, 1))
    reject("dimension_changed", "projector trace",
           lambda: check_projector(matrix, norm, 2))
    # A trace-preserving symmetric perturbation must reach the idempotence guard.
    broken2 = deepcopy(matrix)
    broken2[0][0] += norm
    broken2[1][1] -= norm
    reject("trace_preserving_projector_corruption", "projector idempotence",
           lambda: check_projector(broken2, norm, 1))

    # An actual rational E8 A2 plane: legal over Q, degenerate at p=3.
    u = SEED
    v = next(i for i in range(120) if abs(sum(x * y for x, y in zip(lines[u], lines[i]))) == 2)
    blade = wedge(wedge({0: 1}, lines[u]), lines[v])
    a2_ids = [i for i, root in enumerate(lines) if not wedge(blade, root)]
    a2, _ = frame_certificate(lines, a2_ids)
    reject("A2_plane_at_prime_3", "blade norm has an odd prime factor", lambda: check_dyadic(a2))
    sign = sum(x * y for x, y in zip(lines[u], lines[v])) // 2
    radical = [(x + sign * y) % 3 for x, y in zip(lines[u], lines[v])]
    need(any(radical) and all(sum(x * y for x, y in zip(radical, lines[i])) % 3 == 0 for i in a2_ids),
         "A2 radical witness")

    # Rational projectors alone do not detect nonunit changes of integral generators.
    scaled = deepcopy(lines)
    scaled[u] = [3 * x for x in scaled[u]]
    scaled_frame, scaled_matrix = frame_certificate(scaled, [u])
    need(scaled_matrix == matrix and scaled_frame["norm_squared"] == norm,
         "scaled-basis positive rational control")
    reject("basis_scaled_by_3", "basis normalization has an odd prime factor",
           lambda: check_dyadic(scaled_frame))
    scaled = deepcopy(lines)
    scaled[v] = [3 * x for x in scaled[v]]
    outside_frame, _ = frame_certificate(scaled, [u])
    reject("outside_root_scaled_by_3", "outside residual has an odd prime factor",
           lambda: check_dyadic(outside_frame))

    # A second traversal order must recover the same primitive oriented blade.
    alternate, alternate_matrix = frame_certificate(lines, a2_ids, seed=(SEED + 1) % 120)
    need(alternate["blade"] == a2["blade"], "basis-order invariance")
    return {
        "rejected": rejected,
        "A2_control": {"root_ids": a2_ids, "chosen_pair": [u, v], "norm_squared": a2["norm_squared"],
                       "radical_mod_3": radical, "basis_coefficients_mod_3": [1, sign % 3],
                       "rational_dimension": 2, "rational_closure_passes": True},
        "positive_controls": ["scaled basis has identical rational projector", "basis-order invariance"],
    }


def load_word(path, source):
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        word = json.load(handle)
    need(digest(word) == source["word"]["semantic_sha256"], "word semantic SHA-256 mismatch")
    return word


def build_receipt(word, source):
    records, matrices, summary = geometry(word)
    controls = negative_controls(word, records, matrices)
    return {
        "status": "PASS_R420_EXTERIOR_FRAMES",
        "schema": "r420-exterior-frames/1",
        "assignment_seed": SEED,
        "base_commit": source["base_commit"],
        "supplier_commit": source["supplier_commit"],
        "word_semantic_sha256": digest(word),
        "geometry_sha256": digest({k: word[k] for k in ("lines", "frames")}),
        "summary": summary,
        "controls": controls,
        "frames": records,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", type=Path, help="Alternate gzip container for the same pinned word")
    parser.add_argument("--check", type=Path, default=HERE / "CERTIFICATE.json")
    parser.add_argument("--output", type=Path, help="Write computed certificate to a NEW file after checking")
    args = parser.parse_args(argv)
    if args.output:
        need(not args.output.exists(), "output already exists")
    source = json.loads((HERE / "SOURCE.json").read_text(encoding="utf-8"))
    word = load_word(args.word or ROOT / source["word"]["path"], source)
    receipt = build_receipt(word, source)
    expected = json.loads(args.check.read_text(encoding="utf-8"))
    need(receipt == expected, "certificate mismatch")
    if args.output:
        with args.output.open("x", encoding="utf-8") as handle:
            json.dump(receipt, handle, sort_keys=True, indent=2)
            handle.write("\n")
    s = receipt["summary"]
    print(f"PASS_R420_EXTERIOR_FRAMES: {s['frames']} frames; "
          f"{s['root_membership_obligations']} memberships; "
          f"{s['ordered_inclusions_including_equalities']} inclusions; "
          f"{len(receipt['controls']['rejected'])} rejected controls; every odd prime")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (Reject, OSError, ValueError, KeyError, TypeError) as error:
        print("REJECT:", error, file=sys.stderr)
        sys.exit(1)
