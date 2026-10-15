#!/usr/bin/env python3
"""Read-only, source-bound replay; --emit prints the deterministic receipt."""
import argparse
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(test, message):
    if not test:
        raise ValueError(message)


def authenticate(data, record):
    need(sha256(data).hexdigest() == record["sha256"], "source SHA256: " + record["path"])
    blob = sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    need(blob == record["git_blob"], "source Git blob: " + record["path"])


def sources(root=ROOT, package=HERE):
    manifest = json.loads((package / "SOURCES.json").read_text())
    count = 0
    for record in manifest["files"]:
        if record["usage"] == "input":
            authenticate((root / record["path"]).read_bytes(), record)
            count += 1
    for record in manifest["vendored"]:
        authenticate((package / record["path"]).read_bytes(), record)
        count += 1
    return count


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def compare_receipt(actual, expected):
    need(canonical(actual) == canonical(expected), "complete typed receipt equality")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--repository", type=Path, default=ROOT,
                        help="repository supplying the pinned immutable inputs")
    args = parser.parse_args()
    count = sources(args.repository)
    sys.path.insert(0, str(HERE))
    import binding
    import checks
    result = checks.run(binding.provider.Catalogue(args.repository))
    result["authenticated_sources"] = count
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected = json.loads((HERE / "RESULT.json").read_text())
        compare_receipt(result, expected)
        print(result["status"], "fixtures=" + str(result["fixture_cases"]),
              "coordinate_equalities=" + str(result["coordinate_equalities"]),
              "independent_equalities=" + str(result["independent_equalities"]),
              "controls=" + str(len(result["controls"])))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        raise SystemExit("FAIL_SELECTED_CONTROL_TABLE_BINDING: " + str(error))
