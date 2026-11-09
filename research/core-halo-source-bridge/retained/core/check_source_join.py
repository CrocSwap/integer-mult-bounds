"""Nontrivial current-source five-stage SEMANTIC replay and independent target.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
This runs all real emitted dense H/D events and the retained staged sparse
value observers. It never claims those host operations are physical tape work.
The final/error observer imports neither factor preparation nor sparse solvers.
"""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
from pathlib import Path
import sys

from independent_numerics import (
    bandwidth, canonical_json, check_complete_return, ceil_log2, decode_pairs,
    five_factors, fraction_digest, need, pow2, squared_norm,
)
from stage_observer import KINDS, check_stages, product


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def truncate(integer, bits):
    return (abs(integer) >> bits) * (-1 if integer < 0 else 1)


def complex_product(first, second, bits):
    real = first[0] * second[0] - first[1] * second[1]
    imag = first[0] * second[1] + first[1] * second[0]
    return (truncate(real, bits), truncate(imag, bits)), int(bool(real % (1 << bits) or imag % (1 << bits)))


def dense_replay(runtime, program, values):
    """Direct emitted-event semantics; no program.execute or predecessor oracle."""
    need(len(values) == program.records and program.incoming == program.bits,
         "complete common-grid actual dense input")
    need(squared_norm(decode_pairs(values, program.bits)) <= program.radius ** 2,
         "actual dense input radius before replay")
    state = list(values)
    hc = dc = rounding = 0
    for event in program.events():
        if isinstance(event, runtime.global_compiler.Hadamard):
            for bit in event.positions:
                step = 1 << bit
                for base in range(0, len(state), 2 * step):
                    for offset in range(step):
                        i, j = base + offset, base + offset + step
                        a, b = state[i], state[j]
                        state[i] = (a[0] + b[0], a[1] + b[1])
                        state[j] = (a[0] - b[0], a[1] - b[1])
            hc += 1
        else:
            need(isinstance(event, runtime.global_compiler.Diagonal), "only actual H/diagonal source events")
            mask, bits, g = (1 << program.axis_bits) - 1, program.bits, program.axes
            for index, value in enumerate(state):
                context = index >> (g * program.axis_bits)
                factor = (1 << bits, 0)
                for axis in reversed(range(g)):
                    digit = (index >> (axis * program.axis_bits)) & mask
                    factor, rounded = complex_product(event.pages[context][axis][digit], factor, bits)
                    rounding += rounded
                state[index], rounded = complex_product(factor, value, bits)
                rounding += rounded
            dc += 1
        need(all(-(1 << (program.data_width - 1)) <= x < 1 << (program.data_width - 1)
                 for z in state for x in z), "every emitted dense event fits its actual signed width")
    need((hc, dc, hc + dc) == (program.h_count, program.diagonal_count, program.stages),
         "all emitted events, including idle words, executed exactly once")
    return tuple(state), dict(H=hc, diagonal=dc, events=hc + dc, nonzero_roundings=rounding)


def sparse_replay(windows, values, precision, source, forward, upper=False):
    """Retained staged per-column function, in router high-axis-first order."""
    contexts, axes, side = len(windows), len(windows[0]), windows[0][0].length
    volume = side ** axes
    state = list(decode_pairs(values, precision))
    calls = 0
    for c, family in enumerate(windows):
        for router_axis, window in enumerate(family):
            low_axis = axes - 1 - router_axis
            step = side ** low_axis
            independent = five_factors(window.H, window.I)
            supplied = tuple(tuple(independent["factors"][3][i][j] for j in window.E)
                             for i in window.E)
            block = 1 << max(1, ceil_log2(2 * bandwidth(supplied) + 1))
            for base in range(0, volume, step * side):
                for offset in range(step):
                    ids = tuple(c * volume + base + offset + i * step for i in window.E)
                    current = tuple(state[i] for i in ids)
                    need(max(sum(map(abs, z), Q()) for z in current) <= window.radius,
                         "actual current sparse input satisfies prepared complex-l1 radius")
                    if upper:
                        result = forward.rounded_oracle(supplied, current, block, precision)
                    else:
                        result = list(source.rounded_solve(window.shear_lower, window.shear_upper,
                                                          current, window.block, precision))
                        selected = tuple(i for i, flag in enumerate(window.j_mask) if flag)
                        solved = source.rounded_solve(window.f_lower, window.f_upper,
                            tuple(result[i] for i in selected), window.block, precision)
                        for i, row in zip(selected, solved):
                            result[i] = row
                    for i, row in zip(ids, result):
                        state[i] = tuple(row)
                    calls += 1
    encoded = tuple(tuple(int(x * (1 << precision)) for x in row) for row in state)
    need(decode_pairs(encoded, precision) == tuple(state), "staged sparse output remains on common grid")
    return encoded, calls


def rejected(call, label):
    try:
        call()
    except ValueError:
        return label
    raise ValueError("accepted source-join negative control: " + label)


def main():
    parser = ArgumentParser()
    parser.add_argument("--source-package", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    package = args.source_package.resolve()
    join = load("_independent_join_sources", package / "join_sources.py")
    with join.numerical() as runtime:
        adapter = load("_independent_admitted_context", package / "admitted_context.py")
        source = load("_independent_source_window", join.INVERSE / "source_window.py")
        forward = load("_independent_forward_pages", join.FORWARD / "pages.py")
        refs = tuple(runtime.reference.Reference(runtime.raw, 15, 1, alpha, 2, 3, 192)
                     for alpha in (2, 3))
        specs = (((0, 0), (1, 4)), ((1, 0), (0, 4)))
        family = tuple(tuple(adapter.AdmittedPartition(runtime, refs[ref], "narrow", origin,
                             4, 2, ((0, 1),)) for ref, origin in row) for row in specs)
        provisional = [adapter.prepare(runtime, family, direction, target=52, radius_bits=0)
                       for direction in (True, False)]
        precision = max(program.bits for program in provisional)
        programs = [adapter.prepare(runtime, family, direction, target=52, radius_bits=0,
                                     incoming=precision, fractional_bits=precision)
                    for direction in (True, False)]
        width = max(precision + 64, *(p.data_width for p in programs))
        windows = tuple(tuple(source.make_window(refs[ref], origin=origin, length=4,
                          interior_blocks=((0, 1),), band=2, cap=2, block=4,
                          precision=precision, width=width, radius=Q(1), target=52)
                        for ref, origin in row) for row in specs)
        low_sources = tuple(tuple(window.H for window in reversed(row)) for row in windows)
        low_interiors = tuple(tuple(window.I for window in reversed(row)) for row in windows)
        factors = tuple(tuple(five_factors(w.H, w.I) for w in row) for row in windows)
        need(all(f["A"][0][1] != 0 and f["A"][1][0] != 0 for row in factors for f in row),
             "all actual two-coordinate interiors are nonidentity and coupled")
        incoming = tuple((((5 * i + 1) % 7 - 3) * (1 << (precision - 6)) + 1,
                          ((3 * i + 2) % 5 - 2) * (1 << (precision - 6)) - 1)
                         for i in range(programs[0].records))
        v2 = 1 << ((programs[0].array_bits + 1) // 2)
        sparse_bounds = []
        for stage in (1, 3):
            per_context = []
            for row, frow in zip(windows, factors):
                hs = tuple(max(sum(map(abs, r), Q()) for r in f["factors"][stage]) for f in frow)
                es = tuple(w.total_error if stage == 1 else
                           Q(max(sum(bool(x) for x in r) for r in f["factors"][stage]) + 6,
                             1 << precision) for w, f in zip(row, frow))
                per_context.append(sum((e * product(hs[a + 1:]) for a, e in enumerate(es)), Q()))
            sparse_bounds.append(v2 * max(per_context))
        allowances = (programs[0].total_error, sparse_bounds[0], programs[1].total_error,
                      sparse_bounds[1], programs[0].total_error)
        state, observations, dense_counts, sparse_calls = incoming, [], [], []
        for stage in range(5):
            before = state
            if stage in (0, 2, 4):
                p = programs[1 if stage == 2 else 0]
                state, counts = dense_replay(runtime, p, state)
                dense_counts.append(counts)
                wi, wo = precision + 2, p.data_width
            else:
                state, calls = sparse_replay(windows, state, precision, source, forward, stage == 3)
                sparse_calls.append(calls)
                wi = wo = width
            observations.append(dict(kind=KINDS[stage], input=before, output=state,
                input_precision=precision, output_precision=precision,
                input_width=wi, output_width=wo, input_radius=1))
        checked = check_stages(low_sources, low_interiors, incoming, precision, observations,
                               allowances, 32, common_precision=precision)
        wrong_axes = tuple(tuple(reversed(row)) for row in low_sources)
        controls = [rejected(lambda: check_complete_return(wrong_axes, incoming, precision,
                              state, precision, 32), "unreversed dense/router source axes"),
                    rejected(lambda: check_complete_return(tuple(reversed(low_sources)), incoming,
                              precision, state, precision, 32), "swapped global source contexts")]
        broken = [dict(row) for row in observations]
        altered = list(broken[1]["input"])
        altered[0] = (altered[0][0] + 1, altered[0][1])
        broken[1]["input"] = tuple(altered)
        controls.append(rejected(lambda: check_stages(low_sources, low_interiors, incoming,
                         precision, broken, allowances, 32), "one-ulp discontinuity at sparse entry"))
        checked.update(physical_execution=False, semantic_execution=True,
            source_reference_hashes=[r.description_hash for r in refs], source_specs=specs,
            grid=precision, common_width=width, dense_counts=dense_counts,
            sparse_line_observer_calls=sparse_calls, negative_controls=controls,
            admitted_partition=True, production_carve=False,
            adapter_sha256=sha256((package / "admitted_context.py").read_bytes()).hexdigest())
        print(canonical_json(checked))


if __name__ == "__main__":
    main()
