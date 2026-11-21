# SPDX-License-Identifier: Apache-2.0
"""Verify one paid-tensor moment certificate and its complete signed consumer."""
from fractions import Fraction as Q
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
PRIOR = PACKAGE/"grid/RESULT.json"
SCREEN = HERE/"screen.py"
CAP = "0.00387992804539617"
CLAIM = "0.00387992804531"
HASHES = {
    "APPLICATION.json": "4b1b348ef8fcb0fb3ea4d9c0224925b1448516c9f8aceb2181ca82713c3159c9",
    "AUDIT.json": "6a2addc5684f3370f640bfcd84316f90d399fed1909b050e123b21204090a8c6",
    "adapter/binary/FINITE.json": "3608f5f0eabbddb5e3a76b9be2e54d21500838872e845ec935471a6f9624cce4",
}


def component(base, prior, screen, proof, stages, check):
    p, h = 23,1804
    check((screen["p"],screen["h"],screen["max_coefficients"]) == (p,h,p+1)
          and (proof["p"],proof["h"],proof["atoms"]) == (p,h,452)
          and screen["base_guard"] and screen["decision"].startswith("all-height component and projected price pass"),
          "one finished power-23 screen and independent atom expansion")
    eps = Q(proof["epsilon_upper"])
    check(eps == Q(prior["epsilon_upper"]) == Q(1,10**15), "full paid-completion allowance")
    moments = list(map(Q,screen["moments"]))
    check(len(moments) == p+1 and moments[1] == Q(3,4) and
          moments == list(map(Q,proof["moments"])), "24 Stirling moments match the direct 452-atom expansion")
    ratios = [Q(screen["ratios"][str(i)]) for i in range(p+1)]
    audit_ratios = list(map(Q,proof["coefficients"]))
    eta = Q(base["uniform"]["eta"][0])
    check(len(ratios) == len(screen["ratios"]) == len(audit_ratios) and eta == Q(proof["eta_lower"])
          and ratios == audit_ratios and all(0 <= ratio < eta for ratio in ratios),
          "all 24 Bell and direct Newton coefficients")
    check(audit_ratios.index(max(audit_ratios)) == proof["worst_index"] == 23
          and max(audit_ratios) == Q(proof["worst_upper"]), "worst coefficient")
    H = base["uniform"]["H"]
    J = 904
    loss = Q(J,H)
    check((h**p << (J-1)) <= (h+H)**p < (h**p << J) and loss*(h+H) > 2*p
          and proof["uniform_J"] == J and Q(proof["uniform_loss"]) == loss, "minimum loss and all widths")
    stages(base,loss,CAP,check)
    ceiling = Q(base["raw_crossing"][1]) - Q(1061,H) - Q(7,10**14)
    cost = screen["prospective_price"]
    claim, previous = Q(CLAIM),Q(prior["candidate_grid_claim"])
    check(Q(prior["uniform_loss"]) == Q(1061,H) and claim > ceiling > previous
          and J == cost["loss"] and Q(CAP) == Q(cost["cap"]) == Q(proof["cap"])
          and claim == Q(cost["claim"]) == Q(proof["candidate_grid_claim"])
          and ceiling == Q(cost["old_relaxed_ceiling"]) == Q(proof["old_cover_forgiven_upper"])
          and claim-ceiling == Q(cost["separation"]) == Q(proof["separation"]),
          "full comparison with prior grid price ceiling")
    check(claim-previous == Q(proof["absolute_gain"]) == Q(13,10**14)
          and 100*(claim-previous)/previous == Q(proof["exact_relative_percent"]), "increment over grid")
    return {"installed": CAP,"old_fixed_loss_ceiling": str(ceiling)}


def run(source, work, legacy, stages, base):
    check, digest = legacy["check"],legacy["digest"]
    check(digest(PRIOR) == "69c8f917d6b2676897639eef67e8f15aae1c23a6bfb608dcd38aed236f299818",
          "complete grid result at #8026 18718411")
    check(digest(SCREEN) == "140849072beff7d547e8b4642dcb918b8d39c4a47e68151ccde065a80160fa66",
          "sealed paid-tensor screen")
    rebuilt = source/"replay/BIT-451.json"
    check(digest(rebuilt) == legacy["BASE_RECEIPT"] == digest(source/"BIT-451.json"), "signed BIT control")
    primary = work/"tensor-primary.json"
    subprocess.run([sys.executable,"-IB",SCREEN,"--bit-source",rebuilt,
                    "--round336-receipt",PRIOR,"--out",primary],check=True)
    proof = json.loads((HERE/"RESULT.json").read_bytes())
    bound = component(base,json.loads(PRIOR.read_bytes()),json.loads(primary.read_bytes()),proof,stages,check)
    outer = work/"tensor-consumer"
    full = legacy["consumer"](source,outer,bound,cap=CAP,expected_claim=CLAIM,expected_hashes=HASHES)
    audited = work/"tensor-audit.json"
    subprocess.run([sys.executable,"-IB",HERE/"audit.py",source,PRIOR,audited,"--power","23","--outer",outer],
                   check=True)
    check(json.loads(audited.read_bytes()) == proof and Q(full["tested"]) == Q(proof["candidate_tested"])
          and Q(full["delta"]) == Q(185,10**14), "independent atom audit and complete signed application")
    print("PASS_COMPLETE_TENSOR_MOMENTS",f"claim={full['claim']}",f"delta_vs_grid={proof['absolute_gain']}",
          f"delta_vs_7863={full['delta']}",flush=True)
    return full


def main():
    if sys.version_info[:2] != (3,12) or not __debug__:
        raise RuntimeError("use CPython 3.12 with assertions")
    for name in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
        os.environ[name] = "1"
    legacy = runpy.run_path(str(PACKAGE/"verify.py"))
    stages = runpy.run_path(str(PACKAGE/"verify_majorant.py"))["seven_stage_bound"]
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        source = legacy["extract"](work)
        subprocess.run([sys.executable,"-IB",source/"replay_451.py"],cwd=source,check=True)
        rebuilt = source/"replay/BIT-451.json"
        legacy["check"](legacy["digest"](rebuilt) == legacy["BASE_RECEIPT"], "original signed supplier reconstruction")
        base = json.loads(rebuilt.read_bytes())
        legacy["supplier"](base)
        run(source,work,legacy,stages,base)
        runpy.run_path(str(HERE/"minimum.py"))["run"](source,work,legacy,stages,base)
        runpy.run_path(str(HERE/"mean.py"))["run"](source,work,legacy,stages,base)
        runpy.run_path(str(HERE/"sibling.py"))["run"](source,work,legacy,stages,base)


if __name__ == "__main__":
    main()
