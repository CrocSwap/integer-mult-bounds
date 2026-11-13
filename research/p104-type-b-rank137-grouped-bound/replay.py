"""Regenerate the grouped Type B census and compare independent reverse replay."""
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
FOCUSED = "receipts/FOCUSED.json"
FOCUSED_REVERSE = "receipts/FOCUSED-REVERSE.json"
EXPECTED = "receipts/EXPECTED.json"
ALL_REVERSE = "receipts/ALL-REVERSE.json"
PINNED = {
    "PROVENANCE.json", "inputs/7113-CALLER.json", "inputs/7481-APPLICATION.json",
    "inputs/pricing.py", "all-masks/check_type_b_root.py", "all-masks/type_a_laurent.py",
    "all-masks/check_type_b_all_masks.py", "independent/check_type_b_reverse.py",
    "independent/check_type_b_all_reverse.py", FOCUSED, FOCUSED_REVERSE, EXPECTED, ALL_REVERSE,
}
CUTS = 4784
CLASS_COUNT = 2 * (2**17 - 2)


def unique(items):
    result = dict(items)
    assert len(result) == len(items), "duplicate JSON key"
    return result


def parse(data):
    return loads(data, object_pairs_hook=unique)


def check_hash(data, digest):
    assert sha256(data).hexdigest() == digest, "changed pinned bytes"


def reproduce(script, *arguments, timeout):
    result = run([executable, "-I", "-B", str(ROOT / script), *map(str, arguments)],
                 capture_output=True, timeout=timeout, check=True)
    assert not result.stderr
    return result.stdout


def check_forward(data, expected):
    lines = data.splitlines(keepends=True)
    assert len(lines) == CUTS + 2
    for i, key in ((0, "header"), (-1, "footer")):
        record = parse(lines[i])
        assert record["cap_seconds"] == 120
        record["cap_seconds"] = 30
        assert record == expected[key]
        lines[i] = dumps(record, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    exact = b"".join(lines)
    check_hash(exact, expected["discovery_transcript_sha256"])
    counts = {"plus": 0, "minus": 0}
    for clock, line in enumerate(lines[1:-1]):
        record = parse(line)
        assert record["cut"] == clock and not record["surviving_classes"]
        for sign in counts:
            result = record[sign]
            assert result["base_minor"]["rank"] == 2 and not result["survivors"]
            assert len(result["checked_classes"]) == len(result["rejected"]) <= 2
            counts[sign] += len(result["checked_classes"])
    assert counts == expected["residual_checks"] == {"plus": 4883, "minus": 4883}
    assert expected["covered_cut_mask_parity_keys"] == CUTS * CLASS_COUNT
    return exact


def normalized(data):
    result = parse(data)
    assert 0 <= result.pop("seconds") < result["cap_seconds"]
    return result


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
    focused = reproduce("all-masks/check_type_b_root.py", ROOT / "inputs", timeout=32)
    assert focused == (ROOT / FOCUSED).read_bytes()
    independent = reproduce("independent/check_type_b_reverse.py", ROOT, ROOT / FOCUSED,
                            pins[FOCUSED], timeout=32)
    fixed = normalized(independent)
    assert fixed == parse((ROOT / FOCUSED_REVERSE).read_bytes())
    assert fixed["status"] == "PASS_INDEPENDENT_GROUPED_PREFIX_EXCLUSION"
    assert fixed["cut"] == 3058 and fixed["unresolved"] == []
    assert fixed["sectors"]["1"]["lead_minor_determinant"] == ["1/2", "0"]
    assert fixed["sectors"]["-1"]["lead_minor_determinant"] == ["0", "-1/2"]
    expected = parse((ROOT / EXPECTED).read_bytes())
    forward = reproduce("all-masks/check_type_b_all_masks.py", ROOT / "inputs", "--cap", 120, timeout=122)
    exact = check_forward(forward, expected)
    with TemporaryDirectory(prefix="type-b-rank137-") as directory:
        journal = Path(directory) / "forward.jsonl"
        journal.write_bytes(exact)
        reverse = reproduce("independent/check_type_b_all_reverse.py", ROOT, journal,
                            expected["discovery_transcript_sha256"], "--cap-seconds", 120, timeout=122)
        reverse = normalized(reverse)
        assert reverse.pop("cap_seconds") == 120
        assert reverse == parse((ROOT / ALL_REVERSE).read_bytes())
        assert reverse["status"] == "PASS_INDEPENDENT_ALL_CUTS_ALL_MASKS"
        assert reverse["cuts_tested"] == CUTS and reverse["conceptual_cases"] == CUTS * CLASS_COUNT
        assert reverse["survivors"] == reverse["unresolved"] == []
    rejects(lambda: parse('{"input":0,"input":1}'))
    rejects(lambda: check_hash(b"changed caller", pins["inputs/7113-CALLER.json"]))
    rejects(lambda: check_forward(forward.split(b"\n", 1)[1], expected))
    print("PASS_TYPE_B_RANK137_GROUPED_BOUND: 4784 cuts and no surviving proper mask or parity")


if __name__ == "__main__":
    main()
