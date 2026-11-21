# SPDX-License-Identifier: Apache-2.0
"""Verify the minimum integer power for the frozen paid tensor moment envelope."""
from fractions import Fraction as Q
import json
from pathlib import Path
import runpy
import subprocess
import sys

HERE = Path(__file__).resolve().parent
PRIOR = HERE/"RESULT.json"
SCREEN = HERE/"minimum_screen.py"
CAP = "0.00387992804546187"
CLAIM = "0.00387992804538"
HASHES = {
    "APPLICATION.json": "43a9c277ebd2578286cf9d3147db662684bbdad070ac69613622389c5e721073",
    "AUDIT.json": "3e206ace6bd05b3c39c0ec153888282ed70537ce7378d58fe741ceac87eb54c0",
    "adapter/binary/FINITE.json": "b3c2dd4a7d8fd5cb34710afd93dbde00b402ec634e71d32c4e817899d4ca0597",
}


def component(base, prior, screen, proof, stages, check):
    p, h = 21,1804
    check((screen["candidate_p"],screen["limiting_control_p"],screen["h"],screen["shift"]) == (p,p-1,h,0)
          and (proof["fixed_envelope_minimum_power"],proof["rejected_power"],proof["h"]) == (p,p-1,h)
          and screen["sufficient_base_pass"] and screen["all_positive_p_through_20_excluded_for_this_envelope"],
          "candidate and limiting control")
    moments = list(map(Q,proof["moments"]))
    check(prior["p"] == 23 and prior["h"] == h and prior["uniform_J"] == 904 and len(moments) == p+1
          and moments[:2] == [1,Q(3,4)] and moments == list(map(Q,prior["moments"][:p+1])),
          "452-atom reconstruction matches the frozen power-23 moment prefix")
    eta_low, eta_high = map(Q,base["uniform"]["eta"])
    q = moments[1]/Q(23,20)
    check(0 < q < 1 and q == Q(proof["limiting_base"]) and
          q**20 == Q(screen["limit_at_20"]) == Q(proof["rejected_limit"]) > eta_high == Q(proof["eta_upper"])
          and q**21 == Q(screen["limit_at_21"]) < eta_low == Q(proof["eta_lower"]),
          "power-20 limit and all smaller positive integers")
    ratios = list(map(Q,screen["initial_coefficient_ratios"]))
    peak = max(ratios)
    check(len(ratios) == p+1 and ratios == list(map(Q,proof["coefficients"])) and
          min(ratios) >= 0 and peak == Q(proof["worst_upper"]) and
          ratios.index(peak) == proof["worst_index"] and peak < Q(screen["uniform_lambda"]) < eta_low,
          "22 signed outer coefficients and all-height strict contraction")
    H = base["uniform"]["H"]
    J = 825
    loss = Q(J,H)
    check((h**p << (J-1)) <= (H+h)**p < (h**p << J) and loss*(H+h)>2*p
          and J == proof["uniform_J"] and loss == Q(proof["uniform_loss"]), "full terminal and tail")
    stages(base,loss,CAP,check)
    cost = screen["price"]
    claim, old = Q(CLAIM),Q(prior["candidate_grid_claim"])
    ceiling = Q(base["raw_crossing"][1]) - Q(904,H) - Q(7,10**14)
    check(cost["passes"] and cost["J"] == J and Q(cost["cap"]) == Q(CAP) == Q(proof["cap"])
          and Q(cost["claim"]) == claim == Q(proof["candidate_grid_claim"])
          and Q(cost["tested"]) == Q(proof["candidate_tested"]) and claim > ceiling > old
          and Q(cost["old_relaxed_ceiling"]) == ceiling == Q(proof["old_cover_forgiven_upper"])
          and Q(cost["separation"]) == claim-ceiling == Q(proof["separation"]),
          "complete signed separation from power-23 envelope")
    check(claim-old == Q(proof["absolute_gain"]) == Q(7,10**14)
          and 100*(claim-old)/old == Q(proof["exact_relative_percent"]), "exact predecessor increase")
    return {"installed":CAP,"old_fixed_loss_ceiling":str(ceiling)}


def run(source, work, legacy, stages, base):
    check, digest = legacy["check"],legacy["digest"]
    check(digest(PRIOR) == "288e194853bb736973600eb51da2983414679a185629c30f769d701f4c55e811"
          and digest(SCREEN) == "2df053c036c3bf8c3f4f6deccdcdfa3d4821b3c801c6410fe0e377dba6149d23",
          "frozen power-23 predecessor and minimum-power screen")
    rebuilt = source/"replay/BIT-451.json"
    check(digest(rebuilt) == legacy["BASE_RECEIPT"] == digest(source/"BIT-451.json"),"signed BIT control")
    primary = work/"minimum-tensor-screen.json"
    subprocess.run([sys.executable,"-IB",SCREEN,"--bit-source",rebuilt,"--round337-receipt",PRIOR,
                    "--out",primary],check=True)
    proof = json.loads((HERE/"MINIMUM.json").read_bytes())
    bound = component(base,json.loads(PRIOR.read_bytes()),json.loads(primary.read_bytes()),proof,stages,check)
    outer = work/"minimum-tensor-consumer"
    full = legacy["consumer"](source,outer,bound,cap=CAP,expected_claim=CLAIM,expected_hashes=HASHES)
    audited = work/"minimum-tensor-audit.json"
    subprocess.run([sys.executable,"-IB",HERE/"minimum_audit.py",source,HERE.parent/"grid/RESULT.json",PRIOR,
                    audited,"--outer",outer],check=True)
    check(json.loads(audited.read_bytes()) == proof and Q(full["tested"]) == Q(proof["candidate_tested"])
          and Q(full["delta"]) == Q(192,10**14), "independent minimum and signed consumer")
    print("PASS_COMPLETE_TENSOR_MINIMUM",f"claim={full['claim']}",f"delta_vs_p23={proof['absolute_gain']}",
          f"delta_vs_7863={full['delta']}",flush=True)
    return full


if __name__ == "__main__":
    # The package driver runs the power-23 positive control first.
    runpy.run_path(str(HERE/"verify.py"),run_name="__main__")
