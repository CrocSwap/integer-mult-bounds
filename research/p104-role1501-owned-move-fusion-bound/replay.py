"""Authenticate and replay the exact role-1501 owned move fusion bound."""
from fractions import Fraction
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
FILES = {
    "7481-WORD.json.gz", "7481-APPLICATION.json", "gate.py", "pricing.py",
    "fuse_1501.py", "verify_fusion_probe.py", "PROVENANCE.json",
    "receipts/SPARSE.json", "receipts/DENSE.json",
}


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), "duplicate JSON key"
    return result


def parse(raw):
    return loads(raw, object_pairs_hook=unique)


def check(raw, digest):
    assert sha256(raw).hexdigest() == digest, "changed bytes"


def compare(sparse, dense):
    assert sparse["status"] == "LOCAL_FUSION_EXCLUDED"
    assert sparse["case_cap"] == 1 and sparse["runner_cap_seconds"] == 30
    assert sparse["points"] == [[40563, 549], [40567, 593]]
    assert sparse["banks"] == dense["bank_roles"]
    assert sparse["bank_rank"] == 15 and sparse["union_rank"] == 16
    assert sparse["target"] == {"607": "-1", "770": "1"}
    assert sparse["probe"] == dense["inputs"] == {"10": "-1", "173": "-1/2", "607": "-1"}
    assert dense["status"] == "PASS_LITERAL_FORWARD_SEPARATOR"
    assert dense["owned_donor"] == "1" and dense["old_outward_increment"] == "-1/2"
    assert dense["zero_control"] is True
    low, high = map(Fraction, sparse["whole_signed_gross"])
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
    outputs = []
    for engine, receipt in (("fuse_1501.py", "SPARSE.json"), ("verify_fusion_probe.py", "DENSE.json")):
        result = run([executable, "-I", "-B", str(ROOT / engine)], check=True,
                     capture_output=True, timeout=31)
        actual = parse(result.stdout)
        assert actual == parse(inputs[f"receipts/{receipt}"])
        outputs.append(actual)
    sparse, dense = outputs
    compare(sparse, dense)
    word = inputs["7481-WORD.json.gz"]
    expect_failure(lambda: check(bytes([word[0] ^ 1]) + word[1:], pins["7481-WORD.json.gz"]))
    expect_failure(lambda: parse('{"word":0,"word":1}'))
    expect_failure(lambda: compare(sparse, dict(dense, old_outward_increment="1/2")))
    print("PASS_ROLE1501_OWNED_MOVE_FUSION: one exact case, zero survivors, signed separator verified")


if __name__ == "__main__":
    main()
