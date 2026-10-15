#!/usr/bin/env python3
"""Exhaust the signed Walsh-character two-total shear family on exact P112."""
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction as Q
from itertools import permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research/p112-single-lift"))
sys.path.insert(0, str(ROOT / "research/complex-local-word-ceiling"))
import geometry  # noqa: E402
import ceiling as C  # noqa: E402

M, FAMILIES, STAGES = 73, 896, 9
BASE_PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82}
OUT = HERE / "RESULT.json"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def parity(x):
    return x.bit_count() & 1


def rank2(rows):
    """Binary row rank; a separate implementation for cross-checking geometry.term_cost."""
    pivots = {}
    for row in rows:
        x = row
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                break
    return len(pivots)


def beta(left, right, data):
    """Literal restricted pairing rank for one ordered factor pair."""
    reader_basis = geometry.binary_basis(
        q for value, q in zip(left, data["duals"]) if value
    )
    rows = []
    for value, label in zip(right, data["labels"]):
        if value:
            rows.append(sum(parity(q & label) << j
                            for j, q in enumerate(reader_basis)))
    return rank2(rows)


def mat_vec(matrix, vector):
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def column(matrix, j):
    return [row[j] for row in matrix]


def characters():
    # Characters of F_2^3, with coordinate b=0,...,7 and character a=0,...,7.
    return [[-1 if parity(a & b) else 1 for b in range(8)] for a in range(8)]


def coefficient_identity_cols(u, v, wrong_sign=False, omit_last=False):
    """Check A B^T exactly in the eight-dimensional coefficient space."""
    result = [[0] * 8 for _ in range(8)]
    for j in range(8):
        t = [int(k == j) - v[0][k] * u[0][j] - v[1][k] * u[1][j]
             for k in range(8)]
        for k in range(8):
            result[j][k] += t[k]
    result_u = [0] if omit_last else list(range(2))
    for l in result_u:
        sign = -1 if wrong_sign else 1
        for i in range(8):
            for j in range(8):
                result[i][j] += sign * u[l][i] * v[l][j]
    return result


def decoder_columns(x, u, v):
    xcols = [column(x, j) for j in range(8)]
    ulifts = [mat_vec(x, vector) for vector in u]
    vlifts = [mat_vec(x, vector) for vector in v]
    dcols = xcols + ulifts
    tcols = []
    for j in range(8):
        tcols.append([
            xcols[j][i]
            - u[0][j] * vlifts[0][i]
            - u[1][j] * vlifts[1][i]
            for i in range(len(x))
        ])
    tcols.extend(vlifts)
    return dcols, tcols


def direct_identity(data, dcols, tcols):
    roots = data["roots"]
    x = data["X"]
    require(len(dcols) == len(tcols) == 10, "ten factors")
    for i in range(112):
        for j in range(112):
            lhs = sum(d[i] * t[j] for d, t in zip(dcols, tcols))
            gram = sum(a * b for a, b in zip(roots[i], roots[j])) // 4
            require(lhs == 2 * gram, "direct P112 identity failed")
            require(sum(a * b for a, b in zip(x[i], x[j])) == 2 * gram,
                    "pinned XX^T identity failed")


def candidate_rows(data):
    chars = characters()
    options = list(permutations(range(8), 2))
    require(len(options) == 56, "ordered distinct Walsh-pair count")
    basis_changes = [
        ("identity", ((1, 0), (0, 1)), ((1, 0), (0, 1))),
        ("upper_plus", ((1, 1), (0, 1)), ((1, 0), (-1, 1))),
        ("upper_minus", ((1, -1), (0, 1)), ((1, 0), (1, 1))),
        ("lower_plus", ((1, 0), (1, 1)), ((1, -1), (0, 1))),
        ("lower_minus", ((1, 0), (-1, 1)), ((1, 1), (0, 1))),
    ]
    rows = []
    profile_counts = Counter()
    by_basis = {name: Counter() for name, _, _ in basis_changes}
    for u_pair in options:
        for v_pair in options:
            base_u = [chars[u_pair[0]], chars[u_pair[1]]]
            base_v = [chars[v_pair[0]], chars[v_pair[1]]]
            for name, matrix, inverse_transpose in basis_changes:
                u = [[sum(base_u[a][i] * matrix[a][j] for a in range(2))
                      for i in range(8)] for j in range(2)]
                v = [[sum(base_v[a][i] * inverse_transpose[a][j] for a in range(2))
                      for i in range(8)] for j in range(2)]
                require(coefficient_identity_cols(u, v) ==
                        [[int(i == j) for j in range(8)] for i in range(8)],
                        "symbolic factor identity failed")
                # Check the claimed non-free basis change preserves the rank-two correction.
                for i in range(8):
                    for j in range(8):
                        before = sum(base_u[a][i] * base_v[a][j] for a in range(2))
                        after = sum(u[a][i] * v[a][j] for a in range(2))
                        require(before == after, "basis change altered UV^T")
                dcols, tcols = decoder_columns(data["X"], u, v)
                ranks = []
                for d, t in zip(dcols, tcols):
                    r = beta(d, t, data)
                    require(1 <= r <= 9, "every Walsh term must be nonzero with rank 1..9")
                    require(r == geometry.term_cost(d, t, data),
                            "independent binary-rank implementations disagree")
                    ranks.append(r)
                profile = tuple(sorted(Counter(ranks).items()))
                profile_counts[profile] += 1
                by_basis[name][profile] += 1
                rows.append({"U": list(u_pair), "V": list(v_pair),
                             "basis": name, "ranks": ranks})
    require(len(rows) == 15680, "complete five-basis ordered Walsh-pair product")
    require(sum(profile_counts.values()) == 15680, "profile census coverage")
    return rows, profile_counts, by_basis, chars


def controls(data, chars):
    u_pair, v_pair = (0, 1), (2, 3)
    identity = [[int(i == j) for j in range(8)] for i in range(8)]
    u = [chars[a] for a in u_pair]
    v = [chars[a] for a in v_pair]
    require(coefficient_identity_cols(u, v) == identity,
            "positive symbolic control")
    require(coefficient_identity_cols(u, v, wrong_sign=True) != identity,
            "wrong-sign control was not rejected")
    require(coefficient_identity_cols(u, v, omit_last=True) != identity,
            "omitted-total control was not rejected")
    options = list(permutations(range(8), 2))
    require((0, 0) not in options and len(options) == 56,
            "duplicate Walsh character pair control")

    dcols, tcols = decoder_columns(data["X"], u, v)
    direct_identity(data, dcols, tcols)
    # A direct matrix mutation checks that dropping the second added product is detected.
    bad_tcols = tcols[:8] + [tcols[8], [0] * 112]
    failed = False
    try:
        direct_identity(data, dcols, bad_tcols)
    except ValueError as error:
        failed = "direct P112 identity failed" in str(error)
    require(failed, "direct dropped-term control did not fail")
    return {
        "positive_symbolic_identity": True,
        "positive_direct_112x112_identity": True,
        "wrong_sign_rejected": True,
        "omitted_symbolic_term_rejected": True,
        "omitted_direct_term_rejected": True,
        "duplicate_character_pair_excluded": True,
        "all_term_ranks_cross_checked": True,
    }


def serialize_profile(profile):
    return {str(r): n for r, n in profile}


def compute():
    data = geometry.build()
    geometry.check_geometry(data)
    rows, profile_counts, by_basis, chars = candidate_rows(data)
    ctrl = controls(data, chars)
    selected_sha = hashlib.sha256(
        (ROOT / "certificates/selected-result.json").read_bytes()
    ).hexdigest()
    require(selected_sha ==
            "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
            "selected record differs from the accepted seed's exact input")
    pinned_ceiling = json.loads((ROOT / "research/complex-local-word-ceiling/RESULT.json").read_text())
    selected_profile = {int(r): n for r, n in pinned_ceiling["selected"]["local_profile_per_call"].items()}
    selected_center = pinned_ceiling["model"]["centre_per_call"]
    _, baseline = C.ceiling(selected_profile, M, FAMILIES, STAGES, selected_center)
    require(str(baseline) == pinned_ceiling["ceiling"]["a_ceiling"],
            "pinned incumbent ceiling changed")
    target = baseline * Q(105, 100)

    profile_results = []
    best = None
    for profile, count in sorted(profile_counts.items()):
        local = {r: n for r, n in selected_profile.items() if r != 8}
        require(local == BASE_PROFILE, "expected selected profile minus eight rank-8 center terms")
        center = sum(r * n for r, n in profile)
        for r, n in profile:
            local[r] = local.get(r, 0) + n
        low, high = C.ceiling(local, M, FAMILIES, STAGES, center)
        candidate = {
            "profile": serialize_profile(profile),
            "candidates": count,
            "center_charge": center,
            "local_profile": {str(r): local[r] for r in sorted(local)},
            "a_lo": str(low),
            "a_hi": str(high),
            "meets_5_percent_gate": low >= target,
        }
        profile_results.append(candidate)
        key = high
        if best is None or key > best[0]:
            best = (key, candidate)

    best_examples = {}
    for row in rows:
        if (serialize_profile(tuple(sorted(Counter(row["ranks"]).items()))) ==
                best[1]["profile"] and row["basis"] not in best_examples):
            best_examples[row["basis"]] = row

    result = {
        "status": "PASS_P112_WALSH_TWO_TOTAL",
        "seed": "6ed83d31ab93b3878e4fc74abdee2988",
        "task": "complex-rank-shape-decoder",
        "base_commit": "ec8707299e2f40918f5f96cdab99ee49cdbabcf0",
        "selected_record_sha256": selected_sha,
        "model": {
            "geometry": "P112, XX^T=2G, exact all-pairs identity",
            "identity": "D=[X,XU], T=[X(I-VU^T),XV]",
            "coefficient_field": "integers",
            "characters": "chi_a(b)=(-1)^<a,b> for a,b in F_2^3",
            "ordered_distinct_pairs_per_side": 56,
            "initial_basis_candidate_count": 3136,
            "additional_unimodular_shear_candidate_count": 12544,
            "candidate_count": 15680,
            "basis_changes": ["identity", "upper_plus", "upper_minus", "lower_plus", "lower_minus"],
            "basis_change_matrices": [
                {"name": "identity", "M": [[1, 0], [0, 1]], "M_inverse_transpose": [[1, 0], [0, 1]]},
                {"name": "upper_plus", "M": [[1, 1], [0, 1]], "M_inverse_transpose": [[1, 0], [-1, 1]]},
                {"name": "upper_minus", "M": [[1, -1], [0, 1]], "M_inverse_transpose": [[1, 0], [1, 1]]},
                {"name": "lower_plus", "M": [[1, 0], [1, 1]], "M_inverse_transpose": [[1, -1], [0, 1]]},
                {"name": "lower_minus", "M": [[1, 0], [-1, 1]], "M_inverse_transpose": [[1, 1], [0, 1]]},
            ],
            "basis_change_rule": "U_new=U M; V_new=V M^{-T}; U_new V_new^T=UV^T exactly",
            "all_ten_terms_nonzero": True,
            "support_cost": "binary rank of the restricted P112 label pairing",
            "center_substitution": "replace the eight rank-8 center terms by this ten-term invoice",
        },
        "incumbent": {
            "local_profile": {str(r): n for r, n in selected_profile.items()},
            "center_charge": selected_center,
            "a_ceiling_hi": str(baseline),
            "a_ceiling_decimal": pinned_ceiling["ceiling"]["a_ceiling_decimal"],
            "five_percent_threshold": str(target),
        },
        "distinct_profiles": len(profile_counts),
        "basis_census": {
            name: {
                "candidates": sum(counts.values()),
                "profiles": [
                    {"profile": serialize_profile(profile), "candidates": count}
                    for profile, count in sorted(counts.items())
                ],
            }
            for name, counts in sorted(by_basis.items())
        },
        "profile_results": profile_results,
        "best_profile": best[1],
        "best_candidate_examples": best_examples,
        "controls": ctrl,
        "conclusion": (
            "finite construction clears the 5% packing-ceiling gate"
            if best[1]["meets_5_percent_gate"] else
            "no member of this finite Walsh-character shear domain clears the 5% packing-ceiling gate"
        ),
        "limits": [
            "The result covers only the 15,680 ordered Walsh-pair/basis tuples in the five listed bases.",
            "The ceiling permits fractional idle packing and waives source, frame, restoration, hosting, precision, and interface costs.",
            "No physical supplier, new selected result, or kappa is established.",
        ],
    }
    rows_blob = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    result["candidate_rows_sha256"] = hashlib.sha256(rows_blob).hexdigest()
    return result


def main():
    result = compute()
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if sys.argv[1:] == ["--write"]:
        OUT.write_text(text)
    else:
        require(OUT.read_text() == text, "RESULT.json differs from exact recomputation")
    print(result["status"],
          "candidates", result["model"]["candidate_count"],
          "profiles", result["distinct_profiles"],
          "best_profile", json.dumps(result["best_profile"]["profile"], sort_keys=True),
          "center", result["best_profile"]["center_charge"],
          "a_hi", result["best_profile"]["a_hi"],
          "gate", result["best_profile"]["meets_5_percent_gate"])


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        print("FAIL:", error)
        raise SystemExit(1)
