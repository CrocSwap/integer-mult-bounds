# SPDX-License-Identifier: Apache-2.0
"""Replay the power-20 ledger at the tightened source mean on the original paid word."""
from fractions import Fraction as Q
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
GRID = HERE.parent / "grid/RESULT.json"
PRIOR = HERE / "MINIMUM.json"
SCREEN = HERE / "mean_screen.py"
CAP = "0.00387992804549430"
CLAIM = "0.00387992804541"
HASHES = {
    "APPLICATION.json": "fd110bf3a3d6ed204f3b312bcd72aedc444806b3821515fd4220b3ba327037f1",
    "AUDIT.json": "001afbe125635833bafb8c5f1b313700d25370b5bf4dfc68983f53220197cacd",
    "adapter/binary/FINITE.json": "fbac738cff45668dd51bf77f5786bf2dc5539910fe5aa5ee8865bed6e15c15b0",
}


def component(base, grid, prior, screen, proof, stages, check):
    power, height, mean = 20, 1804, Q(749, 1000)
    check((screen["p"], screen["h"], Q(screen["new_mean"]), screen["maximum_coefficients"])
          == (power, height, mean, power + 1), "frozen single power-20 test")
    raw, eps = Q(grid["mean_upper"]), Q(grid["epsilon_upper"])
    complete = (raw + eps) / (1 + eps)
    check((proof["p"], proof["h"], proof["atoms"], Q(proof["mean"])) == (power, height, 452, mean)
          and 0 <= raw <= complete < mean and raw == Q(screen["raw_mean_upper"]) == Q(proof["raw_mean_upper"])
          and eps == Q(screen["full_positive_surcharge_ratio_upper"]) == Q(proof["epsilon_upper"])
          and complete == Q(screen["complete_mean_upper"]) == Q(proof["completed_mean_upper"]),
          "admitted paid and completed mean")
    lower, upper = map(Q, base["uniform"]["eta"])
    beta = Q(23, 20)
    check(prior["p"] == 21 and prior["uniform_J"] == 825 and prior["h"] == height
          and (Q(3, 4)/beta)**power == Q(prior["rejected_limit"]) == Q(proof["prior_rejected_limit"]) > upper >= lower
          and (mean/beta)**power == Q(screen["limiting_ratio"]) < lower,
          "same old limiting control and strict new limiting test")
    moments = list(map(Q, screen["moments"]))
    rows = screen["coefficient_ratios"]
    check(set(rows) == {str(j) for j in range(power + 1)} and len(moments) == power + 1
          and moments[:2] == [1, mean] and moments == list(map(Q, proof["moments"])),
          "all 21 upper moments agreed with independent atom reconstruction")
    ratios = [Q(rows[str(j)]) for j in range(power + 1)]
    peak = max(ratios)
    check(ratios == list(map(Q, proof["coefficients"])) and min(ratios) >= 0
          and ratios[-1] == (mean/beta)**power and peak == Q(proof["worst_upper"])
          and ratios.index(peak) == proof["worst_index"] and peak < Q(screen["uniform_lambda"]) < lower,
          "all 21 rational coefficients and all-height contraction")
    H, J = base["uniform"]["H"], 786
    loss = Q(J, H)
    check((height**power << (J-1)) <= (H+height)**power < (height**power << J)
          and loss*(H+height) > 2*power and proof["uniform_J"] == J
          and Q(proof["uniform_loss"]) == loss, "terminal and tail costs")
    stages(base, loss, CAP, check)
    cost, claim, old = screen["price"], Q(CLAIM), Q(prior["candidate_grid_claim"])
    ceiling = Q(base["raw_crossing"][1]) - Q(825, H) - Q(7, 10**14)
    check(cost["passes"] and cost["J"] == J and Q(cost["cap"]) == Q(CAP) and proof["cap"] == CAP
          and list(map(Q, cost["stages"])) == [Q(value) for value, margin in proof["stages"]]
          and claim == Q(cost["claim"]) == Q(proof["candidate_grid_claim"])
          and Q(cost["tested"]) == Q(proof["candidate_tested"]) and claim > ceiling > old
          and ceiling == Q(cost["old_relaxed_ceiling"]) == Q(proof["old_cover_forgiven_upper"])
          and claim-ceiling == Q(cost["separation"]) == Q(proof["separation"])
          and claim-old == Q(proof["absolute_gain"]) == Q(3, 10**14)
          and Q(proof["exact_relative_percent"]) == 100*(claim-old)/old,
          "new signed claim separates from the relaxed power-21 ceiling")
    return {"installed": CAP, "old_fixed_loss_ceiling": str(ceiling)}


def run(source, work, legacy, stages, base):
    check, digest = legacy["check"], legacy["digest"]
    check(digest(SCREEN) == "6aa3a209952502b341e784c0f4d216d619835f177de695f5aa91d8fed0aa41ba"
          and digest(PRIOR) == "2c7692f263da6ccaacb7054471aff9d8a693371e8dcb3b83390d70a7bcff4d10"
          and digest(GRID) == "69c8f917d6b2676897639eef67e8f15aae1c23a6bfb608dcd38aed236f299818"
          and digest(HERE / "MEAN.json") == "41a80ef6b08339dd146791d5a22a7472de8a8ab651b35f25a0282a4ee751295e",
          "source-mean screen, power-21 parent and exact grid ledger")
    rebuilt = source / "replay/BIT-451.json"
    check(digest(rebuilt) == legacy["BASE_RECEIPT"] == digest(source / "BIT-451.json"), "signed BIT control")
    primary = work / "mean-tensor-screen.json"
    subprocess.run([sys.executable, "-IB", SCREEN, "--bit-source", rebuilt, "--round336-receipt", GRID,
                    "--round338-receipt", PRIOR, "--previous-screen", HERE / "minimum_screen.py",
                    "--out", primary], check=True)
    proof = json.loads((HERE / "MEAN.json").read_bytes())
    bound = component(base, json.loads(GRID.read_bytes()), json.loads(PRIOR.read_bytes()),
                      json.loads(primary.read_bytes()), proof, stages, check)
    outer = work / "mean-tensor-consumer"
    full = legacy["consumer"](source, outer, bound, cap=CAP, expected_claim=CLAIM, expected_hashes=HASHES)
    audited = work / "mean-tensor-audit.json"
    subprocess.run([sys.executable, "-IB", HERE / "mean_audit.py", source, GRID, PRIOR, audited,
                    "--outer", outer], check=True)
    check(audited.read_bytes() == (HERE / "MEAN.json").read_bytes()
          and Q(full["tested"]) == Q(proof["candidate_tested"]) and Q(full["delta"]) == Q(195, 10**14),
          "independent tightened-mean proof and complete signed consumer")
    print("PASS_COMPLETE_TENSOR_MEAN", f"claim={full['claim']}", f"delta_vs_p21={proof['absolute_gain']}",
          f"delta_vs_7863={full['delta']}", flush=True)
    return full
