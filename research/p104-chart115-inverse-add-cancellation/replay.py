"""Regenerate the chart-115 cancellation and check exact independent replay."""
from gzip import decompress
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
REVERSE = "receipts/REVERSE.json"
FORWARD = "receipts/FORWARD.json"
EXTRACTION = "receipts/EXTRACTION.json"
ENGINE_NAMES = {"audit_native.py", "clifford_exact.py", "native_verify.py"}
PINNED = {
    "PROVENANCE.json", "inputs/7113-CALLER.json", "inputs/7481-APPLICATION.json",
    "inputs/7481-WORD.json.gz", "next-chart115/check_native.py",
    "next-chart115/retained_independent.py", "independent/check_chart115_component.py",
    *(f"independent/engines/{name}" for name in ENGINE_NAMES), REVERSE, FORWARD, EXTRACTION,
}


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
    return result.stdout, result.stderr.splitlines()


def check_component(actual, reverse, candidate):
    assert actual["status"] == "PASS_CHART115_PHYSICAL_FORWARD_ORDINARY"
    assert reverse["status"] == "PASS_NORMALIZED_CHART115_CANCELLATION"
    assert reverse["omitted_one_add_bad_inputs"] == [751]
    assert reverse["old"]["bad_inputs"] == reverse["new"]["bad_inputs"] == []
    assert reverse["old"]["public"] == reverse["new"]["public"] == 1501
    assert reverse["old"]["events"] - reverse["new"]["events"] == 2
    assert all(reverse["old"][key] == reverse["new"][key] for key in reverse["old"] if key != "events")
    assert actual["canonical_candidate_sha256"] == reverse["word_sha256"] == candidate
    physical = actual["physical"]
    assert physical["chart_pair"] == [3, 115] and physical["move_clocks"] == [38002, 38003]
    assert physical["rank"] == 5 and physical["phase_mutant_rejected"]
    assert physical["forward_columns"] == physical["adjoint_columns"] == 512
    assert actual["forward"]["all_rows"] == 1569 and actual["forward"]["owned_clear_rows"] == 74
    assert actual["forward"]["copy_guards"] == 1
    assert actual["ordinary_original"]["conservative_total"] == 782785912
    assert actual["ordinary_edited"]["conservative_total"] == 782785368
    assert actual["ordinary_saved"] == 544


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
    extraction = parse((ROOT / EXTRACTION).read_bytes())
    assert extraction["status"] == "PASS_EXTRACT_EXACT_RETAINED_ENGINES"
    assert extraction["pins"] == {f"engines/{name}": pins[f"independent/engines/{name}"] for name in ENGINE_NAMES}
    with TemporaryDirectory(prefix="chart115-") as directory:
        word = Path(directory) / "WORD.json.gz"
        raw_reverse, stderr = reproduce("next-chart115/check_native.py", "--write-word", word, timeout=32)
        assert not stderr and raw_reverse == (ROOT / REVERSE).read_bytes()
        reverse = parse(raw_reverse)
        candidate = sha256(decompress(word.read_bytes())).hexdigest()
    forward, progress = reproduce("independent/check_chart115_component.py", ROOT, timeout=362)
    assert progress == [
        b"PASS_CHART115_ALL_PHYSICAL_COLUMNS", b"PASS_PINNED_OLD_FORWARD_GRID",
        b"PASS_CHART115_COMPLETE_FORWARD_GRID",
    ]
    actual = parse(forward)
    assert 0 <= actual.pop("seconds") < actual["cap_seconds"] == 360
    assert actual == parse((ROOT / FORWARD).read_bytes())
    check_component(actual, reverse, candidate)
    rejects(lambda: parse('{"input":0,"input":1}'))
    rejects(lambda: check_hash(b"changed word", pins["inputs/7481-WORD.json.gz"]))
    rejects(lambda: check_component(dict(actual, ordinary_saved=0), reverse, candidate))
    print("PASS_CHART115_INVERSE_ADD_CANCELLATION: two ADDs and 544 ordinary units removed")


if __name__ == "__main__":
    main()
