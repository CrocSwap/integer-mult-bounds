"""Exact arithmetic corroboration of the Lucas specialization; no matrix replay."""

from hashlib import sha256
from math import comb
from pathlib import Path
import json


MAX_H = 512
FILES = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def checked_index(h: int) -> None:
    if type(h) is not int or not 0 <= h <= MAX_H:
        raise ValueError("index must be an integer between zero and MAX_H")


def fibonacci_pair(h: int) -> tuple[int, int]:
    """Return F_h,F_(h+1) by bounded, iterative fast doubling."""
    checked_index(h)
    a, b = 0, 1
    for bit in bin(h)[2:]:
        c, d = a * (2 * b - a), a * a + b * b
        a, b = (c, d) if bit == "0" else (d, c + d)
    return a, b


def lucas(h: int) -> int:
    a, b = fibonacci_pair(h)
    return 2 * b - a


def closed_blocks(h: int) -> int:
    checked_index(h)
    if h % 2:
        raise ValueError("block formula requires an even index")
    numerator = (1 << h) + 2 * lucas(h)
    value, remainder = divmod(numerator, 5)
    require(remainder == 0, "block numerator is not divisible by five")
    return value


def repair_rank(h: int) -> int:
    checked_index(h)
    if h < 4 or h % 4:
        raise ValueError("rank specialization requires a positive multiple of four")
    numerator = 4 * (1 << h) - 2 * lucas(h) - 5
    value, remainder = divmod(numerator, 5)
    require(remainder == 0, "rank numerator is not divisible by five")
    require(0 <= value <= (1 << h) - 2, "rank outside proper-subset dimension")
    return value


def literal_step(counts: tuple[int, ...]) -> tuple[int, ...]:
    """Apply the cited replacements literally, without a Fibonacci formula."""
    rules = ((1,), (0, 2), (1, 3), (2, 4), (4, 4))
    result = [0] * 5
    for count, replacements in zip(counts, rules, strict=True):
        for target in replacements:
            result[target] += count
    return tuple(result)


def binomial_lucas(h: int) -> int:
    """Independent sum for cycle matchings; no Fibonacci calls or recurrence."""
    checked_index(h)
    if h == 0:
        return 2
    return 1 + sum(
        comb(h - j, j) + comb(h - j - 1, j - 1)
        for j in range(1, h // 2 + 1)
    )


def check_formulas() -> dict:
    counts = (1, 0, 0, 0, 0)
    even_cases, rank_cases, formula_cases = 0, 0, 0
    digest = sha256()
    for h in range(MAX_H + 1):
        require(sum((j + 1) * c for j, c in enumerate(counts)) == 1 << h,
                f"dimension invariant failed at {h}")
        require(lucas(h) == binomial_lucas(h), f"Lucas engines disagree at {h}")
        if h >= 1:
            f, g = fibonacci_pair(h)
            first, third = g - f, f
            actual = (counts[0], counts[2]) if h % 2 == 0 else (counts[3], counts[1])
            require(actual == (first, third), f"multiplicity formula failed at {h}")
            require(counts[1] == counts[3] == 0 if h % 2 == 0
                    else counts[0] == counts[2] == 0, f"parity failed at {h}")
            formula_cases += 1
        if h % 2 == 0:
            require(closed_blocks(h) == sum(counts), f"block count failed at {h}")
            even_cases += 1
        if h >= 4 and h % 4 == 0:
            expected = (1 << h) - 1 - sum(counts)
            require(repair_rank(h) == expected, f"rank substitution failed at {h}")
            rank_cases += 1
        digest.update((json.dumps([h, counts], separators=(",", ":")) + "\n").encode())
        counts = literal_step(counts)
    require((repair_rank(4), repair_rank(8)) == (9, 185), "inherited examples changed")
    return {"indices": MAX_H + 1, "multiplicity_cases": formula_cases,
            "even_block_cases": even_cases, "rank_specializations": rank_cases,
            "transcript_sha256": digest.hexdigest()}


def check_controls() -> dict:
    invalid = (-1, MAX_H + 1, True, 1.5, "4", None)
    rejected = 0
    for h in invalid:
        try:
            fibonacci_pair(h)
        except ValueError:
            rejected += 1
        else:
            raise ValueError(f"accepted invalid index {h!r}")
    for h in (0, 1, 2, 3, 6, MAX_H + 4):
        try:
            repair_rank(h)
        except ValueError:
            rejected += 1
        else:
            raise ValueError(f"accepted invalid rank dimension {h}")
    for h in (1, 3, MAX_H - 1):
        try:
            closed_blocks(h)
        except ValueError:
            rejected += 1
        else:
            raise ValueError(f"accepted odd block dimension {h}")
    witnesses = {}
    for name, exponential, coefficient, constant, denominator in (
        ("wrong_exponential", 3, -2, -5, 5),
        ("wrong_lucas_sign", 4, 2, -5, 5),
        ("missing_lucas_factor", 4, -1, -5, 5),
        ("missing_endpoint", 4, -2, 0, 5),
        ("wrong_denominator", 4, -2, -5, 4),
    ):
        for h in range(4, MAX_H + 1, 4):
            wrong = exponential * (1 << h) + coefficient * lucas(h) + constant
            if wrong != denominator * repair_rank(h):
                witnesses[name] = h
                break
        require(name in witnesses, f"mutant survived: {name}")
    return {"invalid_inputs_rejected": rejected, "mutant_first_counterexamples": witnesses}


def main() -> None:
    package = Path(__file__).resolve().parent
    require(tuple(sorted(p.name for p in package.iterdir() if p.is_file())) == FILES,
            "unexpected package file inventory")
    results = check_formulas()
    controls = check_controls()
    hashes = {name: sha256((package / name).read_bytes()).hexdigest() for name in FILES}
    print(json.dumps({"claim_type": "scoped arithmetic proof with cited rank premise",
                      "results": results, "controls": controls,
                      "package_sha256": hashes}, sort_keys=True, indent=2))
    print("PASS_QUINARY_REPAIR_LUCAS_FORMULA")


if __name__ == "__main__":
    main()
