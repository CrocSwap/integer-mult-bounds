"""Reproduce two exact productive endpoint exchange gates on the pinned native word."""
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
INPUTS = ROOT / "inputs"
WORD = INPUTS / "7481-WORD.json.gz"
RUNNERS = (
    ("lead/check_exchange.py", "--inputs", INPUTS),
    ("independent/check_endpoint_windows.py", "--inputs", INPUTS),
    ("pivot/check_cycle.py",),
    ("cycle-prefix-independent/cycle1049_prefix.py", "--word", WORD),
    ("cycle-independent/cycle1049_forward.py", "--word", WORD),
)
RECEIPTS = (
    "PAIR-WINDOWS.json",
    "CYCLE-PREFIX.json",
    "CYCLE-PREFIX-FORWARD.json",
    "CYCLE-SUFFIX.json",
)
PINNED = {"PROVENANCE.json", "inputs/7113-CALLER.json", "inputs/7481-APPLICATION.json",
          "inputs/7481-WORD.json.gz", "inputs/gate.py", "inputs/pricing.py"}
PINNED.update(spec[0] for spec in RUNNERS)
PINNED.update(f"receipts/{receipt}" for receipt in RECEIPTS)


def unique(items):
    result = dict(items)
    assert len(result) == len(items), "duplicate JSON key"
    return result


def read_json(raw):
    return loads(raw, object_pairs_hook=unique)


def same_bytes(raw, digest):
    assert sha256(raw).hexdigest() == digest, "changed bytes"


def reproduce(spec):
    runner, *arguments = spec
    result = run([executable, "-I", "-B", str(ROOT / runner), *map(str, arguments)],
                 capture_output=True, check=True, timeout=32)
    actual = read_json(result.stdout)
    actual.pop("seconds", None)
    return actual


def canonical(value):
    return dumps(value, sort_keys=True, separators=(",", ":")).encode()


def pair_key(lead_id):
    start, stop, chart, (left, right) = lead_id
    return (start, stop, left, right, chart)


def compare_pair(lead, independent, pinned):
    for label, data in (("lead", lead), ("independent", independent)):
        same_bytes(canonical(data), pinned["raw_results"][label]["normalized_sha256"])
        assert data["status"] == "EXHAUSTED"
    assert lead["time_cap_seconds"] == 30
    assert lead["matrix_cap"] == independent["case_cap"] == 32
    assert independent["window_length_limit"] == 64
    assert not (lead["unresolved"] or independent["open_cap_cases"])
    assert not independent["survivor_ids"]
    assert lead["counts"] == pinned["primary_counts"]
    assert independent["classification_counts"] == pinned["independent_counts"]
    assert lead["tested"] == pinned["tested"]
    assert independent["regressions"] == pinned["regressions"]
    assert len(independent["regressions"]) == 9
    assert all(result == "hosted" for _, _, result in independent["regressions"])
    mapping = {
        "hosted": "fixed_main_role",
        "crossed_not_strictly_nested": "not_strictly_positive_crossed_price",
        "equal_price": "not_strictly_positive_crossed_price",
        "negative_price": "not_strictly_positive_crossed_price",
        "positive_price": "eligible",
    }
    primary = {pair_key(i): label for label, ids in lead["rejected_ids"].items() for i in ids}
    primary.update((pair_key(row["id"]), "eligible") for row in lead["tested"])
    other = {tuple(case[:-1]): mapping[case[-1]] for case in independent["classified_windows"]}
    assert len(primary) == len(other) == independent["metadata_window_count"] == 60806
    assert primary == other
    for row, check in zip(lead["tested"], independent["checked"], strict=True):
        assert pair_key(row["id"]) == tuple(check["case"])
        assert row["old"] == check["old_ranks"] and row["new"] == check["new_ranks"]
        assert row["gross"] == check["raw_signed_saving_interval"]
        assert 0 < Fraction(row["gross"][0]) <= Fraction(row["gross"][1]) < 17
        assert row["action"] == check["matrix"]
        assert not row["signed_exchange"] and not check["crossed_monomial"]
    assert len(lead["tested"]) == len(independent["checked"]) == 8


def compare_cycle(prefix, forward, suffix):
    assert prefix["status"] == "PREFIX_EXCLUDES_FIXED_CYCLE"
    assert forward["status"] == "PASS_BOTH_EXACT_FORWARD_PREFIX_SEPARATORS"
    assert suffix["status"] == "PASS_OUTSIDE_RANK_TWO_EXCLUSION"
    assert prefix["cut"] == forward["cut_before"] == suffix["cut_before"] == 36481
    assert forward["chart"] == suffix["chart"] == 1049
    assert prefix["bank"] == forward["bank_order"] == suffix["carrier_order"] == [1322, 1352, 1440]
    assert prefix["old_ranks"] == suffix["old_productive_ranks"] == [9, 5, 2]
    assert prefix["new_ranks"] == suffix["new_productive_ranks"] == [5, 7, 4]
    lo, hi = map(Fraction, prefix["gross"])
    assert Fraction("0.12252") < lo <= hi < Fraction("0.12253")
    assert prefix["case_count"] == forward["case_count"] == suffix["cases_completed"] == 1
    assert prefix["cap_seconds"] == forward["cap_seconds"] == suffix["cap_seconds"] == 30
    for left, right in zip(prefix["contrasts"], forward["checks"], strict=True):
        assert left["probe"] == right["probe"]
        assert list(map(Fraction, left["bank_response"])) == right["cut_bank"] == [0, 0, 0]
        assert left["target_response"] == right["contrast"]
    assert [check["contrast"] for check in forward["checks"]] == ["1", "-1"]
    witness = suffix["witness"]
    assert witness["constraint_rows"] == [["outside_output", 3], ["outside_output", 683]]
    assert witness["carrier_columns"] == [1322, 1440]
    (a, b), (c, d) = [list(map(Fraction, row)) for row in witness["matrix"]]
    assert a * d - b * c == Fraction(witness["determinant"]) == Fraction("-73767/4096")
    assert not suffix["copy_init_guard_responses"] and not suffix["inherited_clear_operands"]
    assert not suffix["mutant_has_rank_two_minor"]


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
    pinned_pair, pinned_prefix, pinned_forward, pinned_suffix = (
        read_json((ROOT / "receipts" / name).read_bytes()) for name in RECEIPTS)
    lead, independent, prefix, forward, suffix = (reproduce(spec) for spec in RUNNERS)
    compare_pair(lead, independent, pinned_pair)
    assert (prefix, forward, suffix) == (pinned_prefix, pinned_forward, pinned_suffix)
    compare_cycle(prefix, forward, suffix)
    rejects(lambda: read_json('{"x":0,"x":1}'))
    rejects(lambda: same_bytes(b"mutated", pins["inputs/7481-WORD.json.gz"]))
    bad_witness = dict(suffix["witness"], determinant="0")
    rejects(lambda: compare_cycle(prefix, forward, dict(suffix, witness=bad_witness)))
    print("PASS_FIXED_PAID_ENDPOINT_EXCHANGES: 60806 windows, eight matrices, one three-role cycle")


if __name__ == "__main__":
    main()
