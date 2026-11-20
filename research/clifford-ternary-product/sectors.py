"""Decode independently chosen Clifford charts in the high binary address fibres."""

from dataclasses import dataclass

from contraction import product_passes
from delivery import deliver
from operand import cantor_flags, recognise_sparse
from templates import plus, trim


@dataclass(frozen=True)
class Sectors:
    low_sites: int
    high_sites: int
    charts: tuple


def control_sites(m):
    # This cap keeps high-address selection polynomial in m on fixed tapes.
    s = max(1, m.bit_length())
    return min(m // 2, (s * s).bit_length() - 1)


def recognise_sectors(raw, m, h=None):
    h = control_sites(m) if h is None else h
    if not 0 <= h <= m // 2:
        raise ValueError("At most half of the sites may select sectors")
    k = m - h
    width = 3 ** k
    if len(raw) > 3 ** m:
        return None
    charts = []
    for prefix, valid in enumerate(cantor_flags(h)):
        block = raw[prefix * width:(prefix + 1) * width]
        if valid:
            chart = recognise_sparse(block, k)
            if chart is None:
                return None
            charts.append(chart)
        elif any(block):
            return None
    return Sectors(k, h, tuple(charts))


def high_pairs(address, h):
    """Enumerate both orientations at each mixed high trit."""
    common = free = 0
    for bit in range(h):
        address, digit = divmod(address, 3)
        if digit == 2:
            common |= 1 << bit
        elif digit == 1:
            free |= 1 << bit
    sub = free
    while True:
        yield common | sub, common | (free ^ sub)
        if not sub:
            break
        sub = (sub - 1) & free


def sector_product(a, b, *, stats=None):
    if (a.low_sites, a.high_sites) != (b.low_sites, b.high_sites):
        raise ValueError("The two sector grids must agree")
    block_width = 3 ** a.low_sites
    output = bytearray()
    carry = b"\0"
    pairs = 0
    emitted = moves = 0
    for address in range(3 ** a.high_sites):
        block = carry
        for left, right in high_pairs(address, a.high_sites):
            detail = {} if stats is not None else None
            term = deliver(product_passes(a.charts[left], b.charts[right]), stats=detail)
            block = plus(block, term)
            pairs += 1
            if detail is not None:
                emitted += detail["emits"]
                moves += detail["moves"]
        output.extend(block[:block_width].ljust(block_width, b"\0"))
        carry = trim(block[block_width:])
    output.extend(carry)
    if stats is not None:
        stats.update(pairs=pairs, charts_per_operand=len(a.charts), emits=emitted, moves=moves)
    return trim(output)
