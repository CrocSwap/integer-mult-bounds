#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Authenticate stored full-release relations and rematerialize its inputs.

This adapts PR3021's receipt audit. It does not run the full native/source chain.
"""

import copy
import gzip
import hashlib
import json
import tempfile
from fractions import Fraction
from pathlib import Path

import materialize as m
import reproduce

EVIDENCE = m.PACKAGE / "evidence"


def validate(records, finite, bindings, materialized):
    full, admission, release, native = records
    m.need(full["status"] == "PASS_T740_R1_COMPLETE_RELEASE", "composition release")
    m.need(admission["status"] == "PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE", "admission")
    m.need(release["status"] == "PASS_RELEASE", "outer release")
    m.need(full["fresh_retained_bootstrap"] is True, "fresh retained bootstrap")
    m.need(full["admission_result_sha256"] == bindings["admission"], "admission binding")
    m.need(full["release_receipt_sha256"] == admission["release_receipt_sha256"] ==
           bindings["release"], "release binding")
    m.need(admission["native_receipt_sha256"] == bindings["native"], "native binding")
    m.need(full["fill_sha256"] == admission["fill_sha256"], "full-run fill binding")
    m.need(full["fill_payload_sha256"] == materialized["payload_sha256"], "literal fill payload")
    m.need(admission["order_sha256"] == materialized["order_sha256"], "actual T740 order")
    m.need(admission["dispatch_sha256"] == materialized["dispatch_sha256"], "actual T740 dispatch")
    expected_source = m.read(m.PACKAGE / "vendor/pr3015/CLAIM.json")["source_manifest_sha256"]
    m.need(admission["source_manifest_sha256"] == native["manifest_sha256"] == expected_source,
           "exact R1 native source")
    m.need(native["status"] == "PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE"
           and native["fresh_current_provider_count"] == 2, "two fresh native providers")
    m.need(admission["replicas"] == 740, "admitted T740")
    m.need({int(k): v for k, v in admission["profile"].items()} == m.PROFILE,
           "complete composed invoice")
    m.need(admission["package_manifest_sha256"] == release["manifest_sha256"], "released package")
    endpoint = Fraction(full["kappa"])
    m.need(endpoint == Fraction(admission["kappa"]) == Fraction(release["kappa_decimal"]),
           "same released endpoint")
    outer = m.read(EVIDENCE / "OUTER-CLAIM.json")
    m.need(endpoint == Fraction(outer["kappa_rational"]) == Fraction(outer["kappa"]),
           "modern outer headline, separate from supplier-only claim")
    previous = Fraction(m.read(m.PACKAGE / "vendor/PR3021-RESULT.json")["kappa"])
    m.need(previous < endpoint < Fraction(finite["moment"]["root"][0]), "strict valid gain")
    baseline = Fraction(m.read(m.PACKAGE / "vendor/pr3015/CLAIM.json")["kappa"])
    m.need(Fraction(full["comparison_kappa"]) == baseline and
           Fraction(full["gain"]) == endpoint - baseline, "exact source comparison")
    stages = full["stages"]
    m.need([s["stage"] for s in stages] == ["source-preflight", *reproduce.RECIPE_NAMES],
           "complete fresh source recipe")
    m.need(all(s["exit_code"] == 0 for s in stages), "successful source stages")
    m.need(finite["physical"] == 663549 and finite["stock"]["buffers"] == 91, "physical bill")


def run():
    m.authenticate()
    raw_invoice = gzip.decompress((EVIDENCE / "DISCOVERY-INVOICE.json.gz").read_bytes())
    m.need(hashlib.sha256(raw_invoice).hexdigest() ==
           m.read(EVIDENCE / "INVOICE-PAYLOAD.json")["decompressed_sha256"], "invoice payload")
    invoice = json.loads(raw_invoice)
    m.need((invoice["physical"], invoice["global_prefix_bits"], invoice["charged_prefix_bits"])
           == (663549, 1477, 2048), "actual complete prefix/physical invoice")
    names = ["COMPOSITION-RESULT.json", "ADMISSION-RESULT.json",
             "RELEASE-RECEIPT.json", "NATIVE-RECEIPT.json"]
    records = [m.read(EVIDENCE / name) for name in names]
    finite = m.read(EVIDENCE / "FINITE.json")
    bindings = {"admission": m.digest(EVIDENCE / names[1]),
                "release": m.digest(EVIDENCE / names[2]),
                "native": m.digest(EVIDENCE / names[3])}
    with tempfile.TemporaryDirectory(prefix="t740-input-audit-") as temporary:
        materialized = m.build(Path(temporary))
    validate(records, finite, bindings, materialized)
    for stage in records[0]["stages"]:
        name = stage["stage"]
        m.need(len(name) <= 64 and name.replace("-", "").isalnum(), "stage log name")
        m.need(m.digest(EVIDENCE / "logs" / (name + ".log.txt")) == stage["log_sha256"],
               "exact fresh stage log")
    controls = [(1, "profile", {"1": 1}), (1, "order_sha256", "0" * 64),
                (1, "dispatch_sha256", "0" * 64), (1, "fill_sha256", "0" * 64),
                (2, "kappa_decimal", "1/100"), (3, "fresh_current_provider_count", 0)]
    for index, field, wrong in controls:
        changed = copy.deepcopy(records)
        changed[index][field] = wrong
        try:
            validate(changed, finite, bindings, materialized)
        except ValueError:
            continue
        raise ValueError("stored receipt mutant accepted: " + field)
    previous = Fraction(m.read(m.PACKAGE / "vendor/PR3021-RESULT.json")["kappa"])
    return {"status": "PASS_PUBLISHED_T740_RELEASE_BINDINGS", "rejected_controls": 6,
            "kappa": records[0]["kappa"],
            "gain_over_pr3021": str(Fraction(records[0]["kappa"]) - previous),
            "scope": "Rematerialized inputs and stored full-release relations; no new native replay."}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
