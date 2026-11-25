#!/usr/bin/env python3
"""Audit a source-side correction for the selected P112 centre cut.

This exact, bounded screen tests (1) whether a four-kernel-row unimodular
completion can keep the original reader with no dirty correction, and (2) the
alternative identity that uses the original reader plus a source-side term.
Neither screen constructs or admits a physical supplier.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None,
            "cannot load " + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def support(matrix) -> int:
    return sum(value != 0 for row in matrix for value in row)


def independent_row_indices(matrix):
    basis = {}
    chosen = []
    for index, original in enumerate(matrix):
        row = [Q(value) for value in original]
        for pivot, normalized in sorted(basis.items()):
            coefficient = row[pivot]
            if coefficient:
                row = [x - coefficient * y
                       for x, y in zip(row, normalized)]
        lead = next((j for j, value in enumerate(row) if value), None)
        if lead is not None:
            value = row[lead]
            basis[lead] = [x / value for x in row]
            chosen.append(index)
    return chosen


def transpose_sum(a, b, c):
    return [[x + y - z for x, y, z in zip(row_a, row_b, row_c)]
            for row_a, row_b, row_c in zip(a, b, c)]


def main() -> None:
    audit = load_module(
        "p112_input_correction_audit",
        ROOT / "research/p112-tetrad-cut-consumer/verify.py")
    selected = load_module(
        "p112_input_correction_selected",
        ROOT / "research/selected-p112-tetrad-rank32-route/verify.py")
    basis = load_module(
        "p112_input_correction_basis",
        ROOT / "research/p112-tetrad-dual-anchor-screen/verify.py")
    gauge = load_module(
        "p112_input_correction_gauge",
        ROOT / "research/gauge44-port-syndrome-encoding/verify.py")
    geometry = load_module(
        "p112_input_correction_geometry",
        ROOT / "research/p112-tetrad-local-decoder/verify.py")
    ceiling = load_module(
        "p112_input_correction_ceiling",
        ROOT / "research/complex-local-word-ceiling/ceiling.py")

    word, _ = selected.load_word()
    selected.build_bound_decoder(word)
    _, scatter, archive_sha256 = audit.read_selected_scatter(gauge)

    roots, frame = geometry.roots_and_frame()
    live = sorted(set(roots) - set(frame))
    classes = defaultdict(list)
    for root_index, root in enumerate(live):
        coordinates = [geometry.dot(root, vector) // 4 for vector in frame]
        tetrad = tuple(j for j, value in enumerate(coordinates) if value)
        parity = sum(coordinates[j] < 0 for j in tetrad) % 2
        classes[tetrad, parity].append((root_index, coordinates))
    tetrads = sorted({tetrad for tetrad, _ in classes})
    require(len(tetrads) == 14, "selected P112 tetrad inventory changed")

    # Each item holds the exact source-bound block matrices needed by both
    # alternative-consumer checks below.
    blocks = []
    no_correction = []
    for tetrad in tetrads:
        even, odd = classes[tetrad, 0], classes[tetrad, 1]
        e0 = [[value[j] for j in tetrad] for _, value in even]
        e1 = [[value[j] for j in tetrad] for _, value in odd]
        e = e0 + e1
        k = basis.matmul(e, basis.transpose(e))
        cross = basis.matmul(e0, basis.transpose(e1))
        transition = basis.matmul(cross, basis.D_EVEN_SUM)
        require(all(value % 4 == 0
                    for row in transition for value in row),
                "kernel transition is no longer integral")
        top = [[-(value // 4) for value in row] for row in transition]
        kernel_rows = audit.transpose(top + basis.D_EVEN_SUM)
        complement = [[int(i == j) for j in range(8)]
                      for i in (0, 5, 6, 7)]
        u = kernel_rows + complement
        require(basis.determinant(u) == -1
                and basis.matmul(u, k)[:4] == [[0] * 8 for _ in range(4)],
                "selected kernel completion changed")

        root_indices = [i for i, _ in even + odd]
        ports = [selected.ROOT_TO_PORT[i] for i in root_indices]
        old = [scatter[port][:] for port in ports]
        changed = audit.matmul(audit.transpose(gauge.inverse(u)), old)
        hybrid = [old[i][:] if i < 4 else changed[i][:]
                  for i in range(8)]
        correction = [([Q(0)] * 8 if i < 4 else
                       [old[i][j] - changed[i][j] for j in range(8)])
                      for i in range(8)]
        uk = basis.matmul(u, k)
        correction_on_update = audit.matmul(
            audit.transpose(correction), uk)

        require([[hybrid[i][j] + correction[i][j]
                  for j in range(8)] for i in range(8)] == old,
                "hybrid dirty identity changed")
        require(audit.matmul(audit.transpose(hybrid), uk)
                == audit.matmul(audit.transpose(old), k),
                "hybrid product identity changed")

        blocks.append({
            "tetrad": tetrad,
            "root_indices": root_indices,
            "ports": ports,
            "E": e,
            "K": k,
            "U": u,
            "S": old,
            "H": hybrid,
            "C": correction,
            "J": correction_on_update,
        })

        # With no separate dirty correction, the unchanged arbitrary-dirty
        # reader must remain S. If U K has first four zero rows, write its
        # remaining four rows as F E^T. Then S^T U K = S^T K iff
        # S_bottom^T F = S^T E.
        a = audit.transpose(old[4:])
        w = audit.matmul(audit.transpose(old), e)
        a_rank = audit.rank(a)
        if a_rank == 0:
            require(support(w) > 0,
                    "zero-rank target unexpectedly admits the original reader")
            no_correction.append({
                "tetrad": tetrad,
                "bottom_reader_rank": 0,
                "consistent_F": False,
                "reason": "S_bottom is zero while S^T E is nonzero",
            })
            continue
        require(a_rank == 4,
                "unexpected partial rank in the selected bottom reader")
        rows = independent_row_indices(a)
        require(len(rows) == 4, "failed to choose an invertible minor")
        a_minor = [a[i] for i in rows]
        w_minor = [w[i] for i in rows]
        f = audit.matmul(gauge.inverse(a_minor), w_minor)
        require(audit.matmul(a, f) == w,
                "old-reader equation has no exact completion factor")
        f0 = basis.matmul(complement, e)
        require(audit.rank(f0) == 4,
                "canonical quotient basis is singular")
        transfer = audit.matmul(f, gauge.inverse(f0))
        transfer_rank, transfer_det = audit.matrix_rank_determinant(transfer)
        transfer_integral = all(
            value.denominator == 1 for row in transfer for value in row)
        no_correction.append({
            "tetrad": tetrad,
            "bottom_reader_rank": a_rank,
            "consistent_F": True,
            "quotient_transfer_rank": transfer_rank,
            "quotient_transfer_determinant": str(transfer_det),
            "transfer_integral": transfer_integral,
            "transfer_is_unimodular": (
                transfer_rank == 4 and transfer_integral
                and abs(transfer_det) == 1),
        })

    require(len(blocks) == 14 and len(no_correction) == 14,
            "not all source-bound blocks were checked")
    rank_histogram = Counter(row["bottom_reader_rank"]
                             for row in no_correction)
    transfer_det_histogram = Counter(
        row["quotient_transfer_determinant"] for row in no_correction
        if row["consistent_F"])
    transfer_rank_histogram = Counter(
        row["quotient_transfer_rank"] for row in no_correction
        if row["consistent_F"])
    transfer_integral_count = sum(
        row["transfer_integral"] for row in no_correction
        if row["consistent_F"])
    require(rank_histogram == Counter({4: 12, 0: 2})
            and transfer_rank_histogram == Counter({4: 10, 2: 2})
            and transfer_det_histogram == Counter({"0": 2, "2": 4, "16": 6})
            and transfer_integral_count == 12
            and not any(row.get("transfer_is_unimodular", False)
                        for row in no_correction),
            "no-correction completion obstruction changed")

    # The identity S^T(d+U K x) - Jx = S^T(d+Kx), with
    # J = C^T U K, avoids retaining d as a second input stream. It uses the
    # original reader S, plus the source-side correction Jx.
    prefix_screens = []
    for count in (3, 5, 9, 14):
        old_support = sum(support(block["S"]) for block in blocks[:count])
        correction_support = sum(support(block["J"])
                                 for block in blocks[:count])
        for block in blocks[:count]:
            require(transpose_sum(
                audit.matmul(audit.transpose(block["S"]),
                             audit.matmul(block["U"], block["K"])),
                [[Q(0)] * 8 for _ in range(8)],
                block["J"])
                == audit.matmul(audit.transpose(block["S"]), block["K"]),
                "source-side correction identity failed")

        overhead = correction_support
        profile = {
            1: 192 + 4 * count + overhead,
            2: 56 - 4 * count,
            72: 73,
            56: 1,
        }
        centre_charge = 112 - 4 * count
        unpaid = Q(1) + Q(count, 28)
        moment = ceiling.relax(
            profile, 73, 896, 9, centre_charge, Q(3, 997), R=51,
            unpaid=unpaid)
        bracket = ceiling.ceiling(
            profile, 73, 896, 9, centre_charge, grid=Q(1, 10**12),
            R=51, unpaid=unpaid)
        sensitivity = bracket[1] / (1 + bracket[1])
        require(moment[1] < 1 and sensitivity > Q(3, 1000),
                "source-side incidence sensitivity no longer clears 0.003")
        prefix_screens.append({
            "transformed_tetrads": count,
            "original_reader_support": old_support,
            "source_correction_support": correction_support,
            "rank1_incidence_profile": {
                str(r): n for r, n in sorted(profile.items())
            },
            "moment_at_3_over_997": [str(x) for x in moment],
            "ideal_incidence_sensitivity": str(sensitivity),
            "ideal_incidence_sensitivity_decimal": f"{float(sensitivity):.12f}",
        })

    j_supports = [support(block["J"]) for block in blocks]
    require(j_supports == [16, 24, 24, 16, 16, 24, 24,
                           24, 24, 16, 16, 24, 24, 16]
            and [row["source_correction_support"] for row in prefix_screens]
            == [64, 96, 192, 288]
            and [row["ideal_incidence_sensitivity_decimal"]
                 for row in prefix_screens]
            == ["0.004756582174", "0.011073245628",
                "0.020601886496", "0.029934752880"],
            "source-side incidence profile changed")

    receipt = {
        "status": "PASS_P112_SOURCE_SIDE_CORRECTION_SCREEN",
        "scope": "Exact source-bound no-dirty-correction completion obstruction and source-side correction identity for the selected P112 tetrads; relaxed incidence sensitivities only.",
        "selected_kappa_unchanged": "0.001672660197076918",
        "selected_archive_sha256": archive_sha256,
        "no_correction_completion": {
            "necessary_equation": "S_bottom^T F = S^T E",
            "block_rank_histogram": dict(sorted(rank_histogram.items())),
            "quotient_transfer_determinant_histogram":
                dict(sorted(transfer_det_histogram.items())),
            "quotient_transfer_rank_histogram":
                dict(sorted(transfer_rank_histogram.items())),
            "quotient_transfer_integral_count": transfer_integral_count,
            "unimodular_completions_preserving_S": 0,
            "blocks": no_correction,
            "scope_limit": "For the four-kernel-row P112 fusion route and original arbitrary-dirty reader S. This is not a universal obstruction to other consumers or changed endpoint contracts.",
        },
        "source_side_correction": {
            "identity": "S^T(d+U K x) - Jx = S^T(d+Kx), J=C^T U K, C=S-H",
            "term_supports_by_block": j_supports,
            "prefix_screens": prefix_screens,
            "interpretation": "The relaxed profile charges one rank-1 unit per nonzero J coefficient. It does not establish source availability at the consumer, a frame-compatible schedule, correction storage, a scalar ADD tariff, supplier admission, restoration, or a new kappa.",
        },
    }
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    print("PASS_P112_SOURCE_SIDE_CORRECTION_SCREEN blocks=14 "
          "no_dirty_correction_completions=0 source_J=64/96/192/288 "
          "ideal_kappa3=0.004756582174 no_new_kappa")


if __name__ == "__main__":
    main()
