#!/usr/bin/env python3
"""Exact scoped regression and independent endpoint checks; no fast tape trace."""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import direct
import frozen

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


def independent_pair(left, right, inverse=False):
    """Ideal rational pair plus its parity defect, rather than four shears."""
    a, b = left
    c, d = right
    p, q = a - c, b - d
    defect = q % 2 - p % 2
    sign = -1 if inverse else 1
    numerators = ((a + c - sign*q + defect, b + d + sign*p - defect),
                  (a + c + sign*q + defect, b + d - sign*p - defect))
    need(all(x % 2 == 0 for pair in numerators for x in pair), "integral parity formula")
    return tuple(tuple(x // 2 for x in pair) for pair in numerators)


def independent_lift(values, axes, inverse=False):
    result = list(values)
    for axis in reversed(axes) if inverse else axes:
        for address in range(len(result)):
            if not (address >> axis) & 1:
                other = address | (1 << axis)
                result[address], result[other] = independent_pair(result[address], result[other], inverse)
    return result


def exact_pair(values, inverse=False):
    (a, b), (c, d) = values
    sign = -1 if inverse else 1
    return [(Q(a+c-sign*(b-d), 2), Q(b+d+sign*(a-c), 2)),
            (Q(a+c+sign*(b-d), 2), Q(b+d-sign*(a-c), 2))]


def rotate_oracle(value, phase):
    a, b = value
    return [(a, b), (-b, a), (-a, -b), (b, -a)][phase % 4]


def formula(values, recipe, multiplicity, inverse=False):
    """Original tensor column formula, without the CNOT word or lift backend."""
    count = len(recipe["matrix_rows"])
    out = [None] * len(values)
    for x in range(len(values)):
        destination = 0
        exponent = multiplicity * recipe["phase"]
        for j in range(multiplicity):
            column = [(x >> (i*multiplicity+j)) & 1 for i in range(count)]
            for i in range(count):
                bit = (recipe["offset"] >> i) & 1
                bit ^= sum(column[k] for k in range(count) if (recipe["matrix_rows"][i] >> k) & 1) % 2
                destination |= bit << (i*multiplicity+j)
                exponent += recipe["linear_Z4"][i] * column[i]
                for k in range(i+1, count):
                    exponent += 2 * column[i] * column[k] * ((recipe["quadratic_rows"][i] >> k) & 1)
        if inverse:
            out[x] = rotate_oracle(values[destination], -exponent)
        else:
            need(out[destination] is None, "formula bijection")
            out[destination] = rotate_oracle(values[x], exponent)
    return out


def executor_class(old):
    class Refined(old.Executor):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.wrapper_receipts = []

        def monomial(self, values, recipe, multiplicity=1, inverse=False):
            need(len(recipe["matrix_rows"]) * multiplicity == self.n, "executor layout")
            word = old.SOURCE["binary_word"](recipe)
            result, low = direct.execute(values, recipe, word, multiplicity, self.fast_lift,
                                         self.width, inverse, self.wrapper_receipts)
            need(low == [(0, 0)] * len(values), "actual returned guard bank")
            self.counts["address_gates"] += len(word)
            return result
    return Refined


def primitives(old):
    count = 0
    for a, b, c, d in product(range(-2, 3), repeat=4):
        for inverse in (False, True):
            actual = independent_pair((a, b), (c, d), inverse)
            need(actual == old.CORE.pair((a, b), (c, d), inverse), "independent parity formula")
            need(independent_pair(*actual, not inverse) == ((a, b), (c, d)), "signed pair inverse")
            count += 1
    # These basis identities are exact Q(i) matrix identities, not random tests.
    for source in ([(1, 0), (0, 0)], [(0, 0), (1, 0)]):
        need(exact_pair(exact_pair(source, True)) == source, "C inverse")
        need(exact_pair(exact_pair(source)) == list(reversed(source)), "C squared is X")
        z = lambda v: [v[0], tuple(-x for x in v[1])]
        result = [rotate_oracle(v, 1) for v in exact_pair(z(exact_pair(z(source), True)))]
        need(result == list(reversed(source)), "i C Z C^-1 Z is X")
    return dict(signed_pair_cases=count, exact_complex_matrix_identities=3)


def bit_boundary():
    def bits(value, width):
        return [(value >> i) & 1 for i in range(width)]

    def decode(word):
        return sum(x << i for i, x in enumerate(word)) - (word[-1] << len(word))

    count = 0
    for width in range(2, 9):
        for guard in range(6):
            for high in (1, 2, 3):
                for value in range(-(1 << (width-1)), 1 << (width-1)):
                    source = bits(value, width)
                    wide = direct.embed_bits(source, guard, high)
                    need(decode(wide) == value * (1 << guard), "actual bit embedding")
                    result, scratch = direct.contract_bits(wide, width, guard)
                    need(result == source and scratch == [0] * (guard+high), "actual sign and guard return")
                    count += 1
    # Change the data's sign and swap components before contraction. Old sign
    # storage must not be used when a monomial endpoint changes signs.
    phase_cases = 0
    for a, b, phase in product(range(-3, 4), range(-3, 4), range(4)):
        output = rotate_oracle((a, b), phase)
        for value in output:
            wide = bits(value << 4, 11)
            small, scratch = direct.contract_bits(wide, 4, 4)
            need(decode(small) == value and not any(scratch), "changed output sign cleanup")
        phase_cases += 1
    dirty_low = direct.embed_bits(bits(-3, 4), 2, 3); dirty_low[0] = 1
    rejects(lambda: direct.contract_bits(dirty_low, 4, 2), "dirty low bits")
    dirty_high = direct.embed_bits(bits(-3, 4), 2, 3); dirty_high[-1] ^= 1
    rejects(lambda: direct.contract_bits(dirty_high, 4, 2), "output sign extension")
    # +8 cannot be contracted to four signed bits after negating -8.
    rejects(lambda: direct.contract_bits(bits(8 << 2, 9), 4, 2), "capacity")
    return dict(exhaustive_signed_words=count, changed_phase_outputs=phase_cases,
                controls=["dirty-low", "wrong-sign-extension", "minimum-negative-negation-overflow"])


def fixtures(size, bits, rng):
    # Tags distinguish every address even after any Gaussian unit rotation.
    tags = [(2**bits + i, 3*2**bits + i) for i in range(size)]
    random_signed = [(rng.randint(-(1 << bits), 1 << bits), rng.randint(-(1 << bits), 1 << bits)) for _ in range(size)]
    return [tags, random_signed]


def wrapper_checks(old, Refined):
    receipts = []
    rng = random.Random(78)
    for index, recipe in zip((2031, 2033), old.SOURCE["recipes"], strict=True):
        for side in ("left", "right"):
            record = recipe[side]
            word = old.SOURCE["binary_word"](record)
            for inverse in (False, True):
                for values in fixtures(512, 67, rng):
                    before = tuple(values)
                    original = old.Executor(9, 256, d=2, spacing=1, suffix=0)
                    refined = Refined(9, 256, d=2, spacing=1, suffix=0)
                    expected = formula(values, record, 1, inverse)
                    baseline = original.monomial(values, record, inverse=inverse)
                    result = refined.monomial(values, record, inverse=inverse)
                    need(result == baseline == expected and tuple(values) == before, "actual native wrapper refinement")
                    need(original.counts["fast_lifts"] == 8 * len(word), "baseline wrapper tariff")
                    need(refined.counts["fast_lifts"] == 2 * len(word), "refined wrapper tariff")
                    receipts.append(dict(event=index, side=side, inverse=inverse, gates=len(word),
                                         old_lifts=original.counts["fast_lifts"], new_lifts=refined.counts["fast_lifts"],
                                         output_sha256=digest(result), guards=refined.wrapper_receipts))
    synthetic = dict(matrix_rows=[3, 2, 7], offset=5, linear_Z4=[1, 3, 2],
                     quadratic_rows=[6, 4, 0], phase=3)
    tensor = []
    plans = [(synthetic, mult, 1) for mult in (1, 2, 3)]
    plans.append((dict(matrix_rows=[3, 2], offset=1, linear_Z4=[1, 2],
                       quadratic_rows=[2, 0], phase=1), 4, 2))
    for synthetic, multiplicity, spacing in plans:
        dimension = len(synthetic["matrix_rows"]) * multiplicity
        for inverse in (False, True):
            for values in fixtures(1 << dimension, 17, rng):
                baseline = old.Executor(dimension, 128, d=2, spacing=spacing, suffix=0)
                refined = Refined(dimension, 128, d=2, spacing=spacing, suffix=0)
                expected = formula(values, synthetic, multiplicity, inverse)
                result = refined.monomial(values, synthetic, multiplicity, inverse)
                need(result == expected == baseline.monomial(values, synthetic, multiplicity, inverse), "tensor wrapper endpoint")
                need(refined.monomial(result, synthetic, multiplicity, not inverse) == values, "tensor literal inverse")
                if multiplicity >= 2:
                    need(refined.counts["inner_oracles"] > 0, "retained nonempty backend cleanup")
                blocks, suffix = refined.split_axes(tuple(range(multiplicity)))
                order = tuple(axis for block in blocks for axis in block) + suffix
                if multiplicity == 4:
                    need(order == (0, 2, 1, 3), "actual changed-order backend coverage")
                tensor.append(dict(multiplicity=multiplicity, inverse=inverse, inner_order=order,
                                   output_sha256=digest(result)))
    return dict(actual=receipts, tensors=tensor)


def exhaustive_gates():
    cases = 0
    # Independent formula backend; all {-1,0,1} Gaussian payloads on two axes.
    for flat in product((-1, 0, 1), repeat=8):
        values = list(zip(flat[::2], flat[1::2], strict=True))
        fine = [(a << 2, b << 2) for a, b in values]
        for controls in (None, (1,)):
            actual = direct.guarded_gate(fine, (0,), controls, independent_lift)
            expected = [None] * 4
            for address, value in enumerate(fine):
                destination = address ^ (1 if controls is None or address & 2 else 0)
                expected[destination] = value
            need(actual == expected, "exhaustive direct guarded gate")
            need(direct.guarded_gate(actual, (0,), controls, independent_lift, True) == fine, "literal gate inverse")
            cases += 1
    return cases


def collector_inputs():
    rng = random.Random(78)
    zero = [(0, 0)] * 512
    small = [[(rng.randint(-100, 100), rng.randint(-100, 100)) for _ in range(512)] for _ in range(6)]
    huge = [(2**257 + i, -(2**259) + i) for i in range(512)]
    negative = [(-a, -b) for a, b in huge]
    return [([list(zero) for _ in range(5)], list(zero), 0, 0),
            (small[:5], small[5], 4, 3),
            ([huge, negative, small[0], list(zero), list(zero)], small[1], 11, 8),
            ([huge, small[0], small[1], small[2], small[3]], huge, 3, 2)]


def collectors(old, Refined):
    results = []
    recipe = old.SOURCE["recipes"][0]
    for sources, query, grid, beta in collector_inputs():
        before = deepcopy((sources, query))
        original = old.Executor(9, 512, d=2, spacing=1, suffix=0, outer=3)
        refined = Refined(9, 512, d=2, spacing=1, suffix=0, outer=3)
        expected = old.collector(original, sources, query, grid, beta, recipe)
        actual = old.collector(refined, sources, query, grid, beta, recipe)
        need(actual == expected and (sources, query) == before, "complete collector refinement and source preservation")
        need(actual["private"] == [(0, 0)] * 512, "collector private zero")
        need(sum(x["field_gates"] for x in refined.wrapper_receipts) == 52, "actual 52 field gates")
        need(sum(x["inner_lifts"] for x in refined.wrapper_receipts) == 104, "actual 104 wrapper lifts")
        need(original.counts["fast_lifts"] - refined.counts["fast_lifts"] == 312, "collector removes 312 wrapper lifts")
        need(original.counts["dense_linear_oracles"] == refined.counts["dense_linear_oracles"], "original core unchanged")
        results.append(dict(input_sha256=digest([sources, query, grid, beta]), result_sha256=digest(actual),
                            grid=actual["grid"], baseline=original.counts, refined=refined.counts,
                            wrapper_receipts=refined.wrapper_receipts))
    return results


def rejects(call, message):
    try:
        call()
    except ValueError as error:
        need(message in str(error), "wrong rejection: " + str(error))
        return
    raise ValueError("missing rejection: " + message)


def controls(old):
    record = old.SOURCE["recipes"][0]["right"]
    word = old.SOURCE["binary_word"](record)
    values = fixtures(512, 9, random.Random(78))[0]
    rejects(lambda: direct.validate_word(record, word[:-1]), "affine endpoint")
    corrupt = deepcopy(record); corrupt["phase"] = True
    rejects(lambda: direct.validate_word(corrupt, word), "global phase")
    rejects(lambda: direct.execute(values[:-1], record, word, 1, independent_lift, 64), "dense field layout")
    rejects(lambda: direct.execute(values, record, word, 1, independent_lift, 8), "signed overflow")
    rejects(lambda: direct.execute([(64, 0)] * 512, record, word, 1, independent_lift, 8), "signed overflow")
    rejects(lambda: direct.split_zero_guards([(1, -1)], 2), "nonzero guard bank")
    negative = [(-12, 8), (-4, -16)]
    need(direct.split_zero_guards(negative, 2) == ([(-3, 2), (-1, -4)], [(0, 0), (0, 0)]), "negative exact shift")
    # Exact Q/phase faults are endpoint errors even though low guards return zero.
    fine = [(4, 0), (0, 0), (8, 0), (12, 0)]
    full = direct.guarded_gate(fine, (0,), (1,), independent_lift)
    missing_phase = direct.character(full, (1,), inverse=True)
    need(missing_phase != full, "omitted character must change endpoint")
    direct.split_zero_guards(missing_phase, 2)
    unguarded = [(2, 0), (-3, 2), (-2, 2), (0, 3)]
    failed = direct.guarded_gate(unguarded, (0,), (1,), independent_lift)
    need(failed != [unguarded[0], unguarded[1], unguarded[3], unguarded[2]], "unguarded direct word is not CNOT")
    # Correct endpoint permutation with missing tensor global phase is wrong.
    synthetic = dict(matrix_rows=[3, 2], offset=1, linear_Z4=[1, 2], quadratic_rows=[2, 0], phase=1)
    tag = fixtures(16, 5, random.Random(78))[0]
    no_global = deepcopy(synthetic); no_global["phase"] = 0
    need(formula(tag, synthetic, 2) != formula(tag, no_global, 2), "tensor phase mutation")
    # Literal R and R^-1 must undo on *all* integers, beyond the guarded lattice.
    arbitrary = [(i*i - 7, 3*i - 5) for i in range(16)]
    sent = direct.guarded_gate(arbitrary, (0, 1), (2, 3), independent_lift)
    need(direct.guarded_gate(sent, (0, 1), (2, 3), independent_lift, True) == arbitrary, "literal unguarded inverse")
    wrong = direct.guarded_gate(sent, (0, 1), (2, 3), independent_lift, True)
    wrong = direct.character(wrong, (2, 3))
    need(wrong != arbitrary, "extra inverse character changes restored payload")
    # The copied source is authenticated before executing any predecessor Python.
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bad.tar"
        data = bytearray((HERE / "inputs/pr3131.tar").read_bytes()); data[1000] ^= 1
        path.write_bytes(data)
        rejects(lambda: frozen.authenticated_members(path), "frozen PR3131 archive")
    # Canonical serialized comparison distinguishes false from zero.
    need(canonical({"x": False}) != canonical({"x": 0}), "typed receipt comparison")
    return ["compiled-word", "typed-phase", "layout", "overflow", "dirty-guard", "negative-shift",
            "omitted-character", "unguarded-endpoint", "tensor-global-phase", "literal-inverse",
            "source-corruption", "typed-receipt"]


def verify():
    old = frozen.load()
    Refined = executor_class(old)
    return dict(status="PASS_GUARDED_WRAPPER_REFINEMENT", seed=78,
                predecessor="0c9e344d5a5295a218558fa4a51d867f39ff5311",
                primitive_checks=primitives(old), bit_boundary=bit_boundary(), exhaustive_gate_cases=exhaustive_gates(),
                wrappers=wrapper_checks(old, Refined), collectors=collectors(old, Refined),
                controls=controls(old), invoice=dict(field_gates=52, baseline_wrapper_lifts=416,
                    refined_wrapper_lifts=104, wrapper_lift_reduction="3/4", baseline_address_oracles=104,
                    refined_address_oracles=0, refined_guard_embeddings=4, refined_guard_contractions=4),
                scope="Exact semantic wrapper refinement; inherited backend/physical premises; no new kappa")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="regenerate the package receipt")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    receipt = verify()
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.write:
        (HERE / "RESULT.json").write_text(encoded)
    else:
        need(canonical(receipt) == canonical(json.loads((HERE / "RESULT.json").read_text())), "deterministic receipt")
    if args.output:
        args.output.write_text(encoded)
    print(receipt["status"], "wrapper_lifts=416->104", "collector_cases=" + str(len(receipt["collectors"])))


if __name__ == "__main__":
    main()
