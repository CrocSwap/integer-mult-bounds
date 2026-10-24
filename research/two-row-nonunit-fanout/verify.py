#!/usr/bin/env python3
"""Exact bounded corroboration, separate graph oracle, and byte bindings.

Krzysztof Wójt; substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys
import types
from fractions import Fraction


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BOUND_FILES = (
    "README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
    "tariff.py", "shortest_path.py", "verify.py",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_source(name, filename):
    """Execute these exact .py bytes, without consulting a bytecode cache."""
    module = types.ModuleType(name)
    module.__file__ = str(HERE / filename)
    sys.modules[name] = module
    exec(compile((HERE / filename).read_bytes(), module.__file__, "exec"), module.__dict__)
    return module


def bindings():
    local = {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest()
             for name in BOUND_FILES}
    manifest = json.loads((HERE/"SOURCES.json").read_text())
    inputs = [row for row in manifest["files"] if row["usage"] == "input"]
    expected = "research/unit-ring-dirty-fanout/README.md"
    require([row["path"] for row in inputs] == [expected], "unexpected live source set")
    for row in inputs:
        digest = hashlib.sha256((ROOT/row["path"]).read_bytes()).hexdigest()
        require(digest == row["sha256"], "predecessor source bytes changed")
    return {"local_sha256": local, "input_sha256": {r["path"]: r["sha256"] for r in inputs}}


def check_ring(ring):
    elements = range(ring.size)
    require(ring.zero != ring.one, "zero ring is excluded")
    for a in elements:
        require(ring.add(a, ring.zero) == a and ring.add(ring.zero, a) == a,
                "additive identity")
        require(ring.mul(a, ring.one) == a and ring.mul(ring.one, a) == a,
                "multiplicative identity")
        require(ring.add(a, ring.neg(a)) == ring.zero, "additive inverse")
        for b in elements:
            require(0 <= ring.add(a, b) < ring.size and 0 <= ring.mul(a, b) < ring.size,
                    "operation closure")
            require(ring.add(a, b) == ring.add(b, a), "additive commutativity")
            for c in elements:
                require(ring.add(ring.add(a, b), c) == ring.add(a, ring.add(b, c)),
                        "additive associativity")
                require(ring.mul(ring.mul(a, b), c) == ring.mul(a, ring.mul(b, c)),
                        "multiplicative associativity")
                require(ring.mul(a, ring.add(b, c)) ==
                        ring.add(ring.mul(a, b), ring.mul(a, c)), "left distributivity")
                require(ring.mul(ring.add(a, b), c) ==
                        ring.add(ring.mul(a, c), ring.mul(b, c)), "right distributivity")


def endpoint_matches(t, ring, word, demand):
    # Every gate uses left coefficients and is right-module linear. These
    # three columns suffice; literal finite dirt is checked separately.
    for column in range(3):
        state = tuple(ring.one if k == column else ring.zero for k in range(3))
        got = t.execute(ring, word, state)
        target = (ring.add(state[0], ring.mul(demand[0], state[2])),
                  ring.add(state[1], ring.mul(demand[1], state[2])), state[2])
        if got != target or t.execute(ring, t.inverse(word, ring), got) != state:
            return False
    return True


def check_constructions(t):
    rings = [t.modular_ring(q) for q in (2, 3, 4, 5, 6, 8, 9)]
    rings += [t.binary_dual_ring(), t.binary_matrix_ring()]
    counts = {"rings": len(rings), "comparable_pairs": 0, "incomparable_pairs": 0,
              "candidate_words": 0, "coefficient_columns_with_inverse": 0,
              "literal_dirty_states_with_inverse": 0}
    prices = t.Prices((Fraction(7, 3), Fraction(31, 5)), (Fraction(5, 7), Fraction(13, 11)))
    for ring in rings:
        check_ring(ring)
        for demand in itertools.product(range(ring.size), repeat=2):
            comparable = any(ring.quotient(demand[i], demand[1-i]) is not None
                             for i in (0, 1))
            if not comparable:
                try:
                    t.optimal_plan(ring, demand, prices)
                except ValueError as exc:
                    require("incomparable" in str(exc), "wrong domain rejection")
                else:
                    raise ValueError("incomparable demand accepted")
                counts["incomparable_pairs"] += 1
                continue
            counts["comparable_pairs"] += 1
            for plan in t.candidates(ring, demand, prices):
                require(endpoint_matches(t, ring, plan.word, demand),
                        f"wrong full endpoint: {ring.name}, {demand}, {plan.name}")
                require(plan.price == t.word_price(plan.word, prices), "wrong word price")
                counts["candidate_words"] += 1
                counts["coefficient_columns_with_inverse"] += 3
            plan = t.optimal_plan(ring, demand, prices)
            require(plan.price == t.lower_envelope(ring, demand, prices), "wrong envelope")
    fixtures = [(t.modular_ring(4), (2, 1), t.Prices((1, 9), (1, 1))),
                (t.modular_ring(4), (2, 1), t.Prices((100, 1000), (1, 1))),
                (t.modular_ring(8), (0, 2), t.Prices((1, 20), (1, 2))),
                (t.binary_dual_ring(), (2, 1), t.Prices((1, 9), (1, 1))),
                (t.binary_matrix_ring(), (11, 1), t.Prices((1, 20), (10, 1)))]
    for ring, demand, prices in fixtures:
        plan = t.optimal_plan(ring, demand, prices)
        for state in itertools.product(range(ring.size), repeat=3):
            target = (ring.add(state[0], ring.mul(demand[0], state[2])),
                      ring.add(state[1], ring.mul(demand[1], state[2])), state[2])
            got = t.execute(ring, plan.word, state)
            require(got == target, "literal dirty endpoint")
            require(t.execute(ring, t.inverse(plan.word, ring), got) == state, "literal inverse")
            counts["literal_dirty_states_with_inverse"] += 1
    return counts


def check_shortest_paths(t, oracle):
    price_vectors = sorted(set(itertools.product((1, 2, 3), repeat=4)) | {
        (1, 9, 1, 1), (100, 1000, 1, 1), (1, 100, 100, 1),
        (100, 1, 1, 100), (9, 4, 7, 1), (4, 9, 1, 7),
    })
    counts = {"moduli": [2, 3, 4, 5, 8, 9], "price_vectors_per_modulus": len(price_vectors),
              "searches": 0, "target_cost_comparisons": 0, "settled_states": 0,
              "transition_scans": 0, "replayed_oracle_paths": 0}
    digest = hashlib.sha256()
    for q in counts["moduli"]:
        ring = t.modular_ring(q)
        for vector in price_vectors:
            prices = t.Prices(vector[:2], vector[2:])
            result = oracle.shortest_prices(q, vector[:2], vector[2:])
            require(result["stats"]["settled_targets"] == q*q, "incomplete oracle search")
            for demand, price in sorted(result["costs"].items()):
                plan = t.optimal_plan(ring, demand, prices)
                require(plan.price == price, f"shortest-path discrepancy {q, vector, demand}")
                digest.update(json.dumps([q, vector, demand, price], separators=(",", ":")).encode()+b"\n")
                counts["target_cost_comparisons"] += 1
            counts["searches"] += 1
            counts["settled_states"] += result["stats"]["settled_states"]
            counts["transition_scans"] += result["stats"]["transition_scans"]
    for vector in ((1, 9, 1, 1), (100, 1000, 1, 1)):
        result = oracle.shortest_prices(4, vector[:2], vector[2:], include_paths=True)
        for demand, path in result["paths"].items():
            word = tuple(t.Gate(a[0], a[1], a[-1]) for a in path)
            require(endpoint_matches(t, t.modular_ring(4), word, demand), "oracle path endpoint")
            require(t.word_price(word, t.Prices(vector[:2], vector[2:])) == result["costs"][demand],
                    "oracle path price")
            counts["replayed_oracle_paths"] += 1
    counts["ordered_optimum_sha256"] = digest.hexdigest()
    return counts


def check_controls(t, oracle):
    passed = []
    ring = t.modular_ring(4)
    repeat = t.optimal_plan(ring, (2, 1), t.Prices((1, 9), (1, 1)))
    mixed = t.optimal_plan(ring, (2, 1), t.Prices((100, 1000), (1, 1)))
    require(repeat.price == 4 and repeat.name == "repeat-0", "credited nonunit boundary")
    require(mixed.price == 104 and mixed.name == "mix-0", "new mixing regime")
    require(min(100+1000, 1000+2, 2*100+2) > mixed.price,
            "forest-and-repeat-only counterexample lost")
    passed.extend(("credited_Z4_optimum_four", "mixing_beats_forests_and_repeat"))
    require(not endpoint_matches(t, ring, repeat.word[1:], (2, 1)), "omitted preparation accepted")
    require(not endpoint_matches(t, ring, mixed.word[:-1], (2, 1)), "unreturned dirt accepted")
    wrong_sign = (t.Gate("add", 0, ring.neg(mixed.word[0].coefficient)),) + mixed.word[1:]
    require(not endpoint_matches(t, ring, wrong_sign, (2, 1)), "wrong sign accepted")
    passed.extend(("omitted_preparation", "unreturned_dirt", "wrong_mixing_sign"))
    noncomm = t.binary_matrix_ring()
    require(noncomm.mul(1, 11) == 3 and noncomm.mul(11, 1) == 1, "noncommuting fixture")
    wrong = (t.Gate("add", 1, 1), t.Gate("source", 0, 11), t.Gate("add", 1, 1))
    require(not endpoint_matches(t, noncomm, wrong, (11, 1)), "wrong multiplication order accepted")
    require(noncomm.quotient(2, 1) is None and noncomm.mul(1, 2) == 2,
            "left/right ideal discriminator lost")
    passed.extend(("wrong_noncommutative_ratio", "left_versus_right_ideal"))
    require(t.optimal_plan(ring, (0, 0), t.Prices((1, 9), (1, 1))).price == 0,
            "zero demands should have an empty word")
    zero_anchor = t.optimal_plan(ring, (0, 1), t.Prices((1, 9), (1, 1)))
    require(zero_anchor.price == 4 and endpoint_matches(t, ring, zero_anchor.word, (0, 1)),
            "zero-demand anchor was incorrectly excluded")
    passed.extend(("zero_demands", "zero_demand_temporary_anchor"))
    invalid = [lambda: t.modular_ring(True), lambda: t.modular_ring(1),
               lambda: t.Prices((True, 1), (1, 1)), lambda: t.Prices((0, 1), (1, 1)),
               lambda: t.Prices((1.0, 1), (1, 1)),
               lambda: t.optimal_plan(ring, (True, 1), t.Prices((1, 1), (1, 1))),
               lambda: t.optimal_plan(t.modular_ring(6), (2, 3), t.Prices((1, 1), (1, 1))),
               lambda: t.execute(ring, (t.Gate("clear", 0, 1),), (0, 0, 0)),
               lambda: t.execute(ring, (t.Gate("add", True, 1),), (0, 0, 0)),
               lambda: oracle.shortest_prices(4, (True, 1), (1, 1))]
    for operation in invalid:
        try:
            operation()
        except (ValueError, TypeError):
            continue
        raise ValueError("invalid-domain control was accepted")
    return {"semantic_controls": passed, "invalid_input_controls": len(invalid)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path, help="write a new receipt; never overwrite")
    args = parser.parse_args()
    bound = bindings()
    receipt_path = HERE/"RESULT.json"
    previous = None
    if args.write_receipt is None:
        previous = json.loads(receipt_path.read_text())
        require(previous.get("bindings") == bound, "receipt source hashes differ")
    elif args.write_receipt.exists():
        raise ValueError("receipt output already exists")
    t = load_source("two_row_tariff", "tariff.py")
    oracle = load_source("two_row_shortest_path", "shortest_path.py")
    report = {"schema": "two-row-nonunit-fanout/v1", "bindings": bound,
              "construction": check_constructions(t), "shortest_paths": check_shortest_paths(t, oracle),
              "controls": check_controls(t, oracle), "new_kappa": False}
    canonical = json.dumps(report, sort_keys=True, indent=2) + "\n"
    if args.write_receipt is not None:
        with args.write_receipt.open("x", encoding="utf-8") as stream:
            stream.write(canonical)
    else:
        require(canonical == json.dumps(previous, sort_keys=True, indent=2)+"\n",
                "typed receipt content differs from the exact replay")
    print("PASS_TWO_ROW_NONUNIT_FANOUT", json.dumps({k: v for k, v in report.items()
          if k not in ("bindings", "schema")}, sort_keys=True))


if __name__ == "__main__":
    main()
