"""Riding shear sandwich.

A bridge, one shear of the owner, and the inverse bridge leave the owner's
partner wire changed by an increment. The rider's partner wire changes by the
coefficient times that increment.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
COEFFICIENT_BOUND = 6
COORDINATE_BOUND = 8


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_RIDING_SANDWICH selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def forward_sandwich(
    owner_x: int, owner_y: int, rider_x: int, rider_y: int, coefficient: int
) -> tuple[int, int, int, int]:
    owner_x += coefficient * rider_x
    rider_y -= coefficient * owner_y
    owner_y += owner_x
    owner_x -= coefficient * rider_x
    rider_y += coefficient * owner_y
    return owner_x, owner_y, rider_x, rider_y


def reverse_sandwich(
    owner_x: int, owner_y: int, rider_x: int, rider_y: int, coefficient: int
) -> tuple[int, int, int, int]:
    rider_x += coefficient * owner_x
    owner_y -= coefficient * rider_y
    owner_x -= owner_y
    rider_x -= coefficient * owner_x
    owner_y += coefficient * rider_y
    return owner_x, owner_y, rider_x, rider_y


def forward_expected(
    owner_x: int, owner_y: int, rider_x: int, rider_y: int, coefficient: int
) -> tuple[int, int, int, int]:
    increment = owner_x + coefficient * rider_x
    return owner_x, owner_y + increment, rider_x, rider_y + coefficient * increment


def reverse_expected(
    owner_x: int, owner_y: int, rider_x: int, rider_y: int, coefficient: int
) -> tuple[int, int, int, int]:
    increment = -owner_y + coefficient * rider_y
    return (
        owner_x + increment,
        owner_y,
        rider_x - coefficient * increment,
        rider_y,
    )


def main() -> None:
    pinned = load()
    states = 0
    values = range(-COORDINATE_BOUND, COORDINATE_BOUND + 1)
    for coefficient in range(-COEFFICIENT_BOUND, COEFFICIENT_BOUND + 1):
        for owner_x in values:
            for owner_y in values:
                for rider_x in values:
                    for rider_y in values:
                        state = (owner_x, owner_y, rider_x, rider_y)
                        if forward_sandwich(*state, coefficient) != forward_expected(*state, coefficient):
                            raise SystemExit("FAIL_RIDING_SANDWICH forward moved")
                        if reverse_sandwich(*state, coefficient) != reverse_expected(*state, coefficient):
                            raise SystemExit("FAIL_RIDING_SANDWICH reverse moved")
                        states += 1
    coefficients = 2 * COEFFICIENT_BOUND + 1
    if states != coefficients * (2 * COORDINATE_BOUND + 1) ** 4:
        raise SystemExit("FAIL_RIDING_SANDWICH count moved")
    # The loop counted one state per coefficient. Report the distinct wire states.
    distinct = states // coefficients
    if (
        pinned["coefficient_bound"] != COEFFICIENT_BOUND
        or pinned["coordinate_bound"] != COORDINATE_BOUND
        or pinned["states"] != distinct
        or pinned["coefficients"] != coefficients
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_RIDING_SANDWICH pinned result moved")
    print(f"PASS_RIDING_SANDWICH states={distinct} no_new_kappa")


if __name__ == "__main__":
    main()
