"""Bounded two-band producer. Produced by Nick Petalas. Apache-2.0.

Host reference and exact checks, not the predecessor's encoded runtime.
"""

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def band(target, d):
    require(type(target) is int and 2 <= target <= 65536, "target domain")
    require(type(d) is int and 2 <= d <= 33, "dimension domain")
    return (target - (target + 3*d - 1) // (3*d) + 1,
            target - (target + 4*d - 1) // (4*d))


def prime_trial(candidate):
    require(type(candidate) is int and 2 <= candidate <= 65536, "candidate domain")
    divisions = 0
    comparisons = 0
    # Bounded reference: no square-root oracle and no unbounded while loop.
    for divisor in range(2, 258):
        comparisons += 1
        if divisor * divisor > candidate:
            return True, divisions, comparisons
        divisions += 1
        if candidate % divisor == 0:
            return False, divisions, comparisons
    raise ValueError("divisor capacity exhausted")


def select(target, d, quota):
    low, high = band(target, d)
    require(type(quota) is int and 0 <= quota < d, "quota domain")
    selected = []
    work = dict(candidates=0, divisions=0, comparisons=0)
    if quota == 0:
        return selected, work
    for candidate in range(low, high + 1):
        passed, divisions, comparisons = prime_trial(candidate)
        work["candidates"] += 1
        work["divisions"] += divisions
        work["comparisons"] += comparisons
        if passed:
            selected.append(candidate)
        if len(selected) == quota:
            return selected, work
    raise ValueError("insufficient primes in finite request")


def merge_and_erase(tables, flags, ell):
    """Model sequential bit-cell copies, erasure, and head returns."""
    require(len(tables) == 2 and 2 <= ell <= 16, "merge shape")
    require(1 <= len(flags) <= 32 and all(type(f) is int and f in (0, 1)
                                       for f in flags), "merge flags")
    require(sum(len(table) for table in tables) == len(flags), "table capacity")
    require(all(type(n) is int and 0 <= n < 1 << ell
                for table in tables for n in table), "table words")
    pages = [bytearray((n >> j) & 1 for n in table for j in range(ell))
             for table in tables]
    heads = [0, 0]
    output = bytearray()
    moves = 0
    for flag in flags:
        for _ in range(ell):
            require(heads[flag] < len(pages[flag]), "table underflow")
            output.append(pages[flag][heads[flag]])
            heads[flag] += 1
            moves += 2
    require(heads == [len(page) for page in pages], "unconsumed table")
    for scale in range(2):
        for _ in range(len(pages[scale])):
            heads[scale] -= 1
            pages[scale][heads[scale]] = 2  # distinguished blank symbol
            moves += 1
    moves += len(output)  # return output head
    moves += 2 * (len(flags) - 1)  # borrowed flags, last one is implicit
    require(heads == [0, 0], "table head return")
    require(all(cell == 2 for page in pages for cell in page), "table erasure")
    return bytes(output), moves


def produce(ell, supplied_flags):
    require(type(ell) is int and 2 <= ell <= 16, "width domain")
    require(type(supplied_flags) is tuple and len(supplied_flags) <= 31,
            "flag stream domain")
    require(all(type(f) is int and f in (0, 1) for f in supplied_flags),
            "literal binary flags")
    flags = supplied_flags + (1,)
    d = len(flags) + 1
    tables = []
    work = dict(candidates=0, divisions=0, comparisons=0)
    for scale in range(2):
        table, counts = select(1 << (ell - 1 + scale), d, flags.count(scale))
        tables.append(table)
        for name in work:
            work[name] += counts[name]
    output, work["stream_head_moves"] = merge_and_erase(tables, flags, ell)
    return output, work


def sieve(cap):
    require(type(cap) is int and 2 <= cap <= 65536, "sieve capacity")
    composite = bytearray(cap + 1)
    composite[0] = composite[1] = 1
    for divisor in range(2, cap + 1):
        if not composite[divisor]:
            for multiple in range(divisor + divisor, cap + 1, divisor):
                composite[multiple] = 1
    return composite


def oracle(ell, supplied_flags, composite):
    flags = supplied_flags + (1,)
    d = len(flags) + 1
    tables = []
    for scale in range(2):
        target = 1 << (ell - 1 + scale)
        # Integer cross-products independently implement rational membership.
        table = [n for n in range(2, target)
                 if target * (3*d - 1) < n * 3*d
                 and n * 4*d <= target * (4*d - 1) and not composite[n]]
        quota = flags.count(scale)
        if len(table) < quota:
            return None
        tables.append(table[:quota])
    positions = [0, 0]
    numbers = []
    for flag in flags:
        numbers.append(tables[flag][positions[flag]])
        positions[flag] += 1
    return tuple(numbers)


def decode(output, ell):
    require(type(ell) is int and 2 <= ell <= 16, "decode width")
    require(len(output) % ell == 0 and len(output) <= 512, "output size")
    require(all(cell in (0, 1) for cell in output), "output alphabet")
    return tuple(sum(output[offset + j] << j for j in range(ell))
                 for offset in range(0, len(output), ell))


def check_output(output, ell, flags, expected):
    numbers = decode(output, ell)
    require(numbers == expected, "ordered source words")
    require(len(set(numbers)) == len(numbers), "distinct sources")
    d = len(numbers) + 1
    for value, flag in zip(numbers, flags + (1,), strict=True):
        target = 1 << (ell - 1 + flag)
        require(value % 2 == 1, "odd sources")
        require(Fraction(target * (3*d - 1), 3*d) < value
                <= Fraction(target * (4*d - 1), 4*d), "source band")


def check_primality(composite):
    counts = dict(integers=0, divisions=0, comparisons=0)
    for candidate in range(2, len(composite)):
        prime, divisions, comparisons = prime_trial(candidate)
        require(prime == (not composite[candidate]), "sieve disagreement")
        require(divisions <= 255 and comparisons <= 256, "work capacity")
        counts["integers"] += 1
        counts["divisions"] += divisions
        counts["comparisons"] += comparisons
    return counts


def check_endpoints():
    cases = 0
    for target in range(2, 258):
        for d in range(2, 34):
            low, high = band(target, d)
            expected = tuple(n for n in range(2, target + 1)
                             if target * (3*d - 1) < n * 3*d
                             and n * 4*d <= target * (4*d - 1))
            require(tuple(range(low, high + 1)) == expected, "band endpoints")
            require(high - low + 1 <= Fraction(target, 12*d) + 1,
                    "band cardinality envelope")
            cases += 1
    return cases


def expect_supply_failure(ell, flags):
    try:
        produce(ell, flags)
    except ValueError as error:
        require(str(error) == "insufficient primes in finite request",
                "unexpected producer failure")
        return
    raise ValueError("accepted exhausted request")


def check_producers(composite):
    counts = dict(requests=0, successes=0, supply_failures=0, source_words=0,
                  candidates=0, divisions=0, comparisons=0, stream_head_moves=0)
    for ell in range(3, 13):
        for dimensions in range(1, 8):
            for flags in itertools.product((0, 1), repeat=dimensions - 1):
                counts["requests"] += 1
                expected = oracle(ell, flags, composite)
                if expected is None:
                    expect_supply_failure(ell, flags)
                    counts["supply_failures"] += 1
                    continue
                output, work = produce(ell, flags)
                check_output(output, ell, flags, expected)
                d = dimensions + 1
                candidate_cap = Fraction(1 << ell, 8*d) + 2
                root_cap = 1 << ((ell + 1) // 2)
                require(work["candidates"] <= candidate_cap, "candidate envelope")
                for name in ("divisions", "comparisons"):
                    require(work[name] <= candidate_cap * root_cap, "work envelope")
                require(work["stream_head_moves"] == 4 * dimensions * ell
                        + 2 * (dimensions - 1), "stream movement bill")
                counts["successes"] += 1
                counts["source_words"] += dimensions
                for name, value in work.items():
                    counts[name] += value
    return counts


def check_controls():
    # Fixed local targets only. Unexpected failures propagate.
    fixtures = [
        (band, (1, 2)), (band, (8, 1)), (prime_trial, (1,)),
        (prime_trial, (65537,)), (produce, (17, ())),
        (produce, (8, [0])), (produce, (8, (True,))),
        (produce, (8, (2,))), (produce, (8, (0,) * 32)),
        (select, (64, 2, 2)), (merge_and_erase, ([[3], []], (1,), 4)),
        (decode, (b"\x00\x02", 2)),
        (check_output, (b"\x01\x00\x00\x00", 4, (), (13,))),
    ]
    for function, arguments in fixtures:
        try:
            function(*arguments)
        except ValueError:
            continue
        raise ValueError("negative control accepted")
    require(not prime_trial(49)[0], "square endpoint 49")
    require(not prime_trial(121)[0], "square endpoint 121")
    require(prime_trial(65521)[0], "large prime capacity")
    expect_supply_failure(2, ())
    return dict(rejected_contracts=len(fixtures), positive_boundaries=3,
                deliberate_supply_failure=1)


def package_hashes():
    root = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        with (root / name).open("rb") as handle:
            data = handle.read(1048577)
        require(len(data) <= 1048576, "package file capacity")
        hashes[name] = hashlib.sha256(data).hexdigest()
    return hashes


def main():
    composite = sieve(65536)
    result = {"claim_type": "scoped constructive proof with finite corroboration",
              "encoded_execution": False, "primality": check_primality(composite),
              "endpoint_cases": check_endpoints(),
              "producer_cases": check_producers(composite),
              "controls": check_controls(), "package_sha256": package_hashes(),
              "status": "PASS_TWO_BAND_PRIME_PRODUCER"}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
