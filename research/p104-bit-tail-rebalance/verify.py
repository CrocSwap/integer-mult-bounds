#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Authenticate and replay the P104 BIT tensor recompile and both application checks."""

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
PRED = Path("7786/research/p104-iterated-returns")
CHAIN = Path("7830/research/p104-chart306-chain")
RAW = "https://raw.githubusercontent.com"
BASE_BIT = "d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d"
BASE_RATIONAL = "7660985e0b618cdbee13e4190a4c6d5f91fbdf01a8f7a5186fdde8b980c19b48"
LAYOUT = "f7de788c4a559282d35a9fce42f841a0e8de5a4015db871e718f9245569b0aa7"
TRIAL = Q("0.003879928045154")
LOSS = Q(1, 10**11)
POWER = 416
CUTOFF, FLOOR, AMBIENT = 10, 16, 134
PAID_TILT, TARGET_TILT = Q(11, 50), Q(3, 10)
EXPECTED = Q("0.00387992802506")
OLD_BOUND = Q("0.00387990740712")


def check(condition, message):
    if not condition:
        raise ValueError(message)


def digest(content):
    return sha256(content).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


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
        prefix = str(item["pr"])
        path = work / prefix / item["path"]
        if not path.exists() and fetch:
            url = f"{RAW}/{item['repo']}/{item['head']}/{item['path']}"
            with urlopen(url, timeout=45) as response:
                data = response.read()
            check(digest(data) == item["sha256"], f"fetched SHA-256 {item['path']}")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        check(digest(path.read_bytes()) == item["sha256"], f"source SHA-256 {item['path']}")


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
              f"independently verified {previous} is unchanged")
    check(native["ordinary"] == predecessor["ordinary"], "unchanged all-call ordinary charge")
    signed = price.signed_profile(targets, paid)
    crossing, signs, _ = binary.exact_crossing(price, signed)
    check(crossing == ["0.003879928046154", "0.003879928046155"], "raw signed BIT bracket")
    check(TRIAL < Q(crossing[0]), "strict finite trial below raw crossing")

    separation = credited.certificate(targets, paid, TRIAL, POWER, CUTOFF, FLOOR,
                                       PAID_TILT, TARGET_TILT)
    monomial_targets = price.moment(targets, TRIAL)
    ratios = (
        price.divide(price.moment(paid, TRIAL), monomial_targets),
        price.divide(price.moment(paid, TRIAL, PAID_TILT),
                     price.mul(price.exp_log(CUTOFF, PAID_TILT), monomial_targets)),
        price.divide(price.mul(price.exp_log(FLOOR, TARGET_TILT),
                               price.moment(targets, TRIAL, -TARGET_TILT)), monomial_targets),
    )
    upper = tuple(Q(value) for value in separation["rational_upper_limits"])
    check(all(Q(interval[1], price.GRID) <= bound for interval, bound in zip(ratios, upper)),
          "second interval implementation fits all three bounds")
    a, g, l = upper
    moment_upper = 1 / (1 + POWER * (1 - a)) + 2 * g**POWER + l**POWER
    check(moment_upper < 1, "strict moment after paid splitting and target debit")

    # Independent full-ambient check of the historical uniform certificate.
    uniform = credited.uniform_certificate(TRIAL, POWER, CUTOFF, FLOOR, AMBIENT, LOSS)
    theta, log_power = Q(uniform["theta"]), uniform["logarithm_power"]
    numerator, denominator = theta.as_integer_ratio()
    check(CUTOFF**denominator < FLOOR**numerator
          and 2 * CUTOFF**(POWER * denominator) <= AMBIENT**(POWER * numerator),
          "both shifted-log inequalities on the 134-base ambient")
    ambient_power = price.raise_interval(price.exp_log(AMBIENT, TRIAL), POWER)
    eta = price.scale(price.invert(ambient_power), 1 - TRIAL)
    check(theta**log_power < Q(eta[0], price.GRID)
          and Q(ambient_power[1], price.GRID) < 2**log_power,
          "independent uniform logarithmic majorant")
    horizon, residual = divmod(uniform["H"], LOSS.denominator)
    check(residual == 0 and (uniform["H"] + 1)**log_power < 2**horizon,
          "integer uniform cutoff")
    check(2**45 * LOSS > 256 and 1 + LOSS / 2 <= 2**horizon,
          "retained delayed cover inequalities at the new loss")

    # exhibit a different paid object even at the same tensor power:
    # 14^v was unsplit at cutoff 15^v, and is split at cutoff 10^v.
    check(paid[14] > 0 and CUTOFF**POWER < 14**POWER < 15**POWER,
          "rank-14 homogeneous paid tuple changes physical call subdivision")
    old = Q(read(source / binary.CLAIM)["admitted_BIT_saving"])
    rho = Q(1, 250)
    covered = TRIAL - 2 * LOSS
    steps, previous = [], old
    for _ in range(4):
        envelope = (1 - rho) * covered + rho * previous
        ticks = int(envelope * 10**15) - 1
        steps.append(f"0.{ticks:015d}")
        previous = Q(steps[-1])
    admitted, stages = price.bootstrap(old, covered, steps)
    check(admitted == Q(steps[-1]) and admitted > OLD_BOUND, "four strict stock stages")
    result = dict(status="PASS_REBALANCED_BIT_FINITE", word_sha256=BASE_BIT,
                  native_calls=native["native_calls"], native=native,
                  raw_crossing=crossing, endpoint_margins=signs,
                  separation=separation, independent_ratios=[price.decimal_interval(r) for r in ratios],
                  normalized_gap=price.rational_display(1 - moment_upper),
                  uniform=uniform, loss_each=str(LOSS), covered=str(covered),
                  ordinary_bootstrap=stages, ordinary_admitted=steps[-1],
                  paid_tuple_witness=dict(rank="14^416", previous_cutoff="15^416",
                                          new_cutoff="10^416", old_calls=1, new_calls="ceil(14^416/10^416)"))
    write(out / "BIT.json", result)
    return result


def rational_application(work, out, bit):
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
    old = read(chain / "DOUBLE-APPLICATION.json")
    check(Q(old["application"]["claim"]) == OLD_BOUND, "comparison matches pinned PR #7830 bound")
    for name in ("invoice", "ordinary", "bracket"):
        check(old["application"][name] == app["application"][name], f"retained rational {name}")
    claim = app["application"]["claim"]
    check(Q(claim) == EXPECTED and Q(claim) == Q(checked["outer"]["claim"]), "independent end-to-end κ comparison")
    return app, checked


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
    pinned_inputs(work, args.fetch)
    prepare = load("source_preparer", work / PRED / "prepare_sources.py")
    count = prepare.sources(work / "cache", args.fetch)
    print(f"Authenticated {count} inherited sources.", flush=True)
    bit = finite_bit(work, out)
    print("PASS_REBALANCED_BIT_FINITE", bit["ordinary_admitted"], flush=True)
    if args.bit_only:
        return
    app, audit = rational_application(work, out, bit)
    result = dict(status="PASS_COMPLETE_CONDITIONAL_APPLICATION", rational_word=BASE_RATIONAL,
                  binary_word=BASE_BIT, binary_ordinary=bit["ordinary_admitted"],
                  binary_raw_bracket=bit["raw_crossing"], rational_raw_bracket=app["application"]["bracket"],
                  claim=app["application"]["claim"], gain=str(EXPECTED-OLD_BOUND),
                  premises=app["premises"], sharp_outer=audit["outer"]["outer_checks"],
                  power=POWER, paid_cutoff=CUTOFF, productive_floor=FLOOR,
                  log_power=bit["uniform"]["logarithm_power"], log2_carrier=bit["uniform"]["H"])
    write(out / "RESULT.json", result)
    print("PASS_COMPLETE_CONDITIONAL_APPLICATION", result["claim"], flush=True)


if __name__ == "__main__":
    main()
