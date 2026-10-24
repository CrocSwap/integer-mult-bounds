#!/usr/bin/env python3
"""Controls that do not import verify.py.

The subtraction gcd and the factored product (B*S)*(G0*3^4)*rows*3^124
must recover the same ratio. Witnesses that drop a factor, or that treat
the 972-bit packet as the parent, are rejected.
"""

from __future__ import annotations


def subtraction_gcd(left: int, right: int) -> int:
    while left != right:
        if left > right:
            left -= right
        else:
            right -= left
    return left


def main() -> None:
    width = 28416
    other = 28425
    divisor = subtraction_gcd(width, other)
    if divisor != 3:
        raise SystemExit(f"gcd {divisor}")
    # Euclid is not used. Cancel the common 3, then multiply.
    combined = (width // divisor) * other
    if combined != 269241600:
        raise SystemExit(f"lcm {combined}")
    if combined // width != 9475 or width * 9475 != combined:
        raise SystemExit("unused-row quotient")

    before, gap, suffix = 2, 3, 2
    atom = 3**4
    executed = (before * suffix) * (gap * atom)
    if executed != 972:
        raise SystemExit(f"executed {executed}")
    omitted = 124
    rows = 9475
    ratio = rows * 3**omitted
    parent = executed * ratio
    if parent != rows * 12 * 3**128:
        raise SystemExit("parent association")
    if parent != rows * before * (gap * 3**omitted) * suffix * atom:
        raise SystemExit("extent association")

    def pays(packet: int, payload: int) -> bool:
        return packet >= payload

    if pays(executed, parent):
        raise SystemExit("972-bit packet was treated as the parent")
    if pays(executed * rows, parent):
        raise SystemExit("dropping the 124 coordinates was accepted")
    if pays(executed * 3**omitted, parent):
        raise SystemExit("dropping the 9475 rows was accepted")
    if (executed * (ratio // 3)) >= parent:
        raise SystemExit("off-by-one coordinate power was accepted")
    # Without the four-atom factor the extent product is 12, not 972.
    if before * gap * suffix == 972:
        raise SystemExit("atom factor was not required")
    print(
        "PASS_R437_PARENT_SPECTATOR_BLANK_CONTROLS "
        "controls=gcd,lcm,extents,both_factors,atom_factor,rejects"
    )


if __name__ == "__main__":
    main()
