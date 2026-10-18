#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compose the literal T148 journal with R1 and certify its complete invoice.

Geometry and directed moment kernels are retained, not independent new checks.
Python allocation is bounded by 1332 calls, 543456 roles and 298368 bins.
"""

import argparse
import gzip
import hashlib
import json
import types
from collections import Counter
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = ROOT / "research/rank7-joint-endframes/allocation"
DELTA = {1: 4, 3: 4, 5: -4, 14: -2, 32: 1}
BASELINE = {1: 1644352, 2: 470862, 3: 159472, 4: 71928,
            5: 13710, 8: 5328, 14: 1, 48: 28190}
EXPECTED = {1: 3288708, 2: 941724, 3: 318948, 4: 143856,
            5: 27416, 8: 10656, 32: 1, 48: 56380}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    raw = path.read_bytes()
    need(len(raw) <= 20_000_000, "compressed input bound")
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    need(len(raw) <= 60_000_000, "decoded input bound")
    return json.loads(raw)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def authenticate(root=ROOT, package=PACKAGE):
    rows = [(root, row) for row in read(package / "SOURCES.json")["files"]
            if row["usage"] == "input"]
    rows += [(package, row) for row in read(package / "VENDOR.json")]
    need(1 <= len(rows) <= 32, "input count")
    for base, row in rows:
        name = Path(row["path"])
        need(not name.is_absolute() and ".." not in name.parts, "input path")
        need(digest(base / name) == row["sha256"], "source drift: " + str(name))


def retained(name):
    authenticate()
    need(name in ("geometry", "moment", "release_driver"), "retained module name")
    path = PACKAGE / "vendor" / (name + ".py")
    module = types.ModuleType("t148_" + name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def apply(fill, journal, count):
    rows = list(fill["rows"])
    edits, seen = journal["edits"], set()
    need(type(edits) is list and len(edits) == count <= 128, "exact journal count")
    for index, before, after in edits:
        need(type(index) is int and 0 <= index < len(rows), "journal index")
        need(index not in seen and rows[index] == before, "literal journal preimage")
        need(len(before) == len(after) == 6 and before[:2] == after[:2], "role identity")
        seen.add(index)
        rows[index] = after
    return {**fill, "rows": rows}


def allocation():
    authenticate()
    order = read(SOURCE / "ORDER.json")
    dispatch = read(SOURCE / "DISPATCH.json")
    fill = apply(read(SOURCE / "FILL.json.gz"),
                 read(PACKAGE / "vendor/PR3018-EXCHANGE.json"), 103)
    need(len(order) == len(dispatch) == 666 and len(fill["rows"]) == 271728,
         "T74 input counts")
    need(not fill.get("dispatch_overrides"), "no implicit dispatch overrides")
    order2 = [[stage, owner + 74 * copy] for stage, owner in order for copy in range(2)]
    dispatch2 = [[stage, owner + 74 * copy, provider]
                 for stage, owner, provider in dispatch for copy in range(2)]
    rows = [[2 * time + copy, helper, owner + 74 * copy, child, port, offset]
            for time, helper, owner, child, port, offset in fill["rows"] for copy in range(2)]
    parent = {**fill, "rows": rows}
    candidate = apply(parent, read(PACKAGE / "vendor/PR3022-EXCHANGE.json"), 86)
    return order, fill, dispatch, order2, parent, candidate, dispatch2


def root(profile, replicas, moment):
    need(replicas in (74, 148), "replica domain")
    need(sum(r * n for r, n in profile.items()) == 65088 * replicas, "complete rank mass")
    threshold = 73 * 896 * replicas * moment.SCALE
    low, high = 0, moment.GRID // 100
    need(moment.moment_numerator(profile, Fraction(0))[1] < threshold, "lower root sign")
    need(moment.moment_numerator(profile, Fraction(1, 100))[0] > threshold, "upper root sign")
    for _ in range(moment.GRID.bit_length()):
        if high - low == 1:
            return Fraction(low, moment.GRID), Fraction(high, moment.GRID)
        middle = (low + high) // 2
        lower, upper = moment.moment_numerator(profile, Fraction(middle, moment.GRID))
        if upper < threshold:
            low = middle
        elif lower > threshold:
            high = middle
        else:
            raise ValueError("interval precision exhausted")
    raise ValueError("bisection bound exhausted")


def stock(replicas):
    need(replicas in (74, 148), "stock replica domain")
    group = 2**1296
    for j in range(1, 37):
        group *= 2**(2 * j) - 1
    physical = 896 * replicas + 408 + 8 + 91 + 2
    bits = (group * physical).bit_length()
    l2 = (bits + 1) // 2
    reserve = 128 + 37 + 18 + l2 + 1 + 4
    need(physical <= 2**20 and l2 <= 1330 and reserve < 2048, "full stock/prefix budget")
    return dict(physical=physical, physical_stock_bits=bits, stock_l2_bits=l2,
                required_reserve_bits=reserve, retained_payload_bits=2048,
                active_depth=18, calls=9 * replicas, bridges=9 * replicas)


def check_invoice(invoice, finite):
    need(invoice["status"] == "PASS_INDEPENDENT_MIXED_ASYNC_SCALAR_PREFIX_AND_FINITE_INVOICE",
         "actual complete prefix invoice")
    expected = finite["stock148"]
    need(invoice["physical"] == expected["physical"] and invoice["live"] == 132608,
         "actual complete physical stock")
    need(invoice["private_zero_buffers"] == 91 and invoice["helpers"] == 408 and
         invoice["centres"] == 8, "all private work charged")
    need(invoice["complete_invocation_sweeps"] == invoice["bridge_sweeps"] == 1332,
         "all doubled sweeps charged")
    bn = invoice["blocknorm"]
    need(bn["status"] == "PASS_TENSOR_BLOCK_NORM_CERTIFICATE" and bn["replicas"] == 148,
         "actual block certificate")
    for key in ("physical_stock_bits", "stock_l2_bits", "required_reserve_bits", "retained_payload_bits"):
        need(bn[key] == expected[key], "actual T-dependent bound: " + key)
    need(bn["physical_families"] == expected["physical"] and bn["max_active_depth"] == 18,
         "physical schedule and completed-event depth")
    local = bn["local_actual_prefix_bits"]
    need(local <= 128 and invoice["charged_prefix_bits"] == 2048, "actual native prefix reserve")
    need(invoice["global_prefix_bits"] == bn["actual_prefix_bits"] ==
         local + 37 + 18 + bn["stock_l2_bits"] + 1 + 4, "actual charged prefix sum")


def general_ceiling(moment, actual_local):
    certificate = read(PACKAGE / "GENERAL-CEILING.json")
    need(certificate["local_profile"] == actual_local, "generic cap actual paid profile")
    local = {int(r): n for r, n in actual_local.items()}
    idle_mass = 65088 - 9 * sum(r * n for r, n in local.items())
    need(idle_mass > 0 and 2 * 51**2 < 73**2, "generic coverage/halving model")
    # Scale the fractional rank-51 relaxation by 51, leaving integer counts.
    profile = {r: 51 * 9 * n for r, n in local.items()}
    profile[51] = idle_mass
    threshold = 73 * 896 * 51 * moment.SCALE
    low, high = map(Fraction, certificate["primitive_saving_cap"])
    need(moment.moment_numerator(profile, low)[1] < threshold, "generic cap lower sign")
    need(moment.moment_numerator(profile, high)[0] > threshold, "generic cap upper sign")
    return low, high


def run():
    geometry, moment = retained("geometry"), retained("moment")
    order, fill, dispatch, order2, parent, candidate, dispatch2 = allocation()
    plan, template = read(SOURCE / "vendor/PLAN.json.gz"), read(SOURCE / "vendor/TEMPLATE.json.gz")
    providers = read(PACKAGE / "vendor/pr3015/PROVIDERS.json")
    data = [(order, fill, dispatch), (order2, parent, dispatch2), (order2, candidate, dispatch2)]
    invoices = []
    for calls, roles, routes in data:
        mapping = {(stage, owner): name for stage, owner, name in routes}
        need(len(mapping) == len(calls), "unique dispatch")
        invoices.append(geometry.check(calls, roles, mapping, plan, template, providers))
    need(invoices[0]["profile"] == BASELINE, "PR3021 baseline with edited providers")
    need(invoices[1]["profile"] == {r: 2 * n for r, n in BASELINE.items()}, "exact double")
    need(invoices[2]["profile"] == EXPECTED, "complete T148 edited invoice")
    difference = Counter(EXPECTED)
    difference.subtract(invoices[1]["profile"])
    need({r: n for r, n in difference.items() if n} == DELTA, "complete journal delta")
    old, new = root(BASELINE, 74, moment), root(EXPECTED, 148, moment)
    need(old[1] < new[0], "strict complete moment gain")
    previous = Fraction(read(PACKAGE / "vendor/PR3021-RESULT.json")["kappa"])
    need(previous < old[0], "published PR3021 comparator below its root")
    cap = read(PACKAGE / "vendor/pr3015/RELAX-CAP.json")
    for tag in ("base", "extra"):
        word = read(PACKAGE / ("vendor/pr3015/FINAL-WORD-" + tag + ".json.gz"))
        need(word["report"]["local_profile"] == cap["local_per_call"] and
             word["report"]["width_inventory"] == cap["inventory_per_call"], "cap source profile")
    cap_low, cap_high = Fraction(cap["cap_lower"]), Fraction(cap["cap_upper"])
    need(new[1] < cap_low < cap_high, "below inherited fixed-inventory packing cap")
    generic = general_ceiling(moment, cap["local_per_call"])
    need(cap_high < generic[0], "capacity-specific cap is tighter")
    return dict(status="PASS_T148_R1_FINITE", profile=EXPECTED, delta=DELTA,
                general_packing_cap=list(map(str, generic)),
                realized_fraction_of_general_cap=str(new[0] / generic[1]),
                inherited_packing_cap=[str(cap_low), str(cap_high)],
                realized_fraction_of_cap=str(new[0] / cap_high),
                gap_to_cap=[str(cap_low - new[1]), str(cap_high - new[0])],
                baseline_root=list(map(str, old)), new_root=list(map(str, new)),
                root_gain=[str(new[0] - old[1]), str(new[1] - old[0])],
                comparison_kappa=str(previous), roles=543456, private_buffers=91,
                stock74=stock(74), stock148=stock(148),
                fill_payload_sha256=hashlib.sha256(canonical(candidate)).hexdigest(),
                order_sha256=hashlib.sha256(canonical(order2)).hexdigest(),
                dispatch_sha256=hashlib.sha256(canonical(dispatch2)).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload)
    print(payload, end="")


if __name__ == "__main__":
    main()
