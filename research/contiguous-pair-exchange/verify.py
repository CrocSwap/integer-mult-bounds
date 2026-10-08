"""Verify contiguous-pair coordinate pricing, two-round carry exchange, and min-cost circuit reclamation.
Prepared by Thomas Marchand with Google Antigravity assistance. Apache-2.0.
"""
import sys
if sys.flags.optimize:
    raise ValueError("Assertions must remain enabled")
sys.dont_write_bytecode = True

import gzip
import importlib.util
import json
import os
import shlex
import subprocess
import tempfile
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

spec98 = importlib.util.spec_from_file_location("parent98", ROOT / "research/final-coordinate-pricing/verify.py")
parent98 = importlib.util.module_from_spec(spec98)
spec98.loader.exec_module(parent98)
parent = parent98.parent

sys.path.insert(0, str(HERE))
import engine
from aligned_composition_nodeops import relabel
from binary_frame_profile_prepare import prepare
from binary_frame_replay import replay


def required():
    return (
        parent98.required()
        | {"research/final-coordinate-pricing/SOURCE.json", ".github/workflows/contiguous-pair-exchange.yml"}
        | {
            str(p.relative_to(ROOT))
            for p in HERE.iterdir()
            if p.is_file() and p.name not in ("SOURCE.json", "validation.json")
        }
    )


def sources():
    parent98.sources()
    d = json.loads((HERE / "SOURCE.json").read_text())
    assert required() <= set(d["files"])
    for name, digest in d["files"].items():
        assert sha256((ROOT / name).read_bytes()).hexdigest() == digest, name


def exact(profiles, certificate=None, stage="B"):
    cert_path = HERE / ("certificate.json" if stage == "B" else "stage-a-certificate.json")
    c = certificate or json.loads(cert_path.read_text())
    bit = parent.combine(profiles)
    js = parent.arithmetic.js
    assert js(bit) == c["bit"]
    saving = Q(c["bit_saving"])
    grid = Q(1, 10**18)
    rows = bit["child_multiplicities"]
    moment = parent.refine.exact_moment(bit["m"], bit["W"], rows, saving)
    rejected = parent.refine.exact_moment(bit["m"], bit["W"], rows, saving + grid)
    assert moment["upper"] < 1 < rejected["lower"]
    assert js(moment) == c["exact_moment"] and str(rejected["lower"]) == c["next_grid_lower"]
    independent = parent.audit.independent_moment(js(bit), saving, js(moment["terms"]))
    negative = parent.audit.independent_moment(js(bit), saving + grid, js(rejected["terms"]))
    assert independent[1] < 1 < negative[0]
    bridge = parent.finite_bridge(bit["W"])
    assert js(bridge) == c["finite_bridge"]
    assembly = parent.refine.assemble(bridge, saving, Q(1, 10**12), 10**18)
    assert js(assembly) == c["assembly"] and str(assembly["kappa"]) == c["kappa"]
    assert len(assembly["assembly"]["constraints"]) == 47
    assert all(x > 0 for x in assembly["assembly"]["constraints"].values())
    assert len(assembly["assembly"]["margins"]) == 7
    assert all(x > assembly["kappa"] for x in assembly["assembly"]["margins"].values())

    prior = json.loads((parent98.HERE / "certificate.json").read_text())
    old = prior["bit"]
    lower = parent.refine.exact_moment(
        old["m"], old["W"], {int(t): n for t, n in old["child_multiplicities"].items()}, saving
    )["lower"]
    assert lower > 1 and str(lower) == c["prior_complete_profile_exclusion_lower"]
    assert assembly["kappa"] > Q(prior["kappa"]) == Q(c["prior_kappa"])

    if stage == "B":
        sa = json.loads((HERE / "stage-a-certificate.json").read_text())
        sa_bit = sa["bit"]
        sa_lower = parent.refine.exact_moment(
            sa_bit["m"], sa_bit["W"], {int(t): n for t, n in sa_bit["child_multiplicities"].items()}, saving
        )["lower"]
        assert sa_lower > 1 and str(sa_lower) == c["stage_a_complete_profile_exclusion_lower"]
        assert assembly["kappa"] > Q(sa["kappa"]) == Q(c["stage_a_kappa"])

    print(
        f"PASS Stage {stage} exact arithmetic: kappa={assembly['kappa']}, 47 constraints, 7 margins, "
        f"next-grid rejection, and prior complete profile exclusion",
        flush=True,
    )


def verify(regenerate=False, regenerate_chain=False):
    sources()
    if regenerate_chain:
        parent98.verify(True)
    with tempfile.TemporaryDirectory(prefix="contiguous-pair-exchange-") as directory:
        work = Path(directory)
        if regenerate:
            oracle_exe = engine.compile_oracle_exe(work)
            for h in (23, 25):
                rec_a = engine.compile_stage_a_axis(h, work, oracle_exe=oracle_exe)
                print("PASS Stage A fresh producer", json.dumps(rec_a), flush=True)
            for h in (23, 25):
                rec_b = engine.compile_stage_b_axis(h, work, oracle_exe=oracle_exe)
                print("PASS Stage B fresh producer", json.dumps(rec_b), flush=True)

        exe = work / "profiles"
        subprocess.run(
            [
                *shlex.split(os.environ.get("CXX", "c++")),
                "-O3",
                "-std=c++17",
                "-I",
                str(ROOT / "references/frame-compiler/pr48/scripts/partial_swap"),
                str(ROOT / "scripts/experiments/binary_frame_profiles.cpp"),
                "-o",
                str(exe),
            ],
            check=True,
        )

        sa_profiles = []
        for h in (23, 25):
            path = HERE / f"stage-a-word-{h}.json.gz"
            replayed = replay(path)
            assert parent.arithmetic.js(replayed) == json.loads((HERE / f"stage-a-replay-{h}.json").read_text())
            trans = work / f"stage-a-transitions-{h}.bin"
            prepare(path, trans)
            subprocess.run([str(exe), str(trans)], check=True)
            profile = json.loads(Path(str(trans) + ".profiles.json").read_text())
            assert profile == json.loads((HERE / f"stage-a-profiles-{h}.json").read_text())
            sa_profiles.append(profile)
            print("PASS Stage A full physical replay and CRT profile", h, flush=True)
        exact(sa_profiles, stage="A")

        sb_profiles = []
        for h in (23, 25):
            path = HERE / f"word-{h}.json.gz"
            replayed = replay(path)
            assert parent.arithmetic.js(replayed) == json.loads((HERE / f"replay-{h}.json").read_text())
            trans = work / f"transitions-{h}.bin"
            prepare(path, trans)
            subprocess.run([str(exe), str(trans)], check=True)
            profile = json.loads(Path(str(trans) + ".profiles.json").read_text())
            assert profile == json.loads((HERE / f"profiles-{h}.json").read_text())
            sb_profiles.append(profile)
            print("PASS Stage B full physical replay and CRT profile", h, flush=True)
        exact(sb_profiles, stage="B")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--regenerate", action="store_true")
    p.add_argument("--regenerate-chain", action="store_true")
    a = p.parse_args()
    verify(a.regenerate, a.regenerate_chain)
