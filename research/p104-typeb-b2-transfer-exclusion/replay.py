"""Reproduce the fixed four-clock signed Type B exclusion."""
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info

PACKAGE = Path(__file__).resolve().parent


def unique(pairs):
    result = {}
    for name, value in pairs:
        assert name not in result, f"Duplicate JSON key {name}"
        result[name] = value
    return result


def replay(script, *args):
    result = run(
        [executable, "-I", "-B", str(PACKAGE / script), *map(str, args)],
        cwd=PACKAGE, capture_output=True, timeout=31, check=True,
    )
    assert not result.stderr, result.stderr
    return result.stdout


def main():
    assert __debug__ and implementation.name == "cpython" and version_info[:2] == (3, 12)
    primary = PACKAGE / "receipts/PRIMARY.jsonl"
    forward = replay("lead/check_body2_relocation.py", PACKAGE / "inputs")
    assert forward == primary.read_bytes()
    backward = replay("independent/check_body2_pullback.py", PACKAGE, primary, sha256(forward).hexdigest())
    witness = loads(backward, object_pairs_hook=unique)
    assert 0 <= witness.pop("seconds") < 30
    assert witness == loads((PACKAGE / "receipts/INDEPENDENT.json").read_bytes(), object_pairs_hook=unique)
    assert witness["status"] == "PASS_INDEPENDENT_B2_RELOCATION_EXCLUSION"
    print("PASS_TYPEB_B2_TRANSFER_EXCLUSION")


if __name__ == "__main__":
    main()
