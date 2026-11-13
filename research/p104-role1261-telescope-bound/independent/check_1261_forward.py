"""Replay the role1261 telescoping correction on the literal #7481 chronology."""
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
HELPER, OBSERVER, PROTECTED, CHART = 1261, 1191, 964, 246
FIRST_MOVE, FIRST_ADD, FUSE, CUT = 38490, 38491, 39433, 39469
BANK = [1145, 1192, 1261, 1443, 1485, 1486, 1487]
CASE = "1261-telescoped-1191-chart246-pre39469"
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
    for v in basis:
        assert v not in out
        out |= {v ^ w for w in out}
    return out


def touches(event, role):
    return role == event[1] or event[0] in ("ADD", "COPY") and role == event[2]


def check_structure(word):
    tape = word["program"]
    assert len(tape) == 76475 and len(word["initial"]) == word["public"] == 1501
    protected = set(word["live"]) | {r + 112 for r in word["live"]}
    protected |= set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
    assert len(protected) == 400 and PROTECTED in protected
    assert HELPER not in protected and OBSERVER not in protected
    frames = [span(word["frames"][c]) for c in (3, 509, 770)]
    assert list(map(len, frames)) == [1, 8, 64]
    assert frames[0] < frames[1] < frames[2]
    assert tape[FIRST_MOVE:FIRST_ADD + 1] == [
        ["MOVE", HELPER, 3, 509, False], ["ADD", OBSERVER, HELPER, "-1", 509],
    ]
    assert tape[FUSE] == ["MOVE", HELPER, 509, 770, False]
    assert tape[CUT] == ["ADD", OBSERVER, HELPER, "1", CHART]
    assert [i for i in range(FIRST_MOVE, FUSE + 1) if touches(tape[i], HELPER)] == [FIRST_MOVE, FIRST_ADD, FUSE]
    observer = {i: tape[i] for i in range(FIRST_ADD, CUT + 1) if touches(tape[i], OBSERVER)}
    assert list(observer) == [FIRST_ADD, 38492, 38494, 38536, 38538, 38876, 38878, CUT]
    assert all(e[1] == OBSERVER and e[0] in ("ADD", "MOVE") for e in observer.values())
    assert tape[38538] == ["ADD", OBSERVER, PROTECTED, "1/2", 925]
    assert tape[39438] == ["ADD", HELPER, 910, "1/2", 903]
    assert tape[39441] == ["ADD", 1145, 953, "-1", 901]
    assert tape[39465] == ["ADD", 910, 894, "-1", 903]
    return observer


def add(left, right, scale=Q(1)):
    result = left.copy()
    for r, v in right.items():
        total = result.get(r, 0) + scale * v
        if total:
            result[r] = total
        else:
            result.pop(r, None)
    return result


def replay(word, initial, edited=False, coefficients=None):
    tape = word["program"]
    active = dict(enumerate(word["initial"]))
    owners = {}
    rows = initial.copy()
    watches = {}
    counts = {"init": 0, "clear": 0, "copy": 0, "move": 0}
    retirement = {}
    copies = {}
    owned_moves = {}
    observer_reads = {}
    prefix = {}
    target_bank = {}
    empty = {}

    def get(role):
        return rows.get(role, empty)

    def apply(event, clock):
        op, dst, *args = event
        before = get(dst)
        if op == "MOVE":
            src, dest, flag = args
            assert src != dest and active[dst] == src and flag == (dst in owners) == (dst >= word["public"])
            active[dst] = dest
            counts["move"] += 1
            if flag:
                owned_moves[clock] = (owners[dst], event, before)
            return
        if op == "INIT":
            assert dst >= word["public"] and dst not in active and dst not in owners and not before
            active[dst] = args[0]
            owners[dst] = clock
            counts["init"] += 1
            return
        if op == "CLEAR":
            assert dst in owners and active.pop(dst) == args[0]
            retirement[clock] = (owners.pop(dst), event, before)
            rows.pop(dst, None)
            counts["clear"] += 1
            return
        if op == "SCALE":
            coefficient, chart = args
            assert active[dst] == chart
            result = add({}, before, Q(coefficient))
        else:
            assert op in ("ADD", "COPY")
            donor, coefficient, chart = args
            assert donor != dst and active[dst] == active[donor] == chart
            source = get(donor)
            if op == "COPY":
                assert not before
                copies[clock] = (event, before, source)
                counts["copy"] += 1
            result = add(before, source, Q(coefficient))
            if clock in (38494, 38538, 38878):
                observer_reads[clock] = (donor, source, before, result)
        if result:
            rows[dst] = result
        else:
            rows.pop(dst, None)

    for clock, event in enumerate(tape):
        if clock == FIRST_ADD:
            watches["v"] = get(HELPER)
        if clock == 39438:
            watches["historical910"] = get(910)
        if clock == 39441:
            watches["historical953"] = get(953)
        if clock == 39466:
            watches["later910"] = get(910)
        if clock == CUT:
            assert active[OBSERVER] == CHART
            target_bank = {r: get(r) for r, c in sorted(active.items()) if c == CHART and r != OBSERVER}
            assert list(target_bank) == BANK
            watches["observer_before"] = get(OBSERVER)
            watches["helper_before"] = get(HELPER)
            prefix = {r: value for r, value in rows.items() if r != OBSERVER}
            watches["cut_owners"] = owners.copy()
            if edited:
                if coefficients is not None:
                    for donor, weight in coefficients.items():
                        if weight:
                            apply(["ADD", OBSERVER, donor, weight, CHART], CUT)
                watches["observer_after"] = get(OBSERVER)
                if coefficients is None:
                    break
                continue
        if edited and clock in (FIRST_MOVE, FIRST_ADD):
            continue
        if edited and clock == FUSE:
            event = ["MOVE", HELPER, 3, 770, False]
        apply(event, clock)
        if clock == CUT:
            watches["observer_after"] = get(OBSERVER)
            if coefficients is None:
                break

    if coefficients is not None:
        assert not owners and active == dict(enumerate(word["final"]))
    return {
        "watch": watches, "bank": target_bank, "prefix": prefix, "observers": observer_reads,
        "retirement": retirement, "copy": copies, "owned_moves": owned_moves,
        "counts": counts, "final": rows if coefficients is not None else None,
    }


def compare(word, initial, coefficients=None):
    # In the support case an empty correction marks the original replay as full-word.
    old = replay(word, initial, coefficients={} if coefficients is not None else None)
    edited = replay(word, initial, edited=True, coefficients=coefficients)
    ow, ew = old["watch"], edited["watch"]
    assert old["bank"] == edited["bank"] and old["prefix"] == edited["prefix"]
    assert old["retirement"] == edited["retirement"] and old["copy"] == edited["copy"]
    assert old["owned_moves"] == edited["owned_moves"] and ow["cut_owners"] == ew["cut_owners"]
    assert old["counts"]["move"] == edited["counts"]["move"] + 1
    assert all(old["counts"][k] == edited["counts"][k] for k in ("init", "clear", "copy"))
    v = ow["v"]
    assert all(ow[k] == ew[k] for k in ("v", "historical910", "historical953", "later910", "helper_before"))
    target = add(add({}, ow["historical910"], Q(1, 2)), ow["historical953"], Q(1, 2))
    assert add(v, target) == ow["helper_before"]
    assert ew["observer_before"] == add(ow["observer_before"], v)
    for i in old["observers"]:
        source, donor, before, after = old["observers"][i]
        other_source, other_donor, other_before, other_after = edited["observers"][i]
        assert (source, donor) == (other_source, other_donor)
        assert (add(before, v), add(after, v)) == (other_before, other_after)
    assert ow["observer_after"] == add(ew["observer_before"], target)
    if coefficients is None:
        assert ow["observer_after"] == add(ew["observer_after"], target)
    else:
        assert ow["observer_after"] == ew["observer_after"]
        assert old["final"] == edited["final"]
    return old, edited, target


def rationals(values):
    result = {int(r): Q(v) for r, v in values.items()}
    assert len(result) == len(values)
    return result


def scalar(row):
    assert set(row) <= {0}
    return row.get(0, Q(0))


def check_separator(word, lead):
    probe = rationals(lead["probe"])
    assert probe and all(0 <= r < word["public"] and v for r, v in probe.items())
    old, edited, target = compare(word, {r: {0: v} for r, v in probe.items()})
    assert not any(edited["bank"].values()) and scalar(target) == 1
    assert sum(v * probe.get(r, 0) for r, v in rationals(lead["target"]).items()) == 1
    ow, ew = old["watch"], edited["watch"]
    return {
        "status": "PASS_INDEPENDENT_FIXED_DONOR_SEPARATOR", "probe": probe,
        "bank_responses": {r: scalar(row) for r, row in edited["bank"].items()},
        "target_response": 1, "old1261_before_first_add": scalar(ow["v"]),
        "old910_before_39438": scalar(ow["historical910"]),
        "old953_before_39441": scalar(ow["historical953"]),
        "old910_after_39465": scalar(ow["later910"]),
        "old1191_before": scalar(ow["observer_before"]),
        "edited1191_before": scalar(ew["observer_before"]),
        "old1191_after": scalar(ow["observer_after"]),
        "unrepaired1191_after": scalar(ew["observer_after"]),
        "protected964_at_38538": scalar(old["observers"][38538][1]),
        "old_guards": old["counts"], "edited_guards": edited["counts"],
        "owned_move_guards_each": len(old["owned_moves"]),
        "cut_owner_count_each": len(ow["cut_owners"]),
    }


def check_support(word, lead):
    coefficients = rationals(lead["representation"])
    assert coefficients.keys() <= set(BANK)
    initial = {r: {r: Q(1)} for r in range(word["public"])}
    old, edited, target = compare(word, initial, coefficients)
    recovered = {}
    for r, weight in coefficients.items():
        recovered = add(recovered, old["bank"][r], weight)
    assert recovered == target == rationals(lead["target"])
    return {
        "status": "PASS_INDEPENDENT_RATIONAL_SUPPORT", "coefficients": coefficients,
        "basis_dimension": word["public"], "target_support_size": len(target),
        "old_guards": old["counts"], "edited_guards": edited["counts"],
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
    contacts = check_structure(word)
    raw_lead = args.lead_receipt.read_bytes()
    assert sha256(raw_lead).hexdigest() == args.lead_sha256
    lead = loads(raw_lead, object_pairs_hook=unique_pairs)
    assert lead["case"] == CASE and lead["cut"] == CUT and lead["bank"] == BANK
    assert lead["fixed_self_coefficient"] == 1 and lead["tested"] == 1 and lead["unresolved"] == []
    if lead["status"] == "EXACT_FIXED_DONOR_EXCLUSION":
        result = check_separator(word, lead)
    else:
        assert lead["status"] == "EXACT_RATIONAL_SUPPORT_REQUIRES_FULL_PRICE"
        result = check_support(word, lead)
    emit(**result, case=CASE, observer_contacts=contacts, input_pins=PINS, native_sha256=NATIVE,
         caller_head=CALLER, lead_sha256=args.lead_sha256,
         runner_cap_seconds=CAP_SECONDS, seconds=perf_counter() - started)
    alarm(0)


if __name__ == "__main__":
    main()
