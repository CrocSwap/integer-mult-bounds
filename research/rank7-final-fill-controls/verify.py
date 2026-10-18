#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check V45 terminal controls against the literal final T74 allocation."""

import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import sys

from allocation import bill, control_case, verify_fill, window_table
import dual
from local import V45, basis, contains, need, recount

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = "research/rank7-joint-endframes/"
SOURCE_HEAD = "be191346391661f4d35fc0d1508d0a6029572576"


def unique_object(items):
    result = {}
    for key, value in items:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique_object)


def read_sources():
    manifest = decode((PACKAGE / "SOURCES.json").read_bytes())
    files, hashes = {}, {}
    for entry in manifest["files"]:
        if entry["usage"] != "input":
            continue
        path = entry["path"]
        need(path.startswith(SOURCE) and ".." not in Path(path).parts, "fixed source root")
        raw = (ROOT / path).read_bytes()
        need(len(raw) <= 16 * 1024 * 1024, "raw source size bound")
        actual = hashlib.sha256(raw).hexdigest()
        need(actual == entry["sha256"], "source SHA256 mismatch: " + path)
        payload = gzip.decompress(raw) if path.endswith(".gz") else raw
        need(len(payload) <= 64 * 1024 * 1024, "decoded source size bound")
        files[path.removeprefix(SOURCE)] = decode(payload)
        hashes[path] = actual
    need(len(files) == 12, "twelve exact live inputs")
    return files, hashes


def integer_profile(data):
    result = Counter()
    for key, count in data.items():
        rank = int(key)
        need(str(rank) == key and 0 < rank <= 73 and type(count) is int and count > 0,
             "positive integer rank histogram")
        result[rank] = count
    return result


def word_controls(word, parent, baseline):
    old_ends = {}
    for helper in V45:
        current = basis(tuple(word["helper_final"][str(helper)]))
        previous = basis(tuple(parent["helper_final"][str(helper)]))
        need(len(current) == 7 and len(previous) == 8 and contains(previous, current),
             "V45 rank-seven subspace inside old rank-eight endpoint")
        need(helper not in map(int, word["start_extra"]), "zero V45 entrance")
        old_ends[helper] = parent["helper_final"][str(helper)]
    out = []
    for mask in range(16):
        widened = [h for i, h in enumerate(V45) if mask & (1 << i)]
        candidate = recount(word, {h: old_ends[h] for h in widened})
        expected = Counter(baseline["profile"])
        if widened:
            expected[1] += len(widened)
        need(candidate["profile"] == expected, "terminal-only local H1 delta")
        need(candidate["private_names"] == baseline["private_names"], "unchanged private names")
        need(candidate["widths"] == [n + (h in widened) for h, n in
                                    zip(baseline["helpers"], baseline["widths"], strict=True)],
             "only selected residual widths change")
        out.append(dict(widened=widened, local_profile=dict(sorted(candidate["profile"].items())),
                        width_inventory=dict(sorted(Counter(candidate["widths"]).items())),
                        terminal_added_ranks=[e for e in candidate["v45_events"]
                                              if e[1][0] == "terminal"]))
    return out


def compute():
    files, hashes = read_sources()
    local_data, provider_receipts = {}, {}
    for provider, tag in (("gauge44", "base"), ("extra", "extra")):
        word = files[f"data/WORD-{tag}.json.gz"]
        parent = files[f"data/PARENT-{tag}.json.gz"]
        data = recount(word)
        need(data["profile"] == integer_profile(word["report"]["local_profile"]),
             "word report matches independent local recount")
        need(Counter(data["widths"]) == integer_profile(word["report"]["width_inventory"]),
             "width inventory matches word report")
        need(len(data["private_names"]) == 91, "91 charged private names")
        local_data[provider] = data
        provider_receipts[provider] = dict(
            baseline_profile=dict(sorted(data["profile"].items())),
            width_inventory=dict(sorted(Counter(data["widths"]).items())),
            private_names=data["private_names"],
            cleanup_operations=len(word["cleanup"]),
            v45_events=data["v45_events"],
            controls=word_controls(word, parent, data),
        )
    need(local_data["gauge44"]["helpers"] == local_data["extra"]["helpers"]
         and local_data["gauge44"]["widths"] == local_data["extra"]["widths"],
         "identical ordered helper inventory across providers")
    need(local_data["gauge44"]["profile"] == local_data["extra"]["profile"],
         "identical local tariff profile across providers")
    order = files["allocation/ORDER.json"]
    plan = files["allocation/vendor/PLAN.json.gz"]
    windows = window_table(files["allocation/vendor/TEMPLATE.json.gz"], order, plan)
    bins, counts = verify_fill(files["allocation/FILL.json.gz"], order,
                              files["allocation/DISPATCH.json"], plan, windows, local_data)
    idle, full = bill(bins, windows, counts, local_data)
    claim = files["CLAIM.json"]
    need(full == integer_profile(files["allocation/PROFILE.json"])
         == integer_profile(claim["profile"]), "literal complete profile agrees")
    need(dict(counts) == {"extra": 416, "gauge44": 250}, "actual provider counts")
    need(claim["calls"] == 666 and claim["replicas"] == 74 and claim["helpers"] == 408
         and claim["zero_buffers"] == 91, "claim stock inputs")
    physical = 896 * 74 + 408 + 8 + 91 + 2
    need(claim["live_families"] == 896 * 74 and claim["physical_families"] == physical,
         "complete nominal physical stock including private buffers")
    helper_indices = {h: local_data["gauge44"]["helpers"].index(h) for h in V45}
    saving = Fraction(claim["complex_lower"])
    packing = dual.check(files["certificates/RELAX-CAP.json"],
                         local_data["gauge44"]["profile"],
                         Counter(local_data["gauge44"]["widths"]), windows, saving)
    packing["actual_baseline_margin_interval"] = dual.check_actual_bill(full, saving)
    cases, all_witnesses = [], {}
    for mask in range(16):
        widened = [h for i, h in enumerate(V45) if mask & (1 << i)]
        case, witnesses = control_case(bins, windows, helper_indices, widened)
        need(all(row["old_idle"] == 0 for row in case["touched_bins"]),
             "every affected bin is saturated")
        need(case["total_excess"] == 666 * len(widened), "all added width becomes excess")
        need(case["feasible_without_reassignment"] == (mask == 0),
             "only the four-lowered endpoint choice fits")
        case["all_packings_rejected_at_source_saving"] = packing[
            "per_replica_excess_over_896_times_73_power"][len(widened)]["all_packings_rejected"]
        cases.append(case)
        all_witnesses[str(mask)] = witnesses
    result = dict(
        status="PASS_RANK7_FINAL_FILL_CONTROLS",
        source_head=SOURCE_HEAD, source_sha256=hashes,
        result_kind="finite capacity certificate and scoped obstruction",
        providers=provider_receipts, helper_indices=helper_indices,
        baseline=dict(calls=666, roles=666 * 408, bins=len(windows) * 112,
                      provider_counts=dict(counts), idle_profile=dict(sorted(idle.items())),
                      complete_profile=dict(sorted(full.items())),
                      rank_mass=sum(r * n for r, n in full.items()),
                      live_families=896 * 74, helpers=408, centres=8,
                      private_buffers=91, coefficient_families=2, physical_families=physical),
        cases=cases, packing_relaxation=packing,
        limits=["No control repacking is constructed or priced.",
                "These controls retain all final stage-2/3 scalar and frame edits.",
                "Original stage-1 guide controls remain separate predecessor evidence.",
                "No native phase, dirty restoration, movement, precision/tape or outer/all-size admission."],
    )
    # Normalize integer dictionary keys to their JSON spelling for receipt comparison.
    return decode(json.dumps(result)), all_witnesses


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print fresh deterministic receipt")
    parser.add_argument("--witnesses", type=Path, help="write all exact overfull-bin witnesses")
    args = parser.parse_args()
    result, witnesses = compute()
    if args.witnesses:
        with args.witnesses.open("x") as stream:
            json.dump(witnesses, stream, indent=2, sort_keys=True)
            stream.write("\n")
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        need(result == decode((PACKAGE / "RESULT.json").read_bytes()),
             "deterministic result differs")
        print(result["status"] + " cases=16 rejected_controls=15 roles=271728 bins=149184 packing_patterns=2551")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, IndexError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        raise SystemExit(1) from None
