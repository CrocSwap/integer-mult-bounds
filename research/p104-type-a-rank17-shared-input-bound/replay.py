"""Regenerate the grouped prefix census, independent witnesses and price."""
from fractions import Fraction
from hashlib import sha256
from json import loads
from pathlib import Path
from runpy import run_path
from subprocess import run
from sys import executable, implementation, version_info
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
INPUTS = ROOT / "inputs"
PRICE = "receipts/PRICE.json"
EXPECTED = "receipts/EXPECTED.json"
FORWARD = "next-grouped/check_grouped_rank17.py"
REVERSE = "check_grouped_reverse.py"
PINNED = {
    "PROVENANCE.json", "inputs/7113-CALLER.json", "inputs/7481-APPLICATION.json",
    "inputs/pricing.py", "next-root28/7398/engines/forward.py",
    "next-root28/7398/inputs/reverse.py", FORWARD, REVERSE, PRICE, EXPECTED,
}
TOTAL = 38272
FORWARD_FINAL = {
    "status": "PASS_COMPLETE_GROUPED_RANK17_PREFIX_CENSUS",
    "completed": TOTAL, "remaining": 0, "survivors": [],
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


def check_forward(data, expected):
    transcript, footer, trailing = data.rsplit(b"\n", 2)
    assert not trailing
    check_hash(transcript + b"\n", expected["forward_transcript_sha256"])
    final = parse(footer)
    assert 0 <= final.pop("seconds") < 30
    assert final == FORWARD_FINAL == expected["forward_final"]
    assert len(transcript.splitlines()) == TOTAL + 1


def check_reverse(data, lead_digest, expected):
    result = parse(data)
    assert 0 <= result.pop("seconds") < 30
    assert result.pop("lead_sha256") == lead_digest
    assert result == expected["reverse"]
    assert result["status"] == "PASS_INDEPENDENT_GROUPED_RANK17_REVERSE"
    assert result["examined"] == result["lead_cases_checked"] == TOTAL
    assert result["survivors"] == result["unresolved"] == []
    assert result["counts"] == {"10/28": {"2/2": 19136}, "7/25": {"2/2": 19136}}


def check_price(pins, price):
    files = {"inputs/7481-APPLICATION.json", "inputs/pricing.py"}
    assert {path: pins[path] for path in files} == price["pins"]
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
    assert 4 * upper < 96


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
    expected = parse((ROOT / EXPECTED).read_bytes())
    forward = reproduce(FORWARD, ROOT)
    check_forward(forward, expected)
    rejects(lambda: parse('{"input":0,"input":1}'))
    rejects(lambda: check_hash(b"changed caller", pins["inputs/7113-CALLER.json"]))
    header, _, remainder = forward.split(b"\n", 2)
    rejects(lambda: check_forward(header + b"\n" + remainder, expected))
    with TemporaryDirectory(prefix="rank17-grouped-") as directory:
        journal = Path(directory) / "forward.jsonl"
        journal.write_bytes(forward)
        digest = sha256(forward).hexdigest()
        reverse = reproduce(REVERSE, ROOT, journal, digest)
        check_reverse(reverse, digest, expected)
    check_price(pins, parse((ROOT / PRICE).read_bytes()))
    print("PASS_RANK17_SHARED_INPUT_BOUND: 38272 exact pair/cut/order/parity exclusions")


if __name__ == "__main__":
    main()
