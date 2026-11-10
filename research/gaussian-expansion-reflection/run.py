"""Run the complete retained Gaussian caller with one setup substitution."""
import argparse
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from adapter import complete_replay


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("baseline", "reflected"), required=True)
    args = parser.parse_args()
    output, counts = complete_replay(args.mode)
    print(output, end="")
    print(json.dumps({"mode": args.mode, "counts": counts}, sort_keys=True), file=sys.stderr)


if __name__ == "__main__":
    main()
