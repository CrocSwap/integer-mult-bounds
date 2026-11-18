#!/usr/bin/env python3
"""Independently enclose the two raw-invoice crossings using decimal intervals."""

import argparse
from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR
from functools import cache
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PARENT = "1f082936ada08b5138b7d13e33368bd21c6f46632c5319a348e2f2a8e0021150"
CHILD = "d5dab11bb773bf5beb8ae2998be1282b243e2d1606c5257896a037c9b52c5c3b"
LO = Context(prec=65, rounding=ROUND_FLOOR)
HI = Context(prec=65, rounding=ROUND_CEILING)
NEAR = Context(prec=65)
ONE = Decimal(1)
ZERO = Decimal(0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


@cache
def logarithm(rank):
    if rank == 1:
        return ZERO, ZERO
    # Decimal.ln and .exp return correctly rounded nearest values. Widen by
    # one representable value on each side. The remaining operations below
    # are directed, with endpoint order reversed for negative multipliers.
    value = NEAR.ln(Decimal(rank))
    return NEAR.next_minus(value), NEAR.next_plus(value)


def raw_margin(interval, invoice, derivative=False):
    lower = upper = ZERO
    for name in sorted(invoice["paid"].keys() | invoice["targets"].keys(), key=int):
        rank = int(name)
        count = invoice["targets"].get(name, 0) - invoice["paid"].get(name, 0)
        a, b = logarithm(rank)
        if rank == 1:
            v = w = ONE
        else:
            left = LO.multiply(a, LO.subtract(ONE, interval[1]))
            right = HI.multiply(b, HI.subtract(ONE, interval[0]))
            v = NEAR.next_minus(NEAR.exp(left))
            w = NEAR.next_plus(NEAR.exp(right))
        if derivative:
            v, w = LO.multiply(a, v), HI.multiply(b, w)
            count = -count
        if count < 0:
            v, w = w, v
        lower = LO.add(lower, LO.multiply(count, v))
        upper = HI.add(upper, HI.multiply(count, w))
    return lower, upper


def root_bracket(invoice, left, right):
    def at(k):
        return raw_margin((k, k), invoice)

    require(at(left)[0] > 0 and at(right)[1] < 0, "outer bracket has strict opposite signs")
    derivative = raw_margin((left, right), invoice, derivative=True)
    require(derivative[1] < 0, "strict decrease throughout the tested interval")
    # Every midpoint and decimal grid point below is exactly representable.
    ticks = Decimal(10) ** 13
    a, b = int(left * ticks), int(right * ticks)
    while b - a > 1:
        m = (a + b) // 2
        lower, upper = at(Decimal(m) / ticks)
        if lower > 0:
            a = m
        elif upper < 0:
            b = m
        else:
            raise ValueError("unresolved sign at a grid point")
    return (Decimal(a) / ticks, Decimal(b) / ticks), derivative


def text_pair(interval):
    return [str(x) for x in interval]


def check(caller, claim):
    source = (HERE / "data" / "PARENT-INVOICES.json").read_bytes()
    require(hashlib.sha256(source).hexdigest() == caller["published_parent_invoice_sha256"],
            "source invoice hash")
    peer, child = (caller["invoices"][key] for key in ("peer", "candidate"))
    require(caller["graphs"] == {"peer": PARENT, "candidate": CHILD}
            and json.loads(source)["candidate"] == peer, "exact parent, child and invoice")
    require(peer["paid"] == child["paid"] and child["contract"] == peer["contract"],
            "all paid ranks and the price contract agree")
    changes = {r: child["targets"].get(r, 0) - peer["targets"].get(r, 0)
               for r in peer["targets"].keys() | child["targets"].keys()}
    require({r: v for r, v in changes.items() if v} == {"1": 16, "8": 16, "9": -16},
            "exact full signed target difference")
    left, right = Decimal("0.0037260"), Decimal("0.00376669")
    peer_bracket, peer_slope = root_bracket(peer, left, right)
    child_bracket, child_slope = root_bracket(child, left, right)
    require(peer_bracket == (Decimal("0.0037261023900"), Decimal("0.0037261023901")),
            "exact #7682 crossing bracket")
    require(peer_bracket[1] < claim <= child_bracket[0], "strict guarded gain")
    margin = raw_margin((claim, claim), child)
    at_peer = raw_margin((peer_bracket[1], peer_bracket[1]), child)
    control = dict(child, paid=dict(child["paid"]))
    control["paid"]["1"] += 1
    bad = raw_margin((claim, claim), control)
    require(margin[0] > 0 and at_peer[0] > 0 and bad[1] < 0, "two strict signs and fee control")
    return {
        "status": "PASS_INDEPENDENT_DIRECTED_PRICE",
        "parent_bracket": text_pair(peer_bracket), "child_bracket": text_pair(child_bracket),
        "strict_gain_above_parent_upper": str(claim - peer_bracket[1]),
        "claim": str(claim), "child_margin_at_claim": text_pair(margin),
        "child_margin_at_parent_upper": text_pair(at_peer),
        "one_extra_rank_one_at_claim": text_pair(bad),
        "derivative_domain": text_pair((left, right)),
        "derivatives": {"peer": text_pair(peer_slope), "child": text_pair(child_slope)},
        "candidate_graph_sha256": CHILD, "parent_graph_sha256": PARENT,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--caller", type=Path, required=True)
    parser.add_argument("--claim", type=Decimal, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    receipt = check(json.loads(args.caller.read_bytes()), args.claim)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(receipt["status"], receipt["strict_gain_above_parent_upper"])
