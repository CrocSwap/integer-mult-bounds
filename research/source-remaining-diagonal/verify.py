#!/usr/bin/env python3
"""Independent rational coefficient oracle and bounded actual physical join.

No floating-point acceptance, no copied interval implementation, and no online
host numerical callback. Prepared for @CubeJerry with OpenAI assistance.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
import itertools
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from diagonal_sources import authenticate, bridge, load, native, references
from coefficients import Layout, RemainingProgram, need, upper_grid


def reject(function, fragment):
    try:
        function()
    except ValueError as error:
        need(fragment in str(error), "expected rejection: " + fragment)
        return 1
    raise ValueError("negative control accepted: " + fragment)


@lru_cache(None)
def oracle_pi(bits):
    """Exact rational alternating sums, without the retained dyadic interval code."""
    def atan_inverse(d):
        partial = Q(0)
        for i in range(bits + 2):
            partial += Q((-1) ** i, (2 * i + 1) * d ** (2 * i + 1))
        i = bits + 2
        following = partial + Q((-1) ** i, (2 * i + 1) * d ** (2 * i + 1))
        return min(partial, following), max(partial, following)
    a, b = atan_inverse(5), atan_inverse(239)
    return 16 * a[0] - 4 * b[1], 16 * a[1] - 4 * b[0]


@lru_cache(None)
def oracle_positive(exponent, bits):
    """Direct positive Taylor remainder, not reciprocal/range-reduced exp(-x)."""
    pilo, pihi = oracle_pi(bits)
    lo, hi = exponent * pilo, exponent * pihi
    termlo = termhi = sumlo = sumhi = Q(1)
    for n in range(1, 8 * (bits + 1) + 100):
        termlo, termhi = termlo * lo / n, termhi * hi / n
        sumlo, sumhi = sumlo + termlo, sumhi + termhi
        if hi < n + 2:
            tail = termhi * hi / (n + 1) / (1 - hi / (n + 2))
            if tail < Q(1, 1 << (bits + 16)):
                return sumlo, sumhi + tail
    raise ValueError("bounded positive exponential oracle did not finish")


def prepare():
    with references() as (source, raw):
        ref = source.Reference(raw, 15, 1, 2, 1, 3, 128)
        other = source.Reference(raw, 15, 1, 2, 1, 3, 128)
        cls = source.Reference
    with native() as exact:
        with exact.full_sources() as (_, _, _, compiler, _):
            event_types = compiler.Hadamard, compiler.Diagonal
            single = RemainingProgram(cls, (ref,), (1,), Layout((1, 4), (1,)), 9, 12, 3, compiler.Diagonal)
            pair = RemainingProgram(cls, (ref, other), (1, 1), Layout((4, 1, 4), (2, 0)),
                                    18, 12, 3, compiler.Diagonal)
    return single, pair, event_types


def coefficients(programs):
    checked = trajectories = controls = 0
    beta, alpha, eta = Q(39, 40), Q(99827101, 100000000), Q(332353, 332929)
    need(eta * Q(1, 10 ** 30) < beta * (alpha - eta),
         "full original-period route exponent is strictly subordinate to existing dense exponent")
    for R0 in range(1, 129):
        need(3 * R0 + 2 <= 2 * (2 * R0 + 2), "public ledger q guard funds actual remaining error")
    for ell in range(1, 257):
        need(100 * ell - (2 * ell + 4) - (4 * ell + 16) > 0,
             "source completed p^100 dyadic budget funds actual coefficient contraction")
    for program in programs:
        need(program.axis_bits == sum(program.layout.lengths[a] for a in program.layout.selected),
             "full original period, never Core-side bit count")
        unit = Q(1, 1 << program.bits)
        scale = Q(1, 1 << (program.completed_bits - program.U))
        original_maps = []
        for ref in program.references:
            S, e = ref.spec.source_size, ref.spec.excess
            original_maps.append({j + (2 * e * j + S) // (2 * S):
                                  Q(e * j, S) - (2 * e * j + S) // (2 * S)
                                  for j in range(S)})
        for index, receipt in enumerate(program.receipts):
            coordinates, stride = [], 1
            for axis in program.layout.selected:
                side = 1 << program.layout.lengths[axis]
                coordinates.append((index // stride) % side)
                stride *= side
            exponent = sum(ref.spec.alpha ** 2 * mapping.get(k, Q(0)) ** 2
                           for ref, mapping, k in zip(program.references, original_maps, coordinates))
            need(tuple(coordinates) == receipt["coordinates"] and exponent == receipt["exponent"],
                 "independent forward enumeration binds full original coordinates, beta, and hole exponent")
            lo, hi = oracle_positive(receipt["exponent"], program.bits)
            lo, hi = scale * lo, scale * hi
            c = receipt["value"] * unit
            need(0 <= lo <= hi <= 1 and hi >= receipt["lower"] and lo <= receipt["upper"],
                 "independent direct exponential overlaps actual reciprocal enclosure")
            need(max(abs(c - lo), abs(c - hi)) <= unit, "independent one-ulp coefficient error")
            for real, imag in ((0, 0), (3, 0), (-3, 0), (0, -3), (1, 2), (-1, -2),
                               (Q(1, 4096), Q(-4095, 4096))):
                a, b = int(real / unit), int(imag / unit)
                outa, outb = int(Q(a * receipt["value"], 1 << program.bits)), int(Q(b * receipt["value"], 1 << program.bits))
                error = max(abs(outa * unit - real * lo), abs(outa * unit - real * hi))
                error += max(abs(outb * unit - imag * lo), abs(outb * unit - imag * hi))
                need(error <= (program.radius + 2) * unit, "actual truncation plus coefficient error")
                trajectories += 1
            checked += 1
        # Original-axis order is independently checked by bit-address construction.
        for address in range(1 << program.layout.n):
            packed = 0
            for old in range(program.layout.n):
                packed |= ((address >> old) & 1) << program.layout.gather.get(old, old)
            original_coords = []
            for axis in program.layout.selected:
                offset = sum(program.layout.lengths[:axis])
                original_coords.append((address >> offset) & ((1 << program.layout.lengths[axis]) - 1))
            need(program.layout.coordinates(packed & ((1 << program.layout.h) - 1)) == tuple(original_coords),
                 "actual gather maps every original selected coordinate")
        original = program.completed_bits
        program.completed_bits += 1
        controls += reject(program.validate, "allocation")
        program.completed_bits = original
        original = program.page
        program.page = ((1, 1), *program.page[1:])
        controls += reject(program.validate, "coefficient period")
        program.page = original
        original = program.references[0].target_size
        program.references[0].target_size += 1
        controls += reject(program.validate, "full original target axis")
        program.references[0].target_size = original
        program.validate()
        zerobeta = program.receipts[0]["value"] * unit
        if program.completed_bits - program.U < program.bits:
            need(abs(zerobeta - Q(1, 1 << program.completed_bits)) > unit,
                 "omitted original U compensation negative control")
            controls += 1
    # Adversarial enclosures straddling grid boundaries, including clipping.
    quantizers = 0
    for bits in range(1, 13):
        unit = Q(1, 1 << bits)
        for k in range(min(1 << bits, 24)):
            for lowpart, width in itertools.product((Q(0), Q(1, 10), Q(9, 10)), (Q(0), Q(1, 2), Q(1))):
                lower, upper = (k + lowpart) * unit, (k + lowpart + width) * unit
                if lower > 1:
                    continue
                c = upper_grid(lower, upper, bits) * unit
                need(max(abs(c - lower), abs(c - min(Q(1), upper))) <= unit, "all rational quantizer endpoints")
                quantizers += 1
    lower, upper = Q(9, 10 * 4096), Q(19, 10 * 4096)
    bad = (lower * 4096).__floor__() / Q(4096)
    need(upper - bad > Q(1, 4096), "lower-floor negative control loses more than one ulp")
    controls += 1
    controls += reject(lambda: upper_grid(Q(0), Q(2), 3), "one-ulp width")
    return dict(coefficient_entries=checked, independent_grid_trajectories=trajectories,
                rational_quantizer_cases=quantizers, negative_controls=controls,
                programs=[p.record() for p in programs])


def encode_external(values, width):
    return "".join("".join(str(int(value < 0)) + format(abs(value), "0" + str(width - 1) + "b")
                            for value in pair) + "#" for pair in values)


def physical(program, event_types):
    with native() as exact:
        with exact.opened() as state:
            from cardinal_counts import Count
            from encoded import compare
            from records import Tape
            from session import initialize_marker, erase_marker
            from words import BLANK
            from physical_controls import PreparedFull
            from check_support import no_decode
            import check_composed
            owner_module = load("remaining_physical_owner", HERE / "diagonal_owner.py")
            B, codec_module = bridge()
            root, visits = check_composed.fixture("standard", False)
            observations = Counter()
            owner = owner_module.RemainingOwner(root, lambda name: observations.update((name,)))
            prepared = PreparedFull(program, Tape, Count, event_types)
            expected_parameters = (program.layout.n, program.layout.n - program.layout.h,
                program.layout.h, 1, program.bits, program.data_width, program.bits + 2,
                program.bits + 2, 2 * program.data_width + 3, program.bits,
                program.data_width, program.radius_bits,
                max(1, (program.layout.n - 1).bit_length()), 1, 0, 1)
            for actual, expected_parameter in zip(prepared.parameters, expected_parameters):
                expected_count = Count.literal(expected_parameter)
                try:
                    need(compare(actual, expected_count) == 0, "all16 original physical metadata positions")
                finally:
                    expected_count.close()
                    erase_marker(expected_count.tape)
            radius_log = program.radius_bits - (program.layout.n + 1) // 2
            accumulator_bits = 2 * program.bits + 2 * radius_log + program.layout.n
            need(program.temporary_width - accumulator_bits >= 7,
                 "full-field accumulator bound has at least seven temporary margin bits")
            routes = owner_module.PreparedRoutes(program.layout, program.data_width)
            fmt = codec_module.Format(program.bits + program.radius.bit_length() + 1, program.bits,
                                      program.data_width, program.bits, 0)
            codec = codec_module.Codec(B, Tape, BLANK, initialize_marker, erase_marker, fmt)
            bound = owner_module.BoundRemaining(codec, owner, routes, prepared)
            values = []
            for index in range(1 << program.layout.n):
                numerator = ((index * 613) % (3 << program.bits)) - (3 << (program.bits - 1))
                values.append((numerator, int((-1) ** index) * ((index * 31) % 1024)))
            need(all(abs(a) + abs(b) <= program.radius << program.bits for a, b in values), "fixture actual input radius")
            source = B.Tape("original external actual-state input", encode_external(values, fmt.external_bits))
            B.home(source)
            before = source.inspect()
            ports = (routes.forward, routes.inverse, prepared.code,
                     *(x.tape for x in routes.parameters), *(x.tape for x in prepared.parameters))
            snapshots = tuple((bytes(t.cells), t.head) for t in ports)
            alias_controls = 0
            for private in (owner.output, owner.pool.tapes[0], owner.diagonal.output,
                            owner.diagonal.word.output, root.router.output):
                alias_controls += reject(lambda private=private: owner.run(private, routes.forward,
                    routes.inverse, routes.parameters, prepared.code, prepared.parameters),
                    "external remaining-diagonal source/control ports")
            need(tuple((bytes(t.cells), t.head) for t in ports) == snapshots,
                 "private aliases rejected before borrowed control traffic")
            expected = []
            # Direct original-coordinate extraction, independent of route implementation.
            for index, pair in enumerate(values):
                coordinate = (index >> 1) & 15
                coefficient = program.page[coordinate][0]
                expected.append(tuple(int(Q(value * coefficient, 1 << program.bits)) for value in pair))
            started = time.monotonic()
            with no_decode():
                returned = bound.run(source)
            elapsed = time.monotonic() - started
            need(returned.inspect() == encode_external(expected, fmt.external_bits),
                 "unchanged native products and exact zero-drop codec match independent all-record oracle")
            need(source.inspect() == before and source._head == 1, "preserved original external field")
            need(tuple((bytes(t.cells), t.head) for t in ports) == snapshots, "all borrowed control heads and bytes restored")
            need(observations["input_squares"] == 2 << program.layout.n and
                 observations["data_products"] == 1 << program.layout.n and
                 observations["coefficient_products"] == 0 and owner.calls["gathers"] == 2
                 and owner.diagonal.arithmetic.products == 6 << program.layout.n,
                 "actual full radius, all products, and both original-frame routes")
            result = dict(elapsed_seconds=round(elapsed, 3), native_observations=dict(observations),
                          gathers=owner.calls["gathers"], page_components=prepared.page_components,
                          scalar_products=owner.diagonal.arithmetic.products,
                          parameter_positions_checked=16,
                          accumulator_margin_bits=program.temporary_width - accumulator_bits,
                          negative_controls=alias_controls + reject(lambda: bound.run(source),
                              "consume previous external remaining-diagonal output"),
                          scalar_cutoff=owner.diagonal.word.base_bits,
                          native_grid=fmt.native_grid, external_grid=fmt.external_grid, codec_drop=fmt.drop,
                          input_sha256=sha256(before.encode()).hexdigest(),
                          output_sha256=sha256(returned.inspect().encode()).hexdigest(),
                          external_tapes=[t.bill() for t in (*codec.templates, *codec.work)],
                          authenticated_native_imports=state.authenticated_imports,
                          retained_native_cells=sum(len(t.cells) for t in owner.private),
                          private_tape_roles=len(owner.private))
            bound.consume()
            need(not owner.pending and not bound.pending and owner.closed and owner.output.read() == BLANK
                 and all(t.inspect() == "" for t in codec.work), "consumed protected return and cleared owned payloads")
            owner.idle()
            prepared.close()
            routes.close()
            return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--physical", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    inputs = authenticate()
    single, pair, event_types = prepare()
    result = dict(status="PASS", source_inputs=len(inputs), coefficient=coefficients((single, pair)))
    if args.physical:
        result["physical"] = physical(single, event_types)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    # Normalize tuple/list representation before comparing a JSON receipt.
    result = json.loads(encoded)
    if args.output:
        Path(args.output).write_text(encoded)
    else:
        recorded = json.loads((HERE / "evidence/REPLAY.json").read_text())
        need(result["coefficient"] == recorded["coefficient"] and
             result["source_inputs"] == recorded["source_inputs"], "complete frozen coefficient/source receipt")
        if args.physical:
            stable = lambda row: {k: v for k, v in row.items() if k != "elapsed_seconds"}
            need(stable(result["physical"]) == stable(recorded["physical"]),
                 "complete frozen actual native/codec receipt except elapsed time")
    print(json.dumps(dict(status="PASS_SOURCE_REMAINING_DIAGONAL", source_inputs=len(inputs),
                         coefficients=result["coefficient"]["coefficient_entries"],
                         independent_grid_trajectories=result["coefficient"]["independent_grid_trajectories"],
                         coefficient_controls=result["coefficient"]["negative_controls"],
                         physical_scalar_calls=result.get("physical", {}).get("scalar_products"),
                         physical_controls=result.get("physical", {}).get("negative_controls")), sort_keys=True))


if __name__ == "__main__":
    main()
