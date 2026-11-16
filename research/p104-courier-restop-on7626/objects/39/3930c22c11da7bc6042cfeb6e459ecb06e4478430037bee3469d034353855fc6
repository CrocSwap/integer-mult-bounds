#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compare declared recursive invoices by exact signed concave order.

Usage: python3 -B scripts/compare_recursive_invoices.py OLD.json NEW.json

Each input has schema ``integer-mult-recursive-invoice/v1``, an identical
contract object with model, rank_semantics, ambient_rank and boundary, and
paid/targets objects mapping canonical positive decimal ranks to nonnegative
integer counts. Contracts are declarations, not verified mathematical premises.

For d = (new paid - old paid) - (new targets - old targets), set
K(k) = sum_r d[r] min(r,k). The sign of K at every support knot determines
the order for every increasing concave tariff f with f(0)=0. Indeed, on the
integer ranks 0..R, write s_j=f(j)-f(j-1). Then

  sum_r d[r] f(r) = s_R K(R) + sum_(k=1..R-1) (s_k-s_(k+1)) K(k).

All coefficients on the right are nonnegative. Conversely, the increasing
concave tariffs min(r,k) witness every required hinge. Between support knots
K is linear. For f(r)=r**t, 0<t<1, all the displayed slope coefficients are
positive, so a nonzero one-sided hinge certificate gives strict power order.
Other concave tariffs can give equality; the uniform classification is weak.

This is classical concave-order/majorization arithmetic, already used by
mightyOil's research/t16-moment-order-audit and its credited predecessors.
The new interface retains both paid jobs and surrendered target credits.
Prepared with substantial OpenAI Codex assistance. No new theorem is claimed.
"""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys


SCHEMA = "integer-mult-recursive-invoice/v1"
REPORT_SCHEMA = "integer-mult-recursive-invoice-comparison/v1"
MAX_BYTES = 1024 * 1024
MAX_SUPPORT = 4096
MAX_RANK = 10**9
MAX_COUNT = 10**60
MAX_TEXT = 4096
RANK_KEY = re.compile(r"[1-9][0-9]{0,9}\Z", re.ASCII)
CONTRACT_KEYS = {"model", "rank_semantics", "ambient_rank", "boundary"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _integer(text):
    # Check before int(): do not rely on a particular Python digit limit.
    digits = text.removeprefix("-")
    require(len(digits) <= 61, "integer token exceeds 61 digits")
    value = int(text)
    require(abs(value) <= MAX_COUNT, "integer token exceeds magnitude 10^60")
    return value


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON object key")
        result[key] = value
    return result


def _not_integer(_text):
    raise ValueError("floating-point and nonfinite JSON numbers are unsupported")


def validate_invoice(value, label="invoice"):
    """Validate and copy an invoice; remove zero counts, preserving string keys."""
    require(type(value) is dict, label + ": expected an object")
    require(value.keys() == {"schema", "contract", "paid", "targets"},
            label + ": expected exactly schema, contract, paid and targets")
    require(value["schema"] == SCHEMA, label + ": unsupported schema")
    contract = value["contract"]
    require(type(contract) is dict and contract.keys() == CONTRACT_KEYS,
            label + ": contract needs model, rank_semantics, ambient_rank and boundary")
    for key in ("model", "rank_semantics", "boundary"):
        item = contract[key]
        require(type(item) is str and 0 < len(item) <= MAX_TEXT and item.strip(),
                label + ": contract " + key + " must be a nonempty bounded string")
    ambient = contract["ambient_rank"]
    require(type(ambient) is int and 1 <= ambient <= MAX_RANK,
            label + ": ambient_rank must be an integer in 1..10^9")
    result = {"schema": SCHEMA, "contract": dict(contract)}
    for side in ("paid", "targets"):
        histogram = value[side]
        require(type(histogram) is dict and len(histogram) <= MAX_SUPPORT,
                label + ": " + side + " must have at most 4096 rank keys")
        clean = {}
        for key, count in histogram.items():
            require(type(key) is str and RANK_KEY.fullmatch(key) is not None,
                    label + ": " + side + " rank keys must be canonical positive decimals")
            rank = int(key)
            require(rank <= ambient, label + ": rank exceeds declared ambient_rank")
            require(type(count) is int and 0 <= count <= MAX_COUNT,
                    label + ": counts must be integers in 0..10^60")
            if count:
                clean[key] = count
        result[side] = dict(sorted(clean.items(), key=lambda item: int(item[0])))
    return result


def parse_invoice(raw, label="invoice"):
    require(type(raw) is bytes and len(raw) <= MAX_BYTES,
            label + ": input exceeds 1 MiB")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                           parse_int=_integer, parse_float=_not_integer,
                           parse_constant=_not_integer)
    except (UnicodeError, RecursionError) as exc:
        raise ValueError(label + ": invalid UTF-8 or excessive JSON nesting") from exc
    return validate_invoice(value, label)


def load_invoice(path):
    path = Path(path)
    with path.open("rb") as source:
        raw = source.read(MAX_BYTES + 1)
    invoice = parse_invoice(raw, str(path))
    return invoice, {"path": str(path), "sha256": sha256(raw).hexdigest(),
                     "bytes": len(raw)}


def _difference(new, old):
    ranks = sorted({int(r) for r in new} | {int(r) for r in old})
    return {str(r): new.get(str(r), 0) - old.get(str(r), 0) for r in ranks
            if new.get(str(r), 0) != old.get(str(r), 0)}


def _mass(histogram):
    return sum(int(rank) * count for rank, count in histogram.items())


def _masses(invoice):
    paid, targets = _mass(invoice["paid"]), _mass(invoice["targets"])
    return {"paid": paid, "targets": targets, "paid_minus_targets": paid - targets}


def compare_invoices(old, new):
    """Return exact arithmetic evidence; input correctness is a declared premise."""
    old, new = validate_invoice(old, "old"), validate_invoice(new, "new")
    require(old["contract"] == new["contract"], "declared invoice contracts differ")
    paid = _difference(new["paid"], old["paid"])
    targets = _difference(new["targets"], old["targets"])
    net = _difference(paid, targets)
    # A sparse sweep avoids both an ambient-rank array and a quadratic scan.
    hinges = [{"rank": 0, "value": 0}]
    prefix_mass, remaining_count = 0, sum(net.values())
    for rank, count in net.items():
        k = int(rank)
        prefix_mass += k * count
        remaining_count -= count
        hinges.append({"rank": k, "value": prefix_mass + k * remaining_count})
    values = [entry["value"] for entry in hinges]
    if not net:
        classification, power_sign = "equal", "identically_zero"
    elif all(value <= 0 for value in values):
        classification, power_sign = "uniformly_better", "strictly_negative"
    elif all(value >= 0 for value in values):
        classification, power_sign = "uniformly_worse", "strictly_positive"
    else:
        classification, power_sign = "inconclusive", "not_determined"
    old_mass, new_mass = _masses(old), _masses(new)
    return {
        "schema": REPORT_SCHEMA,
        "classification": classification,
        "contract": old["contract"],
        "delta_paid": paid,
        "delta_targets": targets,
        "signed_net_delta": net,
        "hinges": hinges,
        "rank_mass": {"old": old_mass, "new": new_mass,
                      "delta": {key: new_mass[key] - old_mass[key] for key in old_mass}},
        "quantity": "(new paid - new targets) - (old paid - old targets)",
        "tariff_class": "increasing concave f on nonnegative ranks, with f(0)=0",
        "uniform_order": "weak; some concave tariffs can give equality",
        "power_moment": {"tariff": "r^t", "exponent": "0 < t < 1",
                         "new_minus_old_sign": power_sign},
        "assurance": {
            "contract": "Exact matching user declarations; mathematical applicability is not verified.",
            "input_binding": "SHA-256 identifies the exact input bytes read, when loaded by this CLI.",
            "scope": "Histogram arithmetic only. Histogram correctness, circuit legality, ownership, "
                     "phases, precision, supplier admission and compiler endpoints are not validated.",
            "inconclusive": "Mixed hinge signs do not establish a power-moment crossing or failure.",
        },
        "method_credit": "Classical concave order/majorization; mightyOil's t16-moment-order-audit "
                         "and its retained predecessors. No new theorem claim.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("old", help="old invoice JSON")
    parser.add_argument("new", help="new invoice JSON")
    args = parser.parse_args(argv)
    try:
        old, old_evidence = load_invoice(args.old)
        new, new_evidence = load_invoice(args.new)
        report = compare_invoices(old, new)
        report["inputs"] = {"old": old_evidence, "new": new_evidence}
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        print(json.dumps({"status": "INVALID_RECURSIVE_INVOICE", "error": str(exc)},
                         ensure_ascii=True), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
