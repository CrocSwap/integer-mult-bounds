#!/usr/bin/env python3
"""Source-bound one-buffer relative-chart R439 adapter.

Ross Richardson with substantial OpenAI Codex assistance, Apache-2.0.
PR2481 supplies the two-buffer comparator and credited PR2448 source loader,
packet route compiler and chronological constructor. This is a new outer
schedule, not an independently implemented route compiler.
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


def load_source():
    for pin in json.loads((HERE / "PREDECESSORS.json").read_text())["files"]:
        raw = (HERE / pin["local_path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == pin["sha256"], "retained source SHA256")
        require(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
                == pin["git_blob"], "retained source Git blob")
    spec = importlib.util.spec_from_file_location("credited_pr2481", HERE / "source/pr2481/verify.py")
    parent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    parent.ROOT = ROOT
    return parent, parent.load_source()


def atom(role, row):
    return frozenset(((role, row),))


class Guard:
    routing = False


class Parked(list):
    def __init__(self, values, guard):
        super().__init__(values)
        self.guard = guard

    def __setitem__(self, key, value):
        require(not self.guard.routing, "route wrote parked payload")
        super().__setitem__(key, value)


def execute(source, events, expected_events, fault=None):
    width = len(source.HIGH)
    charts = [source.chart(r) for r in range(111)]
    lows = [source.mul(source.IDENTITY, source.inv(a), source.Q) for a in charts]
    owned = [[i for i, g in enumerate(source.ROWS) if source.split(g)[0] == lo] for lo in lows]
    selected = [set(indices) for indices in owned]
    require(all(len(indices) == width for indices in owned), "complete packets")
    forward = [source.compile_route(lo, a, fault == "omit_carry") for lo, a in zip(lows, charts)]
    backward = [source.compile_route(source.IDENTITY, source.inv(a)) for a in charts]
    guard = Guard()
    families = [Parked((atom(r, i) for i in range(len(source.ROWS))), guard) for r in range(111)]
    snapshot = Parked((atom(111, i) for i in range(width)), guard)
    snapshot_before = tuple(snapshot)
    buffer = [atom(112, i) for i in range(width)]
    dirty_before = tuple(buffer)
    meter = Counter()
    # Known layout annotation for the verifier, not implemented header storage.
    # Reversible physical header/control transitions are a separate obligation.
    current_low = None

    def exchange(role, broken=False):
        offset = 0
        for position in range(len(families[role])):
            meter["exchange_family_records_scanned"] += 1
            if position not in selected[role]:
                continue
            if broken:
                buffer[offset] ^= families[role][position]
                meter["packet_xor_records"] += 1
            else:
                families[role][position] ^= buffer[offset]
                buffer[offset] ^= families[role][position]
                families[role][position] ^= buffer[offset]
                meter["packet_xor_records"] += 3
            offset += 1
        require(offset == width, "exchange packet width")
        meter["packet_exchanges"] += 1
        meter["exchange_family_head_steps"] += 2 * len(families[role])
        meter["exchange_buffer_head_steps"] += 2 * width
        meter["exchange_family_head_returns"] += 1
        meter["exchange_buffer_head_returns"] += 1

    def route(role, inverse=False, corrupt=False):
        nonlocal current_low
        require(current_low == (source.IDENTITY if inverse else lows[role]), "route entry layout")
        guard.routing = True
        try:
            if corrupt:
                snapshot[0] ^= atom(999, 0)
            current_low, result = source.execute_route(
                (current_low, buffer), backward[role] if inverse else forward[role], meter)
        finally:
            guard.routing = False
        require(result is buffer, "one buffer identity")
        require(current_low == (lows[role] if inverse else source.IDENTITY), "route exit layout")

    for event_index, (target, src) in enumerate(events):
        require(0 <= target < 111 and 0 <= src <= 111 and target != src, "disjoint event roles")
        # Observer data below is verification state, never used by the adapter.
        source_before = tuple(families[src][i] for i in owned[src]) if src != 111 else None
        expected_target = []
        for position in owned[target]:
            common = source.mul(source.ROWS[position], charts[target])
            read = (snapshot[source.HI_INDEX[source.split(common)[1]]] if src == 111 else
                    families[src][source.ROW_INDEX[source.mul(common, source.inv(charts[src]))]])
            expected_target.append(families[target][position] ^ read)

        if src == 111:
            exchange(target, fault == "dirty_copy" and event_index == 0)
            current_low = lows[target]
            route(target, corrupt=fault == "snapshot_write" and event_index == 0)
            for i in range(width):
                buffer[i] ^= snapshot[i]
            meter["update_head_steps"] += 4 * width
            meter["snapshot_read_head_returns"] += 1
            route(target, inverse=True)
            if not (fault == "omit_exchange_back" and event_index == 0):
                exchange(target)
        else:
            exchange(src, fault == "dirty_copy" and event_index == 0)
            current_low = lows[src]
            route(src, corrupt=fault == "snapshot_write" and event_index == 0)
            route(target, inverse=True)
            require(current_low == lows[target], "target update layout")
            offset = 0
            for position in range(len(families[target])):
                meter["update_family_records_scanned"] += 1
                if position in selected[target]:
                    families[target][position] ^= buffer[offset]
                    offset += 1
            require(offset == width, "direct update packet width")
            if fault == "unowned_write":
                position = next(i for i in range(len(families[target])) if i not in selected[target])
                families[target][position] ^= atom(999, 0)
            meter["update_head_steps"] += 2 * len(families[target]) + 2 * width
            if fault == "wrong_return_order":
                route(src, inverse=True)
                route(target)
            else:
                route(target)
                if fault != "omit_source_inverse":
                    route(src, inverse=True)
            if not (fault == "omit_exchange_back" and event_index == 0):
                exchange(src)
            require(tuple(families[src][i] for i in owned[src]) == source_before,
                    "source not restored")
        meter["update_packet_xors"] += 1
        meter["packet_xor_records"] += width
        meter["update_head_returns"] += 2
        require(tuple(buffer) == dirty_before, "dirty bank not restored")
        require(tuple(snapshot) == snapshot_before, "snapshot not preserved")
        require(tuple(families[target][i] for i in owned[target]) == tuple(expected_target),
                "event full-ring endpoint")
        meter["checked_event_boundaries"] += 1
        meter["event_target_records_checked"] += width

    # Independent of route compilation: logical baseline + full-ring products.
    rows = source.columns(expected_events)
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
            require(family[position] == expected, "final full-ring endpoint")
            checked += 1
    ordinary = sum(src != 111 for _, src in events)
    taps = len(events) - ordinary
    require(meter["route_actions"] == 4 * ordinary + 2 * taps, "route invoice")
    require(meter["packet_exchanges"] == 2 * len(events), "exchange invoice")
    require(meter["packet_xor_records"] == 7 * len(events) * width, "XOR invoice")
    return {"meter": dict(sorted(meter.items())), "checked_family_records": checked,
            "unowned_records_checked": 111 * 47 * 81, "formal_input_records": checked + 2 * width,
            "dirty_records_restored_per_event": width, "snapshot_records_preserved": width,
            "fresh_payload_records": 0, "clear_or_disposal_operations": 0}


def calculate():
    _, source = load_source()
    events, baseline, binding = source.source_window()
    normal = execute(source, events, baseline)
    inverse = execute(source, list(reversed(events)), list(reversed(baseline)))
    old = json.loads((HERE / "source/pr2481/RESULT.json").read_text())
    route_keys = ("adjacent_record_swaps", "route_actions", "route_head_record_steps",
                  "route_head_returns", "route_record_reads", "route_record_writes")
    for new, prior in ((normal, old["forward"]), (inverse, old["inverse_fragment"])):
        require(all(new["meter"][key] == prior["meter"][key] for key in route_keys),
                "predecessor route counter comparison")
    rejected = {}
    faults = {"dirty_copy": {"dirty bank not restored", "source not restored"},
              "omit_exchange_back": {"dirty bank not restored", "source not restored"},
              "omit_source_inverse": {"source not restored"},
              "wrong_return_order": {"route entry layout"},
              "omit_carry": {"source not restored", "event full-ring endpoint"},
              "snapshot_write": {"route wrote parked payload"},
              "unowned_write": {"final full-ring endpoint"}}
    for fault, reasons in faults.items():
        try:
            execute(source, events, baseline, fault)
        except ValueError as exc:
            require(str(exc) in reasons, "fault failed for wrong reason: " + fault + ": " + str(exc))
            rejected[fault] = str(exc)
        else:
            raise ValueError("ineffective fault: " + fault)
    wrong = list(events)
    last = max(i for i, (_, src) in enumerate(wrong) if src == 111)
    wrong.insert(0, wrong.pop(last))
    try:
        execute(source, wrong, baseline)
    except ValueError as exc:
        require(str(exc) == "final full-ring endpoint", "wrong tap rejection")
        rejected["wrong_tap_cut_same_inventory"] = str(exc)
    else:
        raise ValueError("ineffective tap-cut fault")
    return {"status": "PASS_R439_ONE_BUFFER_PACKET", "source_binding": binding,
            "forward": normal, "inverse": inverse, "controls": rejected,
            "scope": "Conditional payload adapter; finite GL2(Z/9), no uniform GL64 compiler, supplier, optimality or new kappa"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = calculate()
    path = HERE / "RESULT.json"
    if args.write_result:
        with path.open("x", encoding="utf-8") as out:
            json.dump(result, out, indent=2, sort_keys=True)
            out.write("\n")
    else:
        require(json.loads(path.read_text()) == result, "receipt mismatch")
    print("PASS_R439_ONE_BUFFER_PACKET events=313 routes=1232 swaps=626 packet_xors=2191 dirty_banks=1 controls=8 no_new_kappa")


if __name__ == "__main__":
    main()
