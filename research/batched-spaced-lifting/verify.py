"""Read-only exact checks and typed receipt comparison."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=("plans", "algebra", "payloads", "exponents", "errors"), required=True)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    manifest = json.loads((HERE/"VERIFY.json").read_text())
    sources = json.loads((HERE/"SOURCES.json").read_text())
    inputs = [row for row in sources["files"] if row["usage"] == "input"]
    if {row["path"] for row in inputs} != set(manifest["inputs"]):
        raise ValueError("complete batched source input inventory")
    for row in inputs:
        if sha256((ROOT/row["path"]).read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError("changed batched source premise: "+row["path"])
    import check
    result = getattr(check, args.suite)()
    digest = sha256(json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    if not args.emit:
        expected = json.loads((HERE/"RESULT.json").read_text())[args.suite]
        if digest != expected:
            raise ValueError("complete typed batched-lifting receipt differs: "+args.suite+": "+digest)
    print(json.dumps(dict(suite=args.suite, sha256=digest, result=result), sort_keys=True, indent=2))
    print("PASS_BATCHED_SPACED_LIFTING_"+args.suite.upper())


if __name__ == "__main__":
    main()
