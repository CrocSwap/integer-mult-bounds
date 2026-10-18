#!/usr/bin/env python3
"""Source-bound exact replay. Ross Richardson / OpenAI Codex. Apache-2.0."""
import argparse
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def load_model():
    module = types.ModuleType("signed_delivery_model")
    path = PACKAGE / "model.py"
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def sources():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    for pin in manifest["files"]:
        if pin.get("usage", "input") == "input":
            data = (ROOT / pin["path"]).read_bytes()
            if hashlib.sha256(data).hexdigest() != pin["sha256"]:
                raise ValueError("source mismatch: " + pin["path"])
    return len([p for p in manifest["files"] if p.get("usage", "input") == "input"])


def run():
    m = load_model()
    pins = sources()
    cases = 0
    states = 0
    for k in (1, 2, 3):
        for offsets in product((0, 1, 2), repeat=k):
            rows = [(1, s) for s in offsets]
            for prices in ((1,) * k, tuple(range(1, k + 1)), tuple(Fraction(2 * i + 1, 3) for i in range(k))):
                result = m.optimum(rows, (1,) * k, prices)
                t = result["balance"]
                m.need(all(sum(t[i] * rows[i][j] for i in range(k)) == 0 for j in range(2)), "nonkernel witness")
                m.need(result["source_cost"] == sum(b * m.phi(q) for b, q in zip(prices, t)), "incorrect tariff")
                m.need(result["total"] <= result["closed_total"], "closed control lost")
                cases += 1
                states += result["states"]
    rows = ((1, 0), (1, 1), (1, 2))
    result = m.optimum(rows, (1, 1, 1), (1, 1, 1))
    m.need(result["total"] == 10 and result["source_cost"] == 4, "second-difference optimum")
    m.need(tuple(map(abs, result["balance"])) == (1, 2, 1), "second-difference balance")
    # Every all-length solution in this three-row kernel is q*(1,-2,1).
    # This finite sample corroborates, and does not replace, the written proof.
    for q in range(-12, 13):
        bill = sum(m.phi(t) for t in (q, -2 * q, q))
        m.need(bill >= 4 and (bill == 4) == (abs(q) == 1), "kernel price control")
    for prices in ((1, 7, 2), (Fraction(1, 9), 2, Fraction(3, 7))):
        got = m.optimum(rows, (1,) * 3, prices)
        m.need(got["source_cost"] == Fraction(prices[0]) + 2 * Fraction(prices[1]) + Fraction(prices[2]), "weighted AP formula")
    # Characteristic-zero lift control: a binary-restored choice need not restore.
    binary_only = (1, 0, 1)
    residue = tuple(sum(binary_only[i] * rows[i][j] for i in range(3)) for j in range(2))
    m.need(residue == (2, 2), "binary/integer defect control")
    m.need(not any(all(sum(t[i] * rows[i][j] for i in range(3)) == 0 for j in range(2))
                   for t in product((-1, 0, 1), repeat=3) if any(t)), "unit-net-only obstruction")

    candidate, closed, direct = m.pilot((1, -2, 1)), m.pilot((0, 0, 0)), m.direct_pilot()
    target = m.expected()
    pilots = {}
    for name, word in (("candidate", candidate), ("closed", closed), ("direct", direct)):
        matrix, maxima, cuts = m.symbolic(word)
        m.need(matrix == target, name + " endpoint mismatch")
        for i, at_cut in cuts:
            for j in range(3):
                m.need(at_cut[6 + j] == (target[6 + j] if j <= i else m.identity()[6 + j]), "delivery cut mismatch")
        reverse = tuple((s, t, -q, i, kind) for s, t, q, i, kind in reversed(word))
        # Composition by exact basis execution covers arbitrary dirty Q/C inputs.
        for j in range(m.N):
            vector = [int(i == j) for i in range(m.N)]
            m.need(m.execute(reverse, m.execute(word, vector)) == vector, "literal inverse mismatch")
        pilots[name] = m.invoice(word)
    m.need(pilots["candidate"]["unit_adds"] == 32 and pilots["closed"]["unit_adds"] == 40 and pilots["direct"]["unit_adds"] == 14, "full scalar invoice mismatch")
    grid = m.finite_grid(candidate)
    controls = 0
    for index in range(len(candidate)):
        mutant = candidate[:index] + candidate[index + 1:]
        m.need(m.symbolic(mutant)[0] != target, "gate omission control survived")
        controls += 1
    for index in range(len(candidate)):
        source, target_port, sign, i, kind = candidate[index]
        mutant = candidate[:index] + ((source, target_port, -sign, i, kind),) + candidate[index + 1:]
        m.need(m.symbolic(mutant)[0] != target, "sign mutation control survived")
        controls += 1
    for bad in (((), (), ()), (((0, 0),), (1,), (1,)), (((1,),), (0,), (1,)), (((1,),), (1,), (-1,))):
        try:
            m.optimum(*bad)
        except ValueError:
            controls += 1
        else:
            raise ValueError("invalid contract admitted")
    return {"schema_version": 1, "status": "PASS_SIGNED_DEPENDENT_DELIVERY", "no_new_kappa": True,
            "source_input_pins": pins, "primary_optimizer_cases": cases,
            "primary_dp_states": states, "arbitrary_input_basis_columns": m.N,
            "exact_endpoint_coefficients_per_pilot": m.N ** 2,
            "dirty_grid_states": grid, "rejecting_controls": controls,
            "arithmetic_progression": {"rows": rows, "balance": (1, -2, 1),
                                       "source_queries": [1, 2, 1], "readers": [2, 2, 2],
                                       "query_tariff": 10, "closed_query_tariff": 12,
                                       "binary_only_integer_residual": residue},
            "pilot": pilots}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="explicitly regenerate RESULT.json")
    args = parser.parse_args()
    result = run()
    # Normalize tuples before the typed canonical payload comparison.
    result = json.loads(json.dumps(result))
    path = PACKAGE / "RESULT.json"
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        if json.dumps(json.loads(path.read_text()), sort_keys=True) != json.dumps(result, sort_keys=True):
            raise ValueError("complete result receipt mismatch")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
