#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay a small journal, independently check every role, and certify its gain."""

import argparse
import gzip
import hashlib
import json
import types
from collections import Counter
from fractions import Fraction
from pathlib import Path

import geometry
import moment

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = ROOT / "research/rank7-joint-endframes"
DELTA = {1: 4, 3: 4, 5: -6, 14: 1}


def read(path):
    raw = path.read_bytes()
    moment.need(len(raw) <= 4_000_000, "compressed source size")
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    moment.need(len(raw) <= 20_000_000, "decompressed source size")
    return json.loads(raw)


def authenticate():
    sources = read(PACKAGE / "SOURCES.json")
    moment.need(len(sources["files"]) <= 32, "source count")
    hashes = {}
    for entry in sources["files"]:
        if entry["usage"] != "input":
            continue
        path = ROOT / entry["path"]
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        moment.need(actual == entry["sha256"], "source digest: " + entry["path"])
        hashes[entry["path"]] = actual
    return hashes


def apply(fill, certificate):
    rows = list(fill["rows"])
    edits = certificate["edits"]
    moment.need(0 < len(edits) <= 128, "journal size")
    seen = set()
    for index, before, after in edits:
        moment.need(type(index) is int and 0 <= index < len(rows), "journal index")
        moment.need(index not in seen, "duplicate journal index")
        moment.need(rows[index] == before, "journal preimage")
        moment.need(len(after) == 6 and after[:2] == before[:2], "fixed call/helper")
        rows[index] = after
        seen.add(index)
    return {**fill, "rows": rows}


def buffers_and_widths(providers):
    for tag, provider in [("base", "gauge44"), ("extra", "extra")]:
        word = read(SOURCE / f"data/WORD-{tag}.json.gz")
        helpers = sorted(set(range(224, 704)) - set(word["removed"]))
        widths = [
            len(word["helper_final"].get(str(h), [0] * 9))
            - len(word["start_extra"].get(str(h), []))
            for h in helpers
        ]
        moment.need(widths == providers[provider]["widths"], "literal endpoint widths")
        used = {
            r
            for gate in word["cleanup"]
            for r in (gate[1:3] if gate[0] == "add" else gate[1:2])
            if r >= 704
        }
        moment.need(
            used == {704 + int(h) for h in word["helper_final"]}, "private namespace"
        )
        moment.need(len(used) == 91 and len(word["centers"]) == 8, "physical inventory")
        moment.need(
            word["report"]["local_profile"]
            == providers[provider]["actual_paid_profile"],
            "source local profile",
        )
    return 91


def strict_gain(old, new):
    old_interval, new_interval = moment.root(old), moment.root(new)
    moment.need(old_interval[1] < new_interval[0], "strict root improvement")
    return old_interval, new_interval


def check_routes(parent, candidate, certificate, providers, order, dispatch):
    moves = {
        index
        for index, before, after in certificate["edits"]
        if before[2:5] != after[2:5]
    }
    moment.need(len(moves) == 44 and len(certificate["routes"]) == 13, "relay counts")
    listed = set()
    for route in certificate["routes"]:
        moment.need(1 <= len(route) <= 8, "relay length")
        widths = set()
        for index, target in route:
            moment.need(index in moves and index not in listed, "relay role coverage")
            moment.need(candidate["rows"][index][2:5] == target, "relay destination")
            time, helper = parent["rows"][index][:2]
            widths.add(providers[dispatch[tuple(order[time])]]["widths"][helper])
            listed.add(index)
        moment.need(len(widths) == 1, "homogeneous relay width")
    moment.need(listed == moves, "complete relay coverage")


def retained_crosscheck(order, fill, dispatch, plan, template, providers, expected):
    """Secondary retained checker, not part of the independent implementation."""
    path = SOURCE / "allocation/vendor/independent_owners.py"
    module = types.ModuleType("pinned_owner_comparison")
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    normalized = {
        name: {
            **provider,
            "actual_paid_profile": {
                int(k): v for k, v in provider["actual_paid_profile"].items()
            },
        }
        for name, provider in providers.items()
    }
    actual, _, _ = module.check(
        74, order, fill, dispatch, expected, plan, template, normalized
    )
    moment.need(actual["profile"] == expected, "retained checker profile")
    moment.need(actual["live"] + 408 + 8 + 91 + 2 == 66813, "complete private stock")
    return actual["physical"]


def reject(action, label, rejected):
    try:
        action()
    except ValueError:
        rejected.append(label)
    else:
        raise ValueError("accepted control: " + label)


def controls(order, fill, dispatch, plan, template, providers, certificate, old, new):
    rejected = []

    def check(rows):
        return geometry.check(
            order, {**fill, "rows": rows}, dispatch, plan, template, providers
        )

    rows = fill["rows"]
    reject(lambda: check(rows[:-1]), "missing_role", rejected)
    duplicate = list(rows[1])
    duplicate[1] = rows[0][1]
    reject(lambda: check([rows[0], duplicate, *rows[2:]]), "duplicate_helper", rejected)
    collision = list(rows[1])
    collision[2:5] = rows[0][2:5]
    reject(lambda: check([rows[0], collision, *rows[2:]]), "family_collision", rejected)
    windows = geometry.windows(template, order, 74)
    unavailable = next(
        key for key, (_, low, high) in windows.items() if not low < rows[0][0] <= high
    )
    bad = list(rows[0])
    bad[2:4] = unavailable
    reject(lambda: check([bad, *rows[1:]]), "unavailable_source", rejected)
    bad = list(rows[0])
    bad[5] = 48
    reject(lambda: check([bad, *rows[1:]]), "capacity_overflow", rejected)
    last = {}
    for index, row in enumerate(rows):
        key = tuple(row[2:5])
        if key not in last or row[5] > rows[last[key]][5]:
            last[key] = index
    for key, index in last.items():
        row = rows[index]
        width = providers[dispatch[tuple(order[row[0]])]]["widths"][row[1]]
        if row[5] + width < windows[key[:2]][0]:
            bad = list(row)
            bad[5] += 1
            mutant = list(rows)
            mutant[index] = bad
            reject(
                lambda changed=mutant: check(changed), "unpaid_prefix_hole", rejected
            )
            break
    moment.need("unpaid_prefix_hole" in rejected, "prefix control executed")
    stale = {**certificate, "edits": [*certificate["edits"], certificate["edits"][0]]}
    reject(
        lambda: apply(read(SOURCE / "allocation/FILL.json.gz"), stale),
        "duplicate_edit",
        rejected,
    )
    reject(lambda: apply(fill, certificate), "stale_preimage", rejected)
    reject(lambda: strict_gain(old, old), "no_op_gain", rejected)
    reject(lambda: strict_gain(new, old), "reversed_gain", rejected)
    unpaid = dict(new)
    unpaid[1] -= 1
    reject(lambda: moment.root(unpaid), "omitted_paid_child", rejected)
    return rejected


def moment_receipt(old, new):
    old_root, new_root = strict_gain(old, new)
    cap = read(SOURCE / "certificates/RELAX-CAP.json")
    moment.need(
        new_root[1] < Fraction(cap["cap_lower"]), "below inherited relaxation cap"
    )
    return {
        "baseline_root": list(map(str, old_root)),
        "new_root": list(map(str, new_root)),
        "gain": [str(new_root[0] - old_root[1]), str(new_root[1] - old_root[0])],
        "gap_to_inherited_cap": [
            str(Fraction(cap["cap_lower"]) - new_root[1]),
            str(Fraction(cap["cap_upper"]) - new_root[0]),
        ],
        "realized_fraction_of_inherited_cap": str(
            new_root[0] / Fraction(cap["cap_upper"])
        ),
        "sign_certificate": moment.sign_certificate(),
    }


def run():
    hashes = authenticate()
    order = read(SOURCE / "allocation/ORDER.json")
    dispatch_rows = read(SOURCE / "allocation/DISPATCH.json")
    dispatch = {(s, r): provider for s, r, provider in dispatch_rows}
    moment.need(len(dispatch) == len(dispatch_rows) == 666, "dispatch uniqueness")
    providers = read(SOURCE / "allocation/PROVIDERS.json")
    plan = read(SOURCE / "allocation/vendor/PLAN.json.gz")
    template = read(SOURCE / "allocation/vendor/TEMPLATE.json.gz")
    buffers_and_widths(providers)
    parent = read(SOURCE / "allocation/FILL.json.gz")
    certificate = read(PACKAGE / "EXCHANGE.json")
    candidate = apply(parent, certificate)
    check_routes(parent, candidate, certificate, providers, order, dispatch)
    baseline = geometry.check(order, parent, dispatch, plan, template, providers)
    result = geometry.check(order, candidate, dispatch, plan, template, providers)
    old = {int(k): v for k, v in read(SOURCE / "allocation/PROFILE.json").items()}
    moment.need(baseline["profile"] == old, "independent baseline recount")
    delta = Counter(result["profile"])
    delta.subtract(old)
    moment.need(
        {k: v for k, v in delta.items() if v} == DELTA, "literal exchange delta"
    )
    certified_moment = moment_receipt(old, result["profile"])
    legacy = retained_crosscheck(
        order, candidate, dispatch, plan, template, providers, result["profile"]
    )
    rejected = controls(
        order,
        candidate,
        dispatch,
        plan,
        template,
        providers,
        certificate,
        old,
        result["profile"],
    )
    return {
        "status": "PASS_RANK7_INTEGRALITY_EXCHANGE",
        "scope": "Finite chronological allocation and complete conditional moment; no supplier/outer admission.",
        "roles": result["roles"],
        "calls": 666,
        "replicas": 74,
        "edits": len(certificate["edits"]),
        "moved_roles": sum(
            before[2:5] != after[2:5] for _, before, after in certificate["edits"]
        ),
        "physical": result["physical"],
        "private_buffers": 91,
        "legacy_checker_physical": legacy,
        "rank_mass": result["rank_mass"],
        "profile": result["profile"],
        "idle": result["idle"],
        "delta": DELTA,
        "patterns": result["bin_pattern_histogram"],
        **certified_moment,
        "rejected_controls": rejected,
        "source_sha256": hashes,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = run()
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.write_result:
        (PACKAGE / "RESULT.json").write_text(encoded, encoding="utf-8")
    else:
        moment.need(
            json.loads(encoded) == read(PACKAGE / "RESULT.json"), "committed receipt"
        )
    print(
        result["status"],
        "roles=271728 moved=44 controls=" + str(len(result["rejected_controls"])),
    )


if __name__ == "__main__":
    main()
