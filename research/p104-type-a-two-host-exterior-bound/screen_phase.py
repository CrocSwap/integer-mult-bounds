# SPDX-License-Identifier: Apache-2.0
"""Check the exterior support of both fixed host write axes at exact phases."""
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import runpy
import sys


def rank_complex(rows, rank_rational):
    realified = [
        [part for value in row for part in (value[0], -value[1])]
        for row in rows
    ] + [
        [part for value in row for part in (value[1], value[0])]
        for row in rows
    ]
    result = rank_rational(realified)
    assert result % 2 == 0
    return result // 2


def exterior_certificate(augmented, row_ids, output_ids, rank_rational):
    columns = list(zip(*augmented, strict=True))
    keep = []
    for j, column in enumerate(columns):
        candidate = [columns[k] for k in keep] + [column]
        if rank_complex(candidate, rank_rational) > len(keep):
            keep.append(j)
    assert keep[:len(output_ids)] == list(range(len(output_ids))) and len(keep) == 6
    assert len(output_ids) == 4
    chosen = []
    for i, row in enumerate(augmented):
        candidate = chosen + [i]
        values = [[augmented[k][j] for j in keep] for k in candidate]
        if rank_complex(values, rank_rational) > len(chosen):
            chosen = candidate
    assert len(chosen) == 6
    matrix = [[augmented[i][j] for j in keep] for i in chosen]
    return {
        "rows": [row_ids[i] for i in chosen],
        "transport_columns": output_ids,
        "required_minus_transport_columns": [j - len(output_ids) for j in keep[len(output_ids):]],
        "matrix_real_imag_pairs": [[[str(real), str(imag)] for real, imag in row] for row in matrix],
        "complex_rank": rank_complex(matrix, rank_rational),
    }


def rotate(value, quarter_turns):
    r, i = value
    return ((r, i), (-i, r), (-r, -i), (i, -r))[quarter_turns % 4]


def direct_unit_i(events, clocks, vector, *, demote=(), undo=False):
    """Independent Gaussian-rational walk at q=i with unit bodies."""
    state = vector.copy()
    direction = -1 if undo else 1

    def add(dest, source, factor, turn=0):
        r, i = rotate(state[source], turn)
        a, b = state[dest]
        state[dest] = a + direction * factor * r, b + direction * factor * i

    for clock in reversed(clocks) if undo else clocks:
        kind, op, *args = events[clock]
        if kind == "B":
            continue
        if kind == "J":
            x, y, u, v = args[0]
            add(y, x, 1, -1)
            add(u, v, -1, 1)
            continue
        assert kind == "A"
        dest, *params = args
        if op == "ADD":
            add(dest, params[0], Fraction(params[1]))
        elif op == "QUERY":
            add(dest, params[0], 1, 0 if clock in demote else params[1])
        elif op == "SCALE":
            scale = Fraction(params[0])**direction
            state[dest] = tuple(scale * x for x in state[dest])
        elif op == "SWAP":
            src = params[0]
            state[dest], state[src] = state[src], state[dest]
        elif op == "LAMBDA":
            state[dest] = rotate(state[dest], direction * params[0])
        else:
            assert op == "IDLE_ONE"
    return state


def exterior_quotient(caller, before, middle, after, m, t, tools):
    paired_rows = ((1, 10), (19, 28))
    hosted = tools["A"]
    probes = tools["ROOTS"]
    for column in (*hosted, *probes):
        e = [(Fraction(j == column), Fraction()) for j in range(tools["N"])]
        original = caller["events"]
        x = direct_unit_i(original, before, e, undo=True)
        desired = [value if j in probes else rotate(value, -1) for j, value in enumerate(x)]
        t_col = direct_unit_i(original, after, desired, undo=True)
        m_col = direct_unit_i(original, middle, e, demote=tools["DEMOTED"])
        assert m_col == [row[column] for row in m]
        assert t_col == [row[column] for row in t]
    observed = []
    for a, b in paired_rows:
        assert a not in tools["B"] and b not in tools["B"]
        assert all(m[a][j] == m[b][j] for j in hosted)
        values = []
        for j in probes:
            values.append(tuple((t[a][j][k] - m[a][j][k]) - (t[b][j][k] - m[b][j][k])
                                for k in range(2)))
        observed.append(values)
    assert observed == [[(2, -2), (0, 0)], [(0, 0), (2, -2)]]
    return {
        "output_row_differences": [list(pair) for pair in paired_rows],
        "target_input_columns": list(probes),
        "required_quotient_real_imag": [[[str(r), str(i)] for r, i in row] for row in observed],
        "quotient_determinant": "-8i",
        "independent_direct_walk": "Transport and target columns agree with the pinned Laurent engine",
    }


def specialization(caller, data, phase, negated_bodies, tools):
    events = caller["events"]
    before, middle, after = tools["retiming"](events)
    timed = before + [tools["J8"]] + middle + [tools["J9"]] + after
    word, _ = tools["laurent_engine"](data)
    engine = runpy.run_path(str(data))
    zero = engine["ZERO"]

    def compile_value(clocks, demote=False):
        return [
            (op, d, s, c * (-1) ** sum(b[j - 1] for j in negated_bodies), t, zero)
            for op, d, s, c, t, b in word(caller, clocks, phase, demote)
        ]

    def apply(gates, column, undo=False):
        return engine["apply"](gates, [entry.copy() for entry in column], undo=undo)

    def spin(turn):
        return {(turn % 2, zero): Fraction(-1 if turn % 4 >= 2 else 1)}

    def pair(value):
        return value.get((0, zero), Fraction()), value.get((1, zero), Fraction())

    def diag(values, original):
        result = []
        for j, source in enumerate(values):
            power, lam, *body_mask = caller["types"]["A"]["diagonal"][j]
            assert (power, lam) == (-1, 0)
            sign = (-1) ** sum(body_mask[k - 1] for k in negated_bodies)
            phase_power = phase * power if original or j not in tools["ROOTS"] else 0
            value = {}
            engine["add_scaled"](value, source, Fraction(sign), phase_power)
            result.append(value)
        return result

    original = compile_value(range(len(events)))
    retimed = compile_value(timed)
    pre = compile_value(before)
    mid = compile_value(middle, demote=True)
    post = compile_value(after)
    before8 = tools["A"]
    after9 = tools["B"]
    outside8 = [i for i in range(tools["N"]) if i not in before8]
    outside9 = [i for i in range(tools["N"]) if i not in after9]
    cols_m, cols_t = [], []
    for j in range(tools["N"]):
        e = [{} for _ in range(tools["N"])]
        e[j] = spin(0)
        assert apply(original, e) == apply(retimed, e) == diag(e, original=True)
        cols_m.append(list(map(pair, apply(mid, e))))
        wanted = diag(apply(pre, e, undo=True), original=False)
        cols_t.append(list(map(pair, apply(post, wanted, undo=True))))
    m = list(zip(*cols_m, strict=True))
    t = list(zip(*cols_t, strict=True))
    residual = [[(u[0] - v[0], u[1] - v[1]) for u, v in zip(a, b, strict=True)]
                for a, b in zip(t, m, strict=True)]
    projection = [list(m[i][j] for j in before8) for i in outside9]
    augmented = [base + residual[i] for base, i in zip(projection, outside9, strict=True)]
    corner = [[residual[i][j] for j in outside8] for i in outside9]
    rational = tools["rank"]
    result = {
        "q_i_power": phase,
        "negated_bodies": negated_bodies,
        "matched_original_and_retimed_columns": tools["N"],
        "transport_rank_on_fixed_J8_outputs": rank_complex(projection, rational),
        "rank_after_adding_required_exterior": rank_complex(augmented, rational),
        "outside_J8_input_residual_rank": rank_complex(corner, rational),
    }
    if phase == 1 and not negated_bodies:
        assert result["transport_rank_on_fixed_J8_outputs"] == 4
        assert result["rank_after_adding_required_exterior"] == 6
        result["exterior_rank_six_certificate"] = exterior_certificate(augmented, outside9, before8, rational)
        result["exterior_quotient"] = exterior_quotient(caller, before, middle, after, m, t, tools)
    return result


def main():
    local = Path(__file__).with_name("screen.py")
    tools = runpy.run_path(str(local))
    source = Path(sys.argv[1])
    for path, digest in tools["SOURCES"].items():
        assert sha256((source / path).read_bytes()).hexdigest() == digest, path
    caller = json.loads((source / "inputs/CALLER.json").read_bytes())
    data = source / "inputs/full_body.py"
    cases = product(range(4), ((), (8,), (9,)))
    result = [specialization(caller, data, phase, bodies, tools) for phase, bodies in cases]
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
