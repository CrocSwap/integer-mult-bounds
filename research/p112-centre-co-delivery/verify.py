#!/usr/bin/env python3
"""Verify the selected P112 centre co-delivery identity and rank profile."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None,
         "could not load " + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def gf2_rank(values) -> int:
    pivots = {}
    for value in values:
        row = int(value)
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def support(matrix) -> int:
    return sum(value != 0 for row in matrix for value in row)


def add_matrices(a, b):
    need(len(a) == len(b) and all(len(x) == len(y) for x, y in zip(a, b)),
         "matrix sum shape")
    return [[x + y for x, y in zip(row_a, row_b)]
            for row_a, row_b in zip(a, b)]


def decimal(value: Q, digits: int = 12) -> str:
    return format(float(value), ".%dg" % digits)


def center_root_labels(geometry, live, frame, root_to_port, port_labels):
    labels = []
    for frame_root in frame:
        required = [
            (geometry.dot(root, frame_root) // 4 + 1) % 2
            for root in live
        ]
        candidates = [
            label for label in range(512)
            if all(
                (port_labels[root_to_port[index]] & label).bit_count() % 2
                == required[index]
                for index in range(112)
            )
        ]
        need(len(candidates) == 1,
             "an omitted P112 frame root has no unique selected q label")
        labels.append(candidates[0])
    return labels


def native_center_binding(word, omitted_labels, native_result):
    need(native_result["status"] == "PASS_SELECTED_CENTRE_NATIVE_LIFT",
         "selected native-centre receipt is not a passing lift")
    need(native_result["centre_frames"] == word["center_frames"],
         "native-lift centre-frame binding differs from the selected word")
    need(len(word["centers"]) == len(word["center_frames"]) == 8,
         "expected eight selected centre slots and frames")

    slot_to_root = []
    rows = []
    for slot, frame_id in enumerate(word["center_frames"]):
        frame_labels = word["frames"][frame_id]
        need(len(frame_labels) == 8 and gf2_rank(frame_labels) == 8,
             "a selected native centre frame is not rank eight")
        orthogonal_labels = [
            label for label in range(1, 512)
            if all((label & vector).bit_count() % 2 == 0
                   for vector in frame_labels)
        ]
        matches = [index for index, label in enumerate(omitted_labels)
                   if label in orthogonal_labels]
        need(len(orthogonal_labels) == len(matches) == 1,
             "a native centre frame does not bind one omitted P112 label")
        root_index = matches[0]
        slot_to_root.append(root_index)
        rows.append({
            "slot": slot,
            "role": word["centers"][slot],
            "frame_id": frame_id,
            "frame_rank": 8,
            "orthogonal_q_label": orthogonal_labels[0],
            "omitted_root_index": root_index,
        })

    need(len(set(slot_to_root)) == 8,
         "native centre frames do not bind distinct omitted roots")
    return slot_to_root, rows


def output_term_rank(input_mask, port_outputs, center_outputs, slot_to_root,
                     port_pairing, center_pairing):
    pairing_rows = [port_pairing[port] & input_mask
                    for port in port_outputs]
    pairing_rows.extend(center_pairing[slot_to_root[slot]] & input_mask
                        for slot in center_outputs)
    return gf2_rank(pairing_rows)


def construct_blocks(geometry, basis, audit, gauge, word, scatter,
                     root_to_port, port_pairing, center_pairing,
                     physical_slot_to_root):
    roots, frame = geometry.roots_and_frame()
    live = sorted(set(roots) - set(frame))
    classes = defaultdict(list)
    for root_index, root in enumerate(live):
        coordinates = [geometry.dot(root, f) // 4 for f in frame]
        tetrad = tuple(j for j, value in enumerate(coordinates) if value)
        parity = sum(coordinates[j] < 0 for j in tetrad) % 2
        classes[tetrad, parity].append((root_index, coordinates))

    tetrads = sorted({tetrad for tetrad, _ in classes})
    need(len(roots) == 120 and len(frame) == 8 and len(live) == 112,
         "P112 root/frame inventory changed")
    need(len(tetrads) == 14 and len(classes) == 28
         and all(len(rows) == 4 for rows in classes.values()),
         "P112 tetrad partition changed")

    term_specs = []
    block_rows = []
    term_profile = Counter()
    baseline_profile = Counter()
    total_m_support = 0
    total_cm_support = 0
    total_j_support = 0

    for tetrad in tetrads:
        even = classes[tetrad, 0]
        odd = classes[tetrad, 1]
        e0 = [[value[j] for j in tetrad] for _, value in even]
        e1 = [[value[j] for j in tetrad] for _, value in odd]
        e = e0 + e1
        root_indices = [index for index, _ in even + odd]
        ports = [root_to_port[index] for index in root_indices]
        k = basis.matmul(e, basis.transpose(e))
        cross = basis.matmul(e0, basis.transpose(e1))
        transition = basis.matmul(cross, basis.D_EVEN_SUM)
        need(all(value % 4 == 0
                 for row in transition for value in row),
             "kernel transition is no longer integral")
        top = [[-(value // 4) for value in row] for row in transition]
        kernel_rows = basis.transpose(top + basis.D_EVEN_SUM)
        complement = [
            [int(i == j) for j in range(8)] for i in (0, 5, 6, 7)
        ]
        u = kernel_rows + complement
        need(basis.determinant(u) == -1,
             "the tetrad transform is no longer unimodular")
        uk = basis.matmul(u, k)
        need(uk[:4] == [[0] * 8 for _ in range(4)],
             "the first four transformed rows left the update kernel")

        old = [scatter[port][:] for port in ports]
        changed = audit.matmul(audit.transpose(gauge.inverse(u)), old)
        hybrid = [old[i][:] if i < 4 else changed[i][:]
                  for i in range(8)]
        correction = [
            ([Q(0)] * 8 if i < 4 else
             [old[i][j] - changed[i][j] for j in range(8)])
            for i in range(8)
        ]
        need([[hybrid[i][j] + correction[i][j]
               for j in range(8)] for i in range(8)] == old,
             "hybrid dirty-baseline split changed")
        need(audit.matmul(audit.transpose(hybrid), uk)
             == audit.matmul(audit.transpose(old), k),
             "hybrid product identity changed")

        m = basis.matmul(u, e)
        cm = audit.matmul(audit.transpose(correction), m)
        j = audit.matmul(audit.transpose(correction), uk)
        need(basis.matmul(m, basis.transpose(e)) == uk,
             "co-delivered port factorization failed")
        need(audit.matmul(cm, basis.transpose(e)) == j,
             "co-delivered centre factorization failed")
        need(audit.matmul(audit.transpose(old), uk)
             == add_matrices(audit.matmul(audit.transpose(old), k), j),
             "source-side correction does not recover the original reader")

        local_terms = []
        for term_index in range(4):
            input_ports = [ports[i] for i in range(8) if e[i][term_index]]
            input_mask = sum(1 << port for port in input_ports)
            port_outputs = [ports[i] for i in range(8)
                            if m[i][term_index]]
            center_outputs = [slot for slot in range(8)
                              if cm[slot][term_index]]
            local_terms.append((input_mask, port_outputs, center_outputs))
            port_only_rank = output_term_rank(
                input_mask, port_outputs, [], physical_slot_to_root,
                port_pairing, center_pairing)
            term_rank = output_term_rank(
                input_mask, port_outputs, center_outputs,
                physical_slot_to_root, port_pairing, center_pairing)
            baseline_profile[port_only_rank] += 1
            term_profile[term_rank] += 1
            term_specs.append((input_mask, port_outputs, center_outputs))

        m_support = support(m)
        cm_support = support(cm)
        j_support = support(j)
        total_m_support += m_support
        total_cm_support += cm_support
        total_j_support += j_support
        block_rows.append({
            "tetrad": list(tetrad),
            "terms": 4,
            "M_port_coefficients": m_support,
            "C_transpose_M_centre_coefficients": cm_support,
            "J_source_correction_coefficients": j_support,
            "term_ranks": [
                output_term_rank(mask, ports_out, centers_out,
                                 physical_slot_to_root, port_pairing,
                                 center_pairing)
                for mask, ports_out, centers_out in local_terms
            ],
        })

    need(term_profile == Counter({1: 56}),
         "the native-bound co-delivery profile is not 56 rank-one terms")
    need(baseline_profile == Counter({1: 56}),
         "the fused port-only control profile changed")
    need((total_m_support, total_cm_support, total_j_support) == (224, 92, 288),
         "the fourteen-block coefficient-support census changed")
    need(sum(row["C_transpose_M_centre_coefficients"]
             for row in block_rows[:3]) == 19
         and sum(row["J_source_correction_coefficients"]
                 for row in block_rows[:3]) == 64,
         "the first-three-block support control changed")

    return term_specs, block_rows, term_profile, baseline_profile, {
        "M_port_coefficients": total_m_support,
        "C_transpose_M_centre_coefficients": total_cm_support,
        "J_source_correction_coefficients": total_j_support,
    }


def assignment_profile(term_specs, assignment, port_pairing,
                       center_pairing):
    profile = Counter()
    for input_mask, port_outputs, center_outputs in term_specs:
        rank = output_term_rank(
            input_mask, port_outputs, center_outputs, assignment,
            port_pairing, center_pairing)
        profile[rank] += 1
    return profile


def assignment_census(term_specs, physical_slot_to_root, port_pairing,
                      center_pairing):
    frame_order_profile = assignment_profile(
        term_specs, tuple(range(8)), port_pairing, center_pairing)
    best_mass = None
    minimizers = []
    best_profile = None
    for assignment in itertools.permutations(range(8)):
        profile = assignment_profile(
            term_specs, assignment, port_pairing, center_pairing)
        mass = sum(rank * count for rank, count in profile.items())
        if best_mass is None or mass < best_mass:
            best_mass = mass
            minimizers = [assignment]
            best_profile = profile
        elif mass == best_mass:
            minimizers.append(assignment)

    need(frame_order_profile == Counter({1: 24, 2: 32}),
         "frame-order mapping control changed")
    need(best_mass == 56 and len(minimizers) == 1,
         "the eight-slot exhaustive minimum is not unique at mass 56")
    need(tuple(physical_slot_to_root) == minimizers[0],
         "the selected native centre binding is not the unique minimum")
    need(best_profile == Counter({1: 56}),
         "the exhaustive minimum profile changed")
    return {
        "assignments_checked": 40320,
        "frame_order_profile": {
            str(rank): count for rank, count in sorted(frame_order_profile.items())
        },
        "frame_order_rank_mass": sum(
            rank * count for rank, count in frame_order_profile.items()),
        "minimum_rank_mass": best_mass,
        "minimizer_count": len(minimizers),
        "unique_minimizer_slot_to_frame_root": list(minimizers[0]),
        "minimum_profile": {
            str(rank): count for rank, count in sorted(best_profile.items())
        },
    }


def complement_shear_census(geometry, basis, audit, gauge, word, scatter,
                            selected, live, frame, port_pairing,
                            center_pairing, slot_to_root):
    roots, _ = geometry.roots_and_frame()
    classes = defaultdict(list)
    for root_index, root in enumerate(live):
        coordinates = [geometry.dot(root, f) // 4 for f in frame]
        tetrad = tuple(j for j, value in enumerate(coordinates) if value)
        parity = sum(coordinates[j] < 0 for j in tetrad) % 2
        classes[tetrad, parity].append((root_index, coordinates))

    tetrads = sorted({tetrad for tetrad, _ in classes})
    need(len(roots) == 120 and len(tetrads) == 14,
         "complement/shear census P112 partition changed")
    identity8 = [[int(i == j) for j in range(8)] for i in range(8)]
    identity4 = [[int(i == j) for j in range(4)] for i in range(4)]
    block_rows = []
    total_complements = 0
    total_shears = 0
    total_rank1_shears = 0

    for block_index, tetrad in enumerate(tetrads):
        even = classes[tetrad, 0]
        odd = classes[tetrad, 1]
        e0 = [[value[j] for j in tetrad] for _, value in even]
        e1 = [[value[j] for j in tetrad] for _, value in odd]
        e = e0 + e1
        ports = [selected.ROOT_TO_PORT[index]
                 for index, _ in even + odd]
        cross = basis.matmul(e0, basis.transpose(e1))
        transition = basis.matmul(cross, basis.D_EVEN_SUM)
        need(all(value % 4 == 0
                 for row in transition for value in row),
             "shear census kernel transition is not integral")
        top = [[-(value // 4) for value in row] for row in transition]
        kernel_rows = basis.transpose(top + basis.D_EVEN_SUM)
        old = [scatter[port][:] for port in ports]
        k = basis.matmul(e, basis.transpose(e))

        complement_rows = []
        for subset in itertools.combinations(range(8), 4):
            u = kernel_rows + [identity8[index] for index in subset]
            determinant = basis.determinant(u)
            if abs(determinant) != 1:
                continue
            uk = basis.matmul(u, k)
            need(uk[:4] == [[0] * 8 for _ in range(4)],
                 "a sheared completion lost its kernel rows")
            changed = audit.matmul(audit.transpose(gauge.inverse(u)), old)
            correction = [
                ([0] * 8 if row < 4 else
                 [old[row][column] - changed[row][column]
                  for column in range(8)])
                for row in range(8)
            ]
            m = basis.matmul(u, e)
            cm = audit.matmul(audit.transpose(correction), m)
            need(basis.matmul(m, basis.transpose(e)) == uk,
                 "un-sheared term factorization failed")
            complement_rows.append((subset, uk, m, cm, support(cm)))

        need(len(complement_rows) == 56,
             "expected 56 unimodular standard-row complements")
        total_complements += len(complement_rows)
        complement_min = min(row[4] for row in complement_rows)
        best = None
        rank1_count = 0
        strict_improvements = 0
        tested = 0

        for subset, uk, m, cm, _ in complement_rows:
            for i in range(4):
                for j in range(4):
                    if i == j:
                        continue
                    for sign in (-1, 1):
                        # A = I + sign E_ij; A^{-T} = I - sign E_ji.
                        a = [row[:] for row in identity4]
                        a_inverse_transpose = [row[:] for row in identity4]
                        a[i][j] += sign
                        a_inverse_transpose[j][i] -= sign
                        e_sheared = basis.matmul(e, a)
                        m_sheared = basis.matmul(m, a_inverse_transpose)
                        cm_sheared = basis.matmul(cm, a_inverse_transpose)
                        tested += 1
                        total_shears += 1
                        need(basis.matmul(m_sheared,
                                          basis.transpose(e_sheared)) == uk,
                             "elementary shear changed the product update")

                        ranks = []
                        for term_index in range(4):
                            input_mask = sum(
                                1 << ports[row]
                                for row in range(8)
                                if e_sheared[row][term_index]
                            )
                            port_outputs = [
                                ports[row] for row in range(8)
                                if m_sheared[row][term_index]
                            ]
                            center_outputs = [
                                row for row in range(8)
                                if cm_sheared[row][term_index]
                            ]
                            ranks.append(output_term_rank(
                                input_mask, port_outputs, center_outputs,
                                slot_to_root, port_pairing, center_pairing))
                        if ranks != [1, 1, 1, 1]:
                            continue

                        rank1_count += 1
                        total_rank1_shears += 1
                        center_support = support(cm_sheared)
                        if center_support < complement_min:
                            strict_improvements += 1
                        candidate = (
                            center_support, subset, i, j, sign,
                            support(e_sheared), support(m_sheared))
                        if best is None or candidate < best:
                            best = candidate

        need(tested == 1344 and rank1_count == 1344 and best is not None,
             "the bounded elementary-shear census changed")
        block_rows.append({
            "block": block_index,
            "tetrad": list(tetrad),
            "unimodular_complements": len(complement_rows),
            "shears_tested": tested,
            "rank_one_shears": rank1_count,
            "complement_min_C_transpose_M_support": complement_min,
            "best_sheared_C_transpose_M_support": best[0],
            "best_complement": list(best[1]),
            "best_shear": {
                "row": best[2], "column": best[3], "sign": best[4]
            },
            "best_input_support": best[5],
            "best_port_output_support": best[6],
            "shears_below_complement_min": strict_improvements,
        })

    support_vector = [row["best_sheared_C_transpose_M_support"]
                      for row in block_rows]
    need(support_vector == [2, 7, 7, 2, 7, 6, 6, 7, 7, 7, 2, 7, 7, 2],
         "fourteen-block elementary-shear minimum changed")
    total_center_support = sum(support_vector)
    rank_mass = 56
    support_priced_cost = rank_mass + total_center_support
    need((total_complements, total_shears, total_rank1_shears,
          total_center_support, support_priced_cost) ==
         (784, 18816, 18816, 76, 132),
         "aggregate complement/shear sensitivity changed")
    return {
        "complements_tested": total_complements,
        "shears_tested": total_shears,
        "rank_one_shears": total_rank1_shears,
        "block_supports": block_rows,
        "minimum_C_transpose_M_support_total": total_center_support,
        "rank_mass": rank_mass,
        "one_unit_per_coefficient_local_cost": support_priced_cost,
        "original_P112_copy_mass_control": 112,
        "beats_original_control": support_priced_cost < 112,
        "scope": "standard-coordinate unimodular complements and elementary integer input shears I +/- E_ij only; no scalar schedule or supplier admitted",
    }


def conditional_budget(ceiling, sheared_center_support):
    baseline_profile = {1: 192, 2: 56, 32: 166}
    candidate_profile = {1: 248, 32: 166}
    args = (73, 896, 9, 112)
    options = {"R": 51, "unpaid": 2}
    target_a = Q(1, 99)
    baseline_model = ceiling.model(baseline_profile, *args, **options)
    candidate_model = ceiling.model(candidate_profile, *args, **options)
    baseline_root = ceiling.ceiling(
        baseline_profile, *args, grid=Q(1, 10**12), **options)
    candidate_root = ceiling.ceiling(
        candidate_profile, *args, grid=Q(1, 10**12), **options)
    charged_profile = {
        1: 192 + 56 + sheared_center_support,
        32: 166,
    }
    charged_model = ceiling.model(charged_profile, *args, **options)
    charged_root = ceiling.ceiling(
        charged_profile, *args, grid=Q(1, 10**12), **options)
    charged_kappa = charged_root[1] / (1 + charged_root[1])
    charged_target = ceiling.relax(
        charged_profile, *args, target_a, **options)
    charged_one_unpaid = ceiling.relax(
        charged_profile, *args, target_a, R=51, unpaid=1)
    candidate_target = ceiling.relax(
        candidate_profile, *args, target_a, **options)
    one_unpaid_target = ceiling.relax(
        candidate_profile, *args, target_a, R=51, unpaid=1)
    need(candidate_target[1] < 1,
         "the two-unpaid target moment no longer passes")
    need(one_unpaid_target[0] > 1,
         "the one-unpaid failure control no longer fails")
    need(candidate_model["local_mass"] == 5560
         and baseline_model["local_mass"] == 5616,
         "conditional complex local mass changed")
    need(sheared_center_support == 76
         and charged_model["local_mass"] == 5636
         and decimal(charged_kappa) == "0.0134440084459"
         and charged_target[1] < 1 and charged_one_unpaid[0] > 1,
         "support-priced shear sensitivity changed")

    baseline_kappa = baseline_root[1] / (1 + baseline_root[1])
    candidate_kappa = candidate_root[1] / (1 + candidate_root[1])
    need(decimal(baseline_kappa) == "0.0137876681081"
         and decimal(candidate_kappa) == "0.0141093063394",
         "conditional complex ceiling changed")
    return {
        "assumptions": {
            "width": 73,
            "families": 896,
            "stages": 9,
            "centre_charge": 112,
            "idle_rank_cap": 51,
            "unpaid_coordinates": 2,
            "target_a": "1/99",
        },
        "baseline_profile": {str(k): v for k, v in baseline_profile.items()},
        "candidate_profile": {str(k): v for k, v in candidate_profile.items()},
        "baseline_local_mass": str(baseline_model["local_mass"]),
        "candidate_local_mass": str(candidate_model["local_mass"]),
        "baseline_a_ceiling_hi": str(baseline_root[1]),
        "candidate_a_ceiling_hi": str(candidate_root[1]),
        "baseline_complex_kappa_cap_hi": decimal(baseline_kappa),
        "candidate_complex_kappa_cap_hi": decimal(candidate_kappa),
        "shear_sensitivity_profile": {
            str(k): v for k, v in charged_profile.items()
        },
        "shear_sensitivity_local_mass": str(charged_model["local_mass"]),
        "shear_sensitivity_complex_kappa_cap_hi": decimal(charged_kappa),
        "shear_sensitivity_two_unpaid_target_moment": [
            str(charged_target[0]), str(charged_target[1])
        ],
        "shear_sensitivity_one_unpaid_control": [
            str(charged_one_unpaid[0]), str(charged_one_unpaid[1])
        ],
        "candidate_two_unpaid_target_moment": [
            str(candidate_target[0]), str(candidate_target[1])
        ],
        "candidate_one_unpaid_target_moment_control": [
            str(one_unpaid_target[0]), str(one_unpaid_target[1])
        ],
        "selected_kappa_unchanged": "0.001672660197076918",
        "scope": "complex-side ideal ceiling only; no supplier, full invoice, joint cap, or selected-kappa update",
    }


def calculate():
    selected = load_module(
        "codelivery_selected_p112",
        ROOT / "research/selected-p112-tetrad-rank32-route/verify.py")
    audit = load_module(
        "codelivery_p112_cut",
        ROOT / "research/p112-tetrad-cut-consumer/verify.py")
    basis = load_module(
        "codelivery_p112_basis",
        ROOT / "research/p112-tetrad-dual-anchor-screen/verify.py")
    gauge = load_module(
        "codelivery_gauge44",
        ROOT / "research/gauge44-port-syndrome-encoding/verify.py")
    geometry = load_module(
        "codelivery_p112_geometry",
        ROOT / "research/p112-tetrad-local-decoder/verify.py")
    ceiling = load_module(
        "codelivery_complex_ceiling",
        ROOT / "research/complex-local-word-ceiling/ceiling.py")

    selected_word, word_payload_sha = selected.load_word()
    selected_decoder = selected.build_bound_decoder(selected_word)
    word, scatter, archive_sha = audit.read_selected_scatter(gauge)
    need(word == selected_word, "the selected word readers disagree")
    need(selected_decoder["decoder_copy_profile"] == {"2": 56}
         and selected_decoder["decoder_copy_mass"] == 112,
         "the source-bound P112 control profile changed")

    native_result = read_json(
        ROOT / "research/selected-centre-native-lift/RESULT.json")
    roots, frame = geometry.roots_and_frame()
    live = sorted(set(roots) - set(frame))
    omitted_labels = center_root_labels(
        geometry, live, frame, selected.ROOT_TO_PORT, word["ports"])
    need(len(set(omitted_labels)) == 8
         and not set(omitted_labels) & set(word["ports"]),
         "omitted-root labels are not distinct from the selected ports")
    slot_to_root, frame_rows = native_center_binding(
        word, omitted_labels, native_result)

    port_pairing = [
        sum(1 << j for j, q_j in enumerate(word["ports"])
            if (q_i & q_j).bit_count() % 2)
        for q_i in word["ports"]
    ]
    center_pairing = [
        sum(1 << j for j, q_j in enumerate(word["ports"])
            if (q_i & q_j).bit_count() % 2)
        for q_i in omitted_labels
    ]
    term_specs, block_rows, profile, port_only_profile, supports = construct_blocks(
        geometry, basis, audit, gauge, word, scatter,
        selected.ROOT_TO_PORT, port_pairing, center_pairing, slot_to_root)
    census = assignment_census(
        term_specs, slot_to_root, port_pairing, center_pairing)
    basis_sensitivity = complement_shear_census(
        geometry, basis, audit, gauge, word, scatter, selected, live, frame,
        port_pairing, center_pairing, slot_to_root)
    budget = conditional_budget(
        ceiling, basis_sensitivity["minimum_C_transpose_M_support_total"])

    return {
        "status": "PASS_P112_CENTRE_CO_DELIVERY",
        "source": {
            "selected_archive_sha256": archive_sha,
            "canonical_word_payload_sha256": word_payload_sha,
            "selected_port_map_sha256": selected_decoder["map_sha256"],
        },
        "centre_label_binding": {
            "omitted_p112_root_q_labels_in_frame_order": omitted_labels,
            "native_center_frames": frame_rows,
            "slot_to_omitted_root": slot_to_root,
        },
        "co_delivery": {
            "blocks": len(block_rows),
            "terms": sum(profile.values()),
            "profile": {str(k): v for k, v in sorted(profile.items())},
            "rank_mass": sum(k * v for k, v in profile.items()),
            "port_only_profile": {
                str(k): v for k, v in sorted(port_only_profile.items())
            },
            "coefficient_supports": supports,
            "block_supports": block_rows,
            "identities": [
                "M E^T = U K",
                "(C^T M) E^T = C^T U K = J",
                "S^T(d + U K x) - J x = S^T(d + K x)",
            ],
        },
        "slot_assignment_census": census,
        "complement_shear_sensitivity": basis_sensitivity,
        "conditional_budget": budget,
        "selected_kappa_changed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true",
                        help="write the recomputed RESULT.json")
    args = parser.parse_args()
    result = calculate()
    path = PACKAGE / "RESULT.json"
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        path.write_text(encoded, encoding="utf-8")
    else:
        need(path.exists(), "RESULT.json is absent; run verify.py --write")
        need(json.loads(path.read_text(encoding="utf-8")) == result,
             "recomputed RESULT.json differs")
    budget = result["conditional_budget"]
    print(
        "PASS_P112_CENTRE_CO_DELIVERY blocks=14 terms=56 profile=56xrank1 "
        "rank_mass=56 native_slot_map=[7,5,4,6,3,1,0,2] "
        "best_center_support=" + str(
            result["complement_shear_sensitivity"][
                "minimum_C_transpose_M_support_total"]) +
        " support_priced_cost=" + str(
            result["complement_shear_sensitivity"][
                "one_unit_per_coefficient_local_cost"]) +
        " ideal_complex_kappa=" + budget[
            "shear_sensitivity_complex_kappa_cap_hi"] +
        " selected_unchanged"
    )


if __name__ == "__main__":
    main()
