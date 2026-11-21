# SPDX-License-Identifier: Apache-2.0
"""Reconstruct the three-cell bound with the known-good power-18 replay in hand."""
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
from shutil import copyfile
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CAP = "0.00387992804559244"
CLAIM = "0.00387992804551"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_bytes())


def coefficients(rows, limit):
    require(set(rows) == {str(i) for i in range(limit)}, "coverage of ordered coefficient indices")
    for row in rows.values():
        require(row["passes"] and F(row["ratio"]) < F(row["capacity"]), "directed comparison")
    return [F(rows[str(i)]["ratio"]) for i in range(limit)]


def compare(primary, proof):
    require(primary["case"] == {"p":17,"h":1804,"q":"749/1000","B":"4","x_cuts":["5/6","11/12"],"G_cut":32}
            and primary["decision"] == "ADVANCE_ONE_COMPLETE_REPLAY", "frozen three-cell primary passed")
    require(primary["coverage"] == {"direct_checked":64,"direct_unvisited":0,"coefficients_checked":54,
                                    "coefficients_unvisited":0}, "direct and coefficient budget exhausted")
    require(proof["decision"].startswith("PASS") and proof["p"] == 17 and proof["h"] == 1804
            and proof["negative_control_old_capacity_fails"] is True, "independent source capacity and control")
    require(coefficients(primary["newton"]["low"],18) == list(map(F,proof["small_x_coefficient_ratios"])),
            "low cell at all heights")
    for cell, left, right in (("middle","5/6","11/12"),("upper","11/12","1")):
        independent = proof["cells"][right]
        require(primary["cells"][cell]["l"] == independent["left"] == left
                and primary["cells"][cell]["u"] == right, "cell boundaries")
        initial = coefficients(primary["explicit"][cell],32)
        require(set(independent["rows"]) == {str(i) for i in range(32)}
                and initial == [F(independent["rows"][str(i)][0]) for i in range(32)], "32 explicit heights")
        require(coefficients(primary["newton"][cell],18) == list(map(F,independent["tail"])),
                "all 18 independent translated coefficients")
    price = primary["price"]
    require(price["passed"] and price["base"] and price["tail"] and price["carrier"]
            and price["J"] == proof["uniform_J"] == 668
            and [row[0] for row in price["stages"]] == proof["stages"] and len(proof["stages"]) == 7,
            "least terminal debit and seven paid stages")
    require(proof["cap"] == CAP and F(price["cap"]) == F(CAP) and F(CLAIM) == F(price["claim"])
            == F(proof["candidate_grid_claim"]) and F(price["tested"]) == F(proof["candidate_tested"])
            == F("0.00387992804558"), "directed cap, claim and actual test")
    ceiling = F(proof["old_relaxed_ceiling"])
    require(ceiling == F(price["old_ceiling"]) and F(CLAIM)-ceiling == F(proof["separation"])
            == F(price["separation"]) == F(277,20040000000000000)
            and F(proof["absolute_gain"]) == F(price["change"]) == F(4,10**14), "old relaxed complete ceiling")


def run(source, work, legacy, stages, base, known_good, signed_receipt):
    previous = HERE.parent.parent/"bit-451-carrier-cover"
    for key, path in {
        "round341/independent/audit.py": previous/"tensor/sibling_audit.py",
        "round343/screen.py": HERE.parent/"screen.py",
        "round343/primary.json": HERE/"POWER-18-PRIMARY.json",
    }.items():
        target = work/key
        target.parent.mkdir(parents=True,exist_ok=True)
        copyfile(path,target)
    # The sealed control includes timestamps. Match its scientific fields to the
    # power-18 replay just completed in this invocation.
    frozen = read(HERE/"POWER-18-PRIMARY.json")
    live = read(work/"primary.json")
    for field in ("decision","price","terminal","nonroot","root","small_x","large_x_prefix","large_x_tail"):
        require(live[field] == frozen[field], "replayed power-18 control "+field)
    require(sha256((HERE/"screen.py").read_bytes()).hexdigest() ==
            "a31815c475628f7ddca9d2f978e3d373bd01e9e1fe797f1d334f5fba208fd23c", "frozen primary")
    receipt = work/"three-cell-primary.json"
    subprocess.run([sys.executable,"-IB",HERE/"screen.py","--campaign-root",work,"--out",receipt],
                   timeout=65,check=True)
    audited = work/"three-cell-independent.json"
    subprocess.run([sys.executable,"-IB",HERE/"audit.py",work,audited],timeout=55,check=True)
    require(audited.read_bytes() == (HERE/"RESULT.json").read_bytes(), "independent exact certificate")
    proof = read(audited)
    compare(read(receipt),proof)
    signed = read(HERE/"SIGNED.json")
    require(sha256(audited.read_bytes()).hexdigest() == signed["new_component_sha256"]
            and signed["old_component_sha256"] == sha256((HERE.parent/"RESULT.json").read_bytes()).hexdigest(),
            "signed binding to both certificates")
    signed_receipt(work/"height-consumer",known_good,signed["known_good"],"0.00387992804547")
    stages(base,F(proof["uniform_loss"]),CAP,require)
    result = work/"three-cell-consumer"
    bound = {"installed":CAP,"old_fixed_loss_ceiling":proof["old_relaxed_ceiling"]}
    new = legacy["consumer"](source,result,bound,cap=CAP,expected_claim=CLAIM,
                             expected_hashes=signed["signed"]["output_sha256"])
    signed_receipt(result,new,signed["signed"],CLAIM)
    require(signed["known_good"]["orientations"] == signed["signed"]["orientations"]
            and F(new["delta"]) == F(205,10**14), "signed caller and peer comparison")
    print("PASS_COMPLETE_THREE_CELL_SOURCE", f"claim={new['claim']}", f"delta_vs_p18={proof['absolute_gain']}",
          f"delta_vs_7863={new['delta']}",flush=True)
    return new
