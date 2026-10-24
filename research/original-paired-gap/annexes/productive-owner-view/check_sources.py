#!/usr/bin/env python3
"""Audit the retained proof sources. This is not a mathematical replay."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    output = parser.parse_args().out
    require(not output.exists(), "Use a new output directory")
    manifest = json.loads((ROOT / "SOURCES.json").read_bytes())
    for entry in manifest["files"]:
        require(digest(ROOT / entry["path"]) == entry["sha256"], "Source changed: " + entry["path"])
    lanes = ROOT / "frozen/lanes"
    review = json.loads((lanes / "coherent-port/PRODUCTIVE-OWNER-VIEW-REVIEW.json").read_bytes())
    for relative, pin in review["sources"].items():
        require(digest(lanes / relative) == pin, "Written review source pin: " + relative)
    require(review["status"] == "PASS_NARROW_PHYSICAL_VIEW_PROOF_REVIEW", "Wrong review scope")
    output.mkdir(parents=True)
    result = {"status": "PASS_PRODUCTIVE_OWNER_VIEW_SOURCE_AUDIT",
              "source_count": len(manifest["files"]), "written_review_pins_checked": len(review["sources"]),
              "source_manifest_sha256": digest(ROOT / "SOURCES.json"),
              "checker_sha256": digest(Path(__file__)),
              "mathematical_replay_performed": False,
              "scope": "Fresh source-integrity audit for the written change-of-coordinates proof. No native phase, owner-history, matching, global defect, or restoration replay."}
    (output / "CHECKS.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
