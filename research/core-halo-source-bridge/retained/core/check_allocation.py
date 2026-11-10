"""Independent exact admission audit of the prepared complete-Core interface.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
The producer prepares input-independent source objects. This audit reconstructs
the factor algebra, norms, residual constants, global grid and signed ranges
using independent rational matrix operations; no physical payload is supplied.
"""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
from pathlib import Path
import sys

from independent_numerics import (
    budget, canonical_json, ceil_div, ceil_log2, column_norm, five_factors,
    identity, inverse, multiply, need, pow2, row_norm,
)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def pad(matrix, block):
    n = len(matrix)
    extent = ceil_div(n, block) * block
    return tuple(tuple(matrix[i][j] if i < n and j < n else Q(i == j)
                       for j in range(extent)) for i in range(extent))


def reverse(matrix):
    return tuple(tuple(reversed(row)) for row in reversed(matrix))


def pass_constants(matrix, block, eta):
    matrix = pad(matrix, block)
    n = len(matrix)
    need(all(not matrix[i][j] or i // block - 1 <= j // block <= i // block
             for i in range(n) for j in range(n)), "actual adjacent-block source support")
    diagonal = max(row_norm(tuple(tuple(matrix[i][j] for j in range(k, k + block))
                                  for i in range(k, k + block)))
                   for k in range(0, n, block))
    preceding = max([Q()] + [row_norm(tuple(tuple(matrix[i][j] for j in range(k - block, k))
                                             for i in range(k, k + block)))
                             for k in range(block, n, block)])
    inv = row_norm(inverse(matrix))
    c0, c1 = diagonal * block + 2 * diagonal + 1, block * (diagonal * (preceding + 1) + 1)
    need(block * eta <= 1 and c0 * eta <= 1 and inv * c1 * eta <= Q(1, 2),
         "all actual completed-residual absorption admissions")
    return dict(diagonal=diagonal, preceding=preceding, inverse=inv, c0=c0, c1=c1,
                error_coefficient=inv * (c0 + 4 * inv * c1))


def audit_window(window, factors, supplied, lifted_block, plan):
    P, width, radius = plan["P"], plan["width"], plan["Rstar"]
    need(window.precision == P and window.width == width and window.radius == radius
         and window.target == plan["local_target"], "same actual sparse numerical descriptors")
    for name in ("A", "B", "C", "D", "F", "I", "J", "E"):
        need(getattr(window, name) == factors[name], "original-Q independent sparse factor: " + name)
    need(multiply(window.f_lower, window.f_upper) == factors["F"], "actual exact Schur LU factors")
    e = window.E
    N = tuple(tuple(window.H[i][j] if i in window.J and j in window.I else Q() for j in e)
              for i in e)
    need(window.N == N and multiply(N, N) == tuple(tuple(Q() for _ in e) for _ in e),
         "actual same-Reference lower coupling and square-zero mask")
    need(multiply(window.shear_lower, window.shear_upper) ==
         tuple(tuple(Q(i == j) + N[i][j] for j in range(len(e))) for i in range(len(e))),
         "actual exact shear factors")
    eta = pow2(1 - P)
    matrices = (window.shear_lower, reverse(pad(window.shear_upper, window.block)),
                window.f_lower, reverse(pad(window.f_upper, window.block)))
    passes = tuple(pass_constants(matrix, window.block, eta) for matrix in matrices)
    for actual, observed in zip(passes, window.pass_budgets):
        need(all(getattr(observed, name) == value for name, value in actual.items()),
             "independently recomputed actual inverse pass constants")
    s1, s2, f1, f2 = passes
    shear = eta * (s2["inverse"] * s1["error_coefficient"]
                   + 4 * s1["inverse"] * s2["error_coefficient"]) * radius
    solve_radius = (1 + row_norm(N)) * radius + shear
    f_error = eta * (f2["inverse"] * f1["error_coefficient"]
                     + 4 * f1["inverse"] * f2["error_coefficient"]) * solve_radius
    total = row_norm(inverse(factors["F"])) * shear + f_error
    need((shear, solve_radius, total) ==
         (window.shear_error, window.solve_input_radius, window.total_error),
         "actual staged errors include perturbed F-solve input")
    need(total <= pow2(-plan["local_target"]), "actual inverse local target")
    root = Q()
    for first, second, incoming in ((s1, s2, radius), (f1, f2, solve_radius)):
        for stats, value in ((first, incoming), (second, 4 * first["inverse"] * incoming)):
            M, c = stats["inverse"], stats["preceding"]
            root = max(root, value, 4 * M * value, 6 * M * (c + 1) * value,
                       value + (c + window.block * eta) * 4 * M * value + eta, M + 1, c + 1)
    need(root == window.root_record_radius and root < pow2(width - P - 1),
         "all actual inverse states, residuals and coefficients fit common signed width")
    upper = tuple(tuple(factors["factors"][3][i][j] for j in e) for i in e)
    need(supplied == upper, "supplied forward action is the actual upper E factor")
    lift = max(abs(2 * i - (2 * j + 1)) for i, row in enumerate(upper)
               for j, value in enumerate(row) if value)
    need(lift <= lifted_block and lifted_block == 1 << ceil_log2(max(2, lift)),
         "literal interleaved support and least checked forward block")
    s, gamma = max(sum(bool(x) for x in row) for row in upper), max(Q(1), row_norm(upper))
    need(Q(s * radius + 6, 1 << P) <= pow2(-plan["local_target"])
         and gamma * radius < pow2(width - P - 1), "actual forward error and carrier admission")
    return dict(inverse_block=window.block, forward_block=lifted_block,
                input_radius_bits=ceil_log2(radius), inverse_root_bits=ceil_log2(root),
                common_integer_bits=width - P - 1)


def audit(runtime, prepare, family, *, name, incoming=0):
    programs, windows, actions, blocks, plan = prepare.build_numeric(
        runtime, family, target=2, initial_radius_bits=0, h=2, incoming=incoming)
    K, g, side = len(family), len(family[0]), family[0][0].size
    n = K.bit_length() - 1 + g * (side.bit_length() - 1)
    independent = budget(n, g, 2, 2, incoming, 0)
    for key in ("n", "g", "h", "H", "target", "R0", "R2", "Rstar", "stage_target", "local_target", "V2"):
        need(plan[key] == independent[key], "complete global allocation: " + key)
    P, width, R2, td = plan["P"], plan["width"], plan["R2"], plan["stage_target"]
    rb = R2.bit_length() - 1
    need(P >= incoming and plan["incoming"] == P and plan["radius_bits"] == rb,
         "public input already uses the chosen common grid")
    need(width >= P + rb + 2, "common signed width covers every completed dense result")
    admissions = []
    for c, row in enumerate(family):
        for a, part in enumerate(row):
            original = tuple(tuple(part.reference.entry("narrow", part.first + i,
                                                       part.first + j).value
                                   for j in range(side)) for i in range(side))
            exact = five_factors(original, tuple(i for block in part.indices for i in block))
            need(windows[c][a].H == original, "unchanged Reference and original-coordinate source")
            need(all(max(row_norm(m), column_norm(m)) <= plan["h"] for m in exact["factors"]),
                 "rational row AND column bounds for every actual five-factor matrix")
            admissions.append(audit_window(windows[c][a], exact, actions[c][a], blocks[c][a], plan))
    for direction, program in zip((True, False), programs):
        need((program.labels, program.axes, program.size, program.array_bits, program.records) ==
             (K, g, side, n, 1 << n), "one complete global dense cohort")
        need(program.bits == program.incoming == P and program.radius == R2
             and program.target == td and program.norm_conversion == plan["V2"],
             "unchanged whole-field source radius, precision and global norm conversion")
        A, E, D, b = program.prefix, program.endpoint, program.diagonal_count, program.factor_bound + 1
        coefficient = 8 * E * D * A * A * g * b ** (g - 1) * R2
        rounding = 4 * E * A * D * plan["V2"]
        need((program.coefficient_constant, program.rounding_constant) == (coefficient, rounding),
             "complete coefficient and rounding constants include every context")
        minimum = max(P, 1, td + ceil_log2(4 * (coefficient + rounding)))
        arithmetic = (coefficient + rounding) * pow2(-P)
        need(P >= minimum and arithmetic == program.arithmetic_error
             and arithmetic <= pow2(-td - 2), "actual global dense grid minimum and arithmetic allowance")
        need(D * A * A * 4 * g * b ** (g - 1) * pow2(-P) <= Q(1, 2),
             "actual perturbed-prefix absorption")
        source_errors = []
        for c, raw_programs in enumerate(program.programs):
            endpoints = [part.lambdas[int(direction)] for part in reversed(family[c])]
            suffix = [Q(1)] * (g + 1)
            for a in reversed(range(g)):
                suffix[a] = endpoints[a] * suffix[a + 1]
            preceding, error = Q(1), Q()
            for a, raw in enumerate(raw_programs):
                error += preceding * raw.upstream_error * suffix[a + 1]
                preceding *= raw.endpoint
            source_errors.append(error)
        source_error = R2 * max(source_errors)
        need(source_error == program.source_error and source_error <= pow2(-td - 3)
             and program.total_error == source_error + arithmetic < pow2(-td),
             "unchanged complete source-accuracy admission, before all payloads")
        amplitude = 4 * A * (R2 + 1)
        need(program.data_width == P + ceil_log2(amplitude) + 2
             and program.factor_width == P + ceil_log2(b) + 2
             and program.cache_width == P + ceil_log2(2 * b ** g) + 2,
             "dense internal widths remain the actual source allocations")
        program.validate()
    return dict(name=name, contexts=K, axes=g, side=side, n=n, requested_incoming=incoming,
                P=P, width=width, W0=P + rb + 2, Wd=[p.data_width for p in programs],
                V2=plan["V2"], local_target=plan["local_target"],
                stage_target=td, source_admissions=admissions), (programs, windows, plan)


def rejects(call, phrase):
    try:
        call()
    except ValueError as error:
        need(phrase in str(error), "negative control failed at the intended source admission")
        return phrase
    raise ValueError("accepted inadmissible allocation: " + phrase)


def main():
    parser = ArgumentParser()
    parser.add_argument("--source-package", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    package = args.source_package.resolve()
    join = load("join_sources", package / "join_sources.py")
    with join.numerical() as runtime:
        adapter = load("admitted_context", package / "admitted_context.py")
        prepare = load("prepared_join", package / "prepared_join.py")
        source = __import__("source_window")
        reference = runtime.reference.Reference(runtime.raw, 7, 1, 2, 1, 3, 64)
        part = adapter.AdmittedPartition(runtime, reference, "narrow", 2, 2, 1, ((1,),))
        tiny = ((part,),)
        rows = []
        result, saved = audit(runtime, prepare, tiny, name="actual_scalar_interior_fixture")
        rows.append(result)
        result, _ = audit(runtime, prepare, tiny, name="incoming_grid_dominates", incoming=320)
        rows.append(result)
        references = tuple(runtime.reference.Reference(runtime.raw, 15, 1, alpha, 2, 3, 192)
                           for alpha in (2, 3))
        specs = (((0, 0), (1, 4)), ((1, 0), (0, 4)))
        family = tuple(tuple(adapter.AdmittedPartition(runtime, references[r], "narrow", origin,
                             4, 2, ((0, 1),)) for r, origin in row) for row in specs)
        result, _ = audit(runtime, prepare, family, name="global_nonidentity_interiors")
        rows.append(result)
        programs, windows, plan = saved
        controls = [rejects(lambda: prepare.build_numeric(runtime, tiny, h=1),
                            "actual source row and column norm bound"),
                    rejects(lambda: adapter.prepare(runtime, tiny, True,
                        target=plan["stage_target"], radius_bits=plan["radius_bits"],
                        incoming=plan["P"], fractional_bits=plan["P"] - 1),
                            "funded global common grid"),
                    rejects(lambda: source.make_window(reference, origin=2, length=2,
                        interior_blocks=((1,),), band=1, cap=1, block=windows[0][0].block,
                        precision=plan["P"], width=plan["P"] + 1, radius=plan["Rstar"],
                        target=plan["local_target"]), "funded signed scalar record carrier")]
        short_source = runtime.reference.Reference(runtime.raw, 15, 1, 2, 1, 3, 192)
        short_part = adapter.AdmittedPartition(runtime, short_source, "narrow", 0, 4, 2, ((0, 1),))
        controls.append(rejects(lambda: adapter.prepare(runtime, ((short_part,),), True,
                                  target=52, radius_bits=0),
                                "common reference accuracy at this raw inverse caller"))
        need(rows[0]["width"] < min(rows[0]["Wd"]) and rows[0]["width"] >= rows[0]["W0"],
             "actual checked sign shrink is strictly sharper than w>=Wd")
        print(canonical_json(dict(status="PASS_INDEPENDENT_COMPLETE_ALLOCATION", physical_execution=False,
            cases=rows, negative_controls=controls, source_interface="common-P input",
            source_sha256={name: sha256((package / name).read_bytes()).hexdigest()
                           for name in ("prepared_join.py", "admitted_context.py")})))


if __name__ == "__main__":
    main()
