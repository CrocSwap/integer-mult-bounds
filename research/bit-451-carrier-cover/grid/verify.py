# SPDX-License-Identifier: Apache-2.0
"""Rebuild the fixed 451-factor supplier and replay its quantized paid-log bound."""
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
PRIOR = PACKAGE/"weighted/SECOND.json"
SCREEN = HERE/"screen.py"
CAP = "0.00387992804526559"
CLAIM = "0.00387992804518"
WEIGHTS = [0]*11 + [173,53821,8141,1832,1569]
HASHES = {
    "APPLICATION.json": "9300f140d1ad01f3e0177402b5f361619191229a22e353a2e36de5a597895db2",
    "AUDIT.json": "a0d962f26dc7a623a8636b1e8670690227e627588b2d34b952edcff164ff9326",
    "adapter/binary/FINITE.json": "21751e8364eb1e2cd0e67786bc25c7c01289bfc18cb272954d0821ad169bcf29",
}


def component(base, prior, search, result, coefficients, seven_stages, check):
    grid = search["grid"]
    check(search["status"] == "SCREEN_COMPLETE" and (search["low"],search["high"]) == (26,27)
          and [entry["power"] for entry in search["history"]] == [30,15,22,26,28,27],
          "exhaustive decision for the frozen integer grid")
    check(grid["weights"] == WEIGHTS == result["integer_masses"] and
          grid["mass_denominator"] == result["denominator"] == 65536 and
          grid["cut_denominator"] == 16 and grid["cdf_floor_units"] == result["cdf_numerators"],
          "complete dyadic masses match independent source derivation")
    p, h = result["p_minimum"],result["h"]
    check((p,h,result["shift"],result["failed_power"],result["failed_height"]) == (27,1804,0,26,-1),
          "fixed power and limiting obstruction")
    eta_low, eta_high = map(Q,base["uniform"]["eta"])
    mean = Q(sum(k*n for k,n in enumerate(WEIGHTS,1)),16*65536)
    limit = (mean/Q(23,20))**26
    check(limit == Q(result["failed_ratio"]) > eta_high and 0 < mean/Q(23,20) < 1 and
          Q(7,6)+1 < Q(319,100) and 1 < Q(23,20),
          "preceding and smaller powers fail the frozen dominating law")
    top, bottom = coefficients(p,WEIGHTS)
    check(all(n>=0 and d>0 for n,d in zip(top,bottom)),"nonnegative Bell coefficients")
    ratios = [n/d for n,d in zip(top,bottom)]
    check(len(top) == len(bottom) == p+1 and not result["prefix_ratios"] and
          ratios == list(map(Q,result["shifted_ratios"])) and
          max(ratios) == Q(result["worst_upper"]) < eta_low, "28 Bell and independent Newton ratios")
    H = base["uniform"]["H"]
    check(Q(h+(134**451).bit_length()-1,h)**p > Q(base["uniform"]["ambient_power"][1]),
          "ordinary base ranks")
    J = 1061
    check((h**p << (J-1)) <= (H+h)**p < (h**p << J) and
          result["uniform_J"] == J and Q(result["uniform_loss"]) == Q(J,H) and
          Q(J,H)*(H+h)>2*p, "least carrier debit and complete tail")
    seven_stages(base,Q(J,H),CAP,check)
    price = search["history"][-1]["price"]
    ceiling = Q(base["raw_crossing"][1]) - Q(1218,H) - Q(7,10**14)
    old, claim = Q(prior["candidate_grid_claim"]),Q(CLAIM)
    check(Q(prior["uniform_loss"]) == Q(1218,H) and claim > ceiling > old and
          Q(CAP) == Q(price["ordinary_cap"]) == Q(result["cap"]) and
          claim == Q(price["candidate_grid_claim"]) == Q(result["candidate_grid_claim"]) and
          ceiling == Q(price["old_relaxed_ceiling"]) == Q(result["old_cover_forgiven_upper"]) and
          claim-ceiling == Q(result["separation"]), "strict separation from prior complete envelope")
    check(claim-old == Q(result["absolute_gain"]) == Q(13,10**14) and
          100*(claim-old)/old == Q(result["exact_relative_percent"]), "exact previous gain")
    return {"installed":CAP,"old_fixed_loss_ceiling":str(ceiling)}


def main():
    if sys.version_info[:2] != (3,12) or not __debug__:
        raise RuntimeError("use CPython 3.12 with assertions")
    for name in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
        os.environ[name] = "1"
    legacy = runpy.run_path(str(PACKAGE/"verify.py"))
    check, digest = legacy["check"],legacy["digest"]
    check(digest(PRIOR) == "e6919418a22bd2679320b0178860b506357dd882415b2431b96ffa879976eed6",
          "exact predecessor at #8026 47f5718d")
    check(digest(SCREEN) == "5d6e9892ec68b7d150677c9b74e8e6b04a116d144accc3af589a3c224bee4b8c", "frozen primary screen")
    prior = json.loads(PRIOR.read_bytes())
    expected = json.loads((HERE/"RESULT.json").read_bytes())
    seven_stages = runpy.run_path(str(PACKAGE/"verify_majorant.py"))["seven_stage_bound"]
    coefficients = runpy.run_path(str(SCREEN))["coefficients"]
    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary)
        source = legacy["extract"](work)
        subprocess.run([sys.executable,"-IB",source/"replay_451.py"],cwd=source,check=True)
        rebuilt = source/"replay/BIT-451.json"
        check(digest(rebuilt) == legacy["BASE_RECEIPT"] == digest(source/"BIT-451.json"),"complete signed BIT control")
        base = json.loads(rebuilt.read_bytes())
        legacy["supplier"](base)
        screen = work/"primary.json"
        subprocess.run([sys.executable,"-IB",SCREEN,"--bit-source",rebuilt,"--out",screen],check=True)
        bound = component(base,prior,json.loads(screen.read_bytes()),expected,coefficients,seven_stages,check)
        outer = work/"consumer"
        full = legacy["consumer"](source,outer,bound,cap=CAP,expected_claim=CLAIM,expected_hashes=HASHES)
        report = work/"independent.json"
        subprocess.run([sys.executable,"-IB",HERE/"audit.py",source,PRIOR,report,
                        "--power","27","--shift","0","--failed-height","-1","--outer",outer],check=True)
        check(json.loads(report.read_bytes()) == expected and Q(full["tested"]) == Q(expected["candidate_tested"])
              and Q(full["delta"]) == Q(172,10**14), "independent all-height proof and complete signed application")
        print("PASS_COMPLETE_DYADIC_GRID",f"claim={full['claim']}",f"delta_vs_second={expected['absolute_gain']}",
              f"delta_vs_7863={full['delta']}",flush=True)


if __name__ == "__main__":
    main()
