"""Check the binary construction and the published finite receipt."""

import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))

from bit_application import verify


def main():
    computed = verify(PACKAGE.parents[1])
    expected = json.loads((PACKAGE / "BIT-RESULT.json").read_bytes())
    if json.loads(json.dumps(computed)) != expected:
        raise ValueError("binary evidence differs from the published receipt")
    print("PASS_CHANGED_ORDINARY_BIT 0.00385896149")


if __name__ == "__main__":
    main()
