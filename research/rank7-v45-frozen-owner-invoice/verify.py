#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Recount V45's complete invoice on PR2942's fixed owner-bin assignment."""

import argparse
import gzip
import hashlib
import io
import json
from collections import Counter
from itertools import combinations
from pathlib import Path

from frames import HELPERS, recount, require, v45_word
from owners import (
    check_fill,
    complete_profile,
    idle_invoice,
    source_windows,
    strict_cost_increase,
)

PACKAGE = Path(__file__).resolve().parent
CONSTRUCTION = "research/rank7-joint-endframes/"
ALLOCATION = "research/paired-extension-normal45/allocation/"


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    require(path.stat().st_size <= 16 * 1024 * 1024, "raw input size bound")
    raw = path.read_bytes()
    if raw[:2] == b"\x1f\x8b":
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(64 * 1024 * 1024 + 1)
    require(len(raw) <= 64 * 1024 * 1024, "decoded input size bound")
    return json.loads(raw, object_pairs_hook=unique_object)


def authenticate(root):
    sources = read_json(PACKAGE / "SOURCES.json")
    inputs = [f for f in sources["files"] if f["usage"] == "input"]
    require(len(inputs) == 10, "ten authenticated live inputs")
    hashes = {}
    for record in inputs:
        relative = record["path"]
        require(
            relative.startswith((CONSTRUCTION, ALLOCATION))
            and ".." not in Path(relative).parts,
            "source path",
        )
        path = root / relative
        require(path.stat().st_size <= 16 * 1024 * 1024, "raw input size bound")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        require(actual == record["sha256"], "source bytes: " + relative)
        hashes[relative] = actual
    require(len(hashes) == 10, "unique input inventory")
    return hashes


def clean(counter):
    return {str(r): n for r, n in sorted(counter.items()) if n}


def difference(after, before):
    delta = Counter(after)
    delta.subtract(before)
    return Counter({r: n for r, n in delta.items() if n})


def frame_variants(parents, edits, subset):
    local, widths, records = {}, {}, {}
    for provider, parent in parents.items():
        old_profile, old_widths = recount(parent)
        word = v45_word(parent, edits, subset)
        profile, new_widths = recount(word)
        expected = Counter({1: 2 - len(subset), 2: 10, 3: 6, 4: -10})
        require(
            difference(profile, old_profile) == difference(expected, {}),
            "V45 symbolic frame identity",
        )
        live = sorted(set(range(224, 704)) - set(parent["removed"]))
        indices = {live.index(h) for h in subset}
        require(
            new_widths == [v - (i in indices) for i, v in enumerate(old_widths)],
            "only selected widths fall",
        )
        require(
            word["cleanup"] == parent["cleanup"] and len(parent["helper_final"]) == 86,
            "86 unchanged private names",
        )
        local[provider], widths[provider] = profile, new_widths
        records[provider] = {
            "local_profile": clean(profile),
            "width_inventory": clean(Counter(new_widths)),
            "local_delta": clean(difference(profile, old_profile)),
            "private_names": 86,
        }
    return local, widths, records


def load_sources(root):
    hashes = authenticate(root)
    data = {name: read_json(root / name) for name in hashes}
    parents = {
        provider: data[CONSTRUCTION + "data/PARENT-" + tag + ".json.gz"]
        for provider, tag in (("gauge44", "base"), ("extra", "extra"))
    }
    order = data[ALLOCATION + "ORDER.json"]
    raw_dispatch = data[ALLOCATION + "DISPATCH.json"]
    require(len(raw_dispatch) == 666, "666 literal provider calls")
    dispatch = {(stage, replica): provider for stage, replica, provider in raw_dispatch}
    require(len(dispatch) == 666, "unique dispatch calls")
    widths, profiles = {}, {}
    registry = data[ALLOCATION + "PROVIDERS.json"]
    for provider, parent in parents.items():
        profiles[provider], widths[provider] = recount(parent)
        require(
            clean(profiles[provider]) == parent["report"]["local_profile"],
            "parent local report",
        )
        require(
            widths[provider] == registry[provider]["widths"],
            "source helper ordering and widths",
        )
        require(
            clean(profiles[provider]) == registry[provider]["actual_paid_profile"],
            "source paid registry",
        )
        live = sorted(set(range(224, 704)) - set(parent["removed"]))
        require(
            [live.index(h) for h in HELPERS] == [25, 27, 41, 43], "V45 helper ordering"
        )
    windows = source_windows(data[ALLOCATION + "vendor/TEMPLATE.json.gz"], order)
    bins = check_fill(
        data[ALLOCATION + "FILL.json.gz"],
        order,
        dispatch,
        data[ALLOCATION + "vendor/PLAN.json.gz"],
        windows,
        widths,
    )
    return hashes, data, parents, order, dispatch, profiles, windows, bins


def run(root):
    hashes, data, parents, _order, dispatch, profiles, windows, bins = load_sources(
        root
    )
    parent_idle, _touched, _journal = idle_invoice(bins, windows, set())
    baseline = complete_profile(parent_idle, profiles, dispatch)
    require(
        clean(baseline) == data[ALLOCATION + "PROFILE.json"], "complete parent profile"
    )
    edits = data[CONSTRUCTION + "data/STAGE1-FRAME-EDITS.json"]
    cases = []
    for size in range(5):
        for subset in combinations(HELPERS, size):
            local, _widths, frame_records = frame_variants(parents, edits, subset)
            indices = {
                dict(zip(HELPERS, (25, 27, 41, 43), strict=True))[h] for h in subset
            }
            idle, touched, journal = idle_invoice(bins, windows, indices)
            profile = complete_profile(idle, local, dispatch)
            delta = difference(profile, baseline)
            proof = strict_cost_increase(delta)
            require(
                all(old == 0 and freed in (1, 2) for old, freed in touched),
                "only full source bins, at most two freed units",
            )
            payload = json.dumps(journal, separators=(",", ":")).encode()
            cases.append(
                {
                    "helpers": list(subset),
                    "frames": frame_records,
                    "idle": clean(idle),
                    "idle_delta": clean(difference(idle, parent_idle)),
                    "complete_profile": clean(profile),
                    "complete_delta": clean(delta),
                    "strict_cost_increase": proof,
                    "touched_bins": [
                        {"old_idle": old, "freed": freed, "count": n}
                        for (old, freed), n in sorted(touched.items())
                    ],
                    "rebound_rows": len(journal),
                    "rebound_rows_sha256": hashlib.sha256(payload).hexdigest(),
                }
            )
    require(len(cases) == 16, "all endpoint subsets")
    require(
        cases[-1]["complete_delta"] == {"1": 1038, "2": 6807, "3": 3996, "4": -6660},
        "joint full invoice",
    )
    require(authenticate(root) == hashes, "no input drift")
    return {
        "status": "PASS_V45_FROZEN_OWNER_INVOICE",
        "inputs": hashes,
        "parent_idle": clean(parent_idle),
        "parent_profile": clean(baseline),
        "calls": 666,
        "roles": 271728,
        "bins": 149184,
        "replicas": 74,
        "provider_calls": dict(sorted(Counter(dispatch.values()).items())),
        "cases": cases,
        "scope": "Fixed call/owner/child/port assignment, free within-bin compaction, complete recursive histogram; no native or physical admission.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--emit", action="store_true", help="print fresh deterministic evidence"
    )
    parser.add_argument("--source-root", type=Path, default=PACKAGE.parents[1])
    args = parser.parse_args()
    result = run(args.source_root.resolve())
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        require(
            result == read_json(PACKAGE / "RESULT.json"),
            "committed evidence matches replay",
        )
        print(result["status"], "16 subsets; strictly higher moment for every a > 0")


if __name__ == "__main__":
    main()
