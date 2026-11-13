"""Replay the owned1537 four-return correction gate by exact forward substitution."""
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
OWNER, TARGET, ADVANCED, OUT = 1537, 1004, 1397, 830
DONORS = (813, 1162, 1448, ADVANCED)
SOURCE, OMIT, RETIRE, CUT, LATE, OUT_CLOCK = 41491, 41492, 41495, 49170, 51411, 54998
CASE = "owned1537-four-returns-pre49170"
CAP_SECONDS = 30


def emit(**record):
    print(dumps(record, sort_keys=True, default=str), flush=True)


def unique_pairs(pairs):
    result = {}
    for name, value in pairs:
        assert name not in result, f"Duplicate JSON key {name}"
        result[name] = value
    return result


def span(basis):
    out = {0}
    for vector in basis:
        assert vector not in out
        out |= {vector ^ old for old in out}
    return out


def contacts(tape, role, start, stop):
    return [
        i for i in range(start, stop)
        if role == tape[i][1] or tape[i][0] in ("ADD", "COPY") and role == tape[i][2]
    ]


def check_structure(word):
    tape = word["program"]
    assert len(tape) == 76475 and word["public"] == len(word["initial"]) == 1501
    source, middle, terminal = (span(word["frames"][c]) for c in (1090, 477, 127))
    assert source < middle < terminal and list(map(len, (source, middle, terminal))) == [16, 256, 512]
    assert tape[SOURCE:OMIT + 1] == [["MOVE", OWNER, 1090, 477, True], ["ADD", TARGET, OWNER, "1", 477]]
    assert tape[RETIRE] == ["CLEAR", OWNER, 477]
    assert tape[CUT] == ["SCALE", TARGET, "4", 127]
    assert tape[OUT_CLOCK] == ["ADD", OUT, TARGET, "1/2", 127]
    assert [tape[i] for i in (46134, 46208, 46676, LATE)] == [
        ["MOVE", r, 1090, 127, False] for r in DONORS
    ]
    assert contacts(tape, OWNER, SOURCE, RETIRE + 1) == [SOURCE, OMIT, RETIRE]
    assert contacts(tape, ADVANCED, 35119, LATE + 2) == [35119, LATE, LATE + 1]
    assert contacts(tape, TARGET, OMIT, OUT_CLOCK + 1) == [
        OMIT, 46133, 46135, 46209, CUT, 49594, 49721, OUT_CLOCK
    ]
    for clock in (46135, 46209, 49594, 49721):
        assert tape[clock][:2] == ["ADD", TARGET] and tape[clock][2] != TARGET
    birth = max(i for i in range(SOURCE) if tape[i][:2] == ["INIT", OWNER])
    return {i: tape[i] for i in contacts(tape, OWNER, birth, RETIRE + 1)}


def add(left, right, scale):
    out = left.copy()
    for j, value in right.items():
        total = out.get(j, 0) + scale * value
        if total:
            out[j] = total
        else:
            out.pop(j, None)
    return out


def replay(word, initial, edited, coefficients=None):
    tape = word["program"]
    active = dict(enumerate(word["initial"]))
    owners = {}
    rows = initial.copy()
    empty = {}
    watch = {}
    counts = {"init": 0, "clear": 0, "copy": 0, "move": 0}
    observed_old = {}
    owned_at_retirement = None
    cut_donors = None
    cut_before = None

    def get(role):
        return rows.get(role, empty)

    def execute(event, clock):
        op, dst, *args = event
        before = get(dst)
        if op == "MOVE":
            src, dest, flag = args
            assert src != dest and active[dst] == src and flag == (dst in owners) == (dst >= word["public"])
            active[dst] = dest
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
            result = add({}, before, Q(weight))
        else:
            assert op in ("ADD", "COPY")
            source, weight, chart = args
            assert dst != source and active[dst] == active[source] == chart
            if op == "COPY":
                assert not before
                counts["copy"] += 1
            result = add(before, get(source), Q(weight))
            if source == OWNER:
                observed_old[clock] = (dst, before, get(source), result)
        if result:
            rows[dst] = result
        else:
            rows.pop(dst, None)

    for clock, event in enumerate(tape[:OUT_CLOCK + 1]):
        if clock == SOURCE:
            assert active[OWNER] == 1090 and OWNER in owners
            watch["target"] = get(OWNER)
            watch["owner_birth"] = owners[OWNER]
        if clock == RETIRE:
            watch["retired_value"] = get(OWNER)
            owned_at_retirement = owners.copy()
        if edited:
            if clock in (SOURCE, OMIT, LATE):
                if clock == LATE:
                    assert active[ADVANCED] == 127
                    watch["late_advanced"] = get(ADVANCED)
                continue
            if clock == RETIRE:
                event = ["CLEAR", OWNER, 1090]
            if clock == CUT:
                assert active[ADVANCED] == 1090
                execute(tape[LATE], LATE)
        if clock == CUT:
            assert OWNER not in active and OWNER not in owners and active[TARGET] == 127
            assert [active[role] for role in DONORS] == [127, 127, 127, 127 if edited else 1090]
            cut_donors = {r: get(r) for r in DONORS}
            cut_before = get(TARGET)
            if coefficients is not None:
                assert edited
                for donor, weight in coefficients.items():
                    execute(["ADD", TARGET, donor, weight, 127], CUT)
            watch["before_scale"] = get(TARGET)
        if clock == LATE and not edited:
            assert active[ADVANCED] == 1090
            watch["late_advanced"] = get(ADVANCED)
        if clock == OUT_CLOCK:
            watch["first_before"] = get(OUT)
            watch["first_donor"] = get(TARGET)
        execute(event, clock)
        if clock == CUT:
            watch["after_scale"] = get(TARGET)
        if clock == LATE + 1:
            watch["late_1397_receiver"] = get(787)
        if clock == OUT_CLOCK:
            watch["first_after"] = get(OUT)
    return watch, cut_donors, cut_before, counts, observed_old, owned_at_retirement


def checked_prefixes(word, initial, coefficients=None):
    old, old_donors, old_before, old_counts, old_reads, old_retire = replay(word, initial, False)
    edit, new_donors, edit_before, edit_counts, edit_reads, edit_retire = replay(word, initial, True, coefficients)
    target = old["target"]
    assert target == edit["target"] == old["retired_value"] == edit["retired_value"]
    assert old["owner_birth"] == edit["owner_birth"] == old_retire[OWNER] == edit_retire[OWNER]
    assert old_retire == edit_retire
    assert {i: v for i, v in old_reads.items() if i != OMIT} == edit_reads
    assert old_donors == new_donors
    assert old["late_advanced"] == edit["late_advanced"] == new_donors[ADVANCED]
    assert old["late_1397_receiver"] == edit["late_1397_receiver"]
    assert old_counts["move"] == edit_counts["move"] + 1
    assert all(old_counts[k] == edit_counts[k] for k in ("init", "clear", "copy"))
    assert old_before == add(edit_before, target, Q(1))
    assert old["first_before"] == edit["first_before"]
    if coefficients is None:
        assert old["before_scale"] == add(edit["before_scale"], target, Q(1))
        assert old["after_scale"] == add(edit["after_scale"], target, Q(4))
        assert old["first_donor"] == add(edit["first_donor"], target, Q(4))
        assert old["first_after"] == add(edit["first_after"], target, Q(2))
    else:
        assert all(old[k] == edit[k] for k in ("before_scale", "after_scale", "first_donor", "first_after"))
    return old, edit, old_donors, old_counts, edit_counts


def scalar(row):
    assert set(row) <= {0}
    return row.get(0, Q(0))


def rationals(values):
    result = {int(j): Q(value) for j, value in values.items()}
    assert len(result) == len(values)
    return result


def check_separator(word, lead):
    probe = rationals(lead["probe"])
    assert probe and all(0 <= i < word["public"] and v for i, v in probe.items())
    old, edit, donors, old_counts, edit_counts = checked_prefixes(word, {r: {0: v} for r, v in probe.items()})
    assert scalar(old["target"]) == 1 and not any(donors.values())
    return {
        "status": "PASS_INDEPENDENT_NAMED_FOUR_RETURNS_SEPARATOR", "probe": probe,
        "target": 1, "donor_responses": {r: scalar(v) for r, v in donors.items()},
        "old_before_scale": scalar(old["before_scale"]), "edited_before_scale": scalar(edit["before_scale"]),
        "old_after_scale": scalar(old["after_scale"]), "edited_after_scale": scalar(edit["after_scale"]),
        "old_first_outward_after": scalar(old["first_after"]), "edited_first_outward_after": scalar(edit["first_after"]),
        "old_guards": old_counts, "edited_guards": edit_counts,
    }


def check_support(word, lead):
    coefficients = rationals(lead["coefficients"])
    assert coefficients.keys() <= set(DONORS)
    initial = {r: {r: Q(1)} for r in range(word["public"])}
    old, _edit, donors, old_counts, edit_counts = checked_prefixes(word, initial, coefficients)
    recovered = {}
    for role, weight in coefficients.items():
        recovered = add(recovered, donors[role], weight)
    assert recovered == old["target"]
    return {
        "status": "PASS_INDEPENDENT_RATIONAL_SUPPORT", "coefficients": coefficients,
        "basis_dimension": word["public"], "target_support_size": len(recovered),
        "old_guards": old_counts, "edited_guards": edit_counts,
    }


def main():
    assert __debug__ and version_info[:2] == (3, 12)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("replay_root", type=Path)
    parser.add_argument("lead_receipt", type=Path)
    parser.add_argument("lead_sha256")
    args = parser.parse_args()
    started = perf_counter()

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
    assert lead["case"] == CASE and lead["cut"] == CUT and tuple(lead["donors"]) == DONORS
    assert lead["tested"] == 1 and lead["unresolved"] == []
    if lead["status"] == "EXACT_NAMED_FOUR_RETURNS_EXCLUSION":
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
