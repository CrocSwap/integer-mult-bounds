"""Exact source, full-output codec, and Fourier-bound corroboration.

For @CubeJerry, substantial OpenAI Codex assistance. Apache-2.0.
The universal mathematical proof is PROOF.md; this is bounded validation.
"""
from copy import deepcopy
from itertools import product

import construction as c
import optimal_codec as o
import recovery as r


def source_checks(matrix):
    c.validate(matrix, *c.matrices())
    for i in range(112):
        x = [int(i == j) for j in range(112)]
        r.require(c.apply_u(c.apply_u(x), True) == x, "left frame inverse")
        r.require(c.apply_u(c.apply_u(x, True)) == x, "right frame inverse")
        r.require(c.project(matrix, c.apply_u(x)) == c.project(matrix, x),
                  "rank-four frame changed modes")
    return {"rank_four_basis_inverse_checks": 224}


def walsh_checks():
    points, tables = 0, set()
    for s in range(-208, 209):
        cells = o.joint_cells(s)
        counts = tuple(len(cells[p, q]) for p, q in product(range(2), repeat=2))
        tables.add(counts)
        for (a, b), bound in zip(((0, 0), (1, 0), (0, 1), (1, 1)),
                                 (169, 1, 13, 13)):
            value = sum((-1) ** (a * p + b * q) * len(cells[p, q])
                        for p, q in product(range(2), repeat=2))
            r.require(abs(value) <= bound, "absolute Fourier bound failed")
        points += sum(counts)
    r.require(len(tables) == 12, "scalar tie-table coverage changed")
    return {"walsh_scalar_parameters": 417, "walsh_scalar_points": points,
            "distinct_joint_tables": 12}


def zero_codec_checks(matrix):
    zero, offset, cases = [0] * 112, 0, 0
    parts = o.blocks(matrix, zero)
    r.require(len(parts) == 256, "rank-four code pair partition changed")
    for _, _, size in parts:
        tag = offset + size // 2
        x = o.decode(matrix, zero, tag)
        r.require(o.encode(matrix, x) == (zero, tag), "zero block roundtrip")
        offset += size
        cases += 1
    r.require(offset == o.max_states() == 2601832488601921,
              "sharp optimal-frame count changed")
    r.require((offset - 1).bit_length() == 52, "optimal packed width changed")
    return {"zero_code_pair_blocks": cases, "optimal_states": offset,
            "optimal_packed_bits": 52}


def arbitrary_codec_checks(matrix):
    outputs = set()
    for sample in range(48):
        x = [((sample + 3) * (i * i + 17) % 127) - 63 for i in range(112)]
        if sample == 47:
            x = [((-1) ** i) * (10 ** 30 + i) for i in range(112)]
        y, tag = o.encode(matrix, x)
        outputs.add(tuple(y))
        r.require(o.decode(matrix, y, tag) == x, "arbitrary output roundtrip")
        count = o.fiber_count(matrix, y)
        r.require(0 < count <= o.max_states(), "arbitrary output maximum")
        for edge in (0, count - 1):
            decoded = o.decode(matrix, y, edge)
            r.require(o.encode(matrix, decoded) == (y, edge),
                      "arbitrary output endpoint rank")
    r.require(len(outputs) == 48, "nonzero-output coverage collapsed")
    return {"distinct_arbitrary_outputs": len(outputs),
            "arbitrary_output_codec_roundtrips": 144}


def rejected(function, label):
    try:
        function()
    except ValueError:
        return 1
    raise ValueError("control was accepted: " + label)


def matrix_controls(matrix):
    e, v, ell = c.matrices()
    count = 0
    for name in ("kernel", "nilpotence", "dual", "quotient", "code"):
        ee, vv, ll = deepcopy((e, v, ell))
        if name == "kernel":
            vv[64][0] = 2
        elif name == "nilpotence":
            ee[0][64] = 1
        elif name == "dual":
            ll[0][0] = 1
        elif name == "quotient":
            for row in vv:
                row[1] = row[0]
        else:
            ee[3] = list(ee[0])
        count += rejected(lambda: c.validate(matrix, ee, vv, ll), name)
    return count


def controls(matrix):
    zero = [0] * 112
    cases = [(lambda: o.decode(matrix, zero, -1), "negative tag"),
             (lambda: o.decode(matrix, zero, o.max_states()), "large tag"),
             (lambda: o.decode(matrix, zero, True), "Boolean tag"),
             (lambda: o.encode(matrix, [0.0] * 112), "inexact input"),
             (lambda: c.inverse_from_total(matrix, zero, [1] + [0] * 7),
              "nonintegral total")]
    count = matrix_controls(matrix)
    count += sum(rejected(function, label) for function, label in cases)
    cells = o.joint_cells(2)
    r.require(min(map(len, cells.values())) > 36,
              "false entrywise-domination negative control disappeared")
    unreachable = [0] * 112
    unreachable[3] = 1
    r.require(o.fiber_count(matrix, unreachable) == 0,
              "outside-image output accepted")
    return {"optimal_rejecting_controls": count + 2}


def output_contract_checks(matrix):
    mode = matrix[0]
    numerator = [-13 * value for value in c.lift(matrix, mode)]
    numerator[0] += 52
    r.require(all(value % 2 == 0 for value in numerator), "reachable witness parity")
    x = [value // 2 for value in numerator]
    h = [52 * int(i == 0) for i in range(112)]
    r.require(c.kernel(matrix, numerator) == h, "first native output witness")
    restored = c.apply_u(c.forward(matrix, x), True)
    baseline = c.kernel(matrix, h)
    gram_column = [sum(a * b for a, b in zip(matrix[i], mode))
                   for i in c.SELECTORS]
    r.require(gram_column == [4, 2, 2, 2], "selected Gram witness")
    expected = [0] * 112
    for coefficient, column in zip(gram_column, c.COLUMNS):
        for i, value in column:
            expected[i] += coefficient * value
    r.require([a - b for a, b in zip(restored, baseline)] == expected,
              "inverse frame silently restored baseline output")
    r.require(any(expected) and max(map(abs, x)) == 13, "nonzero reachable defect")
    return {"reachable_output_contract_defect": gram_column,
            "reachable_witness_input_norm_infinity": 13}


def three_stage_control():
    results = []
    for s in (0, 2):
        value = 0
        lo, hi = r.quotient_interval(s)
        for q3 in range(lo, hi + 1):
            lo2, hi2 = r.quotient_interval(s + 56 * q3)
            for q2 in range(lo2, hi2 + 1):
                lo1, hi1 = r.quotient_interval(s + 56 * (q2 + q3))
                value += (-1) ** (q2 + q3) * (hi1 - lo1 + 1)
        results.append(value)
    r.require(results == [13, -14], "three-stage method boundary changed")
    return {"three_stage_character_011_at_s0_s2": results}


def observer_checks(matrix):
    gram = [[sum(a * b for a, b in zip(matrix[i], matrix[j]))
             for j in c.SELECTORS] for i in c.SELECTORS]
    expected = [[2 + 2 * int(i == j) for j in range(4)] for i in range(4)]
    r.require(gram == expected, "observer spanning Gram changed")
    for column, source in enumerate(c.SELECTORS):
        x = [26 * int(i == source) for i in range(112)]
        h = c.kernel(matrix, [2 * a for a in x])
        expected_column = [52 * int(i == column) - gram[i][column]
                           for i in range(4)]
        r.require([h[i] for i in c.SELECTORS] == expected_column,
                  "observer witness does not span")
        baseline = c.kernel(matrix, h)
        changed = c.forward(matrix, x)
        r.require(c.project(matrix, changed) == c.project(matrix, baseline),
                  "mode observer changed")
    return {"linear_observer_spanning_inputs": 4,
            "linear_observer_spanning_determinant": 42 * 50 ** 3}


def checks(matrix):
    report = {}
    for check in (source_checks, zero_codec_checks, arbitrary_codec_checks,
                  controls, output_contract_checks, observer_checks):
        report.update(check(matrix))
    report.update(walsh_checks())
    report.update(three_stage_control())
    return report
