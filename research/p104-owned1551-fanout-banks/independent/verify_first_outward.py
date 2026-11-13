"""Independently check a separator or row representation at #7481 ADD47956."""
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
SOURCE, CUT = 45636, 47956
WRITES = {45639: 817, 45641: 790, 45643: 873, 45646: 1497, 45649: 878, 45651: 833}
RECIPIENTS = set(WRITES.values())


def store(values, role, value):
    if value:
        values[role] = value
    else:
        values.pop(role, None)


def forward(word, probe, edited):
    live = dict(enumerate(word["initial"]))
    values = probe.copy()
    target, guards = None, 0
    for clock, (op, dest, *args) in enumerate(word["program"][:CUT]):
        if clock == SOURCE:
            target = values.get(862, 0)
            assert live[862] == 1091
        if edited and clock in WRITES:
            continue
        if op == "MOVE":
            assert live[dest] == args[0] and args[2] == (dest >= word["public"])
            live[dest] = args[1]
        elif op == "INIT":
            assert dest not in live and dest not in values
            live[dest] = args[0]
            guards += 1
        elif op == "CLEAR":
            assert live.pop(dest) == args[0]
            values.pop(dest, None)
        elif op == "SCALE":
            assert live[dest] == args[1]
            if dest in values:
                store(values, dest, values[dest] * F(args[0]))
        else:
            assert op in ("ADD", "COPY")
            src, weight, chart = args
            assert live[dest] == live[src] == chart
            if op == "COPY":
                assert dest not in values
                guards += 1
            if src in values:
                store(values, dest, values.get(dest, 0) + F(weight) * values[src])
    bank = tuple(sorted(role for role, chart in live.items() if chart == 127))
    assert len(bank) == 644 and set(bank) & RECIPIENTS == {873, 878}
    assert target is not None
    return values, target, guards, bank


def pull(tape, row, edited):
    # One aggregate transpose row, independent of the lead's row-by-row basis.
    result = row.copy()
    for clock in range(len(tape) - 1, -1, -1):
        op, dest, *args = tape[clock]
        if dest not in result or (edited and clock in WRITES):
            continue
        coefficient = result[dest]
        if op in ("INIT", "COPY", "CLEAR"):
            del result[dest]
        if op == "SCALE":
            store(result, dest, F(args[0]) * coefficient)
        elif op in ("ADD", "COPY"):
            src, weight, _ = args
            store(result, src, result.get(src, 0) + F(weight) * coefficient)
    return result


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", type=Path, required=True)
    parser.add_argument("--witness", type=Path, required=True)
    args = parser.parse_args()
    start = perf_counter()
    alarm(30)
    archive = args.word.read_bytes()
    assert sha256(archive).hexdigest() == ARCHIVE
    payload = gzip.decompress(archive)
    assert sha256(payload).hexdigest() == NATIVE
    word = json.loads(payload)
    tape = word["program"]
    assert tape[SOURCE] == ["ADD", 1551, 862, "-1", 1091]
    assert tape[CUT - 1:CUT + 1] == [
        ["MOVE", 878, 267, 127, False], ["ADD", 549, 878, "1", 127],
    ]
    observed_writes = set()
    for clock, event in enumerate(tape[min(WRITES):CUT + 1], min(WRITES)):
        op, dest, *parts = event
        if op in ("ADD", "COPY") and parts[0] in observed_writes:
            assert clock == CUT and parts[0] == 878
        if dest in observed_writes:
            assert op == "MOVE" or (clock == 46149 and event == ["ADD", 873, 862, "1", 127])
        if clock in WRITES:
            assert event == ["ADD", WRITES[clock], 1551, "1", 267]
            observed_writes.add(dest)
    assert observed_writes == RECIPIENTS
    input_bytes = args.witness.read_bytes()
    artifact = json.loads(input_bytes)
    assert set(artifact) in ({"probe"}, {"representation"})
    if "probe" in artifact:
        probe = {int(key): F(value) for key, value in artifact["probe"].items()}
        assert probe and all(0 <= role < word["public"] for role in probe)
    else:
        # A nontrivial forward control in the same geometry; full coverage
        # of a representation comes from the exact aggregate transpose.
        probe = {230: F(-1), 547: F(1)}
    edited, u, edited_guards, bank = forward(word, probe, edited=True)
    old, old_u, old_guards, old_bank = forward(word, probe, edited=False)
    assert u == old_u and edited_guards == old_guards and bank == old_bank
    delta = {role: edited.get(role, 0) - old.get(role, 0) for role in edited.keys() | old.keys()}
    delta = {role: value for role, value in delta.items() if value}
    assert delta == ({role: u for role in RECIPIENTS} if u else {})
    if "probe" in artifact:
        assert u and all(not edited.get(role, 0) for role in bank)
        status = "PASS_EXACT_FULL_EDITED_BANK_SEPARATOR"
        terms = None
    else:
        terms = {int(role): F(value) for role, value in artifact["representation"].items()}
        assert terms and set(terms) <= set(bank)
        target = pull(tape[:SOURCE], {862: F(1)}, edited=False)
        represented = pull(tape[:CUT], terms, edited=True)
        assert target and target == represented
        assert sum(weight * edited.get(role, 0) for role, weight in terms.items()) == u
        status = "PASS_EXACT_SUPPORT_RESTORATION_OPEN"
    print(json.dumps({
        "status": status, "case_id": "7481:owned1551:first-outward:pre47956:chart127",
        "native_sha256": NATIVE, "cut": CUT, "source": SOURCE, "bank": bank,
        "bank_size": len(bank), "probe": probe, "old_source_response": u,
        "edited_bank_nonzero_count_on_probe": sum(bool(edited.get(role, 0)) for role in bank),
        "old_bank_nonzero_count_on_probe": sum(bool(old.get(role, 0)) for role in bank),
        "edited_minus_old": delta, "guards_each": edited_guards, "representation": terms,
        "witness_sha256": sha256(input_bytes).hexdigest(), "case_count": 1,
        "runner_cap_seconds": 30, "seconds": perf_counter() - start,
    }, default=str, sort_keys=True, indent=2))
    alarm(0)


if __name__ == "__main__":
    main()
