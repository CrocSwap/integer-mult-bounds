#!/usr/bin/env python3
"""Independent finite chart-595 owner-column, signed caller, and price checks."""

import argparse
from collections import Counter
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from math import prod
from pathlib import Path


HERE = Path(__file__).resolve().parent.parent
PARENT = "1f082936ada08b5138b7d13e33368bd21c6f46632c5319a348e2f2a8e0021150"
CHILD = "d5dab11bb773bf5beb8ae2998be1282b243e2d1606c5257896a037c9b52c5c3b"
CALLER = "62d94fb992acab0a71c3d12f22be4ce63f4f65e5cbe3f420b93aa1393ffa8dcf"
LAYOUT = "622c6f458eba2dab0fdfd6050303cbc16ad684ab8b834c7df568264e4cf01db6"
EDIT = "c8a914049eb36f5f307dfabef080169bbee06c024eab77b75249566028ca3fcf"
BASE_INVOICE = "a9aecf52d99d5370506b9dc6d03799241bebd2c03bbdcfa2dd5f45ec03c9d70d"
OLD_ROLE = 281
NEW_ROLE = 1501
GOAL = Fraction("0.00372611")


def require(predicate, reason):
    if not predicate:
        raise ValueError(reason)


def read(name, expected):
    path = HERE / name
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    require(sha256(raw).hexdigest() == expected, f"pinned {name}")
    return json.loads(raw)


def chart_ranks(frames):
    spans = []
    for basis in frames:
        span = {0}
        for vector in basis:
            require(vector not in span and 0 < vector < 512, "independent source chart")
            span.update({x ^ vector for x in span})
        spans.append(span)

    @cache
    def rank(a, b):
        require(spans[a] < spans[b] or spans[b] < spans[a], "positive nested pair")
        return abs(len(frames[a]) - len(frames[b]))

    return rank


def read_rows(graph, raw_forms):
    paid = {key: (source, end) for key, source, end in graph["moves"]}
    terminal_offset = graph["first_output"]
    records = {key: {donor: Fraction(q) for donor, q in facts} for key, facts in raw_forms}
    expected = paid.keys() | set(range(terminal_offset, terminal_offset + len(graph["final"])))
    schedule = graph["schedule"]
    require(len(expected) == len(records) == len(schedule) and set(schedule) == expected,
            "each paid and terminal row once")
    available = {~role: chart for role, chart in enumerate(graph["initial"])}
    for key in schedule:
        if key in paid:
            source, end = paid[key]
        else:
            source, end = graph["final"][key - terminal_offset], None
        require(all(available.get(donor) == source for donor in records[key]),
                f"available same-chart charged donor at {key}")
        if end is not None:
            available[key] = end
    return records


def evaluate(graph, records, inputs):
    held = {~r: Fraction(inputs.get(r, 0)) for r in range(len(graph["initial"]))}
    for key in graph["schedule"]:
        held[key] = sum((a * held[k] for k, a in records[key].items() if held[k]), Fraction())
    start = graph["first_output"]
    return {i: held[start + i] for i in range(len(graph["final"])) if held[start + i]}


def early_public_overwrite(graph, records, short_key, first_suffix):
    """Install into the short owner's actual public slot before running the suffix."""
    roster = {OLD_ROLE: Fraction(7), NEW_ROLE: Fraction(-11)}
    public = {r: (r, chart, roster.get(r, Fraction())) for r, chart in enumerate(graph["initial"])}
    held = {~r: field[2] for r, field in public.items()}
    old_entry = public[OLD_ROLE]
    short = (OLD_ROLE, 595, roster[OLD_ROLE])
    for position, key in enumerate(graph["schedule"]):
        held[key] = sum((a * held[k] for k, a in records[key].items() if held[k]), Fraction())
        if key == short_key:
            require(public[OLD_ROLE] == old_entry and held[key] == short[2], "complete short owner before install")
            public[OLD_ROLE] = (OLD_ROLE, graph["final"][OLD_ROLE], held[key])
            # A later use of even the old private entrance would now fail.
            del held[~OLD_ROLE]
        if position == first_suffix:
            require(public[OLD_ROLE] == short and public[OLD_ROLE] != old_entry
                    and ~OLD_ROLE not in held, "public chart changed before independent suffix")
    start = graph["first_output"]
    for r, chart in enumerate(graph["final"]):
        if r != OLD_ROLE:
            public[r] = (r, chart, held[start + r])
        require(public[r] == (r, chart, roster.get(r, Fraction())), f"early-install complete owner {r}")
    return {"early_same_owner_chart": public[OLD_ROLE][1], "fresh_same_owner_chart": public[NEW_ROLE][1],
            "distinct_signed_payloads": [str(public[r][2]) for r in (OLD_ROLE, NEW_ROLE)],
            "old_private_entry_removed_at_cut": True, "complete_owner_outputs_compared": len(public)}


def check_cut(parent, child, edit):
    require(len(parent["initial"]) == 1501 and len(child["initial"]) == 1502
            and parent["frames"] == child["frames"]
            and parent["moves"] == child["moves"] and len(child["moves"]) == 6142,
            "unchanged paid word and expanded public stock")
    require(parent["initial"] == child["initial"][:-1]
            and [r for r in range(1501) if parent["final"][r] != child["final"][r]] == [OLD_ROLE],
            "only declared public owner boundaries change")
    frames = child["initial"], child["final"]
    require([(frames[0][r], frames[1][r]) for r in (OLD_ROLE, NEW_ROLE)] == [(3, 595), (595, 127)],
            "separate same-owner endpoint charts")
    paid = {key for key, _, _ in child["moves"]}
    require([k for k in child["schedule"] if k in paid] ==
            [k for k in parent["schedule"] if k in paid], "same chronological paid order")
    records = read_rows(child, child["forms"])
    prefix = {k: Fraction(q) for k, q in edit["prefix"]}
    injection = {k: Fraction(q) for k, q in edit["injection"]}
    old_exit = child["first_output"] + OLD_ROLE
    position = {key: i for i, key in enumerate(child["schedule"])}
    first_suffix = min(position[k] for k in injection)
    require(records[old_exit] == prefix
            and max(position[k] for k in prefix) < position[old_exit] < first_suffix,
            "complete 281 output precedes fresh suffix")
    require({key: row[~NEW_ROLE] for key, row in records.items() if ~NEW_ROLE in row} == injection,
            "fresh owner is read solely in the ten suffix sends")
    handoff = {}
    for role in (OLD_ROLE, NEW_ROLE):
        observed = evaluate(child, records, {role: 1})
        require(observed == {role: 1}, f"complete normalized arbitrary owner column {role}")
        handoff[role] = {i: str(value) for i, value in observed.items()}

    separate_inputs = {OLD_ROLE: 0, NEW_ROLE: 1}
    aliased_inputs = {**separate_inputs, NEW_ROLE: separate_inputs[OLD_ROLE]}
    aliased = evaluate(child, records, aliased_inputs)
    require(aliased == {} and handoff[NEW_ROLE] == {NEW_ROLE: "1"},
            "copied instead of independent owner fails the y-only column")
    broken = records.copy()
    key = min(injection, key=position.get)
    broken[key] = records[key].copy()
    for donor, weight in prefix.items():
        broken[key][donor] = broken[key].get(donor, 0) + injection[key] * weight
    leaked = evaluate(child, broken, {OLD_ROLE: 1})
    require(leaked != {OLD_ROLE: 1}, "same-price omitted old-value correction fails")
    return {"early_terminal_position_zero_based": position[old_exit],
            "first_fresh_read_position_zero_based": first_suffix,
            "early_same_owner_overwrite_control": early_public_overwrite(child, records, old_exit, first_suffix),
            "private_entry_281_reads_after_commit": sum(
                ~OLD_ROLE in records[k] for k in child["schedule"][position[old_exit]+1:]),
            "independent_owner_columns": handoff,
            "aliased_fresh_column": {i: str(value) for i, value in aliased.items()},
            "omitted_old_value_injection_slot": key,
            "omission_different_roles": sorted(i for i in leaked.keys() | {OLD_ROLE}
                                                if leaked.get(i, 0) != (i == OLD_ROLE))}


def recount(graph, tape, layout, rank):
    main = set(layout["live"])
    main.update(r + 112 for r in layout["live"])
    main.update(layout["hosted"]["X2"])
    main.update(layout["hosted"]["Y2"])
    require(len(main) == 400, "four hundred actual native main slots")
    types = tape["types"]
    require(set(types["A"]["ports"]).isdisjoint(types["B"]["ports"])
            and (len(types["A"]["ports"]), len(types["B"]["ports"])) == (96, 8),
            "disjoint actual port types")
    stages = [e[1] for e in tape["events"] if e[0] == "J"]
    require(stages == list(range(1, 17)) and tape["ambient_rank"] == 137, "literal signed stages")
    paid = Counter(rank(a, b) for _, a, b in graph["moves"])
    target = Counter(rank(a, b) for r, (a, b) in enumerate(zip(graph["initial"], graph["final"], strict=True))
                     if r not in main)
    paid = Counter({r: len(stages) * n for r, n in paid.items()})
    target = Counter({r: len(stages) * n for r, n in target.items()})
    for kind, instruction, *args in tape["events"]:
        if kind == "J":
            continue
        multiplier = len(types[kind]["ports"])
        if instruction == "QUERY":
            paid[1] += multiplier
        elif instruction.startswith("IDLE_"):
            paid[8*len(args[1]) + (instruction == "IDLE_ODD")] += multiplier
    root_owners = set()
    for spec in types.values():
        for j, (phase, coeff_phase, *axes) in enumerate(spec["diagonal"]):
            require(len(axes) == 16 and set(axes) <= {0, 1} and coeff_phase == 0,
                    "literal squarefree root target")
            target[8 * sum(axes) + (phase % 2)] += len(spec["ports"])
            root_owners.update((port, spec["offset"] + j) for port in spec["ports"])
    helpers = {(stage, r) for stage in stages for r in range(len(graph["initial"])) if r not in main}
    require(len(root_owners) == 3536 and len(helpers) + len(root_owners) == sum(target.values()),
            "distinct native helper tags and root owners")
    return paid, target, len(helpers)


def signed_sectors(tape):
    prime = 1000000009
    candidates = [pow(base, (prime - 1) // 4, prime) for base in range(2, 16)]
    imaginary = next(q for q in candidates if q*q % prime == prime - 1)
    inverse_two = pow(2, -1, prime)
    body = {i: 7 + 2*i for i in range(1, 17)}
    width = tape["roles"]
    weights = {}

    def linear(a, b, coefficient):
        return [(x + coefficient*y) % prime for x, y in zip(a, b, strict=True)]

    def scaled(row, amount):
        return [x * amount % prime for x in row]

    for q in (1, prime-1, imaginary, prime-imaginary):
        q_inverse = pow(q, -1, prime)
        rows = [[int(i == j) for j in range(width)] for i in range(width)]
        for event in tape["events"]:
            if event[0] == "J":
                _, stage, (x, y, u, v), (a, b, alpha, beta) = event
                require(alpha == "-1" and beta == "1/2"
                        and len({x, y, u, v, a, b}) == 6, "actual J signs and distinct lanes")
                rows[y] = linear(rows[y], rows[x], q_inverse)
                rows[u] = linear(rows[u], rows[v], -q)
                left, right = rows[a], rows[b]
                rows[a] = linear(left, right, -q)
                rows[b] = scaled(linear(right, left, q_inverse), inverse_two)
                for k in (x, y, u, v, a, b):
                    rows[k] = scaled(rows[k], body[stage])
                continue
            _, op, r, *args = event
            if op == "SWAP":
                s = args[0]
                rows[r], rows[s] = rows[s], rows[r]
            elif op == "QUERY":
                s, phase = args
                rows[r] = linear(rows[r], rows[s], pow(q, phase, prime))
            elif op in ("ADD", "SCALE"):
                c = Fraction(args[-1])
                amount = c.numerator * pow(c.denominator, -1, prime) % prime
                if op == "ADD":
                    rows[r] = linear(rows[r], rows[args[0]], amount)
                else:
                    rows[r] = scaled(rows[r], amount)
            elif op == "LAMBDA":
                phase = args[0]
                amount = (1 + imaginary*phase) + (1 - imaginary*phase) * q*q
                rows[r] = scaled(rows[r], amount*inverse_two)
            elif op == "IDLE_ONE":
                rows[r] = scaled(rows[r], prod(body[i] for i in args[0]))
            elif op == "IDLE_ODD":
                rows[r] = scaled(rows[r], prod(body[i] for i in args[0]) * pow(q, args[1], prime))
            else:
                raise ValueError(f"unknown signed caller operation {op}")
        for spec in tape["types"].values():
            for index, (phase, _, *axes) in enumerate(spec["diagonal"]):
                r = spec["offset"] + index
                expected = pow(q, phase, prime) * prod(body[i] for i, on in enumerate(axes, 1) if on)
                require(rows[r] == [expected % prime if r == j else 0 for j in range(width)],
                        f"full signed sector {q} row {r}")
        weights[q] = sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()
    return {"prime": prime, "body_fixture": body, "phi": imaginary, "q_sector_output_hashes": weights,
            "complete_rows_per_sector": width}


def log_term(z):
    # 2*atanh(z), with a geometric upper bound on the remaining denominator-weighted terms.
    terms = 28
    low = 2 * sum((z ** (2*j+1) / (2*j+1) for j in range(terms)), Fraction())
    high = low + 2 * z ** (2*terms+1) / ((2*terms+1)*(1-z*z))
    return low, high


@cache
def log_rank(rank):
    power = rank.bit_length() - 1
    mantissa = Fraction(rank, 1 << power)
    lo, hi = log_term((mantissa - 1) / (mantissa + 1))
    l2, h2 = log_term(Fraction(1, 3))
    return lo + power*l2, hi + power*h2


def alternating_exp(x):
    require(0 <= x < 1, "alternating exponential in decreasing range")
    term = total = Fraction(1)
    for n in range(1, 20):
        term *= -x/n
        total += term
    return total, total-term


@cache
def weight(rank, point):
    lo, hi = log_rank(rank)
    lower = rank * alternating_exp(point*hi)[0]
    upper = rank * alternating_exp(point*lo)[1]
    # Keep exact intervals portable without serializing huge intermediate denominators.
    denominator = 1 << 160
    lower_tick = (lower.numerator * denominator) // lower.denominator
    negative_upper_tick = (-upper.numerator * denominator) // upper.denominator
    return Fraction(lower_tick, denominator), Fraction(-negative_upper_tick, denominator)


def moment(paid, targets, point):
    lower = upper = Fraction()
    for rank in paid.keys() | targets.keys():
        coefficient = targets[rank] - paid[rank]
        lo, hi = weight(rank, point)
        a, b = sorted((coefficient*lo, coefficient*hi))
        lower += a
        upper += b
    return lower, upper


def bill(invoice):
    return tuple(Counter({int(k): value for k, value in invoice[name].items()})
                 for name in ("paid", "targets"))


def endpoint_certificate(outer, parent_bill, child_bill):
    require(outer["graphs"] == {"candidate": CHILD, "peer": PARENT}
            and outer["caller_sha256"] == CALLER, "frozen joined outer inputs")
    claim = Fraction(outer["candidate_directed_conditional_lower"])
    peer_upper = Fraction(outer["published_peer_upper"])
    lo, hi = map(Fraction, outer["candidate_raw_bracket"])
    require(peer_upper < GOAL <= claim < lo < hi < 1, "literal comparator and candidate order")
    cases = {
        "peer_on_peer_upper": (parent_bill, peer_upper, -1),
        "child_on_claim": (child_bill, claim, 1),
        "child_on_raw_lower": (child_bill, lo, 1),
        "child_on_raw_upper": (child_bill, hi, -1),
    }
    result = {}
    for name, ((p, t), point, sign) in cases.items():
        bounds = moment(p, t, point)
        require(bounds[0] > 0 if sign > 0 else bounds[1] < 0, f"independent directed sign {name}")
        result[name] = {"point": str(point), "bounds": list(map(str, bounds)),
                        "decimal_for_readback": list(map(float, bounds))}
    return result


def check_price(parent, child, tape, layout, caller_receipt, outer):
    rank = chart_ranks(child["frames"])
    p0, t0, h0 = recount(parent, tape, layout, rank)
    p1, t1, h1 = recount(child, tape, layout, rank)
    original = read("data/PARENT-INVOICES.json", BASE_INVOICE)
    require((p0, t0) == bill(original["candidate"]), "independent literal parent recensus")
    require(caller_receipt["graphs"]["candidate"] == CHILD and caller_receipt["caller_sha256"] == CALLER
            and (p1, t1) == bill(caller_receipt["invoices"]["candidate"]),
            "independent literal child agrees with the signed caller run")
    changed = t1.copy()
    changed.subtract(t0)
    require(p0 == p1 and {r: n for r, n in changed.items() if n} == {1: 16, 8: 16, 9: -16},
            "only the signed 16-call split")
    require((sum(p1.values()), sum(t1.values()), h0, h1) == (101824, 21168, 17616, 17632),
            "complete distinct productive census")
    k = GOAL
    old = moment(p0, t0, k)
    candidate = moment(p1, t1, k)
    fee_paid = p1.copy()
    fee_paid[1] += 1
    lost_credit = t1.copy()
    lost_credit[1] -= 1
    fee = moment(fee_paid, t1, k)
    lost = moment(p1, lost_credit, k)
    require(old[1] < 0 < candidate[0] and fee == lost and fee[1] < 0,
            "both one-rank-one failure modes reject the threshold")
    ranges = {"parent": old, "candidate": candidate, "one_paid_rank_one_added": fee,
              "one_rank_one_productive_credit_withdrawn": lost}
    result = {"point": str(k), "ranges": {k: list(map(str, v)) for k, v in ranges.items()},
              "ranges_decimal_for_readback": {k: list(map(float, v)) for k, v in ranges.items()},
              "native_helpers_parent": h0, "native_helpers_child": h1, "whole_paid_child": sum(p1.values()),
              "whole_targets_child": sum(t1.values()), "paid": p1, "targets": t1}
    if outer is not None:
        result["outer_receipt_endpoint_signs"] = endpoint_certificate(outer, (p0, t0), (p1, t1))
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--caller-receipt", type=Path, required=True)
    ap.add_argument("--outer-receipt", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    p = read("data/PARENT-GRAPH.json.gz", PARENT)
    c = read("data/CANDIDATE-GRAPH.json.gz", CHILD)
    tape = read("data/CALLER.json.gz", CALLER)
    layout = read("data/CALLER-LAYOUT.json", LAYOUT)
    edit = read("EDIT.json", EDIT)
    receipt = args.caller_receipt.read_bytes()
    outer = args.outer_receipt.read_bytes() if args.outer_receipt else None
    result = {
        "status": "PASS_INDEPENDENT_CUT_SECTORS_AND_DIRECTED_PRICE_CONTROL",
        "candidate_graph": CHILD, "parent_graph": PARENT, "signed_caller": CALLER,
        "actual_signed_caller_receipt_sha256": sha256(receipt).hexdigest(),
        "owner_columns_and_timing": check_cut(p, c, edit),
        "signed_sector_evaluations": signed_sectors(tape),
        "price": check_price(p, c, tape, layout, json.loads(receipt), json.loads(outer) if outer else None),
    }
    if outer:
        result["joined_outer_receipt_sha256"] = sha256(outer).hexdigest()
    with args.out.open("x") as out:
        json.dump(result, out, sort_keys=True, indent=2)
        out.write("\n")
    print(result["status"])


if __name__ == "__main__":
    main()
