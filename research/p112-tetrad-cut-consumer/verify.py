#!/usr/bin/env python3
"""Bind three P112 tetrad basis changes to the selected gauge44 centre cut."""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[2]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None,
            "cannot load " + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def matmul(a, b):
    require(bool(a) and bool(b) and len(a[0]) == len(b),
            "matrix product shape")
    return [[sum((a[i][k] * b[k][j] for k in range(len(b))), Q(0))
             for j in range(len(b[0]))] for i in range(len(a))]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def rank(matrix):
    rows = [[Q(value) for value in row] for row in matrix]
    pivot_row = 0
    for column in range(len(rows[0])):
        pivot = next((i for i in range(pivot_row, len(rows))
                      if rows[i][column]), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        scale = rows[pivot_row][column]
        rows[pivot_row] = [value / scale for value in rows[pivot_row]]
        for i in range(len(rows)):
            if i != pivot_row and rows[i][column]:
                scale = rows[i][column]
                rows[i] = [rows[i][j] - scale * rows[pivot_row][j]
                           for j in range(len(rows[0]))]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def read_selected_scatter(gauge):
    archive_bytes = gauge.ARCHIVE.read_bytes()
    archive_hash = hashlib.sha256(archive_bytes).hexdigest()
    require(archive_hash == gauge.ARCHIVE_SHA256,
            "selected replay archive hash changed")
    with tarfile.open(gauge.ARCHIVE, "r:gz") as archive:
        compressed_word = archive.extractfile(gauge.MEMBER).read()
        phase_payload = archive.extractfile(gauge.PHASE_MEMBER).read()
    require(hashlib.sha256(compressed_word).hexdigest() == gauge.MEMBER_SHA256,
            "selected canonical-word member hash changed")
    require(hashlib.sha256(phase_payload).hexdigest() == gauge.PHASE_SHA256,
            "selected data-phase payload hash changed")
    word = json.loads(gzip.decompress(compressed_word))
    phases = json.loads(phase_payload)
    recipes = sorted(phases["recipes"], key=lambda item: item["port"])
    labels = [item["q"] for item in recipes]
    require(len(labels) == 112 and
            [item["port"] for item in recipes] == list(range(112)),
            "selected port labels are not in canonical port order")
    require(word["ports"] == labels,
            "selected word and data-phase port labels disagree")

    centers = word["centers"]
    require(len(centers) == 8 and len(set(centers)) == 8,
            "expected eight selected centre destinations")
    require(set(centers).isdisjoint(range(112, 224)),
            "centre destinations alias a live port source")
    center_index = {register: index for index, register in enumerate(centers)}
    scatter = [[Q(0) for _ in centers] for _ in range(112)]
    for instruction in word["cut"]:
        op, source, destination, numerator, denominator, *_ = instruction
        require(op == "add" and 112 <= source < 224 and
                destination in center_index,
                "unexpected selected centre-cut instruction")
        scatter[source - 112][center_index[destination]] += Q(
            numerator, denominator)
    require(len(word["cut"]) == 176 and
            sum(value != 0 for row in scatter for value in row) == 176,
            "selected cut instruction/support count changed")
    return word, scatter, archive_hash


def run():
    geometry = load_module(
        "p112_consumer_geometry",
        ROOT / "research/p112-tetrad-local-decoder/verify.py")
    selected = load_module(
        "p112_consumer_selected",
        ROOT / "research/selected-p112-tetrad-rank32-route/verify.py")
    p112 = load_module(
        "p112_consumer_basis",
        ROOT / "research/p112-tetrad-dual-anchor-screen/verify.py")
    gauge = load_module(
        "p112_consumer_gauge",
        ROOT / "research/gauge44-port-syndrome-encoding/verify.py")
    ceiling = load_module(
        "p112_consumer_ceiling",
        ROOT / "research/complex-local-word-ceiling/ceiling.py")

    selected_record = json.loads(
        (ROOT / "certificates/selected-result.json").read_text())
    require(selected_record["kappa"] == "836330098538459/500000000000000000",
            "selected result changed")
    word, _ = selected.load_word()
    selected.build_bound_decoder(word)
    word, scatter, archive_hash = read_selected_scatter(gauge)

    roots, frame = geometry.roots_and_frame()
    live = sorted(set(roots) - set(frame))
    require(len(live) == 112, "selected P112 live-root count changed")
    classes = defaultdict(list)
    for root_index, root in enumerate(live):
        coordinates = [geometry.dot(root, vector) // 4 for vector in frame]
        tetrad = tuple(i for i, value in enumerate(coordinates) if value)
        require(len(tetrad) == 4 and
                all(coordinates[i] in (-1, 1) for i in tetrad),
                "live root is not a signed tetrad row")
        parity = sum(coordinates[i] < 0 for i in tetrad) % 2
        classes[tetrad, parity].append((root_index, coordinates))
    tetrads = sorted({tetrad for tetrad, _ in classes})
    require(len(tetrads) == 14, "selected P112 tetrad count changed")

    original_cut = [row[:] for row in scatter]
    changed_cut = [row[:] for row in scatter]
    block_results = []
    changed_ports = set()
    for tetrad in tetrads[:3]:
        even, odd = classes[tetrad, 0], classes[tetrad, 1]
        require(len(even) == len(odd) == 4,
                "selected tetrad frame sizes changed")
        e0 = [[value[j] for j in tetrad] for _, value in even]
        e1 = [[value[j] for j in tetrad] for _, value in odd]
        e = e0 + e1
        k = p112.matmul(e, p112.transpose(e))
        cross = p112.matmul(e0, p112.transpose(e1))
        transition = p112.matmul(cross, p112.D_EVEN_SUM)
        require(all(value % 4 == 0 for row in transition for value in row),
                "kernel transition lost integrality")
        top = [[-(value // 4) for value in row] for row in transition]
        kernel_rows = p112.transpose(top + p112.D_EVEN_SUM)
        complement = [[int(i == j) for j in range(8)] for i in (0, 5, 6, 7)]
        u = kernel_rows + complement
        require(p112.determinant(u) == -1,
                "basis change is not unimodular")
        require(p112.matmul(u, k)[:4] == [[0] * 8 for _ in range(4)],
                "first four transformed outputs do not annihilate the update")

        ports = [selected.ROOT_TO_PORT[i] for i, _ in even + odd]
        require(len(set(ports)) == 8, "tetrad port map is not injective")
        changed_ports.update(ports)
        old_block = [scatter[port][:] for port in ports]
        # If y' = U y, then S^T y = (U^-T S)^T y'.
        new_block = matmul(transpose(gauge.inverse(u)), old_block)
        composed = matmul(transpose(new_block), u)
        require(composed == transpose(old_block),
                "consumer composition fails for arbitrary dirty port values")
        mutant = [row[:] for row in new_block]
        mutant[0][0] += Q(1, 4)
        require(matmul(transpose(mutant), u) != transpose(old_block),
                "consumer mutation control failed to detect a changed coefficient")
        for row_index, port in enumerate(ports):
            changed_cut[port] = new_block[row_index]

        old_support = sum(value != 0 for row in old_block for value in row)
        new_support = sum(value != 0 for row in new_block for value in row)
        denominators = sorted({value.denominator for row in new_block
                               for value in row if value})
        require(all(value.denominator in (1, 2, 4)
                    for row in new_block for value in row),
                "new cut coefficient is outside the selected dyadic basis")
        block_results.append({
            "tetrad": list(tetrad),
            "ports_in_U_order": ports,
            "unimodular_determinant": -1,
            "kernel_rows": 4,
            "consumer_rank": rank(new_block),
            "old_nonzero_cut_coefficients": old_support,
            "new_nonzero_cut_coefficients": new_support,
            "added_nonzero_cut_coefficients": new_support - old_support,
            "new_denominators": denominators,
        })

    require(len(changed_ports) == 24, "expected three disjoint tetrads")
    old_support = sum(value != 0 for row in original_cut for value in row)
    new_support = sum(value != 0 for row in changed_cut for value in row)
    require((old_support, new_support) == (176, 202),
            "three-block consumer incidence count changed")
    require(sum(value != 0 for row in changed_cut for value in row) ==
            len(word["cut"]) + 26,
            "literal additive cut length does not match its coefficient support")

    # Rebuild the literal modified cut from its exact matrix and check the full
    # output map. The cut only adds to centre accumulators; it preserves their
    # incoming dirty values because the same delta is added for every port vector.
    changed_instructions = []
    for port, row in enumerate(changed_cut):
        for center_index, coefficient in enumerate(row):
            if coefficient:
                changed_instructions.append([
                    "add", 112 + port, word["centers"][center_index],
                    coefficient.numerator, coefficient.denominator, None,
                ])
    require(len(changed_instructions) == 202,
            "rebuilt centre cut has the wrong instruction count")
    rebuilt = [[Q(0) for _ in word["centers"]] for _ in range(112)]
    center_index = {register: index for index, register in
                    enumerate(word["centers"])}
    for op, source, destination, numerator, denominator, _ in changed_instructions:
        require(op == "add", "rebuilt cut contains a non-add operation")
        rebuilt[source - 112][center_index[destination]] += Q(
            numerator, denominator)
    require(rebuilt == changed_cut, "rebuilt cut differs from its exact matrix")

    target_a = Q(3, 997)
    k_blocks = 3
    profile = {
        1: 192 + 4 * k_blocks,
        2: 56 - 4 * k_blocks,
        72: 73,
        56: 1,
    }
    centre = 112 - 4 * k_blocks
    unpaid = Q(1) + Q(k_blocks, 28)
    incidence_overhead = new_support - old_support
    base_profile = dict(profile)
    sensitivity_profile = dict(profile)
    sensitivity_profile[1] += incidence_overhead
    base_moment = ceiling.relax(
        base_profile, 73, 896, 9, centre, target_a, R=51, unpaid=unpaid)
    sensitivity_moment = ceiling.relax(
        sensitivity_profile, 73, 896, 9, centre, target_a, R=51,
        unpaid=unpaid)
    base_bracket = ceiling.ceiling(
        base_profile, 73, 896, 9, centre, grid=Q(1, 10**12), R=51,
        unpaid=unpaid)
    sensitivity_bracket = ceiling.ceiling(
        sensitivity_profile, 73, 896, 9, centre, grid=Q(1, 10**12), R=51,
        unpaid=unpaid)
    base_kappa = base_bracket[1] / (1 + base_bracket[1])
    sensitivity_kappa = (sensitivity_bracket[1] /
                         (1 + sensitivity_bracket[1]))
    require(sensitivity_moment[1] < 1 and sensitivity_kappa > Q(3, 1000),
            "rank-one incidence sensitivity no longer clears kappa=0.003")

    receipt = {
        "status": "PASS_P112_SELECTED_CENTER_CUT_COMPOSITION",
        "scope": "Three-block exact composition into the immediate selected centre cut; no supplier admission or selected-kappa change.",
        "selected_kappa_unchanged": selected_record["decimal"],
        "selected_archive_sha256": archive_hash,
        "tetrads_transformed": len(block_results),
        "blocks": block_results,
        "cut": {
            "old_add_instructions": len(word["cut"]),
            "new_add_instructions": len(changed_instructions),
            "old_nonzero_coefficients": old_support,
            "new_nonzero_coefficients": new_support,
            "added_nonzero_coefficients": incidence_overhead,
            "consumer_identity": "S^T = S_new^T U on each transformed block",
            "arithmetic_domain": "exact rational coefficients",
        },
        "rank72_complex_sensitivity_only": {
            "profile_before_incidence_charge": {
                str(r): n for r, n in sorted(base_profile.items())
            },
            "profile_if_each_added_incidence_costs_one_rank1_unit": {
                str(r): n for r, n in sorted(sensitivity_profile.items())
            },
            "moment_at_a_3_over_997_before": [str(x) for x in base_moment],
            "moment_at_a_3_over_997_after": [str(x) for x in sensitivity_moment],
            "complex_kappa_ceiling_before": str(base_kappa),
            "complex_kappa_ceiling_after": str(sensitivity_kappa),
            "not_a_scalar_ADD_tariff": True,
        },
        "scope_limit": "The rank-72 profile and rank-1 incidence charge are sensitivities, not suppliers or a verified scalar-cost conversion; bit-side and complete implementation invoices remain open.",
    }
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    print("PASS_P112_SELECTED_CENTER_CUT_COMPOSITION blocks=3 cut_adds=176->202 "
          "rank1_incidence_sensitivity_complex_kappa=%.12f no_new_kappa" %
          float(sensitivity_kappa))


if __name__ == "__main__":
    run()
