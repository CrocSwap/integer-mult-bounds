#!/usr/bin/env python3
"""Exact parameter certificate and finite schedule model for direct axis swaps.

The primitives below model the completed permutations of upstream lemmas.
They do not implement those lemmas on tapes or certify their time bounds.
"""
from dataclasses import replace
from fractions import Fraction as Q
import json
from pathlib import Path

from certify import (balanced, certify_network, certify_parameters, certify_rational_network,
                     constraints, dyadic, margins, pushed, require, verify_sources)

ROOT = Path(__file__).resolve().parents[1]


def parameters(network="h46"):
    require(network in ("h46", "frozen"), "Unknown network")
    base = pushed("109") if network == "h46" else balanced(50)
    return replace(base, epsilon=Q(1, 40), kappa=dyadic(78 if network == "h46" else 107))


def certificate():
    result = {"upstream_commit": verify_sources(),
              "scope": "Conditional on upstream swap/stream interfaces and the direct-axis scheduling proof",
              "layout_model": "nonadjacent",
              "network_certificates": {"h46": certify_rational_network(),
                                       "frozen": certify_network(100, 50, 20)}, "cases": {}}
    for name in ("h46", "frozen"):
        p = parameters(name)
        cert = certify_parameters(p, strict_margin=True, layout_model="nonadjacent")
        old = constraints(p)["crt_layout"]
        require(old < 0, "Witness should expose the old layout obstruction")
        a = 1-p.tau
        gs = margins(p, layout_model="nonadjacent")
        require(gs["g2"] == gs["g3"] == min(gs.values()) == a*a/80,
                "Unexpected limiting margin")
        require(gs["g4"] == 39*a/40, "Wrong new layout margin")
        cert["rejected_adjacent_layout_slack"] = str(old)
        cert["remaining_exponents"] = {
            "dimension": "1/40", "ell": "39/40", "guard": "1/2",
            "alpha": "21/80", "gamma": "11/20", "prime_interval": "19/20",
            "chunk_width": str(p.epsilon*p.c),
        }
        result["cases"][name] = cert
    return result


def apply_primitive(items, operation):
    """Apply a completed equal-width swap or single-digit move to named slots."""
    out = list(items)
    kind, left, right, width = operation
    if kind == "swap":
        require(width >= 0 and left+width <= right, "Overlapping chunks")
        out[left:left+width], out[right:right+width] = (
            out[right:right+width], out[left:left+width])
    elif kind == "move":
        require(width == 1, "Only a single digit may be moved")
        out.insert(right, out.pop(left))
    else:
        raise ValueError("Unknown primitive")
    return out


def swap_schedule(widths, first, second):
    """Swap two complete axis fields using the upstream one-bit-mismatch schedule.

    Positions refer to the current bit-slot list. A move's destination is its
    final index, after removing its source. Zero-width singleton axes are allowed.
    """
    require(all(isinstance(w, int) and w >= 0 for w in widths), "Invalid widths")
    require(0 <= first < len(widths) and 0 <= second < len(widths), "Invalid axes")
    if first == second:
        return []
    i, j = sorted((first, second))
    wi, wj = widths[i], widths[j]
    require(abs(wi-wj) <= 1, "Widths must differ by at most one")
    left, right = sum(widths[:i]), sum(widths[:j])
    if wi == wj:
        return [("swap", left, right, wi)] if wi else []
    if wi == wj+1:
        # e x G y -> e y G x -> y G e x
        return ([("swap", left+1, right, wj)] if wj else []) + [
            ("move", left, right-1, 1)]
    # x G e y -> e x G y -> e y G x
    return [("move", right, left, 1)] + (
        [("swap", left+1, right+1, wi)] if wi else [])


def inverse_schedule(schedule):
    return [(kind, right, left, width) if kind == "move" else (kind, left, right, width)
            for kind, left, right, width in reversed(schedule)]


def permute_records(records, widths, schedule):
    """Finite reference model; each payload record is carried intact."""
    bits = sum(widths)
    require(len(records) == 1 << bits, "Expected the full padded address box")
    missing = object()
    out = [missing]*len(records)
    for address, record in enumerate(records):
        digits = [(address >> j) & 1 for j in reversed(range(bits))]
        for operation in schedule:
            digits = apply_primitive(digits, operation)
        target = 0
        for digit in digits:
            target = 2*target+digit
        require(out[target] is missing, "Schedule is not a permutation")
        out[target] = record
    return out


if __name__ == "__main__":
    result = certificate()
    target = ROOT / "certificates/nonadjacent-axis.json"
    target.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    for name, case in result["cases"].items():
        print(f"PASS nonadjacent {name}: kappa={case['parameters']['kappa']}, minimum={case['minimum_margin']}")
