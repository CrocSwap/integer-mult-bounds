"""Independently replay a #7481 owned1502 fixed-late-bank separator."""
import argparse
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import perf_counter

PINS = {
    "7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
}
NATIVE = "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
OWNER, OBSERVER, RECEIVER = 1502, 1489, 152
FUSE, OMIT, SECOND = 33140, 33141, 33142
LOWER_READS = {33143: 629, 33145: 732}
LATE, CHART = 43317, 905
CAP_SECONDS = 30


def emit(**record):
    print(dumps(record, default=str, sort_keys=True), flush=True)


def span(basis):
    out = {0}
    for vector in basis:
        out |= {vector ^ old for old in out}
    return out


def touches(event, role):
    stop = 3 if event[0] in ("ADD", "COPY") else 2
    return role in event[1:stop]


def check_structure(word):
    tape = word["program"]
    assert len(tape) == 76475 and len(word["initial"]) == word["public"] == 1501
    low, mid, high = [span(word["frames"][chart]) for chart in (117, 534, 541)]
    assert low < mid < high and len(high) == 2 * len(mid) == 4 * len(low)
    assert tape[FUSE:SECOND + 1] == [
        ["MOVE", OWNER, 541, 534, True],
        ["ADD", OBSERVER, OWNER, "4", 534],
        ["MOVE", OWNER, 534, 117, True],
    ]
    for clock, destination in LOWER_READS.items():
        op, dst, donor, weight, chart = tape[clock]
        assert (op, dst, donor, chart) == ("ADD", destination, OWNER, 117) and Q(weight)
    assert tape[33149] == ["MOVE", OWNER, 117, 594, True]
    lower_after = span(word["frames"][594])
    assert lower_after < low and len(low) == 16 * len(lower_after)
    assert tape[LATE - 2:LATE] == [
        ["MOVE", RECEIVER, 1057, CHART, False],
        ["MOVE", OBSERVER, 534, CHART, False],
    ]
    assert tape[LATE][:3] == ["ADD", RECEIVER, OBSERVER]
    assert Q(tape[LATE][3]) and tape[LATE][-1] == CHART

    # Track syntactic influence independently of probe arithmetic. This overapproximates
    # dependencies, so no new tainted destination means no transitive mutation.
    tainted = {OBSERVER}
    taint_contacts = {}
    for clock in range(OMIT + 1, LATE):
        op, dst, *args = tape[clock]
        if any(touches(tape[clock], r) for r in tainted):
            taint_contacts[clock] = tape[clock]
        if op in ("INIT", "CLEAR"):
            tainted.discard(dst)
        elif op in ("ADD", "COPY") and args[0] in tainted:
            tainted.add(dst)
    assert tainted == {OBSERVER} and taint_contacts == {LATE - 1: tape[LATE - 1]}

    birth = max(i for i in range(FUSE) if tape[i][:2] == ["INIT", OWNER])
    death = min(i for i in range(SECOND + 1, len(tape)) if tape[i][:2] == ["CLEAR", OWNER])
    owner_contacts = {
        clock: tape[clock] for clock in range(birth, death + 1)
        if touches(tape[clock], OWNER)
    }
    assert list(owner_contacts)[:1] == [birth] and list(owner_contacts)[-1:] == [death]
    assert not any(e[0] in ("INIT", "CLEAR") for i, e in owner_contacts.items() if birth < i < death)
    return taint_contacts, owner_contacts


def replay(word, probe, edited):
    tape = word["program"]
    active = dict(enumerate(word["initial"]))
    owners = {}
    value = probe.copy()
    reads = {}
    guards = {"init": 0, "copy": 0, "move": 0}
    history = None
    bank = None
    for clock, (op, dst, *args) in enumerate(tape[:LATE + 1]):
        if clock == OMIT:
            history = value.get(OWNER, Q(0))
        if clock == LATE:
            bank = {r: value.get(r, Q(0)) for r, chart in sorted(active.items()) if chart == CHART}
            receiver_before = value.get(RECEIVER, Q(0))
        if edited:
            if clock in (OMIT, SECOND):
                continue
            if clock == FUSE:
                args = [541, 117, True]
        old = value.get(dst, Q(0))
        if op == "MOVE":
            source, target, owned = args
            assert active[dst] == source and owned == (dst in owners) == (dst >= word["public"])
            active[dst] = target
            guards["move"] += 1
            continue
        if op == "INIT":
            assert dst >= word["public"] and dst not in owners and dst not in active and not old
            owners[dst] = clock
            active[dst] = args[0]
            guards["init"] += 1
            continue
        if op == "CLEAR":
            assert dst in owners and active.pop(dst) == args[0]
            del owners[dst]
            value.pop(dst, None)
            continue
        if op == "SCALE":
            weight, chart = args
            assert active[dst] == chart
            new = Q(weight) * old
        else:
            assert op in ("ADD", "COPY")
            donor, weight, chart = args
            assert active[dst] == active[donor] == chart
            if op == "COPY":
                assert not old
                guards["copy"] += 1
            source = value.get(donor, Q(0))
            new = old + Q(weight) * source
            if clock in LOWER_READS:
                reads[clock] = {"receiver": dst, "before": old, "donor": source, "after": new}
        if new:
            value[dst] = new
        else:
            value.pop(dst, None)
    return {
        "historical_response": history, "bank": bank, "lower_reads": reads,
        "receiver_before": receiver_before, "receiver_after": value.get(RECEIVER, Q(0)),
        "ownership_at_late_cut": owners, "guards": guards,
    }


def rationals(values):
    return {int(r): Q(v) for r, v in values.items()}


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_root", type=Path)
    parser.add_argument("lead_receipt", type=Path)
    parser.add_argument("lead_sha256")
    args = parser.parse_args()
    started = perf_counter()

    def on_cap(_signal, _frame):
        emit(status="INDEPENDENT_CAP", unresolved=["owned1502/chart905/43317"],
             seconds=perf_counter() - started)
        raise SystemExit(124)

    signal(SIGALRM, on_cap)
    alarm(CAP_SECONDS)
    raw = {name: (args.input_root / name).read_bytes() for name in PINS}
    assert {name: sha256(data).hexdigest() for name, data in raw.items()} == PINS
    canonical = decompress(raw["7481-WORD.json.gz"])
    assert sha256(canonical).hexdigest() == NATIVE
    app = loads(raw["7481-APPLICATION.json"])
    caller = loads(raw["7113-CALLER.json"])
    assert app["caller_head"] == CALLER and app["caller_sha256"] == PINS["7113-CALLER.json"]
    assert app["candidate_canonical_sha256"] == NATIVE
    assert caller["stages"] == sum(event[0] == "J" for event in caller["events"]) == 17
    word = loads(canonical)
    taint_contacts, owner_contacts = check_structure(word)

    raw_lead = args.lead_receipt.read_bytes()
    assert sha256(raw_lead).hexdigest() == args.lead_sha256
    lead = loads(raw_lead)
    assert lead["status"] == "EXACT_FIXED_LATE_BANK_EXCLUSION"
    probe = rationals(lead["probe"])
    assert probe and len(probe) == len(lead["probe"])
    assert all(0 <= r < word["public"] and v for r, v in probe.items())

    old = replay(word, probe, edited=False)
    edited = replay(word, probe, edited=True)
    assert list(old["bank"]) == list(edited["bank"]) == lead["bank"]
    assert old["bank"] == rationals(lead["old_bank_responses"])
    assert edited["bank"] == rationals(lead["edited_bank_responses"])
    u = old["historical_response"]
    assert u == edited["historical_response"] == Q(lead["historical_response"]) == 1
    assert not any(edited["bank"].values())
    assert {r: v for r, v in old["bank"].items() if v} == {OBSERVER: 4 * u}
    assert old["lower_reads"] == edited["lower_reads"]
    assert old["ownership_at_late_cut"] == edited["ownership_at_late_cut"]
    assert old["guards"]["move"] == edited["guards"]["move"] + 1
    assert all(old["guards"][op] == edited["guards"][op] for op in ("init", "copy"))
    assert old["receiver_before"] == edited["receiver_before"] == 0
    old_receiver = old["receiver_after"]
    assert old_receiver == 4 * u * Q(word["program"][LATE][3]) != 0
    assert edited["receiver_after"] == 0

    emit(
        status="PASS_INDEPENDENT_FIXED_LATE_BANK_SEPARATOR",
        probe=probe, historical_response=u,
        old_bank=old["bank"], edited_bank=edited["bank"], lower_reads=old["lower_reads"],
        receiver_after_old=old_receiver, receiver_after_unrepaired=edited["receiver_after"],
        old_guards=old["guards"], edited_guards=edited["guards"],
        taint_contacts_before_outward=taint_contacts, owner_lifetime_contacts=owner_contacts,
        input_pins=PINS, native_sha256=NATIVE, caller_head=CALLER,
        lead_sha256=args.lead_sha256, runner_cap_seconds=CAP_SECONDS,
        seconds=perf_counter() - started,
    )
    alarm(0)


if __name__ == "__main__":
    main()
