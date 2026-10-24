#!/usr/bin/env python3
"""Parent spectator blank-return is not paid by the 972-bit R437 child.

The identities are the ones stated in research/r437-carrier-integration
PHYSICAL.md, NUMERICAL.md section 5, and physical.py's weighted_child.
This checker does not import that package or execute its packet engine.
"""

from __future__ import annotations

W = 28416
OTHER = 28425
STATED_LCM = 269241600
UNUSED_ROWS = 9475
B = 2
EXECUTED_GAP = 3
OMITTED_COORDINATES = 124
S = 2
ATOM_FACTOR = 3**4
EXECUTED_BITS = 972


def gcd(left: int, right: int) -> int:
    while right:
        left, right = right, left % right
    return left


def lcm(left: int, right: int) -> int:
    return left // gcd(left, right) * right


def executed_packet() -> int:
    """B * G0 * S * 3^4, the extent formula with the executed gap G0=3."""
    return B * EXECUTED_GAP * S * ATOM_FACTOR


def parent_payload() -> int:
    """U * B * (G0 * 3^124) * S * 3^4."""
    gap = EXECUTED_GAP * 3**OMITTED_COORDINATES
    return UNUSED_ROWS * B * gap * S * ATOM_FACTOR


def parent_over_executed() -> int:
    return UNUSED_ROWS * 3**OMITTED_COORDINATES


def certify() -> dict:
    divisor = gcd(W, OTHER)
    if divisor != 3:
        raise AssertionError(divisor)
    combined = lcm(W, OTHER)
    if combined != STATED_LCM:
        raise AssertionError(combined)
    if W * UNUSED_ROWS != STATED_LCM or STATED_LCM % W != 0:
        raise AssertionError((STATED_LCM, W, UNUSED_ROWS))
    if STATED_LCM // W != UNUSED_ROWS:
        raise AssertionError(STATED_LCM // W)
    # 28416/3 * 28425 is the same lcm, multiplied before dividing.
    if (W // divisor) * OTHER != STATED_LCM:
        raise AssertionError((W // divisor) * OTHER)

    child = executed_packet()
    if child != EXECUTED_BITS:
        raise AssertionError(child)
    parent = parent_payload()
    gap = EXECUTED_GAP * 3**OMITTED_COORDINATES
    expanded = B * gap * S * ATOM_FACTOR
    # 2 * 3^125 * 2 * 3^4 = 4 * 3^129 = 12 * 3^128.
    if gap != 3**125 or expanded != 12 * 3**128:
        raise AssertionError((gap, expanded))
    if parent != UNUSED_ROWS * 12 * 3**128:
        raise AssertionError(parent)
    ratio = parent_over_executed()
    if parent != child * ratio:
        raise AssertionError((parent, child, ratio))
    if ratio != UNUSED_ROWS * 3**OMITTED_COORDINATES:
        raise AssertionError(ratio)
    if not parent > child:
        raise AssertionError((parent, child))
    # Dropping either factor is a different, strictly smaller comparison.
    rows_only = UNUSED_ROWS
    coordinates_only = 3**OMITTED_COORDINATES
    if rows_only * coordinates_only != ratio:
        raise AssertionError((rows_only, coordinates_only, ratio))
    if rows_only >= ratio or coordinates_only >= ratio:
        raise AssertionError("a single factor must not be the full ratio")
    # One visit per payload symbol cannot be paid by the executed packet.
    if child >= parent:
        raise AssertionError("executed packet pays the parent")
    return {
        "unused_rows": UNUSED_ROWS,
        "omitted_coordinates": OMITTED_COORDINATES,
        "executed_bits": child,
        "parent_over_executed": ratio,
        "parent_over_executed_digits": len(str(ratio)),
        "lcm": combined,
    }


def main() -> None:
    row = certify()
    print(
        "PASS_R437_PARENT_SPECTATOR_BLANK "
        f"rows={row['unused_rows']} "
        f"omitted_coordinates={row['omitted_coordinates']} "
        f"executed_bits={row['executed_bits']} "
        f"parent_over_executed={row['unused_rows']}*3^{row['omitted_coordinates']} "
        f"parent_over_executed_digits={row['parent_over_executed_digits']} "
        f"lcm={row['lcm']} "
        "blank_return_discharged=false no_new_kappa"
    )


if __name__ == "__main__":
    main()
