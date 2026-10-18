#!/usr/bin/env python3
"""Independent exact Walsh-character oracle; no producer code is imported.

Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
Every complex coefficient is an integer pair divided by two. PERM recipes
are checked on all 512 characters before the full thirteen-role replay.
The explicit --write option is the only operation that creates a receipt.
"""

import argparse
from collections import Counter
import copy
import hashlib
from itertools import combinations
import json
from pathlib import Path
import struct
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
H = 9
N = 1 << H
ROLES = 13
BASE = "c5108f0f68d482e5712a8e26a5978d47762dfc16"
FIXED_PINS = {
    "inputs/pr1230-WITNESS.json": "8360caf56e5fa2b24528ee05ec45d3126df92b0b66abe5558f63ca021c6736f2",
    "inputs/pr1230-PROOF.md": "154752a984064a634a996b68e923e8025f9767c6fd48c04599bdcbc1759b1710",
    "inputs/pr1230-README.md": "555436aa7126a903e8af0a50fc5ff86ddce0a20d682a33efb443735ec4e0ba20",
    "notes/general-clifford-frames.tex": "c9bb9655b594583c6b4bab8cb485233f1d1e588f83858cf1e4c3530cee8fed54",
    "certificates/selected-result.json": "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
    "research/community-frontier1094-audit/ASSEMBLY.json": "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045",
    "research/community-frontier1094-audit/SELECTED-SOURCE.json": "79b3de5db3dbcb9829789ba58e9e45758926031e2a7d80667a08429d369be53b",
    "docs/research/community-batch1099-review.md": "7e76d2c38e5fce30587835b7251df1430488ae4dd372611ef69a3f03f476b6cb",
}
S = [31, 55, 457, 458, 481, 482]
T = [47, 59, 87, 151, 279, 451]
ALPHA = [1, 1, -1, -1, -1, -1]
BETA = [1, 1, 1, 1, 1, -1]
UB = [31, 481, 3, 40]
F = [(1 << j, 1) for j in range(H)]


class Rejected(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Rejected(message)


def integer(value, low, high, context):
    require(type(value) is int and low <= value <= high, context)
    return value


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def parity(mask):
    return mask.bit_count() & 1


def span(basis):
    values = {0}
    for v in basis:
        values |= {x ^ v for x in values}
    return values


def gf_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return len(pivots)


def transpose(columns):
    return [sum(((columns[j] >> i) & 1) << j for j in range(H))
            for i in range(H)]


def linear(columns, x):
    answer = 0
    for j, col in enumerate(columns):
        if (x >> j) & 1:
            answer ^= col
    return answer


def inverse(columns):
    rows = [row | (1 << (H + j))
            for j, row in enumerate(transpose(columns))]
    for j in range(H):
        pivot = next((i for i in range(j, H) if (rows[i] >> j) & 1), None)
        require(pivot is not None, "singular address permutation")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        for i in range(H):
            if i != j and ((rows[i] >> j) & 1):
                rows[i] ^= rows[j]
    return transpose([row >> H for row in rows])


def factors(value):
    require(type(value) is list, "frame factors must be a list")
    for pair in value:
        require(type(pair) is list and len(pair) == 2, "invalid frame factor")
        integer(pair[0], 1, N - 1, "frame mask")
        integer(pair[1], -1, 1, "frame sign")
        require(pair[1] != 0, "zero frame sign")
    return value


def phase(frame, k):
    return sum(sign * parity(mask & k) for mask, sign in frame) % 4


def binary_b(frame):
    rows = [0] * H
    for mask, _ in frame:
        for j in range(H):
            if (mask >> j) & 1:
                rows[j] ^= mask
    return rows


def transition_rank(before, after):
    return gf_rank([a ^ b for a, b in zip(binary_b(before), binary_b(after))])


def rotate(z, exponent):
    re, im = z
    return ((re, im), (-im, re), (-re, -im), (im, -re))[exponent % 4]


def source_pins():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    require(manifest.get("base_commit") == BASE, "wrong base commit")
    entries = manifest.get("retained_inputs", []) + manifest.get("repository_inputs", [])
    require(len(entries) == len(FIXED_PINS), "incomplete source inventory")
    require(len({entry.get("path") for entry in entries}) == len(FIXED_PINS),
            "duplicated source inventory")
    require({entry.get("path") for entry in entries} == set(FIXED_PINS),
            "unexpected source inventory")
    result = {}
    for entry in entries:
        name = entry["path"]
        raw = ((HERE if name.startswith("inputs/") else ROOT) / name).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        git_blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(digest == FIXED_PINS[name] == entry.get("sha256"), "source digest " + name)
        require(git_blob == entry.get("git_blob"), "source Git blob " + name)
        result[name] = digest
    witness = json.loads((HERE / "inputs/pr1230-WITNESS.json").read_text())["witness"]
    require(witness["h"] == H and witness["source_labels"] == S
            and witness["target_labels"] == T and witness["source_signs"] == ALPHA
            and witness["target_signs"] == BETA and witness["U_basis"] == UB,
            "changed fixed geometric witness")
    return result, witness


def geometry(witness):
    u = span(UB)
    require(len(u) == 16, "separator dimension")
    odd = sorted(x for x in u if parity(x))
    orthonormal = next((list(q) for q in combinations(odd, 4)
                        if all(not parity(q[i] & q[j])
                               for i in range(4) for j in range(i))), None)
    require(orthonormal is not None and span(orthonormal) == u, "no orthonormal U basis")
    require(all(s in u for s in S), "source outside separator")
    require(all(not parity(t & v) for t in T for v in UB), "target outside complement")
    for i, s in enumerate(S):
        for j, t in enumerate(T):
            entry = [1, 0, -1, 0][(s & t).bit_count() % 4]
            require(entry == ALPHA[i] * BETA[j], "fixed signed kernel")
    for label, basis in zip(S, witness["incoming_residual_bases"]):
        require(len(basis) == 3 and len(span(basis)) == 8,
                "incoming residual dimension")
        require(span(basis) == {v for v in u if not parity(v & label)},
                "incoming residual space")
        require(all(parity(a & b) == (i == j)
                    for i, a in enumerate(basis) for j, b in enumerate(basis)),
                "incoming residual Gram")
    w = {x for x in range(N) if all(not parity(x & v) for v in UB)}
    for label, basis in zip(T, witness["outgoing_residual_bases"]):
        require(len(basis) == 4 and span(basis) == {v for v in w if not parity(v & label)},
                "outgoing residual space")
        require(all(parity(a & b) == (i == j)
                    for i, a in enumerate(basis) for j, b in enumerate(basis)),
                "outgoing residual Gram")
    return orthonormal


def logical_word(anchor):
    if anchor is None:
        return ([(12, i, ALPHA[i], 0) for i in range(6)]
                + [(6 + j, 12, BETA[j], 1) for j in range(6)]
                + [(12, i, -ALPHA[i], 0) for i in reversed(range(6))]
                + [(6 + j, 12, -BETA[j], 1) for j in range(6)])
    p = 6 + anchor
    return ([(6 + j, p, -BETA[j] * BETA[anchor], 0)
             for j in range(6) if j != anchor]
            + [(p, i, BETA[anchor] * ALPHA[i], 1) for i in range(6)]
            + [(6 + j, p, BETA[j] * BETA[anchor], 0)
               for j in range(6) if j != anchor])


def scheduled(anchor, orthonormal):
    gauges = [[(s, 1)] for s in S] + [F + [(t, -1)] for t in T]
    gauges.append([(v, 1) for v in orthonormal] if anchor is None else [])
    operations = []
    profile = Counter()
    def transform(role, before, after):
        if any(phase(before, k) != phase(after, k) for k in range(N)):
            operations.append(("PHASE", role, [(phase(after, k) - phase(before, k)) % 4
                                               for k in range(N)]))
        rank = transition_rank(before, after)
        if rank:
            profile[rank] += 1
    for role, gauge in enumerate(gauges):
        transform(role, [], gauge)
    for dst, src, sign, power in logical_word(anchor):
        transform(src, gauges[src], gauges[dst])
        operations.append(("AXPY", dst, src, sign, power))
        transform(src, gauges[dst], gauges[src])
    for role, gauge in enumerate(gauges):
        transform(role, gauge, F)
    return operations, dict(sorted(profile.items()))


def checked_recipe(stream, transform):
    start = integer(transform.get("start"), 0, len(stream), "transform start")
    end = integer(transform.get("end"), start, len(stream), "transform end")
    role = integer(transform.get("role"), 0, ROLES - 1, "transform role")
    before = factors(transform.get("from_factors"))
    after = factors(transform.get("to_factors"))
    rank = transition_rank(before, after)
    child_ranks = []
    modes = list(range(N))
    phases = [0] * N
    movement = Counter()
    for primitive in stream[start:end]:
        require(type(primitive) is list and primitive[0] in ("PERM", "CHILD", "SHIFT"),
                "invalid frame recipe primitive")
        require(primitive[1] == role and type(primitive[1]) is int, "recipe role mismatch")
        if primitive[0] == "PERM":
            require(len(primitive) == 3 and type(primitive[2]) is list
                    and len(primitive[2]) == H, "PERM schema")
            columns = [integer(v, 0, N - 1, "PERM column") for v in primitive[2]]
            inv_transpose = transpose(inverse(columns))
            modes = [linear(inv_transpose, k) for k in modes]
            movement["address_permutations"] += 1
        elif primitive[0] == "CHILD":
            require(len(primitive) == 4 and primitive[3] is False,
                    "CHILD must be forward-only; implement inverse with an explicit SHIFT")
            r = integer(primitive[2], 1, H, "CHILD rank")
            phases = [(e + (k & ((1 << r) - 1)).bit_count()) % 4
                      for e, k in zip(phases, modes)]
            child_ranks.append(r)
        else:
            require(len(primitive) == 3, "SHIFT schema")
            mask = integer(primitive[2], 0, N - 1, "SHIFT mask")
            phases = [(e + 2 * parity(k & mask)) % 4 for e, k in zip(phases, modes)]
            movement["translations"] += 1
    require(modes == list(range(N)), "frame recipe is not circulant")
    expected = [(phase(after, k) - phase(before, k)) % 4 for k in range(N)]
    require(phases == expected, "physical recipe disagrees with declared exact phase")
    require(child_ranks == ([rank] if rank else []), "child rank invoice differs from binary B rank")
    if "basis" in transform:
        basis = [integer(v, 1, N - 1, "child basis vector") for v in transform["basis"]]
        require(len(basis) == rank and len(span(basis)) == 1 << rank, "child basis rank")
        require(binary_b([(v, 1) for v in basis])
                == [a ^ b for a, b in zip(binary_b(before), binary_b(after))],
                "child basis has wrong binary B block")
    return start, end, ("PHASE", role, phases), rank, movement


def physical_program(program, reverse=False):
    require(type(program) is dict and type(program.get("stream")) is list
            and type(program.get("transforms")) is list, "program schema")
    stream = program["stream"]
    by_start = {}
    covered = set()
    profile = Counter()
    movement = Counter()
    exact_recipes = 0
    for transform in program["transforms"]:
        start, end, operation, rank, costs = checked_recipe(stream, transform)
        require(start < end, "empty physical recipe")
        require(start not in by_start and not (covered & set(range(start, end))),
                "overlapping physical recipes")
        covered.update(range(start, end))
        by_start[start] = (end, operation, transform)
        if rank:
            profile[rank] += 1
        movement.update(costs)
        exact_recipes += 1
    operations = []
    scalar_word = []
    current_frames = [F if reverse else [] for _ in range(ROLES)]
    rank_descents = 0
    cursor = 0
    while cursor < len(stream):
        if cursor in by_start:
            end, operation, transform = by_start[cursor]
            role = transform["role"]
            before, after = transform["from_factors"], transform["to_factors"]
            require(all(phase(before, k) == phase(current_frames[role], k) for k in range(N)),
                    "declared input gauge differs from actual current gauge")
            rank_descents += gf_rank(binary_b(after)) < gf_rank(binary_b(before))
            current_frames[role] = after
            operations.append(operation)
            cursor = end
            continue
        require(cursor not in covered, "unreachable recipe boundary")
        primitive = stream[cursor]
        require(type(primitive) is list and len(primitive) == 5
                and primitive[0] == "AXPY", "uncovered non-AXPY primitive")
        dst = integer(primitive[1], 0, ROLES - 1, "AXPY destination")
        src = integer(primitive[2], 0, ROLES - 1, "AXPY source")
        require(dst != src, "AXPY aliases")
        sign = integer(primitive[3], -1, 1, "AXPY sign")
        require(sign != 0, "zero AXPY")
        power = integer(primitive[4], 0, 1, "AXPY scale")
        require(all(phase(current_frames[dst], k) == phase(current_frames[src], k)
                    for k in range(N)), "AXPY operands do not have one exact common gauge")
        operations.append(("AXPY", dst, src, sign, power))
        scalar_word.append((dst, src, sign, power))
        cursor += 1
    expected_word = logical_word(program.get("anchor"))
    if reverse:
        expected_word = [(dst, src, -sign, power)
                         for dst, src, sign, power in reversed(expected_word)]
    require(scalar_word == expected_word, "physical logical word differs")
    terminal = [] if reverse else F
    require(all(phase(frame, k) == phase(terminal, k)
                for frame in current_frames for k in range(N)), "missing final boundary gauge")
    movement["scalar_adds"] = len(scalar_word)
    movement["half_scalings"] = sum(item[3] for item in scalar_word)
    movement["cells_per_array"] = N
    movement["frame_rank_descents"] = rank_descents
    return operations, dict(sorted(profile.items())), dict(sorted(movement.items())), exact_recipes


def forward_only_inverse(program):
    """Independently expand inverses into the same forward-only primitive API."""
    stream = program["stream"]
    ends = {transform["end"]: transform for transform in program["transforms"]}
    output = {"name": program["name"], "anchor": program["anchor"],
              "stream": [], "transforms": []}
    cursor = len(stream)
    while cursor:
        if cursor in ends:
            transform = ends[cursor]
            inverted = copy.deepcopy(transform)
            inverted["start"] = len(output["stream"])
            for primitive in reversed(stream[transform["start"]:cursor]):
                op, role = primitive[:2]
                if op == "PERM":
                    output["stream"].append(["PERM", role, inverse(primitive[2])])
                elif op == "SHIFT":
                    output["stream"].append(primitive[:])
                else:
                    require(op == "CHILD" and primitive[3] is False,
                            "unsupported inverse primitive")
                    output["stream"] += [["SHIFT", role, (1 << primitive[2]) - 1],
                                          primitive[:]]
            inverted["end"] = len(output["stream"])
            inverted["from_factors"], inverted["to_factors"] = (
                inverted["to_factors"], inverted["from_factors"])
            output["transforms"].append(inverted)
            cursor = transform["start"]
        else:
            primitive = stream[cursor - 1]
            require(primitive[0] == "AXPY", "uncovered inverse primitive")
            output["stream"].append(primitive[:3] + [-primitive[3], primitive[4]])
            cursor -= 1
    return output


def expected_matrix(k, reverse=False):
    matrix = [[(0, 0) for _ in range(ROLES)] for _ in range(ROLES)]
    e = (-k.bit_count() if reverse else k.bit_count()) % 4
    for role in range(ROLES):
        matrix[role][role] = rotate((2, 0), e)
    for j in range(6):
        for i in range(6):
            matrix[6 + j][i] = rotate(((-1 if reverse else 1) * ALPHA[i] * BETA[j], 0), e)
    return matrix


def run_matrix(operations, k, reverse=False):
    matrix = [[(2, 0) if row == col else (0, 0)
               for col in range(ROLES)] for row in range(ROLES)]
    sequence = reversed(operations) if reverse else operations
    for operation in sequence:
        if operation[0] == "PHASE":
            _, role, exponents = operation
            e = (-exponents[k] if reverse else exponents[k]) % 4
            matrix[role] = [rotate(z, e) for z in matrix[role]]
        else:
            _, dst, src, sign, power = operation
            sign *= -1 if reverse else 1
            divisor = 1 << power
            require(all(re % divisor == 0 and im % divisor == 0 for re, im in matrix[src]),
                    "unexpected non-half-integral intermediate coefficient")
            matrix[dst] = [(a + sign * c // divisor, b + sign * d // divisor)
                           for (a, b), (c, d) in zip(matrix[dst], matrix[src])]
    return matrix


def replay(operations):
    digests = []
    for reverse in (False, True):
        digest = hashlib.sha256()
        for k in range(N):
            matrix = run_matrix(operations, k, reverse)
            require(matrix == expected_matrix(k, reverse),
                    "wrong complete dirty endpoint at Walsh character " + str(k))
            for row in range(ROLES):
                for col in range(ROLES):
                    re, im = matrix[row][col]
                    digest.update(struct.pack("<5i", k, row, col, re, im))
        digests.append(digest.hexdigest())
    return digests


def rejected(function, message):
    try:
        function()
    except (Rejected, KeyError, IndexError, TypeError):
        return message
    raise Rejected("negative control passed: " + message)


def controls(programs, abstract):
    results = []
    baseline = copy.deepcopy(abstract[0])
    index = next(i for i, op in enumerate(baseline) if op[0] == "AXPY" and op[4] == 1)
    baseline[index] = baseline[index][:4] + (0,)
    results.append(rejected(lambda: replay(baseline), "omit_half_factor"))
    for name, anchor, selector in (("omit_anchor_precompensation", 1, "first"),
                                   ("omit_anchor_postcompensation", 1, "last")):
        ops = copy.deepcopy(abstract[anchor])
        candidates = [i for i, op in enumerate(ops) if op[0] == "AXPY" and op[4] == 0]
        del ops[candidates[0 if selector == "first" else -1]]
        results.append(rejected(lambda: replay(ops), name))
    ops = copy.deepcopy(abstract[0])
    last_axpy = max(i for i, op in enumerate(ops) if op[0] == "AXPY")
    del ops[last_axpy]
    results.append(rejected(lambda: replay(ops), "omit_helper_dirty_correction"))
    ops = copy.deepcopy(abstract[0])
    first_axpy = next(i for i, op in enumerate(ops) if op[0] == "AXPY")
    del ops[first_axpy + 1]
    results.append(rejected(lambda: replay(ops), "omit_source_restore_transition"))
    ops = copy.deepcopy(abstract[1])
    del ops[0]
    results.append(rejected(lambda: replay(ops), "omit_source_birth"))
    ops = copy.deepcopy(abstract[1])
    del ops[-1]
    results.append(rejected(lambda: replay(ops), "omit_unused_helper_F_tail"))
    ops = copy.deepcopy(abstract[1])
    tag, role, exponents = ops[-1]
    ops[-1] = (tag, role, [(-x) % 4 for x in exponents])
    results.append(rejected(lambda: replay(ops), "replace_exact_F_by_F_inverse"))
    physical = copy.deepcopy(programs[0])
    child_index = next(i for i, op in enumerate(physical["stream"]) if op[0] == "CHILD")
    physical["stream"][child_index][3] = not physical["stream"][child_index][3]
    results.append(rejected(lambda: physical_program(physical), "wrong_exact_child_inverse"))
    physical = copy.deepcopy(programs[0])
    permutation = next(op for op in physical["stream"] if op[0] == "PERM")
    permutation[2][0] = 0
    results.append(rejected(lambda: physical_program(physical), "singular_address_adapter"))
    physical = copy.deepcopy(programs[0])
    child = next(op for op in physical["stream"] if op[0] == "CHILD")
    child[2] = 1 if child[2] != 1 else 2
    results.append(rejected(lambda: physical_program(physical), "wrong_recursive_child_rank"))
    physical = copy.deepcopy(programs[0])
    transform = physical["transforms"][0]
    transform["to_factors"][0][1] *= -1
    results.append(rejected(lambda: physical_program(physical), "wrong_declared_phase"))
    physical = copy.deepcopy(programs[0])
    # Modify both ends equally: the ratio still matches the physical recipe,
    # while the asserted current gauge becomes false.
    transform = physical["transforms"][0]
    transform["from_factors"] += [[1, 1]]
    transform["to_factors"] += [[1, 1]]
    results.append(rejected(lambda: physical_program(physical), "wrong_common_gauge_chronology"))
    return results


def compute():
    pins, witness = source_pins()
    ub = geometry(witness)
    payload = json.loads((HERE / "PROGRAMS.json").read_text())
    require(payload.get("h") == H and type(payload.get("h")) is int
            and payload.get("roles") == ROLES and type(payload.get("roles")) is int,
            "wrong physical dimensions")
    require(payload.get("seed") == 47 and type(payload.get("seed")) is int
            and payload.get("base_commit") == BASE, "wrong physical seed or base")
    programs = payload.get("programs")
    require(type(programs) is list and len(programs) == 7, "incomplete anchor census")
    require([program.get("anchor") for program in programs] == [None, 0, 1, 2, 3, 4, 5],
            "wrong anchor census order")
    require([program.get("name") for program in programs]
            == ["baseline"] + ["anchor-" + str(i) for i in range(6)], "program names")
    reports = []
    abstracts = []
    for program in programs:
        anchor = program["anchor"]
        if anchor is not None:
            integer(anchor, 0, 5, "anchor type")
        reference, predicted_profile = scheduled(anchor, ub)
        physical, physical_profile, costs, recipes = physical_program(program)
        expected_profile = ({1: 12, 3: 24, 4: 25, 5: 1, 8: 12} if anchor is None
                            else {1: 12, 2: 20, 7: 12, 8: 12, 9: 1})
        require(predicted_profile == physical_profile == expected_profile,
                "complete primitive profile mismatch")
        reference_digests = replay(reference)
        physical_digests = replay(physical)
        require(reference_digests == physical_digests, "physical and independent endpoint differ")
        inverse_program = forward_only_inverse(program)
        inverse_operations, inverse_profile, inverse_costs, inverse_recipes = physical_program(
            inverse_program, reverse=True)
        require(inverse_profile == physical_profile and inverse_recipes == recipes,
                "forward-only inverse changed the child profile")
        for k in range(N):
            require(run_matrix(inverse_operations, k) == expected_matrix(k, reverse=True),
                    "forward-only inverse has wrong dirty endpoint")
        require(inverse_costs["translations"] == costs["translations"] + sum(physical_profile.values()),
                "inverse coordinate translations were not completely charged")
        require(costs["scalar_adds"] == (24 if anchor is None else 16)
                and costs["half_scalings"] == (12 if anchor is None else 6), "scalar invoice")
        mass = sum(rank * count for rank, count in physical_profile.items())
        require(mass == (285 if anchor is None else 241), "rank mass")
        reports.append({"name": program["name"], "anchor": anchor,
                        "profile": physical_profile, "rank_mass": mass,
                        "costs": costs, "physical_recipes": recipes,
                        "inverse_forward_only_costs": inverse_costs,
                        "forward_walsh_endpoint_sha256": physical_digests[0],
                        "inverse_walsh_endpoint_sha256": physical_digests[1],
                        "walsh_characters": N, "raw_input_columns": ROLES,
                        "entry_checks_each_direction": N * ROLES * ROLES,
                        "strictly_below_thirteen_role_mass": mass < ROLES * H})
        abstracts.append(reference)
    require(len({r["forward_walsh_endpoint_sha256"] for r in reports}) == 1,
            "programs have different complete endpoints")
    negative = controls(programs, abstracts)
    return {"schema": "seed47-independent-walsh-v1", "seed": 47,
            "base_commit": BASE, "retained_source_sha256": pins,
            "programs_raw_sha256": hashlib.sha256((HERE / "PROGRAMS.json").read_bytes()).hexdigest(),
            "independently_found_orthonormal_U_basis": ub,
            "coefficient_encoding": "Gaussian integer pair divided by2",
            "endpoint": "all13 outputs: F times identity plus target/source alpha*beta/2 shear",
            "inverse_endpoint": "all13 outputs: F inverse times identity minus target/source alpha*beta/2 shear",
            "programs": reports, "negative_controls": negative,
            "anchor_census": 6, "selected_anchor": 47 % 6,
            "temporary_source_observation_counterexample": {
                "program": "baseline", "source_role": 0, "walsh_character": 1,
                "prescribed_source_phase": phase([(S[0], 1)], 1),
                "phase_during_first_read": phase([(v, 1) for v in ub], 1),
                "required_contract": "source is mutable and unobserved within read/restore query"},
            "rank_mass_improvement": 44, "scalar_add_improvement": 8,
            "half_scaling_improvement": 6, "thirteen_role_reference_mass": ROLES * H,
            "new_kappa": False, "monotone_supplier_adoption": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path,
                        help="explicitly generate this receipt path; default only compares existing receipt")
    args = parser.parse_args()
    receipt = HERE / "INDEPENDENT.json"
    if args.write is None:
        require(receipt.is_file(), "missing INDEPENDENT.json; explicit --write is required to generate")
        saved = json.loads(receipt.read_text())
    result = compute()
    if args.write is not None:
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(canonical(saved) == canonical(result), "independent receipt mismatch")
    print("PASS_SEED47_INDEPENDENT_WALSH anchors=6 characters=512 columns=13 mass=285->241 adds=24->16 controls="
          + str(len(result["negative_controls"])) + " no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (Rejected, OSError, ValueError, KeyError, TypeError) as error:
        print("FAIL_SEED47_INDEPENDENT_WALSH: " + str(error), file=sys.stderr)
        sys.exit(1)
