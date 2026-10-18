#!/usr/bin/env python3
"""Read-only replay by default; --write explicitly regenerates RESULT.json."""
import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from audit import build_receipt, canonical, need


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true")
    group.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    receipt = build_receipt()
    if args.emit:
        print(json.dumps(receipt, indent=2))
        return
    if args.write:
        (HERE / "RESULT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    else:
        saved = json.loads((HERE / "RESULT.json").read_text())
        need(canonical(saved) == canonical(receipt), "exact typed receipt equality")
    print("PASS_SELECTED_CONTROL_REQUEST_MASS"
          f" source_programs={receipt['source_census']['programs']}"
          f" coordinates={receipt['source_census']['coordinates']}"
          f" abstract_cases={receipt['abstract_census']['cases']}"
          f" controls={len(receipt['controls']['rejections'])}"
          " preparation_exponent=592 no_new_kappa")


if __name__ == "__main__":
    main()
