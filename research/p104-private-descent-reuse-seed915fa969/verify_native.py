#!/usr/bin/env python3
"""Run the exact native finite-word checker on the reused-helper variant."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path


ROOT = Path(os.environ.get("P104_REPLAY_ROOT", Path(__file__).resolve().parents[2])).resolve()


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location("p104_private_reuse_" + name, path)
    if spec is None or spec.loader is None:
        raise ValueError("cannot load " + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    fanout = load("fanout", ROOT / "research/p104-interleaved-search/fanout.py")
    native = load("native", ROOT / "research/p104-interleaved-search/native_checks.py")
    built = fanout.construct(reuse_helper=7)
    witness = fanout.native_witness(built)
    result = native.verify(witness)
    expected = {"1": 2611, "2": 513, "3": 378, "4": 132,
                "5": 81, "6": 15, "7": 13}
    if result["status"] != "PASS_FINITE_NATIVE_LOWERING":
        raise ValueError("native finite-word replay did not pass")
    if result["paid_profile"] != expected:
        raise ValueError("native transport invoice differs from the priced profile")
    if result["private_paths"] != 8 or result["private_path_gaussian_columns"] != 4096:
        raise ValueError("native private descent coverage is incomplete")
    if not result["wrong_global_phase_control_rejected"]:
        raise ValueError("native global-phase negative control did not reject")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
