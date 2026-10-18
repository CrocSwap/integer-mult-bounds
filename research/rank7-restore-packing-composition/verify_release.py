#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check published receipt bindings; this does not rerun the full source chain."""

import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import verify

PACKAGE = Path(__file__).resolve().parent
EVIDENCE = PACKAGE / "evidence"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(full, admission, release, native, finite, bindings):
    need = verify.need
    need(full["status"] == "PASS_RESTORE_PACKING_COMPLETE_RELEASE", "composition release")
    need(admission["status"] == "PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE", "admission")
    need(release["status"] == "PASS_RELEASE", "release")
    need(full["fresh_retained_bootstrap"] is True, "fresh retained bootstrap")
    need(full["admission_result_sha256"] == bindings["admission"], "admission receipt binding")
    need(full["release_receipt_sha256"] == admission["release_receipt_sha256"] ==
         bindings["release"], "release receipt binding")
    need(admission["native_receipt_sha256"] == bindings["native"], "native receipt binding")
    need(full["fill_sha256"] == admission["fill_sha256"], "full-run container binding")
    need(full["fill_payload_sha256"] == bindings["fill_payload"], "canonical composed fill")
    expected_source = verify.read(PACKAGE / "vendor/pr3015/CLAIM.json")["source_manifest_sha256"]
    need(admission["source_manifest_sha256"] == native["manifest_sha256"] ==
         expected_source, "exact PR3015 native source")
    need(native["fresh_current_provider_count"] == 2, "both current native providers")
    need(native["status"] == "PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE",
         "complete native receipt")
    need({int(k): v for k, v in admission["profile"].items()} == verify.EXPECTED,
         "composed complete invoice")
    need(admission["package_manifest_sha256"] == release["manifest_sha256"], "released package")
    endpoint = Fraction(full["kappa"])
    need(endpoint == Fraction(admission["kappa"]) == Fraction(release["kappa_decimal"]),
         "same released endpoint")
    baseline = Fraction(verify.read(PACKAGE / "vendor/pr3015/CLAIM.json")["kappa"])
    need(Fraction(full["comparison_kappa"]) == baseline, "pinned PR3015 comparator")
    need(endpoint > baseline and endpoint < Fraction(finite["new_root"][0]), "strict valid gain")
    need(Fraction(full["gain"]) == endpoint - baseline, "exact released gain")
    stages = full["stages"]
    need(1 <= len(stages) <= 20 and all(s["exit_code"] == 0 for s in stages), "successful stages")
    need(sum(s["stage"] == "fresh-retained-bootstrap" for s in stages) == 1,
         "one fresh retained bootstrap")
    need(finite["physical"] == 66813 and finite["private_buffers"] == 91, "physical bill")


def run():
    finite = verify.run()
    canonical_finite = json.loads(json.dumps(finite, sort_keys=True))
    verify.need(canonical_finite == verify.read(EVIDENCE / "FINITE.json"), "replayed finite receipt")
    names = ["COMPOSITION-RESULT.json", "ADMISSION-RESULT.json",
             "RELEASE-RECEIPT.json", "NATIVE-RECEIPT.json"]
    records = [verify.read(EVIDENCE / name) for name in names]
    raw = (json.dumps(verify.composed_fill(), sort_keys=True, separators=(",", ":")) + "\n").encode()
    bindings = {"admission": digest(EVIDENCE / names[1]),
                "release": digest(EVIDENCE / names[2]), "native": digest(EVIDENCE / names[3]),
                "fill_payload": hashlib.sha256(raw).hexdigest()}
    validate(*records, finite, bindings)
    for stage in records[0]["stages"]:
        name = stage["stage"]
        verify.need(len(name) <= 64 and name.replace("-", "").isalnum(), "stage log name")
        verify.need(digest(EVIDENCE / "logs" / (name + ".log.txt")) == stage["log_sha256"],
                    "exact full-replay log")
    controls = [(1, "profile", {"1": 1644348}),
                (1, "fill_sha256", "0" * 64),
                (2, "kappa_decimal", "1/100"),
                (3, "fresh_current_provider_count", 0)]
    for index, field, wrong in controls:
        changed = copy.deepcopy(records)
        changed[index][field] = wrong
        try:
            validate(*changed, finite, bindings)
        except ValueError:
            pass
        else:
            raise ValueError("stored receipt control accepted: " + field)
    return {"status": "PASS_PUBLISHED_COMPOSITION_RECEIPT_BINDINGS", "rejected_controls": 4,
            "kappa": records[0]["kappa"], "gain": records[0]["gain"],
            "scope": "Replayed finite invoice and stored full-release relations; no new full replay."}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
