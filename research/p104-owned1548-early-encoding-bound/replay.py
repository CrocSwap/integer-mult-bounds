"""Regenerate the fixed first-use quotient obstruction and contact trace."""
from fractions import Fraction
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
    WORD, "inputs/gate.py", "lead/check_owned1548_early.py", "lead/integer_basis.py",
    "independent/check_owned1548_early_forward.py", LEAD, FORWARD, CONTACTS,
}
CASE = "owned1548-early-1197-1358-first-use-pre46664"
DONORS = [913, 587, 1494]
ROLES = [927, 913, 1197, 1358, 587, 1494, 1298, 1429, 1548, 1153, 665, 1075]


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
    assert (start, end) == (37960, 56017) and trace["roles"] == ROLES
    assert all(tape[int(clock)] == event for clock, event in trace["key_clocks"].items())
    contacts = {str(role): [] for role in ROLES}
    for clock in range(start, end + 1):
        event = tape[clock]
        touched = set(event[1:3] if event[0] in ("ADD", "COPY") else event[1:2])
        for role in touched.intersection(ROLES):
            contacts[str(role)].append([clock, event])
    assert contacts == trace["contacts"]


def check_minor(actual, lead):
    assert actual["status"] == "PASS_INDEPENDENT_FIRST_USE_RANK3_EXCLUSION"
    assert actual["case"] == lead["case"] == CASE
    records = actual["records"]
    assert [record["probe"] for record in records] == lead["probes"]
    assert all(record["bank"] == {str(role): "0" for role in DONORS} for record in records)
    assert all(record["old_peak"][0] == 50 and record["edited_peak"] == [51, 39811] for record in records)
    matrix = [record["a_b_u"] for record in records]
    assert matrix == actual["response_matrix"] == lead["response_matrix"]
    (a,b,c),(d,e,f),(g,h,i) = [list(map(Fraction, row)) for row in matrix]
    determinant = a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g)
    assert determinant == Fraction(actual["determinant"]) == Fraction(lead["determinant"]) == -2


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
    raw_lead = reproduce("lead/check_owned1548_early.py", ROOT / "inputs")
    assert raw_lead == (ROOT / LEAD).read_bytes()
    lead = parse(raw_lead)
    assert lead["status"] == "EXACT_FIRST_USE_RANK3_EXCLUSION"
    assert lead["tested"] == 1 and lead["unresolved"] == []
    assert lead["cut"] == 46664 and lead["donors"] == DONORS and lead["quotient_rank"] == 3
    assert lead["carried_original_rows"] == [1197, 1358] and lead["gross_raw"] == 17
    forward = reproduce("independent/check_owned1548_early_forward.py", ROOT, ROOT / LEAD, pins[LEAD])
    actual = parse(forward)
    assert 0 <= actual.pop("seconds") < 30
    assert actual == parse((ROOT / FORWARD).read_bytes())
    check_minor(actual, lead)
    rejects(lambda: parse('{"input":0,"input":1}'))
    rejects(lambda: check_hash(b"changed word", pins[WORD]))
    rejects(lambda: check_minor(dict(actual, determinant="0"), lead))
    print("PASS_OWNED1548_EARLY_ENCODING_BOUND: exact rank three at the first deadline")


if __name__ == "__main__":
    main()
