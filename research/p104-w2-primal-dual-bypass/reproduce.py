"""Reproduce the explicitly adapted Step-1 (W2 primal-dual bypass) application using authenticated #7605 sources."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent

BASE_7605_SPEC = {
    "base_pr": 7605,
    "base_head": "e1d2756eecf03e146338239fee81772a99ba8d4c",
    "base_application_sha256": "b46e39f81116aaa2feb3283d0e53bf95608313240b16e96f174b43fa7b4ab69e",
    "candidate_compressed_sha256": "bfe2a4fb54dd82940ba78d8b3efd4f587e3fc9e978ccfd48561199d2c9fb4887",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def apply_records(path: Path, records: list[dict]) -> None:
    text = path.read_text(encoding="utf-8")
    for rec in records:
        count = rec.get("occurrences", rec.get("count"))
        assert text.count(rec["before"]) == count, (path.name, rec["before"], text.count(rec["before"]), count)
        text = text.replace(rec["before"], rec["after"])
    path.write_text(text, encoding="utf-8")


def main() -> None:
    if not __debug__:
        raise RuntimeError("Optimized Python (-O/-OO) is prohibited: verification assertions are required")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, required=True, help="Immutable #7605 research/p104-timed-helper757 directory")
    ap.add_argument("--work", type=Path, required=True, help="New empty output working directory")
    ap.add_argument("--stage", choices=["prepare", "native", "signed", "all"], default="all")
    ap.add_argument("--skip-pins", action="store_true", help="Skip package PINS.json self-hash check during draft assembly")
    args = ap.parse_args()
    if args.skip_pins:
        raise RuntimeError("--skip-pins is prohibited in the published package")

    pins_path = HERE / "PINS.json"
    if not pins_path.is_file():
        raise RuntimeError("PINS.json is required")
    if pins_path.is_file():
        for rel, h in read_json(pins_path).items():
            assert hashlib.sha256((HERE / rel).read_bytes()).hexdigest() == h, rel

    source = args.source.resolve()
    work = args.work.resolve()
    assert hashlib.sha256((source / "application.py").read_bytes()).hexdigest() == BASE_7605_SPEC["base_application_sha256"]

    spec = importlib.util.spec_from_file_location("base_application", source / "application.py")
    base_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base_mod)
    base_mod.authenticate()

    if args.stage in ("prepare", "all"):
        assert not work.exists(), "Use a new empty output directory; do not overwrite prior evidence"
        base_mod.prepare(work, base_mod.authenticate())
        word_bytes = (HERE / "data/word.json.gz").read_bytes()
        assert hashlib.sha256(word_bytes).hexdigest() == BASE_7605_SPEC["candidate_compressed_sha256"]
        for rel in ("producer54/reroute/WORD.json.gz", "frozen-composition/CANDIDATE-WORD.json.gz"):
            (work / rel).write_bytes(word_bytes)
        (work / "frozen-composition/W2-EDITS.json").write_bytes((HERE / "data/edits7605.json").read_bytes())
        (work / "frozen-composition/W3H-STEP1-ON-7616-EDITS.json").write_bytes((HERE / "data/edits-on-7616.json").read_bytes())
        (work / "frozen-composition/CANDIDATE-INVOICE.json").write_bytes((HERE / "evidence/invoice-step1.json").read_bytes())
        apply_records(work / "producer54/validation_native/run.py", read_json(HERE / "adapters/native.json"))
        apply_records(work / "producer54/validation_signed/run.py", read_json(HERE / "adapters/signed.json"))
        adapt_src = (work / "inputs/pr7480/adapt.py").read_text(encoding="utf-8")
        assert adapt_src.count("(74, 50, 68)") == 1
        (work / "producer54/validation_signed/w2_adapt.py").write_text(
            adapt_src.replace("(74, 50, 68)", "(204, 50, 68)"),
            encoding="utf-8",
        )
    if args.stage == "prepare":
        return

    tmp = work.parent / "w3h_tmp"
    tmp.mkdir(exist_ok=True)
    env = dict(os.environ, TEMP=str(tmp), TMP=str(tmp))
    for stage in (["native", "signed"] if args.stage == "all" else [args.stage]):
        if stage == "signed":
            assert read_json(work / "producer54/validation_native/NATIVE-RESULT.json")["status"] == "PASS_W3H_ADAPTED_COMPLETE_NATIVE"
        subprocess.run(
            [sys.executable, "-I", "-B", str(HERE / "windows_path_shim.py"), str(work / f"producer54/validation_{stage}/run.py")],
            env=env,
            check=True,
            timeout=1500,
        )
    print("PASS Step-1 (W2 primal-dual bypass) candidate-adapted application; inherited + CLEAR-content premises apply")


if __name__ == "__main__":
    main()
