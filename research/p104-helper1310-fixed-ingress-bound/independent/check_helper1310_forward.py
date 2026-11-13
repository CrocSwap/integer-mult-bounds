"""Check the helper1310 chart1051 fixed-cut gate by literal forward substitution."""
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
ROLE, CUT, CHART = 1310, 38219, 1051
FIRST_OUT, RECEIVER = CUT + 1, 1312
HISTORY = {35424: 890, 35425: 943}
CASE = "role1310-chart1051-pre38219"
CAP_SECONDS = 30


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


def check_structure(word):
    tape = word["program"]
    assert len(tape) == 76475 and len(word["initial"]) == word["public"] == 1501
    assert word["initial"][ROLE] == 3 and word["final"][ROLE] == 127
    lo, mid, hi = [span(word["frames"][chart]) for chart in (3, CHART, 127)]
    assert lo < mid < hi and len(mid) == 32 * len(lo) and len(hi) == 16 * len(mid)
    contacts = {}
    for clock, event in enumerate(tape[:CUT]):
        op, dst, *args = event
        if dst == ROLE or (op in ("COPY", "ADD") and args[0] == ROLE):
            contacts[clock] = event
    assert contacts == {
        **{clock: ["ADD", ROLE, donor, "1", 3] for clock, donor in HISTORY.items()},
        CUT - 2: ["MOVE", ROLE, 3, CHART, False],
    }
    assert tape[CUT - 1] == ["MOVE", 1311, 3, CHART, False]
    assert tape[CUT][:2] == ["ADD", ROLE] and tape[CUT][-1] == CHART and Q(tape[CUT][3])
    assert tape[FIRST_OUT][:3] == ["ADD", RECEIVER, ROLE]
    assert tape[FIRST_OUT][-1] == CHART and Q(tape[FIRST_OUT][3])
    return contacts


def affine_add(old, extra, coefficient):
    result = old.copy()
    for k, q in extra.items():
        value = result.get(k, 0) + coefficient * q
        if value:
            result[k] = value
        else:
            result.pop(k, None)
    return result


def forward(word, initial):
    active = dict(enumerate(word["initial"]))
    owned = set()
    rows = initial.copy()
    history = {}
    observations = {}
    checks = {"init": 0, "copy": 0, "move": 0}
    empty = {}
    for clock, (op, dst, *args) in enumerate(word["program"][:FIRST_OUT + 1]):
        if clock in HISTORY:
            history[clock] = rows.get(HISTORY[clock], empty)
        if clock == CUT:
            bank = {r: rows.get(r, empty) for r, c in sorted(active.items()) if c == CHART}
            bank_owners = [r for r in bank if r in owned]
        if op == "MOVE":
            src, dst_chart, owner = args
            assert active[dst] == src and owner == (dst in owned) == (dst >= word["public"])
            active[dst] = dst_chart
            checks["move"] += 1
            continue
        if op == "INIT":
            assert dst >= word["public"] and dst not in active and dst not in owned and dst not in rows
            active[dst] = args[0]
            owned.add(dst)
            checks["init"] += 1
            continue
        if op == "CLEAR":
            assert dst in owned and active.pop(dst) == args[0]
            owned.remove(dst)
            rows.pop(dst, None)
            continue
        old = rows.get(dst, empty)
        if op == "SCALE":
            weight, chart = args
            assert active[dst] == chart
            weight = Q(weight)
            new = {k: weight * value for k, value in old.items() if weight * value}
        else:
            assert op in ("ADD", "COPY")
            donor, weight, chart = args
            assert donor != dst and active[dst] == active[donor] == chart
            if op == "COPY":
                assert not old
                checks["copy"] += 1
            source = rows.get(donor, empty)
            new = affine_add(old, source, Q(weight))
            if clock in (CUT, FIRST_OUT):
                observations[clock] = {"destination": dst, "before": old, "source": donor,
                                       "source_value": source, "weight": weight, "after": new}
        if new:
            rows[dst] = new
        else:
            rows.pop(dst, None)
    return bank, bank_owners, history, observations, checks


def scalar(row):
    assert set(row) <= {0}
    return row.get(0, Q(0))


def check_separator(word, lead):
    probe = {int(i): Q(v) for i, v in lead["probe"].items()}
    assert probe and len(probe) == len(lead["probe"])
    assert all(0 <= i < word["public"] and value for i, value in probe.items())
    initial = {i: {0: v} for i, v in probe.items()}
    bank, owners, history, observations, checks = forward(word, initial)
    assert [r for r in bank if r != ROLE] == lead["bank"]
    responses = {r: scalar(row) for r, row in bank.items()}
    historical = [scalar(history[clock]) for clock in HISTORY]
    assert historical == [Q(v) for v in lead["historical_donor_responses"]]
    ingress = sum(historical)
    assert ingress == 1 and responses[ROLE] == probe.get(ROLE, 0) + ingress
    assert not any(v for r, v in responses.items() if r != ROLE)

    # Change only the still independent old input to make the complete bank zero.
    # A new helper's independently chosen input is zero too. Then no homogeneous
    # chart-local recovery can expose the nonzero old input.
    zero_bank_initial = initial.copy()
    zero_bank_initial[ROLE] = {0: -ingress}
    bank2, owners2, history2, observations2, checks2 = forward(word, zero_bank_initial)
    assert list(bank) == list(bank2) and owners == owners2 and checks == checks2
    assert history2 == history and all(not row for row in bank2.values())
    assert not observations2[FIRST_OUT]["after"] and not observations2[FIRST_OUT]["source_value"]
    first = observations[FIRST_OUT]
    assert scalar(first["before"]) == 0
    assert scalar(first["source_value"]) == responses[ROLE]
    assert scalar(first["after"]) == Q(first["weight"]) * responses[ROLE]
    return {
        "status": "PASS_INDEPENDENT_FIXED_INGRESS_SEPARATOR", "probe": probe,
        "historical_donor_responses": historical, "ingress_response": ingress,
        "chart_bank_responses": responses, "bank_owners": owners,
        "first_outward_event": word["program"][FIRST_OUT],
        "first_outward_response": scalar(first["after"]),
        "zero_complete_bank_probe": {**probe, ROLE: -ingress},
        "zero_complete_bank_responses": {r: scalar(row) for r, row in bank2.items()},
        "fresh_helper_input_for_control": 0,
        "required_recovered_old_input": -ingress, "first_outward_zero_bank_response": 0,
        "coframe_ownership_guards_each": checks,
    }


def check_support(word, lead):
    initial = {r: {r: Q(1)} for r in range(word["public"])}
    bank, owners, history, observations, checks = forward(word, initial)
    assert [r for r in bank if r != ROLE] == lead["bank"]
    g = affine_add(history[35424], history[35425], Q(1))
    assert ROLE not in g and all(ROLE not in row for r, row in bank.items() if r != ROLE)
    assert bank[ROLE] == affine_add(initial[ROLE], g, Q(1))
    representation = {int(r): Q(v) for r, v in lead["representation"].items()}
    assert len(representation) == len(lead["representation"])
    assert representation.keys() <= set(bank) - {ROLE}
    recovered = {}
    for r, coefficient in representation.items():
        recovered = affine_add(recovered, bank[r], coefficient)
    assert recovered == g
    y = word["public"] + word["owned_fields"]
    old_recovered = affine_add(bank[ROLE], recovered, Q(-1))
    new_role = affine_add({y: Q(1)}, recovered, Q(1))
    assert old_recovered == initial[ROLE]

    def relabel(row):
        assert y not in row
        return {(y if r == ROLE else r): v for r, v in row.items()}

    assert relabel(bank[ROLE]) == new_role
    incoming, outward = observations[CUT], observations[FIRST_OUT]
    new_role = affine_add(new_role, incoming["source_value"], Q(incoming["weight"]))
    new_outward = affine_add(outward["before"], new_role, Q(outward["weight"]))
    assert new_role == relabel(incoming["after"]) and new_outward == relabel(outward["after"])
    return {
        "status": "PASS_INDEPENDENT_RATIONAL_SUPPORT",
        "representation": representation, "input_basis_dimension": word["public"],
        "ingress_support_size": len(g), "bank_owners": owners,
        "checked_independent_fresh_role": y,
        "coframe_ownership_guards": checks,
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
    assert lead["case"] == CASE and lead["cut"] == CUT and lead["chart"] == CHART
    assert lead["tested"] == 1 and lead["unresolved"] == []
    if lead["status"] == "EXACT_FIXED_INGRESS_EXCLUSION":
        result = check_separator(word, lead)
    else:
        assert lead["status"] == "EXACT_RATIONAL_SUPPORT"
        result = check_support(word, lead)
    emit(**result, case=CASE, contacts=contacts, first_paid_arrival=word["program"][CUT - 1],
         input_pins=PINS, native_sha256=NATIVE, caller_head=CALLER, lead_sha256=args.lead_sha256,
         runner_cap_seconds=CAP_SECONDS, seconds=perf_counter() - started)
    alarm(0)


if __name__ == "__main__":
    main()
