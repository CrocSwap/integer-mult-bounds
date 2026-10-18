#!/usr/bin/env python3
"""Window-restored resident packets for the pinned R439 interleaved window.

ywz65 with substantial OpenAI Codex assistance, Apache-2.0. The packet route
compiler and source-window constructor are explicitly reused from PR2448;
the finite routing/endpoint harness is adapted from ywz65 PR2481. This adds
window residency, the exact restricted schedule minimum and its complete bill.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import itertools
import sys
import tempfile
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
    exec(compile((HERE / "source/pr2448/verify.py").read_bytes(), str(HERE / "source/pr2448/verify.py"), "exec"), source.__dict__)
    source.ROOT = ROOT
    return source


def logical_rows(events):
    rows = [1 << i for i in range(112)]
    for target, source in events:
        require(0 <= target < 111 and 0 <= source < 112 and target != source, "logical event")
        rows[target] ^= rows[source]
    return rows



def plan(events):
    """Unit-load exact DP; no prefetch, event reorder or third resident slot."""
    states = {(): (0, ())}
    for target, src in events:
        needed = {target} | ({src} if src != 111 else set())
        require(0 <= target < 111 and 0 <= src <= 111 and target != src, "schedule role")
        following = {}
        for old, (cost, history) in states.items():
            pool = set(old) | needed
            for new in itertools.combinations(sorted(pool), min(2, len(pool))):
                if not needed.issubset(new):
                    continue
                candidate = cost + len(set(new) - set(old)), history + (new,)
                if new not in following or candidate < following[new]:
                    following[new] = candidate
        states = following
    cost, history = min(states.values())
    return {"loads": cost, "states": history}


def greedy_loads(events):
    """Independent farthest-next-demand policy for the two-slot set requests."""
    requests = [{d} | ({s} if s != 111 else set()) for d, s in events]
    resident = set()
    loads = 0
    for i, needed in enumerate(requests):
        for role in sorted(needed - resident):
            if len(resident) == 2:
                choices = resident - needed
                require(bool(choices), "greedy capacity")
                def next_use(candidate):
                    return next((j for j in range(i + 1, len(requests))
                                 if candidate in requests[j]), len(requests))
                resident.remove(max(choices, key=lambda r: (next_use(r), r)))
            resident.add(role)
            loads += 1
    return loads


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

    schedule = plan(events)
    require(schedule["loads"] == greedy_loads(events), "independent schedule count")
    residents = [None, None]
    rows_now = [1 << i for i in range(112)]
    # Common-frame atoms from direct full-ring multiplication, separate from
    # the inherited carry/adjacent-swap route compiler.
    common_atoms = [[atom(role, source.ROW_INDEX[source.mul(source.join(source.IDENTITY, hi),
                    source.inv(charts[role]))]) for hi in source.HIGH] for role in range(111)]
    common_atoms.append(list(snapshot_before))

    def expect_common(role, position):
        terms = frozenset()
        for contributor in range(112):
            if rows_now[role] >> contributor & 1:
                terms ^= common_atoms[contributor][position]
        return terms

    def check_residents():
        for bank, role in enumerate(residents):
            if role is None:
                require(tuple(buffers[bank]) == dirty_before[bank], "inactive bank not restored")
            else:
                require(tuple(families[role][i] for i in owned[role]) == dirty_before[bank],
                        "parked bank dirt changed")
                require(all(value == expect_common(role, j) for j, value in enumerate(buffers[bank])),
                        "resident logical payload mismatch")
        require(tuple(snapshot) == snapshot_before, "snapshot not preserved")

    def evict(bank, skip_return=False):
        role = residents[bank]
        require(role is not None, "evict inactive bank")
        if not skip_return:
            route(role, bank, inverse=True)
        exchange(role, bank)
        residents[bank] = None
        require(tuple(buffers[bank]) == dirty_before[bank], "eviction failed dirty restoration")
        require(all(families[role][i] == expect_common(role, source.HI_INDEX[
                    source.split(source.mul(source.ROWS[i], charts[role]))[1]])
                    for i in owned[role]), "evicted logical payload mismatch")
        meter["residency_evictions"] += 1

    reuse_fault_done = False
    for index, ((target, src), wanted) in enumerate(zip(events, schedule["states"])):
        previous = tuple(residents)
        for bank, role in enumerate(residents):
            if role is not None and role not in wanted:
                evict(bank, fault == "omit_eviction_inverse" and meter["residency_evictions"] == 0)
        for role in wanted:
            if role not in residents:
                bank = residents.index(None)
                exchange(role, bank, fault == "dirty_copy_instead_of_swap" and index == 0)
                route(role, bank, corrupt=fault == "transient_snapshot_write" and index == 0)
                residents[bank] = role
                meter["residency_loads"] += 1
        require(len(set(r for r in residents if r is not None)) == sum(r is not None for r in residents),
                "duplicate resident ownership")
        check_residents()
        target_bank = residents.index(target)
        source_bank = None if src == 111 else residents.index(src)
        if fault == "forgot_resident_role" and not reuse_fault_done and target in previous:
            target_bank = 1 - target_bank
            reuse_fault_done = True
        values = snapshot if src == 111 else buffers[source_bank]
        for position in range(width):
            buffers[target_bank][position] ^= values[position]
        rows_now[target] ^= rows_now[src]
        meter["update_packet_xors"] += 1
        meter["packet_xor_records"] += width
        meter["update_head_steps"] += 4 * width
        meter["update_head_returns"] += 2
        if src == 111:
            meter["snapshot_read_head_returns"] += 1
        meter["reused_resident_boundaries"] += len(set(wanted) & {r for r in previous if r is not None})
        check_residents()
        meter["checked_event_boundaries"] += 1
    for bank, role in enumerate(residents):
        if role is not None and not (fault == "omit_final_flush" and bank == 0):
            evict(bank)
    require(residents == [None, None], "resident packet not returned at window boundary")
    check_residents()

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
    loads = schedule["loads"]
    require(meter["residency_loads"] == loads and meter["residency_evictions"] == loads,
            "complete residence interval count")
    require(meter["route_actions"] == 2 * loads and meter["packet_exchanges"] == 2 * loads,
            "complete resident route/exchange invoice")
    require(meter["packet_xor_records"] == (6 * loads + len(events)) * width, "complete XOR invoice")
    return {"meter": dict(sorted(meter.items())), "checked_target_records": checked,
            "unowned_records_checked": 111 * 47 * 81, "dirty_records_restored_at_window": 2 * width,
            "snapshot_records_preserved": width, "formal_input_records": checked + 3 * width,
            "fresh_payload_records": 0, "clear_or_disposal_operations": 0,
            "schedule": schedule, "minimum_loads_in_fixed_model": loads}


def calculate():
    source = load_source()
    events, baseline, binding = source.source_window()
    require(logical_rows(events) == logical_rows(baseline), "source logical endpoint")
    normal = execute(source, events, baseline)
    inverse = execute(source, list(reversed(events)), list(reversed(baseline)))
    rejected = {}
    expected_failures = {
        "dirty_copy_instead_of_swap": "parked bank dirt changed",
        "omit_final_flush": "resident packet not returned at window boundary",
        "omit_eviction_inverse": "evicted logical payload mismatch",
        "forgot_resident_role": "resident logical payload mismatch",
        "omit_carry": "resident logical payload mismatch",
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
    return {"status": "PASS_R439_RESIDENT_PACKETS", "source_binding": binding,
            "forward": normal, "inverse_fragment": inverse, "controls": rejected,
            "scope": "Conditional two-bank window-restored residency with temporarily exchanged originals; finite GL2(Z/9) route replay, no uniform GL64 compiler, child scratch admission or new kappa"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    # A fresh empty cache namespace makes retained SourceFileLoader calls read
    # source bytes even under -B. This is replay hygiene, not a security sandbox.
    old_prefix = sys.pycache_prefix
    old_write = sys.dont_write_bytecode
    with tempfile.TemporaryDirectory(prefix="r439-bytecode-") as cache:
        sys.pycache_prefix, sys.dont_write_bytecode = cache, True
        try:
            result = calculate()
        finally:
            sys.pycache_prefix, sys.dont_write_bytecode = old_prefix, old_write
    # Match JSON arrays in the immutable receipt.
    result = json.loads(json.dumps(result))
    path = HERE / "RESULT.json"
    if args.write_result:
        with path.open("x", encoding="utf-8", newline="\n") as out:
            json.dump(result, out, sort_keys=True, indent=2)
            out.write("\n")
    else:
        require(json.loads(path.read_text(encoding="utf-8")) == result, "committed receipt mismatch")
    print("PASS_R439_RESIDENT_PACKETS events=313 minimum_loads=542 routes=1084 swaps=1084 packet_xors=3565 dirty_buffers=2 controls=7 no_new_kappa")


if __name__ == "__main__":
    main()
