#!/usr/bin/env python3
"""Check all scalar centre maps against the supplied response space."""

import ast
import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path


if not __debug__:
    raise RuntimeError("Run without -O; this checker uses assertions.")


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
SPACE = LANES / "oblique-native-20261017/interior-cut/RESPONSE-SPACE.json"
CUT = LANES / "new-core-transfer-20261017/CUT-PROBE.json"
CORE = LANES / "new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz"
PRIME = 1000003


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mod(value):
    value = Fraction(value)
    return value.numerator * pow(value.denominator, -1, PRIME) % PRIME


def add(dst, src, factor):
    for key, value in src.items():
        result = (dst.get(key, 0) + factor * value) % PRIME
        if result:
            dst[key] = result
        else:
            dst.pop(key, None)


def insert(basis, row):
    row = dict(row)
    while row:
        pivot = min(row)
        if pivot not in basis:
            factor = pow(row[pivot], -1, PRIME)
            basis[pivot] = {key: value * factor % PRIME
                            for key, value in row.items()}
            return True
        add(row, basis[pivot], -row[pivot])
    return False


def reduce_by(basis, row):
    row = dict(row)
    result = {}
    while row:
        pivot = min(row)
        if pivot not in basis:
            result[pivot] = row.pop(pivot)
        else:
            add(row, basis[pivot], -row[pivot])
    return result


def nullspace(basis, size):
    result = []
    for free in range(size):
        if free in basis:
            continue
        row = {free: 1}
        for pivot, equation in sorted(basis.items(), reverse=True):
            value = -sum(c * row.get(k, 0)
                         for k, c in equation.items() if k != pivot) % PRIME
            if value:
                row[pivot] = value
        result.append([row.get(k, 0) for k in range(size)])
    return result


def exact_add(dst, src, factor):
    for key, value in src.items():
        result = dst.get(key, 0) + factor * value
        if result:
            dst[key] = result
        else:
            dst.pop(key, None)


def y_port(field):
    return field[1] - 112 if field[0] == "L" and 112 <= field[1] < 224 else None


def original_equations(item, r):
    word, program = item["canonical"], item["programs"]["forward"]
    n = len(word["start"])
    columns = [{i: Fraction(1)} for i in range(112)]
    tails = {}
    for position in range(len(program) - 1, -1, -1):
        event = program[position]
        if event[0] != "scalar":
            continue
        op = event[1]
        target = y_port(op[1])
        if op[0] == "add":
            source = y_port(op[2])
            assert source is None or target is not None
            if target is not None:
                if source is None:
                    tails[position] = dict(columns[target])
                else:
                    exact_add(columns[source], columns[target], Fraction(*op[3:5]))
        elif target is not None:
            assert op[0] == "scale"
            columns[target] = {key: Fraction(*op[2:4]) * value
                               for key, value in columns[target].items()}
    assert columns == [{i: 1} for i in range(112)]
    fields = [("L", i) for i in range(n)] + [("C", i) for i in range(8)]
    state = {field: {(field, ()): Fraction(1)} for field in fields}
    frames = {("L", i): f for i, f in enumerate(word["start"])}
    frames.update({("C", i): 0 for i in range(8)})
    allowed = {("L", i) for i in range(224, n) if word["start"][i] == 0}
    sources = {}
    zero = set()
    for position, event in enumerate(program):
        tag = event[0]
        if tag == "scalar":
            op, frame = event[1:]
            target = tuple(op[1])
            if op[0] == "clear":
                state[target], frames[target] = {}, frame
            else:
                assert frames[target] == frame
                if op[0] == "scale":
                    state[target] = {key: Fraction(*op[2:4]) * value
                                     for key, value in state[target].items()}
                else:
                    source = tuple(op[2])
                    assert frames[source] == frame and source != target
                    if position in tails:
                        sources[position] = dict(state[source])
                    if op[0] == "copy":
                        state[target] = dict(state[source])
                    else:
                        assert op[0] == "add"
                        exact_add(state[target], state[source], Fraction(*op[3:5]))
        elif tag == "climb":
            target = ("L", event[2])
            assert frames[target] == event[3]
            assert len(word["frames"][event[4]]) - len(word["frames"][event[3]]) == event[5]
            frames[target] = event[4]
        elif tag == "warp":
            target, symbol = tuple(event[1]), event[2]
            assert y_port(target) is None and frames[target] == event[3]
            frames[target] = event[4]
            state[target] = {
                (source, history[:-1] if history and history[-1] == -symbol
                 else history + (symbol,)): value
                for (source, history), value in state[target].items()}
        elif tag == "zero_buffer":
            target = ("Z", event[2])
            if event[1] == "alloc":
                assert target not in zero
                state[target], frames[target] = {}, 1
                zero.add(target)
            else:
                assert target in zero and not state[target]
                zero.remove(target)
        else:
            assert tag in ("phase", "adapter", "residual_adapter")
    assert not zero
    assert [frames["L", i] for i in range(n)] == word["final"]
    assert all(frames["C", i] == 0 for i in range(8))
    assert not state["C", 0]
    assert all(state["C", i] == {(("C", i), ()): 1} for i in range(1, 8))
    for p in range(112):
        assert state["L", p] == {(("L", p), ()): 1}
        goal = {(("L", 112+p), ()): Fraction(1), (("L", p), ()): Fraction(1)}
        for row in r:
            for s, value in row.items():
                exact_add(goal, {(("L", s), ()): value}, -row.get(p, 0) / 4)
        assert state["L", 112+p] == goal
    assert all(state["L", p] == {(("L", p), ()): 1} for p in range(224, n))
    active = sorted(pos for pos, source in sources.items()
                    if any(field not in allowed or history for field, history in source))
    equations = {}
    for col, pos in enumerate(active):
        for t, tc in tails[pos].items():
            for (field, history), sc in sources[pos].items():
                if field in allowed and not history:
                    continue
                if field[0] == "L" and field[1] < 112 and not history:
                    if t == field[1]:
                        continue
                    key = ("data", t, field[1])
                else:
                    key = ("other", t, field, history)
                exact_add(equations.setdefault(key, {}), {col: tc * sc}, 1)
    for a in range(8):
        for b in range(8):
            col = len(active) + 8*a + b
            for t, tc in r[a].items():
                for s, sc in r[b].items():
                    if t != s:
                        exact_add(equations.setdefault(("data", t, s), {}),
                                  {col: tc * sc / 4}, 1)
    witness = [Fraction(*program[pos][1][3:5]) for pos in active]
    witness += [Fraction(a == b) for a in range(8) for b in range(8)]
    assert all(sum(value*witness[col] for col, value in row.items()) == 0
               for row in equations.values())
    x_warp_terms = sum(field[0] == "L" and field[1] < 112 and bool(history)
                       for pos in active for field, history in sources[pos])
    return active, equations, witness, x_warp_terms


def main():
    assert digest(SPACE) == "320e25fec5c0f52285aa2e945b2e0f30d43e2504de207595b0f35ec93bab7337"
    assert digest(CUT) == "78c9c2f87d0ae5c345e5ae467f94a92f94c97d618b3011e436c0dc94c3b15cbc"
    supplied = json.loads(SPACE.read_text())
    source = json.loads(CUT.read_text())
    r = [{int(k): Fraction(v) for k, v in row.items()}
         for row in source["base"]["center_R"]]
    assert source["base"]["center_R"] == source["extra"]["center_R"]
    basis = {}
    for item in supplied["directions"]:
        row = {ast.literal_eval(k): v % PRIME for k, v in item["effect"].items()}
        assert not any(t == s for t, s in row)
        assert insert(basis, row)
    assert len(basis) == 413
    equations = {}
    sizes = []
    for a in range(8):
        for b in range(8):
            row = {(t, s): mod(tc * sc / 4)
                   for t, tc in r[a].items() for s, sc in r[b].items() if t != s}
            remainder = reduce_by(basis, row)
            sizes.append(len(remainder))
            for key, value in remainder.items():
                equations.setdefault(key, {})[8 * a + b] = value
        print("centre row", a, "complete", flush=True)
    constraints = {}
    for key in sorted(equations):
        insert(constraints, equations[key])
    kernels = nullspace(constraints, 64)
    print("quotient rank", len(constraints), "kernel dimension", len(kernels), flush=True)
    identity = [int(a == b) for a in range(8) for b in range(8)]
    assert kernels == [identity]
    data = gzip.decompress(CORE.read_bytes())
    assert hashlib.sha256(data).hexdigest() == "a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa"
    core = json.loads(data)
    original_reports = {}
    first_equations = None
    for name, item in core["providers"].items():
        active, native_equations, witness, x_warp_terms = original_equations(item, r)
        assert active == supplied["active_sites"]
        native_basis = {}
        selected_rows = []
        for key in sorted(native_equations):
            if insert(native_basis, {col: mod(value) for col, value in native_equations[key].items()}):
                selected_rows.append(key)
        assert len(native_basis) == len(active) + 63 == 888
        kernel = nullspace(native_basis, len(active) + 64)
        assert len(kernel) == 1 and kernel[0] == [mod(value) for value in witness]
        if first_equations is not None:
            assert native_equations == first_equations
        first_equations = native_equations
        data_site_basis, data_combined_basis = {}, {}
        for key in sorted(native_equations):
            if key[0] != "data":
                continue
            equation = {col: mod(value) for col, value in native_equations[key].items()}
            insert(data_site_basis, {col: value for col, value in equation.items() if col < len(active)})
            insert(data_combined_basis, equation)
        original_reports[name] = {
            "variables": len(active) + 64,
            "equations": len(native_equations),
            "rank_mod_prime": len(native_basis),
            "exact_rational_witness": "The original clean-J cross-site coefficients and A=I8.",
            "exact_rational_nullity": 1,
            "scalar_frame_checks": True,
            "all_input_column_checks": len(item["canonical"]["start"]) + 8,
            "source_X_warp_term_count": x_warp_terms,
            "plain_data_site_rank": len(data_site_basis),
            "plain_data_combined_rank": len(data_combined_basis),
            "pivot_columns": sorted(native_basis),
            "independent_equation_keys": selected_rows,
        }
        print(name, "original equation rank", len(native_basis), "exact nullity 1", flush=True)
    result = {
        "inputs": {str(SPACE.relative_to(LANES)): digest(SPACE),
                   str(CUT.relative_to(LANES)): digest(CUT)},
        "prime": PRIME,
        "response_dimension": len(basis),
        "centre_parameter_count": 64,
        "quotient_rank": len(constraints),
        "admissible_basis": [
            [[x if x <= PRIME // 2 else x - PRIME for x in v[8*a:8*a+8]]
             for a in range(8)] for v in kernels],
        "elementary_residual_sizes": [sizes[8*a:8*a+8] for a in range(8)],
        "original_equation_checks": original_reports,
        "clean_core_decompressed_sha256": hashlib.sha256(data).hexdigest(),
        "scope": "Constant scalar centre maps and existing cross sites, with coefficientwise formal operator-word cancellation. The original rational equation matrix has nullity one."
    }
    (HERE / "MIXING.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
