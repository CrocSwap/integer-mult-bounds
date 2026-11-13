"""Forward-check the #7481 owned1551 named-carrier deferral exclusion."""
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
SOURCE, CUT = 45636, 46149
BANK = (862, 988, 991, 1499)
RECIPIENTS = (
    (817, 45639, 48748), (790, 45641, 47990), (873, 45643, 46147),
    (1497, 45646, 51351), (878, 45649, 47955), (833, 45651, 48877),
)
FANOUT = {write for _, write, _ in RECIPIENTS}


def mentions(event, role):
    return event[1] == role or (event[0] in ("ADD", "COPY") and event[2] == role)


def forward(word, probe, omitted=()):
    values = probe.copy()
    active = dict(enumerate(word["initial"]))
    target, copies = None, 0
    for clock, (op, dest, *args) in enumerate(word["program"][:CUT]):
        if clock == SOURCE:
            assert active[862] == 1091
            target = values.get(862, 0)
        if clock in omitted:
            assert op == "ADD"
            continue
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
    assert all(active[role] == 127 for role in (*BANK, 873))
    assert target is not None
    return values, target, copies


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", required=True, type=Path)
    parser.add_argument("--probe", required=True, type=Path)
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
    assert tape[45638] == ["MOVE", 1551, 1091, 267, True]
    assert tape[45652] == ["CLEAR", 1551, 267]
    assert tape[46148] == ["MOVE", 862, 1091, 127, False]
    first_touches = {}
    for role, write, move in RECIPIENTS:
        assert tape[write] == ["ADD", role, 1551, "1", 267]
        assert tape[move] == ["MOVE", role, 267, 127, False]
        assert not any(mentions(event, role) for event in tape[write+1:move])
        first_touches[role] = next((clock, event) for clock, event in enumerate(tape[move+1:], move+1)
                                   if mentions(event, role))
    assert min(clock for clock, _ in first_touches.values()) == CUT
    assert first_touches[873][0] == CUT
    # Only recipient rows differ up to the first return, so no provider can
    # have inherited a perturbation in the tested deletion prefix.
    assert not set(BANK) & {role for role, _, _ in RECIPIENTS}
    probe = {int(role): F(value) for role, value in json.loads(args.probe.read_text()).items()}
    assert probe and all(0 <= role < word["public"] for role in probe)
    old, target, copies = forward(word, probe)
    modified, target_control, control_copies = forward(word, probe, omitted=FANOUT)
    assert target and target_control == target
    assert copies == control_copies
    bank = {role: old.get(role, 0) for role in BANK}
    assert not any(bank.values()) and all(modified.get(role, 0) == 0 for role in BANK)
    assert modified.get(873, 0) == 0
    delta = {role: modified.get(role, 0) - old.get(role, 0)
             for role in old.keys() | modified.keys()}
    delta = {role: value for role, value in delta.items() if value}
    assert delta == {role: target for role, _, _ in RECIPIENTS}
    print(json.dumps({
        "status": "PASS_EXACT_NAMED_CARRIER_SEPARATOR",
        "native_sha256": NATIVE, "cut_before": CUT, "target_before": SOURCE,
        "probe": probe, "old_source_862": target, "named_bank": bank,
        "edited_first_recipient_873": modified.get(873, 0),
        "recipient_next_move_and_first_post_move_contact": [
            [role, write, move, *first_touches[role]] for role, write, move in RECIPIENTS
        ],
        "control_omit_six_old_updates": {"modified_minus_old": delta,
                                         "first_observer_role": 873,
                                         "first_observer_delta": delta[873]},
        "copy_guards_checked_per_probe": copies,
        "runner_cap_seconds": 30, "cases_completed": 1, "seconds": perf_counter() - start,
    }, sort_keys=True, indent=2, default=str))
    alarm(0)


if __name__ == "__main__":
    main()
