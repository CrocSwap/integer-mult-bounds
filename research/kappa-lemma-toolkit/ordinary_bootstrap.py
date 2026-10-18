"""Exact finite completed-ordinary bootstrap for this package's modern ledger.

Standard library only; no file writes unless --out names an external receipt.
The retained all-size completed-interface construction is stated in
ORDINARY-BOOTSTRAP.md. Finite arithmetic is not an all-size implementation proof.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PINS = {
    "outer/outer/LEDGER.json": "493001fe310faabfbef65dafc62778f93499021bd830c22cb5c9eb0653eb7c96",
    "outer/ENDPOINT.json": "5f14f9a2faf15754be54b7de238425409fcd8e2e61635e2d7796714bc4abaa51",
    "outer/SPEC.json": "f626f1d563e770a052fbfc8cd855721be8bf561d8293a7f1fed0c4595f5264e6",
    "PRICE-EXPECTED.json": "04a6590a13950655e7ba21f6aefeba24fba51dc8f914cf136b0ff2903c8f0a87",
    "OWNERS.json.gz": "11a8742b501446c258ef4a1fa423ec2f8c041135c94f4d82356f7bd6f7da3d1c",
    "Recursion.lean": "098ecce913798bf932a613a578b453f67b96309f479b9099c09caafb23d2d59d",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(name):
    return json.loads((HERE / name).read_bytes())


def stage_chain(s, seed, target, levels):
    need(0 < seed < target < s < Q(1, 32), "ordered positive bootstrap rates")
    ordinary = seed
    stages = []
    for level in range(1, levels + 1):
        previous = ordinary
        ordinary = (1 - s) * s + s * previous
        gaps = {
            "atom": s - ordinary,
            "borrowing": 1 - ordinary - s,
            "remainder": 1 - ordinary - s * (1 - previous),
            "stock": 1 - s,
        }
        need(previous < ordinary < s, "strict finite-stage progress")
        need(all(value > 0 for value in gaps.values()), "all four sufficient stage gaps")
        need(s - ordinary == s ** level * (s - seed), "exact closed-form gap")
        stages.append({
            "level": level,
            "saving": str(ordinary),
            "gap_to_fixed_point": str(s - ordinary),
            "strict_gaps": {key: str(value) for key, value in gaps.items()},
            "above_target": target < ordinary,
        })
    need(target < ordinary, "finite stages must reach the actual ordinary target")
    return ordinary, stages


def rejection(function, label):
    try:
        function()
    except ValueError:
        return label
    raise ValueError("invalid bootstrap accepted: " + label)


def calculate():
    hashes = {}
    for name, expected in PINS.items():
        hashes[name] = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        need(hashes[name] == expected, "source drift: " + name)
    ledger = read("outer/outer/LEDGER.json")
    endpoint = read("outer/ENDPOINT.json")
    spec = read("outer/SPEC.json")
    price = read("PRICE-EXPECTED.json")
    row = ledger["rows"]["struct_boundary_radix_union"]
    coarse = Q(ledger["complex_lower_short"]["rational"])
    certified = Q(ledger["complex_lower_pinned"]["rational"])
    q = Q(row["q"]["rational"])
    target = Q(row["a"]["rational"])
    bit = Q(price["inherited_bit_saving"])
    need(certified == Q(endpoint["complex_lower"]) == Q(price["certified_complex_saving"]),
         "actual primitive rate binding")
    need(Q(spec["supplier"]["certified_complex_saving"]) == certified,
         "specification primitive rate binding")
    need(bit == Q(spec["supplier"]["bit_lower"]), "actual bit endpoint binding")
    need(spec["supplier"]["owners_sha256"] == hashes["OWNERS.json.gz"], "actual owner binding")
    need(price["source_sha256"]["kappa-lemma-toolkit/OWNERS.json.gz"] == hashes["OWNERS.json.gz"],
         "price owner binding")
    need(price["profile"] == spec["expected"]["global_profile"], "complete paid profile binding")
    need(ledger["profile"] == spec["expected"]["global_profile"], "ledger paid profile binding")
    digits = spec["outer_refinement"]["endpoint_digits"]
    reserve = Q(1, 10 ** (digits + 80))
    need(digits == 8 and certified == Q("0.00168358"), "this fixed DIG8 witness")
    need(coarse == certified - reserve and q == coarse - reserve, "actual free-gap family")
    need(target == (q + coarse) / 2, "actual effective ordinary rate")
    s = (target + coarse) / 2
    beta = (coarse - s) / (2 * coarse)
    seed = Q(384599, 10 ** 10)
    need(0 < seed < target < s < (1 - beta) * coarse < coarse < certified < bit < Q(1, 32),
         "retained stopped-coarse bootstrap rate conditions")
    need(0 < beta < 1, "strictly positive finite bootstrap slack")
    ordinary, stages = stage_chain(s, seed, target, 31)
    need(all(not stage["above_target"] for stage in stages[:-1]), "earlier stages below this target")
    need(Q(stages[-2]["saving"]) < target, "stage30 below actual target")
    need(ordinary - target > Q(8, 10 ** 90), "strict final sufficient gap")
    need(s ** 31 * (s - seed) < s - target, "Lean power-bound sufficient witness")
    controls = [
        rejection(lambda: stage_chain(s, seed, target, 7), "seven_stages_insufficient"),
        rejection(lambda: stage_chain(s, s, target, 31), "nonprogressing_seed"),
        rejection(lambda: stage_chain(s, seed, s, 31), "target_at_unattained_fixed_point"),
    ]
    for name in ("ordinary_bootstrap.py", "ORDINARY-BOOTSTRAP.md"):
        hashes[name] = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
    return {
        "status": "PASS_EXPLICIT_31_LEVEL_COMPLETED_ORDINARY_BOOTSTRAP",
        "levels": 31,
        "certified_complex_saving": str(certified),
        "coarse_complex_saving": str(coarse),
        "retained_bit_saving": str(bit),
        "q": str(q),
        "target_effective_ordinary": str(target),
        "atom_exponent": str(s),
        "bootstrap_beta": str(beta),
        "initial_ordinary_saving": str(seed),
        "final_ordinary_saving": str(ordinary),
        "final_gap_above_target": str(ordinary - target),
        "previous_stage_below_target": True,
        "all_four_stage_gaps_strictly_positive": True,
        "stages": stages,
        "negative_controls": controls,
        "source_sha256": hashes,
        "supporting_source_commits": {
            "PR185_head": "561d6ecbbeb94a11b67862ccedd32bfcbad2cae0",
            "reviewed_PR185_copy_and_PR387_proof": "d9fb9410b1ae6f6ada376a1e7fd12bc176e476ea",
        },
        "cutoff_recipe": "At each fixed level choose its own dominating finite C_j and integer ell_j>=1 with C_j<2^ell_j. For the minimum positive stage gap delta_j use L_j=ceil(max(1,36/delta_j^2,2*(4+ell_j)/delta_j)); below width2^L_j use the previous completed ordinary algorithm. No actual constant is assumed below2^512.",
        "scope": "Exact finite rational witness for31 acyclic levels of the retained PR185/387 completed ordinary stopped-leaf construction. All-size compiler, internal borrowing/restoration, fixed tapes, recovery and analytic interfaces remain inherited. The new universal bootstrap algebra is separately Lean-audited; this arithmetic receipt is not an all-size implementation proof.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="Optional receipt outside the published research package")
    args = parser.parse_args()
    if args.out:
        target = args.out.resolve()
        published = HERE.parent.resolve()
        need(target != published and published not in target.parents,
             "receipt output must be outside the published package")
    result = calculate()
    need(result == read("ORDINARY-BOOTSTRAP-EXPECTED.json"), "exact expected bootstrap receipt mismatch")
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    print(result["status"], "levels", result["levels"], "fault controls", len(result["negative_controls"]))


if __name__ == "__main__":
    main()
