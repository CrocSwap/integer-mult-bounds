#!/usr/bin/env python3
"""Check exact modular borrowed-port execution, recovery, and its complete bill.

Gareth Davidson (@bitplane), with substantial OpenAI Codex assistance.
Apache-2.0. Standard library only; all rejection checks survive -O.
"""
import argparse
import copy
import hashlib
import itertools
from pathlib import Path
import random
import runpy

C = runpy.run_path(str(Path(__file__).with_name("common.py")))
HERE, need, same = C["HERE"], C["need"], C["same"]
D = C["module"]("modular_dense", HERE / "dense.py")
I = C["module"]("modular_independent", HERE / "independent.py")
C["pins"]()  # Authenticate copied source bytes before executing the parent emitter.
P = C["module"]("pinned_borrowing", HERE / "vendor/pr1057/borrow.py")


def factors(n):
    result = []
    for i in range(n):
        a = [[1, 1], [0, 1]] if i % 2 == 0 else [[1, 0], [1, 1]]
        sign = -1 if (i + 52) % 7 in (0, 3) else 1
        result.append([[sign * x for x in row] for row in a])
    return result


def main_artifacts():
    _, plans, comparisons = P.unit_plan(64)
    tree, matrices = plans[51], factors(52)
    width = D.bound(matrices, 7, 7)["width"]
    word = list(P.instructions(tree))
    case = dict(format="modular-port-borrowing/1", assignment_seed=52, n=52, length=2,
                tree=tree, factors=matrices, word=word, width=width, x_bound=7, y_bound=7,
                plan_comparisons_through64=comparisons)
    program = list(D.primitive_word(word, 2))
    return case, program, plans


def admit_artifacts():
    C["pins"]()
    case, program, plans = main_artifacts()
    same(C["load"](HERE / "CASE.json.gz"), case, "complete case regeneration")
    same(C["load"](HERE / "PROGRAM.json.gz"), program, "complete primitive regeneration")
    return case, program, plans


def concrete(case, program, full_dirty_bits, sign=1):
    matrices, w, length = case["factors"], case["width"], case["length"]
    modulus = 1 << w
    rng = random.Random(52)
    entry = [[-7, 7], [7, -7]] + [[rng.randrange(modulus) if full_dirty_bits else rng.randrange(-7, 8)
                                  for _ in range(length)] for _ in range(3)]
    initial = [[x % modulus for x in row] for row in entry]
    D.admit(matrices, initial, w, 7, 7)
    word = list(P.instructions(case["tree"], sign=sign))
    if sign < 0:
        program = list(D.primitive_word(word, length))
    prefix = iter(I.concrete_prefixes(word, matrices, initial, w))
    transcript, largest = hashlib.sha256(), 0

    def observe(index, leaf, data):
        nonlocal largest
        same(list(leaf), list(word[index]), "leaf event order")
        integer, largest = next(prefix)
        same(data, [[x % modulus for x in row] for row in integer], "literal/integer prefix quotient")
        transcript.update(C["canonical"](data))

    final, execution = D.execute(program, matrices, initial, w, observe)
    need(next(prefix, None) is None, "complete independent prefix coverage")
    signed_entry = [[D.signed(x, w) for x in row] for row in initial]
    expected = I.endpoint(matrices, signed_entry, sign)
    same(final, [[x % modulus for x in row] for row in expected], "complete modular endpoint")
    same([D.signed(x, w) for x in final[1]], expected[1], "unique signed integer recovery")
    need(all(final[i] == initial[i] for i in (0, 2, 3, 4)), "bitwise dirty restoration")
    invoice = D.invoice(word, length, len(matrices), w)
    for key in ("counts", "commands", "leaves", "intercell_steps", "accesses", "head_bit_moves",
                "data_bit_actions", "work_bits"):
        same(execution[key], invoice[key], "literal/closed invoice: " + key)
    inverse = [(s, t, f, -q) for s, t, f, q in reversed(word)]
    undone, _ = D.execute(D.primitive_word(inverse, length), matrices, final, w)
    same(undone, initial, "literal inverse restores all bit patterns")
    return dict(initial=initial, final=final, signed_output=expected[1], sign=sign,
                observed_integer_prefix_peak=str(largest), observed_integer_prefix_bits=largest.bit_length() + 1,
                transcript_sha256=transcript.hexdigest(), execution=execution, invoice=invoice)


def all_tree_checks(plans):
    records, shapes_total, cases, leaves, returns = [], 0, 0, 0, 0
    for n in range(1, 8):
        digest = hashlib.sha256()
        shapes = I.shapes(n)
        shapes_total += len(shapes)
        subtotal = 0
        for shape in shapes:
            tree = I.label(shape)
            for width in (1, 2, 5):
                for sign in (1, -1):
                    word = list(P.instructions(tree, sign=sign))
                    checked = I.basis_trace(tree, factors(n), width, sign, word)
                    digest.update(C["canonical"](checked))
                    cases += 1
                    subtotal += 1
                    leaves += checked["leaves"]
                    returns += checked["recursive_returns"]
        records.append(dict(n=n, shapes=len(shapes), cases=subtotal, receipt_sha256=digest.hexdigest()))
    long_cases = []
    for n in range(8, 65):
        matrices = factors(n)
        width = D.bound(matrices, 7, 7)["width"]
        for sign in (1, -1):
            checked = I.basis_trace(plans[n - 1], matrices, width, sign,
                                    list(P.instructions(plans[n - 1], sign=sign)))
            long_cases.append(dict(n=n, width=width, sign=sign, **checked))
            cases += 1
            leaves += checked["leaves"]
            returns += checked["recursive_returns"]
    need(shapes_total == 861 and cases == 5280, "complete tree/sign/width coverage")
    return dict(shapes=shapes_total, cases=cases, leaf_prefixes=leaves,
                recursive_returns=returns, columns_per_case=10, small_trees=records, long_cases=long_cases)


def exhaustive_scalar():
    """Every raw data state and coefficient tuple for two small quotient rings."""
    rows = []
    for width, tree, n in ((2, (0, 1), 2), (1, (0, 1, 2), 3)):
        modulus, count, commands = 1 << width, 0, 0
        digest = hashlib.sha256()
        for coefficients in itertools.product(range(modulus), repeat=n):
            matrices = [[[x]] for x in coefficients]
            for sign in (1, -1):
                word = list(P.instructions(tree, sign=sign))
                program = list(D.primitive_word(word, 1))
                for state in itertools.product(range(modulus), repeat=5):
                    initial = [[x] for x in state]
                    final, receipt = D.execute(program, matrices, initial, width)
                    same(final, I.endpoint(matrices, initial, sign, modulus), "exhaustive scalar endpoint")
                    need(receipt["leaves"] == len(word), "exhaustive complete word")
                    digest.update(C["canonical"]([coefficients, sign, state, final]))
                    count += 1
                    commands += receipt["commands"]
        need(count == modulus**(n + 5) * 2, "exhaustive state coverage")
        rows.append(dict(width=width, factors=n, cases=count, commands=commands, sha256=digest.hexdigest()))
    need(sum(row["cases"] for row in rows) == 33280, "complete small quotient census")
    return rows


def additional_dense():
    """Vary dimensions, zero norms, signs and modulus widths, with exact lifting."""
    rng, cases, digest = random.Random(52), 0, hashlib.sha256()
    for length in (1, 2, 3):
        for n in (1, 2, 3, 5, 8, 13):
            for trial in range(4):
                matrices = [[[rng.randrange(-2, 3) for _ in range(length)] for _ in range(length)] for _ in range(n)]
                if trial == 0:
                    matrices[n // 2] = [[0] * length for _ in range(length)]
                tree = P.unit_plan(n)[1][-1]
                info = D.bound(matrices, 7, 7)
                w, modulus = info["width"], 1 << info["width"]
                signed_entry = [[rng.randrange(-7, 8) for _ in range(length)] for _ in range(2)]
                initial = [[x % modulus for x in row] for row in signed_entry]
                initial += [[rng.randrange(modulus) for _ in range(length)] for _ in range(3)]
                D.admit(matrices, initial, w, 7, 7)
                for sign in (1, -1):
                    word = list(P.instructions(tree, sign=sign))
                    final, receipt = D.execute(D.primitive_word(word, length), matrices, initial, w)
                    expected = I.endpoint(matrices, initial, sign, modulus)
                    same(final, expected, "dense modular endpoint")
                    signed_initial = [[D.signed(x, w) for x in row] for row in initial]
                    same([D.signed(x, w) for x in final[1]], I.endpoint(matrices, signed_initial, sign)[1],
                         "dense signed endpoint recovery")
                    invoice = D.invoice(word, length, n, w)
                    for key in ("counts", "commands", "intercell_steps", "head_bit_moves", "work_bits"):
                        same(receipt[key], invoice[key], "dense full invoice")
                    digest.update(C["canonical"]([n, length, trial, sign, info, final, receipt]))
                    cases += 1
    need(cases == 144, "dense fixture coverage")
    return dict(cases=cases, sha256=digest.hexdigest())


def controls(case, program, concrete_cases):
    rejected = []

    def reject(label, action, message):
        try:
            action()
        except ValueError as exc:
            need(message in str(exc), "wrong control rejection: " + label + ": " + str(exc))
            rejected.append(label)
        else:
            raise ValueError("negative control accepted: " + label)

    initial = concrete_cases["bounded_positive"]["initial"]
    reject("undersized endpoint allowance", lambda: D.admit(case["factors"],
           [[x % (1 << (case["width"] - 1)) for x in row] for row in initial], case["width"] - 1, 7, 7),
           "signed recovery guard")
    reject("signed guard equality", lambda: D.admit([[[1]]], [[0]] * 5, 2, 1, 1), "signed recovery guard")
    need(D.bound([[[0]]], 2, 0)["width"] == 3, "zero factor still needs representable external input")
    reject("zero product hides unrepresentable input", lambda: D.admit([[[0]]], [[0]] * 5, 1, 2, 0),
           "signed recovery guard")
    reject("unjustified input bound", lambda: D.admit([[[1]]], [[1], [0], [0], [0], [0]], 4, 0, 0), "input bound")
    reject("noncanonical dirty input", lambda: D.admit([[[1]]], [[0], [0], [16], [0], [0]], 4, 0, 0),
           "canonical data residues")
    for value, label in ((0.5, "rounded fractional leaf"), (True, "boolean coefficient")):
        reject(label, lambda x=value: D.bound([[[x]]], 1, 1), "integer matrix coefficients")
    reject("aliased ports", lambda: list(D.primitive_word([(1, 1, 0, 1)], 1)), "leaf ports")
    reject("global input used as target", lambda: list(D.primitive_word([(1, 0, 0, 1)], 1)), "leaf ports")
    matrices, small_initial, w = [[[2]], [[3]]], [[1], [0], [7], [5], [3]], 7
    word = list(P.instructions((0, 1)))

    def boundary(changed):
        final, _ = D.execute(D.primitive_word(changed, 1), matrices, small_initial, w)
        same(final, I.endpoint(matrices, small_initial, 1, 1 << w), "dirty endpoint")

    reject("omitted helper restoration", lambda: boundary(word[:2] + word[3:]), "dirty endpoint")
    wrong = list(word)
    s, t, f, q = wrong[-1]
    wrong[-1] = s, t, f, -q
    reject("wrong inverse sign", lambda: boundary(wrong), "dirty endpoint")
    final, _ = D.execute(D.primitive_word(word, 1), matrices, small_initial, w)
    wrong_inverse = [(s, t, f, -q) for s, t, f, q in word]
    bad_final, _ = D.execute(D.primitive_word(wrong_inverse, 1), matrices, final, w)
    reject("negation without reversal", lambda: same(bad_final, small_initial, "inverse order"), "inverse order")
    small_program = list(D.primitive_word([(0, 1, 0, 1)], 1))
    no_low = list(small_program)
    no_low.remove(("low", "p"))
    reject("unpaid product reduction", lambda: D.execute(no_low, [[[3]]], [[15], [0], [0], [0], [0]], 4),
           "unsigned work overflow")
    long_program = [x for x in D.primitive_word([(0, 1, 0, 1)], 3) if x != ("low", "a")]
    reject("unpaid accumulator reductions", lambda: D.execute(long_program, [[[15] * 3 for _ in range(3)]],
           [[1] * 3] + [[0] * 3 for _ in range(4)], 4), "unsigned work overflow")
    no_clear = list(small_program)
    last_c = max(i for i, x in enumerate(no_clear) if x == ("zero", "c"))
    no_clear[last_c] = ("low", "c")
    reject("uncleared private coefficient work", lambda: D.execute(no_clear, [[[3]]], [[1], [0], [0], [0], [0]], 4),
           "private work not cleared")
    invoice = copy.deepcopy(concrete_cases["bounded_positive"]["invoice"])
    invoice["counts"]["low"] -= 1
    reject("undercharged reductions", lambda: same(invoice["counts"],
           concrete_cases["bounded_positive"]["execution"]["counts"], "reduction invoice"), "reduction invoice")
    # The quotient ring endpoint is exact, yet decoding cannot identify an out-of-range integer.
    wrapped, _ = D.execute(D.primitive_word([(0, 1, 0, 1)], 1), [[[3]]], [[3], [3], [0], [0], [0]], 4)
    need(wrapped[1] == [12] and D.signed(12, 4) == -4, "out-of-range witness")
    reject("modular success does not imply integer recovery", lambda: D.admit([[[3]]],
           [[3], [3], [0], [0], [0]], 4, 3, 3), "signed recovery guard")
    # Saturation is not reduction modulo 2^w; integer division by two does not descend to this quotient.
    sat = lambda x: max(-8, min(7, x))
    x, y, z = 1, 0, 7
    z = sat(z + 2 * x)
    y = sat(y + 2 * z)
    z = sat(z - 2 * x)
    y = sat(y - 2 * z)
    need((y, z) == (-3, 5), "saturation witness")
    reject("saturation loses restoration", lambda: same([y, z], [4, 7], "saturation endpoint"), "saturation endpoint")
    need(1 % 4 == 5 % 4 and (1 // 2) % 4 != (5 // 2) % 4, "division does not descend")
    rounded_delta = (1 + 1) // 2 - 1 // 2
    need(rounded_delta == 1 and 1 // 2 == 0, "dirty-dependent rounded echo")
    stress = concrete_cases["dirty_bits_positive"]
    need(stress["observed_integer_prefix_bits"] > case["width"], "actual overflow stress required")
    reject("unreduced integer lift in endpoint-sized registers", lambda: need(
           int(stress["observed_integer_prefix_peak"]) < 1 << (case["width"] - 1), "integer prefix overflow"),
           "integer prefix overflow")
    return dict(rejected=rejected, out_of_range=dict(true_integer=12, residue=12, decoded=-4, width=4),
                saturation=dict(target=y, helper=z, wanted_target=4, wanted_helper=7),
                half_division=dict(congruent_lifts=[1, 5], modulus=4, outputs=[0, 2],
                                   rounded_echo_increment=1, wanted_increment=0))


def historical_comparison(case):
    n, length, width = case["n"], case["length"], case["width"]
    h = P.norm_bound(case["tree"], 2)
    rows = {}
    for name, dirty_bound in (("all_entry_cells_bounded_7", 7),
                               ("arbitrary_signed_width_bit_dirt", 1 << (width - 1))):
        p = max(2, dirty_bound * h).bit_length() + 1
        rows[name] = dict(entry_bound=dirty_bound, inherited_sufficient_width=p,
                          data_bits=5 * length * p, coefficient_bits=n * length * length * p,
                          scalar_work_bits=4 * p,
                          commands=len(case["word"]) * (4 * length * length + 4 * length + 4) + 4)
    need(rows["all_entry_cells_bounded_7"]["inherited_sufficient_width"] == 114
         and rows["arbitrary_signed_width_bit_dirt"]["inherited_sufficient_width"] == 167,
         "credited sufficient-width comparison")
    return dict(norm_majorant=str(h), comparison=rows, minimality_claim=False)


def admit_certificate(case, program):
    """Fast envelope/invoice checks before the complete mathematical replay."""
    receipt = C["load"](HERE / "CERTIFICATE.json")
    same(receipt["sources"], C["pins"](), "certificate source binding")
    same(receipt["case_sha256"], C["digest"](case), "case digest")
    same(receipt["program_sha256"], C["digest"](program), "program digest")
    same(receipt["endpoint_bound"], D.bound(case["factors"], 7, 7), "endpoint allowance")
    same(receipt["historical"], historical_comparison(case), "historical sufficient widths")
    for name, row in receipt["concrete"].items():
        sign = -1 if name.endswith("negative") else 1
        same(row["sign"], sign, "concrete sign")
        invoice = D.invoice(list(P.instructions(case["tree"], sign=sign)), 2, 52, case["width"])
        same(row["invoice"], invoice, "complete invoice")
        for key in ("counts", "commands", "leaves", "intercell_steps", "accesses", "head_bit_moves",
                    "data_bit_actions", "work_bits"):
            same(row["execution"][key], invoice[key], "literal receipt invoice")
    same(sorted(receipt["concrete"]), ["bounded_negative", "bounded_positive",
                                     "dirty_bits_negative", "dirty_bits_positive"], "concrete inventory")
    same({k: receipt["all_trees"][k] for k in ("shapes", "cases", "columns_per_case")},
         dict(shapes=861, cases=5280, columns_per_case=10), "matrix coverage declaration")
    need(receipt["no_new_kappa"] is True, "scope declaration")
    return receipt


def run(write_artifacts=False):
    manifest = C["pins"]()
    if write_artifacts:
        case, program, plans = main_artifacts()
    else:
        case, program, plans = admit_artifacts()
        admit_certificate(case, program)
    print("52-factor literal backend: every prefix, signed recovery, inverse and full invoice", flush=True)
    concrete_cases = {name: concrete(case, program, dirty, sign) for name, dirty, sign in (
        ("bounded_positive", False, 1), ("bounded_negative", False, -1),
        ("dirty_bits_positive", True, 1), ("dirty_bits_negative", True, -1))}
    need(case["width"] == 56 and len(case["word"]) == 1376, "primary fixture")
    print("861 trees and all parent plans through64: quotient maps and every recursive return", flush=True)
    trees = all_tree_checks(plans)
    print("exhaust every scalar state and coefficient tuple in the declared two quotient rings", flush=True)
    scalar = exhaustive_scalar()
    additional = additional_dense()
    negatives = controls(case, program, concrete_cases)
    # Credited predecessor's 56-factor fixture, with its exact same leaf count.
    old_tree = plans[55]
    predecessor = dict(n=56, leaf_calls=len(list(P.instructions(old_tree))),
                       inherited_width=(7 * P.norm_bound(old_tree, 2)).bit_length() + 1,
                       modular_width=D.bound(factors(56), 7, 7)["width"])
    same(predecessor, dict(n=56, leaf_calls=1568, inherited_width=119, modular_width=60),
         "credited 56-factor comparison")
    receipt = dict(status="PASS_MODULAR_PORT_BORROWING", sources=manifest,
                   case_sha256=C["digest"](case), program_sha256=C["digest"](program),
                   endpoint_bound=D.bound(case["factors"], 7, 7), concrete=concrete_cases,
                   all_trees=trees, scalar_exhaustion=scalar, additional_dense=additional,
                   controls=negatives, historical=historical_comparison(case),
                   predecessor56=predecessor, no_new_kappa=True)
    if write_artifacts:
        C["write"](HERE / "CASE.json.gz", case)
        C["write"](HERE / "PROGRAM.json.gz", program)
        C["write"](HERE / "CERTIFICATE.json", receipt)
    else:
        same(receipt, C["load"](HERE / "CERTIFICATE.json"), "complete deterministic certificate")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-artifacts", action="store_true", help="initial production; refuses existing artifacts")
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    receipt = run(args.write_artifacts)
    if args.receipt:
        C["write"](args.receipt, receipt)
    print("PASS_MODULAR_PORT_BORROWING: 52 factors; 1376 calls; 56-bit data; "
          "5280 matrix cases; 33280 scalar states; 144 dense cases; paid reductions; no new kappa")


if __name__ == "__main__":
    main()
