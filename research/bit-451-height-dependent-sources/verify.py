# SPDX-License-Identifier: Apache-2.0
"""Verify one height-dependent BIT proof and its preceding signed application."""
from fractions import Fraction as F
from hashlib import sha256
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PREVIOUS = HERE.parent / "bit-451-carrier-cover"
CAP = "0.00387992804555917"
CLAIM = "0.00387992804547"


def require(predicate, message):
    if not predicate:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_bytes())


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def check_sources():
    seen = set()
    for row in read(HERE / "SOURCES.json")["files"]:
        if row["usage"] != "input":
            continue
        key = row["path"]
        require(key not in seen, "duplicate dependency path")
        require(digest(REPO / key) == row["sha256"], key)
        seen.add(key)
    require(seen == set(read(HERE / "VERIFY.json")["inputs"]), "complete external input inventory")


def component(source, work):
    old, grid, mean = (PREVIOUS / path for path in ("tensor/SIBLING.json","grid/RESULT.json","tensor/MEAN.json"))
    files = {
        "round321/benchmark/producer/BIT-451.json": source / "replay/BIT-451.json",
        "round336/independent/receipt.json": grid,
        "round339/independent/receipt.json": mean,
        "round341/independent/receipt-with-minimum.json": old,
        "round342/screen.py": HERE / "original_screen.py",
        "round342/primary.json": HERE / "CAPPED.json",
        "round342/independent/outer-verified.json": HERE / "SIGNED.json",
    }
    for name, path in files.items():
        target = work / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    # Reconstruct the independent certificate before the screen's matched comparison.
    audited = work / "round342/independent/receipt.json"
    subprocess.run([sys.executable, "-IB", HERE / "audit.py", "--bit", source / "BIT-451.json",
                    "--grid", grid, "--mean", mean, "--old", old, "--closure", PREVIOUS / "tensor/sibling_audit.py",
                    "--out", audited], check=True, timeout=60)
    require(audited.read_bytes() == (HERE / "RESULT.json").read_bytes(), "exact independent certificate")
    require(digest(HERE / "screen.py") == "bcb2134b4570246029b35d1eb585f04fdf2318b686910dac1c45fb3ee674554d",
            "frozen primary endpoint reconstruction")
    primary = work / "primary.json"
    subprocess.run([sys.executable, "-IB", HERE / "run_screen.py", "--campaign-root", work, "--out", primary],
                   check=True, timeout=65)
    screen, proof = read(primary), read(audited)
    require(screen["decision"] == "PRIMARY_AND_INDEPENDENT_SIGNED_REPLAY_MATCH", "primary/independent arithmetic")
    require(proof["decision"] == "PASS component; independent signed application required"
            and proof["positive_control_no_x_slack_fails"] is True, "upper region requires its size slack")
    require(len(proof["left_ratios"]) == len(proof["tail_ratios"]) == 19
            and [row["g"] for row in proof["finite"]] == list(range(32)), "all initial, finite and tail bounds")
    require(F(proof["ug_multiplier_upper"]) < 1 and F(proof["uniform_loss"]) == F(708,1202400000000000)
            and proof["uniform_J"] == 708 and len(proof["stages"]) == 7
            and proof["cap"] == CAP and F(proof["candidate_grid_claim"]) == F(CLAIM)
            and F(proof["candidate_tested"]) == F("0.00387992804554"), "full terminal guard and signed price")
    ceiling = F(proof["old_relaxed_ceiling"])
    require(F(CLAIM)-ceiling == F(proof["separation"]) == F(209,33400000000000000)
            and F(CLAIM)-F(read(old)["candidate_grid_claim"]) == F(proof["absolute_gain"]) == F(3,10**14),
            "comparison with power-19 predecessor")
    return proof


def signed_receipt(directory, observed, expected, claim):
    actual = read(directory / "receipt.json")
    require(len(expected["output_sha256"]) == 5, "five signed scientific outputs")
    for name, value in expected["output_sha256"].items():
        require(digest(directory / name) == actual["output_sha256"][name] == value, "signed output " + name)
    app, audit = read(directory/"APPLICATION.json"), read(directory/"AUDIT.json")
    outer = audit["outer"]
    require(app["premises"] == audit["premises"] == expected["premises"], "inherited signed premises")
    require(F(actual["cap"]) == F(app["binary_ordinary"]) == F(outer["pinned_binary_cap"]) == F(expected["cap"])
            and F(observed["claim"]) == F(actual["claim"]) == F(claim) == F(outer["claim"]) == F(expected["claim"])
            and F(observed["tested"]) == F(actual["tested"]) == F(expected["tested"]), "signed price")
    require(outer["outer_checks"] == expected["checks"] and expected["checks"]["strict_count"] == 54
            and expected["checks"]["functional_count"] == 4, "all signed checks")
    require(set(actual["controls"]) == set(expected["controls"]) == {"extra_rank_1_charge_rejected","low_cap_rejected"},
            "corrupted paid and low-cap controls")


def main():
    require(sys.version_info[:2] == (3,12) and sys.implementation.name == "cpython" and __debug__,
            "CPython 3.12 with assertions required")
    for name in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
        os.environ[name] = "1"
    check_sources()
    legacy = runpy.run_path(str(PREVIOUS/"verify.py"))
    stages = runpy.run_path(str(PREVIOUS/"verify_majorant.py"))["seven_stage_bound"]
    signed = read(HERE / "SIGNED.json")
    with TemporaryDirectory() as directory:
        work = Path(directory)
        source = legacy["extract"](work)
        subprocess.run([sys.executable,"-IB",source/"replay_451.py"], cwd=source, check=True)
        rebuilt = source/"replay/BIT-451.json"
        require(digest(rebuilt) == digest(source/"BIT-451.json") == legacy["BASE_RECEIPT"], "original binary words")
        base = read(rebuilt)
        legacy["supplier"](base)
        old = runpy.run_path(str(PREVIOUS/"tensor/sibling.py"))["run"](source,work,legacy,stages,base)
        signed_receipt(work/"sibling-tensor-consumer", old, signed["known_good"], "0.00387992804544")

        proof = component(source,work)
        stages(base,F(proof["uniform_loss"]),CAP,require)
        bound = {"installed":CAP, "old_fixed_loss_ceiling":proof["old_relaxed_ceiling"]}
        result = work/"height-consumer"
        new = legacy["consumer"](source,result,bound,cap=CAP,expected_claim=CLAIM,
                                 expected_hashes=signed["signed"]["output_sha256"])
        signed_receipt(result,new,signed["signed"],CLAIM)
        require(signed["known_good"]["orientations"] == signed["signed"]["orientations"]
                and F(new["delta"]) == F(201,10**14), "old and new signed scope and peer comparison")
        print("PASS_COMPLETE_HEIGHT_DEPENDENT_SOURCE", f"claim={new['claim']}",
              f"delta_vs_p19={proof['absolute_gain']}",f"delta_vs_7863={new['delta']}",flush=True)
        runpy.run_path(str(HERE/"three-cells/verify.py"))["run"](source,work,legacy,stages,base,new,signed_receipt)


if __name__ == "__main__":
    main()
