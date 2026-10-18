#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 thakrarsagar. Developed with substantial OpenAI Codex assistance.
"""Exact all-character, all-twenty-site phase map and its rational inverse.

The authenticated source projection and phase replay adapt the attributed
PR3272 certificate; this package proves a full nonzero-parameter inverse.
"""

import argparse
from collections import defaultdict
import hashlib
from fractions import Fraction
import sys
import json
from pathlib import Path
from types import ModuleType

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/idle-star-paired-axis-census"
ALLOCATION = "research/rank7-joint-endframes/allocation"
PHASES = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
BITS = 73
SITES = tuple(range(20))
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


def normalized_rows(matrix, q=11):
    """Retain the only two ambient phases: 1 and g=i^(-parity(q & chi))."""
    phase_types = {ZERO_PHASE: 0, phase_scale(phase_axis(q), -1): -1}
    rows = []
    for row, entries in enumerate(matrix):
        for column, entry in enumerate(entries):
            phases = set()
            for (mask, low, high, cross), coefficient in entry.items():
                phase = (low, high, cross)
                require(phase in phase_types, "unexpected ambient phase")
                phases.add(phase)
                rows.append([row, column, mask, phase_types[phase], coefficient])
            require(len(phases) <= 1, "one common ambient factor per matrix entry")
    return sorted(rows)


class Laurent:
    """Sparse exact Laurent polynomials in z0,...,z19,g.

    Division is permitted only by a nonzero monomial. Each actual denominator
    in the inverse simplifies to such a monomial; this is checked, not assumed.
    """
    ZERO = (0,) * 21

    def __init__(self, terms):
        self.terms = {key: Fraction(value) for key, value in terms.items() if value}

    @classmethod
    def constant(cls, value):
        return cls({cls.ZERO: value})

    @classmethod
    def variable(cls, index):
        powers = list(cls.ZERO)
        powers[index] = 1
        return cls({tuple(powers): 1})

    @classmethod
    def cast(cls, value):
        return value if isinstance(value, cls) else cls.constant(value)

    def __add__(self, other):
        other = self.cast(other)
        terms = self.terms.copy()
        for key, value in other.terms.items():
            terms[key] = terms.get(key, 0) + value
        return Laurent(terms)

    __radd__ = __add__

    def __neg__(self):
        return Laurent({key: -value for key, value in self.terms.items()})

    def __sub__(self, other):
        return self + -self.cast(other)

    def __rsub__(self, other):
        return self.cast(other) + -self

    def __mul__(self, other):
        other = self.cast(other)
        terms = defaultdict(Fraction)
        for a, x in self.terms.items():
            for b, y in other.terms.items():
                terms[tuple(i + j for i, j in zip(a, b))] += x * y
        return Laurent(terms)

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = self.cast(other)
        require(len(other.terms) == 1, "inverse denominator must be a nonzero monomial")
        (powers, coefficient), = other.terms.items()
        return Laurent({tuple(a - b for a, b in zip(key, powers)): value / coefficient
                        for key, value in self.terms.items()})

    def __eq__(self, other):
        return self.terms == self.cast(other).terms


def polynomial_matrix(rows):
    matrix = [[Laurent.constant(0) for _ in range(8)] for _ in range(8)]
    for row, column, mask, ambient, coefficient in rows:
        require(ambient in (0, -1), "ambient factor convention")
        powers = tuple((mask >> index) & 1 for index in SITES) + (-ambient,)
        matrix[row][column] += Laurent({powers: coefficient})
    return matrix


def inverse(matrix, g):
    """Twenty-entry inverse; defined on every image of nonzero z and g."""
    m = matrix
    z = [None] * 20
    z[13], z[12] = m[0][0], m[1][1]
    z[0] = (m[0][2] + m[2][2]) / z[13]
    z[1] = 1 + m[1][2] / (g * z[0] * z[12])
    z[15] = m[2][2] / (z[0] * z[1])
    u = z[12] - m[3][1]
    z[14] = m[3][0] / g + u
    z[3] = u / z[14]
    z[2] = m[3][3] / u
    z[4] = (m[4][4] - m[0][4]) / z[15]
    z[5] = 1 + m[3][4] / (g * z[4] * z[14])
    z[17] = m[4][4] / (z[4] * z[5])
    p = m[5][1] / z[3] + z[14]
    z[16] = (m[5][2] / (g * z[0]) - z[14] * (1 - z[1]) + p) / z[1]
    z[7] = p / z[16]
    z[6] = m[5][5] / p
    z[8] = (m[0][6] + m[6][6]) / z[17]
    z[9] = 1 + m[5][6] / (g * z[8] * z[16])
    z[19] = m[6][6] / (z[8] * z[9])
    p = z[16] - m[7][1] / (z[3] * z[7])
    z[18] = (m[7][4] / (g * z[4]) - z[16] * (1 - z[5]) + p) / z[5]
    z[11] = p / z[18]
    z[10] = m[7][7] / p
    require(all(value != 0 for value in z), "inverse requires nonzero phases")
    return z


def certify(context, blocks):
    require(context["recipe"]["q"] == 11, "source ambient phase vector")
    ranks = [[child, len(context["residual"][child])] for child in SITES]
    require(ranks == [[child, {4: 1, 6: 1, 8: 48, 10: 48, 12: 48, 13: 48,
                              14: 1, 15: 1}.get(child, 0)] for child in SITES],
            "source residual ranks")
    for child in SITES:
        combined = context["hosted_axes"].get(child, []) + context["residual"][child]
        require(all((a & b).bit_count() % 2 == int(i == j)
                    for i, a in enumerate(combined) for j, b in enumerate(combined)),
                "source hosted and residual axes form an orthonormal basis")
    raw, peak = symbolic_replay(context, blocks)
    rows = normalized_rows(raw)
    matrix = polynomial_matrix(rows)
    recovered = inverse(matrix, Laurent.variable(20))
    require(recovered == [Laurent.variable(index) for index in SITES],
            "exact Laurent-polynomial inverse identity")
    baseline = [[defaultdict(int) for _ in range(8)] for _ in range(8)]
    for row, column, _mask, ambient, coefficient in rows:
        baseline[row][column][ambient] += coefficient
    for row in range(8):
        for column in range(8):
            value = {phase: coefficient for phase, coefficient in baseline[row][column].items()
                     if coefficient}
            require(value == ({0: 1} if row == column else {}), "baseline identity")
    require(len(rows) == peak == 72, "full word term count")
    return {
        "schema_version": 1, "owner": 0, "port": 0, "ambient_bits": BITS,
        "sites": list(SITES), "residual_ranks": ranks,
        "polynomial_matrix": rows, "peak_symbolic_terms": peak,
        "matrix_terms": len(rows), "ambient_phase_vector": 11,
        "inverse_checked_sites": len(recovered), "inverse_entry_count": 20,
        "baseline_identity": True,
    }


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
        require(receipt == json.loads((HERE / "RESULT.json").read_bytes()),
                "retained result mismatch")
        print("PASS_T740_COMPLETE_PHASE_MAP sites=20 terms=72 inverse=20")


if __name__ == "__main__":
    main()
