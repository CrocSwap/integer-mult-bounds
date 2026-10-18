#!/usr/bin/env python3
"""Compare every literal receipt with the separately derived integer model."""
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("independent_lifetimes", ROOT / "independent.py")
model = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = model
exec(compile((ROOT / "independent.py").read_bytes(), str(ROOT / "independent.py"), "exec"), model.__dict__)


def main():
    data = json.loads((ROOT / "RESULT.json").read_text())
    for case in data["fixtures"]:
        events = [(e[0], e[2], e[5]) for e in case["events"]]
        root = case["width"]
        for kind, rank, half in reversed(events):
            root = 64*(root//rank) if kind == 0 else root*(128 if half else 64)
        caller = 8 if case["kind"] == "prefix" else 0
        indices = model.validation_indices(root, events, borrowed=case["borrowed"], caller=caller)
        residues = model.validation_residues(case["q"], case["exponent"], case["unit"],
                                             borrowed=case["borrowed"])
        model.require(case["peak"]["validation"] == [residues, indices],
                      "literal and independent-model peaks differ")
        if caller:
            model.require(case["peak"]["directory"] == [4096, 0], "literal directory maximum")
            model.require(case["peak"]["setup"] == [0, 9], "literal initialization maximum")
    print("PASS_CROSS_MODEL_PEAKS fixtures="+str(len(data["fixtures"])))


if __name__ == "__main__":
    main()
