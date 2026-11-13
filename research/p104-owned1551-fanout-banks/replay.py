"""Replay the two fixed chart-127 bank exclusions for owned role 1551."""
from fractions import Fraction
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
WORD = ROOT / "inputs/7481-WORD.json.gz"
RECEIPTS = ROOT / "receipts"
RECIPIENTS = {"790", "817", "833", "873", "878", "1497"}
RUNNERS = (
    ("EARLY-REVERSE.json", "early/check_named.py"),
    ("EARLY-FORWARD.json", "early-independent/fanout46149_forward.py",
     "--word", WORD, "--probe", RECEIPTS / "EARLY-PROBE.json"),
    ("LATE-REVERSE.jsonl", "lead/fast/check_first_outward.py"),
    ("LATE-PRIOR-PROBE.json", "independent/check_prior.py", "--word", WORD),
    ("LATE-FORWARD.json", "independent/verify_first_outward.py",
     "--word", WORD, "--witness", RECEIPTS / "LATE-PROBE.json"),
)
PINNED = {"PROVENANCE.json", "inputs/7113-CALLER.json", "inputs/7481-APPLICATION.json",
          "inputs/7481-WORD.json.gz", "inputs/gate.py", "inputs/pricing.py",
          "receipts/EARLY-PROBE.json", "receipts/LATE-PROBE.json",
          "receipts/LATE-CAPPED-PROVENANCE.jsonl", "lead/fast/integer_basis.py"}
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


def read_output(name, raw):
    if name.endswith(".jsonl"):
        return [read_json(line) for line in raw.splitlines()]
    result = read_json(raw)
    result.pop("seconds", None)
    return result


def reproduce(spec):
    receipt, runner, *arguments = spec
    result = run([executable, "-I", "-B", str(ROOT / runner), *map(str, arguments)],
                 capture_output=True, check=True, timeout=32)
    actual = read_output(receipt, result.stdout)
    expected = read_output(receipt, (RECEIPTS / receipt).read_bytes())
    assert actual == expected, receipt
    return actual


def compare_early(reverse, forward):
    assert reverse["status"] == "NAMED_ROUTE_EXCLUDED_EVEN_WITH_RECIPIENT"
    assert forward["status"] == "PASS_EXACT_NAMED_CARRIER_SEPARATOR"
    assert reverse["cut"] == forward["cut_before"] == 46149
    assert reverse["source"] == forward["target_before"] == 45636
    assert reverse["named_carriers"] == sorted(map(int, forward["named_bank"])) == [862, 988, 991, 1499]
    assert reverse["bank_rank"] == 4 and reverse["with_recipient_rank"] == 5
    assert not any(forward["named_bank"].values()) and forward["edited_first_recipient_873"] == 0
    assert reverse["witness"] == forward["probe"] == {"230": "-1", "547": "1"}
    assert reverse["target_response"] == forward["old_source_862"] == "-1"
    assert forward["control_omit_six_old_updates"]["modified_minus_old"] == dict.fromkeys(RECIPIENTS, "-1")
    assert reverse["case_cap"] == forward["cases_completed"] == 1
    assert reverse["cap_seconds"] == forward["runner_cap_seconds"] == 30
    low, high = map(Fraction, reverse["gross"])
    assert Fraction("67.65706456310") < low <= high < Fraction("67.65706456312")


def compare_late(reverse, prior, forward):
    chronology, old_probe, reconstruction, final = reverse
    assert chronology["stage"] == "authenticated_and_chronology_checked"
    assert chronology["cut"] == final["cut"] == forward["cut"] == prior["cut_before"] == 47956
    assert chronology["bank"] == forward["bank"] and len(chronology["bank"]) == 644
    assert set(chronology["bank"]) & set(map(int, RECIPIENTS)) == {873, 878}
    assert old_probe["stage"] == "prior_probe_inconclusive"
    assert old_probe["edited_bank_nonzero_count"] == prior["nonzero_edited_bank_count"] == 284
    assert prior["first_outward_by_recipient"]["878"] == 47956
    assert min(prior["first_outward_by_recipient"].values()) == 47956
    assert reconstruction == {"stage": "full_bank_rows_reconstructed", "count": 644}
    assert final["status"] == "FULL_FIXED_BANK_EXCLUDED"
    assert forward["status"] == "PASS_EXACT_FULL_EDITED_BANK_SEPARATOR"
    assert final["probe"] == forward["probe"] and len(final["probe"]) == 20
    assert final["old_source_response"] == forward["old_source_response"] == "-2"
    assert final["edited_bank_size"] == forward["bank_size"] == 644
    assert final["edited_bank_nonzero_count"] == forward["edited_bank_nonzero_count_on_probe"] == 0
    assert forward["old_bank_nonzero_count_on_probe"] == 2 and forward["guards_each"] == 73
    assert forward["edited_minus_old"] == dict.fromkeys(RECIPIENTS, "-2")
    assert final["case_count"] == forward["case_count"] == 1
    assert final["cap_seconds"] == forward["runner_cap_seconds"] == 30
    same_bytes((RECEIPTS / "LATE-PROBE.json").read_bytes(), forward["witness_sha256"])


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
    early, early_forward, late, prior, late_forward = (reproduce(spec) for spec in RUNNERS)
    compare_early(early, early_forward)
    compare_late(late, prior, late_forward)
    capped = read_output("receipt.jsonl", (RECEIPTS / "LATE-CAPPED-PROVENANCE.jsonl").read_bytes())
    assert capped == late[:-1]
    rejects(lambda: read_json('{"x":0,"x":1}'))
    rejects(lambda: same_bytes(b"mutated", pins["inputs/7481-WORD.json.gz"]))
    rejects(lambda: compare_late(late, prior, dict(late_forward, edited_bank_nonzero_count_on_probe=1)))
    print("PASS_OWNED1551_FANOUT_BANKS: two exact cuts, 644 rows, 20-coordinate separator")


if __name__ == "__main__":
    main()
