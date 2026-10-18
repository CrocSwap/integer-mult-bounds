"""Bounded source and finite-fixture replay; does not run Lean. Apache-2.0."""
import argparse, importlib.util, json, tempfile, sys
sys.dont_write_bytecode = True
from pathlib import Path

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("toolkit_checks", P / "checks.py")
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    pins = checks.inventory(P)
    control_spec = importlib.util.spec_from_file_location("toolkit_controller_controls", P / "controller_controls.py")
    control = importlib.util.module_from_spec(control_spec)
    sys.modules[control_spec.name] = control
    control_spec.loader.exec_module(control)
    construction = control.run_tests()
    result = {"status": "PASS_SOURCE_AND_FINITE_CONTROLS", "kernel_check": "not_run",
              "source_files": len(pins), "construction": construction, "finite": checks.finite_replay(),
              "audit_corruptions_rejected": checks.audit_controls(),
              "manifest_sha256": checks.digest(P / "MANIFEST.json")}
    if args.out:
        out = args.out.resolve()
        checks.need(out != P and P not in out.parents, "output must be outside package")
        checks.need(not out.exists(), "fresh output directory required")
        out.mkdir(parents=True)
        (out / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
