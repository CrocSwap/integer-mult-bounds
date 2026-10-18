"""Run one bounded cold check and compare its complete typed receipt."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", required=True, choices=("binding", "intervals", "algebra", "original", "consumers", "costs"))
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    import sources
    loaded = sources.load()
    inputs = set(sources.PINS) | set(loaded["inherited_inputs"])
    declared = set(json.loads((HERE/"VERIFY.json").read_text())["inputs"])
    if inputs != declared:
        raise ValueError("complete declared dense-collector source inventory")
    import check
    result = getattr(check, args.suite)()
    digest = sha256(json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    if not args.emit and digest != json.loads((HERE/"RESULT.json").read_text())[args.suite]:
        raise ValueError("complete dense-collector receipt differs: "+args.suite+": "+digest)
    print(json.dumps(dict(suite=args.suite, sha256=digest, result=result), sort_keys=True, indent=2))
    print("PASS_DENSE_PAIRED_COLLECTOR_"+args.suite.upper())


if __name__ == "__main__":
    main()
