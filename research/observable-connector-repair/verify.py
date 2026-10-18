#!/usr/bin/env python3
"""Recompute the scoped certificate and failure controls. Apache-2.0.

Hanson Sun, with substantial OpenAI Codex assistance. Standard library only.
"""
import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import model
import oracle


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rejected(fn):
    try:
        fn()
    except ValueError:
        return True
    raise ValueError("negative control was accepted")


def source_pins():
    refs = json.loads((HERE / "PREDECESSORS.json").read_text())
    for r in refs["references"]:
        b = (HERE / r["retained_path"]).read_bytes()
        require(hashlib.sha256(b).hexdigest() == r["sha256"], "predecessor SHA256 mismatch")
        require(hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest() == r["git_blob"],
                "predecessor Git blob mismatch")
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            raw = (HERE.parents[1] / row["path"]).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == row["sha256"], "live source drift")
    return {"base": sources["base_commit"], "predecessor_notes": len(refs["references"])}


def exhaustive_small():
    """All six scalar demands per stage, length zero through four, two tariffs."""
    options = list(itertools.product(range(1, 4), (0, 1)))
    cases = 0
    digest = hashlib.sha256()
    for n in range(5):
        for conditions in itertools.product(options, repeat=n):
            for weights in ([1, 1], [2, 5]):
                for output_prices in (None, [3 + i % 2 for i in range(n)]):
                    plan = model.solve(2, conditions, weights, output_prices)
                    cost, dual = oracle.shortest(2, conditions, weights, output_prices)
                    require(plan["cost"] == cost, "small-instance oracle disagreement")
                    oracle.validate_dual(2, conditions, weights, output_prices, dual, cost)
                    if n <= 3:
                        candidates = []
                        for path in itertools.product(range(4), repeat=n):
                            defects = [b ^ oracle.parity(a, k, 2) for (a, b), k in zip(conditions, path)]
                            if output_prices is None and any(defects):
                                continue
                            nodes = (0,) + path + (0,)
                            bill = sum(sum(weights[j] for j in range(2) if (p ^ q) & (2 ** j))
                                       for p, q in zip(nodes, nodes[1:]))
                            if output_prices is not None:
                                bill += sum(p * w for p, w in zip(defects, output_prices))
                            candidates.append(bill)
                        require(min(candidates) == cost, "enumerated mask routes disagree")
                    digest.update(json.dumps([conditions, weights, output_prices, cost], separators=(",", ":")).encode() + b"\n")
                    cases += 1
    return {"demand_sequences": sum(6 ** n for n in range(5)), "tariff_mode_cases": cases,
            "maximum_stages": 4, "width": 2, "result_sha256": digest.hexdigest()}


def array_evidence(spec, words):
    cases = columns = cuts = 0
    for word in words.values():
        count = word["registers"]
        for L in (1, 2, 3):
            for j in range(count * L):
                state = [[0] * L for _ in range(count)]
                state[j // L][j % L] = 1
                expected = oracle.direct(spec, state, L)
                result, observed = oracle.run_array(spec, word, state, L)
                require(result == expected, "literal basis mismatch")
                restored, _ = oracle.run_array(spec, word, result, L, backwards=True)
                require(restored == state, "literal inverse mismatch")
                columns += 1
                cuts += observed
                cases += 1
            actual = oracle.literal_invoice(word, L)
            bill = model.invoice(word)
            for field, coefficients in (("head_steps", bill["head_steps_polynomial"]),
                                        ("online_tariff", bill["online_tariff_polynomial"])):
                require(actual[field] == coefficients["L2"] * L * L + coefficients["L"] * L,
                        "literal movement/access invoice disagreement")
    tiny = {"width": 2, "B": [3, 2], "readers": [1, 3], "steps": [0, 0]}
    dc = [(x["reader"], x["demand"]) for x in model.demands(tiny)]
    plan = model.solve(2, dc, [1, 1], [1, 1])
    word = model.emit(tiny, "planned", plan)
    for mask in range(2 ** word["registers"]):
        state = [[(mask >> j) & 1] for j in range(word["registers"])]
        out, observed = oracle.run_array(tiny, word, state)
        require(out == oracle.direct(tiny, state), "small exhaustive dirty mismatch")
        back, _ = oracle.run_array(tiny, word, out, backwards=True)
        require(back == state, "small exhaustive inverse mismatch")
        cuts += observed
        cases += 1
    return {"pilot_basis_columns_forward_and_inverse": columns,
            "literal_cases": cases, "tiny_all_dirty_inputs": 2 ** word["registers"],
            "observation_checks": cuts, "block_lengths": [1, 2, 3]}


def controls(spec, plans, words, conditions, dual):
    passed = []

    def control(name, fn):
        rejected(fn)
        passed.append(name)

    def omitted(kind, last=False):
        word = copy.deepcopy(words["mixed"])
        choices = [i for i, g in enumerate(word["gates"]) if g[2] == kind]
        del word["gates"][choices[-1] if last else choices[0]]
        word["cuts"] = []
        model.check_word(spec, word)

    control("omit_output_correction", lambda: omitted("output_repair"))
    control("omit_terminal_connector_correction", lambda: omitted("connector_repair", True))
    control("omit_final_B_entry", lambda: omitted("B", True))
    control("omit_reader_prewrite", lambda: omitted("reader"))
    control("omit_source_restoration_entry", lambda: omitted("source", True))
    bad = copy.deepcopy(plans["mixed"])
    bad["path"][0] = 1
    control("wrong_observable_coset", lambda: model.emit(spec, "planned", bad))
    bad_dual = copy.deepcopy(dual)
    bad_dual[1][0] += 100
    control("corrupt_lower_bound_potential", lambda: oracle.validate_dual(4, conditions, [1] * 4, [1] * 8, bad_dual, 3))
    control("negative_gate_price", lambda: model.solve(4, conditions, [-1, 1, 1, 1]))
    control("out_of_range_reader", lambda: model.solve(2, [(4, 0)], [1, 1]))
    control("infeasible_zero_reader", lambda: model.solve(2, [(0, 1)], [1, 1]))
    bad_spec = copy.deepcopy(spec)
    bad_spec["steps"] = bad_spec["steps"][:-1]
    bad_spec["readers"] = bad_spec["readers"][:-1]
    control("unrestored_source_tour", lambda: model.demands(bad_spec))
    word = words["mixed"]
    state = [1 << j for j in range(word["registers"])]
    for t, s, kind in word["gates"]:
        if kind != "reader":
            break
        state[t] ^= state[s]
    future = 2 * spec["width"] + 1 + len(spec["readers"]) - 1
    require(state[future] != 1 << future, "early-output observation guard not witnessed")
    passed.append("early_future_output_is_not_canonical")
    require(plans["strict"]["path"][0] != model.demands(spec)[0]["coherent_mask"], "strong-boundary distinction lost")
    require(model.invoice(words["direct"])["scalar_xors"] < model.invoice(words["mixed"])["scalar_xors"],
            "alphabet restriction control lost")
    passed.extend(["strong_coherence_is_not_asserted", "direct_product_fusion_is_cheaper"])
    return passed


def build():
    pins = source_pins()
    spec = model.selected()
    require(spec["B"] == [8, 13, 6, 2] and spec["readers"] == [9, 6, 4, 11, 15, 2, 3, 14]
            and spec["steps"] == [3, 2, 1, 0, 3, 2, 1, 0], "seed fixture drift")
    ds = model.demands(spec)
    conditions = [(x["reader"], x["demand"]) for x in ds]
    plans, optimality = {}, {}
    for name, weights, out in (
        ("strict", [1] * 4, None),
        ("mixed", [1] * 4, [1] * 8),
        ("strict_quadratic", [11, 13, 15, 17], None),
        ("mixed_quadratic", [11, 13, 15, 17], [19 + 2 * i for i in range(8)]),
        ("mixed_tariff_L1", [17, 19, 21, 23], [25 + 2 * i for i in range(8)]),
    ):
        plan = model.solve(4, conditions, weights, out)
        price, dual = oracle.shortest(4, conditions, weights, out)
        require(plan["cost"] == price, "pilot oracle disagreement")
        edges = oracle.validate_dual(4, conditions, weights, out, dual, price)
        plans[name] = plan
        optimality[name] = {"potential": dual, "checked_edges": edges, "minimum": price}
    require(plans["strict"]["path"] == plans["strict_quadratic"]["path"], "strict all-L common witness")
    require(plans["mixed"]["path"] == plans["mixed_quadratic"]["path"]
            == plans["mixed_tariff_L1"]["path"], "mixed all-L common witness")
    require(plans["strict"]["cost"] == 4 and plans["mixed"]["cost"] == 3, "pilot optimum drift")
    words = {name: model.emit(spec, name) for name in ("eager", "coherent", "output_only", "direct")}
    words.update({name: model.emit(spec, "planned", plans[name]) for name in ("strict", "mixed")})
    semantic = {name: model.check_word(spec, word) for name, word in words.items()}
    return {"schema_version": 1, "status": "SCOPED_EXACT_INTERFACE_NO_NEW_KAPPA", "source_pins": pins,
            "spec": spec, "demands": ds, "plans": plans, "optimality": optimality,
            "words": words, "invoices": {name: model.invoice(word) for name, word in words.items()},
            "symbolic_semantics": semantic, "array_evidence": array_evidence(spec, words),
            "small_exhaustion": exhaustive_small(),
            "controls": controls(spec, plans, words, conditions, optimality["mixed"]["potential"])}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", type=Path, help="authoring only: export to a new file, not certificate acceptance")
    args = ap.parse_args()
    result = build()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        with args.write.open("x") as out:
            out.write(encoded)
        print("EXPORTED_SCOPED_CERTIFICATE (not acceptance against committed certificate)")
        return
    expected = json.loads((HERE / "CERTIFICATE.json").read_text())
    require(result == expected, "committed certificate mismatch")
    print("PASS_OBSERVABLE_CONNECTOR strict=4 mixed=3 coherent=14 "
          "complete_xors=72_to_61 small_cases=6220 controls=14 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise SystemExit("FAIL_OBSERVABLE_CONNECTOR: " + str(exc))
