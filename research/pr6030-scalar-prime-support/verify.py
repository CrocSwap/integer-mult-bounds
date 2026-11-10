#!/usr/bin/env python3
"""Prime support of the scalar coefficients on the selected PR6030 word.

The classification is the finite census in PROOF.md. This program binds that
census to the pinned word and rejects coefficients outside it. It does not
discharge analytic_recovery.
"""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
import gzip
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORD = ROOT / "research/p104-helper470-twin-rung-removal/WORD.json.gz"
WORD_SHA256 = "7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f"
ODD_PARTS = {1, 3, 5, 7, 9}
CLEARING = 16
MAX_CLEARED = 256

# Opcode-resolved multiset. Combined value counts are in PROOF.md.
CENSUS = {
    ("ADD", "-16"): 3,
    ("ADD", "-8"): 5,
    ("ADD", "-4"): 99,
    ("ADD", "-3"): 3,
    ("ADD", "-9/4"): 1,
    ("ADD", "-2"): 442,
    ("ADD", "-3/2"): 16,
    ("ADD", "-5/4"): 6,
    ("ADD", "-1"): 2272,
    ("ADD", "-3/4"): 32,
    ("ADD", "-1/2"): 3189,
    ("ADD", "-3/8"): 2,
    ("ADD", "-1/4"): 2719,
    ("ADD", "-1/8"): 178,
    ("ADD", "-1/16"): 3,
    ("ADD", "1/16"): 2,
    ("ADD", "1/8"): 171,
    ("ADD", "1/4"): 2947,
    ("ADD", "3/8"): 1,
    ("ADD", "1/2"): 2513,
    ("ADD", "3/4"): 38,
    ("ADD", "1"): 3296,
    ("ADD", "5/4"): 1,
    ("ADD", "3/2"): 16,
    ("ADD", "7/4"): 2,
    ("ADD", "2"): 353,
    ("ADD", "5/2"): 1,
    ("ADD", "3"): 6,
    ("ADD", "4"): 64,
    ("ADD", "8"): 22,
    ("ADD", "10"): 1,
    ("COPY", "1"): 23,
    ("SCALE", "-8"): 1,
    ("SCALE", "-4"): 8,
    ("SCALE", "-2"): 136,
    ("SCALE", "-1"): 349,
    ("SCALE", "-1/2"): 82,
    ("SCALE", "-1/4"): 17,
    ("SCALE", "-1/8"): 1,
    ("SCALE", "1/4"): 13,
    ("SCALE", "1/2"): 144,
    ("SCALE", "2"): 99,
    ("SCALE", "4"): 11,
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def odd_and_valuation(q):
    """Return (2-valuation, positive odd part) of a nonzero rational."""
    need(q != 0, "zero coefficient")
    num = abs(q.numerator)
    den = q.denominator
    vnum = 0
    while num % 2 == 0:
        num //= 2
        vnum += 1
    vden = 0
    while den % 2 == 0:
        den //= 2
        vden += 1
    need(den == 1, "odd denominator " + str(q))
    need(num in ODD_PARTS, "odd part " + str(num) + " of " + str(q))
    valuation = vnum - vden
    need(-4 <= valuation <= 4, "valuation " + str(valuation) + " of " + str(q))
    cleared = q * CLEARING
    need(cleared.denominator == 1, "16q is not an integer for " + str(q))
    need(abs(cleared) <= MAX_CLEARED, "|16q| exceeds 256 for " + str(q))
    return valuation, num


def load_word():
    payload = WORD.read_bytes()
    need(sha256(payload).hexdigest() == WORD_SHA256, "selected word SHA256")
    word = json.loads(gzip.decompress(payload).decode("utf-8"))
    need(word.get("schema") == "p104-accumulated-block-composition/2", "word schema")
    need(word.get("public") == 770 and word.get("owned_fields") == 29, "inventory")
    need(isinstance(word.get("program"), list), "program")
    return word


def scalar_pairs(program):
    pairs = []
    for event in program:
        need(isinstance(event, list) and event, "event shape")
        op = event[0]
        if op not in ("ADD", "SCALE", "COPY"):
            continue
        need(len(event) == (4 if op == "SCALE" else 5), op + " shape")
        coefficient = Fraction(event[-2])
        odd_and_valuation(coefficient)
        pairs.append((op, str(coefficient)))
    return pairs


def check_census(pairs):
    got = Counter(pairs)
    need(got == Counter(CENSUS), "opcode census drifted")
    values = Counter(Fraction(coeff) for _op, coeff in pairs)
    need(len(values) == 31, "distinct coefficients")
    need(sum(values.values()) == 19288, "scalar event count")
    need(sum(n for (op, _c), n in got.items() if op == "ADD") == 18404, "ADD count")
    need(sum(n for (op, _c), n in got.items() if op == "SCALE") == 861, "SCALE count")
    need(got[("COPY", "1")] == 23, "COPY coefficients are not all +1")
    need(sum(n for q, n in values.items() if q.denominator == 16) == 5, "denominator 16")
    need(values[Fraction(-16)] == 3, "q=-16")
    need(Fraction(16) not in values, "q=+16 is absent")
    need(max(abs(q * CLEARING) for q in values) == MAX_CLEARED, "sharp cleared bound")
    odd_counts = Counter(odd_and_valuation(q)[1] for q, n in values.items() for _ in range(n))
    need(odd_counts == Counter({1: 19162, 3: 114, 5: 9, 7: 2, 9: 1}), "odd-part histogram")
    valuations = Counter(odd_and_valuation(q)[0] for q, n in values.items() for _ in range(n))
    need(valuations == Counter({
        -4: 5, -3: 353, -2: 5776, -1: 5961, 0: 5949,
        1: 1031, 2: 182, 3: 28, 4: 3,
    }), "valuation histogram")
    return values


def reject_coefficient(text):
    try:
        odd_and_valuation(Fraction(text))
    except ValueError:
        return
    raise ValueError("classifier accepted " + text)


def main():
    word = load_word()
    values = check_census(scalar_pairs(word["program"]))
    for bad in ("0", "11", "1/3", "1/32", "32", "15", "27", "1/48"):
        reject_coefficient(bad)
    # The 31 published values themselves must pass the factor test.
    for coefficient in values:
        odd_and_valuation(coefficient)
    print(
        "PASS_PR6030_SCALAR_PRIME_SUPPORT"
        " events=19288 distinct=31 adds=18404 scales=861 copies=23"
        " denom_lcm=16 max_abs_16q=256 odd_primes=3,5,7"
        " valuation=-4..4 no_new_kappa=true"
    )


if __name__ == "__main__":
    main()
