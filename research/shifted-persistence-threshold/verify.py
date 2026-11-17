#!/usr/bin/env python3
"""Exact finite corroboration of the shifted persistence threshold.

Produced by Nick Petalas. Apache-2.0.
The universal argument is in PROOF.md; this program uses integers only.
"""

import hashlib
import json
import platform
import sys
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def threshold(a: int, degree: int) -> int:
    """Return the new sufficient threshold, with D named degree."""
    if type(a) is not int or type(degree) is not int:
        raise ValueError("a and D must be positive integers")
    if a < 1 or degree < 1:
        raise ValueError("a and D must be positive integers")
    if a > degree:
        return 1
    return max(2, (3 * degree - a + 2 * a - 1) // (2 * a))


def step(a: int, degree: int, m: int) -> bool:
    return (m + 1) ** degree < (1 << a) * m ** degree


def check_shifted_power() -> dict[str, int]:
    powers = 0
    decreases = 0
    for m in range(2, 257):
        require((m + 1) ** (2 * m + 1) < 8 * m ** (2 * m + 1),
                f"shifted power failed at {m}")
        powers += 1
    for m in range(1, 256):
        # Cross-multiply F(m)>F(m+1), without logarithms or floats.
        left = (m + 1) ** (4 * m + 4)
        right = m ** (2 * m + 1) * (m + 2) ** (2 * m + 3)
        require(left > right, f"shifted decrease failed at {m}")
        decreases += 1
    return {"shifted_power_cases": powers, "decrease_cases": decreases}


def check_thresholds() -> dict[str, int]:
    parameters = 0
    steps = 0
    drops = 0
    for a in range(1, 97):
        for degree in range(1, 97):
            new = threshold(a, degree)
            old = (27 * degree + 17 * a - 1) // (17 * a)
            require(new <= old, f"threshold worsened at {a},{degree}")
            if a <= degree:
                require(a * (2 * new + 1) >= 3 * degree,
                        "shifted exponent hypothesis missing")
            for m in range(new, new + 3):
                require(step(a, degree, m), f"step failed at {a},{degree},{m}")
                steps += 1
            drops += int(new < old)
            parameters += 1
    return {"parameter_pairs": parameters, "step_cases": steps,
            "strict_threshold_drops": drops}


def check_controls() -> dict[str, int]:
    controls = (
        (threshold(1, 5) == 7, "new first working example missing"),
        (step(1, 5, 7) and not step(1, 5, 6), "seven not sharp"),
        (threshold(2, 5) == 4, "second example changed"),
        (step(2, 5, 4) and not step(2, 5, 3), "four not sharp"),
        (not step(1, 1, 1), "strict equality was accepted"),
        (threshold(1, 1) == 2, "m=1 equality exception missing"),
        (threshold(2, 1) == 1 and step(2, 1, 1), "m=1 success missing"),
        (threshold(1, 10) == 15 and step(1, 10, 14), "threshold not necessary"),
        # A smaller, unproved 7/5 slope would propose m=8 at D=6,a=1.
        (not step(1, 6, 8), "overstrong slope control did not reject"),
    )
    for condition, message in controls:
        require(condition, message)
    invalid = ((0, 1), (1, 0), (-1, 1), (1, -1),
               (True, 1), (1, False), (1.0, 1), (1, "1"))
    rejected = 0
    for a, degree in invalid:
        try:
            threshold(a, degree)
        except ValueError as error:
            require(str(error) == "a and D must be positive integers",
                    "wrong rejection reason")
            rejected += 1
        else:
            raise ValueError("invalid input accepted")
    return {"semantic_controls": len(controls), "invalid_input_controls": rejected}


def main() -> None:
    require(len(sys.argv) == 1, "usage: verify.py")
    counts = {}
    counts.update(check_shifted_power())
    counts.update(check_thresholds())
    counts.update(check_controls())
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "verify.py")
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
              for name in names}
    print(json.dumps({"status": "PASS_SHIFTED_PERSISTENCE_THRESHOLD",
                      "claim_type": "scoped proof with finite corroboration",
                      "counts": counts, "python": platform.python_version(),
                      "package_sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
