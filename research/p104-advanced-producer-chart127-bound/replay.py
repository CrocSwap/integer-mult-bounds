"""Regenerate the fixed chart-127 separator and independently check its action."""
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
LEAD = "receipts/LEAD.json"
FORWARD = "receipts/FORWARD.json"
INITIAL_CAP = "receipts/INITIAL-CAP.json"
PINNED = {
    "PROVENANCE.json", "inputs/7113-CALLER.json", "inputs/7481-APPLICATION.json",
    "inputs/7481-WORD.json.gz", "inputs/gate.py", "inputs/pricing.py",
    "continuation/check_integer.py", "continuation/integer_basis.py",
    "independent/check_public1351_forward.py", LEAD, FORWARD, INITIAL_CAP,
}
CASE = "public1351-advanced1369-pre48155"


def unique(items):
    result = dict(items)
    assert len(result) == len(items), "duplicate JSON key"
    return result


def parse(data):
    return loads(data, object_pairs_hook=unique)


def check_hash(data, digest):
    assert sha256(data).hexdigest() == digest, "changed pinned bytes"


def reproduce(script, *arguments):
    result = run([executable, "-I", "-B", str(ROOT / script), *map(str, arguments)],
                 capture_output=True, timeout=32, check=True)
    return result.stdout, result.stderr.splitlines()


def check_separator(actual, lead):
    assert actual["status"] == "PASS_INDEPENDENT_FIXED_ADVANCED_BANK_SEPARATOR"
    assert actual["case"] == lead["case"] == CASE
    assert actual["probe"] == lead["probe"] and len(actual["probe"]) == 90
    assert set(actual["edited_bank"]) == {str(r) for r in [1351, *lead["donors"]]}
    assert len(actual["edited_bank"]) == 669 and set(actual["edited_bank"].values()) == {"0"}
    assert actual["historical_h"] == "-1"
    assert actual["old1351"] == actual["old408_after"] == "1"
    assert actual["edited408_after"] == "0"


def rejects(check):
    try:
        check()
    except AssertionError:
        return
    raise AssertionError("rejection control unexpectedly passed")


def main():
    assert __debug__ and implementation.name == "cpython" and version_info[:2] == (3, 12)
    pins = parse((ROOT / "PINS.json").read_bytes())
    assert set(pins) == PINNED
    for path, digest in pins.items():
        check_hash((ROOT / path).read_bytes(), digest)
    cap = parse((ROOT / INITIAL_CAP).read_bytes())
    assert cap == {"status": "CAP", "tested": 0, "unresolved": [CASE], "cap_seconds": 30}
    raw_lead, stderr = reproduce("continuation/check_integer.py")
    assert stderr == [b"PINNED_CHRONOLOGY_AND_PRICE", b"EDITED_BANK_READY 669"]
    assert raw_lead == (ROOT / LEAD).read_bytes()
    lead = parse(raw_lead)
    assert lead["status"] == "EXACT_FIXED_ADVANCED_BANK_EXCLUSION"
    assert lead["tested"] == 1 and lead["unresolved"] == []
    assert lead["integer_pivots"] == 669 and len(lead["donors"]) == 668
    assert 1369 in lead["donors"] and 1351 not in lead["donors"]
    assert lead["donor_support"] is False
    assert lead["integer_engine_sha256"] == pins["continuation/integer_basis.py"]
    forward, stderr = reproduce("independent/check_public1351_forward.py", ROOT, ROOT / LEAD, pins[LEAD])
    assert not stderr
    actual = parse(forward)
    assert 0 <= actual.pop("seconds") < 30
    assert actual == parse((ROOT / FORWARD).read_bytes())
    check_separator(actual, lead)
    rejects(lambda: parse('{"input":0,"input":1}'))
    rejects(lambda: check_hash(b"changed word", pins["inputs/7481-WORD.json.gz"]))
    rejects(lambda: check_separator(dict(actual, old408_after="0"), lead))
    print("PASS_ADVANCED_PRODUCER_CHART127_BOUND: one exact 669-row separator")


if __name__ == "__main__":
    main()
