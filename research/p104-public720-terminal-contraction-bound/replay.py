"""Regenerate the chart-265 separator and independently verify the terminal action."""
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
    "next-terminal720/check_lower_bank.py", "independent/check_terminal720_forward.py", LEAD, FORWARD,
}
CASE = "terminal720-chart265-pre41307"
BANK = [236, 454, 720, 1000, 1208, 1347]


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
    assert actual["status"] == "PASS_INDEPENDENT_FIXED_LOWER_BANK_SEPARATOR"
    assert actual["case"] == lead["case"] == CASE
    assert actual["probe"] == lead["probe"] == {"0": "2", "7": "-1", "720": "-1/4"}
    assert actual["lower_bank_responses"] == {str(role): "0" for role in BANK}
    assert actual["earlier_92_at_paid_departure"] == "0"
    assert actual["captured_92_at_ADD33129"] == actual["old1511_at_final_read_and_clear"] == "1"
    assert actual["old720_final"] == "-1/4" and actual["unrepaired720_final"] == "0"


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
    raw_lead, progress = reproduce("next-terminal720/check_lower_bank.py")
    assert progress == [b"PINNED_CHRONOLOGY_PRICE_AND_BANK"]
    assert raw_lead == (ROOT / LEAD).read_bytes()
    lead = parse(raw_lead)
    assert lead["status"] == "EXACT_FIXED_LOWER_BANK_EXCLUSION"
    assert lead["tested"] == 1 and lead["unresolved"] == []
    assert lead["cut"] == 41307 and lead["bank_roles"] == BANK
    forward, stderr = reproduce("independent/check_terminal720_forward.py", ROOT, ROOT / LEAD, pins[LEAD])
    assert not stderr
    actual = parse(forward)
    assert 0 <= actual.pop("seconds") < 30
    assert actual == parse((ROOT / FORWARD).read_bytes())
    check_separator(actual, lead)
    rejects(lambda: parse('{"input":0,"input":1}'))
    rejects(lambda: check_hash(b"changed word", pins["inputs/7481-WORD.json.gz"]))
    rejects(lambda: check_separator(dict(actual, captured_92_at_ADD33129="0"), lead))
    print("PASS_PUBLIC720_TERMINAL_CONTRACTION_BOUND: one exact chart-265 separator")


if __name__ == "__main__":
    main()
