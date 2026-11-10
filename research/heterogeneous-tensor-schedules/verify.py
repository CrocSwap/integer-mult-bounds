"""Independent finite corroboration of the new schedule optimum.

Produced by Nick Petalas. Apache-2.0. No predecessor executable imports.
"""

from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from math import gcd, prod
from pathlib import Path

from schedule import MAX_LENGTH, MAX_RANK, Schedule, optimize


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def exhaustive_profiles() -> dict[str, int]:
    """Check every count, including all ties, without the crossing rule."""
    cases = observations = ties = 0
    profiles = tuple((r, c) for r in range(2, 8) for c in range(1, r))
    for (r, c), (s, d), n in product(profiles, profiles, range(1, 33)):
        values = tuple(min(Fraction(c**a, r**a), Fraction(d ** (n - a), s ** (n - a)))
                       for a in range(n + 1))
        best = max(values)
        counts = tuple(a for a, value in enumerate(values) if value == best)
        answer = optimize(r, c, s, d, n)
        require((answer.counts, answer.density) == (counts, best), "profile optimum")
        k = answer.crossing
        require(r**k * d ** (n - k) <= c**k * s ** (n - k), "left crossing")
        require(r ** (k + 1) * d ** (n - k - 1) > c ** (k + 1) * s ** (n - k - 1),
                "right crossing")
        cases += 1
        observations += len(values)
        ties += len(counts) == 2
    return {"profile_contracts": cases, "count_observations": observations, "ties": ties}


def tensor_diagonal(word: tuple[int, ...], first: tuple[int, ...],
                    second: tuple[int, ...]) -> list[int]:
    """Materialize every diagonal coefficient, in chronological factor order."""
    entries = [1]
    for letter in word:
        factor = (first, second)[letter]
        entries = [x * y for x in entries for y in factor]
    require(len(entries) <= 256, "literal tensor capacity")
    return entries


def smith_units(entries: list[int]) -> int:
    """Count dyadic units by exact gcd/lcm diagonal Smith operations.

    A two-entry update diag(a,b) -> diag(gcd(a,b),lcm(a,b)) is unimodular
    over Z. Subsequent updates preserve previous divisibility. This oracle
    does not use prime ranks, a count formula, or the schedule optimizer.
    """
    diagonal = entries.copy()
    for i in range(len(diagonal)):
        for j in range(i + 1, len(diagonal)):
            a, b = diagonal[i], diagonal[j]
            common = gcd(a, b)
            diagonal[i], diagonal[j] = common, a // common * b
    require(all(diagonal[i + 1] % diagonal[i] == 0 for i in range(len(diagonal) - 1)),
            "Smith divisibility")
    require(prod(diagonal) == prod(entries), "Smith determinant")
    # All literal fixtures are positive odd integers, whose only dyadic unit is 1.
    return diagonal.count(1)


def literal_schedules() -> dict[str, int]:
    """Exhaust complete binary words and compare the new global optimum."""
    families = (((1, 1, 3), (1, 5)), ((1, 3), (1, 1, 5)),
                ((1, 3), (1, 5)), ((1, 3, 3), (1, 1, 5)))
    words = coefficients = lengths = 0
    for first, second in families:
        r, c, s, d = len(first), first.count(1), len(second), second.count(1)
        for n in range(1, 6):
            best = Fraction(0)
            attained = set()
            for word in product((0, 1), repeat=n):
                entries = tensor_diagonal(word, first, second)
                density = Fraction(smith_units(entries), len(entries))
                if density > best:
                    best, attained = density, {word.count(0)}
                elif density == best:
                    attained.add(word.count(0))
                words += 1
                coefficients += len(entries)
            answer = optimize(r, c, s, d, n)
            require((answer.counts, answer.density) == (tuple(sorted(attained)), best),
                    "literal tensor schedule optimum")
            lengths += 1
    return {"literal_words": words, "literal_coefficients": coefficients,
            "literal_length_contracts": lengths}


def controls() -> dict[str, int]:
    rejected = 0
    bad = ((True, 1, 2, 1, 1), (2, 1, 2, 1, 1.0), (2, 0, 2, 1, 1),
           (2, 2, 2, 1, 1), (1, 1, 2, 1, 1), (2, 1, 2, -1, 1),
           (2, 1, 1, 1, 1), (MAX_RANK + 1, 1, 2, 1, 1),
           (2, 1, MAX_RANK + 1, 1, 1), (2, 1, 2, 1, 0),
           (2, 1, 2, 1, MAX_LENGTH + 1))
    for args in bad:
        try:
            optimize(*args)
        except (TypeError, ValueError):
            rejected += 1
        else:
            raise AssertionError("invalid profile accepted")
    edge = optimize(MAX_RANK, MAX_RANK - 1, 2, 1, MAX_LENGTH)
    # A shared bad prime violates the theorem's hypothesis, and its answer differs.
    common_prime_density = Fraction(smith_units(tensor_diagonal((0, 1), (1, 3), (1, 3))), 4)
    semantic = (
        (optimize(3, 2, 2, 1, 4) == Schedule(2, (3,), Fraction(8, 27)), "attainment"),
        (optimize(2, 1, 2, 1, 3).counts == (1, 2), "tie retention"),
        (optimize(4, 1, 2, 1, 3).crossing == 1, "crossing equality"),
        (optimize(3, 2, 2, 1, 1).counts == (1,), "single factor"),
        (all(0 <= a <= MAX_LENGTH for a in edge.counts), "capacity boundary"),
        (common_prime_density == Fraction(1, 4), "shared-prime fixture"),
        (common_prime_density != optimize(2, 1, 2, 1, 2).density, "disjoint defects"),
        (Fraction(8, 27) < Fraction(4, 9), "strict bound improvement"),
        (Fraction(8, 27) > Fraction(1, 4), "unequal multiplicities"),
    )
    for condition, message in semantic:
        require(condition, message)
    return {"invalid_profiles_rejected": rejected, "semantic_controls": len(semantic)}


def main() -> None:
    counts = exhaustive_profiles() | literal_schedules() | controls()
    root = Path(__file__).resolve().parent
    files = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "schedule.py", "verify.py")
    hashes = {}
    for name in files:
        path = root / name
        require(path.stat().st_size <= 256 * 1024, "package file capacity before read")
        data = path.read_bytes()
        require(len(data) <= 256 * 1024, "package file capacity")
        hashes[name] = sha256(data).hexdigest()
    entries = tensor_diagonal((0, 0, 0, 1), (1, 1, 3), (1, 5))
    capacity = smith_units(entries)
    example = {"r": 3, "c": 2, "s": 2, "d": 1, "n": 4,
               "first_counts": list(optimize(3, 2, 2, 1, 4).counts),
               "capacity": capacity, "rank": len(entries),
               "density": str(Fraction(capacity, len(entries)))}
    receipt = {"schema": "heterogeneous-tensor-schedules/1", "counts": counts,
               "example": example, "sha256": hashes}
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_HETEROGENEOUS_TENSOR_SCHEDULES")


if __name__ == "__main__":
    main()
