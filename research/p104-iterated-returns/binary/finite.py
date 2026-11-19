#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reprice and finitely admit a literal BIT native under the pinned paired caller."""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys


HEAD = "913fb6febe28cc3ccad1c16de8e45b8bce0da063"
BASE = "861f5181e4f34db638ab0c573c319fe26ff034d63b21242d67220a4a5d6433ff"
COMPARATOR = Q("0.00386981257853")
TARGET = Q("0.00387981257853")
DEFAULT_TRIAL = Q("0.003870038700")
BASE_STEPS = ("0.0038699682", "0.0038700382", "0.003870038498")
PAIRED = Path("research/paired-query-only-bit")
CLAIM = Path("certificates/frontier7000/CLAIM.json")
FINITE = PAIRED / "retained/inputs/credited_trim.py"
PACKAGE_PINS = {
    "binary/independent/literal.py": "4021766d87fa791a43a78a6665c9260b7ba3772d8b2db6e9c84b6a3d51a1305c",
    "binary/independent/price.py": "d720df6f3f7a22554e83d0c29243af3ee04fa036073404926bab7bc2f2687e1b",
    "binary/REPLAY.json": "d79558b8f85e35b2aedcaf69ee867fe6a3148929b74b8cb054c92617d1e30559",
}
SOURCE_PINS = {
    str(CLAIM): "3f8add8252adb223b60418ec69351a69b6b5edfe601ec1c6b4b65cd9e2afd9b2",
    str(FINITE): "fcff17fdd3108be68761fbde0fcbfe218be166cf518c99f7163e60d53ab785d9",
    str(FINITE.parent / "inputs/exact_arithmetic.py"): "0ce7e7137422d5ffeda22085c81fa88471bbe963100fdad62e659f1e3bf89326",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pinned(path, expected):
    contents = path.read_bytes()
    need(sha256(contents).hexdigest() == expected, f"pinned bytes for {path}")
    return contents


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def candidate_receipt(literal, path, word_sha, baseline, caller):
    encoded = path.read_bytes()
    raw = gzip.decompress(encoded) if encoded.startswith(b"\x1f\x8b") else encoded
    word = json.loads(raw)
    need(literal.canonical(word) == word_sha, "canonical proposed BIT word")
    n = word["public"]
    need(n >= 222 and len(word["start"]) == len(word["final"]) == n, "distinct public endpoints")
    need(word["frames"] == baseline["frames"] and all(
        word[k][:222] == baseline[k][:222] for k in ("start", "final")
    ), "frozen physical charts and all 111 port contact quartets")
    charts = literal.Charts(word["frames"])
    ports = charts.main_contacts(word["start"], word["final"])
    forward, f_log, _ = literal.tape(word, charts)
    adjoint, a_log, _ = literal.tape(word, charts, adjoint=True)
    need(forward == literal.expected_rows(n, False) and adjoint == literal.expected_rows(n, True),
         "all independent arbitrary-input coefficients and exact adjoint")
    need(f_log["paid"] == a_log["paid"], "both literal paid rank histograms")
    need(all(charts.rank[a] < charts.rank[b] for a, b in zip(word["start"][222:], word["final"][222:])),
         "positive native helper directions")
    native_targets = Counter(charts.leg(a, b) for a, b in zip(word["start"][222:], word["final"][222:]))
    events = Counter(row[0] for row in caller["events"])
    paid, targets = literal.paired_invoice(caller, f_log["paid"], native_targets, events)
    ordinary = literal.ordinary(word, caller, events, paid, targets)
    clear_clock = next(i for i, (op, *_) in enumerate(word["program"]) if op == "CLEAR")
    try:
        literal.tape(word, charts, omit=clear_clock)
    except ValueError:
        pass
    else:
        raise ValueError("omitting a CLEAR must break private retirement")
    return dict(status="PASS_LITERAL_BINARY_CANDIDATE", candidate_canonical_sha256=word_sha,
                candidate_file_sha256=sha256(raw).hexdigest(), candidate_gzip_sha256=sha256(encoded).hexdigest(),
                caller_sha256=literal.CALLER_SHA, native_calls=events["LOCAL"], public=n,
                frames=len(charts.frames), main_ports=ports, instruction_counts=f_log["counts"],
                native_scalar_coefficients_each_way=n*n, caller_polynomial_coefficients_each_way=38**2,
                native_targets=native_targets, native_paid=f_log["paid"],
                paid=paid, targets=targets, ordinary=ordinary,
                owned_nonzero_CLEAR=f_log["erase_dirty"], dual_nonzero_retirement=a_log["erase_dirty"],
                omitted_CLEAR_rejected=True, omitted_CLEAR_clock=clear_clock)


def exact_crossing(price, signed):
    scale = 10**15
    low, high = 0, 6_900_000_000_000
    derivative = price.derivative_bound(signed, Q(high, scale))
    need(price.moment(signed, Q(low, scale))[0] > 0 > price.moment(signed, Q(high, scale))[1],
         "initial directed signed crossing bracket")
    while high-low > 1:
        middle = (low+high)//2
        lower, upper = price.moment(signed, Q(middle, scale))
        need(lower > 0 or upper < 0, "decisive directed sign")
        if lower > 0:
            low = middle
        else:
            high = middle
    bracket = [f"0.{c:015d}" for c in (low, high)]
    return bracket, [price.decimal_interval(price.moment(signed, Q(c))) for c in bracket], derivative


def ordinary_certificate(price, compiler, native, selected, trial, steps):
    targets, paid = native["targets"], native["paid"]
    signed = price.signed_profile(targets, paid)
    crossing, endpoint_signs, derivative = exact_crossing(price, signed)
    if trial is None:
        trial = Q(crossing[0])-Q(1, 10**11)
    margin = price.moment(signed, trial)
    need(margin[0] > 0 and trial < Q(crossing[0]), "strict finite trial below raw crossing")
    independent = price.compiler(paid, targets, trial)
    v, cutoff, floor, ambient = (independent[k] for k in ("product_exponent", "cutoff", "productive_floor", "ambient_base"))
    gap = price.LOSS
    offset = Q(1, 5)
    original = compiler.certificate(targets, paid, trial, v, cutoff, floor, offset, offset)
    uniform = compiler.uniform_certificate(trial, v, cutoff, floor, ambient, gap)
    need((uniform["H"], uniform["logarithm_power"], uniform["theta"])
         == tuple(independent[k] for k in ("H", "logarithm_power", "theta")),
         "independent logarithm and carrier comparisons")
    for ratio, historical_upper in zip(independent["ratio_intervals"], original["rational_upper_limits"], strict=True):
        need(Q(ratio[1]) <= Q(historical_upper), "independent directed ratio lies below historical bound")

    caps = native["ordinary"]
    need(native["native_calls"] == 36 and 0 < caps["ordinary_records"] < caps["raw_ordinary_allowance"] == 10**12
         and 0 < caps["owned_backing"] < caps["raw_owned_allowance"] == 10**7,
         "complete paired raw record and owned caps")
    need(max(paid) < max(targets) <= ambient and cutoff**v < floor**v <= ambient**v,
         "paid cutoff, productive floor, and full working ambient")
    t, p = sum(targets.values()), sum(paid.values())
    occurrences = sum(t**(v-1-i)*p**i for i in range(v))
    products = dict(target_tuples=t**v, paid_tuples=p**v, raw_occurrences=occurrences,
                    split_paid_calls=sum(r*n for r,n in paid.items())**v,
                    raw_ordinary_records=occurrences*caps["ordinary_records"],
                    raw_owned_fields=occurrences*caps["owned_backing"], target_specialization_records=2*t**v)
    horizon, residual = divmod(uniform["H"], gap.denominator)
    need(residual == 0 and horizon > 0 and 2**45*gap > 256 and 1+gap/2 <= 2**horizon,
         "uniform exponent and charged delayed cover")
    covered = trial-2*gap
    rho = Q(1, 250)
    if steps is None:
        steps, previous = [], selected
        for _ in range(4):
            envelope = (1-rho)*covered + rho*previous
            numerator = (envelope.numerator*10**15)//envelope.denominator-1
            steps.append(f"0.{numerator:015d}")
            previous = Q(steps[-1])
    admitted, stages = price.bootstrap(selected, covered, steps)
    need(admitted > COMPARATOR, "ordinary BIT cap exceeds submitted complex raw upper")
    minimum_gaps = []
    for row in stages:
        old, new = Q(row["previous"]), Q(row["claim"])
        envelope = (1-rho)*covered + rho*old
        delta = min(rho-new, envelope-new, 1-rho-new)
        need(delta > 0, "strict threshold gaps for all three complete ordinary costs")
        minimum_gaps.append(str(delta))
    return dict(raw_crossing=crossing, crossing_margins=endpoint_signs,
                derivative_upper=price.decimal_interval((derivative, derivative), 12)[1],
                tested_saving=str(trial), trial_margin=price.decimal_interval(margin),
                target_signed_margin=price.decimal_interval(price.moment(signed,TARGET)),
                finite_separation=original, independent_directed_compiler=independent, uniform=uniform,
                uniform_loss=str(gap), delayed_cover_loss=str(gap), log2_of_N_to_cover_loss=horizon,
                cover_prime_condition="odd q > 2^45*N^5 avoiding the frozen finite catalogue witnesses",
                finite_product_bound_bit_lengths={k: n.bit_length() for k,n in products.items()},
                covered=str(covered), rho=str(rho), ordinary_bootstrap=stages, ordinary_admitted=steps[-1],
                stock=dict(atom_width="w=ceil(e^(1/250))", n="max(1,ceil(e/w))",
                           coarse_child_size="at most floor(n/N)", depth="2+ceil(log_N(n))",
                           reserve="W(w)^depth*S_old, including restored outer spectators",
                           W="B*|GL_N(F_q)|*q^(N^2*(w-1))", high_digits="O_fixed(w log e)",
                           backend_levels=len(stages), minimum_cost_gaps=minimum_gaps,
                           threshold_rule="Freeze each level at 2^j, with j>4*d/delta and C*(j+1)^d<=2^(delta*j) for fixed counted C,d. Smaller widths use its predecessor."))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("package", "source-root", "out"):
        parser.add_argument("--"+arg, type=Path, required=True)
    parser.add_argument("--word", type=Path)
    parser.add_argument("--word-sha")
    parser.add_argument("--trial", type=Q)
    args = parser.parse_args()
    need(__debug__, "run without -O")
    need(bool(args.word) == bool(args.word_sha), "candidate word and expected SHA-256 must be paired")
    published = {name: pinned(args.package / name, digest) for name,digest in PACKAGE_PINS.items()}
    source = {name: pinned(args.source_root / name, digest) for name,digest in SOURCE_PINS.items()}
    binary_dir = args.package / "binary"
    literal = load(binary_dir / "independent/literal.py", "literal")
    price = load(binary_dir / "independent/price.py", "common_caller_price")
    compiler = load(args.source_root / FINITE, "common_caller_credited_trim")
    baseline_path = binary_dir / "WORD.json.gz"
    baseline = literal.candidate_word(baseline_path)
    selected = Q(json.loads(source[str(CLAIM)])["admitted_BIT_saving"])
    need(selected == Q("0.00385248"), "selected completed ordinary interface")
    if args.word is None:
        native = literal.verify(args.source_root, baseline_path)
        archived = json.loads(published["binary/REPLAY.json"])
        need(all(literal.histogram(native[k]) == literal.histogram(archived[k]) for k in ("targets", "paid"))
             and native["ordinary"] == archived["ordinary"], "literal archival and independent bills coincide")
        trial = args.trial or DEFAULT_TRIAL
        steps = BASE_STEPS if args.trial is None else None
    else:
        caller = literal.pinned(args.source_root / PAIRED / "EFREE-CALLER.json.gz", literal.CALLER_SHA)
        native = candidate_receipt(literal, args.word, args.word_sha, baseline, caller)
        trial, steps = args.trial, None
    proof = ordinary_certificate(price, compiler, native, selected, trial, steps)
    result = dict(status="PASS_SHARPENED_FINITE_ORDINARY_BIT", published_reference_head=HEAD,
                  published_reference_word_sha256=BASE, word_sha256=native["candidate_canonical_sha256"],
                  word_file_sha256=native["candidate_file_sha256"], caller_sha256=native["caller_sha256"],
                  published_pins=PACKAGE_PINS, trusted_inputs=SOURCE_PINS, native=native,
                  ordinary=native["ordinary"], targets=native["targets"], paid=native["paid"], **proof)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(result["status"], result["word_sha256"], result["ordinary_admitted"], *result["raw_crossing"])


if __name__ == "__main__":
    main()
