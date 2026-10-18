"""Native coverage and semantic controls for the enlarged private-free roots.

The native selector and exact Gaussian kernel are credited retained tools.
The new value and forward-provenance algorithms are in lifetimes.py.
SPDX-License-Identifier: Apache-2.0
"""
from collections import Counter
from copy import deepcopy
import json
import sys

import audit_io as io
import lifetimes as life


def rejected(action, text):
    try:
        action()
    except (ValueError, KeyError) as error:
        io.require(text in str(error), "wrong semantic rejection: " + str(error))
        return str(error)
    raise ValueError("semantic control unexpectedly passed: " + text)


def value_controls(events, original, backward, closure):
    """A real uncovered cleanup coefficient changes one free, not the old roots."""
    index = 17254 if backward else 17256
    io.require(index not in closure["old_pair"]["event_indices"], "mutant outside predecessor cone")
    expected = ["add", "Z395", "L96", -4, 1] if backward else ["add", "Z395", "L5", -1, 1]
    io.require(events[index][1] == expected, "literal uncovered mutation preimage")
    mutant = deepcopy(events)
    mutant[index][1][3] *= -1
    changed = life.values(mutant, original, backward, strict=False)
    failed = [row for row in changed["frees"] if row["value"]]
    io.require([row["role"] for row in failed] == ["Z395"], "exact peer failure set")
    io.require(all(not word for _, word, _ in failed[0]["value"]), "concrete scalar witness has no warp symbols")
    io.require(changed["helper249"] == [["L249", [], "1"]], "old helper root unchanged")
    io.require(next(row for row in changed["frees"] if row["role"] == "Z249")["value"] == [],
               "old private root unchanged")
    failure = rejected(lambda: life.values(mutant, original, backward), "nonzero private free Z395")
    allocation = next(i for i, e in enumerate(events) if e == ["zero_buffer", "alloc", "Z395"])
    early = deepcopy(events)
    early.insert(allocation + 1, ["zero_buffer", "free", "Z395"])
    early_failure = rejected(lambda: life.values(early, original, backward), "private use outside lifetime")
    early_graph = rejected(lambda: life.provenance(early, original), "provenance private lifetime")
    return {"uncovered_sign_flip": {"event": index, "original": json.loads(json.dumps(events[index])),
                "private_failure": failed[0], "old_helper_and_private_still_pass": True,
                "rejection": failure},
            "premature_free_value_rejection": early_failure,
            "premature_free_graph_rejection": early_graph}


def native_coverage(native, kernel, events, closure, data, backward, progress=False):
    """Check EVERY expanded native class, including previously reported classes."""
    canonical, recipes, adapters = data["canonical"], data["recipes"], data["adapters"]
    old = native.classes(events, closure["old_pair"]["event_indices"], canonical)
    enlarged = native.classes(events, closure["expanded"]["event_indices"], canonical)
    io.require(set(old) <= set(enlarged), "native coverage is monotone")
    checked, added, identity_records = set(), [], []
    for n, (key, indices) in enumerate(sorted(enlarged.items(), key=lambda row: native.stable_key(row[0]))):
        candidate, reference, record = native.selected(kernel, key, canonical, recipes, adapters)
        payload = json.dumps([candidate, reference, record, backward], sort_keys=True, separators=(",", ":"))
        if payload not in checked:
            native.check(kernel, key, canonical, recipes, adapters, backward)
            checked.add(payload)
        identity_records.append([list(key), io.digest(json.loads(payload)), indices])
        if key not in old:
            added.append({"class": list(key), "events": indices})
        if progress and n % 200 == 0:
            print("native classes " + str(n + 1) + "/" + str(len(enlarged)), file=sys.stderr, flush=True)
    io.require(added, "nonempty added native coverage")
    child_key = next(tuple(row["class"]) for row in added if row["class"][0] == "child")
    changed = deepcopy(recipes)
    selected = next(row for row in changed["children"] if (row["old"], row["new"]) == child_key[1:])
    selected["left"]["phase"] = (selected["left"]["phase"] + 1) % 4
    failure = rejected(lambda: native.check(kernel, child_key, canonical, changed, adapters, backward),
                       "exact native class mismatch")
    return {"previous_classes": len(old), "expanded_classes": len(enlarged),
            "new_classes": len(added), "new_by_kind": dict(sorted(Counter(row["class"][0] for row in added).items())),
            "new_class_associations": added, "all_class_bindings_sha256": io.digest(identity_records),
            "distinct_exact_identities_checked": len(checked), "columns_per_identity": 512,
            "includes_global_phase": True, "all_expanded_classes_replayed": True,
            "new_class_phase_control": {"class": list(child_key), "rejection": failure},
            "method": "PR3038 retained native selector and credited independent exact Gaussian kernel; new root coverage"}


def invoice(blobs, private_count):
    claim = json.loads(blobs["research/rank7-joint-endframes/CLAIM.json"])
    frame = json.loads(blobs["research/rank7-joint-frame-audit/RESULT.json"])["invoice_boundary"]
    frozen = json.loads(blobs["research/rank7-v45-frozen-owner-invoice/RESULT.json"])
    io.require(private_count == claim["zero_buffers"] == 91, "all charged private names discharged")
    total = claim["live_families"] + claim["helpers"] + 8 + private_count + 2
    io.require(total == claim["physical_families"] == 66813, "source-declared complete stock sum")
    profile = {int(k): v for k, v in claim["profile"].items()}
    local = {int(k): v * claim["calls"] for k, v in claim["local_profile"].items()}
    idle = {k: profile.get(k, 0) - local.get(k, 0) for k in profile.keys() | local.keys()}
    idle = {str(k): v for k, v in sorted(idle.items()) if v}
    io.require(all(v >= 0 for v in idle.values()), "nonnegative claimed idle remainder")
    io.require(idle == frame["conditional_idle_remainder"], "source-claim invoice reconciliation")
    cases = [row for row in frozen["cases"] if row["helpers"] in ([249], [249, 251, 265, 267])]
    io.require(len(cases) == 2, "joint and single controls retained")
    controls = []
    for row in cases:
        delta = {int(k): v for k, v in row["complete_delta"].items()}
        io.require(sum(k * v for k, v in delta.items()) == 0, "frozen-parent signed rank mass")
        io.require(delta[4] < 0 and all(v > 0 and k < 4 for k, v in delta.items() if k != 4),
                   "strict positive moment difference for a > 0")
        controls.append({"helpers": row["helpers"], "complete_delta": row["complete_delta"]})
    return {"changed_costs": "none: no event, allocation or tariff is changed",
            "private_families": private_count, "live_families": claim["live_families"],
            "helper_families": claim["helpers"], "center_families": 8, "other_families": 2,
            "source_declared_physical_families": total, "source_claimed_complete_profile": claim["profile"],
            "conditional_idle_remainder": idle, "frozen_parent_controls": controls,
            "status": "source-bound arithmetic trace; allocation, physical stock and moment admission not replayed"}
