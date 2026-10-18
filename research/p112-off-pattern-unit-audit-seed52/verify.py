#!/usr/bin/env python3
"""Independent exact replay of the d0=76 asymmetric P112 witness (stdlib only)."""

from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SOURCE_HASHES = {
    "research/format-limits/scripts/c6_asym.py": "a9e17c1cf50a8403734a0e35863776a5ec7e60b44e9556f7b0206163c7f18cd0",
    "research/format-limits/scripts/e8units.py": "3134443d8327d0bf2a8a66c26327cf5268cec6b7ffd85dde750b7e197ce63ef1",
}


def need(condition, message):
    if not condition:
        raise SystemExit("FAIL " + message)


def parity(x):
    return x.bit_count() & 1


def gf2_rank(rows):
    basis = {}
    for value in rows:
        value = int(value)
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return len(basis)


def roots_e8():
    """Build the 120 representatives from the extended [8,4,4] Hamming code."""
    generators = (
        (1, 1, 1, 1, 0, 0, 0, 0),
        (0, 0, 1, 1, 1, 1, 0, 0),
        (0, 0, 0, 0, 1, 1, 1, 1),
        (0, 1, 0, 1, 0, 1, 0, 1),
    )
    code = {
        tuple(sum(coeff[k] * generators[k][j] for k in range(4)) % 2 for j in range(8))
        for coeff in product((0, 1), repeat=4)
    }
    supports = sorted(word for word in code if sum(word) == 4)
    need(len(supports) == 14, "extended Hamming code has 14 weight-four supports")
    roots = [tuple(2 if j == a else 0 for j in range(8)) for a in range(8)]
    for support in supports:
        indexes = [j for j, bit in enumerate(support) if bit]
        for signs in product((1, -1), repeat=3):
            row = [0] * 8
            row[indexes[0]] = 1
            for k, sign in enumerate(signs):
                row[indexes[k + 1]] = sign
            roots.append(tuple(row))
    need(len(roots) == 120, "E8 line count")
    gram = [[sum(a * b for a, b in zip(x, y)) // 2 for y in roots] for x in roots]
    need(all(gram[i][i] == 2 for i in range(120)), "E8 diagonal Gram entries")
    need(all(gram[i][j] in (-1, 0, 1) for i in range(120) for j in range(120) if i != j),
         "E8 off-diagonal Gram entries")
    return roots, gram


def orthonormal_basis(form):
    """Return rows C with C form C^T = I over F2, using bit-vector elimination."""
    n = len(form)

    def dot_form(x, y):
        return sum(parity(form[i] & y) for i in range(n) if (x >> i) & 1) & 1

    def complement(known):
        rows = [1 << i for i in range(n)]
        for b in known:
            rows = [row ^ (b if dot_form(row, b) else 0) for row in rows]
        return rows

    basis = []
    residual = [1 << i for i in range(n)]
    norms = [dot_form(row, row) for row in residual]
    while len(basis) < n:
        candidates = [i for i, q in enumerate(norms) if q]
        if candidates:
            b = residual[candidates[0]]
            basis.append(b)
            products = [dot_form(row, b) for row in residual]
            residual = [row ^ (b if p else 0) for row, p in zip(residual, products)]
            norms = [q ^ p for q, p in zip(norms, products)]
            continue

        # The residual form is alternating. Absorb a hyperbolic pair into an
        # earlier unit vector, preserving orthonormality while replacing it by
        # three unit vectors.
        nonzero = [row for row in residual if row]
        pair = next(((x, y) for x, y in combinations(nonzero, 2) if dot_form(x, y)), None)
        need(pair is not None and basis, "nondegenerate alternating residual pair")
        x, y = pair
        unit = basis.pop(0)
        basis.extend((unit ^ x, unit ^ y, unit ^ x ^ y))
        residual = complement(basis)
        norms = [dot_form(row, row) for row in residual]

    gram_out = [[dot_form(basis[i], basis[j]) for j in range(n)] for i in range(n)]
    need(all(gram_out[i][j] == int(i == j) for i in range(n) for j in range(n)), "orthonormal F2 basis")
    return basis


def labels_from_gram(gram):
    """Factor M=(J+G) mod 2 as U U^T using exact F2 row operations."""
    n = len(gram)
    mrows = [sum((((1 + gram[i][j]) & 1) << j) for j in range(n)) for i in range(n)]
    echelon = {}
    selected = []
    for i, value in enumerate(mrows):
        reduced = value
        while reduced:
            pivot = reduced.bit_length() - 1
            if pivot in echelon:
                reduced ^= echelon[pivot]
            else:
                echelon[pivot] = reduced
                selected.append(i)
                break
    width = len(selected)
    need(width == 9, "E8 pairing Gram rank is nine")

    form = [sum((((mrows[selected[i]] >> selected[j]) & 1) << j) for j in range(width))
            for i in range(width)]
    change = orthonormal_basis(form)
    labels = []
    for row in mrows:
        restricted = sum((((row >> selected[j]) & 1) << j) for j in range(width))
        labels.append([parity(restricted & basis_row) for basis_row in change])
    need(all((sum(labels[i][k] * labels[j][k] for k in range(width)) & 1)
             == ((1 + gram[i][j]) & 1) for i in range(n) for j in range(n)),
         "all 120 x 120 label pairings")
    return labels


def encode_label(row):
    return sum(int(bit) << (8 - j) for j, bit in enumerate(row))


def rank_submatrix(rows, row_ids, col_ids):
    packed = [sum(((rows[i] >> col) & 1) << j for j, col in enumerate(col_ids)) for i in row_ids]
    return gf2_rank(packed)


def build_witness(roots, gram, labels):
    ports = list(range(8, 120))
    local = {global_id: i for i, global_id in enumerate(ports)}
    label_values = [encode_label(labels[i]) for i in ports]
    target_to_sink = {75: 329, 76: 438}
    target_mu = {75: Fraction(-1), 76: Fraction(0)}
    d0 = roots[76]
    e = roots[0]

    # For each changed row, the extra-total support consists of source labels
    # paired to its sink, excluding the target itself, whose E8 root is
    # orthogonal to e and nonorthogonal to d0.
    extra_sets = {}
    for target, sink in target_to_sink.items():
        t = local[target]
        e_set = set()
        for s, global_s in enumerate(ports):
            paired = parity(sink & label_values[s])
            e_perp = sum(roots[global_s][k] * e[k] for k in range(8)) == 0
            d_nonzero = sum(roots[global_s][k] * d0[k] for k in range(8)) != 0
            if paired and s != t and e_perp and d_nonzero:
                e_set.add(s)
        need(t not in e_set, "extra-total support excludes its target")
        extra_sets[target] = e_set
    extra_sources = extra_sets[75] | extra_sets[76]
    need(len(extra_sources) == 24, "shared extra total has 24 source ports")

    # Baseline pairing M=(J+G) mod 2, with exactly two sink rows replaced.
    b_rows = []
    for t, global_t in enumerate(ports):
        sink = target_to_sink.get(global_t, label_values[t])
        b_rows.append(sum(parity(sink & label_values[s]) << s for s in range(len(ports))))
    n_rows = [[Fraction(gram[gt][gs], 2) for gs in ports] for gt in ports]
    alpha = {s: -sum(roots[ports[s]][k] * d0[k] for k in range(8)) for s in extra_sources}
    for global_t in (75, 76):
        t = local[global_t]
        mu = target_mu[global_t]
        vec = [Fraction(d0[k]) + mu * Fraction(e[k]) for k in range(8)]
        n_rows[t] = [sum(Fraction(roots[global_s][k]) * vec[k] for k in range(8)) + alpha.get(s, 0)
                       for s, global_s in enumerate(ports)]
    return ports, b_rows, n_rows, extra_sources, target_to_sink, target_mu


def exactness(b_rows, n_rows):
    for t, row in enumerate(n_rows):
        if not ((b_rows[t] >> t) & 1) or row[t] == 0:
            return False
        for s, value in enumerate(row):
            if s != t and value and ((b_rows[t] >> s) & 1):
                return False
    return True


def main():
    for path, expected in SOURCE_HASHES.items():
        actual = sha256((ROOT / path).read_bytes()).hexdigest()
        need(actual == expected, "source pin " + path)

    roots, gram = roots_e8()
    labels = labels_from_gram(gram)
    ports, b_rows, n_rows, extra_sources, target_to_sink, target_mu = build_witness(roots, gram, labels)
    need(len(ports) == 112, "P112 port count")
    need(exactness(b_rows, n_rows), "N o B has exactly the diagonal support on all 112 x 112 entries")

    copy_rank = gf2_rank(b_rows)
    need(copy_rank == 9, "global sink/source pairing window")
    coordinate_ranks = []
    for a in range(8):
        readers = [i for i, global_i in enumerate(ports) if roots[global_i][a] != 0 or global_i in target_to_sink]
        sources = [i for i, global_i in enumerate(ports) if roots[global_i][a] != 0]
        coordinate_ranks.append(rank_submatrix(b_rows, readers, sources))
    extra_rank = rank_submatrix(b_rows, [67, 68], sorted(extra_sources))
    copy_cost = sum(coordinate_ranks) + extra_rank
    need(coordinate_ranks == [8] * 8 and extra_rank == 1 and copy_cost == 65,
         "eight coordinate ranks, shared-total rank and total copy rank")

    relaxed_local = [ports.index(i) for i in (75, 76)]
    corrections = [sum(s != t and value != 0 for s, value in enumerate(n_rows[t])) for t in relaxed_local]
    baseline_corrections = [sum(s != t and gram[gt][gs] != 0 for s, gs in enumerate(ports))
                            for t, gt in zip(relaxed_local, (75, 76))]
    need(corrections == [28, 28] and baseline_corrections == [52, 52], "exact correction support counts")
    correction_sources = {
        str(gt): [ports[s] for s, value in enumerate(n_rows[t]) if s != t and value != 0]
        for gt, t in zip((75, 76), relaxed_local)
    }
    baseline_sources = {
        str(gt): [gs for s, gs in enumerate(ports) if s != t and gram[gt][gs] != 0]
        for gt, t in zip((75, 76), relaxed_local)
    }

    # Negative controls: change a sink bit, or change the d0=76 target's
    # coefficient. The published witness's exact support property must fail.
    bad_sink_rows = list(b_rows)
    bad_sink_rows[relaxed_local[0]] = sum(
        parity(328 & encode_label(labels[global_s])) << s for s, global_s in enumerate(ports)
    )
    need(not exactness(bad_sink_rows, n_rows), "negative control: altered sink label")

    bad_n_rows = [list(row) for row in n_rows]
    wrong_vec = [Fraction(roots[76][k]) for k in range(8)]
    bad_n_rows[relaxed_local[0]] = [sum(Fraction(roots[global_s][k]) * wrong_vec[k] for k in range(8))
                                    + (-sum(roots[ports[s]][k] * roots[76][k] for k in range(8))
                                       if s in extra_sources else 0)
                                    for s, global_s in enumerate(ports)]
    need(not exactness(b_rows, bad_n_rows), "negative control: altered relaxed-row coefficient")

    # Hash canonical row encodings so the full exact matrices have a compact,
    # reproducible receipt in addition to the entrywise checks above.
    b_encoding = "\n".join(f"{row:028x}" for row in b_rows) + "\n"
    n_encoding = "\n".join(",".join(str(value) for value in row) for row in n_rows) + "\n"
    extra_global = [ports[s] for s in sorted(extra_sources)]
    alpha = {str(global_s): -sum(roots[global_s][k] * roots[76][k] for k in range(8))
             for global_s in extra_global}
    result = {
        "schema_version": 1,
        "assignment": {"os_random_integer": 3423301012, "seed": 52, "track": "structural decoder"},
        "base_commit": "bce54fb3f895cbe5cd4c0eb477c3afeed100190f",
        "predecessor": "research/format-limits/README.md C.6; PR595 / PR717 model",
        "domain": {"global_line_ids": [8, 119], "rows": 112, "matrix_entries": 12544},
        "geometry": {"e_line_id": 0, "e_vector": list(roots[0]), "d0_line_id": 76, "d0_vector": list(roots[76])},
        "witness": {
            "relaxed_target_line_ids": [75, 76],
            "sink_labels": {"75": 329, "76": 438},
            "row_coefficients_mu": {"75": "-1", "76": "0"},
            "shared_extra_source_line_ids": extra_global,
            "extra_total_coefficients": alpha,
        },
        "checks": {
            "exact_diagonal_support": True,
            "sink_source_window_rank": copy_rank,
            "coordinate_copy_ranks": coordinate_ranks,
            "extra_total_copy_rank": extra_rank,
            "total_copy_rank_cost": copy_cost,
            "relaxed_row_correction_supports": corrections,
            "coordinate_row_correction_supports": baseline_corrections,
            "relaxed_row_correction_global_source_ids": correction_sources,
            "coordinate_row_correction_global_source_ids": baseline_sources,
            "negative_controls_fail": ["sink label 329->328", "target 75 mu -1->0"],
        },
        "canonical_matrix_sha256": {
            "pairing_rows_little_column_bit_order_hex": sha256(b_encoding.encode()).hexdigest(),
            "decoder_rows_fraction_strings": sha256(n_encoding.encode()).hexdigest(),
        },
        "source_sha256": SOURCE_HASHES,
        "scope": "Exact finite witness audit only; no completed supplier invoice and no new kappa.",
    }
    cert_path = Path(__file__).resolve().with_name("CERTIFICATE.json")
    if "--write-certificate" in sys.argv:
        need(not cert_path.exists(), "refuse to overwrite an existing certificate")
        cert_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print("WROTE_CERTIFICATE " + str(cert_path))
        return
    need(cert_path.is_file(), "missing committed CERTIFICATE.json")
    need(json.loads(cert_path.read_text()) == result, "committed exact witness certificate")

    print("PASS_P112_ASYMMETRIC_UNIT_AUDIT seed=52 d0=76 ports=112 entries=12544 "
          "window=9 extra_sources=24 copy_ranks=8x8+1 copy_cost=65 "
          "corrections=28+28 baseline=52+52 controls=2 no_new_kappa")


if __name__ == "__main__":
    main()
