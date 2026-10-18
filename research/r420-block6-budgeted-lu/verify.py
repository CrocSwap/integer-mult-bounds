#!/usr/bin/env python3
"""Replay the bounded block-6 search and inherited exact local checks."""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
sys.path.insert(0, str(PACKAGE))

from search import canonical, generate, sha256  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def additions(word: dict) -> int:
    phase_adds = sum(len(record[2]) for phase in ("D", "A", "B", "C") for record in word[phase])
    scatter_adds = sum(len(row) for row in word["scatter"])
    return phase_adds + scatter_adds


def check_sources() -> None:
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    require(manifest["base_commit"] == BASE, "wrong pinned base")
    for rel, pin in manifest["sources"].items():
        data = (ROOT / rel).read_bytes()
        require(sha256(data) == pin["sha256"], f"source bytes differ: {rel}")
        blob = subprocess.check_output(["git", "rev-parse", f"{BASE}:{rel}"], cwd=ROOT, text=True).strip()
        require(blob == pin["git_blob"], f"base blob differs: {rel}")


def run() -> dict:
    require(not sys.flags.optimize, "assertions must remain enabled")
    check_sources()
    subprocess.run(
        [sys.executable, "-I", "-B", str(ROOT / "scripts/verify_selected_result.py")],
        cwd=ROOT, check=True,
    )
    word, certificate = generate()
    stored_word = json.load(gzip.open(PACKAGE / "candidate-word.json.gz", "rt", encoding="utf-8"))
    stored_certificate = json.loads((PACKAGE / "search-certificate.json").read_text())
    require(certificate == stored_certificate, "deterministic search certificate differs")
    require(canonical(word) == canonical(stored_word), "candidate word differs in a proof-relevant field")
    require(sha256(canonical(word)) == certificate["candidate"]["canonical_word_sha256"],
            "candidate canonical hash differs")

    require((len(word["D"]), len(word["A"]), len(word["B"]), len(word["C"])) == (120, 2064, 830, 2654),
            "unexpected regenerated phase gate counts")
    require(additions(word) == 26902, "unexpected complete scalar ADD count")
    require(certificate["object"]["baseline_B_interval"] == [417, 471], "wrong block-6 interval")
    require(certificate["object"]["candidate_operations"] == 47, "wrong candidate gate count")
    require(certificate["object"]["positive_integer_ADDs_saved_including_cleanup"] == 14,
            "wrong literal-cleanup saving")

    with tempfile.TemporaryDirectory(prefix="r420-block6-check-") as scratch:
        scratch_path = Path(scratch)
        candidate_path = scratch_path / "candidate-word.json.gz"
        candidate_path.write_bytes((PACKAGE / "candidate-word.json.gz").read_bytes())
        xreport = scratch_path / "xcheck.json"
        mreport = scratch_path / "mutants.json"
        xcheck = ROOT / "research/e8-bit-r420/code/xcheck.py"
        mutants = ROOT / "research/e8-bit-r420/code/mutants.py"
        subprocess.run(
            [sys.executable, "-I", "-B", str(xcheck), str(candidate_path), "--json", str(xreport)],
            cwd=ROOT, check=True,
        )
        subprocess.run(
            [sys.executable, "-I", "-B", str(mutants), str(xcheck), str(candidate_path), "--json", str(mreport)],
            cwd=ROOT, check=True,
        )
        xresult = json.loads(xreport.read_text())
        mresult = json.loads(mreport.read_text())
        require(all(xresult["hypotheses"].values()) and all(xresult["conclusion"].values()),
                "an inherited H1-H5 hypothesis or interface conclusion failed")
        require(mresult.get("status", "").startswith("PASS"), "inherited mutation controls failed")
        controls = mresult.get("controls", [])
        negatives = [row for row in controls if row["control"] != "positive"]
        positives = [row for row in controls if row["control"] == "positive"]
        require(len(negatives) == 9 and all(row["rejected"] for row in negatives)
                and len(positives) == 1 and not positives[0]["rejected"],
                "unexpected inherited mutation-control coverage")

    return {
        "status": "PASS_R420_BLOCK6_BUDGETED_LU",
        "base_commit": BASE,
        "candidate_word_sha256": certificate["candidate"]["canonical_word_sha256"],
        "block6_operations": [54, 47],
        "scalar_additions": [26916, 26902],
        "exact_interface": "PASS on all 660 source, target, and dirty-helper columns",
        "mutation_controls": "PASS; 9 negative rejected and 1 positive accepted",
        "kappa_claim": None,
    }


if __name__ == "__main__":
    result = run()
    print("PASS_R420_BLOCK6_BUDGETED_LU baseline=54 candidate=47 local_ADDs=26916->26902")
    print("CANDIDATE_SHA256", result["candidate_word_sha256"])
