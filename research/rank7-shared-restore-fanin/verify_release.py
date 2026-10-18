#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check retained release bindings, not a substitute for a fresh native replay."""

import copy
from fractions import Fraction

import reproduce
import rewrite as rw
import verify as v

REQUIRED = {
    "RESULT.json",
    "ADMISSION-RESULT.json",
    "NATIVE-RECEIPT.json",
    "RELEASE-RECEIPT.json",
    "SOURCE-MANIFEST.json",
    "EDIT-DERIVATION.json",
    "STAGES.json",
    "RECIPE.json",
    "WORD-base.json.gz",
    "WORD-extra.json.gz",
    "INVOICE.json.gz",
}


def load():
    directory = v.PACKAGE / "evidence"
    bindings = v.read(directory / "BINDINGS.json")
    allowed = REQUIRED | {"ENVIRONMENT.json", "ADMISSION-STAGES.json"}
    allowed |= {
        "logs/" + name + ".log.txt" for name in ["source-preflight", *reproduce.NAMES]
    }
    rw.need(REQUIRED <= set(bindings) <= allowed, "closed retained evidence inventory")
    hashes = {}
    for name, expected in bindings.items():
        path = directory / name
        rw.need(not path.is_symlink() and path.is_file(), "regular retained evidence")
        hashes[name] = v.digest(path)
        rw.need(hashes[name] == expected, "retained evidence hash: " + name)
    records = {
        name: v.read(directory / name) for name in REQUIRED if not name.endswith(".gz")
    }
    records["words"] = {
        variant: v.read(directory / f"WORD-{variant}.json.gz")
        for variant in ("base", "extra")
    }
    records["invoice"] = v.read(directory / "INVOICE.json.gz")
    return records, hashes


def validate_bindings(records, hashes):
    result = records["RESULT.json"]
    admission, native = records["ADMISSION-RESULT.json"], records["NATIVE-RECEIPT.json"]
    release = records["RELEASE-RECEIPT.json"]
    derivation = records["EDIT-DERIVATION.json"]
    rw.need(
        result["status"] == "PASS_SHARED_RESTORE_COMPLETE_RELEASE", "composed release"
    )
    rw.need(
        admission["status"] == "PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE",
        "admission",
    )
    rw.need(
        native["status"]
        == "PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE",
        "native status",
    )
    rw.need(native["fresh_current_provider_count"] == 2, "both fresh providers")
    rw.need(release["status"] == "PASS_RELEASE", "outer release")
    rw.need(result["fresh_retained_bootstrap"] is True, "fresh retained bootstrap")
    source = hashes["SOURCE-MANIFEST.json"]
    rw.need(
        result["source_manifest_sha256"]
        == admission["source_manifest_sha256"]
        == native["manifest_sha256"]
        == derivation["manifest_sha256"]
        == source,
        "same actual source",
    )
    rw.need(
        admission["source_profile"] == "rank7-shared-restore-fanin", "new source label"
    )
    rw.need(
        admission["native_receipt_sha256"] == hashes["NATIVE-RECEIPT.json"],
        "native binding",
    )
    rw.need(
        admission["release_receipt_sha256"]
        == result["release_receipt_sha256"]
        == hashes["RELEASE-RECEIPT.json"],
        "outer binding",
    )
    rw.need(
        result["admission_sha256"] == hashes["ADMISSION-RESULT.json"],
        "admission binding",
    )
    rw.need(
        admission["package_manifest_sha256"] == release["manifest_sha256"],
        "admitted package",
    )


def validate_endpoint(records):
    result, admission = records["RESULT.json"], records["ADMISSION-RESULT.json"]
    release = records["RELEASE-RECEIPT.json"]
    rw.need(
        {int(k): n for k, n in admission["profile"].items()} == v.EXPECTED,
        "full paid profile",
    )
    rw.need(
        {int(k): n for k, n in result["profile"].items()} == v.EXPECTED,
        "same complete bill",
    )
    rw.need(
        admission["replicas"] == 74 and admission["actual_expected_helpers"] == 408,
        "T74 helper census",
    )
    finite = v.read(v.PACKAGE / "evidence/FINITE.json")
    lower = Fraction(finite["moment"]["root"][0])
    expected = (
        Fraction((lower * 10**24).__floor__(), 10**24)
        - Fraction(1, 10**46)
        - Fraction(1, 10**70)
    )
    rw.need(
        Fraction(result["kappa"])
        == Fraction(admission["kappa"])
        == Fraction(release["kappa_decimal"])
        == expected,
        "exact strict released endpoint",
    )
    return finite, expected


def validate(records, hashes):
    validate_bindings(records, hashes)
    finite, expected = validate_endpoint(records)
    validate_invoice(records["invoice"])
    validate_words(
        records,
        hashes,
        finite,
        records["NATIVE-RECEIPT.json"],
        records["SOURCE-MANIFEST.json"],
    )
    stages = records["STAGES.json"]
    rw.need(
        [s["stage"] for s in stages] == ["source-preflight", *reproduce.NAMES],
        "complete fresh stages",
    )
    for entry in stages:
        rw.need(entry["exit_code"] == 0, "successful actual stage")
        name = "logs/" + entry["stage"] + ".log.txt"
        rw.need(hashes[name] == entry["log_sha256"], "actual stage log binding")
    return str(expected)


def validate_words(records, hashes, finite, native, manifest):
    for variant in ("base", "extra"):
        word = records["words"][variant]
        rw.need(
            v.canonical(word)
            == finite["variants"][variant]["R1R2"]["canonical_sha256"],
            "retained word equals the regenerated semantic payload",
        )
        name = f"new/borrow/words/BORROW-WORD-43{variant}.json.gz"
        rw.need(
            native["providers"][variant]["word_sha256"]
            == manifest[name]
            == hashes[f"WORD-{variant}.json.gz"],
            "native word and compiled source binding",
        )
        rw.need(len(word["helper_final"]) == 91, "all private buffers")
        rw.need(word["report"]["local_profile"] == rw.LOCAL, "actual local bill")
        rw.need(word["report"]["width_inventory"] == rw.INVENTORY, "unchanged widths")


def validate_invoice(invoice):
    rw.need(
        invoice["status"]
        == "PASS_INDEPENDENT_MIXED_ASYNC_SCALAR_PREFIX_AND_FINITE_INVOICE",
        "actual emitted-program invoice",
    )
    rw.need(
        invoice["physical"] == 66813
        and invoice["live"] == 66304
        and invoice["private_zero_buffers"] == 91,
        "all physical families and buffers",
    )
    local = {int(r): n for r, n in invoice["selected_local_paid_profile"].items()}
    rw.need(
        local == {int(r): 666 * n for r, n in rw.LOCAL.items()},
        "actual paid local calls",
    )
    rw.need(
        invoice["complete_invocation_sweeps"] == invoice["bridge_sweeps"] == 666,
        "all invocation and bridge sweeps",
    )
    block = invoice["blocknorm"]
    rw.need(
        block["physical_families"] == 66813 and block["stock_l2_bits"] == 1322,
        "actual stock bound",
    )
    rw.need(
        block["local_actual_prefix_bits"] == 93
        and invoice["global_prefix_bits"] == block["actual_prefix_bits"] == 1475,
        "actual local/global prefixes",
    )
    rw.need(
        block["required_reserve_bits"]
        == 1510
        <= invoice["charged_prefix_bits"]
        == block["retained_payload_bits"]
        == 2048,
        "charged prefix allowance",
    )
    checks = invoice["strict_checks"]
    rw.need(
        len(checks) == 9 and all(value is True for value in checks.values()),
        "all strict finite invoice checks",
    )


def controls(records, hashes):
    names = [
        "native-count",
        "paid-profile",
        "stale-kappa",
        "source-manifest",
        "native-word",
        "missing-stage",
        "derivation",
        "private-buffer",
        "prefix",
        "missing-sweep",
    ]
    for name in names:
        mutant = copy.deepcopy(records)
        if name == "native-count":
            mutant["NATIVE-RECEIPT.json"]["fresh_current_provider_count"] = 1
        elif name == "paid-profile":
            mutant["ADMISSION-RESULT.json"]["profile"]["1"] += 1
        elif name == "stale-kappa":
            mutant["RESULT.json"]["kappa"] = "0.001729152756004330934535"
        elif name == "source-manifest":
            mutant["ADMISSION-RESULT.json"]["source_manifest_sha256"] = "0" * 64
        elif name == "native-word":
            mutant["NATIVE-RECEIPT.json"]["providers"]["base"]["word_sha256"] = "0" * 64
        elif name == "missing-stage":
            mutant["STAGES.json"].pop(3)
        elif name == "derivation":
            mutant["EDIT-DERIVATION.json"]["manifest_sha256"] = "0" * 64
        elif name == "private-buffer":
            mutant["invoice"]["private_zero_buffers"] = 90
        elif name == "prefix":
            mutant["invoice"]["charged_prefix_bits"] = 1474
        else:
            mutant["invoice"]["bridge_sweeps"] = 665
        try:
            validate(mutant, hashes)
        except ValueError:
            continue
        raise ValueError("accepted release mutant: " + name)
    return len(names)


def main():
    v.authenticate()
    records, hashes = load()
    kappa = validate(records, hashes)
    count = controls(records, hashes)
    print("PASS_SHARED_RESTORE_RECORDED_RELEASE", kappa, "controls=" + str(count))


if __name__ == "__main__":
    main()
