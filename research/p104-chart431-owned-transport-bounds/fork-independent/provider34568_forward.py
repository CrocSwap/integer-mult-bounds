"""Exact forward verification of one #7481 provider-fork separator."""
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
CUT = 34568
OLD_BANK = (375, 1135, 1137, 1348, 1507, 1518, 1519, 1535)
REMOVED = (1507, 1518, 1519)


def forward(word, probe, suppressed=None):
    active = dict(enumerate(word["initial"]))
    values = probe.copy()
    for clock, (op, dest, *args) in enumerate(word["program"][:CUT]):
        if clock == suppressed:
            assert op == "ADD"
            continue
        if op == "MOVE":
            assert active[dest] == args[0]
            assert args[2] == (dest >= word["public"])
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
            if src in values:
                value += F(coefficient) * values[src]
        if value:
            values[dest] = value
        else:
            values.pop(dest, None)
    bank = tuple(sorted(role for role, chart in active.items() if chart == 431))
    assert bank == OLD_BANK
    return values


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", type=Path, required=True)
    parser.add_argument("--probe", type=Path, required=True)
    args = parser.parse_args()
    start = perf_counter()
    alarm(30)
    archive = args.word.read_bytes()
    assert sha256(archive).hexdigest() == ARCHIVE
    payload = gzip.decompress(archive)
    assert sha256(payload).hexdigest() == NATIVE
    word = json.loads(payload)
    program = word["program"]
    assert program[34526:34533] == [
        ["INIT", 1518, 243], ["ADD", 1518, 1513, "1", 243],
        ["MOVE", 1518, 243, 431, True], ["ADD", 1507, 1518, "1", 431],
        ["SCALE", 1507, "1/4", 431], ["INIT", 1519, 431],
        ["ADD", 1519, 1507, "1", 431],
    ]
    assert program[34566:34569] == [
        ["MOVE", 1348, 3, 431, False], ["ADD", 1348, 1137, "4", 431],
        ["ADD", 375, 1507, "-4", 431],
    ]
    assert program[35443] == ["MOVE", 1519, 431, 600, True]
    assert not any(e[0] in ("ADD", "COPY") and e[2] == 1507
                   and e[1] < word["public"] for e in program[34529:CUT])
    probe = {int(role): F(value) for role, value in json.loads(args.probe.read_text()).items()}
    assert probe and all(0 <= role < word["public"] for role in probe)
    old = forward(word, probe)
    bank = {role: old.get(role, 0) for role in OLD_BANK if role not in REMOVED}
    assert not any(bank.values())
    retained_u = old.get(1518, 0)
    provider = old.get(1507, 0)
    assert retained_u and retained_u == 4 * provider
    assert old.get(1519, 0) == provider
    mutant = forward(word, probe, suppressed=34529)
    assert all(mutant.get(role, 0) == 0 for role in (*bank, 1507, 1519))
    assert mutant.get(1518, 0) == retained_u
    print(json.dumps({
        "status": "PASS_FULL_FIXED_CHART431_BANK_SEPARATOR",
        "native_sha256": NATIVE, "cut_before": CUT, "old_bank": OLD_BANK,
        "surviving_bank": bank, "removed_bank_roles": REMOVED, "probe": probe,
        "old_owned_provider_1507": provider, "old_owned_1518": retained_u,
        "old_owned_1519": old.get(1519, 0), "old_outward_add_contribution": -4 * provider,
        "control_drop_ADD34529": {"old_1507": 0, "old_1519": 0, "unchanged_1518": retained_u},
        "cases_completed": 1, "runner_cap_seconds": 30, "seconds": perf_counter() - start,
    }, default=str, sort_keys=True, indent=2))
    alarm(0)


if __name__ == "__main__":
    main()
