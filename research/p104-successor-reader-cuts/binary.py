# SPDX-License-Identifier: Apache-2.0
"""Independent binary literal interpreter and fixed-endpoint ingress cuts."""

from collections import Counter, defaultdict
from functools import cache
from functools import reduce
from operator import xor

from common import Q, canonical, digest, parts, row_rank

BANK = 266
FIRST = 11
HELD = (740, 753)
COORDINATE = 252
PEERS = (326, 439, 457, 475, 493)


class Charts:
    def __init__(self, frames):
        self.frames = {int(i): {kind: [tuple(map(Q, r)) for r in v[kind]] for kind in ("A", "B")}
                       for i, v in frames.items()}
        for i, v in frames.items():
            data = self.frames[int(i)]
            rows = data["A"] + data["B"]
            assert len(data["B"]) == v["dim"] and len(rows) == 8 and all(len(r) == 8 for r in rows)
            assert self.orthogonal(data["B"], data["A"])
            assert row_rank({k: q for k, q in enumerate(r) if q} for r in rows) == 8

    @staticmethod
    def orthogonal(x, y):
        return all(sum(a * b for a, b in zip(u, v, strict=True)) == 0 for u in x for v in y)

    @cache
    def grade(self, a, b):
        x, y = sorted((self.frames[a], self.frames[b]), key=lambda row: len(row["B"]))
        n = len(y["B"]) - len(x["B"])
        assert n > 0 and self.orthogonal(x["B"], y["A"]), (a, b)
        return n


def tape(word, charts, adjoint=False):
    """Evaluate on independent original-input variables using local packet expressions."""
    n = word["public"]
    banks = n + word["owned_fields"]
    initial, final = word["start"], word["final"]
    if adjoint:
        initial, final = final, initial
    locations = list(initial) + [None] * (banks - n)
    slots = [1 << i for i in range(n)] + [0] * (banks - n)
    rows = {i: 1 << i for i in range(n)}
    routes = {}
    stock = defaultdict(list)
    demand = defaultdict(dict)
    for axis, chart in enumerate(initial):
        stock[chart].append(axis)
    clocks = range(len(word["program"]))
    erasures = 0
    counts = Counter()
    for clock in (reversed(clocks) if adjoint else clocks):
        op, a, *arg = word["program"][clock]
        counts[op] += 1
        if op in ("INIT", "CLEAR"):
            opening = (op == "INIT") != adjoint
            chart, = arg
            assert a >= n and chart in charts.frames and 0 <= a < banks
            if opening:
                assert locations[a] is None and not slots[a]
                locations[a] = chart
            else:
                assert locations[a] == chart
                erasures += bool(reduce(xor, (rows[k] for k in parts(slots[a])), 0))
                locations[a], slots[a] = None, 0
        elif op == "SWAP":
            b, = arg
            assert a != b and locations[a] is not None and locations[b] is not None
            slots[a], slots[b] = slots[b], slots[a]
            locations[a], locations[b] = locations[b], locations[a]
        elif op == "ADD":
            b, chart = arg
            assert a != b and locations[a] == locations[b] == chart
            if adjoint:
                slots[b] ^= slots[a]
            else:
                slots[a] ^= slots[b]
        else:
            assert a >= n and op == "MOVE"
            sender, receiver = arg[::-1] if adjoint else arg
            assert locations[a] == sender
            label = n + len(routes)
            routes[label] = (sender, receiver, clock, charts.grade(sender, receiver))
            assert set(parts(slots[a])) <= set(stock[sender])
            rows[label] = reduce(xor, (rows[k] for k in parts(slots[a])), 0)
            demand[sender][label] = slots[a]
            stock[receiver].append(label)
            locations[a], slots[a] = receiver, 1 << label
    assert locations == list(final) + [None] * (banks - n)
    assert n == 680 and not any(slots[n:])
    for axis, chart in enumerate(final):
        assert set(parts(slots[axis])) <= set(stock[chart])
        demand[chart][~axis] = slots[axis]
        rows[~axis] = reduce(xor, (rows[k] for k in parts(slots[axis])), 0)
        want = 1 << axis
        if adjoint and axis < 111:
            want ^= 1 << (axis + 111)
        if not adjoint and 111 <= axis < 222:
            want ^= 1 << (axis - 111)
        assert rows[~axis] == want
    assert erasures == word["owned_fields"]
    return rows, routes, stock, demand, counts


def quotient(references, wanted):
    basis = {}
    for word in references:
        while word:
            pivot = word.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = word
                break
            word ^= basis[pivot]
    for pivot in sorted(basis, reverse=True):
        if (wanted >> pivot) & 1:
            wanted ^= basis[pivot]
    return wanted


def cut(word, charts, forward, frozen, causal):
    rows, routes, stock, demand, counts = forward
    assert routes[3553] == (509, 1, 31290, 4)
    assert word["start"][411] == 509 and word["final"][411] == 1
    assert rows[3553] == rows[~411] == 1 << 411
    assert demand[509][3553] == 1 << 411 and demand[1][~411] == 1 << 3553
    assert routes[740] == (FIRST, BANK, 213, 3) and routes[753] == (13, BANK, 260, 3)
    assert list(parts(demand[FIRST][740])) == [9, 737] and rows[740] == (1 << 9) ^ (1 << 247)
    assert word["start"][9] == FIRST and routes[737][1] == FIRST and routes[737][2] < 213
    retained = [i for i in stock[BANK] if i not in HELD]
    assert retained == [1632, 1704, 1776, 1848]
    assert all(i in routes for i in stock[BANK])
    fixed = [rows[i] for i in retained]
    lines = [quotient(fixed, rows[i]) for i in HELD]
    assert [list(parts(r)) for r in lines] == [[9, 247], [11, 252]]
    assert list(quotient(fixed, r) for r in lines) == lines and lines[0] != lines[1]
    lines.append(lines[0] ^ lines[1])

    s8, = [case for case in causal["staged_hits"] if case["receiver"] == BANK and set(case["held"]) == set(HELD)]
    saved, = [trial for trial in s8["first_safe_with_optimistic_second"] if trial[2] == FIRST]
    assert saved[:4] == [1, 3, FIRST, [9, 737]]
    assert tuple(trial[2] for trial in saved[4]) == PEERS

    def coeff(label, axis=COORDINATE):
        return (rows[label] >> axis) & 1

    def packet(label):
        a, b, clock, g = routes[label]
        return {"label": label, "source": a, "target": b, "clock": clock, "grade": g,
                "input_coefficients": list(parts(rows[label])),
                "stock_coefficients": list(parts(demand[a][label]))}

    def downstream(label):
        chart = routes[label][1]
        uses = [i for i, local in demand[chart].items() if local >> label & 1]
        return {"chart": chart, "paid_packets": [i for i in uses if i >= 0],
                "public_outputs": [~i for i in uses if i < 0]}

    assert set(demand[BANK]) == set(range(1919, 1925))
    assert [packet(i) | {"immediate_readers": downstream(i)} for i in demand[BANK]] == frozen["receiver_original_readers"]
    assert [packet(i) for i in retained] == frozen["receiver_retained"]
    marked = [i for i in demand[BANK] if coeff(i)]
    assert marked == frozen["required_receiver_packets_with_nonzero_projection"] == [1919, 1921, 1922, 1923, 1924]

    cases = []
    for (which, grade, peer, donors), prior in zip(saved[4], frozen["cases"], strict=True):
        region = {BANK, peer}
        assert all(i in routes for i in stock[peer]) and charts.grade(peer, BANK) == grade == 2
        old_donor = reduce(xor, (rows[i] for i in donors), 0)
        assert old_donor >> COORDINATE & 1 and quotient(fixed, old_donor) == lines[which - 1]
        crossings = [i for i, (a, b, _, _) in routes.items()
                     if b in region and a not in region and i not in HELD]
        assert len(crossings) == 6 and not any(coeff(i) for i in crossings)
        assert {i: packet(i) for i in crossings} == {v["label"]: v for v in prior["outside_edges_into_cut"]}
        assert [packet(i) for i in stock[peer]] == prior["all_original_peer_ingresses"]
        assert [packet(i) for i in donors] == prior["donor_rows"]

        # Spend the one funded recode on a chosen crossing. Both replacement
        # sends enter the cut, and the recoded crossing also enters the cut.
        # Every arrival or initial row at its exterior producer stays fixed.
        # All of those rows vanish on input e252, even with unlimited retiming.
        producers = sorted({routes[i][0] for i in crossings})
        outside_stock = [{"chart": c, "stock_labels": stock[c], "nonzero_at_252": [
            i for i in stock[c] if coeff(i)]} for c in producers]
        assert all(not rec["nonzero_at_252"] for rec in outside_stock)
        assert outside_stock == prior["original_stocks_of_outside_producers"]
        assert all(routes[i][1] in region for i in (*crossings, *HELD))
        assert FIRST not in region and FIRST not in producers
        assert not coeff(740)
        # A recode ending at chart 11 leaves all six crossings fixed.
        # The new first send must still represent the stipulated line.
        required = [i for i in marked if routes[i][1] not in region]
        assert len(required) == 4 and required == prior["external_demands_at_252"]
        assert all(i not in HELD for i in required)
        exterior = [packet(i) | {"immediate_readers": downstream(i)} for i in demand[peer]]
        assert exterior == prior["original_peer_outputs"]
        cases.append({
            "inside": sorted(region), "route": [peer, BANK, grade],
            "original_donor": [packet(i) for i in donors],
            "crossings": [packet(i) for i in crossings],
            "recoded_crossing_producer_stock": outside_stock,
            "required_exterior_e252_rows": [packet(i) | {"immediate_readers": downstream(i)}
                                             for i in required],
            "minimum_preserved_nonzero_rows": len(required) - 1, "peer_outputs": exterior,
        })

    # A different coefficient already enters chart 507. Granting it a new
    # early e252 row also breaks the separating invariant on 2292.
    assert routes[1366][1] == routes[2292][0] == 507
    assert routes[1366][2] < routes[2292][2] and coeff(1366, 11) and not coeff(1366)
    assert 1366 in stock[507] and 2292 in stock[326]
    assert coeff(753) and not any(coeff(i) for i in stock[BANK] if i != 753)
    assert demand[326][2409] >> 2292 & 1
    assert not demand[326][2410] >> 2292 & 1
    assert routes[1366][1] not in {BANK, 326} and routes[2292][1] in {BANK, 326}
    injected = rows[1366] ^ (1 << COORDINATE)
    assert ((injected ^ rows[2292]) >> COORDINATE) & 1
    return {
        "held": [packet(i) for i in HELD], "receiver_readers": [packet(i) | {"immediate_readers": downstream(i)} for i in demand[BANK]],
        "quotient_generators": [list(parts(r)) for r in lines],
        "cases": cases,
        "bridge": packet(3553) | {"required_owner": 411, "immediate_readers": downstream(3553)},
        "controls": {
            "restored_753_ingress_at_e252": coeff(753),
            "edge_1366": packet(1366),
            "edge_2292": packet(2292),
            "e11_at_prior_chart507_stock_labels": [i for i in stock[507] if coeff(i, 11)],
            "e252_if_1366_receives_injected_unit": 1,
            "e252_if_2292_uses_injected_1366": 1,
            "limits": "Injecting an independent early row and recoding 2292 spends a second edit.",
        },
    }


def census(word, routes, charts, caller):
    calls = sum(item[0] == "LOCAL" for item in caller["events"])
    assert calls == 36 and (caller["roles"], caller["ports"], caller["stages"],
                            caller["body_rank"], caller["ambient_rank"]) == (38, 111, 18, 7, 127)
    for j in range(111):
        a, b = word["start"][j], word["final"][j + 111]
        assert len(charts.frames[a]["B"]) == 1 and len(charts.frames[b]["B"]) == 7
        assert not charts.frames[word["start"][j + 111]]["B"]
        assert len(charts.frames[word["final"][j]]["B"]) == 8
        assert charts.orthogonal(charts.frames[a]["B"], charts.frames[b]["B"])
    paid = Counter(grade for _, _, _, grade in routes.values())
    targets = Counter(charts.grade(a, b) for a, b in zip(word["start"][222:], word["final"][222:], strict=True))
    macro_events = Counter(row[0] for row in caller["events"])
    assert [row[1] for row in caller["events"] if row[0] == "LOCAL"] == sorted(list(range(1, 19)) * 2)
    ports = caller["ports"]
    fixed_paid = Counter({1: ports * macro_events["QUERY"]})
    for row in caller["events"]:
        if row[0] == "IDLE_ONE":
            assert len(set(row[2])) == len(row[2])
            fixed_paid[7 * len(row[2])] += ports
    fixed_targets = Counter()
    for owner in caller["diagonal"]:
        assert owner["q"] == 1 and len(set(owner["stages"])) == len(owner["stages"])
        fixed_targets[1 + 7 * len(owner["stages"])] += ports
    return calls, paid, targets, fixed_paid, fixed_targets, macro_events


def literal_ordinary(word, caller, counts, calls, paid, targets):
    ports = caller["ports"]
    public, owned = word["public"], word["owned_fields"]
    registers = public + owned + 4
    work = 16 * registers * len(word["program"])
    overhead = ports * (8 * (counts["ADD"] + 3 * counts["SWAP"]) +
                        256 * (calls + counts["QUERY"] + caller["roles"]))
    groups = 4 * (sum(paid.values()) + sum(targets.values())) + 8 * ports * (calls + counts["IDLE_ONE"])
    routed = groups * 80 * 134 * 135
    owned_all = (calls * (owned + 4) + 2 * ports * caller["roles"] * len(caller["events"])
                 + 16 * ports * (calls + counts["QUERY"] + caller["roles"]))
    return {
        "native_banks_and_scratch": registers, "native_bank_transits_per_call": work,
        "caller_bank_transits": overhead, "route_groups": groups, "route_records": routed,
        "ordinary_records": calls * work + overhead + routed, "owned_backing": owned_all,
        "raw_ordinary_allowance": 10**12, "raw_owned_allowance": 10**7,
    }
