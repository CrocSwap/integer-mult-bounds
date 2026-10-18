"""Run a cold selected-prefix check and compare its complete typed receipt."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))


def authenticate():
    sources = json.loads((HERE/"SOURCES.json").read_text())
    manifest = json.loads((HERE/"VERIFY.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            if row["path"] not in manifest["inputs"] or sha256((ROOT/row["path"]).read_bytes()).hexdigest() != row["sha256"]:
                raise ValueError("changed or undeclared selected-prefix input: "+row["path"])
    import prefix_sources
    inherited = prefix_sources.activate()
    predecessor = json.loads((inherited/"SOURCES.json").read_text())
    for row in predecessor["files"]:
        if row["usage"] == "input" and row["path"] not in manifest["inputs"]:
            raise ValueError("undeclared transitive scalar input")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", required=True, choices=("bindings", "hoist", "packets", "returns", "extent"))
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    authenticate()
    import prefix_checks
    result = getattr(prefix_checks, args.suite)()
    digest = sha256(json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    if not args.emit:
        expected = json.loads((HERE/"RESULT.json").read_text())[args.suite]
        if digest != expected:
            raise ValueError("complete prefix receipt differs: "+args.suite+": "+digest)
    print(json.dumps(dict(suite=args.suite, sha256=digest, result=result), sort_keys=True, indent=2))
    print("PASS_SELECTED_FIRST_PREFIX_"+args.suite.upper())


if __name__ == "__main__":
    main()
