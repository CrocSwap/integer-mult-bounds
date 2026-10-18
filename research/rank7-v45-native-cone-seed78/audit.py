# SPDX-License-Identifier: Apache-2.0
"""Join source completeness, endpoint closure, and every reached native class.

Substantial OpenAI Codex assistance. Exact primitive/native checks are separate
from inherited physical scalar, storage, precision and whole-supplier claims.
"""
from collections import Counter
import hashlib
import json


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def identity_payload(candidate, reference, record, backward):
    # The exact string, not its digest or local frame IDs, is the cache key.
    return canonical({"candidate": candidate, "reference": reference,
                      "selected_record": record, "inverse_transpose": backward})


def normalized_case(source, cone, oracle, word, canonical_word, program, backward):
    events, metadata = source.bind(word, canonical_word, program, backward)
    records, initial = cone.records(events, metadata["start"])
    primary = cone.reverse_demand(records, initial)
    independent = oracle.dependency_cone(records, initial)
    source.require(all(primary[k] == independent[k] for k in primary), "two independent cone algorithms disagree")
    included = primary["event_indices"]
    endpoints = cone.endpoints(events, backward, included)
    counts = Counter(events[i][0] for i in included)
    receipt = {"complete_source_events": len(events), "dependency_records": len(records),
               "cone_events": len(included), "by_kind": dict(sorted(counts.items())),
               "event_indices": included, "boundary_inputs": primary["boundary_inputs"],
               "ssa_versions": len(independent["versions"]), "endpoint_covectors": endpoints,
               "source_complete_binding": True, "closure_methods_agree": True,
               "coordinate_convention": "normalized source; chosen physical helper is F7/inverse F7 after wrappers",
               "peer_private_zero_return_proved": False}
    return events, included, receipt


def native_case(native, kernel, events, included, canonical_word, recipes, adapters,
                backward, checked, progress=None):
    inventory = native.classes(events, included, canonical_word)
    associations = []
    for number, (key, indices) in enumerate(sorted(inventory.items(), key=lambda row: native.stable_key(row[0]))):
        candidate, reference, record = native.selected(kernel, key, canonical_word, recipes, adapters)
        payload = identity_payload(candidate, reference, record, backward)
        reused = payload in checked
        if not reused:
            result = native.check(kernel, key, canonical_word, recipes, adapters, backward)
            checked[payload] = {"receipt_id": hashlib.sha256(payload.encode()).hexdigest(),
                                "columns": result["columns"], "global_phase_included": True,
                                "inverse_transpose": backward,
                                "selected_recipe_sha256": digest(result["selected_recipe"]),
                                "candidate_sha256": digest(candidate), "reference_sha256": digest(reference)}
        associations.append({"class": list(key), "event_indices": indices,
                             "identity_receipt": checked[payload]["receipt_id"],
                             "exact_payload_reused": reused})
        if progress is not None and number % 100 == 0:
            progress({"classes_completed": number + 1, "classes_total": len(inventory),
                      "distinct_identities_checked_so_far": len(checked), "inverse_transpose": backward})
    return {"classes": len(inventory), "by_kind": dict(sorted(Counter(key[0] for key in inventory).items())),
            "covered_native_events": sum(len(v) for v in inventory.values()),
            "associations": associations, "all_classes_discharged": True}


def provider(modules, word, canonical_word, programs, recipes, adapters, progress=None):
    source, cone, oracle, native, kernel = [modules[k] for k in ("source", "cone", "oracle", "native", "kernel")]
    source.require(set(programs) == {"forward", "backward"}, "both emitted orientations")
    checked, cases = {}, {}
    for orientation in ("forward", "backward"):
        backward = orientation == "backward"
        events, included, receipt = normalized_case(source, cone, oracle, word, canonical_word, programs[orientation], backward)
        receipt["native"] = native_case(native, kernel, events, included, canonical_word, recipes, adapters, backward, checked, progress)
        cases[orientation] = receipt
    receipts = sorted(checked.values(), key=lambda r: r["receipt_id"])
    source.require(len({r["receipt_id"] for r in receipts}) == len(receipts), "identity receipt digest collision")
    return {"status": "PASS_SOURCE_BOUND_CLOSED_ENDPOINT_NATIVE_CONE", "orientations": cases,
            "exact_native_identity_receipts": receipts, "distinct_native_identities": len(receipts),
            "columns_each_identity": 512, "new_supplier": False, "new_kappa": False,
            "scope": "Conditional normalized macro endpoint and covered native chart realization. Physical scalar/COPY/CLEAR contracts, peer-private zeros, ownership/storage, precision and whole-supplier admission remain open."}
