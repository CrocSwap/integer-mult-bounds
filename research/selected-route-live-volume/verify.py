"""Authenticate retained inputs before executing the bounded route experiments."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((PACKAGE / "SNAPSHOTS.json").read_text())
    require(len(manifest["files"]) == 16, "exact snapshot inventory")
    for item in manifest["files"]:
        path = item["path"]
        require(path.startswith("vendor/") and Path(path).name == path[7:], "snapshot path")
        data = (PACKAGE / path).read_bytes()
        require(hashlib.sha256(data).hexdigest() == item["sha256"], "source SHA256: " + path)
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(hashlib.sha1(blob).hexdigest() == item["git_blob"], "source Git blob: " + path)


def same_typed(actual, expected):
    """JSON comparison that cannot confuse True with the integer 1."""
    pending = [(actual, expected)]
    for _ in range(20000):
        if not pending:
            return True
        left, right = pending.pop()
        if type(left) is not type(right):
            return False
        if isinstance(left, dict):
            if left.keys() != right.keys():
                return False
            pending.extend((left[key], right[key]) for key in left)
        elif isinstance(left, list):
            if len(left) != len(right):
                return False
            pending.extend(zip(left, right))
        elif left != right:
            return False
    raise ValueError("receipt comparison capacity")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path, help="write a new external receipt without overwriting")
    parser.add_argument("--check-sources", action="store_true")
    args = parser.parse_args()
    authenticate()
    if args.write_result is not None:
        require(not args.write_result.resolve().is_relative_to(PACKAGE), "write receipts outside the package")
        require(not args.write_result.exists(), "receipt output already exists")
    if args.check_sources:
        print("PASS_ROUTE_SNAPSHOT_BINDINGS")
        return
    sys.path.insert(0, str(PACKAGE / "vendor"))
    sys.path.insert(0, str(PACKAGE))
    from replay import experiments
    result = experiments()
    if args.write_result is not None:
        with args.write_result.open("x") as output:
            output.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        require(same_typed(result, expected), "exact typed route receipt")
    print("PASS_SELECTED_ROUTE_LIVE_VOLUME cases=" + str(len(result["cases"]))
          + " controls=" + str(result["controls"]) + " no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        sys.exit("FAIL_SELECTED_ROUTE_LIVE_VOLUME: " + str(error))
