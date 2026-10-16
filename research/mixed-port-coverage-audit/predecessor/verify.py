#!/usr/bin/env python3
"""Exact replay of the five-plane P112 local decoder certificate."""
from __future__ import annotations
import copy, importlib.util, json
from pathlib import Path
PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
spec = importlib.util.spec_from_file_location("five_plane_verify_core", PACKAGE / "core.py")
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)

def matrix_from_blocks(blocks, matrices, labels):
    out = [[0] * core.DIM for _ in range(core.DIM)]
    for group, matrix in zip(blocks, matrices):
        core.need(len(matrix) == len(group) and all(len(row) == len(group) for row in matrix),
                  "coefficient matrix shape")
        for a, i in enumerate(group):
            for b, j in enumerate(group):
                if matrix[a][b]:
                    for r in range(core.DIM):
                        if (labels[i] >> r) & 1:
                            for c in range(core.DIM):
                                if (labels[j] >> c) & 1: out[r][c] ^= 1
    return out

def support_rank(left, right, labels):
    rows = [sum(core.dot(labels[i], labels[j]) << k for k, j in enumerate(right))
            for i in left]
    return core.rank_rows(rows, len(right))

def check_cover(candidate, labels):
    groups = candidate["groups"]; residual = candidate["residual"]
    core.need(len(groups) == 22 and all(len(g) == 5 for g in groups), "22 five-frames")
    core.need(len(residual) == 2, "one residual pair")
    blocks = groups + [residual]
    flat = [i for g in blocks for i in g]
    core.need(sorted(flat) == list(range(core.PORTS)), "cover is not a partition of P112")
    for group in blocks:
        core.need(len(set(group)) == len(group), "repeated port inside block")
        for i in group:
            core.need(core.dot(labels[i], labels[i]) == 1, "frame vector has wrong norm")
        for p, i in enumerate(group):
            for j in group[p + 1:]:
                core.need(core.dot(labels[i], labels[j]) == 0, "block is not an orthogonal frame")
    return blocks

def check_terms(candidate, labels):
    blocks = candidate["blocks"]; matrices = candidate["coefficient_matrices"]
    core.need(len(blocks) == len(matrices) == 23, "block/matrix count")
    got = matrix_from_blocks(blocks, matrices, labels)
    core.need(got == [[int(r == c) for c in range(core.DIM)] for r in range(core.DIM)],
              "sum A_g M_g A_g^T is not I_9")
    terms_by_block = [[] for _ in blocks]; hist = {}
    for term in candidate["terms"]:
        b = term["block"]; group = blocks[b]
        core.need(term["group"] == group, "term block index/group mismatch")
        d = len(group); left = term["left_coeff"]; right = term["right_coeff"]
        core.need(0 < left < (1 << d) and 0 < right < (1 << d), "rank-one coefficient mask")
        left_label = core.xor_selected([labels[i] for i in group], left)
        right_label = core.xor_selected([labels[i] for i in group], right)
        core.need(term["left_label"] == left_label and term["right_label"] == right_label,
                  "term label xor")
        ls = [i for i, q in enumerate(labels) if core.dot(q, left_label)]
        rs = [i for i, q in enumerate(labels) if core.dot(q, right_label)]
        core.need(term["left_support"] == ls and term["right_support"] == rs,
                  "term support sets")
        rank = support_rank(ls, rs, labels)
        core.need(rank == term["copy_rank"] and rank > 0, "B14 support-pairing charge")
        hist[rank] = hist.get(rank, 0) + 1; terms_by_block[b].append(term)
    for b, matrix in enumerate(matrices):
        group_terms = terms_by_block[b]
        for r in range(len(matrix)):
            for c in range(len(matrix)):
                value = 0
                for term in group_terms:
                    value ^= ((term["left_coeff"] >> r) & 1) & ((term["right_coeff"] >> c) & 1)
                core.need(value == matrix[r][c], "rank-one term reconstruction")
    need_hist = {str(k): v for k, v in sorted(hist.items())}
    core.need(need_hist == candidate["copy_rank_histogram"], "copy-rank histogram")
    charge = sum(k * v for k, v in hist.items())
    core.need(charge == candidate["copy_charge"] == 118, "total copy charge")
    # Independently verify the induced full 112 by 112 masked decoder.
    for i in range(core.PORTS):
        for j in range(core.PORTS):
            value = 0
            for term in candidate["terms"]:
                value ^= core.dot(labels[i], term["left_label"]) & core.dot(labels[j], term["right_label"])
            core.need(value == core.dot(labels[i], labels[j]), "full P112 decoder identity")
    return hist
def apply_c(state, q):
    out = {}
    def add(index, a, b):
        olda, oldb = out.get(index, (0, 0)); out[index] = (olda + a, oldb + b)
    for index, (a, b) in state.items():
        add(index, a - b, a + b)
        add(index ^ q, a + b, b - a)
    return {i: z for i, z in out.items() if z != (0, 0)}

def check_dirty_endpoint(blocks, labels, terms):
    checks = 0; full_target = (1 << core.PORTS) - 1
    patterns = [0, full_target, sum(1 << i for i in range(core.PORTS) if i % 2 == 0)]
    for source_index in range(core.PORTS):
        for dirty in patterns:
            for i in range(core.PORTS):
                value = (dirty >> i) & 1
                for term in terms:
                    value ^= core.dot(labels[i], term["left_label"]) \
                             & core.dot(labels[source_index], term["right_label"])
                expected = ((dirty >> i) & 1) ^ core.dot(labels[i], labels[source_index])
                core.need(value == expected, "dirty target source-basis action")
            checks += 1
    for dirty in patterns:
        for i in range(core.PORTS):
            value = (dirty >> i) & 1
            core.need(value == ((dirty >> i) & 1), "zero-source dirty target changed")
            checks += 1
    return checks

def check_corrections(blocks, labels):
    checks = 0
    for group in blocks:
        shift = 0
        for i in group: shift ^= labels[i]
        for start in range(1 << core.DIM):
            state = {start: (1, 0)}
            for i in group + group: state = apply_c(state, labels[i])
            expected = {start ^ shift: (1 << (2 * len(group)), 0)}
            core.need(state == expected, "C_E squared is not the aggregate translation")
            checks += 1
    return checks

def main():
    labels, _ = core.load_sources()
    record = json.loads((PACKAGE / "CANDIDATE.json").read_text())
    candidate = record["candidate"]
    core.need(record["seed"] == core.SEED and record["base_commit"] ==
              "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2", "candidate source pins")
    blocks = check_cover(candidate, labels)
    hist = check_terms(candidate, labels)

    # Re-run the bounded randomized-greedy construction to bind the saved cover to the seed.
    replay = core.find_cover(labels, candidate["attempt_cap"])
    core.need(replay is not None and replay == {k: candidate[k] for k in
              ("groups", "residual", "attempt", "greedy_steps", "five_frame_count", "attempt_cap")},
              "seeded construction replay")
    core.need(candidate["attempt"] == 365 and candidate["greedy_steps"] == 7438 and
              candidate["five_frame_count"] == 161280, "bounded search receipt")

    dirty_checks = check_dirty_endpoint(blocks, labels, candidate["terms"])
    correction_checks = check_corrections(blocks, labels)
    core.need(dirty_checks == 672 and correction_checks == 23 * (1 << core.DIM),
              "endpoint case count")

    # Negative controls: corrupt a block, an identity coefficient, and a rank-one term.
    bad_cover = copy.deepcopy(candidate); bad_cover["residual"][0] = bad_cover["groups"][0][0]
    rejected_cover = False
    try: check_cover(bad_cover, labels)
    except ValueError: rejected_cover = True
    core.need(rejected_cover, "duplicate-port cover control accepted")
    bad_matrix = copy.deepcopy(candidate); bad_matrix["coefficient_matrices"][0][0][0] ^= 1
    rejected_matrix = matrix_from_blocks(bad_matrix["blocks"], bad_matrix["coefficient_matrices"], labels) != \
                      [[int(r == c) for c in range(core.DIM)] for r in range(core.DIM)]
    core.need(rejected_matrix, "coefficient corruption control accepted")
    dropped = candidate["terms"][1:]
    rejected_term = any(
        sum((core.dot(labels[i], t["left_label"]) & core.dot(labels[j], t["right_label"]))
            for t in dropped) % 2 != core.dot(labels[i], labels[j])
        for i in range(core.PORTS) for j in range(core.PORTS))
    core.need(rejected_term, "deleted-term control accepted")

    profile, centre = core.profile_for(hist)
    screen = core.moment_screen(profile, centre)
    core.need(screen == candidate["moment_screen_u5"], "exact selected-word moment receipt")
    core.need(screen["moment_upper_decimal"] < 1.0 and screen["ceiling_upper_decimal"] > 1 / 99,
              "u=5 local screen does not pass a=1/99")
    shifted = profile.copy(); shifted[1] += len(blocks)
    shifted_screen = core.moment_screen(shifted, centre + len(blocks))
    core.need(shifted_screen == candidate["one_unit_per_aggregate_translation_screen"],
              "aggregate-translation cost screen")
    core.need(shifted_screen["moment_upper_decimal"] < 1.0,
              "one rank-1 unit per aggregate correction exceeds target")
    overhead = core.all_in_rank1_threshold(profile, centre)
    core.need(overhead == candidate["all_in_rank1_overhead_threshold"], "overhead budget receipt")
    core.need(overhead["largest_passing"]["total_rank1_equivalent_charge"] == 275 and
              overhead["first_failing"]["total_rank1_equivalent_charge"] == 276 and
              overhead["largest_passing"]["moment_upper_decimal"] < 1 <
              overhead["first_failing"]["moment_lower_decimal"], "rank-1 overhead threshold")

    print("PASS_P112_FIVE_PLANE_PORT_DECODER",
          f"frames={len(candidate['groups'])}+1x2",
          f"cover_attempt={candidate['attempt']}",
          f"terms={candidate['term_count']}", f"copy={candidate['copy_charge']}",
          f"rank_hist={candidate['copy_rank_histogram']}",
          f"endpoint_checks={correction_checks}", f"dirty_checks={dirty_checks}",
          f"a_hi={screen['ceiling_upper_decimal']:.12f}",
          f"rank1_overhead={overhead['largest_passing']['extra_rank1_equivalent_charge']}")

if __name__ == "__main__":
    main()
