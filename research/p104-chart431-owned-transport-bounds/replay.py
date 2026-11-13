"""Replay three exact bank exclusions for the #7481 chart 431 owned transports."""
from fractions import Fraction
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
WORD = ROOT / "inputs/7481-WORD.json.gz"
RECEIPTS = ROOT / "receipts"
RUNNERS = (
    ("FORK-REVERSE.json", "fork/check_provider.py"),
    ("FORK-FORWARD.json", "fork-independent/provider34568_forward.py",
     "--word", WORD, "--probe", RECEIPTS / "FORK-PROBE.json"),
    ("SOURCE-REVERSE.json", "source/check_source1348.py", "--method", "reverse"),
    ("SOURCE-FORWARD.json", "source-independent/check_forward.py",
     "--word", WORD, "--solver-receipt", RECEIPTS / "SOURCE-REVERSE.json", "--method", "reverse"),
    ("PRODUCT-REVERSE.json", "product/check_return_extended.py", "--include-retained-product"),
    ("PRODUCT-FORWARD.json", "product-independent/extended/check_extended.py",
     "--word", WORD, "--probe", RECEIPTS / "PRODUCT-PROBE.json"),
)
PINNED = {"PROVENANCE.json", "inputs/7113-CALLER.json", "inputs/7481-APPLICATION.json",
          "inputs/7481-WORD.json.gz", "inputs/gate.py", "inputs/pricing.py",
          "receipts/FORK-PROBE.json", "receipts/PRODUCT-PROBE.json",
          "product-independent/product35452_forward.py"}
PINNED.update(spec[1] for spec in RUNNERS)
PINNED.update(f"receipts/{spec[0]}" for spec in RUNNERS)


def unique(items):
    result = dict(items)
    assert len(result) == len(items), "duplicate JSON key"
    return result


def read_json(raw):
    return loads(raw, object_pairs_hook=unique)


def same_bytes(raw, digest):
    assert sha256(raw).hexdigest() == digest, "changed bytes"


def reproduce(spec):
    receipt, runner, *arguments = spec
    result = run([executable, "-I", "-B", str(ROOT / runner), *map(str, arguments)],
                 capture_output=True, check=True, timeout=32)
    actual = read_json(result.stdout)
    actual.pop("seconds", None)
    expected = read_json((RECEIPTS / receipt).read_bytes())
    assert actual == expected, receipt
    return actual


def compare_fork(reverse, forward):
    assert reverse["status"] == "FIXED_OBSERVER_BANK_EXCLUDED"
    assert forward["status"] == "PASS_FULL_FIXED_CHART431_BANK_SEPARATOR"
    assert reverse["read"] == forward["cut_before"] == 34568
    assert reverse["old_bank"] == forward["old_bank"]
    assert set(map(int, forward["surviving_bank"])) == {375, 1135, 1137, 1348, 1535}
    assert not any(forward["surviving_bank"].values())
    assert forward["probe"] == {"2": "1"}
    assert reverse["old_u_response"] == forward["old_owned_1518"] == "1"
    assert reverse["needed_outward_response"] == forward["old_outward_add_contribution"] == "-1"
    assert forward["old_owned_1519"] == forward["old_owned_provider_1507"] == "1/4"
    assert forward["control_drop_ADD34529"] == {
        "old_1507": 0, "old_1519": 0, "unchanged_1518": "1"}


def compare_source(reverse, forward):
    assert reverse["decision"] == "FIXED_SOURCE_BANK_EXCLUDED"
    assert forward["status"] == "PASS_INDEPENDENT_EXACT_SOURCE_SEPARATOR"
    assert reverse["case_id"] == forward["case_id"] == "7481:1348:pre34566:chart3:old1513@34527"
    assert forward["source_cut_before"] == 34566 and forward["provider_read_before"] == 34527
    assert reverse["witness"] == forward["probe"] == {"2": "1"}
    bank = forward["full_source_bank"]
    assert sorted(map(int, bank)) == reverse["bank"] and len(bank) == 623 and "1348" in bank
    assert not any(bank.values())
    assert reverse["old_u_response"] == forward["old_u_response"] == "1"
    assert forward["zero_probe_control_old_u_response"] == 0
    same_bytes((RECEIPTS / "SOURCE-REVERSE.json").read_bytes(), forward["solver_receipt_sha256"])


def compare_product(reverse, forward):
    assert reverse["status"] == "BANK_EXCLUDES_HISTORICAL_OPERAND"
    assert forward["status"] == "PASS_BANK_AND_RETAINED_PRODUCT_SEPARATOR"
    assert reverse["cut"] == forward["return_cut_before"] == 35452
    assert reverse["historical_read"] == forward["source_before"] == 34379
    assert reverse["granted_retained_product"] and reverse["bank_rank"] == 22
    assert len(reverse["bank"]) == 22 and sorted(map(int, forward["bank"])) == reverse["bank"]
    assert not any(forward["bank"].values())
    assert reverse["witness"] == forward["probe"]
    assert Fraction(reverse["old1545_at_witness"]) == Fraction(forward["old_product_1545"]) == 0
    assert reverse["target_value"] == forward["old_source_1137"] == "-1/2"
    assert Fraction(forward["old_return_1544"]) == Fraction("-1/2")
    assert forward["control_drop_ADD34379"]["return_1544"] == 0
    same_bytes((RECEIPTS / "PRODUCT-PROBE.json").read_bytes(), forward["probe_sha256"])


def rejects(check):
    try:
        check()
    except AssertionError:
        return
    raise AssertionError("negative control unexpectedly passed")


def main():
    assert __debug__ and implementation.name == "cpython" and version_info[:2] == (3, 12)
    pins = read_json((ROOT / "PINS.json").read_bytes())
    assert set(pins) == PINNED
    for name, digest in pins.items():
        same_bytes((ROOT / name).read_bytes(), digest)
    a, b, c, d, e, f = (reproduce(spec) for spec in RUNNERS)
    compare_fork(a, b)
    compare_source(c, d)
    compare_product(e, f)
    assert a["gross"] == e["gross_exact"]
    low, high = map(Fraction, a["gross"])
    assert Fraction("0.11809207775534") < low <= high < Fraction("0.11809207775535") < 17
    rejects(lambda: read_json('{"x":0,"x":1}'))
    rejects(lambda: same_bytes(b"mutated", pins["inputs/7481-WORD.json.gz"]))
    rejects(lambda: compare_product(e, dict(f, old_product_1545="1")))
    print("PASS_CHART431_OWNED_TRANSPORTS: three exact cuts and six source-bound receipts")


if __name__ == "__main__":
    main()
