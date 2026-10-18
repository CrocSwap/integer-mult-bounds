#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Recheck finite construction and published full-release relations, not a new cold replay."""

import copy
import gzip
import hashlib
import json
from fractions import Fraction

import verify

EVIDENCE = verify.PACKAGE / "evidence"


def validate(full, admission, release, native, finite, bindings, invoice):
    need = verify.need
    need(full["status"] == "PASS_T148_R1_COMPLETE_RELEASE", "T148 complete release")
    need(admission["status"] == "PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE", "admission")
    need(release["status"] == "PASS_RELEASE", "release")
    need(full["replicas"] == admission["replicas"] == 148, "actual doubled replica count")
    need(full["fresh_retained_bootstrap"] is True, "fresh retained bootstrap")
    need(full["admission_result_sha256"] == bindings["admission"], "admission receipt")
    need(full["release_receipt_sha256"] == admission["release_receipt_sha256"] == bindings["release"],
         "release receipt")
    need(full["native_receipt_sha256"] == admission["native_receipt_sha256"] == bindings["native"],
         "native receipt")
    for key in ("fill_sha256", "order_sha256", "dispatch_sha256"):
        need(full[key] == admission[key], "admission input: " + key)
    need(full["fill_payload_sha256"] == finite["fill_payload_sha256"], "canonical fill")
    need(full["order_sha256"] == finite["order_sha256"] and
         full["dispatch_sha256"] == finite["dispatch_sha256"], "literal chronology and dispatch")
    need({int(k): n for k, n in admission["profile"].items()} == verify.EXPECTED,
         "complete paid profile")
    need(full["stock"] == finite["stock148"], "complete physical/prefix ledger")
    need(full["invoice_payload_sha256"] == bindings["invoice"], "actual complete invoice bytes")
    verify.check_invoice(invoice, finite)
    need(admission["package_manifest_sha256"] == release["manifest_sha256"], "admitted package")
    expected_source = verify.read(verify.PACKAGE / "vendor/pr3015/CLAIM.json")["source_manifest_sha256"]
    need(admission["source_manifest_sha256"] == native["manifest_sha256"] == expected_source,
         "exact R1 source")
    need(native["fresh_current_provider_count"] == 2 and native["status"] ==
         "PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE", "two fresh native providers")
    endpoint, previous = Fraction(full["kappa"]), Fraction(finite["comparison_kappa"])
    need(previous < endpoint < Fraction(finite["new_root"][0]), "strict valid gain over PR3021")
    need(endpoint == Fraction(admission["kappa"]) == Fraction(release["kappa_decimal"]), "same endpoint")
    need(Fraction(full["comparison_kappa"]) == previous and
         Fraction(full["gain"]) == endpoint - previous, "exact comparator/gain")
    names = ["source-preflight", *verify.retained("release_driver").RECIPE_NAMES]
    need([s["stage"] for s in full["stages"]] == names and
         all(s["exit_code"] == 0 for s in full["stages"]), "all successful fresh stages")


def run():
    finite = verify.run()
    verify.need(json.loads(json.dumps(finite)) == verify.read(EVIDENCE / "FINITE.json"),
                "replayed finite receipt")
    names = ["RESULT.json", "ADMISSION-RESULT.json", "RELEASE-RECEIPT.json", "NATIVE-RECEIPT.json"]
    records = [verify.read(EVIDENCE / name) for name in names]
    bindings = dict(zip(("admission", "release", "native"),
                        (verify.digest(EVIDENCE / name) for name in names[1:]), strict=True))
    invoice_bytes = gzip.decompress((EVIDENCE / "PREFIX-AND-INVOICE.json.gz").read_bytes())
    verify.need(len(invoice_bytes) <= 2_000_000, "published invoice bound")
    invoice = json.loads(invoice_bytes)
    bindings["invoice"] = hashlib.sha256(invoice_bytes).hexdigest()
    validate(*records, finite, bindings, invoice)
    for stage in records[0]["stages"]:
        name = stage["stage"]
        verify.need(len(name) <= 64 and name.replace("-", "").isalnum(), "log filename")
        verify.need(verify.digest(EVIDENCE / "logs" / (name + ".log.txt")) == stage["log_sha256"],
                    "full stage log")
    controls = [(1, "replicas", 74), (1, "profile", {"1": 3288704}),
                (1, "fill_sha256", "0" * 64), (2, "kappa_decimal", "1/100"),
                (3, "fresh_current_provider_count", 0), (0, "stock", {"physical": 132608})]
    for index, field, wrong in controls:
        changed = copy.deepcopy(records)
        changed[index][field] = wrong
        try:
            validate(*changed, finite, bindings, invoice)
        except ValueError:
            continue
        raise ValueError("accepted receipt control: " + field)
    for field, wrong in [("stock_l2_bits", 1322), ("physical_stock_bits", 2644),
                         ("required_reserve_bits", 1510), ("max_active_depth", 17)]:
        changed = copy.deepcopy(invoice)
        changed["blocknorm"][field] = wrong
        try:
            validate(*records, finite, bindings, changed)
        except ValueError:
            continue
        raise ValueError("accepted actual-invoice control: " + field)
    return dict(status="PASS_T148_STORED_RELEASE_BINDINGS", rejected_controls=len(controls) + 4,
                receipt_controls=len(controls), actual_invoice_controls=4,
                kappa=records[0]["kappa"], gain=records[0]["gain"],
                scope="Recomputed finite invoice and stored relations; no fresh cold replay.")


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
