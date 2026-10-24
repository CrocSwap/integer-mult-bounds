#!/usr/bin/env python3
"""Verify the new cache directly from congruences, without predecessor replay."""

from itertools import permutations, product
from math import gcd, prod
from pathlib import Path
import hashlib
import json
import runpy


API = runpy.run_path(str(Path(__file__).with_name("cache.py")))
prepare = API["prepare"]
require = API["require"]


class InverseSpy:
    def __init__(self) -> None:
        self.calls = []

    def __call__(self, value: int, modulus: int) -> int:
        require(not self.calls, "second inverse-provider call")
        self.calls.append((value, modulus))
        return pow(value, -1, modulus)


def oracle_integer(residues: tuple, moduli: tuple) -> int:
    """Small bounded oracle: find the unique number by direct enumeration."""
    scaled = []
    prefix = 1
    for residue, modulus in zip(residues, moduli):
        scaled.append(residue * prefix % modulus)
        prefix *= modulus
    matches = [value for value in range(prod(moduli))
               if all(value % modulus == residue
                      for modulus, residue in zip(moduli, scaled))]
    require(len(matches) == 1, "CRT oracle did not have a unique result")
    return matches[0]


def check_case(moduli: tuple, target: int, prefix: int, exhaustive: bool) -> dict:
    spy = InverseSpy()
    cache = prepare(moduli, target, prefix, spy)
    require(len(spy.calls) == 1, "setup must make exactly one inverse call")
    require(spy.calls[0] == (cache.unit, cache.full_modulus), "wrong provider arguments")
    require(cache.full_modulus == prod(moduli) * target, "wrong combined modulus")
    for modulus, coefficient in zip(moduli, cache.coefficients):
        require((cache.product // modulus) * coefficient % modulus == 1,
                "extracted coefficient does not solve its congruence")
    require(cache.product * prefix * cache.target_inverse % target == 1,
            "extracted target inverse does not solve its congruence")
    vectors = product(*(range(modulus + 1) for modulus in moduli)) if exhaustive else (
        tuple(0 for _ in moduli), tuple(modulus - 1 for modulus in moduli),
        tuple(moduli))
    count = 0
    for residues in vectors:
        count += 1
        valid, integer, offset = cache.evaluate(residues)
        expected_valid = all(value < modulus for value, modulus in zip(residues, moduli))
        require(valid == expected_valid, "padded validity changed")
        if not valid:
            require((integer, offset) == (0, 0), "invalid vector must disable offset")
            continue
        if exhaustive:
            require(integer == oracle_integer(residues, moduli), "reconstruction changed")
        preceding = 1
        for residue, modulus in zip(residues, moduli):
            require(integer % modulus == residue * preceding % modulus,
                    "locally scaled congruence failed")
            preceding *= modulus
        require(offset * cache.product * prefix % target == integer % target,
                "target offset changed")
    require(len(spy.calls) == 1, "evaluation must make no inverse calls")
    return {"vectors": count, "modulus_bits": cache.full_modulus.bit_length()}


def expect_rejection(operation) -> None:
    try:
        operation()
    except (TypeError, ValueError):
        return
    raise ValueError("negative control was accepted")


def check_controls() -> dict:
    cases = [((), 5, 1), ((True,), 5, 1), ((1,), 5, 1), ((3,), True, 1),
             ((3,), 5, 0), ((6, 10), 7, 1), ((3, 5), 15, 1), ((3, 5), 7, 7)]
    for moduli, target, prefix in cases:
        expect_rejection(lambda: prepare(moduli, target, prefix))
    for bad in (True, -1, 0, 999999):
        expect_rejection(lambda: prepare((3, 5), 7, 1, lambda u, m: bad))
    cache = prepare((3, 5), 7)
    for residues in ((1,), (True, 1), (-1, 0), [0, 0]):
        expect_rejection(lambda: cache.evaluate(residues))
    # Omitting the target summand leaves the packed unit divisible by target.
    packed_without_target = 7 * ((5 + 3) % 15) % 105
    require(gcd(packed_without_target, 105) == 7, "target-omission control failed")
    # Both extraction multipliers are necessary, even in the first source fixture.
    fixture = prepare((11, 13), 17)
    require(any(fixture.unit_inverse % n != a
                for n, a in zip(fixture.moduli, fixture.coefficients)),
            "left-multiplier omission control failed")
    require(fixture.unit_inverse % 17 != fixture.target_inverse,
            "target-multiplier omission control failed")
    return {"rejected_inputs_or_providers": len(cases) + 4 + 4,
            "semantic_omissions_detected": 3}


def main() -> None:
    cases = []
    for triple in permutations((2, 3, 4, 5, 7, 8, 9), 3):
        if any(gcd(a, b) != 1 for a, b in ((triple[0], triple[1]),
                                         (triple[0], triple[2]),
                                         (triple[1], triple[2]))):
            continue
        for prefix in (1, 11):
            cases.append(check_case(triple[:2], triple[2], prefix, True))
    for moduli, target, prefix in (((11, 13), 17, 1), ((4, 9, 25), 49, 11),
                                   ((3,), 5, 1), ((3, 4, 5, 7), 11, 13),
                                   ((2**127 - 1,), 2**61 - 1, 2**521 - 1)):
        cases.append(check_case(moduli, target, prefix, False))
    fixture = prepare((11, 13), 17)
    controls = check_controls()
    hashes = {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
              for name in ("cache.py", "verify.py")}
    print(json.dumps({"status": "PASS_CRT_ONE_INVERSE_CACHE", "cases": len(cases),
                      "vectors": sum(case["vectors"] for case in cases),
                      "max_inversion_modulus_bits": max(case["modulus_bits"] for case in cases),
                      "controls": controls,
                      "source_fixture": {"unit": fixture.unit,
                                         "inverse_modulus": fixture.full_modulus,
                                         "inverse": fixture.unit_inverse,
                                         "alpha": fixture.coefficients,
                                         "mu": fixture.target_inverse},
                      "sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
