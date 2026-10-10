#!/usr/bin/env python3
"""Recount and exactly price the literal gen4 candidate.

The fixed-prime interval method follows the retained PR265 refinement; the
moment and outer engines are dynamically loaded from the pinned PR276 package.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
import sys
if not __debug__:
    raise SystemExit("Assertions required; refusing -O")
sys.dont_write_bytecode = True
sys.set_int_max_str_digits(0)

from array import array
from collections import Counter
from decimal import Decimal, ROUND_FLOOR, localcontext
from fractions import Fraction as Q
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json

PRIME = (1 << 127) - 1
M = 120
RHO = Q(2 * M**3, PRIME)
ETA = Q(1, 10**24)
BETA = Q(1, 10**9)
GRID = 10**27
COMPLEX_SAVING = Q(747454944651775, 10**18)
INITIAL_LEAF = Q(384599, 10**10)
BASE_MANIFEST_SHA256 = "6381aa8d881a4a89cf6c40db5bcd705b928a27599540a270bf3cd15f604c705d"
PUBLISHED_BASELINE = Q("0.000722869827347495")
EXPECTED_KAPPA = Q(724189082265949363570532, GRID)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_engine(name, base):
    path = base / (name + ".py")
    manifest = json.loads((base / "MANIFEST.json").read_text())
    assert sha(base / "MANIFEST.json") == BASE_MANIFEST_SHA256
    assert sha(path) == manifest["files"][path.name]
    spec = importlib.util.spec_from_file_location("gen4_pinned_" + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_word(path):
    blob = Path(path).read_bytes()
    assert len(blob) % 24 == 0, "Bad six-int32 record alignment"
    words = array("i")
    assert words.itemsize == 4
    words.frombytes(blob)
    if sys.byteorder != "little":
        words.byteswap()
    records = list(zip(*[iter(words)] * 6))
    assert all(record[0] in (0, 1, 2, 3) for record in records)
    return records


def word_inventory(candidate):
    records = read_word(candidate / "COHORT249-RECORDS.bin")
    histogram, opcounts, coefficients = Counter(), Counter(), Counter()
    for op, a, b, c, frame, category in records:
        opcounts[op] += 1
        if op == 0 and frame:
            histogram[frame] += 1
        elif op == 2:
            histogram[category] += 1
        elif op == 1:
            coefficients[abs(c)] += 1
    assert histogram and min(histogram) > 0 and max(histogram) < 24
    return records, histogram, opcounts, coefficients

def serial(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value

def bridge_template():
    # Literal retained bridge from source527 math_check.py, itself pinned in SOURCE.json.
    return dict(
        proof="PROOF.md",
        representation="Exact powers with source-bound finite overcharges",
        semantic=dict(G=dict(base=2, exponent=30000), E=dict(base=2, exponent=100000),
                      B_upper=dict(base=2, exponent=100001), C0=dict(base=2, exponent=210000),
                      C1=1, strict_literal_gap=1, induction_gap_lower=1),
        rows=dict(coefficient=20161, degree=10**6, suffix_slope=4*10**6,
                  degree_gap=Q(10**6) - Q(51*20161, 25)))

def fixed_moment(histogram, m, stock, calls, saving, cost):
    lo, hi = cost.moment(histogram, m, stock, saving, False)
    log_lo, log_hi = cost.logarithm(Q(m))
    exp_lo = cost.exponential(saving * log_lo, saving * log_lo)[0]
    exp_hi = cost.exponential(saving * log_hi, saving * log_hi)[1]
    fallback_weight = Q(32 * m * calls, stock) * RHO
    return cost.floor(lo + fallback_weight * exp_lo), cost.ceil(hi + fallback_weight * exp_hi)

def second_engine_with_fallback(histogram, m, stock, calls, saving, other):
    lower, upper = other.moment(m, stock, list(histogram.items()), saving)
    log_lo, log_hi = other.log_bounds(Q(m))
    exp_lo = other.exp_bounds(saving * log_lo)[0]
    exp_hi = other.exp_bounds(saving * log_hi)[1]
    fallback_weight = Q(32 * m * calls, stock) * RHO
    return lower + fallback_weight * exp_lo, upper + fallback_weight * exp_hi

def certify_coarse(histogram, m, stock, calls, cost, other):
    with localcontext() as ctx:
        ctx.prec = 80
        terms = [(Decimal(r*n) / Decimal(m*stock), (Decimal(m) / Decimal(r)).ln())
                 for r, n in histogram.items()]
        fallback = (Decimal(32*m*calls) / Decimal(stock)
                    * Decimal(2*m**3) / Decimal(PRIME))
        log_m = Decimal(m).ln()
        lower, upper = Decimal(0), Decimal("0.003")
        for _ in range(240):
            candidate = (lower + upper) / 2
            total = sum(p * (candidate * log_r).exp() for p, log_r in terms)
            total += fallback * (candidate * log_m).exp()
            if total < 1:
                lower = candidate
            else:
                upper = candidate
        endpoint = Q(int(((lower + upper) / 2 * GRID).to_integral_value(rounding=ROUND_FLOOR)), GRID)
    next_endpoint = endpoint + Q(1, GRID)
    first = fixed_moment(histogram, m, stock, calls, endpoint, cost)
    first_next = fixed_moment(histogram, m, stock, calls, next_endpoint, cost)
    second = second_engine_with_fallback(histogram, m, stock, calls, endpoint, other)
    second_next = second_engine_with_fallback(histogram, m, stock, calls, next_endpoint, other)
    assert first[1] < 1 < first_next[0]
    assert second[1] < 1 < second_next[0]
    return endpoint, next_endpoint, first, first_next, second, second_next

def grid_kappa(bit_saving, eta=ETA):
    q = bit_saving * (1 - 2*eta)
    minimum = (1 - eta) * q / (1 + q)
    ticks = minimum * GRID
    return Q((ticks.numerator - 1) // ticks.denominator, GRID)

def ceil_fraction(value):
    assert value >= 0
    return (value.numerator + value.denominator - 1) // value.denominator

def compute(candidate, base):
    candidate, base = Path(candidate).resolve(), Path(base).resolve()
    cost = load_engine("moment", base)
    other = load_engine("base_two_moment", base)
    outer = load_engine("outer", base)
    _, local, operations, coefficients = word_inventory(candidate)
    histogram = Counter({rank: 60 * count for rank, count in local.items()})
    histogram.update({rank: 24 * 1760 for rank in (4, 23, 46, 50)})
    histogram = dict(sorted(histogram.items()))
    stock = 255841  # Independently reconstructed from actual endpoints by admit.py.
    calls = sum(histogram.values())
    mass = sum(rank * count for rank, count in histogram.items())
    assert (calls, mass, 120 * stock - mass) == (5808240, 30648120, 52800)
    coarse, next_coarse, first, first_next, second, second_next = certify_coarse(
        histogram, 120, stock, calls, cost, other
    )
    chain, gaps = [INITIAL_LEAF], []
    for level in range(1, 9):
        old = chain[-1]
        new = (1 - coarse) * coarse + coarse * old
        assert old < new < coarse < 1 - new
        chain.append(new)
        gap = dict(atom=coarse-new, borrowing=1-new-coarse,
                   remainder=1-new-coarse*(1-old), stock=1-coarse)
        assert min(gap.values()) > 0
        gaps.append(dict(level=level, gaps=gap))
    kappa = grid_kappa(chain[-1])
    assembly = outer.assembly(chain[-1], COMPLEX_SAVING, bridge_template(),
                              kappa, eta=ETA, beta=BETA)
    assert len(assembly["strict_constraints"]) == 47
    assert min(assembly["strict_constraints"].values()) > 0
    try:
        outer.assembly(chain[-1], COMPLEX_SAVING, bridge_template(),
                       kappa + Q(1, GRID), eta=ETA, beta=BETA)
    except AssertionError:
        pass
    else:
        raise AssertionError("Adjacent finite-grid kappa admitted")
    assert kappa == EXPECTED_KAPPA
    target = PUBLISHED_BASELINE * Q(1001, 1000)
    assert kappa > target
    sources = [Path(__file__).resolve(), base / "MANIFEST.json"]
    sources += [base / (name + ".py") for name in ("moment", "base_two_moment", "outer")]
    sources += [candidate / name for name in ("COHORT249-RECORDS.bin", "COHORT249-INITIAL.json",
                                            "COHORT249-FINAL.json", "COHORT249-FRAMES.json")]
    return serial(dict(
        status="PASS_EXACT_ACTUAL_WORD_PRICE_REQUIRES_SEPARATE_CONSTRUCTION_ADMISSION",
        base_package=str(base), base_manifest_sha256=BASE_MANIFEST_SHA256,
        source_word_sha256=sha(candidate / "COHORT249-RECORDS.bin"),
        source_bindings={str(path): sha(path) for path in sources},
        literal_replicas=60, normalization_factor=5, stock=stock, literal_stock=5*stock,
        local_histogram=local, histogram=histogram, calls=calls, rank_mass=mass,
        deficit=52800, operation_counts=operations, scalar_coefficient_counts=coefficients,
        prime=PRIME, rare_density=RHO, full_fallback_kept=True,
        coarse=coarse, coarse_bracket=[coarse, next_coarse],
        first_engine_interval=first, first_engine_next_interval=first_next,
        second_engine_interval=second, second_engine_next_interval=second_next,
        ordinary_levels=8, ordinary_chain=chain, ordinary_gaps=gaps,
        assembly=assembly, kappa=kappa, kappa_decimal=cost.decimal(kappa),
        coarse_cap=grid_kappa(coarse), adjacent_grid_rejected_at_finite=True,
        published_PR276_kappa=PUBLISHED_BASELINE, strict_PR276_0p1_percent_target=target,
        gain_percent=100*(kappa-PUBLISHED_BASELINE)/PUBLISHED_BASELINE,
        exceeds_PR276_0p1_percent=True,
        scope="Exact pricing only. Source-bound scalar, geometry, chart, bank and finite "
              "construction admission are separate mandatory checks."
    ))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = compute(args.candidate, args.base)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print("PASS exact price", result["kappa_decimal"], flush=True)


if __name__ == "__main__":
    main()
