#!/usr/bin/env python3
"""Source-bound consolidation of exact rational and residue borrowing scopes.

Gareth Davidson, substantial OpenAI Codex assistance. Apache-2.0.
No rounded supplier, new echo planner, rational-reconstruction algorithm or
new multiplication bound is supplied.
"""
import argparse
import copy
from fractions import Fraction as F
from itertools import product as tuples
from math import lcm
from pathlib import Path
import runpy
import tempfile

C = runpy.run_path(str(Path(__file__).with_name("common.py")))
need, same = C["need"], C["same"]
A = runpy.run_path(str(Path(__file__).with_name("algebra.py")))


def inverse_bits(q, w):
    """Independent one-bit lifting, without Newton or Python modular inversion."""
    need(q % 2, "nonunit denominator")
    value = 1
    for bit in range(1, w):
        if (q * value >> bit) & 1:
            value += 1 << bit
    need(q * value % (1 << w) == 1, "bit inverse")
    return value


def check_coefficients(factors, encoded, width):
    need(len(factors) == len(encoded), "coefficient factor count")
    for matrix, received in zip(factors, encoded):
        need(len(matrix) == len(received), "coefficient row count")
        for row, values in zip(matrix, received):
            need(len(row) == len(values), "coefficient column count")
            for rational, value in zip(row, values):
                expected = rational.numerator * inverse_bits(rational.denominator, width) % (1 << width)
                need(type(value) is int and value == expected, "rational coefficient residue")


def independent_preparation_invoice(factors, width, report):
    entries = sum(len(row) for matrix in factors for row in matrix)
    denoms = {x.denominator for matrix in factors for row in matrix for x in row}
    r, steps = len(denoms), (width - 1).bit_length()
    expected = dict(zero=8*r+4+4*entries, read_denominator=r+entries, check_odd=r,
                    set_one=r, mul=r*(2*steps+1)+entries, low=r*(3*steps+1)+2*entries,
                    subtract=r*steps, move=r*steps, check_one=r, write_inverse=r,
                    read_numerator=entries, read_inverse=entries, write_coefficient=entries)
    same(report["counts"], expected, "complete preparation command bill")
    need(report["commands"] == r*(15+7*steps)+4+11*entries, "preparation command total")
    need(report["work_bits"] == 5*width+3, "preparation private storage")
    need(report["inverse_table_bits"] == r*width, "inverse table storage")
    flat = [x for matrix in factors for row in matrix for x in row]
    ordered = sorted(denoms)
    length = len(factors[0])
    nb = max(abs(z.numerator).bit_length()+1 for z in flat)
    db = max(z.denominator.bit_length() for z in flat)
    cb, ib = 5*length*width, (5*length+entries)*width
    rb = ib+r*width
    batches = []
    for q in ordered:
        i = next(i for i, z in enumerate(flat) if z.denominator == q)
        batches.append([[rb+i*(nb+db)+nb, db, "read"], [ib+ordered.index(q)*width, width, "write"]])
    for i, value in enumerate(flat):
        batches.append([[rb+i*(nb+db), nb, "read"], [rb+i*(nb+db)+nb, db, "read"],
                        [ib+ordered.index(value.denominator)*width, width, "read"], [cb+i*width, width, "write"]])
    trace = [event for batch in batches for event in batch]
    travel = 0
    for batch in batches:
        itinerary = [0] + [event[0] for event in batch] + [0]
        travel += sum(abs(a-b) for a, b in zip(itinerary, itinerary[1:]))
    memory = dict(accesses=len(trace), bit_actions=sum(e[1] for e in trace), interfield_bit_travel=travel,
                  head_bit_moves=travel+sum(2*(e[1]-1) for e in trace), trace_sha256=C["digest"](trace),
                  data_coefficient_inverse_descriptor_bits=rb+entries*(nb+db))
    same(report["external_memory"], memory, "preparation source routing invoice")
    need(report["original_descriptor_fixed_bits"] == entries*(nb+db), "original descriptor storage")


def unit_census():
    units, nonunits = 0, 0
    for width in range(1, 9):
        modulus = 1 << width
        for denominator in range(1, 32):
            if denominator % 2:
                need(inverse_bits(denominator, width) == pow(denominator, -1, modulus), "unit census")
                units += 1
            else:
                need(all(denominator * a % modulus != 1 for a in range(modulus)), "even denominator unit")
                nonunits += 1
    homomorphisms = 0
    for width in range(1, 7):
        modulus = 1 << width
        for denominator in (3, 5, 7):
            for numerator in (-5, -2, 1, 4):
                alpha = F(numerator, denominator)
                coefficient = A["residue"](alpha, width)
                for x, y in tuples(range(modulus), repeat=2):
                    need(A["residue"](alpha * (x+y), width) == coefficient*(x+y) % modulus,
                         "additive quotient map")
                    homomorphisms += 1
    return dict(unit_inverse_cases=units, nonunit_exclusions=nonunits,
                quotient_addition_cases=homomorphisms, widths_units=[1, 8], widths_addition=[1, 6])


def signed_inverse(word):
    return [[s, t, i, -q] for s, t, i, q in reversed(word)]


def small_cases(borrow, dense):
    _, trees, _ = borrow.unit_plan(8)
    count, prefixes, commands = 0, 0, 0
    for n in range(1, 9):
        for length in (1, 2, 3):
            integer = []
            for factor in range(n):
                matrix = [[int(i == j) for j in range(length)] for i in range(length)]
                if length > 1:
                    matrix[factor % length][(factor+1) % length] += (-1)**factor
                integer.append(matrix)
            for denominator in (3, 5, 7):
                factors, _ = A["scale_fixture"](integer, denominator)
                width = max(A["rational_bound"](factors, 1, 1)["width"], denominator.bit_length()+1)
                A["validate"](factors, width, 1, 1)
                encoded, prep = A["prepare"](factors, width)
                check_coefficients(factors, encoded, width)
                independent_preparation_invoice(factors, width, prep)
                initial = [[(-1)**j for j in range(length)], [(-1)**(j+1) for j in range(length)]]
                initial += [[((r+2)*(j+3)) % (1 << width) - (1 << (width-1))
                             for j in range(length)] for r in range(3)]
                word = [list(x) for x in borrow.instructions(trees[n-1])]
                for active in (word, signed_inverse(word)):
                    report = A["lifted_replay"](active, factors, initial, encoded, width, dense, 1, 1)
                    count += 1
                    prefixes += report["leaf_prefixes"]
                    commands += report["primitive"]["commands"]
    return dict(cases=count, factor_counts=[1, 8], dimensions=[1, 2, 3],
                denominators=[3, 5, 7], directions=2, leaf_prefixes=prefixes, commands=commands)


def failures(factors, coefficients, width, prep, borrow, contracts, basis):
    rejected = []

    def reject(label, action, reason):
        try:
            action()
        except ValueError as exc:
            need(reason in str(exc), "wrong failure: " + label + ": " + str(exc))
            rejected.append(label)
        else:
            raise ValueError("failure control accepted: " + label)

    reject("even reduced denominator", lambda: A["validate"]([[[F(1, 2)]]], 5, 1, 0), "nonunit")
    reject("odd denominator but nonintegral completed map", lambda: A["validate"]([[[F(1, 3)]]], 5, 1, 0),
           "completed map not integral")
    reject("integral endpoint beyond signed range", lambda: A["validate"]([[[F(3)]]], 4, 3, 0), "recovery guard")
    reject("equality at signed cap", lambda: A["validate"]([[[F(1)]]], 4, 7, 1), "recovery guard")
    reject("zero map cannot hide nonrepresentable source", lambda: A["validate"]([[[F(0)]]], 4, 8, 0),
           "recovery guard")
    corrupted = copy.deepcopy(coefficients)
    corrupted[0][0][0] ^= 1
    reject("bad prepared inverse/coefficient", lambda: check_coefficients(factors, corrupted, width), "coefficient residue")
    free_preparation = copy.deepcopy(prep)
    free_preparation["counts"]["move"] -= 1
    reject("omitted inverse update move", lambda: independent_preparation_invoice(factors, width, free_preparation),
           "preparation command bill")
    free_table = copy.deepcopy(prep)
    free_table["inverse_table_bits"] = 0
    reject("unpaid inverse table", lambda: independent_preparation_invoice(factors, width, free_table), "table storage")
    free_routing = copy.deepcopy(prep)
    free_routing["external_memory"]["head_bit_moves"] -= 1
    reject("unpaid preparation head travel", lambda: independent_preparation_invoice(factors, width, free_routing),
           "source routing invoice")
    reject("boolean width", lambda: A["validate"](factors, True, 7, 7), "positive width")
    reject("raw denominator exceeds priced preparation workspace",
           lambda: A["prepare"]([[[F(1, 17)]]], 4), "descriptor range")
    witness = F(*basis[0]["denominator_witness"]["value"])
    reject("common numerator denominator three is insufficient",
           lambda: need((3*witness).denominator == 1, "nonintegral common numerator"),
           "nonintegral common numerator")

    # Concrete forbidden interpretations are recorded, not silently admitted.
    nonintegral = A["residue"](F(1, 3), 4)
    decoded = nonintegral if nonintegral < 8 else nonintegral - 16
    need(decoded != F(1, 3), "nonintegral signed decoding counterexample")
    word = [list(x) for x in borrow.instructions((0, 1))]
    initial = [1, 0, 2, -1, 3]
    rounded = contracts.replay(word, initial, lambda i, z: contracts.nearest(z, 3) if i == 0 else 3*z)
    need(rounded[1] != 1 and all(rounded[i] == initial[i] for i in (0, 2, 3, 4)), "rounded same-product witness")
    nested_word = [list(x) for x in borrow.instructions((0, ((1, 2), 3)))]
    nested = None
    for initial_tuple in tuples(range(-2, 3), repeat=5):
        result = contracts.replay(nested_word, initial_tuple,
                                 lambda i, z: contracts.nearest(4*z, 3) if i == 2 else z)
        if any(result[i] != initial_tuple[i] for i in (2, 3, 4)):
            nested = dict(initial=list(initial_tuple), final=result)
            break
    need(nested is not None, "nested rounded helper counterexample")
    # Normalizing a fraction first matters: raw denominator six cancels to three.
    need(A["residue"](F(2, 6), 4) == A["residue"](F(1, 3), 4), "cancelled even denominator positive control")
    return dict(rejected=rejected, counterexamples=dict(nonintegral_residue=nonintegral,
                nonintegral_signed_decode=decoded, rounded_integral_product=dict(initial=initial, final=rounded),
                nested_rounded_helper=nested),
                positive_controls=["2/6 normalizes to unit denominator 3"])


def run(output, write_expected=False, receipt=None):
    manifest = C["pins"]()  # Before executing any vendored source.
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    dense = C["module"]("rational_frozen_dense", C["HERE"] / "vendor/pr1159/dense.py")
    borrow = C["module"]("rational_frozen_borrow", C["HERE"] / "vendor/pr1057/borrow.py")
    contracts = C["module"]("rational_frozen_contracts", C["HERE"] / "vendor/pr1135/contracts.py")
    source = C["load"](C["HERE"] / "vendor/pr1159/CASE.json.gz")
    same(source["word"], [list(x) for x in borrow.instructions(source["tree"])], "frozen parent word")
    same(C["load"](C["HERE"] / "vendor/pr1159/PROGRAM.json.gz"),
         [list(x) for x in dense.primitive_word(source["word"], 2)], "unchanged full primitive program")
    factors, exponents = A["scale_fixture"](source["factors"])
    endpoint, bounds = A["validate"](factors, source["width"], source["x_bound"], source["y_bound"])
    need(endpoint == A["product"](source["factors"]) and sum(exponents) == 0, "central-scale cancellation")
    width = source["width"]
    coefficients, preparation = A["prepare"](factors, width)
    check_coefficients(factors, coefficients, width)
    independent_preparation_invoice(factors, width, preparation)
    forward, reverse = source["word"], signed_inverse(source["word"])
    basis = [A["prefix_basis"](word, factors, width, 7, 7) for word in (forward, reverse)]
    need([x["endpoint_direction"] for x in basis] == [1, -1], "both basis orientations")
    degree = contracts.prefix_degree(forward, 5)
    common = lcm(*(x["least_common_prefix_denominator"] for x in basis))
    comparison = dict(formal_prefix_degree=degree, conservative_denominator=str(3**degree),
                      conservative_denominator_bits=(3**degree).bit_length(),
                      least_common_prefix_denominator=common,
                      numerator_sufficient_bits=max(x["common_numerator_sufficient_bits"] for x in basis),
                      conservative_numerator_sufficient_bits=max(
                          (F(*x["rational_absolute_prefix_bound"])*3**degree).numerator.bit_length()+1 for x in basis))
    initial_sets = [
        [[7, -7], [-3, 5], [(1 << 55)-1, -(1 << 54)], [-(1 << 55), 123], [17, -91]],
        [[7, -7], [-3, 5], [2, -4], [-7, 6], [5, -1]],
    ]
    replays = []
    for initial in initial_sets:
        for word in (forward, reverse):
            got = A["lifted_replay"](word, factors, initial, coefficients, width, dense, 7, 7)
            expected = dense.invoice(word, 2, 52, width)
            for key in ("commands", "leaves", "counts", "intercell_steps", "accesses", "work_bits",
                        "head_bit_moves", "data_bit_actions"):
                same(got["primitive"][key], expected[key], "retained kernel invoice " + key)
            replays.append(got)
    case = dict(format="rational-residue-scope/1", source_case_sha256=C["digest"](source), width=width,
                central_scale_exponents=exponents,
                rational_factors=[[[A["encode"](x) for x in row] for row in a] for a in factors],
                residue_coefficients=coefficients, integral_product=[[int(x) for x in row] for row in endpoint])
    report = dict(format="rational-residue-scope-receipt/1", source_manifest_sha256=C["digest"](manifest),
                  case_sha256=C["digest"](case), bounds=bounds, basis=basis, comparison=comparison,
                  preparation=preparation, kernel=dense.invoice(forward, 2, 52, width),
                  initial_sets=initial_sets, replays=replays, unit_census=unit_census(),
                  small_cases=small_cases(borrow, dense),
                  controls=failures(factors, coefficients, width, preparation, borrow, contracts, basis),
                  admission_rational_product_ops=dict(multiplies=52*2**3, adds=52*2**3,
                      scope="Additional arbitrary-precision product check; operand sizes, normalization, descriptors, norm guard and routing are separate paid terms"),
                  kernel_plus_priced_preparation_commands=preparation["commands"]+replays[0]["primitive"]["commands"],
                  new_kappa_claim=False)
    for name, value in (("CASE.json.gz", case), ("EXPECTED.json", report)):
        C["write"](output / name, value)
        if write_expected:
            C["write"](C["HERE"] / name, value)
        else:
            same(C["load"](C["HERE"] / name), value, "complete regenerated " + name)
    if receipt:
        C["write"](receipt, report)
    print("PASS_RATIONAL_RESIDUE_SCOPE: 52 rational factors; 1376 calls; 56-bit data;",
          report["kernel_plus_priced_preparation_commands"], "priced kernel/preparation commands;",
          report["small_cases"]["cases"], "small cases; no rounded contract or new kappa")
    print("receipt_sha256", C["digest"](report))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--write-expected", action="store_true", help="initial production only; refuses overwrite")
    args = parser.parse_args()
    if args.output:
        run(args.output, args.write_expected, args.receipt)
    else:
        with tempfile.TemporaryDirectory(prefix="rational-residue-") as temporary:
            run(Path(temporary) / "run", args.write_expected, args.receipt)
