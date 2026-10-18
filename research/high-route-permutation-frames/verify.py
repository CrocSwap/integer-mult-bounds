"""Bounded replay, exact typed receipts, and no artifact writes."""
import argparse
from hashlib import sha256
import importlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def check_equal(actual, expected, name):
    if canonical(actual) != canonical(expected):
        raise ValueError("complete typed receipt differs: " + name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", required=True, choices=("algebra","catalogue","physical","controls"))
    parser.add_argument("--emit", action="store_true", help="print the full result without comparing saved receipts")
    args = parser.parse_args()
    import bindings
    bindings.authenticate()
    result = importlib.import_module("check_"+args.suite).run()
    digest = sha256(canonical(result).encode()).hexdigest()
    if not args.emit:
        expected = json.loads((HERE/"RESULT.json").read_text())
        check_equal(digest, expected[args.suite], args.suite)
        if args.suite == "catalogue":
            rows = [json.loads(line) for line in (HERE/"CATALOGUE.jsonl").read_text().splitlines()]
            check_equal(result["entries"], rows, "per-chart complete invoice")
            summary = {k:v for k,v in result.items() if k != "entries"}
            summary["weighted_delta_operations"] = sum(
                row["occurrences"]*sum(row["delta_high_operations"]) for row in rows)
            summary["all_bound_deltas_nonpositive"] = all(
                value <= 0 for row in rows for value in row["setup_and_adapter_delta_per_V"])
            check_equal(summary,json.loads((HERE/"SUMMARY.json").read_text()),"catalogue summary")
    if args.emit:
        print(canonical(result))
    else:
        summary = {k:v for k,v in result.items() if k != "entries"} if isinstance(result,dict) else result
        print(canonical(dict(suite=args.suite, sha256=digest, result=summary)))
    print("PASS_HIGH_ROUTE_FRAMES_"+args.suite.upper())


if __name__ == "__main__":
    main()
