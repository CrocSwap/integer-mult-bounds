"""Replay independent ordinary-interface obligations with complete receipts."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", required=True, choices=("setup", "engine", "binary", "root", "controls"))
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    if args.suite == "setup":
        import check_setup as checks
    elif args.suite == "engine":
        import check_engine as checks
    elif args.suite == "binary":
        import check_binary as checks
    elif args.suite == "root":
        import check_root as checks
    else:
        import check_controls as checks
    result = checks.run()
    digest = sha256(json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    if not args.emit:
        expected = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))[args.suite]
        if digest != expected:
            raise ValueError("complete typed receipt differs: " + args.suite + ": " + digest)
    print(json.dumps(dict(suite=args.suite, sha256=digest, result=result), sort_keys=True, indent=2))
    print("PASS_PHYSICAL_ORDINARY_" + args.suite.upper())


if __name__ == "__main__":
    main()
