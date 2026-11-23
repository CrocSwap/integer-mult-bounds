#!/usr/bin/env python3
"""Run the unchanged owner reviewer with package-relative inputs and explicit output."""
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse

HERE = Path(__file__).resolve().parent
PIN = "9f585184774697db158efa313fe963f7cc2111d5fcf0dacf46d4f2ebedeac0ca"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    path = HERE / "review_check.py"
    if sha256(path.read_bytes()).hexdigest() != PIN:
        raise ArithmeticError("The frozen independent owner reviewer changed")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    spec = spec_from_file_location("frozen_owner_review", path)
    review = module_from_spec(spec)
    spec.loader.exec_module(review)
    # Only locations change. All proof checks, pins, controls and source loaders
    # remain exactly those in the hash-checked original reviewer.
    review.AUTHOR = HERE.parent
    review.RUNTIME = args.runtime.resolve()
    review.HERE = output
    review.main()


if __name__ == "__main__":
    main()
