"""Replay the complete price and two independently derived stage-17 certificates."""
import argparse
import json
import subprocess
import sys
import tempfile
from fractions import Fraction
from hashlib import sha1, sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NATIVE_HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER_HEAD = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
REVERSE_SHA = "389851b30c3dd04c314b9f5751b5c7cd7b65448cd1e00e706c42559c8f96abae"
SCRIPTS = ("price.py", "stage17.py", "reverse.py", "reverse_initial.py", "pair_gate.py")


def unique(pairs):
    decoded = dict(pairs)
    if len(decoded) != len(pairs):
        raise ValueError("duplicate JSON key")
    return decoded


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique)


def source(name):
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != name:
        raise ValueError(f"invalid package path {name}")
    return (ROOT / path).read_bytes()


def digest(raw):
    return sha256(raw).hexdigest()


def dependencies():
    pins = decode(source("LOCAL-PINS.json"))
    for name, expected in pins.items():
        if digest(source(name)) != expected:
            raise ValueError(f"changed package dependency {name}")
    prov = decode(source("PROVENANCE.json"))
    for name, entry in prov["files"].items():
        raw = source(name)
        assert digest(raw) == entry["sha256"]
        assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == entry["git_blob"]
    for name, entry in prov["derived_inputs"].items():
        assert digest(source(name)) == decode(source(entry["receipt"]))[entry["key"]]
    admitted = decode(source("inputs/ADMITTED.json"))
    assert admitted["head"] == NATIVE_HEAD and admitted["caller"] == CALLER_HEAD
    assert admitted["caller_sha256"] == digest(source("inputs/CALLER.json"))
    assert admitted["exit"] == 0 and admitted["kappa"] == "0.00364665195644"
    assert set(admitted["stages"]) == {"native", "early", "caller", "frontier"}


def write(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def call(script, *args, timeout=22, expected_failure=None):
    command = [sys.executable, "-I", "-B", str(script), *map(str, args)]
    result = subprocess.run(command, capture_output=True, timeout=timeout)
    if expected_failure is None:
        if result.returncode:
            sys.stderr.write(result.stderr.decode(errors="replace"))
        result.check_returncode()
    else:
        assert result.returncode != 0 and not result.stdout
        assert expected_failure in result.stderr
    return result.stdout


def replay(tmp, out):
    dependencies()
    for name in SCRIPTS:
        write(tmp / name, source("engines/" + name))
    for name in ("CALLER.json", "R92-PRICE.json", "pricing.py"):
        write(tmp / "inputs" / name, source("inputs/" + name))
    caller = tmp / "inputs/CALLER.json"
    records = {}

    def record(name, script, *args, timeout=22):
        raw = call(tmp / script, *args, timeout=timeout)
        assert raw == source("receipts/" + name), f"changed receipt {name}"
        write(tmp / name, raw)
        records[name] = raw
        return decode(raw)

    price = record("PRICE.json", "price.py")
    old = price["price"]["old_crossing_upper"]
    assert price["paid_delta"] == {} and price["target_delta"] == {"9":-8,"17":8,"129":8,"137":-8}
    assert (price["paid_positions"], price["productive_positions"], price["rank_surplus"]) == (110519, 22461, 1424)
    assert 0 < Fraction(old["one_edit_gross"][0]) <= Fraction(old["one_edit_gross"][1]) < Fraction("0.537159504482460")
    assert Fraction(old["with_one_extra_paid_rank_one"][1]) < 0
    assert Fraction(old["stage17_relaxed_two_slot_gross_upper"]) < Fraction("1.074319008964920")

    forward = record("FORWARD.json", "stage17.py", caller)
    reverse = record("REVERSE.json", "reverse.py", "--caller", caller)
    assert [r["rank_two_minor_of_required"]["determinant"] for r in forward["cases"]] == ["3","-1"]
    assert [r["required_rank"] for r in reverse["cases"]] == [3,3]
    assert forward["unresolved"] == reverse["survivors"] == []
    pair = record("PAIR.json", "pair_gate.py", tmp / "FORWARD.json", tmp / "REVERSE.json", REVERSE_SHA, caller, timeout=12)
    assert pair["source_receipts_agree_on_all_slot_entries"]
    assert (pair["one_factor_endpoint_count"], pair["two_factor_distinct_endpoint_count"],
            pair["two_factor_labelled_bijection_count"]) == (16,36,72)
    assert pair["unresolved"] == [] and pair["max_realized_raw_saving"] == "0"

    # Preserve the original baseline failure from differentiating untouched J rows.
    call(tmp / "reverse_initial.py", "--caller", caller, expected_failure=b"assert observed == original")
    corrupted = tmp / "changed-caller.json"
    write(corrupted, caller.read_bytes()+b" ")
    call(tmp / "reverse.py", "--caller", corrupted, expected_failure=b"changed caller bytes")

    if out:
        for name, data in records.items():
            write(out / name, data)
    print(json.dumps({"deterministic_receipts":len(records), "one_factor_endpoints":16,
                      "two_factor_endpoints":36, "labelled_two_factor_assignments":72,
                      "unresolved":0, "expected_failures_rejected":2, "kappa_delta":"0"},
                     sort_keys=True))
    print("PASS_P104_STAGE17_BODY_TRANSFER_BOUND")


def main():
    if sys.implementation.name != "cpython" or sys.version_info[:2] != (3,12) or not __debug__:
        raise SystemExit("CPython 3.12 with assertions is required")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="p104-stage17-") as tmp:
        replay(Path(tmp), args.out)


if __name__ == "__main__":
    main()
