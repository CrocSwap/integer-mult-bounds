"""Source-bound finite stopped-ordinary bootstrap for this package's exact ledger.
Standard library only. --out names an external JSON receipt filename.
All-size compiler and completed-interface hypotheses remain explicitly inherited.
"""
import argparse
import ast
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCES = ("new/SPEC.json", "outer/LEDGER.json", "outer/B.json", "outer/check_ledger.py", "outer/OUTER-CLAIM.json", "code/assemble.py")

def need(condition, message):
    if not condition:
        raise ValueError(message)

def read(name):
    return json.loads((HERE / name).read_bytes())

def stage_chain(s, seed, target, levels):
    need(0 < seed < target < s < Q(1, 32), "ordered positive bootstrap rates")
    current = seed
    stages = []
    for level in range(1, levels + 1):
        previous = current
        current = (1 - s) * s + s * previous
        gaps = {"atom": s - current, "borrowing": 1 - current - s,
                "remainder": 1 - current - s * (1 - previous), "stock": 1 - s}
        need(previous < current < s, "strict finite-stage progress")
        need(all(v > 0 for v in gaps.values()), "four sufficient stage gaps")
        need(s - current == s ** level * (s - seed), "closed-form gap")
        stages.append({"level": level, "saving": str(current),
                       "gap_to_fixed_point": str(s - current),
                       "strict_gaps": {k: str(v) for k, v in gaps.items()},
                       "above_target": target < current})
    need(target < current, "finite chain must reach actual ordinary target")
    return current, stages

def rejection(fn, name):
    try:
        fn()
    except ValueError:
        return name
    raise ValueError("invalid bootstrap accepted: " + name)

def calculate():
    ledger, spec, endpoint = read("outer/LEDGER.json"), read("new/SPEC.json"), read("outer/B.json")
    row = ledger["rows"]["struct_boundary_radix_union"]
    claim = read("outer/OUTER-CLAIM.json")
    need(Q(claim["kappa_rational"]) == Q(row["kappa"]["rational"]), "actual final kappa binding")
    coarse, certified = Q(ledger["complex_lower_short"]["rational"]), Q(spec["expected"]["complex_lower"])
    q, target = Q(row["q"]["rational"]), Q(row["a"]["rational"])
    # Read the exact unchanged bit rate from the actual outer program's literal assignment.
    tree = ast.parse((HERE / "outer/check_ledger.py").read_text(encoding="utf-8"))
    assignments = [node for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "bit" for t in node.targets)]
    need(len(assignments) == 1, "unique bit endpoint assignment")
    expression = assignments[0].value
    need(isinstance(expression, ast.Call) and isinstance(expression.func, ast.Name)
         and expression.func.id == "Q" and len(expression.args) == 1
         and isinstance(expression.args[0], ast.Constant)
         and isinstance(expression.args[0].value, str), "literal exact bit endpoint")
    bit = Q(expression.args[0].value)
    need(certified == Q(claim["supplier_C"]), "actual claimed supplier binding")
    need(certified == Q(ledger["complex_lower_pinned"]["rational"]), "primitive endpoint binding")
    need(coarse == Q(endpoint["b"]), "actual ledger coarse endpoint")
    need(ledger["profile"] == spec["expected"]["global_profile"] == endpoint["profile"], "actual full paid profile")
    need(Q(endpoint["b_above_endpoint"]) > certified, "rejected endpoint is above certified one")
    need(q < target < coarse and target == (q + coarse) / 2, "actual effective ordinary rate")
    s = (target + coarse) / 2
    beta = (coarse - s) / (2 * coarse)
    seed = Q(384599, 10 ** 10)
    need(0 < seed < target < s < (1 - beta) * coarse < coarse < certified < bit < Q(1, 32),
         "retained stopped-bootstrap interface conditions")
    need(0 < beta < 1, "strict positive fixed bootstrap slack")
    current, level = seed, 0
    while current <= target:
        need(level < 4096, "bounded explicit finite witness search")
        current = (1 - s) * s + s * current
        level += 1
    final, stages = stage_chain(s, seed, target, level)
    need(all(not x["above_target"] for x in stages[:-1]), "minimal finite stage count")
    need(s ** level * (s - seed) < s - target, "sufficient power witness")
    controls = [rejection(lambda: stage_chain(s, seed, target, level - 1), "one_fewer_stage_insufficient"),
                rejection(lambda: stage_chain(s, s, target, level), "nonprogressing_seed"),
                rejection(lambda: stage_chain(s, seed, s, level), "unattained_fixed_point_target")]
    hashes = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
              for name in SOURCES + ("ordinary_bootstrap.py", "ORDINARY-BOOTSTRAP.md")}
    return {"status": "PASS_EXPLICIT_FINITE_COMPLETED_ORDINARY_BOOTSTRAP", "levels": level,
            "claimed_final_kappa": claim["kappa_rational"], "certified_complex_saving": str(certified), "coarse_complex_saving": str(coarse),
            "retained_bit_saving": str(bit), "q": str(q), "target_effective_ordinary": str(target),
            "atom_exponent": str(s), "bootstrap_beta": str(beta), "initial_ordinary_saving": str(seed),
            "final_ordinary_saving": str(final), "final_gap_above_target": str(final - target),
            "all_four_stage_gaps_strictly_positive": True, "stages": stages,
            "negative_controls": controls, "source_sha256": hashes,
            "cutoff_recipe": "At each fixed level choose its own dominating finite C_j and integer ell_j>=1 with C_j<2^ell_j. For the minimum positive stage gap delta_j use L_j=ceil(max(1,36/delta_j^2,2*(4+ell_j)/delta_j)); below width2^L_j use the previous completed ordinary algorithm. No numeric upper bound on hidden previous constants is assumed.",
            "scope": "Exact finite rational witness for the retained PR185/387 acyclic completed ordinary stopped-leaf construction. All-size compiler, internal borrowing/restoration, fixed tapes, recovery and analytic interfaces remain inherited. This finite arithmetic receipt does not assert an implementation proof of those interfaces."}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="Optional external JSON receipt filename")
    args = parser.parse_args()
    if args.out:
        target = args.out.resolve()
        need(target != HERE and HERE not in target.parents, "receipt output must be outside published package")
    result = calculate()
    need(result == read("ORDINARY-BOOTSTRAP-EXPECTED.json"), "exact expected receipt mismatch")
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"], "levels", result["levels"], "fault controls", len(result["negative_controls"]))

if __name__ == "__main__":
    main()
