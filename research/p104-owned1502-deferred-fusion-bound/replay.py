"""Reconstruct and independently check the fixed chart-905 separator."""
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
    "lead/check_owned1502.py", "independent/check_owned1502_forward.py", LEAD, FORWARD,
}


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
    return result.stdout, result.stderr


def check_separator(lead):
    assert lead["status"] == "EXACT_FIXED_LATE_BANK_EXCLUSION"
    assert lead["tested"] == 1 and lead["unresolved"] == []
    assert lead["bank"] == [152, 1489] and lead["bank_rank"] == 2
    assert lead["probe"] == {"2": "-4"} and lead["historical_response"] == "1"
    assert lead["edited_bank_responses"] == {"152": "0", "1489": "0"}
    assert lead["old_bank_responses"] == {"152": "0", "1489": "4"}


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
    raw_lead, progress = reproduce("lead/check_owned1502.py")
    assert progress.splitlines() == [b"PASS_PINNED_CHRONOLOGY_AND_PRICE", b"BANK_ROWS_READY 2"]
    assert raw_lead == (ROOT / LEAD).read_bytes()
    lead = parse(raw_lead)
    check_separator(lead)
    forward, stderr = reproduce("independent/check_owned1502_forward.py", ROOT / "inputs",
                                ROOT / LEAD, pins[LEAD])
    assert not stderr
    actual = parse(forward)
    assert 0 <= actual.pop("seconds") < 30
    assert actual == parse((ROOT / FORWARD).read_bytes())
    assert actual["status"] == "PASS_INDEPENDENT_FIXED_LATE_BANK_SEPARATOR"
    assert actual["receiver_after_old"] == "-2" and actual["receiver_after_unrepaired"] == "0"
    rejects(lambda: parse('{"input":0,"input":1}'))
    rejects(lambda: check_hash(b"changed word", pins["inputs/7481-WORD.json.gz"]))
    rejects(lambda: check_separator(dict(lead, probe={"2": "0"})))
    print("PASS_OWNED1502_DEFERRED_FUSION_BOUND: one exact chart-905 separator")


if __name__ == "__main__":
    main()
