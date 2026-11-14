#!/usr/bin/env python3
"""Exact all-public one-relation price screen using paired main/full pivots.

This computes P∩H and each target residual online. It avoids storing native
history snapshots or performing a full helper-kernel echelon separately for
each target.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys


PACKAGE = Path(__file__).resolve().parents[1]
WORD_PATH = PACKAGE / "inputs/WORD.json.gz"
CALLER_PATH = PACKAGE / "inputs/CALLER.json"
INVOICE_PATH = PACKAGE / "inputs/CURRENT-PRICE.json"
WORD_SHA = "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9"
CALLER_SHA = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
INVOICE_SHA = "86f71ccbc923db5d7a6753aa971c3a9c8a572680534498ed17be072cfa2aae6b"


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def add(dst, src, factor=Q(1)):
    for coordinate, value in src.items():
        result = dst.get(coordinate, Q(0)) + factor * value
        if result:
            dst[coordinate] = result
        else:
            dst.pop(coordinate, None)


def reduce_row(row, basis):
    result = row.copy()
    for pivot in sorted(basis):
        if result.get(pivot):
            add(result, basis[pivot], -result[pivot])
    return result


def insert(basis, row):
    result = reduce_row(row, basis)
    if not result:
        return False
    pivot = min(result)
    scale = result[pivot]
    basis[pivot] = {coordinate: value / scale
                    for coordinate, value in result.items()}
    return True


def make_state():
    return {"image": {}, "lifts": {}, "kernel": {}, "kernel_support": set(),
            "observations": 0}


def insert_observation(state, row, mains, helpers):
    """Insert a full row while maintaining main projection and its kernel."""
    projected = {h: value for h, value in row.items() if h in mains}
    residual = row.copy()
    for pivot in sorted(state["image"]):
        coefficient = projected.get(pivot)
        if coefficient:
            add(projected, state["image"][pivot], -coefficient)
            add(residual, state["lifts"][pivot], -coefficient)
    if projected:
        pivot = min(projected)
        scale = projected[pivot]
        state["image"][pivot] = {h: value/scale for h, value in projected.items()}
        state["lifts"][pivot] = {h: value/scale for h, value in residual.items()}
    else:
        need(set(residual) <= helpers, "projection-kernel row has helper-only support")
        state["kernel_support"].update(residual)
        insert(state["kernel"], residual)
    state["observations"] += 1


def target_residual(state, row, mains, helpers):
    """Return projected residual and paired full residual for a target."""
    projected = {h: value for h, value in row.items() if h in mains}
    residual = row.copy()
    for pivot in sorted(state["image"]):
        coefficient = projected.get(pivot)
        if coefficient:
            add(projected, state["image"][pivot], -coefficient)
            add(residual, state["lifts"][pivot], -coefficient)
    if not projected:
        need(set(residual) <= helpers, "main-span residual is helper-only")
    return projected, residual


def span_key(frame):
    values = {0}
    for vector in frame:
        values |= {x ^ vector for x in tuple(values)}
    need(len(values) == 1 << len(frame), "every original frame is an independent basis")
    return frozenset(values)


def load_price_module():
    path = PACKAGE / "verifier/integer_prices.py"
    spec = importlib.util.spec_from_file_location("wave52_paired_integer_prices", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run():
    raw = WORD_PATH.read_bytes()
    need(sha256(raw).hexdigest() == WORD_SHA, "exact #7481 WORD bytes")
    word = json.loads(gzip.decompress(raw))
    payload = sha256(json.dumps(word, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    need(payload == "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8",
         "canonical #7481 native payload")
    spans = [span_key(frame) for frame in word["frames"]]
    dimensions = [len(frame) for frame in word["frames"]]
    for instruction in word["program"]:
        if instruction[0] == "MOVE":
            source, destination = instruction[2:4]
            need(spans[source] <= spans[destination] or
                 spans[destination] <= spans[source],
                 "every native MOVE frame pair is nested")
    public = word["public"]
    mains = (set(word["live"]) | {h + 112 for h in word["live"]} |
             set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"]))
    helpers = set(range(public)) - mains
    target_ranks = {h: abs(dimensions[word["initial"][h]] -
                           dimensions[word["final"][h]]) for h in helpers}
    for helper, rank in target_ranks.items():
        source, destination = word["initial"][helper], word["final"][helper]
        need(spans[source] <= spans[destination] or
             spans[destination] <= spans[source],
             "every helper entrance/final pair is nested")
        need(rank <= dimensions[source] + dimensions[destination],
             "helper rank is a finite chart dimension difference")
    states = {}

    def state_for(frame):
        return states.setdefault(spans[frame], make_state())

    rows = [{h: Q(1)} for h in range(public)] + [None] * word["owned_fields"]
    charts = list(word["initial"]) + [None] * word["owned_fields"]
    for owner, frame in enumerate(word["initial"]):
        insert_observation(state_for(frame), {owner: Q(1)}, mains, helpers)

    records = []
    helper_only_count = 0
    op_counts = Counter()
    for event, instruction in enumerate(word["program"]):
        opcode, owner = instruction[:2]
        op_counts[opcode] += 1
        if opcode == "MOVE":
            source, destination = instruction[2:4]
            need(rows[owner] is not None and charts[owner] == source,
                 "MOVE source lifecycle/frame")
            target = rows[owner].copy()
            state = state_for(destination)
            projected = {h: value for h, value in target.items() if h in mains}
            rank = abs(dimensions[source] - dimensions[destination])
            if not projected:
                helper_only_count += 1
            else:
                main_residual, helper_residual = target_residual(state, target, mains, helpers)
                if not main_residual and not instruction[4] and rank > 0:
                    full_miss = bool(reduce_row(helper_residual, state["kernel"]))
                    if full_miss:
                        support = state["kernel_support"] | set(helper_residual)
                        need(support, "one-cache relation support is nonempty")
                        minimum_rank = min(target_ranks[h] for h in support)
                        cheapest = min(h for h in support
                                       if target_ranks[h] == minimum_rank)
                        if helper_residual.get(cheapest):
                            relation_witness = helper_residual.copy()
                        else:
                            kernel_witness = next(row for row in state["kernel"].values()
                                                  if row.get(cheapest))
                            relation_witness = None
                            for scalar in (Q(1), Q(2)):
                                candidate = helper_residual.copy()
                                add(candidate, kernel_witness, scalar)
                                if candidate.get(cheapest):
                                    relation_witness = candidate
                                    break
                            need(relation_witness is not None,
                                 "can retain cheapest coordinate while leaving kernel")
                        need(bool(reduce_row(relation_witness, state["kernel"])),
                             "enabling witness is outside prior helper history")
                        need(set(relation_witness) <= helpers,
                             "enabling witness is helper-only")
                    else:
                        minimum_rank = None
                        relation_witness = None
                    records.append({"event": event, "owner": owner, "source": source,
                        "destination": destination, "target_rank": rank,
                        "full_history_miss": full_miss,
                        "prior_history_rank": len(state["image"]) + len(state["kernel"]),
                        "prior_helper_history_rank": len(state["kernel"]),
                        "minimum_enabling_relation_rank": minimum_rank,
                        "minimum_witness_support_size": (None if relation_witness is None
                                                          else len(relation_witness)),
                        "minimum_helper_coordinate": cheapest if full_miss else None})
            insert_observation(state, target, mains, helpers)
            rows[owner] = target
            charts[owner] = destination
        elif opcode == "INIT":
            need(owner >= public and charts[owner] is None and rows[owner] is None,
                 "owned INIT lifecycle")
            charts[owner], rows[owner] = instruction[2], {}
        elif opcode == "CLEAR":
            need(owner >= public and charts[owner] == instruction[2] and rows[owner] is not None,
                 "owned CLEAR lifecycle")
            charts[owner], rows[owner] = None, None
        elif opcode == "SCALE":
            need(charts[owner] == instruction[3] and rows[owner] is not None,
                 "SCALE frame")
            scale = Q(instruction[2])
            need(scale, "nonzero SCALE")
            rows[owner] = {h: scale * value for h, value in rows[owner].items()
                           if scale * value}
        elif opcode in ("ADD", "COPY"):
            donor = instruction[2]
            need(owner != donor and charts[owner] == charts[donor] == instruction[4],
                 "coframed scalar contact")
            if opcode == "COPY":
                need(owner >= public and not rows[owner], "COPY zero owned destination")
            add(rows[owner], rows[donor], Q(instruction[3]))
        else:
            raise AssertionError(f"unknown native opcode: {opcode}")
    need(charts == list(word["final"]) + [None] * word["owned_fields"],
         "final owner chart map")
    need(len([ins for ins in word["program"] if ins[0] == "MOVE"]) == 6279,
         "all 6,279 MOVE targets processed")
    need(helper_only_count == 468, "all 468 helper-only targets classified separately")

    price = load_price_module()
    caller_raw = CALLER_PATH.read_bytes()
    invoice_raw = INVOICE_PATH.read_bytes()
    need(sha256(caller_raw).hexdigest() == CALLER_SHA, "pinned caller")
    need(sha256(invoice_raw).hexdigest() == INVOICE_SHA, "pinned current price invoice")
    caller = json.loads(caller_raw)
    calls = sum(event[0] == "J" for event in caller["events"])
    need(calls == caller["stages"] == 17, "signed 17-call caller")
    invoice = json.loads(invoice_raw)
    need(invoice["new_native"] == payload, "complete invoice binds exact native payload")
    baseline = {int(rank): int(count) for rank, count in invoice["after"]["T"].items()}
    for rank, count in invoice["after"]["P"].items():
        baseline[int(rank)] = baseline.get(int(rank), 0) - int(count)
    baseline = {rank: count for rank, count in baseline.items() if count}
    baseline_moment = price.moment(baseline)
    required = (-baseline_moment[1] / calls, -baseline_moment[0] / calls)

    price_classes = Counter()
    miss_by_target_rank = Counter()
    full_hits = 0
    best = None
    for record in records:
        if not record["full_history_miss"]:
            full_hits += 1
            record["saving_0038"] = {"exact": ["0", "0"], "classification": "zero"}
            price_classes["zero_full_history_hit"] += 1
        else:
            miss_by_target_rank[record["target_rank"]] += 1
            profile = Counter({record["target_rank"]: 1})
            profile[record["minimum_enabling_relation_rank"]] -= 1
            saving = price.moment({rank: count for rank, count in profile.items() if count})
            record["saving_0038"] = price.display(saving)
            if saving[0] > 0:
                record["saving_0038"]["classification"] = "positive"
                price_classes["positive"] += 1
            elif saving[1] < 0:
                record["saving_0038"]["classification"] = "negative"
                price_classes["negative"] += 1
            else:
                record["saving_0038"]["classification"] = "zero_or_interval_overlap"
                price_classes["zero_or_interval_overlap"] += 1
            if best is None or saving[1] > best["saving_upper"]:
                best = {"event": record["event"], "target_rank": record["target_rank"],
                        "minimum_rank": record["minimum_enabling_relation_rank"],
                        "saving_lower": saving[0], "saving_upper": saving[1]}

    need(len(records) == 1066, "every positive-rank public main-history hit processed")
    result = {
        "status": "FRESH_EXACTQ_ALL_PUBLIC_SINGLE_RELATION_PRICE_SCREEN",
        "source_sha256": WORD_SHA,
        "source_payload_sha256": payload,
        "caller_sha256": CALLER_SHA,
        "invoice_sha256": INVOICE_SHA,
        "native_calls": calls,
        "move_count": 6279,
        "public_main_history_hit_count": len(records),
        "public_full_history_miss_count": len(records) - full_hits,
        "public_full_history_hit_count": full_hits,
        "public_full_history_miss_by_target_rank": dict(sorted(miss_by_target_rank.items())),
        "saving_class_counts": dict(sorted(price_classes.items())),
        "best_single_relation_saving": None if best is None else {
            "event": best["event"], "target_rank": best["target_rank"],
            "minimum_helper_target_rank": best["minimum_rank"],
            "exact_interval": [str(best["saving_lower"]), str(best["saving_upper"])],
            "beats_required_per_call": best["saving_lower"] > required[1]},
        "required_net_native_saving_per_call_0038": [str(x) for x in required],
        "baseline_full_signed_moment_0038": price.display(baseline_moment),
        "helper_only_move_count_separate": helper_only_count,
        "screen_method": "At each coframe keep a main-projection echelon with full-row lifts and the helper-only kernel of all prior native histories. For a main-history hit target c, paired reduction gives g=c-p in helpers; full-history miss iff g is outside P∩H. The new cache relation space is (P∩H)+span(g). Its support is the union of prior kernel support and g support, so the minimum one-row target debit is the minimum fixed target-rank among those helper coordinates. If the cheapest coordinate occurs only in P∩H, add its kernel vector to g, avoiding cancellation; the sum remains outside P∩H.",
        "scope_limits": "Fresh exhaustive exact screen of all #7481 public positive-rank main-history hits, under same-span normalized history pooling. Savings are optimistic rank-price only, one relation per target, and ignore public zero reframe availability, relation preparation, ordinary ADD/COPY/SCALE cost, precision/phase, storage and lifetime costs. No source extension, full system admission, or kappa gain is claimed.",
        "records": records,
    }
    return result
