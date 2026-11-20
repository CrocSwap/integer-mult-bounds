#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Verify the mixed 480-factor binary supplier and its complete rational consumer."""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from functools import cache
from hashlib import sha1, sha256
import importlib.util
import json
from itertools import product
from math import prod
from pathlib import Path
import shutil
import sys
from urllib.request import urlopen


HERE = Path(__file__).resolve().parent
PRED = Path("7786/research/p104-iterated-returns")
CHAIN = Path("7830/research/p104-chart306-chain")
OLD = Path("7835/research/p104-grade14-paid-cut")
EARLIER = Path("7831/research/p104-bit-tail-rebalance")
FRAMEWORK_HEAD = "e54523517d0f03e58352e647c403a5af3e525a57"
BASE_HEAD = "43007c979859fa84ccc3a3509ccacc9620d181fa"
BIT_WORD = "d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d"
RATIONAL_WORD = "7660985e0b618cdbee13e4190a4c6d5f91fbdf01a8f7a5186fdde8b980c19b48"
RATIONAL_LAYOUT = "f7de788c4a559282d35a9fce42f841a0e8de5a4015db871e718f9245569b0aa7"
RATIONAL_CALLER = "156fdf3a4a129b39225fd6ca51011de27974d7f104e8b04907c17ed5344bc858"
OLD_APPLICATION = "3366feccd6cc059c51943ee08c68bee2efd48d559c0b6507db4906cfaa27d00b"
SOURCE_LOCK = "b46b919292e1a1907345056b6925f5f1400d45650e2f0f610779a07163bb64ee"
SEED_PIN = "3f8add8252adb223b60418ec69351a69b6b5edfe601ec1c6b4b65cd9e2afd9b2"
PREMISES = ["native_all_columns", "owned_erasure", "compiler", "precision_tape", "analytic_recovery"]
TRIAL = Q("0.003879928046148")
TARGET = Q("0.003889928046155")
POWER, FLOOR, AMBIENT = 480, 16, 134
THETA, LOG_POWER, H = Q(13, 15), 64, 1_285_200_000_000_000
UNIFORM_LOSS, COVER_LOSS = Q(1, 400_000_000_000), Q(8, 10**12)
BINS = ((range(1, 5), 10, Q(11, 50), "grades_1_to_4"),
        (range(5, AMBIENT+1), 11, Q(13, 50), "grades_above_4"))
TARGET_TILT = Q(17, 50)
BIT_BRACKET = ["0.003879928046154", "0.003879928046155"]
RATIONAL_BRACKET = ["0.00388013644474", "0.00388013644475"]
CLAIM = "0.00387992803556"
ORDINARY = "0.003879928035646"
GRID = 10**70
LOCK_MANIFEST = "af24ecde1d2d009ff2e65a889719d7ae33a8958d90026351729f1f9eb7564af2"
OPERATOR_PIN = "36b3da4f72f8a6c946136fbd58b20838c00b0243c2effaf909c20b76967a5349"
PRODUCER_SOURCE_PINS = {
    "SOURCES.json": "357e6fe1a57bcb03be10874ba69ad075729802f15ac9614606856a16dc2c8e4f",
    "bit_certificate.py": "833bee1b33bb564cd44f3dc80201ab87c88d23db2fd9e2e879b46b1bfbf0b500",
    "verify.py": "5a073a31a4ea63ab5943057db2682029cb5524b8373116f51be580b1a3dde69b",
}


def check(condition, name):
    if not condition:
        raise ValueError(name)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def write(path, payload):
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def authenticate(work, fetch):
    manifest = HERE / "review_sources.json"
    check(digest(manifest) == LOCK_MANIFEST, "independent source manifest identity")
    rows = read(manifest)
    for entry in rows:
        source = work / entry["cache_key"] / entry["path"]
        if fetch and not source.exists():
            url = f"https://raw.githubusercontent.com/{entry['repo']}/{entry['head']}/{entry['path']}"
            with urlopen(url, timeout=45) as reply:
                raw = reply.read()
            check(sha256(raw).hexdigest() == entry["sha256"], f"download pin for {source.name}")
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_bytes(raw)
        raw = source.read_bytes()
        check(sha256(raw).hexdigest() == entry["sha256"], f"pinned bytes of {entry['path']}")
        if "git_blob" in entry:
            blob = sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
            check(blob == entry["git_blob"], f"exact Git blob of {entry['path']}")
    lock = work / PRED / "SOURCE-LOCK.json"
    check(digest(lock) == SOURCE_LOCK, "independent inherited source lock")
    if fetch:
        prepare = load("review_source_preparer", work / PRED / "prepare_sources.py")
        prepare.sources(work / "cache", fetch)
    checked = 0
    for key, source in read(lock)["sources"].items():
        for filename, info in source["files"].items():
            file = work / "cache" / key / filename
            check(digest(file) == info["sha256"], f"verified inherited source {key}/{filename}")
            checked += 1
    check(checked == 127, "complete inherited source lock census")
    return len(rows), checked


def native_binary(work, archived):
    source = HERE / "binary_operator.py"
    check(digest(source) == OPERATOR_PIN, "pinned separate literal binary operator")
    replay = load("review_binary_operator", source)
    word = replay.load_json(work / PRED / "binary/WORD.json.gz", replay.WORD_GZIP, True)
    caller = replay.load_json(work / "cache/source/research/paired-query-only-bit/EFREE-CALLER.json.gz",
                              replay.CALLER, True)
    layout = {key: word[key] for key in ("frames", "start", "final")}
    check(replay.canonical_hash(word) == replay.WORD == BIT_WORD
          and replay.canonical_hash(layout) == replay.LAYOUT, "frozen binary word and layout")
    atlas = replay.Atlas(word["frames"])
    main_contacts = atlas.main_contacts(word["start"], word["final"])
    forward, adjoint, omitted_add = replay.native_checks(word, atlas)
    direct = {(key, field.source, field.receiver, field.grade, field.clock) for key, field in forward.packets.items()}
    dual = {(key, field.receiver, field.source, field.grade, field.clock) for key, field in adjoint.packets.items()}
    check(direct == dual, "adjoint paid packet addresses and ranks")
    local_paid, local_targets, paid, targets = replay.binary_invoice(word, caller, atlas, forward)
    ordinary = replay.ordinary_boundary(word, caller, paid, targets)
    archived_native = archived["native"]
    check(paid == histogram(archived_native["paid"]) and targets == histogram(archived_native["targets"])
          and local_paid == histogram(archived_native["native_paid"])
          and local_targets == histogram(archived_native["native_targets"]), "every inherited BIT rank count")
    check(ordinary["raw_records"] == archived_native["ordinary"]["ordinary_records"]
          and ordinary["owned_fields"] == archived_native["ordinary"]["owned_backing"],
          "raw BIT work and real owned backing")
    check(8 + caller["stages"] * caller["body_rank"] == AMBIENT, "full BIT working geometry")
    # Bind a named occurrence of each supported grade, using actual native MOVE or caller IDLE/QUERY sites.
    native_legs = [(field.clock, word["program"][field.clock][1], field.grade)
                   for field in forward.packets.values()]
    paid_labels = {}
    for clock, row in enumerate(caller["events"]):
        labels = ()
        if row[0] == "LOCAL":
            labels = ((clock, subclock, bank, grade) for subclock, bank, grade in native_legs)
        if row[0] in {"IDLE_ONE", "QUERY"}:
            grade = 7 * len(row[2]) if row[0] == "IDLE_ONE" else 1
            labels = ((clock, -1, port, grade) for port in range(caller["ports"]))
        for clock, subclock, owner, grade in labels:
            identity = (clock, subclock, owner)
            check(identity not in paid_labels, "unique literal paid occurrence ID")
            paid_labels[identity] = grade
    provenance = {}
    for identity, grade in sorted(paid_labels.items()):
        provenance.setdefault(grade, identity)
    check(Counter(paid_labels.values()) == paid, "exact full physical paid-label inventory")
    return paid, targets, provenance, paid_labels, {"word": BIT_WORD, "layout": replay.LAYOUT, "caller": replay.CALLER,
        "native_scalar_coefficients_each_way": word["public"]**2, "caller_polynomial_coefficients_each_way": caller["roles"]**2,
        "public_roles": word["public"], "main_contacts": main_contacts, "frames": len(atlas.body),
        "dirty_retirement_each_way": forward.dirty, "dirty_retirement_omission_rejected": True,
        "bridge_packet": replay.BRIDGE_PACKET, "omitted_bridge_add_clock": omitted_add, **ordinary}


# The directed grid with range-reduced rational logarithms and positive Taylor
# exponential enclosures is adapted from the independent #7831 replay.
def ceildiv(a, b):
    return -((-a) // b)


def enclose(x):
    p = x.numerator * GRID
    return p // x.denominator, ceildiv(p, x.denominator)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def sub(a, b):
    return a[0] - b[1], a[1] - b[0]


def mul(a, b):
    products = [x * y for x in a for y in b]
    return min(products) // GRID, ceildiv(max(products), GRID)


def quotient(a, b):
    check(0 <= a[0] <= a[1] and 0 < b[0] <= b[1], "positive interval division")
    return a[0] * GRID // b[1], ceildiv(a[1] * GRID, b[0])


def scale(a, c):
    return mul(a, enclose(Q(c)))


def report_interval(interval, places=48):
    factor = 10**places

    def fixed(value):
        head, tail = divmod(abs(value), factor)
        return f"{'-' if value < 0 else ''}{head}.{tail:0{places}}"

    return [fixed(interval[0] * factor // GRID),
            fixed(ceildiv(interval[1] * factor, GRID))]


def small_log(x):
    z = (x - 1) / (x + 1)
    z_squared = z * z
    power = z
    partial = Q(0)
    for term in range(80):
        partial += 2 * power / (2 * term + 1)
        power *= z_squared
    tail = 2 * power / (161 * (1 - z_squared))
    return enclose(partial)[0], enclose(partial + tail)[1]


@cache
def log_int(r):
    power = r.bit_length() - 1
    return add(scale(small_log(Q(2)), power), small_log(Q(r, 2**power)))


def exp_closed(x):
    """Positive Taylor series on [0, 1/8], then interval squaring."""
    check(x[0] >= 0, "nonnegative exponent argument")
    squarings, divisor = 0, 1
    while 8 * x[1] > divisor * GRID:
        squarings += 1
        divisor *= 2
    y = scale(x, Q(1, divisor))
    term = result = (GRID, GRID)
    for n in range(1, 57):
        term = scale(mul(term, y), Q(1, n))
        result = add(result, term)
    next_term = scale(mul(term, y), Q(1, 57))
    # Rounding y by one grid ulp still gives less than 1/7, so
    # twice the first omitted term bounds the whole positive tail.
    check(y[1] * 7 < GRID, "geometric exponential tail")
    result = result[0], result[1] + 2 * next_term[1]
    for _ in range(squarings):
        result = mul(result, result)
    return result


@cache
def power(rank, exponent):
    return exp_closed(scale(log_int(rank), exponent))


def moment(histogram, exponent):
    result = (0, 0)
    for rank, multiplicity in histogram.items():
        result = add(result, scale(power(rank, exponent), multiplicity))
    return result


def histogram(value):
    return Counter({int(rank): count for rank, count in value.items()})


def native_rational(application):
    native, caller = application["native"], application["caller_census"]
    invoice = application["application"]["invoice"]
    check(caller["calls"] == 48 and native["public"] == 1289, "rational caller dimensions")
    check(native["retired_and_guards_restored"] and native["all_public_inputs_preserved_until_final_installs"]
          and native["exact_all_public_rows"] == native["exact_source_columns"] == 1289, "arbitrary rows and retirement")

    def recount(native_key, fixed_key, invoice_key):
        value = Counter({rank: caller["calls"] * n for rank, n in histogram(native[native_key]).items()})
        value.update(histogram(caller[fixed_key]))
        check(value == histogram(invoice[invoice_key]), f"complete caller histogram {invoice_key}")
        return value

    paid = recount("paid_native_ranks", "fixed_caller_paid", "paid")
    targets = recount("positive_helper_ranks", "fixed_root_targets", "targets")
    ordinary = application["application"]["ordinary"]
    check(sum(paid.values()) == ordinary["raw_paid_positions"]
          and sum(targets.values()) == ordinary["raw_productive_targets"], "matched rational ordinary counts")
    check(32 * sum(ordinary["raw_scalar_incidence_allowance_before_factor_32"].values())
          == ordinary["scalar_services"], "all charged scalar services")
    return paid, targets, ordinary


def directed_invoice(paid, targets, bracket, enrolled):
    lo, hi = (sub(moment(targets, 1 - Q(k)), moment(paid, 1 - Q(k))) for k in bracket)
    check(lo[0] > 0 > hi[1], "directed signs at raw crossing endpoints")
    coeff = targets.copy()
    coeff.subtract(paid)
    derivative_upper = 0
    for rank, signed_count in coeff.items():
        # Positive signed mass has a negative derivative with greatest value
        # at enrolled. Paid mass has a positive derivative maximized at zero.
        at = 1 - enrolled if signed_count > 0 else Q(1)
        term = scale(mul(power(rank, at), log_int(rank)), -signed_count)
        derivative_upper += term[1]
    check(derivative_upper < 0 and Q(bracket[1]) < enrolled, "unique decreasing crossing through target")
    signed = sub(moment(targets, 1 - enrolled), moment(paid, 1 - enrolled))
    check(signed[1] < 0, "negative signed target balance")
    return {"raw_crossing": bracket, "endpoint_margins": [report_interval(lo), report_interval(hi)],
            "derivative_upper_through_enrolled_target": report_interval((derivative_upper, derivative_upper))[1],
            "target_signed_margin": report_interval(signed),
            "required_saving": report_interval((-signed[1], -signed[0])),
            "paid": dict(paid), "productive": dict(targets)}


def outer_margins(kappa, gap, cap):
    """Evaluate the inherited outer conditions on the exact rational parameters."""
    b, a, q = (kappa + n * gap for n in (5, 4, 3))
    eps, beta = 1 - gap, 1 - 3 * gap
    sigma, tau = 1 - b, 1 - a
    internal = tau + (1 - gap) * max(sigma - tau, 0)
    leaf = sigma + gap * (1 - sigma)
    ell = 1 - (q + a) / 2
    xi = eps * (1 + q) - Q(3, 32) + gap
    r0, key = gap / 10, beta + 1 - eps
    recurrence = [eps * q, a, 1 - eps + q * beta, 1 - eps + a * beta, 1 - eps + beta,
                  Q(3, 32) + xi - eps, xi + Q(1, 2) - eps, eps, 1 - (eps + beta + 48 - 128 + 2)]
    strict = [
        cap - a, b - a, q, b - q, a - q, gap, 1 - gap, (1 - gap) * b - a,
        1 - internal - q, 1 - leaf - q, ell - tau, ell - sigma, ell - internal, 1 - q - ell, 1 - q - leaf,
        eps, 1 - eps, xi - Q(1, 2), eps - xi, beta, eps - beta, 1 - beta,
        1 - (2 * xi - 2) - r0 - beta, 1 - (2 * xi - 2) - beta, 1 - eps - r0, 1 - eps, r0, 1 - key,
        1 - beta - 2 * (1 - eps), 128 - 48 - beta, gap, eps - a, Q(1, 32) - b, 2**45 - 7**16,
        2, 2 - xi, 5, 1 - beta, 1 - beta, 1 - eps, recurrence[2] - recurrence[0],
        gap, kappa - Q(".001730970419199163702738"), 1 - eps, Q(11, 2),
    ] + [term - kappa for term in recurrence]
    functional = [1 - beta, beta * Q(997, 1000), 128 - 48 - eps - beta - 1, beta * Q(249, 250)]
    check(min(strict + functional) > 0, "all strict and functional outer conditions")
    return {"strict_count": len(strict), "functional_count": len(functional),
            "minimum_margin": str(min(strict + functional)),
            "BIT_just_below_effective_rejected": a - Q(1, 10**12) < a}


def rational_outer(application, audit, paid, targets, cap, published):
    compiler = audit["outer"]["finite_compiler"]
    claim = Q(published["claim"])
    tested = Q(compiler["tested"])
    gap = (tested - claim) / 7
    check(gap == Q(1, 10**14) and 0 < claim < tested < cap, "outer strict ordinary BIT headroom")
    raw = moment(targets, 1 - tested)
    alpha = quotient(moment(paid, 1 - tested), raw)
    gamma = quotient(moment(paid, 1 - tested + Q(1, 7)), mul(power(11, Q(1, 7)), raw))
    delta = quotient(enclose(Q(12 * sum(targets.values()))), mul(power(11, tested), raw))
    reserve, decay, v = Q(1, 10**27), Q(31, 32), 1920
    check(Q(alpha[1], GRID) < 1 - reserve and max(Q(gamma[1], GRID), Q(delta[1], GRID)) < decay
          and 1 / (1 + v * reserve) + 4 * decay**v < 1, "rational separated compiler moments")
    working_bound = power(153, v * tested)
    eta = quotient(enclose(1 - tested), working_bound)
    p, shift = 2381, Q(63, 64)
    check(shift**(p - 1) < Q(eta[0], GRID) <= Q(eta[1], GRID) <= shift**(p - 2)
          and Q(working_bound[1], GRID) < 2**p, "rational minimum and written log powers")
    check(11**64 < 12**63 and 2 * 11**(v * 64) <= 153**(v * 63), "rational shifted logarithm inequalities")
    H = int(compiler["H"])
    horizon = H // gap.denominator
    check(H * gap == horizon and (H + 1)**p < 2**horizon
          and (H + 1 - gap.denominator)**p >= 2**(horizon - 1), "rational carrier depth cutoff")
    common = application["common_root"]
    guards = application["common_depth_guards"]
    check(common["context_c"] == 856 and common["signed_width"] == "W=p+h+2D+3"
          and common["temporary_width"] == "W+26", "complete common-root width")
    for guard in guards.values():
        level = guard["compiler_H"]
        bits = (common["context_c"] * 1920 * 153**1920 * (level + 1)**2).bit_length()
        check(guard["strict_guard_passed"] and bits == guard["argument_bit_length"] < level, "common root depth")

    # Exact substitution into the inherited input-lift signed transfer.
    positive, negative = {7: 1, 3: 1, 5: 1}, {9: 1, 4: 1, 1: 2}
    d1, curvature = (0, 0), (0, 0)
    check(sum(r * n for r, n in positive.items()) == sum(r * n for r, n in negative.items()),
          "input-lift difference vanishes at zero")
    for rank, n in positive.items():
        d1 = add(d1, scale(log_int(rank), rank * n))
    for rank, n in negative.items():
        lg = log_int(rank)
        d1 = sub(d1, scale(lg, rank * n))
        curvature = add(curvature, scale(mul(lg, lg), rank * n))
    check(Q(d1[1], GRID) + cap * Q(curvature[1], GRID) < 0, "strict input lift throughout the cap interval")
    for k in (claim, tested):
        check(sub(moment(positive, 1 - k), moment(negative, 1 - k))[0] > 0, "positive signed input-lift margin")

    outer = outer_margins(claim, gap, cap)
    check(outer == audit["outer"]["outer_checks"] == published["sharp_outer"]
          and outer["BIT_just_below_effective_rejected"]
          and outer["strict_count"] == 54 and outer["functional_count"] == 4
          and Q(outer["minimum_margin"]) == gap / 10, "all matched outer conditions and below-cap control")
    return {"tested": str(tested), "cap_headroom": str(cap - tested), "H": H,
            "min_log_power": p - 1, "written_log_power": p, "common_depth_guards": guards,
            "moments": [report_interval(interval) for interval in (alpha, gamma, delta)], **outer}


def split_rank(rank, cutoff):
    full, tail = divmod(rank, cutoff)
    # Store the arithmetic progression of disjoint full-slab intervals and one final residual.
    end = full * cutoff
    calls = full + bool(tail)
    check(end <= rank == end + tail < end + cutoff and 0 < calls <= rank, "rank mass of disjoint slabs")
    return full, tail, calls


def reject(action, expected):
    try:
        action()
    except ValueError as failure:
        check(str(failure) == expected, f"unexpected rejection: {failure}")
    else:
        raise ValueError(f"mutation survived: {expected}")


def partition_controls(paid, paid_labels):
    # Enumerate the full, exact grade support for a short control. Weights are
    # the actual counts, so this enumerates all two-factor occurrence pairs.
    pairs = tuple(product(sorted(paid), repeat=2))

    def partition(rows):
        projected = Counter((a, b) for a, b, _ in rows)
        check(projected == Counter(pairs), "omitted or repeated ordered tuple")
        classes = Counter()
        masses = Counter()
        peak = 0
        for a, b, cut in rows:
            check(cut == (10 if a <= 4 else 11), "first occurrence misclassified")
            mult, rank = paid[a] * paid[b], a * b
            classes[cut] += mult
            masses[cut] += mult * rank
            full, tail, calls = split_rank(rank, cut**2)
            paid_slices = [cut**2] * full + ([tail] if tail else [])
            # Assemble the physical axis ranges and compare two disjoint passes
            # with one direct pass on arbitrary signed entries and spectators.
            source = [3 - 2*i for i in range(rank)]
            spectator = [91, -22]
            direct = [-x for x in source]
            work = source + spectator
            start = 0
            for length in paid_slices:
                stop = start + length
                work[start:stop] = [-x for x in work[start:stop]]
                start = stop
            check(start == rank and len(paid_slices) == calls and work == direct + spectator,
                  "checked chronological disjoint slices and spectators")
            peak = max(peak, calls)
        return classes, masses, peak

    rows = [(a, b, 10 if a <= 4 else 11) for a, b in pairs]
    counts, masses, peak = partition(rows)
    total_count = sum(paid.values())
    total_mass = sum(r * n for r, n in paid.items())
    check(sum(counts.values()) == total_count**2 and sum(masses.values()) == total_mass**2,
          "two-factor total count and rank mass")
    for small in (True, False):
        group = [row for row in rows if (row[0] <= 4) == small]
        rest = [row for row in rows if (row[0] <= 4) != small]
        reject(lambda: partition(rest), "omitted or repeated ordered tuple")
        reject(lambda: partition(rows + group), "omitted or repeated ordered tuple")
    reject(lambda: partition([(a, b, 21 - cut) for a, b, cut in rows]), "first occurrence misclassified")

    # Challenge the identity-keyed partition with different physical calls
    # sharing a grade, as well as whole-stratum omissions and duplications.
    identities = tuple((identity, 10 if grade <= 4 else 11) for identity, grade in paid_labels.items())
    expected = dict(identities)

    def audit_occurrences(instance):
        check(len(instance) == len(expected) and dict(instance) == expected,
              "incomplete actual paid occurrence partition")

    audit_occurrences(identities)
    for cut in (10, 11):
        only = tuple(row for row in identities if row[1] == cut)
        other = tuple(row for row in identities if row[1] != cut)
        reject(lambda: audit_occurrences(other), "incomplete actual paid occurrence partition")
        reject(lambda: audit_occurrences(identities + only), "incomplete actual paid occurrence partition")
    first_grade = paid_labels[identities[0][0]]
    replacement = next(row for row in identities[1:] if paid_labels[row[0]] == first_grade)
    reject(lambda: audit_occurrences((replacement,) + identities[1:]), "incomplete actual paid occurrence partition")

    # Two-coordinate endpoint restriction. A discarded target starts/ends
    # at zero, with a nonzero intermediate value and an obligatory query.
    mirror = lambda x: [x[0] + x[1], x[0] - x[1]]
    for signal in ([1, 0], [0, 1], [-1, 11]):
        polluted = list(signal)
        result = mirror(signal)
        check(any(polluted) and polluted != result, "discarded endpoint may be dirty")
        retired = [x - y for x, y in zip(mirror(polluted), result, strict=True)]
        omitted = [x - y for x, y in zip(polluted, result, strict=True)]
        check(retired == [0, 0] and omitted != retired, "dirty intermediate paid query is necessary")
    return {"distinct_grade_pairs": len(rows), "weighted_count": dict(counts), "weighted_rank_mass": dict(masses),
            "largest_number_of_slices": peak, "checked_actual_paid_occurrence_ids": len(identities),
            "rejected": ["omitted low stratum", "omitted high stratum",
            "duplicate low stratum", "duplicate high stratum", "wrong first-coordinate stratum",
            "same-grade distinct occurrence replacement", "omitted paid query on specialized owned endpoint"]}


def boundary_witnesses(paid, targets, provenance):
    tests = (
        ("below_10", {2: 93, 14: 339, 21: 48}, 2, 10, 0),
        ("above_10_low_first", {4: 182, 14: 134, 21: 164}, 4, 10, 1),
        ("above_10_high_first", {4: 182, 14: 134, 21: 164}, 14, 11, 0),
        ("below_11", {4: 218, 7: 99, 56: 163}, 7, 11, 0),
        ("above_11", {6: 18, 7: 145, 14: 317}, 6, 11, 1),
    )
    fields = {}
    for name, factors, first, base, expected in tests:
        check(sum(factors.values()) == POWER and all(paid[g] > 0 for g in factors)
              and first in factors and base == (10 if first <= 4 else 11), f"actual supported tuple {name}")
        rank, cutoff = prod(g**n for g, n in factors.items()), base**POWER
        full, tail, calls = split_rank(rank, cutoff)
        check(full == expected and tail > 0, f"actual boundary and positive residual for {name}")
        if name != "above_10_high_first":
            check(1000 * abs(rank - cutoff) < cutoff, f"within one per mille of cutoff: {name}")
        fields[name] = {"rank": str(rank), "factors": factors, "first_grade": first,
                        "first_paid_occurrence": provenance[first], "cutoff": f"{base}^{POWER}",
                        "whole_slabs": full, "residual_rank": str(tail), "calls": calls,
                        "ratio_to_cutoff": report_interval(enclose(Q(rank, cutoff)), 20)}
    low, high = fields["above_10_low_first"], fields["above_10_high_first"]
    check(low["rank"] == high["rank"] and low["calls"] == 2 and high["calls"] == 1,
          "equal-rank permutation needs physically distinct stratum")
    check(all(targets[g] > 0 for g in (2, 4, 5, 64))
          and 2 * 4**239 * 64**240 < 4**240 * 64**240 == FLOOR**POWER < 5 * 4**239 * 64**240,
          "productive floor inclusive on the actual invoice")
    return {"paid": fields, "product_target_at_floor": "4^240 * 64^240",
            "below_floor_owned": "2 * 4^239 * 64^240", "above_floor": "5 * 4^239 * 64^240"}


def schedule(paid, targets, physical):
    t, s = 1 - TRIAL, TARGET_TILT
    check(0 < TRIAL < Q(BIT_BRACKET[0]) and 0 < s < t and max(paid) < max(targets) <= AMBIENT,
          "strict trial and complete moment hypotheses")
    baseline = moment(targets, t)
    ratios = {"alpha": quotient(moment(paid, t), baseline),
              "discarded_targets": quotient(mul(power(FLOOR, s), moment(targets, t-s)), baseline)}
    target_count, paid_count = sum(targets.values()), sum(paid.values())
    paid_mass = sum(rank * count for rank, count in paid.items())
    check((target_count, paid_count, paid_mass) == (20_706, 107_460, 291_360), "full raw BIT inventory")
    classes, slab_limits = {}, {}
    for grades, cut, tilt, name in BINS:
        hist = Counter({r: n for r, n in paid.items() if r in grades})
        count = sum(hist.values())
        mass = sum(r*n for r, n in hist.items())
        denominator = mul(power(cut, tilt), baseline)
        check(0 < TRIAL <= tilt and 1 < cut < FLOOR and len(hist) > 0, f"law for every slab in {name}")
        ratios[f"{name}_first"] = quotient(moment(hist, t + tilt), denominator)
        ratios[f"{name}_rest"] = quotient(moment(paid, t + tilt), denominator)
        class_count = count * paid_count**(POWER-1)
        class_mass = mass * paid_mass**(POWER-1)
        # Each ceiling is at most rank, and the total is at most the
        # exact class multiplicity plus the floor of its mass over the cap.
        slab_limits[name] = min(class_mass, class_count + class_mass // cut**POWER)
        classes[name] = {"histogram": {str(rank): count for rank, count in hist.items()},
                         "cutoff_base": cut, "tail_tilt": str(tilt),
                         "first_paid_count": count, "first_paid_rank_mass": mass,
                         "tuple_count": f"{count}*{paid_count}^{POWER-1}",
                         "rank_mass": f"{mass}*{paid_mass}^{POWER-1}",
                         "split_calls_upper_bit_length": slab_limits[name].bit_length()}
    first, second = [histogram(row["histogram"]) for row in classes.values()]
    check(not (first.keys() & second.keys()) and first + second == paid, "disjoint complete first-coordinate laws")
    check(sum(row["first_paid_count"] * paid_count**(POWER-1) for row in classes.values()) == paid_count**POWER
          and sum(row["first_paid_rank_mass"] * paid_mass**(POWER-1) for row in classes.values()) == paid_mass**POWER,
          "full tensor charge partitions")
    cap_grid = 10**22
    caps = {key: Q(ceildiv(interval[1] * cap_grid, GRID), cap_grid) for key, interval in ratios.items()}
    check(all(0 < Q(ratios[key][0], GRID) <= Q(ratios[key][1], GRID) < cap < 1
              for key, cap in caps.items()), "strict directed caps independently rounded to 22 places")
    base_bound = 1 / (1 + POWER * (1 - caps["alpha"]))
    uplift = {key: 2 * caps[f"{key}_first"] * caps[f"{key}_rest"]**(POWER-1) for key in classes}
    debit = caps["discarded_targets"]**POWER
    surplus = 1 - base_bound - sum(uplift.values()) - debit
    check(surplus > Q(123, 10**14), "strict normalized full paid and discarded moment")
    check(1 - base_bound - 2 * uplift["grades_1_to_4"] - uplift["grades_above_4"] - debit < 0,
          "a double-counted lower-cutoff tail fails strict separation")
    invocations = sum(target_count**(POWER - 1 - i) * paid_count**i for i in range(POWER))
    slab_limit = sum(slab_limits.values())
    check(slab_limit < paid_mass**POWER, "tighter complete slab bound")
    magnitudes = {
        "added_block_adapter_sides_upper": 2 * slab_limit,
        "all_possible_targets": target_count**POWER,
        "discarded_target_allocation_and_retirement_pairs_upper": target_count**POWER,
        "raw_owned_instances": invocations * physical["owned_fields"],
        "raw_paid_tuples": paid_count**POWER,
        "raw_record_instances": invocations * physical["raw_records"],
        "source_occurrences": invocations,
        "split_calls_upper": slab_limit,
    }
    report = {"trial": str(TRIAL), "power": POWER, "productive_floor": FLOOR, "target_tilt": str(TARGET_TILT),
              "upper_caps": {key: str(value) for key, value in caps.items()},
              "normalized": {key: report_interval(value) for key, value in ratios.items()},
              "normalized_surplus": report_interval(enclose(surplus)),
              "untouched_moment_majorant": report_interval(enclose(base_bound)),
              "uplift_upper": {key: report_interval(enclose(value)) for key, value in uplift.items()},
              "target_debit_upper": report_interval(enclose(debit)),
              "paid_partition": classes,
              "product_count_bit_lengths": {key: n.bit_length() for key, n in magnitudes.items()}}
    return report, ratios, surplus, uplift, debit


def uniform_and_stock(seed):
    t = 1 - TRIAL
    r, a, k = 11**POWER, AMBIENT**POWER, FLOOR**POWER
    p, num, den = LOG_POWER, THETA.numerator, THETA.denominator
    check(r**den < k**num and 2**(den - num) * r**den <= a**num,
          "full shifted logarithm inequality with 2^(den-num)")
    ambient = power(AMBIENT, POWER * TRIAL)
    eta = quotient(enclose(t), ambient)
    check(THETA**p < Q(eta[0], GRID) <= Q(eta[1], GRID) <= THETA**(p-1)
          and Q(ambient[1], GRID) < 2**p, "ordinary majorant and failure of preceding power")
    check(0 < UNIFORM_LOSS < TRIAL, "positive uniform exponent loss")
    horizon = H * UNIFORM_LOSS
    step = UNIFORM_LOSS.denominator
    check(horizon == 3213 and (H + 1)**p < 2**int(horizon)
          and (H - step + 1)**p >= 2**(int(horizon) - 1)
          and (H + 1) * UNIFORM_LOSS > 2*p,
          "H and preceding grid point, with monotone saving beyond H")
    alt_H, alt_step, alt_horizon = 3_954_000_000_000_000_000, 10**15, 3954
    check(alt_H == alt_step * alt_horizon and (alt_H+1)**p < 2**alt_horizon
          and (alt_H-alt_step+1)**p >= 2**(alt_horizon-1), "uniform-only smaller-loss sensitivity")
    uniform_saving = TRIAL - UNIFORM_LOSS
    # The delayed-cover proof first fixes the rational matcher catalogue.
    # q>2^45 N^5 gives a separate bad-class fee bounded by 64/2^45.
    # Since log(2)>1/2 and N>=2, N^d>=1+d/2 for every d>0.
    bad = Q(64, 2**45)
    check(0 < COVER_LOSS < uniform_saving and UNIFORM_LOSS < COVER_LOSS and H >= 1
          and Q(log_int(2)[0], GRID) > Q(1, 2) and bad < COVER_LOSS/4,
          "distinct uniform and delayed-cover losses")
    check(bad > UNIFORM_LOSS/4 and 2**int(H*COVER_LOSS) >= 1+COVER_LOSS/2,
          "uniform-loss substitution fails proof budget; actual carrier passes cover")
    multiplier = (1+COVER_LOSS/4) / (1+COVER_LOSS/2)
    check(multiplier < 1, "covered moment after bad-class fallback")
    start, rho, covered = Q(seed), Q(1, 250), uniform_saving - COVER_LOSS
    check(start == Q("0.00385248") < covered, "completed ordinary stock seed")
    previous, stages = start, []
    for _ in range(5):
        envelope = (1 - rho) * covered + rho * previous
        tick = int(envelope * 10**15) - 1
        accepted = Q(tick, 10**15)
        check(previous < accepted < envelope < covered < rho < 1 - envelope,
              "strict stock step admits all three work exponents")
        room = min(rho-accepted, envelope-accepted, 1-rho-accepted)
        check(room > 0, "threshold room including spectator and logarithmic overhead")
        stages.append({"previous": str(previous), "claim": f"0.{tick:015d}",
                       "envelope": str(envelope), "slack": str(room)})
        previous = accepted
    overclaim = Q("0.003879928035648")
    check(previous == Q(ORDINARY) and Q(stages[-1]["envelope"]) < overclaim,
          "genuine upward mutation fails the fifth stage envelope")
    return {
        "uniform": {"H": H, "N": f"2^{H}", "gap": str(UNIFORM_LOSS), "theta": str(THETA), "log_power": p,
                    "ambient": f"{AMBIENT}^{POWER}", "ambient_base": AMBIENT, "maximum_paid_base": 11,
                    "minimum_productive_base": FLOOR, "integer_grid_exponent": int(horizon),
                    "eta": report_interval(eta), "ambient_power": report_interval(ambient),
                    "uniform_saving": str(uniform_saving),
                    "alternative_uniform_only": {"gap": str(Q(1, alt_step)), "H": alt_H,
                                                 "integer_grid_exponent": alt_horizon}},
        "delayed_cover_and_stock": {"loss": str(COVER_LOSS), "H_times_cover_loss": str(H*COVER_LOSS),
            "relative_bad_surcharge_budget": str(COVER_LOSS/4), "relative_bad_surcharge_upper": str(bad),
            "covered_moment_upper": str(multiplier), "covered": str(covered), "seed": str(start),
            "rho": str(rho), "stages": stages, "admitted": ORDINARY, "fifth_stage_overclaim_rejected": str(overclaim),
            "q_criterion": "odd prime q > 2^45*N^5 avoiding the frozen finite catalogue determinants, denominators and rank witnesses",
            "high_digits": "fixed-template O(ceil(e^rho) log e), including restored previous-backend stock",
            "stock_reserve": "W(w)^D(e) * S_old", "row_factor": "B*|GL_N(F_q)|*q^(N^2*(w-1))",
            "depth": "2+ceil(log_N(max(1,ceil(e/w))))", "coarse_child": "at most floor(d/N)",
            "backend_rule": "five separately frozen stages, prior completed stage supplies bounded widths and all stock operations"},
    }, ambient, eta


def replay_application(work, out):
    # The independent schedule supplies an independently generated three-key
    # cap adapter. Invoke the pinned operator compiler and its separate audit.
    # Their inputs are frozen public code and words. No candidate verifier is imported.
    bit_root = out / "adapter"
    bit_root.mkdir()
    (bit_root / "binary").mkdir()
    shutil.copyfile(work / PRED / "SOURCE-LOCK.json", bit_root / "SOURCE-LOCK.json")
    shutil.copyfile(work / PRED / "binary/WORD.json.gz", bit_root / "binary/WORD.json.gz")
    stub = bit_root / "binary/FINITE.json"
    write(stub, {"ordinary_admitted": ORDINARY, "native_calls": 36, "word_sha256": BIT_WORD})
    pin = digest(stub)
    qualified = load("review_rational_qualifier", work / PRED / "continuation/qualify.py")
    qualified.BIT_FINITE_PIN = pin
    common = dict(cache=work / "cache", word=work / CHAIN / "DOUBLE-CANDIDATE.json.gz",
                  layout=work / PRED / "continuation/LAYOUT.json.gz",
                  word_sha=RATIONAL_WORD, layout_sha=RATIONAL_LAYOUT)
    reference = work / PRED / "evidence/application.json"
    app_path, audit_path = out / "APPLICATION.json", out / "AUDIT.json"
    app = qualified.qualify(argparse.Namespace(**common, package=bit_root, e40b_receipt=reference, out=app_path))
    write(app_path, app)
    auditor = load("review_rational_auditor", work / PRED / "continuation/audit_expanded.py")
    auditor.BINARY_INDEPENDENT_SHA = pin
    auditor.main(argparse.Namespace(**common, receipt=app_path, binary_receipt=stub,
                                   reference_application=reference, out=audit_path))
    return read(app_path), read(audit_path)


def compare_fixed_application(work, app, audit):
    prior_audit = read(work / OLD / "AUDIT.json")
    check(prior_audit["compiler_report_sha256"] == OLD_APPLICATION, "exact pinned #7835 application digest")
    immutable = set(audit) - {"outer", "compiler_report_sha256"}
    check(audit.keys() == prior_audit.keys() and all(audit[key] == prior_audit[key] for key in immutable),
          "all fixed rational application and physical audit fields match #7835")
    before = read(work / CHAIN / "DOUBLE-APPLICATION.json")
    check(app.keys() == before.keys() and all(app[key] == before[key] for key in app if key not in {
          "application", "binary_ordinary"}), "all inherited #7830 physical and exact caller fields")
    for key in ("invoice", "ordinary", "bracket"):
        check(app["application"][key] == before["application"][key], f"exact #7830 rational {key}")
    check(app["binary_word"] == BIT_WORD and app["word_sha256"] == RATIONAL_WORD
          and app["layout_sha256"] == RATIONAL_LAYOUT and app["caller"] == RATIONAL_CALLER
          and app["premises"] == audit["premises"] == PREMISES, "same words, caller, layout and five conditions")
    check(audit["actual_grid_fixture"]["exact_outputs_each"] == app["native"]["exact_source_columns"]
          == app["native"]["exact_all_public_rows"] == 1289
          and audit["basis_grid"]["all_basis_products"] == 13_030_044
          and audit["scalar_plans"]["omitted_extra_clear_control"]["rejected"]
          and app["conversion"]["partial_clear"]["dirty_unaddressed_last_cell_rejected"]
          and app["native"]["retired_and_guards_restored"] and app["native"]["live_sender_alias_control_rejected"],
          "native, addressed CLEAR and independent rational audit controls")
    check(Q(app["binary_ordinary"]) == Q(audit["outer"]["pinned_binary_cap"]) == Q(ORDINARY), "actual cap consumed")


def rational_orientations(work, app):
    source = work / "cache/parent/complex/independent.py"
    # This source is independently authenticated by SOURCE-LOCK before loading.
    reader = load("review_rational_orientations", source)
    raw, _ = reader.read(work / CHAIN / "DOUBLE-CANDIDATE.json.gz", RATIONAL_WORD)
    layout, _ = reader.read(work / PRED / "continuation/LAYOUT.json.gz", RATIONAL_LAYOUT)
    graph = reader.Graph.parse(raw)
    spans = [reader.span(chart) for chart in graph.frames]
    want, mains = reader.public_operator(graph, layout, spans)
    rows, _ = reader.forward(graph)
    adjoint, _ = reader.adjoint(graph)
    check(rows == want and adjoint == reader.transpose(want) and graph.size == 1289,
          "exact 1289 rational public outputs, forward and independent backward sweeps")
    local_paid, local_targets = reader.ranks(graph, mains, spans)
    check(local_paid == histogram(app["native"]["paid_native_ranks"])
          and local_targets == histogram(app["native"]["positive_helper_ranks"])
          and sum(local_paid.values()) == 5707 and sum(local_targets.values()) == 889,
          "every nested rational paid route and real productive helper grade")
    return {"checked_coefficients_each_way": graph.size**2, "main_fields": len(mains),
            "native_paid": sum(local_paid.values()), "native_helpers": sum(local_targets.values()),
            "forward_sha256": reader.row_digest(rows), "adjoint_sha256": reader.row_digest(adjoint)}


def headline(work, app, audit, binary, rational):
    k, upper = Q(CLAIM), Q(BIT_BRACKET[1])
    predecessor = Q(read(work / OLD / "RESULT.json")["claim"])
    earlier = Q(read(work / EARLIER / "RESULT.json")["claim"])
    check(predecessor == Q("0.00387992802601") and earlier == Q("0.00387992802506")
          and 0 < earlier < predecessor < k < Q(ORDINARY) < TRIAL < upper < Q(RATIONAL_BRACKET[0]) < TARGET,
          "conditional comparator, fixed signed ceiling and target")
    check(Q(app["application"]["claim"]) == Q(audit["outer"]["claim"]) == k, "matched new joint claim")
    gate = audit["outer"]["finite_compiler"]
    check(Q(gate["tested"]) + Q(gate["BIT_margin"]) == Q(ORDINARY)
          and Q(gate["tested"]) == k + Q(7, 10**14), "strict consumer headroom")
    unused_tick = Q(1, 10**14)
    check(k == Q(int(Q(ORDINARY)/unused_tick) - 8) * unused_tick, "inherited producer price tick convention")
    def rounded_margin(receipt):
        lo, hi = (enclose(Q(x)) for x in receipt["target_signed_margin"])
        return report_interval((lo[0], hi[1]), 39)

    return {"status": "PASS_COMPLETE_CONDITIONAL_APPLICATION",
            "rational_word": RATIONAL_WORD, "binary_word": BIT_WORD, "binary_ordinary": ORDINARY,
            "native_calls": {"rational": 48, "binary": 36},
            "binary_raw_bracket": BIT_BRACKET, "rational_raw_bracket": RATIONAL_BRACKET, "claim": CLAIM,
            "binary_enrolled_target_margin": rounded_margin(binary),
            "rational_enrolled_target_margin": rounded_margin(rational),
            "gain_over_7835": "0.00000000000955", "gain_over_7831": "0.00000000001050",
            "enrolled_target": "0.003889928046155", "gap_to_enrolled_target": "0.000010000010595",
            "premises": PREMISES, "sharp_outer": audit["outer"]["outer_checks"], "power": POWER,
            "paid_cutoffs": {name: cut for _, cut, _, name in BINS}, "productive_floor": FLOOR,
            "uniform_loss": str(UNIFORM_LOSS), "delayed_cover_loss": str(COVER_LOSS),
            "log_power": LOG_POWER, "log2_carrier": H}


def verify_aggregate(bit, receipt, ratios, surplus, uplift, debit, ambient, eta, paid_labels):
    claimed = bit["separation"]
    schedule = receipt["schedule"]

    def enclosure(label, claimed, computed):
        if isinstance(claimed, dict):
            claimed = [claimed["lower"], claimed["upper"]]
        a, b = map(Q, claimed)
        lo, hi = (Q(x, GRID) for x in computed)
        check(a <= lo <= hi <= b, f"directed comparison for {label}")

    for name, interval in ratios.items():
        enclosure(name, claimed["normalized"][name], interval)
        enclosure(f"source {name}", claimed["exact_source_normalized"][name], interval)
    for key in ("trial", "power", "productive_floor", "target_tilt", "upper_caps"):
        check(claimed[key] == schedule[key], f"producer and independent separation agree: {key}")
    enclosure("normalized surplus", claimed["normalized_surplus"], enclose(surplus))
    enclosure("full discarded target debit", claimed["target_debit_upper"], enclose(debit))
    for name, extra in uplift.items():
        enclosure(f"split uplifts {name}", claimed["uplift_upper"][name], enclose(extra))
    for key in ("paid_partition", "product_count_bit_lengths"):
        check(bit["product"][key] == schedule[key], f"all split accounting fields agree: {key}")
    check(not bit["product"]["product_materialized"] and not bit["product"]["uniform_materialized"],
          "correct symbolic scope of the enormous product and uniform words")

    uniform = bit["uniform"]
    for key in set(receipt["uniform"]) - {"eta", "ambient_power"}:
        check(uniform[key] == receipt["uniform"][key], f"uniform record agrees for {key}")
    enclosure("ambient exponent", uniform["ambient_power"], ambient)
    enclosure("uniform eta", uniform["eta"], eta)
    covered = bit["delayed_cover_and_stock"]
    both = receipt["delayed_cover_and_stock"]
    fields = ("loss", "H_times_cover_loss", "relative_bad_surcharge_budget", "relative_bad_surcharge_upper",
              "covered_moment_upper", "covered", "seed", "rho", "admitted")
    for field in fields:
        check(Q(covered[field]) == Q(both[field]), f"separate cover or stock value agrees: {field}")
    check(Q(covered["fifth_stage_overclaim_rejected"]) == Q(both["fifth_stage_overclaim_rejected"]),
          "matched rejected cap")
    for row, exact, slack in zip(covered["stages"], both["stages"], covered["minimum_ordinary_gaps"], strict=True):
        check(row["claim"] == exact["claim"] and Q(row["previous"]) == Q(exact["previous"])
              and Q(row["envelope"][0]) == Q(row["envelope"][1]) == Q(exact["envelope"])
              and Q(row["slack"][0]) == Q(row["slack"][1]) == Q(exact["slack"]) == Q(slack),
              "all literal stock stage and work exponents")
    check(covered["q_criterion"] == both["q_criterion"], "same prime criterion and catalogue")
    controls = bit["partition_controls"]
    check(controls["raw_paid_occurrences"] == len(paid_labels) and controls["duplicate_rejected"]
          and controls["missing_rejected"] and controls["replaced_same_grade_occurrence_rejected"]
          and controls["sample_paid_tuples"] == 64, "producer label fault controls")
    equal_rank = controls["equal_rank_control"]
    factors = {int(g): n for g, n in equal_rank["factor_powers"].items()}
    check(sum(factors.values()) == POWER and
          {int(g): paid_labels[tuple(label)] for g, label in equal_rank["labels"].items()}
          == {g: g for g in factors}, "equal-rank witness labels belong to the literal native caller")
    rank = prod(g**n for g, n in factors.items())
    heads = equal_rank["swap_first_grades"]
    test = [split_rank(rank, (10 if g <= 4 else 11)**POWER)[2] for g in heads]
    check(heads == [4, 14] and test == equal_rank["calls"] == [2, 1]
          and str(rank) == schedule["boundary_witnesses"]["paid"]["above_10_low_first"]["rank"],
          "real equal-rank cross-stratum control")
    stock = covered["stock"]
    check(stock["atom_width"] == "w=ceil(e^(1/250))" and stock["W"] == both["row_factor"]
          and stock["depth"] == "2+ceil(log_N(d))" and stock["d"] == "max(1,ceil(e/w))"
          and stock["reserve"] == "W(w)^depth*S_old" and stock["high_digits"] == "O_fixed(w log e)"
          and stock["coarse_child"] == "at most floor(d/N) at every recursion"
          and stock["low_width"] == "use the completed preceding backend"
          and stock["threshold"] == "freeze at 2^j with j>4*degree/slack and C*(j+1)^degree<=2^(slack*j)",
          "full stock depth, row reserve and finite threshold")
    rows = bit["tuple_witnesses"]
    check(len(rows) >= 2, "actual paid witness for each stratum")
    for tag in rows[:2]:
        f, g = (paid_labels[tuple(tag[key])] for key in ("first_label", "repeated_tail_label"))
        which = next((cut, name) for grades, cut, _, name in BINS if f in grades)
        check(f == tag["first_grade"] and g == tag["repeated_tail_grade"]
              and tag["class_name"] == which[1] and tag["repeated_tail_factors"] == POWER-1,
              "actual paid labels, derived grades and factor ordering")
        r = f * g**(POWER-1)
        full, tail, n = split_rank(r, which[0]**POWER)
        check(full == tag["full_blocks"] and tail == int(tag["residual_rank"]) and n == tag["calls"]
              and n != tag["misclassified_calls"] == split_rank(r, (21-which[0])**POWER)[2]
              and tag["grade14_calls_at_same_tensor_power"] == split_rank(r, 14**POWER)[2],
              "actual full disjoint and residual calls")


def collect(work, out, producer, fetch, producer_package=None):
    if producer is not None:
        producer_package = producer_package or HERE.parent
        for name, expected in PRODUCER_SOURCE_PINS.items():
            check(digest(producer_package / name) == expected, f"frozen producer source: {name}")
    explicit, locked = authenticate(work, fetch)
    archived_bit = read(work / OLD / "BIT.json")
    seed_path = work / "cache/source/certificates/frontier7000/CLAIM.json"
    check(digest(seed_path) == SEED_PIN, "authenticated completed ordinary seed and framework")
    seed = read(seed_path)
    check([d["id"] for d in seed["assumptions"]] == PREMISES, "complete inherited assumptions")
    paid, targets, provenance, paid_labels, physical = native_binary(work, archived_bit)
    b, ratios, surplus, uplift, debit = schedule(paid, targets, physical)
    b.update({"boundary_witnesses": boundary_witnesses(paid, targets, provenance),
              "partition_controls": partition_controls(paid, paid_labels)})
    cover, ambient, eta = uniform_and_stock(seed["admitted_BIT_saving"])
    binary = directed_invoice(paid, targets, BIT_BRACKET, TARGET)
    print("PASS independent directed BIT schedule, both orientations, stock and admission", ORDINARY, flush=True)

    app, audit = replay_application(work, out)
    compare_fixed_application(work, app, audit)
    oriented = rational_orientations(work, app)
    rational_paid, rational_targets, rational_bill = native_rational(app)
    rational = directed_invoice(rational_paid, rational_targets, RATIONAL_BRACKET, TARGET)
    published = headline(work, app, audit, binary, rational)
    old_gate = read(work / OLD / "AUDIT.json")["outer"]
    prior = read(work / OLD / "RESULT.json")
    old_outer = rational_outer(app, {"outer": old_gate}, rational_paid, rational_targets, Q(prior["binary_ordinary"]), prior)
    new_outer = rational_outer(app, audit, rational_paid, rational_targets, Q(ORDINARY), published)
    dead_effective = Q(CLAIM) + Q(4, 10**14) - Q(1, 10**15)
    reject(lambda: outer_margins(Q(CLAIM), Q(1, 10**14), dead_effective),
           "all strict and functional outer conditions")
    prior_gain = Q(CLAIM) - Q(prior["claim"])
    prev = Q(read(work / EARLIER / "RESULT.json")["claim"])
    check(prior_gain == Q(published["gain_over_7835"]) and Q(CLAIM)-prev == Q(published["gain_over_7831"])
          and TARGET-Q(CLAIM) == Q(published["gap_to_enrolled_target"]), "headline increments")
    receipt = {"status": "PASS_INDEPENDENT_MIXED_CUTOFF_CONDITIONAL_APPLICATION", "headline": published,
               "predecessor": {"pr": 7835, "head": BASE_HEAD, "claim": prior["claim"],
                               "ordinary_binary": prior["binary_ordinary"], "outer": old_outer},
               "framework": {"head": FRAMEWORK_HEAD, "premises": seed["assumptions"]},
               "binary": {"physical": physical, "signed": binary}, "schedule": b, **cover,
               "rational": {"layout": RATIONAL_LAYOUT, "caller": RATIONAL_CALLER, "ordinary": rational_bill,
                            "physical": {**oriented, "exact_columns": app["native"]["exact_source_columns"],
                                         "retirement": app["native"]["retired_and_guards_restored"],
                                         "basis_products": audit["basis_grid"]["all_basis_products"],
                                         "omitted_clear_rejected": audit["scalar_plans"]["omitted_extra_clear_control"]["rejected"]},
                            "signed": rational, "outer": new_outer, "exact_outer_below_effective_rejected": True},
               "explicit_sources_verified": explicit, "inherited_sources_verified": locked,
               "source_lock_sha256": SOURCE_LOCK, "review_sources_sha256": LOCK_MANIFEST,
               "replay_sha256": {name: digest(out / name) for name in ("APPLICATION.json", "AUDIT.json")}}
    if producer is not None:
        bit, result = (read(producer / name) for name in ("BIT.json", "RESULT.json"))
        check(result == published and bit["raw_crossing"] == BIT_BRACKET and bit["ordinary_admitted"] == ORDINARY
              and bit["word_sha256"] == BIT_WORD and bit["native_calls"] == 36, "exact connected headline and supplier")
        for name in ("APPLICATION.json", "AUDIT.json"):
            check((out / name).read_bytes() == (producer / name).read_bytes(), f"identical isolated replay: {name}")
        check(bit["native"] == archived_bit["native"], "same entire BIT native and ordinary receipt")
        verify_aggregate(bit, receipt, ratios, surplus, uplift, debit, ambient, eta, paid_labels)
        for label in b["paid_partition"]:
            omitted = deepcopy(bit)
            del omitted["product"]["paid_partition"][label]
            reject(lambda: verify_aggregate(omitted, receipt, ratios, surplus, uplift, debit, ambient, eta, paid_labels),
                   "all split accounting fields agree: paid_partition")
            doubled = deepcopy(bit)
            doubled["product"]["paid_partition"][label]["first_paid_count"] *= 2
            reject(lambda: verify_aggregate(doubled, receipt, ratios, surplus, uplift, debit, ambient, eta, paid_labels),
                   "all split accounting fields agree: paid_partition")
        receipt["producer_aggregate_mutations_rejected"] = 4
        receipt["producer_source_sha256"] = PRODUCER_SOURCE_PINS
        receipt["producer_replay_sha256"] = {name: digest(producer / name) for name in
                                            ("BIT.json", "AUDIT.json", "RESULT.json", "APPLICATION.json")}
        print("PASS full finite aggregate and byte-identical rational checks", flush=True)
    write(out / "REVIEW.json", receipt)
    print(receipt["status"], CLAIM, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", required=True, type=Path, help="pinned public inputs directory")
    parser.add_argument("--out", required=True, type=Path, help="new replay directory")
    parser.add_argument("--producer", type=Path, help="isolated producer replay output, for full receipt matching")
    parser.add_argument("--producer-package", type=Path, help="frozen producer sources, defaults to the parent of this review")
    parser.add_argument("--fetch", action="store_true", help="populate missing pinned sources")
    args = parser.parse_args()
    check(__debug__, "run without optimization")
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    collect(args.work.resolve(), out, args.producer.resolve() if args.producer else None, args.fetch,
            args.producer_package.resolve() if args.producer_package else None)


if __name__ == "__main__":
    main()
