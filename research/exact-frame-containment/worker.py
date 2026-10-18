"""Run the complete pinned historical benchmark, with one opt-in substitution."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
INPUTS = {
    "scripts/certify.py", "scripts/exclusion_circuit.py",
    "scripts/paired_exclusion_circuit.py", "scripts/experiments/mixed_point_circuit.py",
    "scripts/rational_span_frames.py", "tests/benchmark_rational_span_frames.py",
}


def check_sources(root=ROOT):
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    inputs = [source for source in manifest["files"] if source["usage"] == "input"]
    if len(inputs) != len(INPUTS) or {source["path"] for source in inputs} != INPUTS:
        raise ValueError("source inventory mismatch")
    for source in inputs:
        data = (root / source["path"]).read_bytes()
        if hashlib.sha256(data).hexdigest() != source["sha256"]:
            raise ValueError("source pin mismatch: " + source["path"])


def main():
    if sys.flags.optimize:
        raise SystemExit("Run without -O: inherited circuit assertions must remain enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("engine", choices=("reference", "equations", "crosscheck"))
    parser.add_argument("output", type=Path)
    parser.add_argument("--cpu", type=int)
    args = parser.parse_args()
    check_sources()
    sys.path.insert(0, str(ROOT / "scripts"))
    import rational_span_frames as frames
    decisions = {"calls": 0, "true": 0, "false": 0}
    if args.engine != "reference":
        from kernel import ExactContainment
        candidate = ExactContainment()
        if args.engine == "crosscheck":
            reference = frames.contained

            def crosscheck(source, target):
                old, new = reference(source, target), candidate(source, target)
                if old is not new:
                    raise ValueError("containment decision differs")
                decisions["calls"] += 1
                decisions["true" if new else "false"] += 1
                return new

            frames.contained = crosscheck
        else:
            frames.contained = candidate
    sys.argv = ["benchmark_rational_span_frames.py", str(ROOT), str(args.output)]
    if args.cpu is not None:
        sys.argv.extend(["--cpu", str(args.cpu)])
    runpy.run_path(str(ROOT / "tests/benchmark_rational_span_frames.py"), run_name="__main__")
    if args.engine == "crosscheck":
        with args.output.with_suffix(".decisions.json").open("x") as stream:
            stream.write(json.dumps(decisions, indent=2) + "\n")


if __name__ == "__main__":
    main()
