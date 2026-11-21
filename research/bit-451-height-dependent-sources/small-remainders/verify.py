# SPDX-License-Identifier: Apache-2.0
"""Verify the directed small-remainder estimate and its complete signed price."""
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
from shutil import copyfile
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CAP = "0.00387992804562487"
CLAIM = "0.00387992804554"
CELLS = (("a","3/4","5/6"),("b","5/6","11/12"),("c","11/12","23/24"),("d","23/24","1"))


def check(ok, message):
    if not ok:
        raise ValueError(message)


def load(path):
    return json.loads(path.read_bytes())


def compare(screen, proof, coefficients):
    check(screen["decision"] == "ADVANCE_ONE_COMPLETE_REPLAY" and proof["decision"].startswith("PASS")
          and (proof["p"], proof["h"]) == (16,1804), "frozen positive power-16 comparison")
    check(screen["coverage"] == {"direct_checked":128,"direct_unvisited":0,"coefficients_checked":85,
                                 "coefficients_unvisited":0}, "128 exact heights and 85 coefficient indices")
    n = screen["nonroot"]
    check(n["raw_labels"] == 107460 and 0 <= F(n["low_share_upper"]) < 1 and 0 <= F(proof["small_mass_upper"]) < 1
          and min(F(n[key]) for key in ("pointwise_lower","middle_lower","old_high_lower")) > 6
          and min(F(proof[key]) for key in ("small_L","mid_L","high_L_reused")) > 6,
          "all three nonroot regimes under the full original paid invoice")
    check(F(proof["limiting_ratio"]) < F(proof["base_capacity"]) and proof["negative_control_old_capacity_fails"]
          and min(F(proof["small_x"]),F(screen["low_root_lower"])) > 6,
          "new root bound and insufficient old multiplier")
    check(coefficients(screen["newton"]["low"],17) == list(map(F,proof["small_x_coefficient_ratios"])),
          "low-cell comparison at every height")
    for name,left,right in CELLS:
        branch = proof["cells"][right]
        height_rows = screen["explicit"][name]
        check(left == branch["left"] == screen["cells"][name]["l"] and right == screen["cells"][name]["u"],
              "input-size cell endpoints")
        check(set(branch["rows"]) == {str(i) for i in range(32)}
              and coefficients(height_rows,32) == [F(branch["rows"][str(i)][0]) for i in range(32)],
              "all 32 first heights for "+name)
        check(coefficients(screen["newton"][name],17) == list(map(F,branch["tail"])),
              "all translated tail coefficients for "+name)
    price = screen["price"]
    check(price["passed"] and price["base"] and price["tail"] and price["carrier"]
          and price["J"] == proof["uniform_J"] == 629 and F(proof["uniform_loss"]) == F(629,1202400000000000)
          and [s[0] for s in price["stages"]] == proof["stages"] and len(proof["stages"]) == 7,
          "terminal charge, carrier and seven ordinary stages")
    check(CAP == proof["cap"] and F(price["cap"]) == F(CAP)
          and F(price["claim"]) == F(proof["candidate_grid_claim"]) == F(CLAIM)
          and F(price["tested"]) == F(proof["candidate_tested"]) == F("0.00387992804561"),
          "full signed rate")
    ceiling = F(proof["old_relaxed_ceiling"])
    check(ceiling == F(price["old_ceiling"]) and F(CLAIM)-ceiling == F(price["separation"])
          == F(proof["separation"]) == F(19,1800000000000000)
          and F(price["change"]) == F(proof["absolute_gain"]) == F(3,10**14), "strict old ceiling separation")


def run(source, work, legacy, stages, base, known_good, signed_receipt, coefficients):
    predecessor = HERE.parent/"three-cells"
    for relative, path in {
        "round344/primary/receipt.json": work/"three-cell-primary.json",
        "round344/independent/receipt.json": work/"three-cell-independent.json",
        "round344/independent/outer-verified.json": predecessor/"SIGNED.json",
    }.items():
        dest = work/relative
        dest.parent.mkdir(parents=True,exist_ok=True)
        copyfile(path,dest)
    primary = work/"small-remainder-primary.json"
    subprocess.run([sys.executable,"-IB",HERE/"screen.py","--campaign-root",work,"--out",primary],
                   check=True,timeout=65)
    independent = work/"small-remainder-independent.json"
    subprocess.run([sys.executable,"-IB",HERE/"audit.py",work,independent],check=True,timeout=55)
    check(independent.read_bytes() == (HERE/"RESULT.json").read_bytes(), "fresh independent scientific receipt")
    proof = load(independent)
    compare(load(primary),proof,coefficients)
    signed = load(HERE/"SIGNED.json")
    check(sha256(independent.read_bytes()).hexdigest() == signed["new_component_sha256"]
          and signed["old_component_sha256"] == sha256((predecessor/"RESULT.json").read_bytes()).hexdigest(),
          "signed binding to fresh p16 and prior p17 certificate")
    signed_receipt(work/"three-cell-consumer",known_good,signed["known_good"],"0.00387992804551")
    stages(base,F(proof["uniform_loss"]),CAP,check)
    result = work/"small-remainder-consumer"
    bound = {"installed":CAP, "old_fixed_loss_ceiling":proof["old_relaxed_ceiling"]}
    new = legacy["consumer"](source,result,bound,cap=CAP,expected_claim=CLAIM,
                             expected_hashes=signed["signed"]["output_sha256"])
    signed_receipt(result,new,signed["signed"],CLAIM)
    check(signed["known_good"]["orientations"] == signed["signed"]["orientations"]
          and F(new["delta"]) == F(208,10**14), "same signed caller and exact peer comparison")
    print("PASS_COMPLETE_SMALL_REMAINDER_SOURCE", f"claim={new['claim']}", f"delta_vs_p17={proof['absolute_gain']}",
          f"delta_vs_7863={new['delta']}", flush=True)
