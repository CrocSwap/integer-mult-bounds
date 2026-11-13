"""Rebuild the four-donor separator and verify both old outward responses."""
from gzip import decompress
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
LEAD = "receipts/LEAD.json"
FORWARD = "receipts/FORWARD.json"
CONTACTS = "receipts/CONTACTS.json"
WORD = "inputs/7481-WORD.json.gz"
PINNED = {
    "PROVENANCE.json", "inputs/7113-CALLER.json", "inputs/7481-APPLICATION.json",
    WORD, "inputs/gate.py", "lead/check_owned1548.py",
    "independent/check_owned1548_forward.py", LEAD, FORWARD, CONTACTS,
}
CASE = "owned1548-two-receivers-advanced-913-1298-pre46664"
DONORS = [913, 1197, 587, 1494]


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


def check_contacts(trace, tape):
    start, end = trace["clock_range"]
    assert (start, end) == (39769, 56017)
    roles = trace["roles"]
    assert roles == [927, 913, 1197, 587, 1494, 1298, 1429, 1548, 1153, 665]
    assert all(tape[int(clock)] == event for clock, event in trace["key_clocks"].items())
    contacts = {str(role): [] for role in roles}
    for clock in range(start, end + 1):
        event = tape[clock]
        touched = set(event[1:3] if event[0] in ("ADD", "COPY") else event[1:2])
        for role in touched.intersection(roles):
            contacts[str(role)].append([clock, event])
    assert contacts == trace["contacts"]


def check_separator(actual, lead):
    assert actual["status"] == "PASS_INDEPENDENT_NAMED_DONOR_EXCLUSION"
    assert actual["case"] == lead["case"] == CASE
    assert actual["probe"] == lead["probe"] == {"164": "4"}
    assert actual["donor_responses"] == {str(role): "0" for role in DONORS}
    assert actual["required_each"] == 1 and actual["owner1548_source_and_retirement"] == "-2"
    assert actual["old_cut_recipients"] == {"1298": "0", "1429": "-1/8"}
    assert actual["unrepaired_cut_recipients"] == {"1298": "-1", "1429": "-9/8"}
    old = actual["first_reads_old_before_donor_after"]
    edited = actual["first_reads_edited_before_donor_after"]
    assert (old["46664"][-1], edited["46664"][-1]) == ("7/8", "-1/8")
    assert (old["47723"][-1], edited["47723"][-1]) == ("0", "-1")
    assert actual["controls"] == {"oracle_target_restores_both": True, "sign_flip_rejected_by_both": True}


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
    check_contacts(parse((ROOT / CONTACTS).read_bytes()), parse(decompress((ROOT / WORD).read_bytes()))["program"])
    raw_lead = reproduce("lead/check_owned1548.py", ROOT / "inputs")
    assert raw_lead == (ROOT / LEAD).read_bytes()
    lead = parse(raw_lead)
    assert lead["status"] == "EXACT_NAMED_DONOR_EXCLUSION"
    assert lead["tested"] == 1 and lead["unresolved"] == []
    assert lead["cut"] == 46664 and lead["donors"] == DONORS and lead["donor_rank"] == 4
    assert lead["recipients"] == [1298, 1429]
    assert lead["gross_raw"] == 17 and lead["signed_paid_delta"] == {"1": -17}
    forward = reproduce("independent/check_owned1548_forward.py", ROOT, ROOT / LEAD, pins[LEAD])
    actual = parse(forward)
    assert 0 <= actual.pop("seconds") < 30
    assert actual == parse((ROOT / FORWARD).read_bytes())
    check_separator(actual, lead)
    rejects(lambda: parse('{"input":0,"input":1}'))
    rejects(lambda: check_hash(b"changed word", pins[WORD]))
    rejects(lambda: check_separator(dict(actual, required_each=-1), lead))
    print("PASS_OWNED1548_TWO_RECIPIENT_BOUND: one exact four-donor separator")


if __name__ == "__main__":
    main()
