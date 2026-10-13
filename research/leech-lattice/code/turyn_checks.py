#!/usr/bin/env python3
"""Exact Turyn tensor geometry, binary fits, and E8 equivalence checks.

Turyn code: (a+x, b+x, a+b+x), a,b in RM(1,3), x in a coordinate
permutation of RM(1,3) intersecting it in {0,1}. See Forney, Coset Codes II:
https://www2.ensc.sfu.ca/people/faculty/cavers/ENSC805/readings/34it05-forney-b.pdf
The integer Leech shell construction is Bannai--Sloane, equation (12):
https://neilsloane.com/doc/Me71.pdf

All tensor products, binary elimination, and equivalence checks use integers.
The pairwise audit streams 128 rows at a time, rather than storing a dense
23040-square matrix. Outputs contain no clocks or machine-dependent paths.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import numpy as np
from binary_labels import inverse, symplectic
from leech_geometry import EXPECTED_WEIGHTS, require, shell, verify


def write_json(output, name, value):
    (output / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def insert_binary(basis, value):
    value = int(value)
    while value:
        pivot = value.bit_length() - 1
        if pivot in basis:
            value ^= basis[pivot]
        else:
            basis[pivot] = value
            return True
    return False


def encode_rows(matrix):
    return [int.from_bytes(row.tobytes(), "little")
            for row in np.packbits(matrix.astype(np.uint8), axis=1, bitorder="little")]


def rank_rows(rows, stop=None):
    basis, selected = {}, []
    for index, value in enumerate(rows):
        if insert_binary(basis, value):
            selected.append(index)
        if stop is not None and len(basis) == stop:
            break
    return basis, selected


def construct_turyn():
    h = [sum(((a >> 3) ^ (((a & 7) & i).bit_count() % 2)) << i
             for i in range(8)) for a in range(16)]
    permutation = [0, 1, 2, 4, 3, 6, 7, 5]
    hp = [sum(((word >> permutation[i]) & 1) << i for i in range(8)) for word in h]
    require(set(h) & set(hp) == {0, 255}, "Hamming-code intersection")
    packed_words = sorted({(a ^ x) | ((b ^ x) << 8) | ((a ^ b ^ x) << 16)
                           for a in h for b in h for x in hp})
    require(len(packed_words) == 4096, "Turyn code dimension")
    words = np.array([[(word >> i) & 1 for i in range(24)]
                      for word in packed_words], dtype=np.int8)
    require(dict(Counter(map(int, words.sum(axis=1)))) == EXPECTED_WEIGHTS,
            "Turyn Golay weight enumerator")
    vectors = shell(words)
    lines, sample_histograms = verify(vectors, words, 16)
    blocks = lines.astype(np.int16).reshape(-1, 3, 8)
    norms = (blocks * blocks).sum(axis=2)
    require(not (norms % 8).any(), "Integral block norms")
    full = np.all(norms != 0, axis=1)
    require(int(full.sum()) == 92160, "Three-block line count")
    candidates = lines[full].copy()
    for block in range(3):
        sub = candidates[:, 8 * block:8 * (block + 1)]
        first = np.argmax(sub != 0, axis=1)
        signs = np.where(sub[np.arange(len(sub)), first] > 0, 1, -1)
        sub *= signs[:, None]
    representatives, multiplicities = np.unique(candidates, axis=0, return_counts=True)
    require(len(representatives) == 23040 and np.all(multiplicities == 4),
            "Four sign fibers per canonical tensor representative")
    line_set = set(map(bytes, lines))
    require(all(bytes(row) in line_set for row in representatives),
            "Canonical representatives remain in the Leech shell")
    representatives = representatives.astype(np.int16)
    rep_norms = (representatives.reshape(-1, 3, 8).astype(np.int32) ** 2).sum(axis=2)
    require(np.all(np.sort(rep_norms, axis=1) == [8, 8, 16]), "Tensor port profiles")
    profiles = np.argmax(rep_norms, axis=1)
    require(Counter(map(int, profiles)) == {0: 7680, 1: 7680, 2: 7680},
            "Profile populations")
    x = np.array([3] + [-1] * 7 + [1] * 16, dtype=np.int8)
    y = np.array([1] * 8 + [3] + [-1] * 7 + [1] * 8, dtype=np.int8)
    require(bytes(x) in line_set and bytes(y) in line_set, "Original label counterexample membership")
    counter_dots = [int(x[b:b + 8].astype(np.int16) @ y[b:b + 8]) for b in (0, 8, 16)]
    require(counter_dots == [-4, -4, 8], "Original label counterexample pairings")
    geometry = {
        "original_leech25_label_counterexample": {
            "x": x.tolist(), "y": y.tolist(), "raw_block_pairings": counter_dots,
            "raw_tensor_kernel": 128, "raw_total_pairing": 0,
            "binary_pairing_under_original_map": 1,
            "scope": "The original map has p(x).p(y)=1+(x.y/8) mod2. This active tensor pair violates that map; the new profile maps are different."},
        "hamming_code": h, "permutation": permutation, "hamming_code_prime": hp,
        "golay_words": len(words), "golay_weight_distribution": EXPECTED_WEIGHTS,
        "minimal_vectors": len(vectors), "minimal_lines": len(lines),
        "block_norm_histogram": [
            {"normalized_squared_norms": list(key), "count": count}
            for key, count in sorted(Counter(tuple(map(int, row)) for row in norms // 8).items())],
        "full_threeblock_lines": 92160, "canonical_representatives": 23040,
        "representative_fiber_size": 4, "ports_per_profile": 7680,
        "integer_lines_sha256": hashlib.sha256(lines.tobytes()).hexdigest(),
        "integer_representatives_sha256": hashlib.sha256(representatives.astype(np.int8).tobytes()).hexdigest(),
        "shell_distribution_sample_rows": sorted(map(int, sample_histograms)),
        "shell_distribution_scope": "All membership, norm, uniqueness and antipodal checks; full dot histograms only at the stated sample rows.",
    }
    return representatives, profiles, geometry


def block_dots(left, right):
    dots = [(left[:, b:b + 8] @ right[:, b:b + 8].T).astype(np.int32)
            for b in (0, 8, 16)]
    require(all(not (dot % 4).any() for dot in dots), "Block pairing divisible by four")
    return dots


def fit_parity(left, right):
    dots = block_dots(left, right)
    return ((1 ^ ((dots[0] // 4) & 1)) & (1 ^ ((dots[1] // 4) & 1))).astype(np.uint8)


def audit_pairwise(vectors, profiles):
    groups = [np.flatnonzero(profiles == high) for high in range(3)]
    basis_cubic, basis_parity = {}, {}
    selected_cubic, selected_parity = [], []
    profile_bases = [{}, {}, {}]
    profile_selected = [[], [], []]
    old_profile_basis, old_profile_selected = {}, []
    histogram = Counter()
    active_count = 0
    for offset in range(0, len(vectors), 128):
        chunk = vectors[offset:offset + 128]
        dots = block_dots(chunk, vectors)
        alpha = [((dot // 4) & 1).astype(np.uint8) for dot in dots]
        require(not (alpha[0] ^ alpha[1] ^ alpha[2]).any(), "Three block parity relation")
        product = dots[0] * dots[1] * dots[2]
        require(not (product % 128).any(), "Integral scaled tensor kernel")
        values, counts = np.unique(product, return_counts=True)
        histogram.update(dict(zip(map(int, values), map(int, counts))))
        fit_cubic = (1 ^ ((product // 128) & 1)).astype(np.uint8)
        fit_lowdegree = ((1 ^ alpha[0]) & (1 ^ alpha[1])).astype(np.uint8)
        for local in range(len(chunk)):
            index = offset + local
            require(product[local, index] == 1024, "Tensor diagonal")
            require(fit_cubic[local, index] == fit_lowdegree[local, index] == 1,
                    "Binary fitting diagonals")
            active = product[local] != 0
            active[index] = False
            require(not (fit_cubic[local].astype(bool) & active).any(), "Cubic fitting zeros")
            require(not (fit_lowdegree[local].astype(bool) & active).any(), "Block parity fitting zeros")
            active_count += int(active.sum())
            high = int(profiles[index])
            low = (high + 1) % 3
            indices = groups[high]
            fit9 = 1 ^ alpha[low][local, indices]
            require(not (fit9.astype(bool) & active[indices]).any(), "Profile rank-nine fitting zeros")
            if insert_binary(profile_bases[high], encode_rows(fit9[None, :])[0]):
                profile_selected[high].append(index)
            if high == 0 and insert_binary(old_profile_basis, encode_rows(fit_cubic[local, indices][None, :])[0]):
                old_profile_selected.append(index)
        for local, value in enumerate(encode_rows(fit_cubic)):
            if insert_binary(basis_cubic, value):
                selected_cubic.append(offset + local)
        for local, value in enumerate(encode_rows(fit_lowdegree)):
            if insert_binary(basis_parity, value):
                selected_parity.append(offset + local)
    histogram[1024] -= len(vectors)
    if histogram[1024] == 0:
        del histogram[1024]
    require(set(histogram) == {-128, 0, 128}, "Exact offdiagonal tensor values")
    require(len(basis_cubic) == 505 and len(basis_parity) == 53, "Global fitting ranks")
    require(len(old_profile_basis) == 390, "Single-profile cubic fitting rank")
    require([len(b) for b in profile_bases] == [9, 9, 9], "Profile fitting ranks")
    report = {
        "ordered_pairs_checked": len(vectors) ** 2,
        "active_offdiagonal_ordered_pairs": active_count,
        "raw_tensor_offdiagonal_histogram": dict(histogram),
        "tensor_gram_denominator": 512, "tensor_diagonal": 2,
        "cubic_fit": {"formula": "B=1+raw_tensor_Gram/128 mod2", "binary_rank": 505,
                      "independent_port_rows": selected_cubic},
        "single_profile_cubic_fit": {"high_block": 0, "binary_rank": 390,
                                     "independent_port_rows": old_profile_selected},
        "parity_fit": {"formula": "alpha_j=raw_block_dot_j/4 mod2; B=(1+alpha_0)(1+alpha_1)",
                       "binary_rank": 53, "independent_port_rows": selected_parity},
        "profile_fit_independent_rows": profile_selected,
        "scope": "Ranks505,390,53 are ranks of the specified completions, not minimum-rank lower bounds over other completions.",
    }
    return report, selected_parity, profile_selected


def factor_odd_gram(gram):
    size = len(gram)
    require(size % 2 == 1 and np.all(np.diag(gram) == 1), "Odd Gram basis")
    characteristic = (inverse(gram) @ np.diag(gram)) & 1
    require(int(characteristic @ gram @ characteristic) % 2 == 1, "Characteristic vector norm")
    even = np.concatenate((np.eye(size - 1, dtype=np.uint8),
                           np.ones((size - 1, 1), dtype=np.uint8)), axis=1)
    alternating = (even @ gram @ even.T) & 1
    standard = (even @ even.T) & 1
    change = (inverse(symplectic(alternating)) @ symplectic(standard)) & 1
    left = np.concatenate((characteristic[None, :], even), axis=0)
    right = np.concatenate((np.ones((1, size), dtype=np.uint8), (change @ even) & 1), axis=0)
    factor = (inverse(left) @ right) & 1
    require(np.array_equal((factor @ factor.T) & 1, gram), "Gram factor isometry")
    return factor


def profile_labels(vectors, profiles, selected_rows):
    labels = np.zeros((len(vectors), 27), dtype=np.uint8)
    report = []
    for high in range(3):
        low = (high + 1) % 3
        indices = np.flatnonzero(profiles == high)
        selected = selected_rows[high]
        dots = vectors[indices, 8 * low:8 * (low + 1)] @ vectors[selected, 8 * low:8 * (low + 1)].T
        require(not (dots % 4).any(), "Profile label coordinate pairing")
        coordinates = (1 ^ ((dots // 4) & 1)).astype(np.uint8)
        location = {int(index): local for local, index in enumerate(indices)}
        gram = coordinates[[location[index] for index in selected]]
        factor = factor_odd_gram(gram)
        block_labels = (coordinates @ inverse(gram) @ factor) & 1
        require(np.all(block_labels.sum(axis=1) % 2 == 1), "Odd profile labels")
        labels[indices, high * 9:(high + 1) * 9] = block_labels
        report.append({"high_block": high, "low_block_used": low, "ports": len(indices),
                       "binary_rank": 9, "independent_port_rows": selected,
                       "gram_mod2": gram.tolist(), "gram_factor": factor.tolist(),
                       "coordinate_rule": "q_i(v)=1+raw_low_block_dot(v, selected_i)/4 mod2; p=q G^-1 gram_factor"})
    basis, _ = rank_rows(encode_rows(labels))
    require(len(basis) == 27, "Direct-sum label rank")
    return labels, {"binary_rank": 27, "profiles": report,
                    "pairing_proof": "The streamed audit establishes each rank-nine symmetric fitting matrix. Its selected principal Gram matrix is invertible, so its nine selected columns retain the full row space. The displayed factor reconstructs that entire Gram matrix. Different profiles occupy disjoint coordinate summands, giving zero cross-profile pairings."}


def support_probe(values, packed, dimension):
    support = np.flatnonzero(values != 0)
    basis, selected = rank_rows((packed[int(index)] for index in support), stop=dimension)
    return {"rank": len(basis), "support_size": len(support),
            "independent_port_rows": support[selected].tolist()}


def orthogonal_ports(vectors, subset=None):
    remaining = np.arange(len(vectors)) if subset is None else subset.copy()
    selected = []
    while len(remaining):
        index = int(remaining[0])
        selected.append(index)
        product = np.ones(len(remaining), dtype=np.int32)
        for block in (0, 8, 16):
            product *= vectors[remaining, block:block + 8] @ vectors[index, block:block + 8]
        remaining = remaining[product == 0]
    require(len(selected) == 512, "Tensor real rank witness")
    dots = block_dots(vectors[selected], vectors[selected])
    gram = dots[0] * dots[1] * dots[2]
    require(np.array_equal(gram, 1024 * np.eye(512, dtype=np.int32)), "Exact orthogonal tensor basis")
    return selected


def centers_audit(vectors, profiles, parity_coordinates, labels27):
    packed53 = encode_rows(parity_coordinates)
    packed27 = encode_rows(labels27)
    require(len(rank_rows(packed53)[0]) == 53, "Parity coordinate rank")
    odd = np.flatnonzero(np.all(vectors % 2 != 0, axis=1))
    require(len(odd) == 12288, "Odd-coordinate tensor ports")
    odd53 = len(rank_rows(packed53[int(i)] for i in odd)[0])
    odd27 = len(rank_rows(packed27[int(i)] for i in odd)[0])
    require((odd53, odd27) == (49, 24), "Odd orbit label ranks")
    literal = []
    features = (vectors[:, :8, None, None] * vectors[:, None, 8:16, None]
                * vectors[:, None, None, 16:24]).reshape(len(vectors), 512)
    for column in range(512):
        r53 = support_probe(features[:, column], packed53, 53)
        r27 = support_probe(features[:, column], packed27, 27)
        require(r53["rank"] == 53 and r27["rank"] == 27, "Literal tensor encoder ranks")
        literal.append({"tensor_coordinate": [column // 64, (column // 8) % 8, column % 8],
                        "parity_fit53": r53, "profile_fit27": r27})
    rng = np.random.default_rng(5323040)
    searches = {}
    choices = np.unique(np.concatenate((np.arange(64), rng.choice(len(vectors), 128, replace=False))))
    results = []
    for index in choices:
        product = np.ones(len(vectors), dtype=np.int32)
        for block in (0, 8, 16):
            product *= vectors[:, block:block + 8] @ vectors[index, block:block + 8]
        result = support_probe(product, packed53, 53)
        result["port_index"] = int(index)
        results.append(result)
    searches["port_kernel_encoders"] = results
    results = []
    for first, second in rng.integers(0, 512, size=(64, 2)):
        if first == second:
            continue
        for sign in (-1, 1):
            result = support_probe(features[:, first] + sign * features[:, second], packed53, 53)
            result["terms"] = [int(first), int(second), sign]
            results.append(result)
    searches["two_monomial_encoders"] = results
    h4 = np.array([[1, 1, 1, 1], [1, -1, 1, -1], [1, 1, -1, -1], [1, -1, -1, 1]], dtype=np.int16)
    h8 = np.zeros((8, 8), dtype=np.int16)
    h8[:4, :4] = h8[4:, 4:] = h4
    transformed = [vectors[:, block:block + 8] @ h8.T for block in (0, 8, 16)]
    results = []
    for i, j, k in rng.integers(0, 8, size=(128, 3)):
        product = transformed[0][:, i].astype(np.int32) * transformed[1][:, j] * transformed[2][:, k]
        result = support_probe(product, packed53, 53)
        result["coordinates"] = [int(i), int(j), int(k)]
        results.append(result)
    searches["hadamard4_encoders"] = results
    directions = [np.unique(vectors[:, block:block + 8], axis=0) for block in (0, 8, 16)]
    results = []
    for _ in range(256):
        selected = [int(rng.integers(0, len(d))) for d in directions]
        product = np.ones(len(vectors), dtype=np.int32)
        for block, index, direction in zip((0, 8, 16), selected, directions):
            product *= vectors[:, block:block + 8] @ direction[index]
        result = support_probe(product, packed53, 53)
        result["directions"] = [direction[index].tolist() for direction, index in zip(directions, selected)]
        results.append(result)
    searches["independent_leech_block_encoders"] = results
    require(sum(map(len, searches.values())) == 703, "Adapted encoder probe count")
    require(all(result["rank"] == 53 for values in searches.values() for result in values),
            "Adapted encoder probe rank")
    return {"literal_centers": literal, "literal_center_count": 512,
            "literal_support_rank_histograms": {"parity_fit53": {53: 512}, "profile_fit27": {27: 512}, "each_profile_fit9": {9: 512}},
            "odd_orbit_spans": {"parity_fit53": odd53, "profile_fit27": odd27},
            "adapted_encoder_probes": searches, "adapted_probe_count": 703,
            "orthogonal_real_basis_port_indices": orthogonal_ports(vectors),
            "single_profile_orthogonal_real_basis_port_indices": orthogonal_ports(vectors, np.flatnonzero(profiles == 0)),
            "real_feature_rank": 512,
            "scope": "The703 adapted probes use the specified53-dimensional parity fit only. They do not constitute a lower bound for all encoders or all binary representations. The27-dimensional construction is assessed separately by exact E8 equivalence and fixed-label cross constraints."}


def e8_equivalence(vectors, profiles, labels):
    result = {}
    for high in range(3):
        selected = np.flatnonzero(profiles == high)
        low = (high + 1) % 3
        other = [i for i in range(3) if i != low]
        roots, assignment, counts = np.unique(vectors[selected, 8 * low:8 * (low + 1)],
                                               axis=0, return_inverse=True, return_counts=True)
        require(len(roots) == 120 and np.all(counts == 64), "E8 groups of64")
        root_gram = roots.astype(np.int32) @ roots.T
        require(np.all(np.diag(root_gram) == 8), "E8 root norms")
        np.fill_diagonal(root_gram, 0)
        require(np.all(np.isin(root_gram, [-4, 0, 4])), "E8 offdiagonal root pairings")
        groups, histogram, reference = [], Counter(), None
        for group in range(120):
            indices = selected[np.flatnonzero(assignment == group)]
            require(np.all(labels[indices] == labels[indices[0]]), "Group basis change preserves binary label")
            w = vectors[indices].astype(np.int32)
            z = (w[:, 8 * other[0]:8 * (other[0] + 1), None]
                 * w[:, None, 8 * other[1]:8 * (other[1] + 1)]).reshape(64, 64)
            require(np.array_equal(z @ z.T, 128 * np.eye(64, dtype=np.int32)), "Orthogonal E8 fiber")
            if reference is None:
                reference = z
            numerator = z @ reference.T
            require(np.array_equal(numerator @ numerator.T, 128 ** 2 * np.eye(64, dtype=np.int32)),
                    "Dyadic orthogonal fiber map")
            require(np.array_equal(numerator.T @ z, 128 * reference), "Exact fiber flattening")
            values, multiplicities = np.unique(numerator, return_counts=True)
            histogram.update(dict(zip(map(int, values), map(int, multiplicities))))
            groups.append({"root": roots[group].tolist(), "port_indices": indices.tolist()})
        result[str(high)] = {"high_block": high, "label_low_block": low, "remaining_blocks": other,
                            "groups": groups, "group_count": 120, "ports_per_group": 64,
                            "raw_remaining_tensor_gram": 128, "change_matrix_denominator": 128,
                            "change_numerator_histogram": dict(histogram),
                            "flattened_kernel": "diag(R_g^T) K diag(R_g)=2 G_E8 tensor I64; G_E8=raw_low_root_Gram/8",
                            "identity": "Z_g Z_g^T=128I; R_g=Z_g Z_0^T/128; R_g^T Z_g=Z_0. Every basis change mixes only ports carrying the identical binary label."}
    return result


def cross_constraints(vectors, profiles, labels):
    groups = [np.flatnonzero(profiles == i) for i in range(3)]
    packed = [labels[:, 9 * i:9 * (i + 1)].astype(np.int32) @ (1 << np.arange(9, dtype=np.int32))
              for i in range(3)]
    report = {}
    for first, second in [(0, 1), (0, 2), (1, 2)]:
        basis, witnesses, seen, visited = {}, [], set(), 0
        for i in groups[first]:
            candidates = groups[second]
            product = np.ones(len(candidates), dtype=np.int32)
            for block in (0, 8, 16):
                product *= vectors[candidates, block:block + 8] @ vectors[i, block:block + 8]
            for j in candidates[product != 0]:
                p, q = int(packed[first][i]), int(packed[second][j])
                visited += 1
                if (p, q) in seen:
                    continue
                seen.add((p, q))
                outer = sum(q << (9 * bit) for bit in range(9) if (p >> bit) & 1)
                if insert_binary(basis, outer):
                    witnesses.append({"ports": [int(i), int(j)], "labels": [p, q],
                                      "outer_product_packed_decimal": str(outer)})
                if len(basis) == 81:
                    break
            if len(basis) == 81:
                break
        require(len(basis) == 81, "Fixed-label cross-Gram constraints")
        report[f"{first},{second}"] = {"constraint_rank": 81, "unknown_cross_gram_entries": 81,
                                        "witness_edges": witnesses, "active_edges_visited": visited,
                                        "distinct_label_pairs_visited": len(seen)}
    report["scope"] = "The fixed rank-nine profile label maps, each with a nine-dimensional image span, force every9x9 cross-Gram block to vanish. This proves rank27 only for linear embeddings of those maps. It does not cover representations with added isotropic radical components, nonlinear maps, or different fitting maps."
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outputdir", type=Path, required=True)
    output = parser.parse_args().outputdir
    output.mkdir(parents=True, exist_ok=True)
    vectors, profiles, geometry = construct_turyn()
    fits, selected_parity, selected_profile = audit_pairwise(vectors, profiles)
    labels, profile_report = profile_labels(vectors, profiles, selected_profile)
    fits["profile9_direct_sum27"] = profile_report
    parity_coordinates = fit_parity(vectors, vectors[selected_parity])
    centers = centers_audit(vectors, profiles, parity_coordinates, labels)
    equivalence = e8_equivalence(vectors, profiles, labels)
    cross = cross_constraints(vectors, profiles, labels)
    write_json(output, "TURYN-GEOMETRY.json", geometry)
    write_json(output, "TURYN-FITS.json", fits)
    write_json(output, "TURYN-CENTERS.json", centers)
    write_json(output, "TURYN-E8-EQUIVALENCE.json", equivalence)
    write_json(output, "TURYN-CROSS-CONSTRAINTS.json", cross)
    print(json.dumps({"ports": len(vectors), "tensor_real_rank": 512,
                      "binary_ranks": {"cubic": 505, "block_parity": 53,
                                       "each_profile": 9, "direct_sum": 27},
                      "literal_support_ranks": [53, 27], "adapted_probes": 703,
                      "e8_copies_per_profile": 64, "cross_constraint_ranks": [81, 81, 81]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
