"""Authenticate and replay the exact chart-549 paid bypass exclusion."""
from fractions import Fraction
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
FILES = {
    "7481-WORD.json.gz", "7481-APPLICATION.json", "gate.py", "gate235.py", "pricing.py",
    "PROVENANCE.json", "verify_separator.py", "receipts/SPARSE.json", "receipts/DENSE.json",
    "receipts/SEPARATOR.json",
}


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), "duplicate JSON key"
    return result


def parse(raw):
    return loads(raw, object_pairs_hook=unique)


def check(raw, digest):
    assert sha256(raw).hexdigest() == digest, "changed bytes"


def compare(sparse, dense, separator):
    assert sparse["completed_cases"] == 1 and sparse["runner_cap_seconds"] == 30
    assert sparse["decision"] == "excluded at fixed bank"
    assert sparse["bank_rank"] == 4 and sparse["union_rank"] == 5
    assert sparse["exact_separating_old_input"] == dense["old_inputs"] == separator == {"7": "1"}
    assert dense["role"] == sparse["role"] == 235
    assert dense["cut"] == sparse["clocks"][1] == 39249
    assert dense["chart"] == sparse["charts"][1] == 549
    assert dense["bank"] == {str(role): "0" for role in sparse["bank"]}
    assert dense["status"] == "EXACT_SIGNED_SEPARATOR"
    assert Fraction(dense["required_old_ADD_delta"]) == -Fraction(sparse["separating_read_value"]) / 2
    assert sparse["conditional_signed_paid_delta"] == {"2": -17, "4": -17, "6": 17}
    assert sparse["conditional_signed_productive_delta"] == {}
    low, high = map(Fraction, sparse["optimistic_signed_saving"])
    assert Fraction("0.2355") < low <= high < Fraction("0.2356")


def expect_failure(action):
    try:
        action()
    except AssertionError:
        return
    raise AssertionError("mutated input or receipt passed")


def main():
    assert __debug__ and implementation.name == "cpython" and version_info[:2] == (3, 12)
    pins = parse((ROOT / "PINS.json").read_bytes())
    assert set(pins) == FILES
    inputs = {name: (ROOT / name).read_bytes() for name in sorted(FILES)}
    for name, raw in inputs.items():
        check(raw, pins[name])
    sparse = parse(run([executable, "-I", "-B", str(ROOT / "gate235.py")], check=True,
                       capture_output=True, timeout=32).stdout)
    dense = parse(run([executable, "-I", "-B", str(ROOT / "verify_separator.py"),
                       str(ROOT / "receipts/SEPARATOR.json")], check=True,
                      capture_output=True, timeout=32).stdout)
    assert sparse == parse(inputs["receipts/SPARSE.json"])
    assert dense == parse(inputs["receipts/DENSE.json"])
    separator = parse(inputs["receipts/SEPARATOR.json"])
    compare(sparse, dense, separator)
    word = inputs["7481-WORD.json.gz"]
    expect_failure(lambda: check(bytes([word[0] ^ 1]) + word[1:], pins["7481-WORD.json.gz"]))
    expect_failure(lambda: parse('{"word":0,"word":1}'))
    expect_failure(lambda: compare(sparse, dict(dense, required_old_ADD_delta="1/2"), separator))
    print("PASS_ROLE235_PAID_BYPASS: one exact case, zero survivors, signed separator verified")


if __name__ == "__main__":
    main()
