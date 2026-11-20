#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay the mixed-cutoff BIT supplier and its full conditional application."""

import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import shutil
import sys
from urllib.request import urlopen

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from bit_certificate import (
    CLASSES, COVER_LOSS, FLOOR, POWER, TRIAL, UNIFORM_LOSS,
    delayed_cover_and_stock, physical_witnesses, product_account,
    separated_moments, uniform_carrier,
)

PRED = Path("7786/research/p104-iterated-returns")
CHAIN = Path("7830/research/p104-chart306-chain")
GRADE14 = Path("7835/research/p104-grade14-paid-cut")
REBALANCED = Path("7831/research/p104-bit-tail-rebalance")
RAW = "https://raw.githubusercontent.com"
BASE_BIT = "d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d"
BASE_RATIONAL = "7660985e0b618cdbee13e4190a4c6d5f91fbdf01a8f7a5186fdde8b980c19b48"
LAYOUT = "f7de788c4a559282d35a9fce42f841a0e8de5a4015db871e718f9245569b0aa7"
EXPECTED = Q("0.00387992803556")
OLD_BOUND = Q("0.00387990740712")
ENROLLED = Q("0.003889928046155")


def check(condition, message):
    if not condition:
        raise ValueError(message)


def digest(content):
    return sha256(content).hexdigest()


def read(path):
    raw = path.read_bytes()
    if raw.startswith(b"\x1f\x8b"):
        raw = gzip.decompress(raw)
    return json.loads(raw)


def write(path, value):
    path.write_bytes((json.dumps(value, indent=2, sort_keys=True) + "\n").encode())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def pinned_inputs(work, fetch):
    locks = read(HERE / "SOURCES.json")
    for item in locks:
        prefix = item["cache_key"] if "cache_key" in item else str(item["pr"])
        path = work / prefix / item["path"]
        if not path.exists() and fetch:
            url = f"{RAW}/{item['repo']}/{item['head']}/{item['path']}"
            with urlopen(url, timeout=45) as response:
                data = response.read()
            check(digest(data) == item["sha256"], f"fetched SHA-256 {item['path']}")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        check(digest(path.read_bytes()) == item["sha256"], f"source SHA-256 {item['path']}")
    return len(locks)


def finite_bit(work, out):
    package = work / PRED
    source = work / "cache/source"
    parent = work / "cache/parent"
    binary = load("candidate_finite", package / "binary/finite.py")
    for name, pin in binary.SOURCE_PINS.items():
        binary.pinned(source / name, pin)
    for name, pin in binary.PACKAGE_PINS.items():
        binary.pinned(parent / name, pin)
    literal = binary.load(parent / "binary/independent/literal.py", "literal")
    price = binary.load(parent / "binary/independent/price.py", "directed_price")
    credited = binary.load(source / binary.FINITE, "credited_trim")
    baseline = literal.candidate_word(parent / "binary/WORD.json.gz")
    caller = literal.pinned(source / binary.PAIRED / "EFREE-CALLER.json.gz", literal.CALLER_SHA)
    word = package / "binary/WORD.json.gz"
    native = binary.candidate_receipt(literal, word, BASE_BIT, baseline, caller)

    predecessor = read(package / "binary/INDEPENDENT.json")
    paid, targets = native["paid"], native["targets"]
    for actual, previous in ((paid, "complete_paid"), (targets, "complete_productive")):
        check(actual == Counter({int(k): v for k, v in predecessor[previous].items()}),
              f"matches the pinned {previous} histogram")
    grade14 = read(work / GRADE14 / "BIT.json")
    check(json.loads(json.dumps(native)) == grade14["native"] and native["ordinary"] == predecessor["ordinary"],
          "literal paid, productive and ordinary comparison in both orientations")
    signed = price.signed_profile(targets, paid)
    crossing, signs, derivative = binary.exact_crossing(price, signed)
    check(crossing == grade14["raw_crossing"] == ["0.003879928046154", "0.003879928046155"]
          and TRIAL < Q(crossing[0]) and price.moment(signed, TRIAL)[0] > 0,
          "strict finite trial below the raw signed crossing")
    enrolled_margin = price.moment(signed, ENROLLED)
    check(enrolled_margin[1] < 0, "same BIT profile has a deficit at the enrolled target")
    inventories, separation = separated_moments(price, credited.E, paid, targets)
    witnesses, controls = physical_witnesses(literal, read(word), caller, paid)
    uniform = uniform_carrier(price, credited.E, paid, targets)
    check(POWER < grade14["separation"]["tensor_power"] and uniform["H"] < grade14["uniform"]["H"],
          "smaller product and uniform carrier than the pinned grade-14 schedule")
    old = Q(read(source / binary.CLAIM)["admitted_BIT_saving"])
    check(old == Q("0.00385248"), "pinned completed ordinary seed")
    stock = delayed_cover_and_stock(price, uniform, old)
    result = dict(
        status="PASS_MIXED_CUTOFF_BIT_FINITE", word_sha256=BASE_BIT, native_calls=native["native_calls"],
        native=native, raw_crossing=crossing, endpoint_margins=signs,
        derivative_upper=price.decimal_interval((derivative, derivative), 12)[1],
        enrolled_target_margin=price.decimal_interval(enrolled_margin),
        separation=separation, uniform=uniform, delayed_cover_and_stock=stock,
        ordinary_admitted=stock["admitted"], tuple_witnesses=witnesses, partition_controls=controls,
        product=product_account(native, inventories),
    )
    write(out / "BIT.json", result)
    return result, price


def rational_application(work, out, bit, price):
    package = work / PRED
    chain = work / CHAIN
    bit_path = out / "BIT.json"
    application_path = out / "APPLICATION.json"
    audit_path = out / "AUDIT.json"

    # The consumer uses the same literal BIT word with our independently
    # recomputed finite admission receipt. Keep both public sources immutable.
    adapter = out / "input"
    (adapter / "binary").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(package / "SOURCE-LOCK.json", adapter / "SOURCE-LOCK.json")
    shutil.copyfile(package / "binary/WORD.json.gz", adapter / "binary/WORD.json.gz")
    shutil.copyfile(bit_path, adapter / "binary/FINITE.json")
    cap_pin = digest(bit_path.read_bytes())
    common = dict(cache=work / "cache", word=chain / "DOUBLE-CANDIDATE.json.gz",
                  layout=package / "continuation/LAYOUT.json.gz", word_sha=BASE_RATIONAL, layout_sha=LAYOUT)
    qualifier = load("expanded_qualifier", package / "continuation/qualify.py")
    qualifier.BIT_FINITE_PIN = cap_pin
    reference = package / "evidence/application.json"
    app = qualifier.qualify(argparse.Namespace(**common, package=adapter,
                                               e40b_receipt=reference, out=application_path))
    write(application_path, app)
    app = read(application_path)
    check(app["binary_word"] == bit["word_sha256"]
          and Q(app["binary_ordinary"]) == Q(bit["ordinary_admitted"]), "BIT consumer consumes recomputed cap")

    audit = load("expanded_audit", package / "continuation/audit_expanded.py")
    audit.BINARY_INDEPENDENT_SHA = cap_pin
    audit.main(argparse.Namespace(**common, receipt=application_path, binary_receipt=bit_path,
                                  reference_application=reference, out=audit_path))
    checked = read(audit_path)
    grade14_audit = read(work / GRADE14 / "AUDIT.json")
    for name in ("schema", "word", "layout", "actual_grid_fixture", "basis_grid", "scalar_plans",
                 "common_root", "ordinary", "signed", "premises"):
        check(checked[name] == grade14_audit[name], f"exact #7835 rational audit comparison for {name}")
    old = read(chain / "DOUBLE-APPLICATION.json")
    check(Q(old["application"]["claim"]) == OLD_BOUND, "comparison matches pinned PR #7830 bound")
    for name in ("invoice", "ordinary", "bracket"):
        check(old["application"][name] == app["application"][name], f"retained rational {name}")
    claim = app["application"]["claim"]
    grade14 = read(work / GRADE14 / "RESULT.json")
    rebalanced = read(work / REBALANCED / "RESULT.json")
    for reference in (grade14, rebalanced):
        check(reference["binary_word"] == BASE_BIT and reference["rational_word"] == BASE_RATIONAL
              and reference["rational_raw_bracket"] == app["application"]["bracket"] and reference["premises"] == app["premises"],
              "pinned predecessor scope")
    check(Q(claim) == EXPECTED and Q(claim) == Q(checked["outer"]["claim"])
          and Q(rebalanced["claim"]) < Q(grade14["claim"]) < EXPECTED
          and EXPECTED < Q(bit["raw_crossing"][1]) < ENROLLED,
          "independent end-to-end comparison and fixed-profile ceiling")
    invoice = app["application"]["invoice"]
    bins = (Counter({int(rank): n for rank, n in invoice[key].items()}) for key in ("targets", "paid"))
    signed = price.signed_profile(*bins)
    target_margin = price.moment(signed, ENROLLED)
    check(price.derivative_bound(signed, ENROLLED) < 0 and target_margin[1] < 0,
          "complete rational signed deficit through the enrolled target")
    return app, checked, price.decimal_interval(target_margin)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", required=True, type=Path, help="immutable source cache root")
    parser.add_argument("--out", required=True, type=Path, help="new evidence directory")
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--bit-only", action="store_true")
    args = parser.parse_args()
    check(__debug__, "verification requires assertions")
    work, out = args.work.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    explicit = pinned_inputs(work, args.fetch)
    prepare = load("source_preparer", work / PRED / "prepare_sources.py")
    count = prepare.sources(work / "cache", args.fetch)
    print(f"Authenticated {explicit} explicit and {count} inherited sources.", flush=True)
    bit, price = finite_bit(work, out)
    print("PASS_MIXED_CUTOFF_BIT_FINITE", bit["ordinary_admitted"], flush=True)
    if args.bit_only:
        return
    app, audit, target_margin = rational_application(work, out, bit, price)
    result = dict(
        status="PASS_COMPLETE_CONDITIONAL_APPLICATION", rational_word=BASE_RATIONAL, binary_word=BASE_BIT,
        binary_ordinary=bit["ordinary_admitted"], native_calls=dict(rational=48, binary=36),
        binary_raw_bracket=bit["raw_crossing"], rational_raw_bracket=app["application"]["bracket"],
        binary_enrolled_target_margin=bit["enrolled_target_margin"], rational_enrolled_target_margin=target_margin,
        claim=app["application"]["claim"], gain_over_7835="0.00000000000955",
        gain_over_7831="0.00000000001050", enrolled_target="0.003889928046155",
        gap_to_enrolled_target="0.000010000010595", premises=app["premises"],
        sharp_outer=audit["outer"]["outer_checks"], power=POWER,
        paid_cutoffs={name: base for name, base, _ in CLASSES}, productive_floor=FLOOR,
        uniform_loss=str(UNIFORM_LOSS), delayed_cover_loss=str(COVER_LOSS),
        log_power=bit["uniform"]["log_power"], log2_carrier=bit["uniform"]["H"],
    )
    check(EXPECTED - Q(read(work / GRADE14 / "RESULT.json")["claim"]) == Q(result["gain_over_7835"])
          and EXPECTED - Q(read(work / REBALANCED / "RESULT.json")["claim"]) == Q(result["gain_over_7831"])
          and ENROLLED - EXPECTED == Q(result["gap_to_enrolled_target"]), "exact headline differences")
    write(out / "RESULT.json", result)
    print("PASS_COMPLETE_CONDITIONAL_APPLICATION", result["claim"], flush=True)


if __name__ == "__main__":
    main()
