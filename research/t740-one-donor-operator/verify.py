#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 thakrarsagar. Developed with substantial OpenAI Codex assistance.
"""All-character five-site operator certificate for one authenticated T740 group.

Baseline phases use degree-two Z4 polynomials on Boolean Fourier coordinates.
Five additional commuting indeterminates record the changed residual phases.
The resulting matrix cancels every ambient character polynomial exactly.
"""

import argparse
from collections import defaultdict
import hashlib
from itertools import product
import json
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/idle-star-paired-axis-census"
ALLOCATION = "research/rank7-joint-endframes/allocation"
PHASES = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
BITS = 73
SITES = (8, 10, 12, 13, 14)
ZERO_PHASE = (0, 0, 0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(root=ROOT):
    data = {}
    for pin in json.loads((HERE / "SOURCES.json").read_bytes())["files"]:
        if pin["usage"] != "input":
            continue
        path = pin["path"]
        require(not Path(path).is_absolute() and ".." not in Path(path).parts,
                "relative source path")
        body = (Path(root) / path).read_bytes()
        require(hashlib.sha256(body).hexdigest() == pin["sha256"], "source hash: " + path)
        data[path] = body
    return data


def load_context(root=ROOT):
    """Reuse authenticated source loading/projection, not its numerical replay."""
    data = authenticate(root)
    source = ModuleType("retained_idle_axis_operator")
    source.__file__ = str(Path(root) / SOURCE / "verify.py")
    exec(compile(data[SOURCE + "/verify.py"], source.__file__, "exec"), source.__dict__)
    source.authenticate()

    def decode(path):
        return source.decode(data[path])

    base = decode(SOURCE + "/vendor/BASE-FILL.json.gz")["rows"]
    journal = decode(SOURCE + "/vendor/EXCHANGE.json")
    rows = source.project_all_ports(base, source.journal_edits(base, journal))[0]
    order = [[stage, owner + 74 * copy]
             for stage, owner in decode(ALLOCATION + "/ORDER.json") for copy in range(10)]
    dispatch = {(stage, owner): tag for stage, owner, tag in decode(ALLOCATION + "/DISPATCH.json")}
    providers = decode(SOURCE + "/vendor/PROVIDERS.json")
    plan = decode(ALLOCATION + "/vendor/PLAN.json.gz")
    template = decode(ALLOCATION + "/vendor/TEMPLATE.json.gz")
    recipes = decode(PHASES)["recipes"]
    context = source.prepare_port(0, rows, order, dispatch, providers, plan, template, recipes)
    require(len(rows) == 30, "owner-zero port-zero hosted rows")
    return source, context, source.stage_blocks(template)


def phase_add(left, right):
    """Add Z4 linear coefficients and even cross coefficients exactly."""
    a, b, c = left
    d, e, f = right
    return a ^ d, b ^ e ^ (a & d), c ^ f


def phase_scale(value, coefficient):
    require(type(coefficient) is int, "integer phase coefficient")
    result = ZERO_PHASE
    for _ in range(coefficient % 4):
        result = phase_add(result, value)
    return result


def phase_axis(vector, bits=BITS):
    """Parity(v & chi) = sum chi_i - 2 sum_{i<j} chi_i chi_j (mod4)."""
    require(type(bits) is int and 1 <= bits <= BITS, "phase coordinate dimension")
    require(type(vector) is int and 0 <= vector < 1 << bits, "phase axis")
    positions = [index for index in range(bits) if vector >> index & 1]
    # Cross positions always use the fixed ambient stride, even in small tests.
    cross = sum(1 << (left * BITS + right)
                for offset, left in enumerate(positions) for right in positions[offset + 1:])
    return vector, 0, cross


def phase_value(value, character):
    require(type(character) is int and 0 <= character < 1 << BITS, "Fourier character")
    low, high, cross = value
    result = (low & character).bit_count() + 2 * (high & character).bit_count()
    while cross:
        bit = cross & -cross
        left, right = divmod(bit.bit_length() - 1, BITS)
        if character >> left & 1 and character >> right & 1:
            result += 2
        cross ^= bit
    return result % 4


def initial_matrix():
    return [[{(0, 0, 0, 0): 1} if row == column else {}
             for column in range(8)] for row in range(8)]


def phase_row(matrix, stream, exponent, variable=0):
    for column in range(8):
        changed = defaultdict(int)
        for (mask, low, high, cross), coefficient in matrix[stream][column].items():
            require(not mask & variable, "formal site occurs at most once along a path")
            changed[(mask | variable,) + phase_add((low, high, cross), exponent)] += coefficient
        matrix[stream][column] = {key: value for key, value in changed.items() if value}


def shear(matrix, destination, source, coefficient):
    require(destination != source and coefficient in (-1, 1), "retained stream shear")
    for column in range(8):
        for key, value in matrix[source][column].items():
            matrix[destination][column][key] = matrix[destination][column].get(key, 0) + coefficient * value
        matrix[destination][column] = {
            key: value for key, value in matrix[destination][column].items() if value}


def sum_axes(axes):
    result = ZERO_PHASE
    for axis in axes:
        result = phase_add(result, phase_axis(axis))
    return result


def data_event(matrix, event, context, variables, seen):
    recipe, template = context["recipe"], context["template"]
    kind, q = event["kind"], phase_axis(recipe["q"])
    if kind == "local_cover_sweep":
        stage = event["stage"]
        local = next(item for item in template["recipe"]
                     if item["kind"] == "local" and item["stage"] == stage)
        left, right = 2 * local["pair"], 2 * local["pair"] + 1
        for side, stream in enumerate((left, right)):
            before = (phase_scale(q, 1 - side) if stage == 0 else
                      phase_add(((1 << (9 + 8 * (stage - 1))) - 1, 0, 0), phase_scale(q, -side)))
            phase_row(matrix, stream, phase_scale(before, -1))
        if local["reverse"]:
            shear(matrix, left, right, -1)
        else:
            shear(matrix, right, left, 1)
        for side, stream in enumerate((left, right)):
            phase_row(matrix, stream,
                      phase_add(((1 << (9 + 8 * stage)) - 1, 0, 0), phase_scale(q, -side)))
    elif kind == "idle_cover_sweep":
        for side, child in enumerate(event["child_indices"]):
            exponent = sum_axes(context["residual"][child])
            translation = recipe["idle_children"][child]["translation_after"]
            exponent = phase_add(exponent, phase_scale(phase_axis(translation), 2))
            variable = variables.get(child, 0)
            if variable:
                require(child not in seen, "one residual insertion per selected site")
                seen.add(child)
            phase_row(matrix, 2 * event["pair"] + side, exponent, variable)
    elif kind == "bridge":
        destination, source, coefficient = event["dst"], event["src"], event["coefficient"]
        shear(matrix, 2 * destination, 2 * source, coefficient)
        shear(matrix, 2 * source + 1, 2 * destination + 1, -coefficient)
    elif kind == "terminal_Y_translations":
        for pair in event["pairs"]:
            phase_row(matrix, 2 * pair + 1, phase_scale(q, 2))
    elif kind == "terminal":
        for pair in range(event["pairs"]):
            matrix[2 * pair], matrix[2 * pair + 1] = matrix[2 * pair + 1], matrix[2 * pair]
            for column in range(8):
                matrix[2 * pair + 1][column] = {
                    key: -value for key, value in matrix[2 * pair + 1][column].items()}
    else:
        raise ValueError("unknown source event: " + kind)


def symbolic_replay(context, blocks, sites=SITES):
    require(len(sites) == len(set(sites)), "distinct formal phase sites")
    variables = {child: 1 << index for index, child in enumerate(sites)}
    matrix, seen, peak = initial_matrix(), set(), 8
    for time, (stage, owner) in enumerate(context["order"]):
        for stream, axes in context["hosts"].get(time, ()):
            phase_row(matrix, stream, sum_axes(axes))
        if owner == 0:
            for event in blocks[stage]:
                data_event(matrix, event, context, variables, seen)
                peak = max(peak, sum(len(entry) for row in matrix for entry in row))
    require(seen == set(sites), "all selected residual sites reached")
    inverse_baseline = phase_scale(((1 << BITS) - 1, 0, 0), -1)
    for stream in range(8):
        phase_row(matrix, stream, inverse_baseline)
    return matrix, peak


def normalized_rows(matrix):
    rows = []
    for row, entries in enumerate(matrix):
        for column, entry in enumerate(entries):
            for (mask, low, high, cross), coefficient in entry.items():
                require(not (low or high or cross), "uncancelled ambient character phase")
                rows.append([row, column, mask, coefficient])
    return sorted(rows)


def specialize(rows, exponents):
    require(len(exponents) == len(SITES) and all(type(x) is int for x in exponents),
            "five integer phase exponents")
    units = ((1, 0), (0, 1), (-1, 0), (0, -1))
    matrix = [[(0, 0) for _ in range(8)] for _ in range(8)]
    for row, column, mask, coefficient in rows:
        exponent = sum(exponents[index] for index in range(len(SITES)) if mask >> index & 1)
        real, imag = units[exponent % 4]
        before_real, before_imag = matrix[row][column]
        matrix[row][column] = (before_real + coefficient * real, before_imag + coefficient * imag)
    return matrix


def certify(context, blocks):
    expected_ranks = [[8, 48], [10, 48], [12, 48], [13, 48], [14, 1]]
    require([[child, len(context["residual"][child])] for child in SITES] == expected_ranks,
            "source residual ranks")
    for child in SITES:
        combined = context["hosted_axes"].get(child, []) + context["residual"][child]
        require(all((a & b).bit_count() % 2 == int(i == j)
                    for i, a in enumerate(combined) for j, b in enumerate(combined)),
                "hosted and residual axes form an orthonormal basis")
    matrix, peak = symbolic_replay(context, blocks)
    rows = normalized_rows(matrix)
    expected = [[0, 0, 8, 1], [0, 2, 0, -1], [0, 2, 8, 1], [1, 1, 4, 1],
                [2, 2, 0, 1], [3, 1, 4, 1], [3, 1, 16, -1], [3, 3, 16, 1],
                [4, 4, 0, 1], [5, 1, 0, 1], [5, 1, 16, -1], [5, 3, 0, -1],
                [5, 3, 16, 1], [5, 5, 0, 1], [6, 6, 1, 1], [7, 7, 2, 1]]
    require(rows == expected, "source-bound five-site matrix")
    identity = [[(int(row == column), 0) for column in range(8)] for row in range(8)]
    accepted = [list(values) for values in product(range(4), repeat=len(SITES))
                if specialize(rows, values) == identity]
    require(accepted == [[0, 0, 0, 0, 0]], "independent residual phase rigidity")
    return dict(schema=1, sites=list(SITES), ambient_bits=BITS, owner=0, port=0,
                residual_ranks=expected_ranks, polynomial_matrix=rows,
                character_dependent_terms=0,
                forcing_diagonal=[[8, 6], [10, 7], [12, 1], [13, 0], [14, 3]],
                exact_phase_assignments=dict(total=1024, accepted=len(accepted), accepted_exponents=accepted),
                peak_symbolic_terms=peak,
                rank_consequence="each selected residual rank is unchanged for independent replacement axes",
                rank_proof="uniform-character phase average has squared magnitude 2^(-rank)")


def build():
    _source, context, blocks = load_context()
    return certify(context, blocks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    receipt = build()
    if args.emit:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        require(receipt == json.loads((HERE / "RESULT.json").read_bytes()), "retained result mismatch")
        print("PASS_T740_ONE_DONOR_OPERATOR sites=5 ambient_bits=73 formal_terms=16 rank_change=0")


if __name__ == "__main__":
    main()
