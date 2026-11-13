"""Independently replay the advanced-1369 correction gate by literal forward substitution."""
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
CUT, MOVED, ADVANCED, OWNER, OUT, CHART = 48155, 1351, 1369, 1568, 408, 127
CASE = "public1351-advanced1369-pre48155"
CAP_SECONDS = 30
STOP = 52132


def emit(**record):
    print(dumps(record, default=str, sort_keys=True), flush=True)


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


def check_structure(word):
    tape = word["program"]
    assert len(tape) == 76475 and len(word["initial"]) == word["public"] == 1501
    start, mid, terminal, producer = (span(word["frames"][c]) for c in (516, 518, CHART, 240))
    assert start < mid < terminal and producer < terminal
    assert list(map(len, (start, mid, terminal, producer))) == [16, 256, 512, 16]
    assert tape[38867:38869] == [["MOVE", MOVED, 516, 518, False], ["ADD", MOVED, 1020, "-1", 518]]
    assert tape[CUT - 1:CUT + 1] == [["MOVE", MOVED, 518, CHART, False], ["ADD", OUT, MOVED, "1", CHART]]
    assert [i for i in range(38867, CUT + 1) if touches(tape[i], MOVED)] == [38867, 38868, CUT - 1, CUT]
    assert tape[52128:52130] == [["ADD", ADVANCED, OWNER, "12", 240], ["MOVE", ADVANCED, 240, CHART, False]]
    assert [i for i in range(36375, STOP) if touches(tape[i], ADVANCED)] == [36375, 52128, 52129, 52131]
    assert tape[37772:37774] == [["INIT", OWNER, 240], ["ADD", OWNER, 863, "1", 240]]
    assert not any(event[1] == OWNER for event in tape[37774:52129])
    owner_reads = {i: tape[i] for i in range(37774, 52129) if touches(tape[i], OWNER)}
    return owner_reads


def plus(left, right, scale=Q(1)):
    result = left.copy()
    for j, value in right.items():
        total = result.get(j, 0) + scale * value
        if total:
            result[j] = total
        else:
            result.pop(j, None)
    return result


def forward(word, initial, edited):
    tape = word["program"]
    active = dict(enumerate(word["initial"]))
    owned = {}
    rows = initial.copy()
    trace = {}
    observations = {}
    guard_count = {"copy": 0, "init": 0, "clear": 0, "move": 0}
    empty = {}

    def read(r):
        return rows.get(r, empty)

    def apply(event, label):
        op, dst, *args = event
        before = read(dst)
        if op == "MOVE":
            source, dest, flag = args
            assert active[dst] == source and flag == (dst in owned) == (dst >= word["public"])
            assert source != dest
            active[dst] = dest
            guard_count["move"] += 1
            return
        if op == "INIT":
            assert dst >= word["public"] and dst not in active and dst not in owned and not before
            active[dst] = args[0]
            owned[dst] = label
            guard_count["init"] += 1
            return
        if op == "CLEAR":
            assert dst in owned and active.pop(dst) == args[0]
            del owned[dst]
            rows.pop(dst, None)
            guard_count["clear"] += 1
            return
        if op == "SCALE":
            coefficient, chart = args
            assert active[dst] == chart
            new = plus({}, before, Q(coefficient))
        else:
            assert op in ("ADD", "COPY")
            donor, coefficient, chart = args
            assert donor != dst and active[dst] == active[donor] == chart
            if op == "COPY":
                assert not before
                guard_count["copy"] += 1
            donor_value = read(donor)
            new = plus(before, donor_value, Q(coefficient))
            if label in (CUT, 52128):
                observations[label] = {"before": before, "donor": donor_value, "after": new}
        if new:
            rows[dst] = new
        else:
            rows.pop(dst, None)

    watches = {
        36360: (1098,), 37774: (OWNER,), 38868: (1020,), 39580: (1538,),
        CUT - 1: (ADVANCED, OWNER, MOVED), CUT: (1098, 1020, OUT, MOVED, OWNER, ADVANCED),
        52128: (ADVANCED, OWNER), 52130: (ADVANCED, OWNER), STOP - 1: (ADVANCED,),
    }
    for clock, event in enumerate(tape[:STOP]):
        if clock in watches:
            trace[clock] = {r: read(r) for r in watches[clock]}
        if clock == CUT:
            bank = {r: read(r) for r, c in sorted(active.items()) if c == CHART}
            cut_owned = owned.copy()
        if edited:
            if clock in (38867, 38868, 52128, 52129):
                continue
            if clock == CUT - 1:
                apply(["MOVE", MOVED, 516, CHART, False], clock)
                assert owned[OWNER] == 37772 and active[ADVANCED] == active[OWNER] == 240
                apply(tape[52128], 52128)
                apply(tape[52129], 52129)
                continue
        if not edited and clock == 52128:
            assert owned[OWNER] == 37772 and active[ADVANCED] == active[OWNER] == 240
        apply(event, clock)
    return bank, trace, observations, cut_owned, guard_count


def checked_prefixes(word, initial, lead):
    old, t, o, own, guards = forward(word, initial, edited=False)
    edited, u, e, edited_own, edited_guards = forward(word, initial, edited=True)
    assert own == edited_own and own[OWNER] == 37772
    assert guards["move"] == edited_guards["move"] + 1
    assert all(guards[k] == edited_guards[k] for k in ("copy", "init", "clear"))
    assert set(old) | {ADVANCED} == set(edited)
    assert list(r for r in edited if r != MOVED) == lead["donors"]
    assert all(old[r] == edited[r] for r in old if r != MOVED)
    p, w, h, a = t[36360][1098], t[37774][OWNER], t[38868][1020], t[39580][1538]
    assert edited[MOVED] == plus(old[MOVED], h)
    assert old[1020] == plus(plus(h, p, Q(-1)), w)
    assert old[1098] == plus(plus(plus({}, p, Q(-1)), a, Q(-1)), w, Q(3))
    assert all(trace[clock][OWNER] == w for trace in (t, u) for clock in (CUT - 1, CUT, 52128, 52130))
    assert t[CUT - 1][ADVANCED] == u[CUT - 1][ADVANCED] == t[52128][ADVANCED]
    assert e[52128] == o[52128]
    assert edited[ADVANCED] == plus(t[CUT][ADVANCED], w, Q(12))
    assert t[52130][ADVANCED] == u[52130][ADVANCED] == edited[ADVANCED]
    assert t[STOP - 1][ADVANCED] == u[STOP - 1][ADVANCED]
    assert o[CUT]["before"] == e[CUT]["before"] == old[OUT]
    assert o[CUT]["donor"] == old[MOVED] and e[CUT]["donor"] == edited[MOVED]
    assert o[CUT]["after"] == plus(o[CUT]["before"], old[MOVED])
    assert e[CUT]["after"] == plus(e[CUT]["before"], edited[MOVED])
    return old, edited, h, w, o[CUT], e[CUT], o[52128], own, guards, edited_guards


def scalar(row):
    assert set(row) <= {0}
    return row.get(0, Q(0))


def rational_map(values):
    result = {int(i): Q(v) for i, v in values.items()}
    assert len(result) == len(values)
    return result


def check_separator(word, lead):
    probe = rational_map(lead["probe"])
    assert probe and all(0 <= i < word["public"] and v for i, v in probe.items())
    initial = {i: {0: v} for i, v in probe.items()}
    old, edited, h, w, old_out, edit_out, producer, owners, guards, edited_guards = checked_prefixes(word, initial, lead)
    assert not any(edited.values()) and scalar(old[MOVED]) == Q(lead["old_1351_response"]) == 1
    assert scalar(h) == Q(lead["historical_h"]) == -1
    assert scalar(old_out["after"]) == 1 and scalar(edit_out["after"]) == 0
    return {
        "status": "PASS_INDEPENDENT_FIXED_ADVANCED_BANK_SEPARATOR",
        "probe": probe, "old1351": scalar(old[MOVED]), "historical_h": scalar(h),
        "owner1568_both_clocks": scalar(w),
        "producer1369_before": scalar(producer["before"]),
        "producer1369_after": scalar(producer["after"]),
        "old408_after": scalar(old_out["after"]), "edited408_after": scalar(edit_out["after"]),
        "old_bank": {r: scalar(row) for r, row in old.items()},
        "edited_bank": {r: scalar(row) for r, row in edited.items()},
        "old_guards": guards, "edited_guards": edited_guards,
        "owned_bank_roles": [r for r in edited if r in owners],
    }


def check_support(word, lead):
    initial = {r: {r: Q(1)} for r in range(word["public"])}
    old, edited, h, _w, old_out, edit_out, _producer, owners, guards, edited_guards = checked_prefixes(word, initial, lead)
    if lead["status"] == "EXACT_PURE_DONOR_SUPPORT":
        coefficients = rational_map(lead["coefficients_for_h"])
        assert coefficients.keys() <= set(edited) - {MOVED}
        total = edited[MOVED]
        for role, scalar_value in coefficients.items():
            total = plus(total, edited[role], -scalar_value)
    else:
        assert lead["status"] == "EXACT_ENLARGED_RATIONAL_SUPPORT"
        coefficients = rational_map(lead["coefficients_for_old1351"])
        assert coefficients.keys() <= set(edited)
        assert coefficients.get(MOVED, 0) == Q(lead["self_coefficient"])
        total = {}
        for role, scalar_value in coefficients.items():
            total = plus(total, edited[role], scalar_value)
    assert total == old[MOVED] and plus(edit_out["before"], total) == old_out["after"]
    return {
        "status": "PASS_INDEPENDENT_RATIONAL_SUPPORT",
        "basis_dimension": word["public"], "h_support_size": len(h), "coefficients": coefficients,
        "old_guards": guards, "edited_guards": edited_guards,
        "owned_bank_roles": [r for r in edited if r in owners],
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
    owner_reads = check_structure(word)

    raw_lead = args.lead_receipt.read_bytes()
    assert sha256(raw_lead).hexdigest() == args.lead_sha256
    lead = loads(raw_lead, object_pairs_hook=unique_pairs)
    assert lead["case"] == CASE and lead["cut"] == CUT and lead["advanced_role"] == ADVANCED
    assert lead["tested"] == 1 and lead["unresolved"] == []
    if lead["status"] == "EXACT_FIXED_ADVANCED_BANK_EXCLUSION":
        result = check_separator(word, lead)
    else:
        result = check_support(word, lead)
    emit(**result, case=CASE, unchanged_owner_reads=owner_reads, input_pins=PINS,
         native_sha256=NATIVE, caller_head=CALLER, lead_sha256=args.lead_sha256,
         runner_cap_seconds=CAP_SECONDS, seconds=perf_counter() - started)
    alarm(0)


if __name__ == "__main__":
    main()
