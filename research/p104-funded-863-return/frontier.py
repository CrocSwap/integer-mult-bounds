# SPDX-License-Identifier: Apache-2.0
"""Derive a proposed frontier claim and independently check the actual outer rows."""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SELECTED = "certificates/frontier7000/CLAIM.json"
OUTER = "research/final4610-independent-admission/checks/outer.py"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_bytes())


def actual_copy_guard(program, n, owned):
    rows = [{r: Q(1)} if r < n else {} for r in range(n + owned)]
    for event in program:
        op, r = event[:2]
        if op == "COPY":
            require(not rows[r], "Actual COPY destination is dirty")
            return
        if op in ("INIT", "CLEAR"):
            rows[r] = {}
        elif op == "SCALE":
            q = Q(event[-2])
            rows[r] = {j: q*x for j, x in rows[r].items()}
        elif op == "ADD":
            q = Q(event[-2])
            for j, x in rows[event[2]].items():
                value = rows[r].get(j, 0) + q*x
                if value:
                    rows[r][j] = value
                else:
                    rows[r].pop(j, None)
    raise ValueError("Missing actual COPY")


def check_copy_control():
    raw = gzip.decompress((HERE / "WORD.json.gz").read_bytes())
    require(sha256(raw).hexdigest() == read(HERE / "NATIVE-RESULT.json")["word_canonical_sha256"], "Exact candidate word")
    word = json.loads(raw)
    program = word["program"]
    indexes = [i for i, e in enumerate(program) if e[0] == "COPY"]
    require(len(indexes) == 1, "One literal COPY")
    i = indexes[0]
    n, owned = word["public"], word["owned_fields"]
    actual_copy_guard(program, n, owned)
    _, dst, src, _, chart = program[i]
    corrupt = [*program[:i], ["ADD", dst, src, "1", chart], *program[i:]]
    try:
        actual_copy_guard(corrupt, n, owned)
    except ValueError as error:
        require(str(error) == "Actual COPY destination is dirty", "Actual dirty-COPY rejection")
    else:
        raise ValueError("Actual COPY mutation was accepted")


def run():
    pins = {x["path"]: x["sha256"] for x in read(HERE / "SOURCES.json")["files"]}
    for name in (SELECTED, OUTER):
        require(sha256((ROOT / name).read_bytes()).hexdigest() == pins[name], "Exact selected application source")
    selected = read(ROOT / SELECTED)
    check_copy_control()
    receipt = read(HERE / "RESULT.json")
    gate = receipt["price"]["gate"]
    k, C = Q(gate["claim"]), Q(gate["tested"])
    gap = (C - k) / 7
    require(k > Q(".003645669928698") > Q(selected["kappa"]) and gap > 0, "Strict improvement and funded gap")
    bit = Q(selected["complex_BIT_premise"])
    require(Q(selected["admitted_BIT_saving"]) > bit > C, "Admitted BIT covers the fixed premise")
    evaluator = runpy.run_path(str(ROOT / OUTER))
    params = evaluator["parameters"](k, C) | {"bit_saving": bit}
    proof = evaluator["evaluate"](params)
    strict, functional = proof["strict_checks"], proof["functional_checks"]
    require(proof["all_positive"] and len(strict) == 54 and len(functional) == 4, "Every outer predicate")
    epsilon, beta = 1-gap, 1-3*gap
    a, q = k+4*gap, k+3*gap
    xi = epsilon*(1+q)-Q(3,32)+gap
    savings = {
        "main_transform": epsilon*q, "global_coordinate_router": a,
        "fused_gaussian": 1-epsilon+q*beta, "group_bit_router": 1-epsilon+a*beta,
        "group_scans": 1-epsilon+beta, "boundary_algebraic_matrix": Q(3,32)+xi-epsilon,
        "sparse_union_movement": xi+Q(1,2)-epsilon, "polynomial_products": epsilon,
        "microbox_face_corrections": 1-(epsilon+beta+48-128+2),
    }
    require(savings == proof["margins"] and min(savings, key=savings.get) == "main_transform", "Nine independent outer savings")
    low = min(savings.values())
    require(low > k, "Strict limiting outer slack")
    for test in (a, a-Q(1,10**12)):
        negative = evaluator["evaluate"](params | {"bit_saving": test})
        require(not negative["all_positive"] and negative["strict_checks"]["actual_bit_above_effective"] == test-a,
                "Actual outer checker rejects insufficient BIT")
    after, before = (receipt["price"][k] for k in ("after", "before"))
    for key, wanted in (("T", {"4":17, "9":-17}), ("P", {"1":17, "6":-17})):
        actual = {r: after[key].get(r,0)-before[key].get(r,0)
                  for r in after[key].keys() | before[key].keys()
                  if after[key].get(r,0) != before[key].get(r,0)}
        require(actual == wanted, "Every actual signed occurrence: " + key)
    require(receipt["price"]["price"]["baseline_rejects_new_claim"], "Complete #7277 bill rejects candidate price")
    require(sum(after["T"].values()) == 22461 and sum(after["P"].values()) == 110536 and
            after["S"] == 1424 and after["empty_root_credits"] == 0, "Complete actual signed invoice")
    return selected | {
        "kappa": str(k),
        "source_result": "research/p104-funded-863-return/RESULT.json",
        "uniform_templates": [dict(family="complex", rank_encoding="2^"+str(gate["H"]), saving=str(k+6*gap), ambient=153),
                              selected["uniform_templates"][1]],
        "nine_outer_savings": {name: str(x) for name, x in savings.items()},
        "outer_formula_source": OUTER,
        "limiting_outer_saving": str(low),
        "strict_limiting_slack": str(low-k),
        "scope": "Conditional application of the funded helper-863 return and exact #7113 signed caller. Maintainer selection, a materialized multiplier and formal-kernel acceptance remain open.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    result = run()
    if args.out:
        with args.out.open("x") as f:
            json.dump(result, f, indent=2)
            f.write("\n")
    else:
        require(result == read(HERE / "PROPOSED-CLAIM.json"), "Every frozen frontier proposal field")
    print("PASS_FUNDED_863_RETURN_FRONTIER_PROPOSAL", result["kappa"], flush=True)


if __name__ == "__main__":
    main()
