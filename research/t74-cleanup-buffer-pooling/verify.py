#!/usr/bin/env python3
"""Exact private-buffer lifetimes in two frozen T74 cleanup words.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
Apache-2.0. No predecessor Python module is imported or executed.
"""
from __future__ import annotations
import argparse
from collections import Counter
import copy
from fractions import Fraction
import gzip
import hashlib
import heapq
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def check(condition, message):
    if not condition:
        raise ValueError(message)


def load_inputs():
    manifest = json.loads((HERE / "INPUTS.json").read_text())
    for item in manifest["files"]:
        data = (HERE / item["path"]).read_bytes()
        check(hashlib.sha256(data).hexdigest() == item["sha256"], "source digest: " + item["path"])
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        check(blob == item["git_blob"], "Git blob: " + item["path"])
    return {name: json.loads(gzip.decompress(
        (HERE / "source" / f"BORROW-WORD-43{name}.json.gz").read_bytes()))
        for name in ("base", "extra")}


def terms_add(left, right, coefficient):
    # Fresh row: no mutable source/destination aliasing.
    result = left.copy()
    for term, value in right.items():
        value = result.get(term, 0) + coefficient * value
        if value:
            result[term] = value
        else:
            result.pop(term, None)
    return result


def left_warp(row, letter):
    result = {}
    for (variable, word), coefficient in row.items():
        reduced = word[1:] if word and word[0] == -letter else (letter,) + word
        result[variable, reduced] = coefficient
    return result


def decode(gate, dual=False):
    # Inverse transpose of each gate, in original chronological order.
    if gate[0] == "add":
        _, destination, source, numerator, denominator, _ = gate
        q = Fraction(numerator, denominator)
        check(destination != source, "self add")
        return ("add", source, destination, -q) if dual else ("add", destination, source, q)
    if gate[0] == "scale":
        _, destination, numerator, denominator, _ = gate
        q = Fraction(numerator, denominator)
        check(q != 0, "singular scale")
        return "scale", destination, 1 / q if dual else q
    check(gate[0] == "warp", "unknown opcode")
    _, destination, operator, _ = gate
    check(operator != 0, "zero warp")
    # In the independent dual run generator j means K_j^{-T}.
    return "warp", destination, operator


def execute(state, event):
    op, destination, *args = event
    if op == "add":
        source, q = args
        state[destination] = terms_add(state[destination], state[source], q)
    elif op == "scale":
        state[destination] = {term: q * args[0] for term, q in state[destination].items()}
    else:
        state[destination] = left_warp(state[destination], args[0])


def schema(word):
    v, h, count = (word["report"][k] for k in ("v", "h", "R"))
    check((v, h, count) == (112, 9, 480), "word geometry")
    total = 2 * v + count
    removed = set(word["removed"])
    check(len(removed) == len(word["removed"]) == 43, "removed helpers")
    check(all(2*v <= r < total for r in removed), "removed range")
    live = set(range(total)) - removed
    cold = set(map(int, word["helper_final"]))
    check(len(cold) == 76 and cold <= live, "cold helper inventory")
    buffers = {total + r for r in cold}
    full = {256, 128, 64, 32, 16, 8, 4, 2, 1}
    for gate in word["cleanup"]:
        check(set(gate[-1]) == full and len(gate[-1]) == 9, "cleanup FULL frame")
        event = decode(gate)
        touched = {event[1], event[2]} if event[0] == "add" else {event[1]}
        check(touched <= live | buffers, "unknown cleanup role")
        check(not touched & cold, "cleanup touches preserved cold helper")
        if event[0] == "warp":
            check(abs(event[2]) <= len(word["warps"]), "unknown warp")
    for section in ("precondition", "compensation", "A", "cut", "B", "restore"):
        for gate in word[section]:
            touched = gate[1:3] if gate[0] == "add" else gate[1:2]
            check(set(touched) <= live, "private buffer touched before cleanup")
    return sorted(live), sorted(buffers)


def initial(live, buffers):
    state = {r: {(r, ()): Fraction(1)} for r in live}
    state.update({r: {} for r in buffers})
    return state


def row_digest(state, registers):
    rows = [[r, [[s, list(w), str(q)] for (s, w), q in sorted(state[r].items())]]
            for r in registers]
    return hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()


def trace(word, dual):
    live, buffers = schema(word)
    private = set(buffers)
    events = [decode(g, dual) for g in word["cleanup"]]
    state = initial(live, buffers)
    active, intervals, omitted = {}, [], []
    peak, peak_event, peak_buffers, peak_rows = 0, 0, [], []
    for step, event in enumerate(events, 1):
        op, destination = event[:2]
        before = bool(state[destination])
        is_zero_noop = ((op == "add" and not state[event[2]]) or
                        (op != "add" and not state[destination]))
        if is_zero_noop:
            omitted.append(step)
        execute(state, event)
        if destination in private:
            after = bool(state[destination])
            if after and not before:
                active[destination] = step
            elif before and not after:
                intervals.append(dict(buffer=destination, start=active.pop(destination), end=step))
        if len(active) > peak:
            peak, peak_event, peak_buffers = len(active), step, sorted(active)
            peak_rows = [[r, [[s, list(w), str(q)] for (s, w), q in sorted(state[r].items())]]
                         for r in peak_buffers]
    check(not active, "nonzero private field at cleanup exit")
    check(all(not state[r] for r in buffers), "private exit not zero")
    intervals.sort(key=lambda x: (x["start"], x["buffer"]))
    return dict(live=live, buffers=buffers, events=events, endpoint=state,
                intervals=intervals, peak=peak, peak_event=peak_event,
                peak_buffers=peak_buffers, peak_rows=peak_rows, omitted=omitted)


def color(intervals):
    # Optimal coloring of inclusive integer event intervals.
    pending, available, result = [], [], []
    slots = 0
    for item in intervals:
        while pending and pending[0][0] < item["start"]:
            _, slot = heapq.heappop(pending)
            heapq.heappush(available, slot)
        if available:
            slot = heapq.heappop(available)
        else:
            slot = slots
            slots += 1
        result.append(dict(item, slot=slot))
        heapq.heappush(pending, (item["end"], slot))
    return slots, result


def pooled_replay(data, plan, slots, *, dirty_slot=None, retained_zero_step=None):
    live, buffers = data["live"], data["buffers"]
    pool = [-(i + 1) for i in range(slots)]
    state = initial(live, pool)
    if dirty_slot is not None:
        state[pool[dirty_slot]] = {(10000, ()): Fraction(1)}
    private, current = set(buffers), {}
    begins, ends = {}, {}
    for interval in plan:
        begins.setdefault(interval["start"], []).append(interval)
        ends.setdefault(interval["end"], []).append(interval)
    omitted = set(data["omitted"])
    if retained_zero_step is not None:
        omitted.remove(retained_zero_step)
    for step, event in enumerate(data["events"], 1):
        for interval in begins.get(step, []):
            r, slot = interval["buffer"], pool[interval["slot"]]
            check(r not in current and slot not in current.values(), "overlapping buffer allocation")
            check(not state[slot], "allocation of dirty pool field")
            current[r] = slot
        if step not in omitted:
            op, destination, *args = event
            dst = current[destination] if destination in private else destination
            if op == "add":
                src, q = args
                src = current[src] if src in private else src
                check(src != dst, "pooled self add")
                execute(state, (op, dst, src, q))
            else:
                execute(state, (op, dst, *args))
        for interval in ends.get(step, []):
            slot = current.pop(interval["buffer"])
            check(not state[slot], "release of nonzero buffer")
    check(not current, "unreleased allocation")
    check(all(not state[r] for r in pool), "pool not restored")
    check(all(state[r] == data["endpoint"][r] for r in live), "pooled endpoint differs")
    return row_digest(state, live)


def hulls(intervals):
    result = {}
    for interval in intervals:
        r = interval["buffer"]
        if r not in result:
            result[r] = dict(interval)
        else:
            result[r]["end"] = interval["end"]
    return sorted(result.values(), key=lambda x: (x["start"], x["buffer"]))


def negative_controls(word, dual, data, plan, slots):
    def rejected(action, label, expected):
        try:
            action()
        except (ValueError, KeyError) as error:
            check(expected in str(error), label + ": wrong rejection: " + str(error))
            return label
        raise ValueError("control accepted: " + label)

    results = []
    # Two intervals provably alive at the maximum must not share a slot.
    at_peak = [i for i, x in enumerate(plan)
               if x["start"] <= data["peak_event"] < x["end"]]
    bad = copy.deepcopy(plan)
    bad[at_peak[1]]["slot"] = bad[at_peak[0]]["slot"]
    results.append(rejected(lambda: pooled_replay(data, bad, slots),
                            "overlap_at_clique", "overlapping buffer allocation"))
    # Releasing one event before a true zero return discards live information.
    bad = copy.deepcopy(plan)
    candidate = next(i for i, x in enumerate(bad) if x["end"] > x["start"])
    bad[candidate]["end"] -= 1
    results.append(rejected(lambda: pooled_replay(data, bad, slots),
                            "early_release", "release of nonzero buffer"))
    results.append(rejected(lambda: pooled_replay(data, plan, slots, dirty_slot=0),
                            "dirty_pool_entry", "allocation of dirty pool field"))
    # A real closing ADD coefficient is necessary, not merely its label/frame.
    closing = next(x for x in data["intervals"]
                   if data["events"][x["end"]-1][0] == "add")
    changed = copy.deepcopy(word)
    changed["cleanup"][closing["end"]-1][3] *= -1
    results.append(rejected(lambda: trace(changed, dual),
                            "closing_add_wrong_sign", "nonzero private field at cleanup exit"))
    # Re-enable a dropped read when its logical zero buffer is not allocated.
    step = next(i for i in data["omitted"] if data["events"][i-1][0] == "add"
                and data["events"][i-1][2] in data["buffers"]
                and not any(x["buffer"] == data["events"][i-1][2]
                            and x["start"] <= i <= x["end"] for x in plan))
    source = data["events"][step-1][2]
    results.append(rejected(lambda: pooled_replay(data, plan, slots, retained_zero_step=step),
                            "unallocated_zero_read", str(source)))
    # Same scratch-zero outcome is insufficient if the ordinary endpoint moves.
    changed = copy.deepcopy(word)
    j = next(i for i, g in enumerate(changed["cleanup"]) if g[0] == "warp")
    changed["cleanup"][j][2] *= -1
    changed_data = trace(changed, dual)
    check(any(changed_data["endpoint"][r] != data["endpoint"][r] for r in data["live"]),
          "warp-sign endpoint control did not change the map")
    results.append("inverse_warp_sign_changes_endpoint")
    return results


def distinct_witness(rows):
    """Small explicit entry values separating all operator-free peak rows."""
    check(all(not term[1] for _, row in rows for term in row), "peak still has warp symbols")
    variables = sorted({term[0] for _, row in rows for term in row})
    for seed in range(100):
        values = {r: int.from_bytes(hashlib.sha256(f"T74-pool/{seed}/{r}".encode()).digest()[:2],
                                    "big") - 32768 for r in variables}
        outputs = [sum((Fraction(q)*values[r] for r, _, q in row), Fraction(0))
                   for _, row in rows]
        if all(outputs) and len(set(outputs)) == len(rows):
            return dict(seed=seed,
                        input_rule="int.from_bytes(SHA256(UTF8('T74-pool/{seed}/{register}'))[:2], 'big') - 32768",
                        unused_inputs=0, max_input_abs=max(abs(x) for x in values.values()),
                        buffer_values=[[row[0], str(value)] for row, value in zip(rows, outputs)])
    raise ValueError("no small distinct-value witness")


def audit(word, dual):
    data = trace(word, dual)
    split_slots, _ = color(data["intervals"])
    slots, plan = color(hulls(data["intervals"]))
    check(slots == data["peak"], "interval clique/color mismatch")
    check(split_slots == slots, "splitting changes optimal capacity")
    digest = pooled_replay(data, plan, slots)
    controls = negative_controls(word, dual, data, plan, slots)
    zero_counts = Counter(data["events"][i-1][0] for i in data["omitted"])
    peak_values = [json.dumps(row[1]) for row in data["peak_rows"]]
    # Equal-value coalescing is outside interval allocation: do not turn a
    # simultaneous-live count into an unrestricted information lower bound.
    equal_groups = {}
    for row, value in zip(data["peak_rows"], peak_values):
        equal_groups.setdefault(value, []).append(row[0])
    witness = distinct_witness(data["peak_rows"]) if dual else None
    return dict(orientation="dual" if dual else "forward", events=len(data["events"]),
                entry_columns=len(data["live"]), private_buffers=len(data["buffers"]),
                pool_slots=slots, interval_count=len(data["intervals"]), intervals=data["intervals"],
                static_plan=plan, allocated_logical_buffers=len(plan),
                zero_noop_events=data["omitted"], peak_after_event=data["peak_event"],
                zero_noop_counts=dict(sorted(zero_counts.items())),
                retained_events=len(data["events"])-len(data["omitted"]),
                peak_buffers=data["peak_buffers"], endpoint_sha256=digest,
                peak_rows=data["peak_rows"],
                peak_distinct_values=len(equal_groups),
                peak_equal_value_groups=sorted(g for g in equal_groups.values() if len(g)>1),
                distinct_value_witness=witness,
                controls=controls)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="exclusive output path for the exact receipt")
    args = parser.parse_args()
    words = load_inputs()
    results = {name: [audit(word, dual) for dual in (False, True)] for name, word in words.items()}
    receipt = dict(schema_version=1, result="EXACT_LITERAL_INTERVAL_POOL", words=results)
    if args.write:
        with args.write.open("x") as output:
            json.dump(receipt, output, indent=2)
            output.write("\n")
    else:
        expected = json.loads((HERE / "EXPECTED.json").read_text())
        check(json.dumps(expected, sort_keys=True) == json.dumps(receipt, sort_keys=True),
              "stored certificate differs (including JSON types)")
    for name, orientations in results.items():
        for result in orientations:
            print(name, result["orientation"], "pool", result["pool_slots"],
                  "intervals", result["interval_count"], "zero_noops", len(result["zero_noop_events"]),
                  "peak", result["peak_after_event"])
    print("PASS_T74_CLEANUP_BUFFER_POOLING")


if __name__ == "__main__":
    main()
