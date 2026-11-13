"""Reconstruct the fixed chart-1051 ingress separator and bank collision."""
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
    "next-helper1310/check_ingress.py", "independent/check_helper1310_forward.py", LEAD, FORWARD,
}
BANK = {666, 667, 668, 669, 670, 1310, 1311, 1312, 1313, 1314, 1315, 1316}


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


def check_collision(actual):
    assert actual["status"] == "PASS_INDEPENDENT_FIXED_INGRESS_SEPARATOR"
    assert actual["chart_bank_responses"] == {str(r): "1" if r == 1310 else "0" for r in BANK}
    assert actual["zero_complete_bank_probe"] == {"890": "1", "1310": "-1"}
    assert actual["zero_complete_bank_responses"] == {str(r): "0" for r in BANK}
    assert actual["fresh_helper_input_for_control"] == 0
    assert actual["required_recovered_old_input"] == "-1"
    assert actual["first_outward_response"] == "1" and actual["first_outward_zero_bank_response"] == 0


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
    raw_lead = reproduce("next-helper1310/check_ingress.py")
    assert raw_lead == (ROOT / LEAD).read_bytes()
    lead = parse(raw_lead)
    assert lead["status"] == "EXACT_FIXED_INGRESS_EXCLUSION"
    assert lead["tested"] == 1 and lead["unresolved"] == []
    assert lead["bank"] == sorted(BANK - {1310}) and lead["bank_rank"] == 11
    assert lead["probe"] == {"890": "1"} and lead["historical_donor_responses"] == ["1", "0"]
    forward = reproduce("independent/check_helper1310_forward.py", ROOT, ROOT / LEAD, pins[LEAD])
    actual = parse(forward)
    assert 0 <= actual.pop("seconds") < 30
    assert actual == parse((ROOT / FORWARD).read_bytes())
    check_collision(actual)
    rejects(lambda: parse('{"input":0,"input":1}'))
    rejects(lambda: check_hash(b"changed word", pins["inputs/7481-WORD.json.gz"]))
    rejects(lambda: check_collision(dict(actual, required_recovered_old_input="0")))
    print("PASS_HELPER1310_FIXED_INGRESS_BOUND: one chart-1051 separator and whole-bank collision")


if __name__ == "__main__":
    main()
