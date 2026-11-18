"""Query one canonical switch with a closed descent formula.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Nick Petalas supplied the child recurrence and endpoint formulas.
"""

MAX_HEIGHT = 65536


def require(condition, message):
    if not condition:
        raise ValueError(message)


def interval_pair(modulus, offset, depth, address):
    """Return the two unreduced interval lengths after the specified descent."""
    mask = (1 << depth) - 1
    tail = address & mask
    return ((offset + tail) >> depth,
            (modulus - offset + mask - tail) >> depth)


def endpoint(left, right, address, height, last):
    """Evaluate the endpoint, including every identity child."""
    if left == 0 or right == 0:
        return 0
    if height == 1:
        return 1
    modulus = left + right
    if not last:
        return int((modulus & left & 1) and address // 2 == modulus // 2)
    if modulus % 2 == 0:
        return int(left % 2 == 1 and address < modulus)
    if left % 2 == 0:
        return int(address < left)
    return int(left - 1 <= address <= modulus)


def switch_bit(height, modulus, offset, layer, address):
    """Return the source's current-wire table bit with O(height) bit work."""
    require(all(type(v) is int for v in (height, modulus, offset, layer, address)),
            "integer parameters")
    require(1 <= height <= MAX_HEIGHT, "height outside the executable limit")
    require(1 <= modulus <= 1 << height, "modulus outside the address domain")
    require(0 <= offset < modulus, "offset outside the canonical interval")
    require(0 <= layer < 2 * height - 1, "layer outside the network")
    require(0 <= address < 1 << height, "address outside the network")
    depth = min(layer, 2 * height - 2 - layer)
    left, right = interval_pair(modulus, offset, depth, address)
    return endpoint(left, right, address >> depth, height - depth, layer != depth)
