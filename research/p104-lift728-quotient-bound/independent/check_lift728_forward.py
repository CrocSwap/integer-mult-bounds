"""Replay the public728 single-carrier quotient gate by exact forward substitution."""
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
OWNER, CARRIER, TARGET, ADVANCED, OUT = 1537, 728, 1004, 1397, 830
SOURCE, OMIT, RETIRE, CUT, LATE, OUT_CLOCK = 41491, 41492, 41495, 49170, 51411, 54998
CASE = "lift728-owned1537-chart127-pre49170"
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


def touches(event, role):
    return role == event[1] or event[0] in ("ADD", "COPY") and role == event[2]


def contacts(tape, role, start, stop):
    return [i for i in range(start, stop) if touches(tape[i], role)]


def check_structure(word):
    tape = word["program"]
    assert len(tape) == 76475 and word["public"] == len(word["initial"]) == 1501
    assert word["initial"][CARRIER] == 3 and word["final"][CARRIER] == 1090
    hosted = word["hosted"]
    protected = set(word["live"]) | {r + 112 for r in word["live"]} | set(hosted["X2"]) | set(hosted["Y2"])
    assert len(protected) == 400 and CARRIER not in protected
    frames = [span(word["frames"][c]) for c in (3, 1090, 477, 127)]
    assert [len(f) for f in frames] == [1, 16, 256, 512]
    assert all(a < b for a, b in zip(frames, frames[1:]))
    assert tape[30631] == ["ADD", OWNER, CARRIER, "-1/4", 1090]
    assert contacts(tape, CARRIER, 30631, len(tape)) == [30631]
    assert tape[SOURCE:OMIT + 1] == [["MOVE", OWNER, 1090, 477, True], ["ADD", TARGET, OWNER, "1", 477]]
    assert tape[RETIRE] == ["CLEAR", OWNER, 477]
    assert tape[CUT] == ["SCALE", TARGET, "4", 127]
    assert tape[LATE] == ["MOVE", ADVANCED, 1090, 127, False]
    assert tape[OUT_CLOCK] == ["ADD", OUT, TARGET, "1/2", 127]
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


def replay(word, initial, alpha=None, repair=None):
    tape = word["program"]
    active = dict(enumerate(word["initial"]))
    owners = {}
    rows = initial.copy()
    empty = {}
    watch = {}
    counts = {"init": 0, "clear": 0, "copy": 0, "move": 0}
    owner_observers = {}

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
            if source == OWNER and dst != CARRIER:
                owner_observers[clock] = (dst, before, get(source), result)
        if result:
            rows[dst] = result
        else:
            rows.pop(dst, None)

    for clock, event in enumerate(tape[:OUT_CLOCK + 1]):
        if clock == SOURCE:
            assert active[OWNER] == active[CARRIER] == 1090 and OWNER in owners
            watch["t"] = get(OWNER)
            watch["e"] = get(CARRIER)
            watch["owner_birth"] = owners[OWNER]
            assert watch["e"] == initial.get(CARRIER, empty)
        if clock == RETIRE:
            watch["owner_retired"] = get(OWNER)
            watch["owners_at_retirement"] = owners.copy()
        if alpha is not None:
            if clock == SOURCE:
                if alpha:
                    execute(["ADD", CARRIER, OWNER, alpha, 1090], SOURCE)
                execute(["MOVE", CARRIER, 1090, 127, False], SOURCE)
                continue
            if clock in (OMIT, LATE):
                if clock == LATE:
                    assert active[ADVANCED] == 127
                    watch["late_1397"] = get(ADVANCED)
                continue
            if clock == RETIRE:
                event = ["CLEAR", OWNER, 1090]
            if clock == CUT:
                execute(tape[LATE], LATE)
        if clock == CUT:
            assert OWNER not in active and OWNER not in owners and active[TARGET] == 127
            assert active[ADVANCED] == active[CARRIER] == (127 if alpha is not None else 1090)
            watch["cut_owners"] = owners.copy()
            watch["bank"] = {
                r: get(r) for r, chart in sorted(active.items()) if chart == 127 and r not in (TARGET, CARRIER)
            }
            watch["carrier_at_cut"] = get(CARRIER)
            watch["uncorrected_target"] = get(TARGET)
            if repair is not None:
                assert alpha is not None
                for operation in repair:
                    execute(operation, CUT)
            watch["before_scale"] = get(TARGET)
            watch["carrier_before_scale"] = get(CARRIER)
        if clock == LATE and alpha is None:
            assert active[ADVANCED] == 1090
            watch["late_1397"] = get(ADVANCED)
        if clock == OUT_CLOCK:
            watch["out_before"] = get(OUT)
            watch["out_donor"] = get(TARGET)
        execute(event, clock)
        if clock == CUT:
            watch["after_scale"] = get(TARGET)
        if clock == LATE + 1:
            watch["late_1397_receiver"] = get(787)
        if clock == OUT_CLOCK:
            watch["out_after"] = get(OUT)
    return watch, counts, owner_observers


def compare_prefix(word, initial, bank_roles, alpha, repair=None):
    old, old_counts, old_reads = replay(word, initial)
    edited, edited_counts, edited_reads = replay(word, initial, alpha, repair)
    e, t = old["e"], old["t"]
    assert e == edited["e"] and t == edited["t"] == old["owner_retired"] == edited["owner_retired"]
    assert old["owner_birth"] == edited["owner_birth"]
    assert old["owners_at_retirement"] == edited["owners_at_retirement"]
    assert old["cut_owners"] == edited["cut_owners"]
    assert {i: v for i, v in old_reads.items() if i != OMIT} == edited_reads
    assert list(edited["bank"]) == bank_roles
    assert set(edited["bank"]) == set(old["bank"]) | {ADVANCED}
    assert all(edited["bank"][r] == row for r, row in old["bank"].items())
    assert old["late_1397"] == edited["late_1397"] == edited["bank"][ADVANCED]
    assert old["late_1397_receiver"] == edited["late_1397_receiver"]
    assert old_counts == edited_counts
    assert old["carrier_at_cut"] == e and edited["carrier_at_cut"] == add(e, t, alpha)
    assert old["uncorrected_target"] == add(edited["uncorrected_target"], t, Q(1))
    assert old["out_before"] == edited["out_before"]
    if repair is None:
        assert old["before_scale"] == add(edited["before_scale"], t, Q(1))
        assert old["after_scale"] == add(edited["after_scale"], t, Q(4))
        assert old["out_donor"] == add(edited["out_donor"], t, Q(4))
        assert old["out_after"] == add(edited["out_after"], t, Q(2))
    else:
        assert edited["carrier_before_scale"] == e
        assert all(old[k] == edited[k] for k in ("before_scale", "after_scale", "out_donor", "out_after"))
    return old, edited, old_counts


def scalar(row):
    assert set(row) <= {0}
    return row.get(0, Q(0))


def check_separator(word, lead):
    probes = lead["probes"]
    assert len(probes) == 2
    records = []
    for raw_probe in probes:
        probe = {int(i): Q(value) for i, value in raw_probe.items()}
        assert probe and len(probe) == len(raw_probe)
        assert all(0 <= i < word["public"] and v for i, v in probe.items())
        initial = {r: {0: v} for r, v in probe.items()}
        old, edited, counts = compare_prefix(word, initial, lead["bank_roles"], Q(1))
        assert not any(edited["bank"].values())
        records.append({
            "probe": probe, "e": scalar(old["e"]), "t": scalar(old["t"]),
            "whole_unchanged_bank_zero": True, "bank_role_count": len(edited["bank"]),
            "owned_bank_roles": [r for r in edited["bank"] if r in edited["cut_owners"]],
            "encoded_carrier_at_alpha_one": scalar(edited["carrier_at_cut"]),
            "old1004_before_scale": scalar(old["before_scale"]),
            "unrepaired1004_before_scale": scalar(edited["before_scale"]),
            "old1004_after_scale": scalar(old["after_scale"]),
            "unrepaired1004_after_scale": scalar(edited["after_scale"]),
            "old830_after_first_outward": scalar(old["out_after"]),
            "unrepaired830_after_first_outward": scalar(edited["out_after"]),
            "old_and_edited_guards": counts,
        })
    (a, b), (c, d) = minor = [[r["e"], r["t"]] for r in records]
    determinant = a * d - b * c
    assert minor == [[Q(v) for v in row] for row in lead["minor"]]
    assert determinant == Q(lead["determinant"]) != 0
    return {
        "status": "PASS_INDEPENDENT_TWO_DIRECTION_QUOTIENT_EXCLUSION",
        "records": records, "minor": minor, "determinant": determinant,
        "bank_roles": lead["bank_roles"],
    }


def check_support(word, lead):
    alpha = Q(lead["alpha"])
    repair = lead["repair"]
    donors = set(lead["bank_roles"])
    for op, dst, *args in repair:
        assert dst in (TARGET, CARRIER) and args[-1] == 127
        if op == "ADD":
            assert args[0] in (donors | {CARRIER}) - {dst} and Q(args[1])
        else:
            assert op == "SCALE" and dst == CARRIER and Q(args[0])
    initial = {r: {r: Q(1)} for r in range(word["public"])}
    _, edited, counts = compare_prefix(word, initial, lead["bank_roles"], alpha, repair)
    return {
        "status": "PASS_INDEPENDENT_RATIONAL_SUPPORT",
        "alpha": alpha, "repair": repair, "basis_dimension": word["public"],
        "bank_role_count": len(edited["bank"]), "old_and_edited_guards": counts,
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
    assert lead["case"] == CASE and lead["cut"] == CUT and lead["unresolved"] == []
    if lead["status"] == "EXACT_TWO_DIRECTION_QUOTIENT_EXCLUSION":
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
