"""Run one cold source-bound suite and compare its complete typed receipt."""
import argparse
from hashlib import sha256
import importlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", required=True, choices=("kernels", "routes", "catalogue", "handoff",
                                                         "caller", "complete", "outer", "controls"))
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    checks = importlib.import_module("check_" + args.suite)
    result = checks.run()
    digest = sha256(json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    if not args.emit:
        expected = json.loads((HERE / "RESULT.json").read_text())[args.suite]
        if digest != expected:
            raise ValueError("complete typed receipt differs: " + args.suite + ": " + digest)
    print(json.dumps(dict(suite=args.suite, sha256=digest, result=result), sort_keys=True, indent=2))
    print("PASS_FAST_PRIMITIVES_" + args.suite.upper())


if __name__ == "__main__":
    main()
