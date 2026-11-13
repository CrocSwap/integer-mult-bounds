"""Verify one R261 chart-3 source-bank separator by literal forward replay."""
import argparse
from fractions import Fraction as F
import gzip
from hashlib import sha256
import json
from pathlib import Path
from signal import alarm
from time import perf_counter

ARCHIVE = "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9"
NATIVE = "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
CASE = "7481:1348:pre34566:chart3:old1513@34527"
CUT, SOURCE_CLOCK = 34566, 34527
CARRIER, SOURCE = 1348, 1513


def forward(word, probe):
    values = probe.copy()
    active = dict(enumerate(word["initial"]))
    old_u, copies = None, 0
    for clock, (op, dest, *args) in enumerate(word["program"][:CUT]):
        if clock == SOURCE_CLOCK:
            assert active[SOURCE] == 243
            old_u = values.get(SOURCE, 0)
        if op == "MOVE":
            assert active[dest] == args[0] and args[2] == (dest >= word["public"])
            active[dest] = args[1]
            continue
        if op == "INIT":
            assert dest not in active and dest not in values
            active[dest] = args[0]
            continue
        if op == "CLEAR":
            assert active.pop(dest) == args[0]
            values.pop(dest, None)
            continue
        value = values.get(dest, 0)
        if op == "SCALE":
            assert active[dest] == args[1]
            value *= F(args[0])
        else:
            assert op in ("ADD", "COPY")
            src, coefficient, chart = args
            assert active[src] == active[dest] == chart
            if op == "COPY":
                assert not value
                copies += 1
            if src in values:
                value += F(coefficient) * values[src]
        if value:
            values[dest] = value
        else:
            values.pop(dest, None)
    bank = {role: values.get(role, 0) for role, chart in sorted(active.items()) if chart == 3}
    assert CARRIER in bank and old_u is not None
    return bank, old_u, copies


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", required=True, type=Path)
    parser.add_argument("--solver-receipt", required=True, type=Path)
    parser.add_argument("--method", choices=("reverse", "probe-first"), required=True)
    args = parser.parse_args()
    start = perf_counter()
    alarm(30)
    receipt = args.solver_receipt.read_bytes()
    result = json.loads(receipt)
    assert result["case_id"] == CASE and result["method"] == args.method
    assert result["cap_seconds"] == 30 and result["case_cap"] == 1
    assert result["decision"] == "FIXED_SOURCE_BANK_EXCLUDED"
    archive = args.word.read_bytes()
    assert sha256(archive).hexdigest() == ARCHIVE
    payload = gzip.decompress(archive)
    assert sha256(payload).hexdigest() == NATIVE
    word = json.loads(payload)
    program = word["program"]
    assert program[SOURCE_CLOCK] == ["ADD", 1518, SOURCE, "1", 243]
    assert program[CUT:CUT + 3] == [
        ["MOVE", CARRIER, 3, 431, False], ["ADD", CARRIER, 1137, "4", 431],
        ["ADD", 375, 1507, "-4", 431],
    ]
    assert word["final"][CARRIER] == 431
    probe = {int(role): F(value) for role, value in result["witness"].items()}
    assert probe and all(0 <= role < word["public"] for role in probe)
    bank, old_u, copies = forward(word, probe)
    assert list(bank) == result["bank"]
    assert not any(bank.values())
    assert old_u and old_u == F(result["old_u_response"])
    control_bank, control_u, control_copies = forward(word, {})
    assert not any(control_bank.values()) and control_u == 0
    assert control_copies == copies and list(control_bank) == list(bank)
    print(json.dumps({
        "status": "PASS_INDEPENDENT_EXACT_SOURCE_SEPARATOR",
        "case_id": CASE, "method": args.method,
        "case_count": 1, "runner_cap_seconds": 30,
        "native_sha256": NATIVE, "solver_receipt_sha256": sha256(receipt).hexdigest(),
        "source_cut_before": CUT, "provider_read_before": SOURCE_CLOCK,
        "probe": probe, "full_source_bank": bank, "old_u_response": old_u,
        "copy_guards_checked_per_probe": copies,
        "zero_probe_control_old_u_response": control_u,
        "seconds": perf_counter() - start,
    }, default=str, sort_keys=True, indent=2))
    alarm(0)


if __name__ == "__main__":
    main()
