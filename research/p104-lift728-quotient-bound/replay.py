"""Reproduce and independently verify the two-direction quotient obstruction."""
from fractions import Fraction
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
    "next-lift728/check_quotient.py", "next-lift728/integer_basis.py",
    "independent/check_lift728_forward.py", LEAD, FORWARD,
}
CASE = "lift728-owned1537-chart127-pre49170"


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


def check_minor(actual, lead):
    assert actual["status"] == "PASS_INDEPENDENT_TWO_DIRECTION_QUOTIENT_EXCLUSION"
    assert actual["case"] == lead["case"] == CASE
    assert actual["bank_roles"] == lead["bank_roles"]
    assert len(actual["bank_roles"]) == len(set(actual["bank_roles"])) == 827
    assert 1397 in actual["bank_roles"] and not {1004, 728} & set(actual["bank_roles"])
    records = actual["records"]
    assert len(records) == 2 and [record["probe"] for record in records] == lead["probes"]
    assert all(record["whole_unchanged_bank_zero"] and record["bank_role_count"] == 827 for record in records)
    first = records[0]
    assert first["old1004_before_scale"] == "0" and first["unrepaired1004_before_scale"] == "-1/4"
    assert first["encoded_carrier_at_alpha_one"] == "1/4"
    minor = [[record["e"], record["t"]] for record in records]
    assert minor == actual["minor"] == lead["minor"] == [["0", "1/4"], ["1", "0"]]
    (a, b), (c, d) = [list(map(Fraction, row)) for row in minor]
    assert a*d-b*c == Fraction(actual["determinant"]) == Fraction(lead["determinant"]) == Fraction(-1, 4)


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
    raw_lead, progress = reproduce("next-lift728/check_quotient.py")
    assert progress == [b"PINNED_CHRONOLOGY_AND_PRICE", b"BANK_READY 827", b"FIRST_DIRECTION_SEPARATED 827"]
    assert raw_lead == (ROOT / LEAD).read_bytes()
    lead = parse(raw_lead)
    assert lead["status"] == "EXACT_TWO_DIRECTION_QUOTIENT_EXCLUSION"
    assert lead["unresolved"] == [] and lead["cut"] == 49170
    assert (lead["bank_rank"], lead["augmented_rank"]) == (827, 828)
    forward, stderr = reproduce("independent/check_lift728_forward.py", ROOT, ROOT / LEAD, pins[LEAD])
    assert not stderr
    actual = parse(forward)
    assert 0 <= actual.pop("seconds") < 30
    assert actual == parse((ROOT / FORWARD).read_bytes())
    check_minor(actual, lead)
    rejects(lambda: parse('{"input":0,"input":1}'))
    rejects(lambda: check_hash(b"changed word", pins["inputs/7481-WORD.json.gz"]))
    rejects(lambda: check_minor(dict(actual, determinant="0"), lead))
    print("PASS_LIFT728_QUOTIENT_BOUND: two independent directions modulo 827 fixed rows")


if __name__ == "__main__":
    main()
