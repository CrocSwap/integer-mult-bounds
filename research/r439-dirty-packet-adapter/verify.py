#!/usr/bin/env python3
"""Reversible dirty-packet adapter for the pinned R439 interleaved window.

ywz65 with substantial OpenAI Codex assistance, Apache-2.0. The packet route
compiler and source-window constructor are explicitly reused from PR2448;
this verifier adds the borrowed-buffer protocol and its complete local bill.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, why):
    if not ok:
        raise ValueError(why)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load_source():
    pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]
    retained = json.loads((HERE / "PREDECESSORS.json").read_text(encoding="utf-8"))["files"]
    for base, records in ((ROOT, pins), (HERE, retained)):
        for item in records:
            if item.get("usage", "input") != "input":
                continue
            raw = (base / item["path"]).read_bytes()
            require(digest(raw) == item["sha256"], "source SHA256: " + item["path"])
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            require(blob == item["git_blob"], "source Git blob: " + item["path"])
    spec = importlib.util.spec_from_file_location("credited_pr2448", HERE / "source/pr2448/verify.py")
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    source.ROOT = ROOT
    return source


def logical_rows(events):
    rows = [1 << i for i in range(112)]
    for target, source in events:
        require(0 <= target < 111 and 0 <= source < 112 and target != source, "logical event")
        rows[target] ^= rows[source]
    return rows


def atom(role, row):
    return frozenset(((role, row),))


class Guard:
    active_route = False


class Parked(list):
    """Original streams cannot be written during a route child."""
    def __init__(self, values, guard):
        super().__init__(values)
        self.guard = guard

    def __setitem__(self, key, value):
        require(not self.guard.active_route, "route touched parked original or snapshot")
        super().__setitem__(key, value)


def execute(source, events, expected_events, fault=None):
    width = len(source.HIGH)
    charts = [source.chart(r) for r in range(111)]
    lows = [source.mul(source.IDENTITY, source.inv(a), source.Q) for a in charts]
    owned = [[i for i, g in enumerate(source.ROWS) if source.split(g)[0] == lo] for lo in lows]
    require(all(len(indices) == width for indices in owned), "complete packet size")
    selected = [set(indices) for indices in owned]
    forward = [source.compile_route(lo, a, fault == "omit_carry") for lo, a in zip(lows, charts)]
    backward = [source.compile_route(source.IDENTITY, source.inv(a)) for a in charts]
    guard = Guard()
    families = [Parked((atom(r, i) for i in range(len(source.ROWS))), guard) for r in range(111)]
    snapshot = Parked((atom(111, i) for i in range(width)), guard)
    snapshot_before = tuple(snapshot)
    # Two arbitrary, persistent, correlated-by-substitution dirty payload banks.
    buffers = [[atom(112 + bank, i) for i in range(width)] for bank in range(2)]
    dirty_before = [tuple(bank) for bank in buffers]
    meter = Counter()

    def exchange(role, bank, broken=False):
        # An in-place full family scan. Three XORs exchange payloads without
        # a clean record or overwrite. Unowned family records are untouched.
        offset = 0
        for position in range(len(families[role])):
            meter["exchange_family_records_scanned"] += 1
            if position not in selected[role]:
                continue
            a, b = families[role], buffers[bank]
            if broken:
                b[offset] ^= a[position]  # the invalid dirty-for-blank shortcut
                meter["packet_xor_records"] += 1
            else:
                a[position] ^= b[offset]
                b[offset] ^= a[position]
                a[position] ^= b[offset]
                meter["packet_xor_records"] += 3
            offset += 1
        require(offset == width, "exchanged whole packet")
        meter["packet_exchanges"] += 1
        meter["exchange_family_head_steps"] += 2 * len(families[role])
        meter["exchange_buffer_head_steps"] += 2 * width
        meter["exchange_family_head_returns"] += 1
        meter["exchange_buffer_head_returns"] += 1

    def route(role, bank, inverse=False, corrupt=False):
        inactive = tuple(buffers[1 - bank])
        old_snapshot = tuple(snapshot)
        program = backward[role] if inverse else forward[role]
        low = source.IDENTITY if inverse else lows[role]
        guard.active_route = True
        try:
            if corrupt:
                # Attempt a transient forbidden write, even if a caller would
                # later undo it. Boundary-only snapshot checks are insufficient.
                snapshot[0] ^= atom(999, 0)
            new_low, result = source.execute_route((low, buffers[bank]), program, meter)
        finally:
            guard.active_route = False
        require(result is buffers[bank], "route changed buffer identity")
        require(new_low == (lows[role] if inverse else source.IDENTITY), "route low class")
        require(tuple(buffers[1 - bank]) == inactive and tuple(snapshot) == old_snapshot,
                "route altered inactive buffer or snapshot")

    for index, (target, src) in enumerate(events):
        source_before = tuple(families[src][i] for i in owned[src]) if src != 111 else None
        exchange(target, 0, fault == "dirty_copy_instead_of_swap" and index == 0)
        route(target, 0, corrupt=fault == "transient_snapshot_write" and index == 0)
        if src == 111:
            values = snapshot
        else:
            exchange(src, 1)
            route(src, 1)
            values = buffers[1]
        for position in range(width):
            buffers[0][position] ^= values[position]
        meter["update_packet_xors"] += 1
        meter["packet_xor_records"] += width
        meter["update_head_steps"] += 4 * width
        meter["update_head_returns"] += 2
        if src == 111:
            meter["snapshot_read_head_returns"] += 1
        route(target, 0, inverse=True)
        if not (fault == "omit_target_exchange_back" and index == 0):
            exchange(target, 0)
        if src != 111:
            if not (fault == "omit_source_return" and index == next(i for i, e in enumerate(events) if e[1] != 111)):
                route(src, 1, inverse=True)
            exchange(src, 1)
            require(tuple(families[src][i] for i in owned[src]) == source_before,
                    "source packet not restored at event boundary")
        require([tuple(bank) for bank in buffers] == dirty_before, "borrowed dirty packet not restored")
        require(tuple(snapshot) == snapshot_before, "snapshot not preserved")
        meter["checked_event_boundaries"] += 1

    # Independent physical endpoint: logical split word and full-ring address
    # multiplication. It uses neither the carry compiler nor its permutation.
    rows = logical_rows(expected_events)
    checked = 0
    for role, family in enumerate(families):
        for position, g in enumerate(source.ROWS):
            if position not in selected[role]:
                expected = atom(role, position)
            else:
                common = source.mul(g, charts[role])
                terms = []
                for contributor in range(112):
                    if not (rows[role] >> contributor) & 1:
                        continue
                    if contributor == 111:
                        terms.append((111, source.HI_INDEX[source.split(common)[1]]))
                    else:
                        row = source.mul(common, source.inv(charts[contributor]))
                        terms.append((contributor, source.ROW_INDEX[row]))
                expected = frozenset(terms)
            require(family[position] == expected, "full-ring physical endpoint mismatch")
            checked += 1
    require(meter["route_actions"] == 1232 and meter["packet_exchanges"] == 1232,
            "complete dirty-adapter route/exchange invoice")
    require(meter["packet_xor_records"] == 4009 * width, "complete XOR invoice")
    return {"meter": dict(sorted(meter.items())), "checked_target_records": checked,
            "unowned_records_checked": 111 * 47 * 81, "dirty_records_restored_per_boundary": 2 * width,
            "snapshot_records_preserved": width, "formal_input_records": checked + 3 * width,
            "fresh_payload_records": 0, "clear_or_disposal_operations": 0}


def calculate():
    source = load_source()
    events, baseline, binding = source.source_window()
    require(logical_rows(events) == logical_rows(baseline), "source logical endpoint")
    normal = execute(source, events, baseline)
    inverse = execute(source, list(reversed(events)), list(reversed(baseline)))
    rejected = {}
    expected_failures = {
        "dirty_copy_instead_of_swap": "borrowed dirty packet not restored",
        "omit_target_exchange_back": "borrowed dirty packet not restored",
        "omit_source_return": "source packet not restored at event boundary",
        "omit_carry": "source packet not restored at event boundary",
        "transient_snapshot_write": "route touched parked original or snapshot",
    }
    for fault, expected_failure in expected_failures.items():
        try:
            execute(source, events, baseline, fault)
        except ValueError as error:
            require(str(error) == expected_failure, "fault failed for wrong reason: " + fault)
            rejected[fault] = str(error)
        else:
            raise ValueError("ineffective semantic fault: " + fault)
    wrong = list(events)
    last_tap = max(i for i, event in enumerate(wrong) if event[1] == 111)
    wrong.insert(0, wrong.pop(last_tap))
    try:
        execute(source, wrong, baseline)
    except ValueError as error:
        require("physical endpoint" in str(error), "wrong-cut fault failed for wrong reason")
        rejected["wrong_tap_cut_same_inventory"] = str(error)
    else:
        raise ValueError("ineffective tap-cut fault")
    return {"status": "PASS_R439_DIRTY_PACKET_ADAPTER", "source_binding": binding,
            "forward": normal, "inverse_fragment": inverse, "controls": rejected,
            "scope": "Conditional reversible payload adapter with temporarily exchanged originals; finite GL2(Z/9) route replay, no uniform GL64 compiler, child scratch admission or new kappa"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = calculate()
    path = HERE / "RESULT.json"
    if args.write_result:
        with path.open("x", encoding="utf-8", newline="\n") as out:
            json.dump(result, out, sort_keys=True, indent=2)
            out.write("\n")
    else:
        require(json.loads(path.read_text(encoding="utf-8")) == result, "committed receipt mismatch")
    print("PASS_R439_DIRTY_PACKET_ADAPTER events=313 routes=1232 swaps=1232 packet_xors=4009 dirty_buffers=2 controls=6 no_new_kappa")


if __name__ == "__main__":
    main()
