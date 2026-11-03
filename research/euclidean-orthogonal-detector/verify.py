"""Finite exact corroboration of the new guard, without predecessor imports.

This contribution was produced by Nick Petalas. Apache-2.0.
"""

import ast
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from guard import Step, allocate, ceil_log2, need, prefix_error, validate
from linear import cayley, checked_traces, check_matrices, exact_trace, rounded_trace


def squared_norm(row):
    return sum((value * value for value in row), Q(0))


def compare_rows(expected, actual, bound):
    need(len(expected) == len(actual), "returned role count")
    for left, right in zip(expected, actual):
        error = [a - b for a, b in zip(left, right)]
        need(squared_norm(error) <= bound * bound, "Euclidean error envelope")


def run_case(program, matrices, parameter, initial, radius):
    dimension, roles = len(initial[0]), len(initial)
    need(all(squared_norm(row) <= radius * radius for row in initial), "input norm")
    plan = allocate(program, dimension, roles, len(matrices), parameter, radius)
    traces = checked_traces(program, matrices, initial, plan["bits"])
    prefixes = coordinates = 0
    endpoints = []
    for side, (exact, rounded) in zip(program, traces):
        for index, (expected, actual) in enumerate(zip(exact, rounded)):
            bound = prefix_error(side[:index + 1], dimension, radius, plan["bits"])
            compare_rows(expected, actual, bound)
            prefixes += 1
            coordinates += roles * dimension
        endpoints.append((exact[-1] if exact else initial,
                          rounded[-1] if rounded else initial))
    for role in range(roles):
        for coordinate in range(dimension):
            value = endpoints[0][0][role][coordinate] - endpoints[1][0][role][coordinate]
            rounded = endpoints[0][1][role][coordinate] - endpoints[1][1][role][coordinate]
            need(abs(value - rounded) <= plan["error"], "complete difference error")
            need(value == 0 or abs(value) >= plan["eta"], "fixture separation")
            need((abs(rounded) > plan["eta"] / 2) == (value != 0), "endpoint decision")
    return prefixes, coordinates


def programs():
    apply = tuple(Step("apply", 0, label=i % 2, direction=1) for i in range(12))
    closed = apply + tuple(Step("apply", 0, label=step.label, direction=-1)
                           for step in reversed(apply))
    return (
        (apply, ()),
        (closed, ()),
        ((Step("apply", 0), Step("apply", 0, label=1)),
         (Step("apply", 0, label=1), Step("apply", 0))),
        ((Step("query", 1, src=0, coefficient=Q(2, 3)),
          Step("query", 1, src=1, label=1, direction=-1, coefficient=Q(-3, 2)),
          Step("linear", 2, terms=((1, Q(5, 7)), (2, Q(-1)), (1, Q(-2, 7)))),
          Step("apply", 2, label=1)),
         (Step("query", 2, src=0, direction=-1, coefficient=Q(1, 5)),)),
        ((Step("linear", 0, terms=((0, Q(1 << 40)), (1, Q(1, 1 << 40)))),
          Step("query", 0, src=0, label=1, coefficient=Q(-1, 3)),
          Step("apply", 0, direction=-1)),
         (Step("linear", 0, terms=((0, Q(1 << 40)),)),)),
        ((Step("linear", 1, terms=()), Step("query", 1, src=0, coefficient=Q(0))),
         (Step("linear", 1, terms=((0, Q(1, 3)), (0, Q(-1, 3)))),)),
        ((), ()),
    )


def finite_program_checks():
    count = prefixes = coordinates = dirty = 0
    for dimension in range(2, 8):
        word = tuple(i % 2 for i in range(dimension - 1))
        for parameter in (Q(1, 4), Q(1, 7)):
            matrices = cayley(word, 2, parameter)
            for program in programs():
                for input_column in range(3 * dimension):
                    initial = [[Q(int(i * dimension + j == input_column))
                                for j in range(dimension)] for i in range(3)]
                    new_prefixes, new_coordinates = run_case(program, matrices, parameter,
                                                             initial, Q(1))
                    count += 1
                    prefixes += new_prefixes
                    coordinates += new_coordinates
                initial = [[Q((i + 2 * j) % 7 - 3) for j in range(dimension)]
                           for i in range(3)]
                new_prefixes, new_coordinates = run_case(program, matrices, parameter,
                                                         initial, Q(3 * dimension))
                count += 1
                dirty += 1
                prefixes += new_prefixes
                coordinates += new_coordinates
    return dict(program_inputs=count, dirty_inputs=dirty,
                checked_prefixes=prefixes, checked_prefix_coordinates=coordinates)


def strict_fixture():
    dimension, parameter = 4, Q(1, 4)
    program = (tuple(Step("apply", 0, label=i % 2) for i in range(12)), ())
    matrices = cayley((0, 1, 0), 2, parameter)
    initial = [[Q(0), Q(0), Q(0), Q(1)]]
    plan = allocate(program, dimension, 1, 2, parameter)
    need(plan["bits"] == 182 and plan["old_bits"] == 228, "strict grid consequence")
    exact = exact_trace(program[0], matrices, initial)[-1]
    need(exact[0][0] != 0, "fixture must be a nonzero selected endpoint")
    for bits in (plan["bits"], plan["old_bits"]):
        actual = rounded_trace(program[0], matrices, initial, bits)[-1]
        compare_rows(exact, actual, plan["eta"] / 4)
        need(abs(actual[0][0]) > plan["eta"] / 2, "strict fixture detector")
    return dict(dimension=dimension, calls=12, parameter=str(parameter),
                old_bits=plan["old_bits"], new_bits=plan["bits"],
                saved_bits=plan["old_bits"] - plan["bits"],
                selected_exact_value=str(exact[0][0]),
                separation=str(plan["eta"]), error_bound=str(plan["error"]))


def product_bound_checks():
    count = 0
    for denominator in range(2, 17):
        for length in range(1, 17):
            amounts = [Q((i * 3 + length) % 7, 7 * length) for i in range(length)]
            total, product = sum(amounts, Q(0)), Q(1)
            h = Q(1, denominator)
            for amount in amounts:
                product *= 1 + h * amount
            need(product <= 1 / (1 - h * total), "finite product bound")
            count += 1
    for numerator in range(1, 257):
        requirement = Q(numerator, 7)
        bits = ceil_log2(requirement)
        need(Q(1 << bits) >= requirement, "precision upper rounding")
        need(bits == 0 or Q(1 << (bits - 1)) < requirement, "precision minimal integer")
    return dict(product_inequalities=count, precision_rounding_cases=256)


def reject_invalid(case):
    try:
        if case == 0:
            validate(((), ()), 0, 1, 1)
        elif case == 1:
            validate(((), ()), 17, 1, 1)
        elif case == 2:
            validate(((), ()), 2, 5, 1)
        elif case == 3:
            validate(((Step("apply", 1),), ()), 2, 1, 1)
        elif case == 4:
            validate(((Step("query", 0, src=1),), ()), 2, 1, 1)
        elif case == 5:
            validate(((Step("apply", 0, direction=0),), ()), 2, 1, 1)
        elif case == 6:
            validate(((Step("linear", 0, terms=((0, 0.5),)),), ()), 2, 1, 1)
        elif case == 7:
            validate(((Step("apply", 0),) * 65, ()), 2, 1, 1)
        elif case == 8:
            allocate(((), ()), 2, 1, 1, Q(1, 3))
        elif case == 9:
            allocate(((), ()), 2, 1, 1, Q(1, 4), Q(1, 2))
        elif case == 10:
            check_matrices([[[Q(2), Q(0)], [Q(0), Q(1)]]], 2)
        elif case == 11:
            rounded_trace((), [[[Q(1)]]], [[Q(1, 3)]], 10)
        elif case == 12:
            prefix_error((Step("apply", 0),), 4, Q(1), 0)
        else:
            validate(((Step("linear", 0, terms=((0, 1 << 129),)),), ()), 2, 1, 1)
    except ValueError:
        return
    raise ValueError(f"control {case} did not reject")


def semantic_controls():
    matrices = cayley((0,), 1, Q(1, 4))
    initial = [[Q(1024), Q(0)]]
    side = (Step("apply", 0),)
    exact = exact_trace(side, matrices, initial)[-1]
    rounded = rounded_trace(side, matrices, initial, 4)[-1]
    error = squared_norm([a - b for a, b in zip(exact[0], rounded[0])])
    need(error > Q(2, 16) ** 2, "omitted coefficient-quantization control")
    side = (Step("apply", 0), Step("apply", 0, direction=-1))
    exact = exact_trace(side, matrices, [[Q(1), Q(0)]])[-1]
    wrong = rounded_trace(side, matrices, [[Q(1), Q(0)]], 100, wrong_inverse=True)[-1]
    need(squared_norm([a - b for a, b in zip(exact[0], wrong[0])]) > Q(1, 8),
         "wrong inverse transpose control")
    alias = (Step("query", 0, src=0),)
    exact = exact_trace(alias, matrices, [[Q(1), Q(0)]])[-1][0]
    wrong_first = Q(1) + matrices[0][0][0]
    wrong_second = matrices[0][1][0] * wrong_first
    need(exact[1] != wrong_second, "old-value alias control")
    q, dimension = 12, 4
    eta = Q(1, 12 ** (q * dimension))
    need(Q(2 * q * (dimension + 2), 1 << 181) > eta / 4,
         "one fewer bit must fail the sufficient error inequality")
    return 4


def receipt():
    paths = sorted(path for path in ROOT.iterdir() if path.is_file())
    need(len(paths) == 8, "package file inventory")
    hashes = {}
    maximum_function = 0
    for path in paths:
        size = path.stat().st_size
        need(size <= 256 * 1024, "package source capacity")
        payload = path.read_bytes()
        hashes[path.name] = sha256(payload).hexdigest()
        if path.suffix == ".py":
            tree = ast.parse(payload, filename=path.name)
            compile(tree, path.name, "exec")
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    maximum_function = max(maximum_function, node.end_lineno - node.lineno + 1)
    need(maximum_function <= 60, "function inspection ceiling")
    return hashes, maximum_function


def main():
    result = finite_program_checks()
    result.update(product_bound_checks())
    result["strict_fixture"] = strict_fixture()
    for case in range(14):
        reject_invalid(case)
    result["invalid_controls"] = 14
    result["semantic_controls"] = semantic_controls()
    hashes, maximum = receipt()
    result.update(marker="PASS_EUCLIDEAN_ORTHOGONAL_DETECTOR",
                  python=platform.python_version(), implementation=platform.python_implementation(),
                  source_sha256=hashes, maximum_function_lines=maximum)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
