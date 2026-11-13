"""Regenerate the chart-246 separator and verify both normalized trajectories."""
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
    "lead/check_1261_telescoping.py", "independent/check_1261_forward.py", LEAD, FORWARD,
}
CASE = "1261-telescoped-1191-chart246-pre39469"
BANK = [1145, 1192, 1261, 1443, 1485, 1486, 1487]


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
    assert actual["status"] == "PASS_INDEPENDENT_FIXED_DONOR_SEPARATOR"
    assert actual["case"] == lead["case"] == CASE
    assert actual["probe"] == lead["probe"] == {"894": "2"}
    assert actual["bank_responses"] == {str(role): "0" for role in BANK}
    assert actual["target_response"] == 1
    assert actual["old1191_after"] == "0" and actual["edited1191_before"] == "-1"
    assert actual["unrepaired1191_after"] == "-1"


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
    raw_lead = reproduce("lead/check_1261_telescoping.py", ROOT / "inputs")
    assert raw_lead == (ROOT / LEAD).read_bytes()
    lead = parse(raw_lead)
    assert lead["status"] == "EXACT_FIXED_DONOR_EXCLUSION"
    assert lead["tested"] == 1 and lead["unresolved"] == []
    assert lead["cut"] == 39469 and lead["bank"] == BANK and lead["bank_rank"] == 7
    assert lead["fixed_self_coefficient"] == 1
    forward = reproduce("independent/check_1261_forward.py", ROOT, ROOT / LEAD, pins[LEAD])
    actual = parse(forward)
    assert 0 <= actual.pop("seconds") < 30
    assert actual == parse((ROOT / FORWARD).read_bytes())
    check_separator(actual, lead)
    rejects(lambda: parse('{"input":0,"input":1}'))
    rejects(lambda: check_hash(b"changed word", pins["inputs/7481-WORD.json.gz"]))
    rejects(lambda: check_separator(dict(actual, edited1191_before="0"), lead))
    print("PASS_ROLE1261_TELESCOPE_BOUND: one exact chart-246 separator")


if __name__ == "__main__":
    main()
