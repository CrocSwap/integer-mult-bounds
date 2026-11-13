"""Reproduce the two independent all-boundary sweeps and the exact price."""
from fractions import Fraction
from hashlib import sha256
from json import loads
from pathlib import Path
from runpy import run_path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
INPUTS = ROOT / "inputs"
FORWARD = "receipts/FORWARD.json"
REVERSE = "receipts/REVERSE.json"
PRICE = "receipts/PRICE.json"
PINNED = {
    "PROVENANCE.json", "check_rank17_reverse.py",
    "inputs/7113-CALLER.json", "inputs/7481-APPLICATION.json", "inputs/pricing.py",
    "next-root28/7398/engines/forward.py", "next-root28/7398/inputs/reverse.py",
    "next-root28/check_all_rank17_forward.py", FORWARD, REVERSE, PRICE,
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
    assert not result.stderr
    return result.stdout


def reverse_record(data):
    record = parse(data)
    assert record.pop("seconds") < 30
    return record


def cross_check(forward, reverse):
    assert forward["status"] == "EXACT_FIXED_PREFIX_CENSUS" and forward["unresolved"] == []
    assert reverse["status"] == "PASS_ALL_RANK17_REVERSE_BOUNDARIES"
    assert reverse["boundaries"] == forward["case_count"] == 19136
    assert reverse["runner_cap_seconds"] == forward["runner_cap_seconds"] == 30
    assert reverse["roots"].keys() == forward["roots"].keys() == {"7", "10", "25", "28"}
    parity = 0
    foreign = 0
    for root, r in reverse["roots"].items():
        f = forward["roots"][root]
        assert r["endpoint_recovered"] and f["endpoint_recovered"]
        assert r["last_completed_cut"] == 0 and r["unvisited"] is None
        assert f["classified_boundaries"] == 4784
        assert r["survivors"] == f["survivors"] == []
        assert r["intervals"] == f["intervals"]
        assert r["first_witness"] == f["witnesses"]
        assert r["counts"].get("mixed_body", 0) == 0
        parity += r["counts"]["mixed_parity"]
        foreign += r["counts"]["foreign_body"]
    assert (parity, foreign) == (1208, 17928)
    for cut in ("1767", "1768"):
        old = reverse["roots"]["28"]["prior_cuts"][cut]
        assert old["decision"] == "foreign_body" and [18, 0, [], "-1", "0"] in old["terms"]


def price_check(pins, price):
    inputs = {"7481-APPLICATION.json", "pricing.py"}
    assert {name: pins[f"inputs/{name}"] for name in inputs} == price["pins"]
    app = parse((INPUTS / "7481-APPLICATION.json").read_bytes())
    assert app["caller_head"] == "07a76c5e2738882c0cb322278e56f6cae3c9885d"
    lo, hi = map(Fraction, app["directed_crossing_bracket"])
    power = run_path(str(INPUTS / "pricing.py"))["power_bounds"]
    lower = 96 * (power(8, hi)[0] + power(9, hi)[0] - power(17, lo)[1])
    upper = 96 * (power(8, lo)[1] + power(9, lo)[1] - power(17, hi)[0])
    assert Fraction("4.07820585157566") < lower <= upper < Fraction("4.07820585157568")
    assert price["gross"] == [str(lower), str(upper)] and price["paid_delta"] == {}
    assert price["productive_delta"] == {"8": 96, "9": 96, "17": -96}
    assert price["net_upper_with_rank_one_per_port"] == str(upper - 96)


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
    for name, digest in pins.items():
        check_hash((ROOT / name).read_bytes(), digest)
    forward = reproduce("next-root28/check_all_rank17_forward.py", INPUTS)
    assert forward == (ROOT / FORWARD).read_bytes()
    reverse = reverse_record(reproduce("check_rank17_reverse.py", ROOT, "--forward-receipt",
                                       ROOT / FORWARD, "--forward-sha256", pins[FORWARD]))
    assert reverse == reverse_record((ROOT / REVERSE).read_bytes())
    cross_check(parse(forward), reverse)
    price_check(pins, parse((ROOT / PRICE).read_bytes()))
    rejects(lambda: parse('{"cut":0,"cut":1}'))
    rejects(lambda: check_hash(b"changed caller", pins["inputs/7113-CALLER.json"]))
    wrong = parse(forward)
    wrong["roots"]["28"]["survivors"] = [{"cut": 1767}]
    rejects(lambda: cross_check(wrong, reverse))
    print("PASS_RANK17_ALL_PREFIX_BOUND: 19136 exact root/boundary exclusions")


if __name__ == "__main__":
    main()
