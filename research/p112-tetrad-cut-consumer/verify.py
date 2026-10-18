#!/usr/bin/env python3
"""Bind three P112 tetrad basis changes to the selected gauge44 centre cut."""
from __future__ import annotations

from collections import Counter, defaultdict
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


def read_selected_forward_program(gauge):
    provider = "candidate/strict/global/base/providers/gauge44/"
    with tarfile.open(gauge.ARCHIVE, "r:gz") as archive:
        program_bytes = archive.extractfile(
            provider + "LOCAL-PROGRAMS.json.gz").read()
        replay_bytes = archive.extractfile(
            provider + "INDEPENDENT-LOCAL-REPLAY.json").read()
    replay = json.loads(replay_bytes)
    require(replay["status"]
            == "PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY"
            and hashlib.sha256(program_bytes).hexdigest()
            == replay["local_programs_sha256"],
            "selected local-program binding changed")
    programs = json.loads(gzip.decompress(program_bytes))
    require(set(programs) == {"forward", "backward"},
            "selected local-program directions changed")
    return programs["forward"]


def matrix_rank_determinant(matrix):
    rows = [[Q(value) for value in row] for row in matrix]
    size = len(rows)
    require(size and all(len(row) == size for row in rows),
            "dirty response matrix is not square")
    determinant = Q(1)
    pivot_row = 0
    for column in range(size):
        pivot = next((i for i in range(pivot_row, size)
                      if rows[i][column]), None)
        if pivot is None:
            continue
        if pivot != pivot_row:
            rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
            determinant = -determinant
        scale = rows[pivot_row][column]
        determinant *= scale
        for i in range(pivot_row + 1, size):
            if rows[i][column]:
                factor = rows[i][column] / scale
                rows[i] = [rows[i][j] - factor * rows[pivot_row][j]
                           for j in range(size)]
        pivot_row += 1
        if pivot_row == size:
            break
    return pivot_row, determinant if pivot_row == size else Q(0)


def audit_selected_cut_chronology(word, forward_program):
    """Bind the cut's position and the word-level dirty response before B."""
    phases = {event[1]: index for index, event in enumerate(forward_program)
              if event[0] == "phase"}
    required_phases = (
        "zero_frame_precondition", "entry_adapters", "A", "centers", "B",
        "cleanup_tail", "full_frame_cleanup",
    )
    require(all(name in phases for name in required_phases),
            "selected forward phase inventory changed")
    require([phases[name] for name in required_phases]
            == sorted(phases[name] for name in required_phases),
            "selected forward phase order changed")

    cut_positions = []
    native_cut = []
    for index, event in enumerate(forward_program):
        if event[0] != "scalar":
            continue
        gate = event[1]
        if (gate[0] == "add" and gate[1][0] == "L"
                and word["v"] <= gate[1][1] < 2 * word["v"]
                and gate[2][0] == "C"):
            require(event[2] == 0, "selected centre cut frame changed")
            cut_positions.append(index)
            native_cut.append((gate[1][1], gate[2][1],
                               Q(gate[3], gate[4])))
    require(len(cut_positions) == len(word["cut"]) == 176,
            "selected native cut instruction count changed")
    center_index = {role: index for index, role in enumerate(word["centers"])}
    canonical_cut = Counter(
        (gate[1], center_index[gate[2]], Q(gate[3], gate[4]))
        for gate in word["cut"]
    )
    require(Counter(native_cut) == canonical_cut,
            "native cut coefficients differ from canonical cut")
    require(phases["A"] < cut_positions[0] <= cut_positions[-1]
            < phases["B"], "selected centre cut no longer lies between A and B")

    v, n = word["v"], 2 * word["v"] + word["R"]
    rows = [{index: Q(1)} for index in range(n)]
    for stage in ("precondition", "compensation", "A"):
        for gate in word[stage]:
            if gate[0] == "add":
                _, source, destination, numerator, denominator, *_ = gate
                require(source != destination, "self-add in dirty prefix")
                coefficient = Q(numerator, denominator)
                for column, value in list(rows[source].items()):
                    result = rows[destination].get(column, Q(0)) + coefficient * value
                    if result:
                        rows[destination][column] = result
                    else:
                        rows[destination].pop(column, None)
            else:
                require(gate[0] == "scale", "non-scalar dirty-prefix operation")
                _, destination, numerator, denominator, *_ = gate
                coefficient = Q(numerator, denominator)
                rows[destination] = {
                    column: coefficient * value
                    for column, value in rows[destination].items()
                }

    dirty_rows = rows[v:2 * v]
    outside_support = sum(
        column not in range(v, 2 * v)
        for row in dirty_rows for column, value in row.items() if value
    )
    dirty_map = [[row.get(v + column, Q(0)) for column in range(v)]
                 for row in dirty_rows]
    dirty_support = sum(value != 0 for row in dirty_map for value in row)
    row_degrees = {}
    for row in dirty_map:
        degree = sum(value != 0 for value in row)
        row_degrees[str(degree)] = row_degrees.get(str(degree), 0) + 1
    dirty_rank, dirty_determinant = matrix_rank_determinant(dirty_map)
    require(outside_support == 0 and dirty_rank == 112
            and dirty_support == 272
            and row_degrees == {"2": 88, "4": 24}
            and dirty_determinant == Q(1, 2 ** 56),
            "word-level pre-cut dirty response changed")

    centers = set(word["centers"])
    b_port_writes = [
        gate for gate in word["B"]
        if gate[0] == "add" and v <= gate[2] < 2 * v
    ]
    b_center_touches = [
        gate for gate in word["B"]
        if (set(gate[1:3]) & centers if gate[0] == "add"
            else gate[1] in centers)
    ]
    require(len(b_port_writes) == 136
            and {gate[2] for gate in b_port_writes} == set(range(v, 2 * v))
            and not b_center_touches,
            "selected B output/centre interaction changed")
    return {
        "forward_phase_indices": {name: phases[name]
                                  for name in required_phases},
        "native_cut_adds": len(cut_positions),
        "native_cut_event_positions": [cut_positions[0], cut_positions[-1]],
        "cut_precedes_B": True,
        "word_scalar_prefix": "precondition + compensation + A; native adapters are not expanded by this matrix projection",
        "word_scalar_pre_cut_dirty_response": {
            "source_columns": "initial L[112:224] only",
            "other_initial_columns_used": outside_support,
            "nonzero_coefficients": dirty_support,
            "row_degree_histogram": row_degrees,
            "rank": dirty_rank,
            "determinant": str(dirty_determinant),
        },
        "B_port_destination_adds": len(b_port_writes),
        "B_distinct_port_destinations": len({gate[2] for gate in b_port_writes}),
        "B_center_touches": len(b_center_touches),
        "adapter_expansion_and_changed_schedule_semantics": "not established",
    }


def retime_readout_through_b(readout, word):
    """Move an exact centre readout from before B to the canonical post-B state.

    If B maps x to M_B x, a pre-B functional a^T x is the post-B
    functional (M_B^-T a)^T x. Check that identity against the complete
    sparse matrix of the pinned B word, over every ordinary role.
    """
    v = word["v"]
    n = 2 * v + word["R"]
    centres = word["centers"]
    require(len(readout) == v and all(len(row) == len(centres)
                                      for row in readout),
            "retimed readout shape changed")

    # Build the exact state matrix x_post = M_B x_pre from the canonical word.
    b_rows = [{role: Q(1)} for role in range(n)]
    for gate in word["B"]:
        if gate[0] == "add":
            _, source, destination, numerator, denominator, *_ = gate
            coefficient = Q(numerator, denominator)
            require(source != destination, "B contains a self-add")
            for column, value in list(b_rows[source].items()):
                result = b_rows[destination].get(column, Q(0)) \
                    + coefficient * value
                if result:
                    b_rows[destination][column] = result
                else:
                    b_rows[destination].pop(column, None)
        else:
            require(gate[0] == "scale", "unexpected operation in canonical B")
            _, destination, numerator, denominator, *_ = gate
            coefficient = Q(numerator, denominator)
            require(coefficient != 0, "B contains a singular scale")
            b_rows[destination] = {
                column: coefficient * value
                for column, value in b_rows[destination].items()
                if coefficient * value
            }

    post = [[Q(0) for _ in centres] for _ in range(n)]
    for centre in range(len(centres)):
        functional = [Q(0)] * n
        for port in range(v):
            functional[v + port] = readout[port][centre]

        # Apply each elementary inverse-transpose in the same order as B.
        for gate in word["B"]:
            if gate[0] == "add":
                _, source, destination, numerator, denominator, *_ = gate
                functional[source] -= Q(numerator, denominator) \
                    * functional[destination]
            else:
                _, destination, numerator, denominator, *_ = gate
                functional[destination] /= Q(numerator, denominator)

        recovered = [Q(0)] * n
        for role, row in enumerate(b_rows):
            if functional[role]:
                for column, value in row.items():
                    recovered[column] += functional[role] * value
        expected = [Q(0)] * n
        for port in range(v):
            expected[v + port] = readout[port][centre]
        require(recovered == expected,
                "post-B inverse-transpose readout identity failed")
        for role, value in enumerate(functional):
            post[role][centre] = value

    support = sum(value != 0 for row in post for value in row)
    source_support = sum(value != 0 for row in post[:v] for value in row)
    output_support = sum(value != 0 for row in post[v:2 * v] for value in row)
    helper_support = sum(value != 0 for row in post[2 * v:] for value in row)
    return post, {
        "nonzero_coefficients": support,
        "input_source_coefficients": source_support,
        "output_port_coefficients": output_support,
        "helper_coefficients": helper_support,
        "per_centre_support": [
            sum(post[role][centre] != 0 for role in range(n))
            for centre in range(len(centres))
        ],
    }


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
    forward_program = read_selected_forward_program(gauge)
    chronology = audit_selected_cut_chronology(word, forward_program)

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
    hybrid_cut = [row[:] for row in scatter]
    hybrid_dirty_correction = [[Q(0) for _ in word["centers"]]
                               for _ in range(112)]
    block_results = []
    first_three_cut = None
    hybrid_prefixes = {}
    prefix_support_deltas = []
    dirty_correction_deltas = []
    hybrid_support_deltas = []
    hybrid_correction_deltas = []
    first_dirty_counterexample = None
    product_map_mismatch_support = 0
    changed_ports = set()
    for block_index, tetrad in enumerate(tetrads, start=1):
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
        prefix_support_deltas.append(new_support - old_support)
        dirty_correction = [[old_block[i][j] - new_block[i][j]
                             for j in range(8)] for i in range(8)]
        correction_support = sum(value != 0 for row in dirty_correction
                                 for value in row)
        dirty_correction_deltas.append(correction_support)
        new_transpose = transpose(new_block)
        correction_transpose = transpose(dirty_correction)
        require(all(new_transpose[i][j] + correction_transpose[i][j]
                    == transpose(old_block)[i][j]
                    for i in range(8) for j in range(8)),
                "separate dirty-baseline correction identity failed")
        old_product_map = matmul(transpose(old_block), k)
        hybrid_block = old_block[:4] + new_block[4:]
        hybrid_dirty_correction_block = (
            [[Q(0)] * 8 for _ in range(4)] + dirty_correction[4:])
        hybrid_support = sum(value != 0 for row in hybrid_block for value in row)
        hybrid_correction_support = sum(
            value != 0 for row in hybrid_dirty_correction_block for value in row)
        require(all(hybrid_block[i][j] + hybrid_dirty_correction_block[i][j]
                    == old_block[i][j]
                    for i in range(8) for j in range(8)),
                "hybrid cut failed to preserve the dirty contribution")
        hybrid_product_map = matmul(transpose(hybrid_block), matmul(u, k))
        require(hybrid_product_map == old_product_map,
                "hybrid cut failed to preserve the fused product update")
        hybrid_support_deltas.append(hybrid_support - old_support)
        hybrid_correction_deltas.append(hybrid_correction_support)
        for row_index, port in enumerate(ports):
            hybrid_cut[port] = hybrid_block[row_index]
            hybrid_dirty_correction[port] = hybrid_dirty_correction_block[row_index]
        if block_index in (3, 5, 9, 14):
            hybrid_prefixes[block_index] = (
                [row[:] for row in hybrid_cut],
                [row[:] for row in hybrid_dirty_correction],
            )
        fused_product_map = matmul(transpose(old_block), matmul(u, k))
        product_mismatch = sum(
            old_product_map[i][j] != fused_product_map[i][j]
            for i in range(8) for j in range(8))
        product_map_mismatch_support += product_mismatch

        if block_index == 1:
            old_dirty = old_block[0]
            fused_cut_dirty = new_block[0]
            corrected_dirty = [fused_cut_dirty[j] + dirty_correction[0][j]
                               for j in range(8)]
            require(old_dirty == [Q(0)] * 8 and
                    fused_cut_dirty == [Q(0), Q(0), Q(0), Q(0),
                                        Q(0), Q(0), Q(1, 4), -Q(1, 4)] and
                    corrected_dirty == old_dirty,
                    "dirty-only counterexample/correction changed")
            first_dirty_counterexample = {
                "tetrad": list(tetrad),
                "dirty_vector_in_U_order": [1, 0, 0, 0, 0, 0, 0, 0],
                "old_cut_delta": [str(value) for value in old_dirty],
                "new_cut_on_untransformed_dirty": [str(value)
                                                   for value in fused_cut_dirty],
                "new_cut_plus_separate_dirty_correction": [
                    str(value) for value in corrected_dirty],
                "old_cut_on_coefficient_fused_update_mismatch_entries":
                    product_mismatch,
            }
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
            "separate_dirty_correction_coefficients": correction_support,
            "hybrid_cut_coefficients": hybrid_support,
            "hybrid_dirty_correction_coefficients": hybrid_correction_support,
            "old_cut_on_coefficient_fused_update_mismatch_entries": product_mismatch,
            "new_denominators": denominators,
        })
        if block_index == 3:
            first_three_cut = [row[:] for row in changed_cut]

    require(len(changed_ports) == 112 and first_three_cut is not None,
            "expected all fourteen disjoint tetrads")
    old_support = sum(value != 0 for row in original_cut for value in row)
    new_support = sum(value != 0 for row in changed_cut for value in row)
    first_three_support = sum(value != 0 for row in first_three_cut for value in row)
    require((old_support, first_three_support, new_support) == (176, 202, 286),
            "selected consumer incidence counts changed")
    require(sum(prefix_support_deltas[:3]) == 26 and
            sum(prefix_support_deltas) == 110,
            "consumer incidence deltas changed")
    require(dirty_correction_deltas == [16, 20, 23, 16, 21, 26, 15,
                                        28, 20, 21, 16, 20, 23, 16]
            and sum(dirty_correction_deltas) == 281,
            "dirty-baseline correction support changed")
    require(first_dirty_counterexample is not None and
            product_map_mismatch_support == 288,
            "dirty-output basis mismatch control changed")
    hybrid_support = sum(value != 0 for row in hybrid_cut for value in row)
    hybrid_correction_support = sum(
        value != 0 for row in hybrid_dirty_correction for value in row)
    hybrid_added_incidences = (
        hybrid_support - old_support + hybrid_correction_support)
    require((hybrid_support, hybrid_correction_support,
             hybrid_added_incidences) == (225, 152, 201)
            and [sum(hybrid_support_deltas[:k])
                 + sum(hybrid_correction_deltas[:k])
                 for k in (3, 5, 9, 14)] == [43, 76, 125, 201],
            "hybrid cut/correction supports changed")
    require(all(hybrid_cut[port][center]
                + hybrid_dirty_correction[port][center]
                == original_cut[port][center]
                for port in range(112) for center in range(8)),
            "global hybrid dirty correction identity failed")

    target_a = Q(3, 997)
    retimed_original, retimed_original_summary = retime_readout_through_b(
        original_cut, word)
    require(retimed_original_summary == {
        "nonzero_coefficients": 448,
        "input_source_coefficients": 0,
        "output_port_coefficients": 448,
        "helper_coefficients": 0,
        "per_centre_support": [56] * 8,
    }, "post-B original readout support changed")
    retimed_hybrid_prefixes = []
    for k_blocks in (3, 5, 9, 14):
        prefix_cut, prefix_correction = hybrid_prefixes[k_blocks]
        post_cut, post_cut_summary = retime_readout_through_b(
            prefix_cut, word)
        post_correction, post_correction_summary = retime_readout_through_b(
            prefix_correction, word)
        require(all(post_cut[role][centre]
                    + post_correction[role][centre]
                    == retimed_original[role][centre]
                    for role in range(len(retimed_original))
                    for centre in range(len(word["centers"]))),
                "post-B hybrid dirty identity failed")
        require(post_cut_summary["input_source_coefficients"] == 0
                and post_cut_summary["helper_coefficients"] == 0
                and post_correction_summary["input_source_coefficients"] == 0
                and post_correction_summary["helper_coefficients"] == 0,
                "post-B readout acquired a non-output role")
        net_added = (post_cut_summary["nonzero_coefficients"]
                     + post_correction_summary["nonzero_coefficients"]
                     - old_support)
        added_over_retimed_old = (
            post_cut_summary["nonzero_coefficients"]
            + post_correction_summary["nonzero_coefficients"]
            - retimed_original_summary["nonzero_coefficients"]
        )
        centre_charge = 112 - 4 * k_blocks
        unpaid = Q(1) + Q(k_blocks, 28)
        profile = {
            1: 192 + 4 * k_blocks + net_added,
            2: 56 - 4 * k_blocks,
            72: 73,
            56: 1,
        }
        moment = ceiling.relax(
            profile, 73, 896, 9, centre_charge, target_a, R=51,
            unpaid=unpaid)
        bracket = ceiling.ceiling(
            profile, 73, 896, 9, centre_charge, grid=Q(1, 10**12),
            R=51, unpaid=unpaid)
        kappa = bracket[1] / (1 + bracket[1])
        require(moment[1] < 1 and kappa > Q(3, 1000),
                "post-B rank-one incidence sensitivity no longer clears 0.003")
        retimed_hybrid_prefixes.append({
            "transformed_tetrads": k_blocks,
            "post_B_hybrid_coefficients":
                post_cut_summary["nonzero_coefficients"],
            "post_B_dirty_correction_coefficients":
                post_correction_summary["nonzero_coefficients"],
            "net_added_incidences_vs_original_pre_B_cut": net_added,
            "added_incidences_over_retimed_original_cut":
                added_over_retimed_old,
            "rank1_incidence_sensitivity_profile": {
                str(r): count for r, count in sorted(profile.items())
            },
            "complex_kappa_ceiling": str(kappa),
            "complex_kappa_ceiling_decimal": f"{float(kappa):.12f}",
        })
    require([
        (row["transformed_tetrads"], row["post_B_hybrid_coefficients"],
         row["post_B_dirty_correction_coefficients"],
         row["net_added_incidences_vs_original_pre_B_cut"],
         row["added_incidences_over_retimed_original_cut"],
         row["complex_kappa_ceiling_decimal"])
        for row in retimed_hybrid_prefixes
    ] == [
        (3, 450, 52, 326, 54, "0.003212495586"),
        (5, 454, 76, 354, 82, "0.007657155804"),
        (9, 441, 140, 405, 133, "0.015679681607"),
        (14, 437, 215, 476, 204, "0.024130777318"),
    ], "post-B retimed support/sensitivity table changed")

    # Rebuild the conditional full-basis cut from its exact matrix. The separate
    # dirty-baseline correction is a second input channel, not part of this cut.
    def build_cut_instructions(matrix):
        instructions = []
        for port, row in enumerate(matrix):
            for center, coefficient in enumerate(row):
                if coefficient:
                    instructions.append([
                        "add", 112 + port, word["centers"][center],
                        coefficient.numerator, coefficient.denominator, None,
                    ])
        return instructions

    first_three_instructions = build_cut_instructions(first_three_cut)
    changed_instructions = build_cut_instructions(changed_cut)
    hybrid_instructions = build_cut_instructions(hybrid_cut)
    require(len(first_three_instructions) == 202 and
            len(changed_instructions) == 286
            and len(hybrid_instructions) == hybrid_support == 225,
            "rebuilt centre cut has the wrong instruction count")
    rebuilt = [[Q(0) for _ in word["centers"]] for _ in range(112)]
    center_index = {register: index for index, register in
                    enumerate(word["centers"])}
    for op, source, destination, numerator, denominator, _ in changed_instructions:
        require(op == "add", "rebuilt cut contains a non-add operation")
        rebuilt[source - 112][center_index[destination]] += Q(
            numerator, denominator)
    require(rebuilt == changed_cut, "rebuilt cut differs from its exact matrix")

    incidence_sensitivities = []
    for k_blocks in (3, 5, 9, 14):
        basis_incidence = sum(prefix_support_deltas[:k_blocks])
        correction_incidence = sum(dirty_correction_deltas[:k_blocks])
        hybrid_incidence = (
            sum(hybrid_support_deltas[:k_blocks])
            + sum(hybrid_correction_deltas[:k_blocks]))
        centre = 112 - 4 * k_blocks
        unpaid = Q(1) + Q(k_blocks, 28)

        def price_sensitivity(overhead):
            profile = {
                1: 192 + 4 * k_blocks + overhead,
                2: 56 - 4 * k_blocks,
                72: 73,
                56: 1,
            }
            moment = ceiling.relax(
                profile, 73, 896, 9, centre, target_a, R=51,
                unpaid=unpaid)
            bracket = ceiling.ceiling(
                profile, 73, 896, 9, centre, grid=Q(1, 10**12), R=51,
                unpaid=unpaid)
            kappa = bracket[1] / (1 + bracket[1])
            require(moment[1] < 1 and kappa > Q(3, 1000),
                    "rank-one incidence sensitivity no longer clears kappa=0.003")
            return {
                "profile_if_each_added_incidence_costs_one_rank1_unit": {
                    str(r): n for r, n in sorted(profile.items())
                },
                "moment_at_a_3_over_997": [str(x) for x in moment],
                "complex_kappa_ceiling": str(kappa),
            }

        incidence_sensitivities.append({
            "transformed_tetrads": k_blocks,
            "full_basis_consumer_added_incidence_count": basis_incidence,
            "fused_update_dirty_correction_added_incidence_count": (
                basis_incidence + correction_incidence),
            "hybrid_fused_update_dirty_correction_added_incidence_count":
                hybrid_incidence,
            "full_basis_consumer": price_sensitivity(basis_incidence),
            "fused_update_plus_separate_dirty_correction": price_sensitivity(
                basis_incidence + correction_incidence),
            "hybrid_cut_plus_bottom_dirty_correction": price_sensitivity(
                hybrid_incidence),
        })
    require([row["full_basis_consumer_added_incidence_count"]
             for row in incidence_sensitivities] == [26, 50, 60, 110]
            and [row["fused_update_dirty_correction_added_incidence_count"]
                 for row in incidence_sensitivities] == [85, 146, 245, 391]
            and [row["hybrid_fused_update_dirty_correction_added_incidence_count"]
                 for row in incidence_sensitivities] == [43, 76, 125, 201],
            "rank-one incidence sensitivity prefixes changed")

    receipt = {
        "status": "PASS_P112_SELECTED_CENTER_CUT_COMPOSITION",
        "scope": "Exact conditional full and hybrid consumer maps for all fourteen source-bound P112 tetrads, a dirty-baseline counterexample, a pinned cut chronology audit, and exact canonical-word post-B readout retiming; no supplier admission or selected-kappa change.",
        "selected_kappa_unchanged": selected_record["decimal"],
        "selected_archive_sha256": archive_hash,
        "chronology": chronology,
        "tetrads_transformed": len(block_results),
        "blocks": block_results,
        "cut": {
            "old_add_instructions": len(word["cut"]),
            "new_add_instructions_after_first_three_blocks": len(first_three_instructions),
            "new_add_instructions_after_all_blocks": len(changed_instructions),
            "old_nonzero_coefficients": old_support,
            "nonzero_coefficients_after_first_three_blocks": first_three_support,
            "new_nonzero_coefficients": new_support,
            "added_nonzero_coefficients_after_first_three_blocks": 26,
            "added_nonzero_coefficients_after_all_blocks": 110,
            "consumer_identity": "S^T = S_new^T U, conditional on the consumer receiving the full transformed vector U y",
            "arithmetic_domain": "exact rational coefficients",
        },
        "hybrid_cut": {
            "definition": "H_top = S_top; H_bottom = (U^-T S)_bottom; C_top = 0; C_bottom = S_bottom - H_bottom",
            "dirty_identity": "H^T d + C^T d = S^T d",
            "fused_update_identity": "H^T U K = S^T K because the first four rows of U K vanish",
            "cut_nonzero_coefficients_all_blocks": hybrid_support,
            "bottom_dirty_correction_nonzero_coefficients_all_blocks":
                hybrid_correction_support,
            "net_added_incidence_count_vs_original_cut": hybrid_added_incidences,
            "net_added_incidence_prefixes_for_3_5_9_14_blocks": [43, 76, 125, 201],
            "schedule_integration": "conditional; the pinned cut precedes B, and adapter-expanded retiming/update availability is not established",
        },
        "post_B_readout_retiming": {
            "identity": "A^T x = (M_B^-T A)^T (M_B x) for the exact canonical B state map",
            "original_cut": retimed_original_summary,
            "hybrid_dirty_prefixes": retimed_hybrid_prefixes,
            "all_retimed_coefficients_use_only_post_B_output_ports": True,
            "separate_dirty_baseline_channel_and_duplicate_B_cost": "unproved",
            "adapter_expansion_and_native_schedule_binding": "unproved",
        },
        "dirty_state": {
            "coefficient_fusion_output_model": "d + U K x; it transforms the update, not the arbitrary dirty baseline d",
            "first_block_counterexample": first_dirty_counterexample,
            "old_cut_on_fused_update_mismatch_nonzeros_all_blocks":
                product_map_mismatch_support,
            "separate_dirty_correction_identity": "S_new^T(d+U K x) + (S-S_new)^T d = S^T(d+Kx)",
            "separate_dirty_correction_coefficients_all_blocks":
                sum(dirty_correction_deltas),
            "separate_dirty_correction_coefficients_first_three":
                sum(dirty_correction_deltas[:3]),
            "dirty_baseline_source_and_retention": "unproved",
        },
        "rank72_complex_incidence_sensitivity_only": {
            "target_a": str(target_a),
            "profile_rule": "{1:192+4k+added_incidence_count, 2:56-4k, 72:73, 56:1}",
            "unpaid_average_rule": "1+k/28",
            "rows": incidence_sensitivities,
            "not_a_scalar_ADD_tariff_or_dirty_source_proof": True,
        },
        "scope_limit": "The rank-72 profile and rank-1 incidence charge are sensitivities, not suppliers or a verified scalar-cost conversion. Post-B retiming is exact only for the canonical word map; adapter expansion, availability of separate fused and dirty-baseline streams, any duplicated B cost, cleanup/restoration, bit-side and complete implementation invoices remain open.",
    }
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    print("PASS_P112_SELECTED_CENTER_CUT_COMPOSITION blocks=14 cut_adds=176->286 "
          "hybrid_net_incidence=201 cut_before_B=true "
          "retimed_post_B_kappa3_sensitivity=%.12f no_new_kappa" %
          float(Q(retimed_hybrid_prefixes[0]["complex_kappa_ceiling"])))


if __name__ == "__main__":
    run()
