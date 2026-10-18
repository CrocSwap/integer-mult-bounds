#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Certify a literal T148 successor to PR3018, not supplier admission."""

import argparse
import gzip
import hashlib
import json
import types
from collections import Counter
from fractions import Fraction
from pathlib import Path

import geometry

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = ROOT / "research/rank7-joint-endframes"
DELTA = {1: 4, 3: 4, 5: -4, 14: -2, 32: 1}
need = geometry.need


def read(path):
    raw = path.read_bytes()
    need(len(raw) <= 4_000_000, "compressed input size")
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    need(len(raw) <= 40_000_000, "decompressed input size")
    return json.loads(raw)


def authenticate():
    sources = read(PACKAGE / "SOURCES.json")
    need(len(sources["files"]) <= 32, "source count")
    hashes = {}
    for entry in sources["files"]:
        if entry["usage"] == "input":
            actual = hashlib.sha256((ROOT / entry["path"]).read_bytes()).hexdigest()
            need(actual == entry["sha256"], "source digest: " + entry["path"])
            hashes[entry["path"]] = actual
    need(len(sources["predecessor_files"]) == 3, "predecessor file count")
    for entry in sources["predecessor_files"]:
        actual = hashlib.sha256(
            (PACKAGE / entry["local_path"]).read_bytes()
        ).hexdigest()
        need(actual == entry["local_sha256"], "predecessor digest")
    return hashes


def apply(fill, journal):
    rows = list(fill["rows"])
    edits = journal["edits"]
    need(type(edits) is list and 0 < len(edits) <= 256, "journal bound")
    seen = set()
    for index, before, after in edits:
        need(type(index) is int and 0 <= index < len(rows), "journal index")
        need(index not in seen and rows[index] == before, "journal preimage")
        need(len(after) == 6 and before[:2] == after[:2], "fixed role identity")
        rows[index] = after
        seen.add(index)
    return {**fill, "rows": rows}


def doubled(order, fill, dispatch):
    need(len(order) == 666 and len(fill["rows"]) == 271728, "T74 baseline")
    new_order = [
        [stage, owner + 74 * copy] for stage, owner in order for copy in range(2)
    ]
    new_rows = [
        [2 * time + copy, helper, owner + 74 * copy, child, port, offset]
        for time, helper, owner, child, port, offset in fill["rows"]
        for copy in range(2)
    ]
    new_dispatch = {
        (stage, owner + 74 * copy): provider
        for (stage, owner), provider in dispatch.items()
        for copy in range(2)
    }
    need(not fill.get("dispatch_overrides"), "no untransported overrides")
    return new_order, {**fill, "rows": new_rows}, new_dispatch


def source_contract(providers):
    for tag, name in [("base", "gauge44"), ("extra", "extra")]:
        word = read(SOURCE / f"data/WORD-{tag}.json.gz")
        helpers = sorted(set(range(224, 704)) - set(word["removed"]))
        widths = [
            len(word["helper_final"].get(str(h), [0] * 9))
            - len(word["start_extra"].get(str(h), []))
            for h in helpers
        ]
        need(widths == providers[name]["widths"], "ordered source widths")
        need(
            word["report"]["local_profile"] == providers[name]["actual_paid_profile"],
            "local bill",
        )
        private = {
            r
            for gate in word["cleanup"]
            for r in (gate[1:3] if gate[0] == "add" else gate[1:2])
            if r >= 704
        }
        need(
            private == {704 + int(h) for h in word["helper_final"]}, "private namespace"
        )
        need(len(private) == 91 and len(word["centers"]) == 8, "private stock")


def root(profile, replicas):
    from vendor import moment

    need(replicas in (74, 148), "moment replica bound")
    need(
        sum(r * n for r, n in profile.items()) == 65088 * replicas, "complete rank mass"
    )
    threshold = 73 * 896 * replicas * moment.SCALE
    low, high = 0, moment.GRID // 100
    need(moment.moment_numerator(profile, Fraction(0))[1] < threshold, "lower endpoint")
    need(
        moment.moment_numerator(profile, Fraction(1, 100))[0] > threshold,
        "upper endpoint",
    )
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


def sign_certificate():
    from vendor import moment

    two = moment.short_log(Fraction(2))
    bounds = {}
    for value, exponent, unit in [
        (3, 1, Fraction(3, 2)),
        (5, 2, Fraction(5, 4)),
        (14, 3, Fraction(7, 4)),
        (32, 5, Fraction(1)),
    ]:
        low, high = moment.short_log(unit)
        bounds[value] = low + exponent * two[0], high + exponent * two[1]
    need(Fraction(109, 100) < bounds[3][0] <= bounds[3][1] < Fraction(11, 10), "log3")
    need(bounds[5][1] < Fraction(161, 100), "log5")
    need(bounds[14][1] < Fraction(66, 25), "log14")
    need(
        Fraction(173, 50) < bounds[32][0] <= bounds[32][1] < Fraction(347, 100), "log32"
    )
    upper = (
        20 * Fraction(161, 100)
        + 28 * Fraction(66, 25)
        - 12 * Fraction(109, 100) * Fraction(989, 1000)
        - 32 * Fraction(173, 50) * Fraction(9653, 10000)
    )
    need(upper == -Fraction(1711767, 125000), "strict derivative bound")
    return {"derivative_upper": str(upper), "domain": "0 < b <= 1/100"}


def check_routes(parent, candidate, journal, providers, order, dispatch):
    moves = {i for i, old, new in journal["edits"] if old[2:5] != new[2:5]}
    need(len(moves) == 50 and len(journal["routes"]) == 18, "relay counts")
    seen = set()
    for route in journal["routes"]:
        need(0 < len(route) <= 8, "route bound")
        widths = set()
        for index, destination in route:
            need(index in moves and index not in seen, "route coverage")
            need(candidate["rows"][index][2:5] == destination, "route destination")
            time, helper = parent["rows"][index][:2]
            widths.add(providers[dispatch[tuple(order[time])]]["widths"][helper])
            seen.add(index)
        need(len(widths) == 1, "homogeneous relay")
    need(seen == moves, "complete relay coverage")


def retained_check(order, fill, dispatch, plan, template, providers, expected):
    """Secondary retained owner engine; not an independent new implementation."""
    path = SOURCE / "allocation/vendor/independent_owners.py"
    module = types.ModuleType("retained_t_owner_check")
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    parsed = {
        name: {
            **provider,
            "actual_paid_profile": {
                int(r): n for r, n in provider["actual_paid_profile"].items()
            },
        }
        for name, provider in providers.items()
    }
    actual, _, _ = module.check(
        148, order, fill, dispatch, expected, plan, template, parsed
    )
    need(actual["profile"] == expected, "retained complete invoice")
    need(
        actual["live"] + 408 + 8 + 91 + 2 == 133117, "retained corrected physical stock"
    )
    return actual["physical"]


def reject(action, label, rejected):
    try:
        action()
    except ValueError:
        rejected.append(label)
    else:
        raise ValueError("accepted control: " + label)


def controls(
    order, parent, candidate, dispatch, providers, plan, template, journal, old, new
):
    rejected = []

    def check(fill):
        return geometry.check(order, fill, dispatch, plan, template, providers)

    reject(lambda: apply(candidate, journal), "stale_preimage", rejected)
    stale = {**journal, "edits": [*journal["edits"], journal["edits"][0]]}
    reject(lambda: apply(parent, stale), "duplicate_edit", rejected)
    reject(
        lambda: check({**candidate, "rows": candidate["rows"][:-1]}),
        "missing_role",
        rejected,
    )
    rows = list(candidate["rows"])
    rows[1] = [rows[0][0], rows[0][1], *rows[1][2:]]
    reject(lambda: check({**candidate, "rows": rows}), "duplicate_role", rejected)
    rows = list(candidate["rows"])
    rows[0] = [*rows[0][:5], 48]
    reject(lambda: check({**candidate, "rows": rows}), "capacity", rejected)
    rows = list(candidate["rows"])
    index, before, after = journal["edits"][0]
    rows[index] = before
    reject(lambda: check({**candidate, "rows": rows}), "omitted_relay_edit", rejected)
    unpaid = dict(new)
    unpaid[32] -= 1
    if unpaid[32] == 0:
        del unpaid[32]
    reject(lambda: root(unpaid, 148), "omitted_idle_child", rejected)
    reject(
        lambda: need(root(old, 74)[1] < root(old, 74)[0], "strict gain"),
        "no_op_gain",
        rejected,
    )
    reject(
        lambda: need(root(new, 148)[1] < root(old, 74)[0], "strict gain"),
        "reversed_gain",
        rejected,
    )
    return rejected


def run():
    hashes = authenticate()
    order = read(SOURCE / "allocation/ORDER.json")
    dispatch_rows = read(SOURCE / "allocation/DISPATCH.json")
    dispatch = {(s, r): name for s, r, name in dispatch_rows}
    need(len(dispatch) == len(dispatch_rows) == 666, "source dispatch")
    providers = read(SOURCE / "allocation/PROVIDERS.json")
    plan = read(SOURCE / "allocation/vendor/PLAN.json.gz")
    template = read(SOURCE / "allocation/vendor/TEMPLATE.json.gz")
    source_contract(providers)
    source_fill = read(SOURCE / "allocation/FILL.json.gz")
    baseline_fill = apply(source_fill, read(PACKAGE / "vendor/PR3018-EXCHANGE.json"))
    baseline = geometry.check(order, baseline_fill, dispatch, plan, template, providers)
    old = baseline["profile"]
    expected = Counter(
        {int(k): n for k, n in read(SOURCE / "allocation/PROFILE.json").items()}
    )
    expected.update({1: 4, 3: 4, 5: -6, 14: 1})
    need(old == dict(expected), "PR3018 baseline invoice")
    order2, parent, dispatch2 = doubled(order, baseline_fill, dispatch)
    double_bill = geometry.check(order2, parent, dispatch2, plan, template, providers)
    need(double_bill["profile"] == {r: 2 * n for r, n in old.items()}, "exact doubling")
    journal = read(PACKAGE / "EXCHANGE.json")
    candidate = apply(parent, journal)
    check_routes(parent, candidate, journal, providers, order2, dispatch2)
    result = geometry.check(order2, candidate, dispatch2, plan, template, providers)
    legacy_physical = retained_check(
        order2, candidate, dispatch2, plan, template, providers, result["profile"]
    )
    delta = Counter(result["profile"])
    delta.subtract(double_bill["profile"])
    need({r: n for r, n in delta.items() if n} == DELTA, "complete moment delta")
    rejected = controls(
        order2,
        parent,
        candidate,
        dispatch2,
        providers,
        plan,
        template,
        journal,
        old,
        result["profile"],
    )
    return certify_receipt(result, legacy_physical, journal, old, hashes, rejected)


def certify_receipt(result, legacy_physical, journal, old, hashes, rejected):
    old_root, new_root = root(old, 74), root(result["profile"], 148)
    need(old_root[1] < new_root[0], "strict gain")
    cap = read(SOURCE / "certificates/RELAX-CAP.json")
    need(new_root[1] < Fraction(cap["cap_lower"]), "below fractional cap")
    return {
        "status": "PASS_RANK7_DOUBLED_RESIDUAL_EXCHANGE",
        "replicas": 148,
        "calls": 1332,
        "roles": result["roles"],
        "physical": result["physical"],
        "private_buffers": 91,
        "legacy_checker_physical": legacy_physical,
        "edits": len(journal["edits"]),
        "moved_roles": 50,
        "rank_mass": result["rank_mass"],
        "profile": result["profile"],
        "idle": result["idle"],
        "patterns": result["bin_pattern_histogram"],
        "baseline_root": list(map(str, old_root)),
        "new_root": list(map(str, new_root)),
        "gain": [str(new_root[0] - old_root[1]), str(new_root[1] - old_root[0])],
        "gap_to_cap": [
            str(Fraction(cap["cap_lower"]) - new_root[1]),
            str(Fraction(cap["cap_upper"]) - new_root[0]),
        ],
        "realized_fraction_of_cap": str(new_root[0] / Fraction(cap["cap_upper"])),
        "delta": DELTA,
        "sign_certificate": sign_certificate(),
        "journal_sha256": hashlib.sha256(
            (PACKAGE / "EXCHANGE.json").read_bytes()
        ).hexdigest(),
        "rejected_controls": rejected,
        "source_sha256": hashes,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = run()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write_result:
        (PACKAGE / "RESULT.json").write_text(encoded, encoding="utf-8")
    else:
        need(json.loads(encoded) == read(PACKAGE / "RESULT.json"), "committed receipt")
    print(
        result["status"],
        "roles=543456 moved=50 controls=" + str(len(result["rejected_controls"])),
    )


if __name__ == "__main__":
    main()
