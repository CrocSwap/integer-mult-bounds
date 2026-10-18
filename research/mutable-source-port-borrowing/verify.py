#!/usr/bin/env python3
"""Rebuild the scoped certificate; default execution never writes artifacts."""
import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random

import engine
import oracle

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def check_sources():
    pins = json.loads((HERE / "PREDECESSORS.json").read_text())
    expected = {
        "references/PR1057-" + name for name in ("README.md", "PROOF.md", "NOTICE.md", "borrow.py")
    } | {
        "references/PR" + str(pr) + "-" + name
        for pr in (1159, 1164) for name in ("PROOF.md", "NOTICE.md")
    }
    require(len(pins) == len(expected) and {p["local"] for p in pins} == expected,
            "missing or duplicate predecessor source")
    for pin in pins:
        path = HERE / pin["local"]
        require(path.resolve().is_relative_to(HERE), "source outside package")
        data = path.read_bytes()
        require(hashlib.sha256(data).hexdigest() == pin["sha256"], "predecessor SHA256 drift")
        header = ("blob " + str(len(data)) + "\0").encode()
        require(hashlib.sha1(header + data).hexdigest() == pin["git_blob"], "predecessor Git blob drift")
    return len(pins)


def load_predecessor():
    spec = importlib.util.spec_from_file_location("pinned_borrow1057", HERE / "references/PR1057-borrow.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reject(function, message):
    try:
        function()
    except (ValueError, TypeError):
        return
    raise ValueError("negative control accepted: " + message)


def semantic_controls():
    _, trees, _ = engine.plan(16)
    word = engine.emit(trees["M"])
    controls = []

    def bad_word(label, candidate):
        reject(lambda: oracle.free_replay(candidate, 16), label)
        controls.append(label)

    bad_word("omit final restoration leaf", word[:-1])
    wrong_sign = list(word)
    s, t, f, q = wrong_sign[-1]
    wrong_sign[-1] = (s, t, f, -q)
    bad_word("wrong final inverse sign", wrong_sign)
    bad_word("reverse factor order", [(s, t, 15 - f, q) for s, t, f, q in word])
    bad_word("discard source-targeted work", [r for r in word if r[1] != 0])
    reject(lambda: engine.emit(trees["M"], mutable_source=False), "protected source capacity")
    controls.append("protected pool rejects mutable optimum")
    reject(lambda: engine.validate_word([(0, 0, 0, 1)], 1), "aliased leaf ports")
    controls.append("aliased leaf ports")
    reject(lambda: engine.emit((0, 0)), "duplicated factor")
    controls.append("duplicated factor")
    reject(lambda: engine.emit(trees["M"], sign=True), "boolean direction")
    controls.append("boolean direction")
    free = oracle.free_replay(word, 16)
    require(free["source_changed"], "source-observation control is vacuous")
    controls.append("source prefix differs despite restored endpoint")

    n = 11
    _, trees, _ = engine.plan(n)
    nonlinear_word = engine.emit(trees["M"])
    bank = [[[v]] for v in (3, 3, 1, 1, 1, 1, 3, 1, 3, 1, 1)]
    dirty = [[1], [14], [6], [12], [8]]
    after = oracle.dense_reference(nonlinear_word, bank, dirty, 16, nonlinear=True)
    require(after == [[1], [7], [4], [12], [8]], "nonlinear witness drift")
    require(after[2:] != dirty[2:], "nonlinear restoration failure disappeared")
    require(oracle.dense_reference(engine.inverse(nonlinear_word), bank, after, 16, nonlinear=True) == dirty,
            "nonlinear literal inverse control failed")
    controls.append("nonlinear helper corruption despite reversible leaves")

    # Residues alone do not identify an unbounded signed result.
    small_word = engine.emit((0, 1))
    small_bank = [[[2]], [[2]]]
    small_input = [[1], [0], [3], [1], [2]]
    wrapped, _ = engine.dense_execute(small_word, small_bank, small_input, 2)
    require(wrapped[1] == [0] and oracle.direct_endpoint(small_bank, small_input)[1] == [4],
            "integer-recovery width control failed")
    controls.append("undersized modulus loses integer output")
    return dict(count=len(controls), checks=controls, nonlinear=dict(n=n, matrices=bank, before=dirty, after=after))


def exhaustive_small():
    receipt = []
    total_words = total_events = 0
    for n in range(1, 8):
        candidates = oracle.shapes(n)
        best_mutable = best_readonly = None
        valid_readonly = 0
        for tree in candidates:
            independent = oracle.independent_word(tree)
            require(independent == engine.emit(tree), "emitter disagreement")
            for sign in (1, -1):
                word = independent if sign == 1 else engine.inverse(independent)
                oracle.free_replay(word, n, sign)
                total_words += 1
                total_events += 2 * len(word)  # forward and literal inverse
            best_mutable = min(best_mutable or len(independent), len(independent))
            try:
                read_only = oracle.independent_word(tree, protected=True)
            except ValueError:
                reject(lambda: engine.emit(tree, mutable_source=False), "invalid protected tree")
                continue
            valid_readonly += 1
            require(read_only == engine.emit(tree, mutable_source=False), "protected emitter disagreement")
            for sign in (1, -1):
                word = read_only if sign == 1 else engine.inverse(read_only)
                facts = oracle.free_replay(word, n, sign)
                require(not facts["source_changed"], "protected source changed")
                total_words += 1
                total_events += 2 * len(word)
            best_readonly = min(best_readonly or len(read_only), len(read_only))
        bills, _, _ = engine.plan(n)
        require((best_mutable, best_readonly) == (bills["M"][-1], bills["R"][-1]), "tree optimum disagreement")
        receipt.append(dict(factors=n, trees=len(candidates), protected_admissible=valid_readonly,
                            mutable_minimum=best_mutable, protected_minimum=best_readonly))
    return dict(domain="every ordered arity-2/3/4 tree through seven factors; both signs and inverses",
                rows=receipt, words=total_words, leaf_events=total_events)


def all_port_coverage():
    cases = events = 0
    for n in range(1, 6):
        for tree in oracle.shapes(n):
            for src in range(5):
                for dst in range(5):
                    if src == dst:
                        continue
                    word = engine.emit(tree, src=src, dst=dst)
                    require(word == oracle.independent_word(tree, src=src, dst=dst), "relocated child emitter mismatch")
                    for sign in (1, -1):
                        oriented = word if sign > 0 else engine.inverse(word)
                        oracle.free_replay(oriented, n, sign, src=src, dst=dst)
                        cases += 1
                        events += 2 * len(oriented)
    return dict(cases=cases, leaf_events=events,
                domain="all 20 distinct immediate-port pairs; every tree through five factors; both signs and inverse")


def fixture(n, kind):
    bills, trees, _ = engine.plan(n)
    word = engine.emit(trees[kind], mutable_source=(kind == "M"))
    require(word == oracle.independent_word(trees[kind], protected=(kind != "M")), "fixture word disagreement")
    require(len(word) == bills[kind][n], "fixture call bill disagreement")
    free_positive = oracle.free_replay(word, n)
    free_negative = oracle.free_replay(engine.inverse(word), n, -1)
    bank = engine.factor_bank(n)
    require(any(engine.matmul(a, b) != engine.matmul(b, a) for a, b in zip(bank, bank[1:])),
            "main fixture lacks noncommuting adjacent factors")
    width = engine.endpoint_width(bank)
    modulus = 1 << width
    signed_input = [[3, -7], [2, 5]]
    initial = [[v % modulus for v in row] for row in signed_input]
    initial += [[modulus - 1, modulus // 2 + 3], [modulus // 3, modulus - 7], [modulus // 2, modulus // 5]]
    result, stats = engine.dense_execute(word, bank, initial, width)
    require(result == oracle.direct_endpoint(bank, initial, modulus=modulus), "modular fixture endpoint failed")
    require(result == oracle.dense_reference(word, bank, initial, modulus), "matrix oracle disagreement")
    original_signed = signed_input + [[0, 0] for _ in range(3)]
    integer_target = oracle.direct_endpoint(bank, original_signed)[1]
    decoded = [v if v < modulus // 2 else v - modulus for v in result[1]]
    require(decoded == integer_target, "signed integer recovery failed")
    inverse_result, inverse_stats = engine.dense_execute(engine.inverse(word), bank, result, width)
    require(inverse_result == initial, "dense inverse failed")
    for actual, literal in ((stats, word), (inverse_stats, engine.inverse(word))):
        closed = oracle.closed_invoice(literal, n, 2, width)
        require(all(actual[key] == value for key, value in closed.items()), "closed invoice disagrees")
    require(stats["data_head_steps"] == inverse_stats["data_head_steps"], "orientation travel differs")
    # The integer lift uses the same arbitrary residue representatives. It
    # is an independent congruence check; its large intermediates are not
    # stored by the modular implementation.
    lifted = oracle.dense_reference(word, bank, initial)
    require([[x % modulus for x in r] for r in lifted] == result, "integer/residue disagreement")
    return dict(factors=n, kind=kind, tree=trees[kind], word_sha256=digest(word),
                bank=bank, width=width, initial=initial, final=result,
                integer_output=integer_target, stats=stats,
                free_positive=free_positive, free_negative=free_negative)


def dense_coverage():
    rng = random.Random(51)
    cases = commands = 0
    for n in (1, 2, 4, 8, 11, 16):
        _, trees, _ = engine.plan(n)
        for kind in ("R", "M"):
            forward = engine.emit(trees[kind], mutable_source=(kind == "M"))
            for length in (1, 2, 3):
                bank = engine.factor_bank(n, length)
                for width in (1, 3, 7):
                    modulus = 1 << width
                    states = []
                    for column in range(5 * length):
                        state = [[0] * length for _ in range(5)]
                        state[column // length][column % length] = 1
                        states.append(state)
                    states.append([[rng.randrange(modulus) for _ in range(length)] for _ in range(5)])
                    for sign in (1, -1):
                        word = forward if sign == 1 else engine.inverse(forward)
                        for initial in states:
                            actual, stats = engine.dense_execute(word, bank, initial, width)
                            expected = oracle.direct_endpoint(bank, initial, sign, modulus)
                            require(actual == expected, "dense basis/dirty endpoint mismatch")
                            require(actual == oracle.dense_reference(word, bank, initial, modulus), "dense interpreter mismatch")
                            closed = oracle.closed_invoice(word, n, length, width)
                            require(all(stats[k] == v for k, v in closed.items()), "dense coverage invoice mismatch")
                            cases += 1
                            commands += stats["commands"]
    # Every dirty scalar state over Z/4Z for one nontrivial borrowed word.
    _, trees, _ = engine.plan(11)
    word = engine.emit(trees["M"])
    bank = engine.factor_bank(11, 1)
    scalar_states = 0
    for flat in itertools.product(range(4), repeat=5):
        initial = [[v] for v in flat]
        require(oracle.dense_reference(word, bank, initial, 4) == oracle.direct_endpoint(bank, initial, modulus=4),
                "exhaustive quotient-ring state failed")
        scalar_states += 1
    return dict(literal_cases=cases, literal_commands=commands, exhaustive_scalar_states=scalar_states,
                domain="n=1,2,4,8,11,16; L=1,2,3; w=1,3,7; R/M; both signs; all basis columns plus seeded dirt")


def rebuild():
    sources = check_sources()
    predecessor = load_predecessor()
    bills, _, candidates = engine.plan(56)
    independent_bills, independent_transitions = oracle.independent_minima(56)
    require(bills == independent_bills, "min-plus oracle cost table mismatch")
    old_bills, old_trees, _ = predecessor.unit_plan(56)
    require(old_bills == bills["T"], "PR1057 comparator table mismatch")
    for n in (51, 56):
        _, trees, _ = engine.plan(n)
        require(trees["T"] == old_trees[n - 1], "PR1057 tie-broken plan mismatch")
    require((bills["R"][51], bills["M"][51], bills["R"][56], bills["M"][56]) == (1040, 928, 1248, 1088),
            "main fixture costs changed")
    fixtures = [fixture(n, k) for n in (51, 56) for k in ("T", "R", "M")]
    for n in (51, 56):
        r = next(f for f in fixtures if f["factors"] == n and f["kind"] == "R")
        m = next(f for f in fixtures if f["factors"] == n and f["kind"] == "M")
        require(r["width"] == m["width"] and r["stats"]["data_bits"] == m["stats"]["data_bits"], "unequal comparison width/cap")
        for field in ("commands", "data_head_steps", "data_bit_actions", "program_bits", "dispatches", "address_events"):
            require(m["stats"][field] < r["stats"][field], "completed backend did not improve " + field)
        require(m["stats"]["source_changed"] and not r["stats"]["source_changed"], "source contract distinction missing")
    return dict(schema_version=1, status="scoped recursive-interface construction; no new kappa",
                assignment_seed=51, predecessor_inputs=sources, cost_tables=bills, planner_candidates=candidates,
                independent_minplus_transitions=independent_transitions,
                small_trees=exhaustive_small(), all_ports=all_port_coverage(),
                fixtures=fixtures, dense=dense_coverage(), controls=semantic_controls())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", type=Path, help="explicit developer-only output path; never overwrites")
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    args = parser.parse_args()
    result = rebuild()
    if args.write_certificate:
        with args.write_certificate.open("x") as handle:
            json.dump(result, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
    else:
        saved = json.loads(args.certificate.read_text())
        require(canonical(saved) == canonical(result), "certificate differs from recomputed mathematical evidence")
    print("PASS_MUTABLE_SOURCE_PORT_BORROWING seed=51 rows=5 n51=1040->928 n56=1248->1088 controls="
          + str(result["controls"]["count"]) + " no_new_kappa")


if __name__ == "__main__":
    main()
