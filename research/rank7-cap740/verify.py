#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Verify literal cap attainment without a solver or a new supplier claim."""

import argparse
import gzip
import hashlib
import json
import types
from collections import Counter
from fractions import Fraction
from pathlib import Path

import cap_proof
import lift

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = ROOT / "research/rank7-joint-endframes"
DELTA = {1: 20, 3: 17, 5: -15, 14: -10, 48: 3}


def read(path):
    raw = path.read_bytes()
    lift.need(len(raw) <= 4_000_000, "compressed input bound")
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    lift.need(len(raw) <= 20_000_000, "decompressed input bound")
    return json.loads(raw)


def authenticate():
    entries = read(PACKAGE / "SOURCES.json")["files"]
    lift.need(len(entries) <= 32, "source count")
    hashes = {}
    for entry in entries:
        if entry["usage"] == "input":
            actual = hashlib.sha256((ROOT / entry["path"]).read_bytes()).hexdigest()
            lift.need(actual == entry["sha256"], "source digest: " + entry["path"])
            hashes[entry["path"]] = actual
    retained = read(PACKAGE / "RETAINED.json")
    for name, expected in retained["sha256"].items():
        lift.need(
            hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest() == expected,
            "retained bytes",
        )
    return hashes


def load_module(path, name):
    module = types.ModuleType(name)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def predecessor(fill):
    rows = list(fill["rows"])
    edits = read(PACKAGE / "PR3018-EXCHANGE.json")["edits"]
    lift.need(len(edits) == 103, "predecessor journal count")
    seen = set()
    for index, before, after in edits:
        lift.need(index not in seen and rows[index] == before, "predecessor preimage")
        lift.need(after[:2] == before[:2], "predecessor identity")
        rows[index] = after
        seen.add(index)
    return {**fill, "rows": rows, "dispatch_overrides": []}


def source_contract(providers):
    for tag, provider in [("base", "gauge44"), ("extra", "extra")]:
        word = read(SOURCE / f"data/WORD-{tag}.json.gz")
        helpers = sorted(set(range(224, 704)) - set(word["removed"]))
        widths = [
            len(word["helper_final"].get(str(h), [0] * 9))
            - len(word["start_extra"].get(str(h), []))
            for h in helpers
        ]
        lift.need(widths == providers[provider]["widths"], "literal ordered widths")
        lift.need(
            word["report"]["local_profile"]
            == providers[provider]["actual_paid_profile"],
            "local report",
        )
        private = {
            r
            for gate in word["cleanup"]
            for r in (gate[1:3] if gate[0] == "add" else gate[1:2])
            if r >= 704
        }
        lift.need(
            private == {704 + int(h) for h in word["helper_final"]}, "private namespace"
        )
        lift.need(
            len(private) == 91 and len(word["centers"]) == 8, "private/centre count"
        )
        inventory = dict(zip(cap_proof.WIDTHS, cap_proof.INVENTORY, strict=True))
        lift.need(Counter(widths) == Counter(inventory), "inventory")
        lift.need(
            {int(k): v for k, v in word["report"]["local_profile"].items()}
            == cap_proof.LOCAL,
            "cap local binding",
        )


def full_comparison(base, edits, order, dispatch, plan, template, providers, profile):
    module = load_module(
        SOURCE / "allocation/vendor/independent_owners.py", "retained_owner"
    )
    normalized = {
        name: {
            **value,
            "actual_paid_profile": {
                int(k): v for k, v in value["actual_paid_profile"].items()
            },
        }
        for name, value in providers.items()
    }
    fill = {
        "columns": ["time", "helper", "owner_replica", "child", "port", "offset"],
        "rows": lift.Rows(base, edits),
        "dispatch_overrides": [],
    }
    result, _, _ = module.check(
        740, order, fill, dispatch, profile, plan, template, normalized
    )
    lift.need(result["roles"] == 2717280, "complete literal comparison")
    lift.need(result["live"] + 408 + 8 + 91 + 2 == 663549, "complete physical bill")
    return result


def root_interval(profile, replicas, root):
    lower, upper = root.kappa_from_profile(profile, replicas)
    return [str(lower), str(upper)]


def moment_receipt(old, profile, full):
    root = load_module(SOURCE / "tools/root.py", "authenticated_root")
    certificate = read(SOURCE / "certificates/RELAX-CAP.json")
    cap = cap_proof.verify_cap(certificate, root)
    scaled_idle = {
        int(r): 740 * Fraction(n) for r, n in cap["idle_per_replica"].items()
    }
    lift.need(
        all(n.denominator == 1 for n in scaled_idle.values()), "integral cap counts"
    )
    expected_idle = {r: int(n) for r, n in scaled_idle.items()}
    lift.need(full["idle"] == expected_idle, "literal fractional-cap attainment")
    old_root = root_interval(old["profile"], 74, root)
    new_root = root_interval(profile, 740, root)
    lift.need(
        Fraction(old_root[1]) < Fraction(new_root[0]), "strict complete moment gain"
    )
    return {
        "baseline_root": old_root,
        "cap_attaining_root": new_root,
        "gain": [
            str(Fraction(new_root[0]) - Fraction(old_root[1])),
            str(Fraction(new_root[1]) - Fraction(old_root[0])),
        ],
        "cap_certificate": cap,
        "sign_certificate": cap_proof.prove_exchange_sign(),
    }


def run():
    hashes = authenticate()
    geometry74 = load_module(PACKAGE / "vendor/geometry74.py", "authenticated_geometry")
    order = read(SOURCE / "allocation/ORDER.json")
    dispatch = {(s, r): p for s, r, p in read(SOURCE / "allocation/DISPATCH.json")}
    providers = read(SOURCE / "allocation/PROVIDERS.json")
    plan = read(SOURCE / "allocation/vendor/PLAN.json.gz")
    template = read(SOURCE / "allocation/vendor/TEMPLATE.json.gz")
    source_contract(providers)
    base = predecessor(read(SOURCE / "allocation/FILL.json.gz"))
    old = geometry74.check(order, base, dispatch, plan, template, providers)
    lift.need(
        old["idle"] == {1: 17314, 3: 4960, 5: 1722, 14: 1, 48: 28190},
        "predecessor idle control",
    )
    edits = lift.patch(base["rows"], read(PACKAGE / "EXCHANGE.json"))
    widths = [providers[dispatch[tuple(call)]]["widths"] for call in order]
    windows = geometry74.windows(template, order, 74)
    families = geometry74._physical_families(plan, {child for _, child in windows})
    difference = lift.differential(base["rows"], edits, widths, windows, families)
    lift.need(difference["idle_delta"] == DELTA, "exact exchange idle delta")
    profile = Counter({r: 10 * n for r, n in old["profile"].items()})
    profile.update(DELTA)
    profile = {r: n for r, n in sorted(profile.items()) if n}
    lift.need(all(n > 0 for n in profile.values()), "positive completed profile")
    lifted_order, lifted_dispatch = lift.chronology(order, dispatch)
    full = full_comparison(
        base["rows"],
        edits,
        lifted_order,
        lifted_dispatch,
        plan,
        template,
        providers,
        profile,
    )
    moved = sum(
        lift.row_at(base["rows"], i)[2:5] != row[2:5] for i, row in edits.items()
    )
    return {
        "status": "PASS_RANK7_CAP740",
        "source_sha256": hashes,
        "copies": 10,
        "replicas": 740,
        "calls": 6660,
        "roles": 2717280,
        "edits": len(edits),
        "moved_roles": moved,
        "private_buffers": 91,
        "physical": 663549,
        "rank_mass": full["rank_mass"],
        "idle": full["idle"],
        "profile": profile,
        "difference": difference,
        **moment_receipt(old, profile, full),
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
        lift.need(
            json.loads(encoded) == read(PACKAGE / "RESULT.json"), "committed receipt"
        )
    print(result["status"], "roles=2717280", "edits=" + str(result["edits"]))


if __name__ == "__main__":
    main()
