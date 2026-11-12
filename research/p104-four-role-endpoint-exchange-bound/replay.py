"""Reproduce the priced four-role P104 prefix exclusion and both workflow arms."""
from hashlib import sha256
from json import dump, loads
from pathlib import Path
from subprocess import PIPE, run
from sys import executable, implementation, version_info
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
STAGES = (
    ("lead/price.py", (), "lead/PRICE.json"),
    ("lead/geometry.py", (), "lead/GEOMETRY.json"),
    ("lead/basis.py", ("prefix",), "lead/PREFIX.json"),
    ("continue_prefix.py", (), "receipts/CONTINUATION.json"),
    ("trial/shared.py", (), "receipts/SHARED.json"),
    ("trial/verify.py", ("archived", "lead/PREFIX.json"), "receipts/ARCHIVED-CHECK.json"),
    ("trial/verify.py", ("per-case", "receipts/CONTINUATION.json"), "receipts/PER-CASE-CHECK.json"),
    ("trial/verify.py", ("shared", "receipts/SHARED.json"), "receipts/SHARED-CHECK.json"),
)


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def decode(raw):
    return loads(raw, object_pairs_hook=unique)


def execute(script, args):
    return run([executable, "-I", "-B", str(ROOT / script), *args],
               cwd=ROOT, stdout=PIPE, stderr=PIPE, timeout=35)


def compare(receipts):
    archived, current, shared = (receipts[f"receipts/{arm}-CHECK.json"]
                                 for arm in ("ARCHIVED", "PER-CASE", "SHARED"))
    for result, count, cuts in ((archived, 8, 16016), (current, 7, 478), (shared, 7, 478)):
        assert not result["cap_reached"]
        assert len(result["rows"]) == count and result["raw_cuts_checked"] == cuts
        for row in result["rows"]:
            assert row["decision"] == "excluded" and row["zero_raw_cuts"] == row["raw_cuts"]
    archive_keys, current_keys, shared_keys = (
        [row["key"] for row in result["rows"]] for result in (archived, current, shared)
    )
    assert current_keys == shared_keys
    assert not set(map(tuple, archive_keys)).intersection(map(tuple, current_keys))
    assert archive_keys + current_keys == (
        receipts["lead/PREFIX.json"]["selected"] + receipts["lead/PREFIX.json"]["unvisited"]
    )
    assert len(receipts["lead/GEOMETRY.json"]["unresolved"]) == 15


def negative_controls(receipt):
    try:
        decode('{"inputs/word": 1, "inputs/word": 2}')
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate dependency key was accepted")

    with TemporaryDirectory(prefix="p104-four-role-negative-") as folder:
        wrong = Path(folder) / "WRONG.json"
        # This direction still separates the target, but leaks into a donor bank.
        proof = receipt["results"][0]["proof"]
        proof["separating_covector"] = {"1251": "1", "1481": "4"}
        proof["separated_target"] = "-4"
        with wrong.open("w") as f:
            dump(receipt, f)
        result = execute("trial/verify.py", ("per-case", str(wrong)))
        assert result.returncode == 1 and b"assert zeros == len(obs)" in result.stderr


def main():
    assert __debug__ and implementation.name == "cpython" and version_info[:2] == (3, 12)
    pins = decode((ROOT / "LOCAL-PINS.json").read_bytes())
    for path, expected in sorted(pins.items()):
        file = (ROOT / path).resolve()
        assert file.is_relative_to(ROOT) and file.is_file(), path
        assert sha256(file.read_bytes()).hexdigest() == expected, ("changed dependency", path)
    expected_files = {path for script, _, receipt in STAGES for path in (script, receipt)}
    assert expected_files <= pins.keys()
    receipts = {}
    for script, args, receipt in STAGES:
        result = execute(script, args)
        assert result.returncode == 0, (script, result.returncode, result.stderr.decode())
        assert result.stdout == (ROOT / receipt).read_bytes(), ("changed receipt", receipt)
        receipts[receipt] = decode(result.stdout)
    compare(receipts)
    negative_controls(receipts["receipts/CONTINUATION.json"])
    print('{"archived_representatives":8,"fresh_representatives":7,"raw_cuts_checked":16494,'
          '"ineligible_raw_cuts":3961,"unresolved_representatives":0,"kappa_delta":"0",'
          '"matched_workflow_trial":"inconclusive","negative_controls":2}')
    print("PASS_P104_FOUR_ROLE_ENDPOINT_EXCHANGE_BOUND")


if __name__ == "__main__":
    main()
