"""Independently replay the fixed public720 lower-bank gate."""
import argparse
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import version_info
from time import perf_counter

PINS = {
    "inputs/7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "inputs/7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "inputs/7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
}
NATIVE = "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
CARRIER, SNAPSHOT, OWNER, LO, HI = 720, 92, 1511, 265, 1091
BIRTH, CAPTURE, CUT, TERMINAL, OMIT, RETIRE = 33128, 33129, 41307, 45363, 45364, 45365
LAST_OUT, OBSERVER_OUT = 40829, 40833
BANK = [236, 454, CARRIER, 1000, 1208, 1347]
CASE = "terminal720-chart265-pre41307"
CAP_SECONDS = 30


def unique_pairs(pairs):
    result = {}
    for name, value in pairs:
        assert name not in result, f"Duplicate JSON key {name}"
        result[name] = value
    return result


def span(basis):
    result = {0}
    for generator in basis:
        assert generator not in result
        result |= {x ^ generator for x in result}
    return result


def contacts(tape, role, start, stop):
    return [
        i for i in range(start, stop)
        if role == tape[i][1] or tape[i][0] in ("ADD", "COPY") and role == tape[i][2]
    ]


def check_structure(word):
    tape = word["program"]
    assert len(tape) == 76475 and len(word["initial"]) == word["public"] == 1501
    protected = set(word["live"]) | {r + 112 for r in word["live"]}
    protected |= set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
    assert len(protected) == 400 and CARRIER not in protected
    assert word["initial"][CARRIER] == 3 and word["final"][CARRIER] == HI
    start, lower, upper = (span(word["frames"][c]) for c in (3, LO, HI))
    assert start < lower < upper and list(map(len, (start, lower, upper))) == [1, 8, 16]
    assert tape[32738] == ["ADD", 236, SNAPSHOT, "1", LO]
    assert tape[32750] == ["MOVE", SNAPSHOT, LO, HI, False]
    assert tape[32940] == ["ADD", SNAPSHOT, 1529, "1", HI]
    assert tape[BIRTH:CAPTURE + 1] == [["INIT", OWNER, HI], ["ADD", OWNER, SNAPSHOT, "1", HI]]
    assert tape[LAST_OUT] == ["ADD", 236, CARRIER, "2", LO]
    assert tape[OBSERVER_OUT] == ["ADD", 454, 236, "1", LO]
    assert tape[CUT] == ["MOVE", 236, LO, 751, False]
    assert tape[TERMINAL:RETIRE + 1] == [
        ["MOVE", CARRIER, LO, HI, False],
        ["ADD", CARRIER, OWNER, "-1/4", HI],
        ["CLEAR", OWNER, HI],
    ]
    assert LAST_OUT < OBSERVER_OUT < CUT < TERMINAL
    assert contacts(tape, CARRIER, LAST_OUT, len(tape)) == [LAST_OUT, TERMINAL, OMIT]
    lifetime = contacts(tape, OWNER, BIRTH, RETIRE + 1)
    assert lifetime == [BIRTH, CAPTURE, 33131, 45348, OMIT, RETIRE]
    assert all(tape[i][0] == "ADD" and tape[i][2] == OWNER for i in lifetime[2:-1])
    return {i: tape[i] for i in lifetime}


def add(left, right, scale):
    result = left.copy()
    for k, value in right.items():
        v = result.get(k, 0) + scale * value
        if v:
            result[k] = v
        else:
            result.pop(k, None)
    return result


def replay(word, initial, edited=False, coefficients=None):
    active = dict(enumerate(word["initial"]))
    owners = {}
    rows = initial.copy()
    empty = {}
    watch = {}
    observer_reads = {}
    owner_reads = {}
    counts = {"init": 0, "clear": 0, "copy": 0, "move": 0}

    def get(role):
        return rows.get(role, empty)

    def execute(event, clock):
        op, dst, *args = event
        before = get(dst)
        if op == "MOVE":
            source, destination, owned = args
            assert source != destination and active[dst] == source
            assert owned == (dst in owners) == (dst >= word["public"])
            active[dst] = destination
            counts["move"] += 1
            return
        if op == "INIT":
            assert dst >= word["public"] and dst not in active and dst not in owners and not before
            owners[dst] = clock
            active[dst] = args[0]
            counts["init"] += 1
            return
        if op == "CLEAR":
            assert dst in owners and active.pop(dst) == args[0]
            del owners[dst]
            rows.pop(dst, None)
            counts["clear"] += 1
            return
        if op == "SCALE":
            weight, chart = args
            assert active[dst] == chart
            new = add({}, before, Q(weight))
        else:
            assert op in ("ADD", "COPY")
            source, weight, chart = args
            assert dst != source and active[dst] == active[source] == chart
            if op == "COPY":
                assert not before
                counts["copy"] += 1
            donor = get(source)
            new = add(before, donor, Q(weight))
            if clock in (32738, LAST_OUT, OBSERVER_OUT):
                observer_reads[clock] = (before, donor, new)
            if source == OWNER:
                assert owners[source] == BIRTH
                owner_reads[clock] = (dst, before, donor, new)
        if new:
            rows[dst] = new
        else:
            rows.pop(dst, None)

    for clock, event in enumerate(word["program"]):
        if clock == 32750:
            assert active[SNAPSHOT] == LO
            watch["earlier_92"] = get(SNAPSHOT)
        if clock == CAPTURE:
            assert active[OWNER] == active[SNAPSHOT] == HI and owners[OWNER] == BIRTH and not get(OWNER)
            watch["snapshot_92"] = get(SNAPSHOT)
        if clock == CUT:
            bank = {r: get(r) for r, chart in sorted(active.items()) if chart == LO}
            assert list(bank) == BANK and all(r not in owners for r in BANK)
            watch["pre_repair_720"] = get(CARRIER)
            if coefficients is not None:
                assert edited
                self_scale = 1 - coefficients.get(CARRIER, 0) / Q(4)
                assert self_scale
                if self_scale != 1:
                    execute(["SCALE", CARRIER, self_scale, LO], CUT)
                for role, weight in coefficients.items():
                    if role != CARRIER and weight:
                        execute(["ADD", CARRIER, role, -weight / Q(4), LO], CUT)
            watch["post_repair_720"] = get(CARRIER)
        if clock == TERMINAL:
            assert active[CARRIER] == LO
            watch["terminal_input_720"] = get(CARRIER)
        if clock == OMIT:
            assert owners[OWNER] == BIRTH and active[OWNER] == HI
            watch["owner_at_final_read"] = get(OWNER)
        if clock == RETIRE:
            assert owners[OWNER] == BIRTH and active[OWNER] == HI
            watch["owner_retired"] = get(OWNER)
        if edited and clock in (TERMINAL, OMIT):
            continue
        execute(event, clock)
    final = word["final"].copy()
    if edited:
        final[CARRIER] = LO
    assert not owners and active == dict(enumerate(final))
    assert watch["terminal_input_720"] == watch["post_repair_720"]
    return rows, bank, watch, observer_reads, owner_reads, counts


def compare(word, initial, coefficients=None):
    old_rows, old_bank, old, old_observers, old_owner, old_counts = replay(word, initial)
    edit_rows, edit_bank, edit, edit_observers, edit_owner, edit_counts = replay(word, initial, True, coefficients)
    assert old_bank == edit_bank
    assert old_observers == edit_observers
    assert {i: value for i, value in old_owner.items() if i != OMIT} == edit_owner
    target = old["snapshot_92"]
    assert target == edit["snapshot_92"] == old["owner_at_final_read"] == edit["owner_at_final_read"]
    assert target == old["owner_retired"] == edit["owner_retired"]
    assert old_observers[32738][1] == old["earlier_92"] == edit["earlier_92"]
    assert old_counts["move"] == edit_counts["move"] + 1
    assert all(old_counts[k] == edit_counts[k] for k in ("init", "clear", "copy"))
    assert {r: row for r, row in old_rows.items() if r != CARRIER} == {
        r: row for r, row in edit_rows.items() if r != CARRIER
    }
    old_final = old_rows.get(CARRIER, {})
    edited_final = edit_rows.get(CARRIER, {})
    assert old_final == add(old["terminal_input_720"], target, Q(-1, 4))
    if coefficients is None:
        assert old_final == add(edited_final, target, Q(-1, 4))
    else:
        assert old_rows == edit_rows
        reproduced = {}
        for role, weight in coefficients.items():
            reproduced = add(reproduced, old_bank[role], weight)
        assert reproduced == target
    return old_bank, old, old_observers, old_owner, old_final, edited_final, old_counts, edit_counts


def scalar(row):
    assert set(row) <= {0}
    return row.get(0, Q(0))


def rational_map(values):
    result = {int(k): Q(v) for k, v in values.items()}
    assert len(result) == len(values)
    return result


def check_separator(word, lead):
    probe = rational_map(lead["probe"])
    assert probe and all(0 <= r < word["public"] and value for r, value in probe.items())
    initial = {r: {0: value} for r, value in probe.items()}
    bank, old, observers, owner_reads, old_final, edited_final, old_counts, edit_counts = compare(word, initial)
    assert not any(bank.values()) and scalar(old["snapshot_92"]) == 1
    assert scalar(old_final) == Q(-1, 4) and not edited_final
    return {
        "status": "PASS_INDEPENDENT_FIXED_LOWER_BANK_SEPARATOR", "probe": probe,
        "lower_bank_responses": {r: scalar(row) for r, row in bank.items()},
        "earlier_92_at_paid_departure": scalar(old["earlier_92"]),
        "captured_92_at_ADD33129": scalar(old["snapshot_92"]),
        "old1511_at_final_read_and_clear": scalar(old["owner_retired"]),
        "old720_final": scalar(old_final), "unrepaired720_final": scalar(edited_final),
        "preserved_observer_reads_before_donor_after": {
            i: [scalar(row) for row in values] for i, values in observers.items()
        },
        "old_owner_reads_destination_before_donor_after": {
            i: [dst, scalar(before), scalar(donor), scalar(after)]
            for i, (dst, before, donor, after) in owner_reads.items()
        },
        "old_guards": old_counts, "edited_guards": edit_counts,
    }


def check_support(word, lead):
    coefficients = rational_map(lead["coefficients"])
    assert coefficients.keys() <= set(BANK)
    assert 1 - coefficients.get(CARRIER, 0) / Q(4) == Q(lead["final_self_coefficient"]) != 0
    initial = {r: {r: Q(1)} for r in range(word["public"])}
    _, _, _, _, _, _, old_counts, edit_counts = compare(word, initial, coefficients)
    return {
        "status": "PASS_INDEPENDENT_RATIONAL_SUPPORT", "coefficients": coefficients,
        "basis_dimension": word["public"], "old_guards": old_counts, "edited_guards": edit_counts,
    }


def main():
    assert __debug__ and version_info[:2] == (3, 12)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("replay_root", type=Path)
    parser.add_argument("lead_receipt", type=Path)
    parser.add_argument("lead_sha256")
    args = parser.parse_args()
    started = perf_counter()

    def emit(**record):
        print(dumps(record, sort_keys=True, default=str), flush=True)

    def on_cap(_signal, _frame):
        emit(status="INDEPENDENT_CAP", unresolved=[CASE], runner_cap_seconds=CAP_SECONDS,
             seconds=perf_counter() - started)
        raise SystemExit(124)

    signal(SIGALRM, on_cap)
    alarm(CAP_SECONDS)
    raw = {name: (args.replay_root / name).read_bytes() for name in PINS}
    assert {name: sha256(data).hexdigest() for name, data in raw.items()} == PINS
    canonical = decompress(raw["inputs/7481-WORD.json.gz"])
    assert sha256(canonical).hexdigest() == NATIVE
    app = loads(raw["inputs/7481-APPLICATION.json"], object_pairs_hook=unique_pairs)
    caller = loads(raw["inputs/7113-CALLER.json"], object_pairs_hook=unique_pairs)
    assert app["caller_head"] == CALLER and app["caller_sha256"] == PINS["inputs/7113-CALLER.json"]
    assert app["candidate_canonical_sha256"] == NATIVE
    assert caller["stages"] == sum(event[0] == "J" for event in caller["events"]) == 17
    word = loads(canonical, object_pairs_hook=unique_pairs)
    lifecycle = check_structure(word)
    raw_lead = args.lead_receipt.read_bytes()
    assert sha256(raw_lead).hexdigest() == args.lead_sha256
    lead = loads(raw_lead, object_pairs_hook=unique_pairs)
    assert lead["case"] == CASE and lead["cut"] == CUT and lead["bank_roles"] == BANK
    assert lead["tested"] == 1 and lead["unresolved"] == []
    if lead["status"] == "EXACT_FIXED_LOWER_BANK_EXCLUSION":
        result = check_separator(word, lead)
    else:
        assert lead["status"] == "EXACT_RATIONAL_SUPPORT"
        result = check_support(word, lead)
    emit(**result, case=CASE, lifecycle=lifecycle, input_pins=PINS, native_sha256=NATIVE,
         caller_head=CALLER, lead_sha256=args.lead_sha256,
         runner_cap_seconds=CAP_SECONDS, seconds=perf_counter() - started)
    alarm(0)


if __name__ == "__main__":
    main()
