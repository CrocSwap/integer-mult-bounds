#!/usr/bin/env python3
"""Exact premises for the PR2234 stock-fit theorem; see README for the proof.

Aakash (@aakashthakkar), with substantial OpenAI Codex assistance. Apache-2.0.
No floating point, external dependencies, predecessor execution or regeneration.
"""
from fractions import Fraction
import hashlib
import json
from math import gcd, lcm
from pathlib import Path
import re
import sys

PACKAGE = Path(__file__).resolve().parent
LIVE = 28416
PHYSICAL = 28425
MULTIPLICITY = 269241600
DIMENSION = 64
MAX_RANK = 42
POWER = Fraction(17, 10000)
CUTOFF = 311311
TAIL = 1 << 20
WITNESS_Q = 213 * (1 << 80) + 1


class VerificationError(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise VerificationError(message)


def depth(e):
    """Literal source recurrence, evaluated without recursion or a depth cache."""
    require(type(e) is int and e >= 0, "width must be a nonnegative integer")
    result = 0
    while e >= DIMENSION:
        e = MAX_RANK * (e // DIMENSION)
        result += 1
    return result


def thresholds(limit):
    """First width of each positive depth, including the first beyond limit."""
    require(type(limit) is int and limit >= DIMENSION, "invalid threshold limit")
    result = [DIMENSION]
    while result[-1] <= limit:
        result.append(DIMENSION * ((result[-1] + MAX_RANK - 1) // MAX_RANK))
    return result


def atom_width(e):
    """Exact ceil(e**(17/10000)); only bounded boundary probes call this."""
    require(type(e) is int and e >= 1, "atom width requires a positive integer")
    target = e ** POWER.numerator
    lo, hi = 0, 1
    while hi ** POWER.denominator < target:
        lo, hi = hi, 2 * hi
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if mid ** POWER.denominator >= target:
            hi = mid
        else:
            lo = mid
    return hi


def guard(e, w=None):
    """Upper bound on ceil(log_q S); optional w is a caller-proved atom width."""
    if w is None:
        w = atom_width(e)
    require(type(w) is int and w >= 1, "invalid atom width")
    d = depth(e)
    return DIMENSION**2 * w * d + (29 * d + 79) // 80


def verify_proth(q, k=213, s=80, base=7):
    """Check the elementary prime certificate proved in README section 4."""
    require(type(q) is int and type(k) is int and type(s) is int,
            "integer prime certificate required")
    require(s >= 1 and 0 < k < 1 << s and k % 2 == 1, "invalid Proth shape")
    require(q == k * (1 << s) + 1, "prime certificate shape mismatch")
    require(1 < base < q and gcd(base, q) == 1, "nonunit prime witness")
    residue = pow(base, (q - 1) // 2, q)
    require(residue == q - 1, "prime witness does not give minus one")
    require(((1 << s) + 1)**2 > q, "prime-divisor lower bound too small")
    return {"q": str(q), "odd_multiplier": k, "two_exponent": s,
            "base": base, "modular_residue": str(residue)}


def sharpness_certificate(q=WITNESS_Q, base=7):
    prime = verify_proth(q, base=base)
    e = CUTOFF - 1
    d, w = depth(e), atom_width(e)
    require((d, w) == (19, 2), "wrong boundary depth or atom width")
    require(q > 1 << 80, "prime outside the source domain")
    # P=product(1-q^-i) > 1-1/(q-1), so P^d > 1-d/(q-1) > 1/2.
    require(2 * d < q - 1, "cover-product lower bound fails")
    power = MULTIPLICITY**d
    require(2 * q**6 < power, "sixth-power lower witness fails")
    require(power < q**7, "seventh-power upper witness fails")
    integral_part = DIMENSION**2 * w * d
    stock_digits = integral_part + 7
    require(2 * stock_digits == e, "boundary is not an exact strict-fit failure")
    return {"width": e, "atom_width": w, "depth": d,
            "prime_certificate": prime,
            "log_q_stock_open_interval": [integral_part + 6, integral_part + 7],
            "borrowed_digits": stock_digits, "twice_borrowed_digits": e,
            "integer_power_checks": {"2*q^6<M^19": True, "M^19<q^7": True}}


def verify_sources(package=PACKAGE):
    """Authenticate retained text before reading any source-defined constants."""
    package = Path(package)
    manifest = json.loads((package / "SOURCES.json").read_text(encoding="utf-8"))
    sources = manifest["external_sources"]
    expected_paths = {"sources/pr2234/PROOF.md", "sources/pr2234/NOTICE.md"}
    require({row["path"] for row in sources} == expected_paths and len(sources) == 2,
            "predecessor source inventory mismatch")
    payloads = {}
    for row in sources:
        require(row["source_commit"] == "d047ef86fbc5b1614d3d8e2b8d3441413beab73f",
                "unexpected predecessor commit")
        data = (package / row["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row["sha256"],
                "source SHA256 mismatch: " + row["path"])
        blob = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
        require(blob == row["git_blob"], "source Git blob mismatch: " + row["path"])
        payloads[row["path"]] = data.decode("utf-8")
    proof = payloads["sources/pr2234/PROOF.md"]
    require(re.search(r"c=17/10000, and w=ceil\(e\^c\)", proof), "atom-power definition drift")
    for fragment in (
        "one odd prime q>2^80", "Let W=28416 live families, P=28425 physical slots, M=lcm(W,P)=269241600",
        "N=|GL64(F_q)|, H=q^(4096(w-1)), and K=MNH", "D(n)=0 for n<64; D(n)=1+D(42 floor(n/64)) otherwise",
        "S=K(w)^D(e) from the original width e", "Borrow k=ceil(log_q S)", "Eventually k<e/2",
    ):
        require(fragment in proof, "source-definition drift: " + fragment)
    return {row["path"]: row["sha256"] for row in sources}


def build_receipt():
    require(lcm(LIVE, PHYSICAL) == MULTIPLICITY, "physical/live lcm mismatch")
    require(MULTIPLICITY < 1 << 29, "multiplicity logarithm allowance fails")
    require(2 * MAX_RANK**2 < DIMENSION**2, "two-level halving fails")
    require(20 * POWER < 1, "finite interval no longer has atom width two")
    stairs = thresholds(TAIL)
    finite = []
    for d, (start, end) in enumerate(zip(stairs, stairs[1:]), 1):
        lo, hi = max(CUTOFF, start), min(TAIL - 1, end - 1)
        if lo > hi:
            continue
        require(depth(lo) == d == depth(hi), "inverse-depth boundary mismatch")
        upper = DIMENSION**2 * 2 * d + (29 * d + 79) // 80
        require(2 * upper < lo, "finite interval is not strictly safe")
        finite.append({"first": lo, "last": hi, "depth": d, "atom_width": 2,
                       "stock_digit_upper": upper, "strict_margin_at_first": lo - 2 * upper})
    require(finite[0]["first"] == CUTOFF and finite[-1]["last"] == TAIL - 1,
            "finite proof does not reach both endpoints")
    require(all(left["last"] + 1 == right["first"] for left, right in zip(finite, finite[1:])),
            "finite proof has a coverage gap")
    # Infinite tail: B_j=16388*(j+1)*2^(c*(j+1)), j=floor(log2 e)>=20.
    # All irrational comparisons are discharged by c*21<1/2 and sqrt(2)<3/2.
    require(21 * POWER < Fraction(1, 2), "tail base exponent fails")
    require(POWER < Fraction(1, 2) and Fraction(3, 2)**2 > 2, "tail ratio premise fails")
    coefficient = 4 * (DIMENSION**2 + 1)
    base_upper = coefficient * 21 * Fraction(3, 2) + 1
    contraction = Fraction(22, 21) * Fraction(3, 4)
    require(base_upper < 1 << 19, "tail base has no strict margin")
    require(Fraction(1, 2) <= contraction < 1, "tail plus-one term does not contract")
    witness = sharpness_certificate()
    return {
        "schema_version": 1,
        "status": "PROVED_STOCK_FIT_ONLY",
        "scope": "Prescribed PR2234 K(w)^D(e), all integer e and all primes q>2^80; not supplier admission.",
        "cutoff": CUTOFF,
        "parameters": {"dimension": DIMENSION, "maximum_rank": MAX_RANK, "live_families": LIVE,
                       "physical_slots": PHYSICAL, "multiplicity": MULTIPLICITY,
                       "atom_power": str(POWER), "source_pr": 2234},
        "depth_thresholds_through_tail": stairs,
        "finite_intervals": finite,
        "tail": {"first_width": TAIL, "first_dyadic_index": 20,
                 "stock_bound_coefficient": coefficient, "base_upper_plus_one": str(base_upper),
                 "half_width_at_base": 1 << 19, "normalized_contraction_upper": str(contraction)},
        "sharpness": witness,
    }


def main():
    try:
        verify_sources()
        expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
        actual = build_receipt()
        canonical = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        require(canonical(actual) == canonical(expected),
                "stored receipt differs from exact reconstruction")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("FAIL_BIT2234_STOCK_THRESHOLD: " + str(exc), file=sys.stderr)
        return 1
    print("PASS_BIT2234_STOCK_THRESHOLD cutoff=311311 boundary=311310 intervals=4 "
          "uniform_prime_domain=q>2^80 exact_prime_witness=verified no_new_kappa")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
