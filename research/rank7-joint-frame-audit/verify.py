#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound independent audit of PR2979's joint rank-seven frame paths."""

import gzip
import hashlib
import io
import json
from collections import Counter
from copy import deepcopy
from itertools import combinations
from pathlib import Path

from frames import Invalid, cleanup_namespace, ledger, require
from lowering import apply_frames, difference, edit_groups

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = "research/rank7-joint-endframes/"


def inputs():
    records = json.loads((PACKAGE / "SOURCES.json").read_text())["files"]
    require(len(records) <= 16, "bounded input manifest")
    result = {}
    for record in records:
        if record["usage"] != "input":
            continue
        path = ROOT / record["path"]
        require(path.stat().st_size <= 2_000_000, "bounded input bytes")
        raw = path.read_bytes()
        require(
            hashlib.sha256(raw).hexdigest() == record["sha256"],
            "input SHA256: " + record["path"],
        )
        if path.suffix == ".gz":
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
                raw = stream.read(8_000_001)
        require(len(raw) <= 8_000_000, "bounded decoded input")
        result[record["path"].removeprefix(SOURCE)] = json.loads(raw)
    return result


def price(delta, weights):
    return sum(n * weights[r] for r, n in delta.items())


def rejected(action, expected):
    try:
        action()
    except Invalid as error:
        require(expected in str(error), ("wrong rejection", expected, str(error)))
        return str(error)
    raise Invalid("mutant accepted: " + expected)


def group_audit(parent, record, baseline, prices):
    weights = {int(r): c for r, c in prices["weights"]["c"].items()}
    break_even = prices["weights"]["break_even"]
    results = {}
    for name, (_, helpers) in record["groups"].items():
        child = apply_frames(parent, record, [name])
        result = ledger(child, check_report=False)
        delta = difference(result["profile"], baseline["profile"])
        declared = next(g for g in prices["stage1"]["groups"] if g["group"] == name)
        cost = price(delta, weights)
        require(cost == declared["joint_delta"], "isolated joint surrogate price")
        require(
            -cost - len(helpers) * break_even == declared["joint_margin"],
            "joint surrogate margin",
        )
        results[name] = {
            "profile_delta": delta,
            "width_delta": difference(result["widths"], baseline["widths"]),
            "surrogate_delta": cost,
            "surrogate_margin": -cost - len(helpers) * break_even,
            "gate_frame_edits": len(edit_groups(record)[name]),
        }
    return results


def subset_audit(parent, record, baseline, prices):
    helpers = record["groups"]["V45"][1]
    weights = {int(r): c for r, c in prices["weights"]["c"].items()}
    results = []
    require(len(helpers) == 4, "four V45 endpoints")
    for count in range(5):
        for subset in combinations(helpers, count):
            child = apply_frames(parent, record, ["V45"], endpoints=subset)
            result = ledger(child, check_report=False)
            delta = difference(result["profile"], baseline["profile"])
            expected = {1: 2 - count, 2: 10, 3: 6, 4: -10}
            require(
                delta == {r: n for r, n in expected.items() if n},
                "all-tariff V45 subset identity",
            )
            require(
                cleanup_namespace(child)
                == {"private_buffers": 86, "cleanup_gates": 4992},
                "subset cleanup contract",
            )
            cost = price(delta, weights)
            margin = -cost - count * prices["weights"]["break_even"]
            if count:
                declared = next(
                    s
                    for s in prices["stage1"]["groups"][0]["subsets"]
                    if set(s["helpers"]) == set(subset)
                )
                require(
                    cost == declared["delta"] and margin == declared["margin"],
                    "source subset surrogate comparison",
                )
            require((margin > 0) == (count == 4), "joint-only guide margin")
            results.append(
                {
                    "helpers": list(subset),
                    "profile_delta": delta,
                    "surrogate_delta": cost,
                    "surrogate_margin": margin,
                }
            )
    require(len(results) == 16, "all endpoint subsets checked")
    return results


def controls(parent, child, record):
    results = {}
    bad = deepcopy(child)
    bad["report"] = deepcopy(parent["report"])
    results["stale_report"] = rejected(lambda: ledger(bad), "paid report mismatch")
    bad = deepcopy(child)
    bad["helper_final"]["249"] = [256, 128, 64, 32, 16, 8, 4]
    results["wrong_rank7_space"] = rejected(lambda: ledger(bad, False), "nonmonotone")
    bad = deepcopy(child)
    edit = next(e for e in record["frame_edits"] if e["gate"][1] == 249)
    bad[edit["section"]][edit["index"]][-1] = edit["old_frame"]
    results["omitted_frame_edit"] = rejected(lambda: ledger(bad, False), "nonmonotone")
    bad = deepcopy(child)
    bad["helper_final"]["249"] = parent["helper_final"]["249"]
    results["widened_endpoint"] = rejected(lambda: ledger(bad), "paid report mismatch")
    bad = deepcopy(child)
    bad["warps"][0][2] = [0] * 9
    results["singular_warp"] = rejected(lambda: ledger(bad, False), "invertible warp")
    bad = deepcopy(child)
    bad["cleanup"] = bad["cleanup"][1:]
    results["missing_cleanup"] = rejected(
        lambda: cleanup_namespace(bad), "cleanup length"
    )
    bad = deepcopy(child)
    bad["cleanup"][0][2] = 704 + 250
    results["wrong_private_name"] = rejected(
        lambda: cleanup_namespace(bad), "inverse cleanup syntax"
    )
    bad_record = deepcopy(record)
    bad_record["frame_edits"][0]["gate"][3] *= -1
    results["stale_gate_preimage"] = rejected(
        lambda: apply_frames(parent, bad_record, list(record["groups"])),
        "gate edit preimage",
    )
    bad_record = deepcopy(record)
    bad_record["frame_edits"].append(deepcopy(record["frame_edits"][0]))
    results["extra_edit"] = rejected(
        lambda: edit_groups(bad_record), "139 declared gate edits"
    )
    return results


def provider_audit(tag, data):
    parent, final = (data[f"data/{kind}-{tag}.json.gz"] for kind in ("PARENT", "WORD"))
    record, prices = (
        data["data/STAGE1-FRAME-EDITS.json"],
        data["construction/STAGE-PRICES.json"],
    )
    before = ledger(parent)
    child = apply_frames(parent, record, list(record["groups"]))
    child["report"]["local_profile"] = record["declared_local_profile"]
    child["report"]["width_inventory"] = record["declared_width_inventory"]
    joint, after = ledger(child), ledger(final)
    groups = group_audit(parent, record, before, prices)
    summed = Counter()
    for result in groups.values():
        summed.update(result["profile_delta"])
    require(
        {r: n for r, n in summed.items() if n}
        == difference(joint["profile"], before["profile"]),
        "isolated groups add to complete stage one",
    )
    namespaces = [cleanup_namespace(word) for word in (parent, child, final)]
    require(
        [n["private_buffers"] for n in namespaces] == [86, 86, 91],
        "all buffers charged",
    )
    stage_delta = difference(joint["profile"], before["profile"])
    require(stage_delta == {1: -4, 2: 90, 3: -50, 4: -2, 5: -8}, "stage-one paid delta")
    return {
        "parent": {k: v for k, v in before.items() if k != "events"},
        "stage_one": {k: v for k, v in joint.items() if k != "events"},
        "final": {k: v for k, v in after.items() if k != "events"},
        "groups": groups,
        "V45_subsets": subset_audit(parent, record, before, prices),
        "cleanup_namespaces": namespaces,
        "controls": controls(parent, child, record),
        "chronological_event_sha256": [
            hashlib.sha256(
                json.dumps(x["events"], separators=(",", ":")).encode()
            ).hexdigest()
            for x in (before, joint, after)
        ],
    }


def conditional_invoice(data, providers):
    order, dispatch = data["allocation/ORDER.json"], data["allocation/DISPATCH.json"]
    require(len(order) == len(dispatch) == 666, "666 complete calls")
    require(len({tuple(pair) for pair in order}) == 666, "unique calls")
    require([row[:2] for row in dispatch] == order, "ordered dispatch binding")
    tags = {"gauge44": "base", "extra": "extra"}
    counts = Counter(row[2] for row in dispatch)
    require(set(counts) <= set(tags), "known providers")
    local = Counter()
    for provider, count in counts.items():
        local.update(
            {
                r: n * count
                for r, n in providers[tags[provider]]["final"]["profile"].items()
            }
        )
    claimed = {int(r): n for r, n in data["allocation/PROFILE.json"].items()}
    remainder = difference(claimed, local)
    require(
        all(n >= 0 for n in remainder.values()), "nonnegative claimed residual invoice"
    )
    return {
        "calls": dict(counts),
        "derived_local_profile": dict(sorted(local.items())),
        "source_claimed_complete_profile": claimed,
        "conditional_idle_remainder": remainder,
        "warning": "Remainder is subtraction from a source claim, not an owner replay. "
        "PR2987 independently checks the packing bridge; native and physical admission remain separate.",
    }


def main():
    data = inputs()
    providers = {tag: provider_audit(tag, data) for tag in ("base", "extra")}
    report = {
        "status": "PASS_INDEPENDENT_RANK7_JOINT_FRAME_AUDIT",
        "providers": providers,
        "invoice_boundary": conditional_invoice(data, providers),
        "scope": "Finite chronological frame paths, exact symbolic paid deltas and cleanup syntax/names only. "
        "Surrogate margins do not certify the complete physical cost or a new kappa.",
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
