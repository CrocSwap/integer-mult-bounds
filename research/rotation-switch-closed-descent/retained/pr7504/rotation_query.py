"""Direct canonical Beneš switch queries for padded modular rotations.

Produced by Nick Petalas. Apache-2.0. See PROOF.md for the exact source rule.
"""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def endpoint_bit(modulus: int, offset: int, address: int, last: bool) -> int:
    """Internal endpoint formula; the public query validates the domain."""
    if not last:
        return int((modulus & offset & 1) and address // 2 == modulus // 2)
    if modulus % 2 == 0:
        return int(offset % 2 == 1 and address < modulus)
    if offset % 2 == 0:
        return int(address < offset)
    return int(offset - 1 <= address <= modulus)


def child_parameters(modulus: int, offset: int, branch: int) -> tuple[int, int]:
    """Internal recurrence, including an empty identity child."""
    child_modulus = modulus // 2 + int(modulus % 2 == 1 and branch == offset % 2)
    raw_offset = offset // 2 + branch * (offset % 2)
    child_offset = 0 if raw_offset == child_modulus else raw_offset
    return child_modulus, child_offset


def switch_bit(h: int, modulus: int, offset: int, layer: int, address: int) -> int:
    """Return a bit of precisely the source's deterministic network.

    The conceptual domain is every h >= 1. The executable caps h at 4096
    to bound interpreter allocation and work. No permutation or ROM is built.
    """
    require(all(type(value) is int for value in (h, modulus, offset, layer, address)),
            "integer parameters")
    require(1 <= h <= 4096, "1 <= h <= 4096")
    require(1 <= modulus <= 1 << h, "modulus in occupied address domain")
    require(0 <= offset < modulus, "canonical offset")
    require(0 <= layer < 2 * h - 1, "network layer")
    require(0 <= address < 1 << h, "network address")
    for _ in range(h):
        if offset == 0:
            return 0
        if h == 1:
            return offset
        if layer == 0 or layer == 2 * h - 2:
            return endpoint_bit(modulus, offset, address, layer != 0)
        modulus, offset = child_parameters(modulus, offset, address & 1)
        require(0 <= offset < modulus, "nonidentity child has positive modulus")
        h -= 1
        layer -= 1
        address //= 2
    raise ArithmeticError("unreachable after one descent per address bit")
