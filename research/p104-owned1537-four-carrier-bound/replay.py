"""Reproduce the four-carrier separator and independently check its response."""
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
LEAD = "receipts/LEAD.json"
FORWARD = "receipts/FORWARD.json"
PINNED = {
    "PROVENANCE.json", "inputs/7113-CALLER.json", "inputs/7481-APPLICATION.json",
    "inputs/7481-WORD.json.gz", "inputs/gate.py", "inputs/pricing.py",
    "next-owned1537/check_four_returns.py", "independent/check_owned1537_forward.py", LEAD, FORWARD,
}
CASE = "owned1537-four-returns-pre49170"
DONORS = [813, 1162, 1448, 1397]


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
    assert not result.stderr
    return result.stdout


def check_separator(actual, lead):
    assert actual["status"] == "PASS_INDEPENDENT_NAMED_FOUR_RETURNS_SEPARATOR"
    assert actual["case"] == lead["case"] == CASE
    assert actual["probe"] == lead["probe"] == {"1": "16", "4": "-16"}
    assert actual["target"] == 1
    assert actual["donor_responses"] == {str(role): "0" for role in DONORS}
    assert actual["old_before_scale"] == "0" and actual["edited_before_scale"] == "-1"
    assert actual["old_after_scale"] == "0" and actual["edited_after_scale"] == "-4"
    assert actual["old_first_outward_after"] == "-8" and actual["edited_first_outward_after"] == "-10"


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
    raw_lead = reproduce("next-owned1537/check_four_returns.py")
    assert raw_lead == (ROOT / LEAD).read_bytes()
    lead = parse(raw_lead)
    assert lead["status"] == "EXACT_NAMED_FOUR_RETURNS_EXCLUSION"
    assert lead["tested"] == 1 and lead["unresolved"] == []
    assert lead["cut"] == 49170 and lead["donors"] == DONORS and lead["rank"] == 4
    forward = reproduce("independent/check_owned1537_forward.py", ROOT, ROOT / LEAD, pins[LEAD])
    actual = parse(forward)
    assert 0 <= actual.pop("seconds") < 30
    assert actual == parse((ROOT / FORWARD).read_bytes())
    check_separator(actual, lead)
    rejects(lambda: parse('{"input":0,"input":1}'))
    rejects(lambda: check_hash(b"changed word", pins["inputs/7481-WORD.json.gz"]))
    rejects(lambda: check_separator(dict(actual, target=0), lead))
    print("PASS_OWNED1537_FOUR_CARRIER_BOUND: one exact four-carrier separator")


if __name__ == "__main__":
    main()
