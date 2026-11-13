#!/usr/bin/env python3
"""Isolated CLI and callable API for the read-only exact verifier."""
import importlib.util
import json
from pathlib import Path
import sys


_ENGINE_PATH = Path(__file__).with_name("engine.py")
_SPEC = importlib.util.spec_from_file_location("p104_joint_funding_engine", _ENGINE_PATH)
_ENGINE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _ENGINE
_SPEC.loader.exec_module(_ENGINE)


def rebuild(word_path):
    return _ENGINE.rebuild(word_path)


def structure(replay_doc):
    return _ENGINE.structure(replay_doc)


def local_bounds(replay_doc, structure_doc):
    return _ENGINE.local_bounds(replay_doc, structure_doc)


def negative_controls(replay_doc, structure_doc):
    return _ENGINE.negative_controls(replay_doc, structure_doc)


def verify(word_path):
    replay_doc = rebuild(word_path)
    structure_doc = structure(replay_doc)
    controls = negative_controls(replay_doc, structure_doc)
    local_doc = local_bounds(replay_doc, structure_doc)
    source_receipt = dict(replay_doc["receipt"])
    source_receipt["executed_mutation_controls"] = controls["controls"]
    return {"source": source_receipt,
            "structure": structure_doc["receipt"],
            "controls": controls,
            "local": {
                "status": local_doc["status"],
                "largest": local_doc["largest_component"],
                "six_zero": local_doc["six_zero_analytic_checks"],
                "small_component_counts": [
                    {"cache_sites": c["cache_sites"], "subsets": c["subset_count"],
                     "cases": c["case_count"]} for c in local_doc["eight_small_components"]],
                "small_subset_count": sum(c["subset_count"] for c in local_doc["eight_small_components"]),
                "small_case_count": sum(c["case_count"] for c in local_doc["eight_small_components"]),
                "six_zero_profile_counts": [
                    {"cache_sites": c["cache_sites"], "subsets": c["subset_count"],
                     "cases": c["case_count"]} for c in local_doc["six_zero_prefix_profiles"]],
                "zero_only_quarter": local_doc["zero_only_quarter_certificate"],
            }}


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        raise SystemExit("usage: run.py /absolute/path/to/WORD.json.gz")
    result = verify(args[0])
    print(json.dumps(_ENGINE.to_jsonable(result), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
