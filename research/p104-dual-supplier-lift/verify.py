"""Check both suppliers and their shared conditional application."""

import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from bit_application import verify as verify_bit


def compare(actual, path):
    expected = json.loads(path.read_bytes())
    if json.loads(json.dumps(actual)) != expected:
        raise ValueError("finite evidence differs from " + path.name)


def main():
    binary = verify_bit(PACKAGE.parents[1])
    compare(binary, PACKAGE / "BIT-RESULT.json")
    cap = binary["compiler"]["ordinary_admitted"]
    sys.path.insert(0, str(PACKAGE / "complex"))
    from supplier import verify
    complete = verify(cap)
    compare(complete, PACKAGE / "complex/RESULT.json")
    print("PASS_DUAL_SUPPLIER_APPLICATION", complete["application"]["claim"], cap)


if __name__ == "__main__":
    main()
