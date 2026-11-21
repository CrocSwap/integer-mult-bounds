"""Select the thin square geometry and expose the two native requests."""

from dataclasses import dataclass
from math import gcd, isqrt


def ceil_log2(value):
    if value < 1:
        raise ValueError("The logarithm needs a positive integer")
    return (value - 1).bit_length()


@dataclass(frozen=True)
class Shape:
    public: int
    extent_bits: int
    count: int

    def axes(self):
        short, larger = divmod(self.extent_bits, self.count)
        for axis in range(self.count):
            yield short + (axis < larger)

    def packs(self):
        """Emit consecutive selections with the same physical axis width."""
        s = ceil_log2(self.public + 2)
        limit = max(1, self.count // (1024 * s))
        short, larger = divmod(self.extent_bits, self.count)
        for first, end, width in ((0, larger, short + 1), (larger, self.count, short)):
            for start in range(first, end, limit):
                yield start, min(start + limit, end), width

    def precision(self):
        maximum = (self.extent_bits + self.count - 1) // self.count
        intervals = 4096 * (self.extent_bits + 6 * self.count)
        stages = 20000 * (self.count + 1) * (maximum + 2) ** 6
        return 4 * self.public + 8 * intervals + 4 * (stages * (self.count + 1)).bit_length() + 64

    def crt_control(self):
        s = ceil_log2(self.public + 2)
        maximum = (self.extent_bits + self.count - 1) // self.count
        guard = 64 * (maximum + s)
        capacity = self.extent_bits // (100 * guard)
        return guard, capacity, capacity * guard


def parameters(input_bits):
    if input_bits < 2:
        return None
    b = ceil_log2(input_bits)
    public = 6 * b
    s = ceil_log2(public + 2)
    extent_bits = ceil_log2((4 * input_bits + b - 1) // b)
    capacity = extent_bits // (64 * s * s)
    if not capacity:
        return None
    return Shape(public, extent_bits, 1 << (capacity.bit_length() - 1))


def square_axes(widths):
    """Use the first admissible base in each of the two predecessor bands."""
    widths = tuple(widths)
    modulus = 2
    for index, width in enumerate(widths):
        denominator = (16 if index % 2 else 4) * len(widths)
        side = 1 << width
        # denominator times x^2 is at least (denominator - 1) times side.
        low_square = ((denominator - 1) * side + denominator - 1) // denominator
        high_square = ((2 * denominator - 1) * side) // (2 * denominator)
        lower = max(3, 1 + isqrt(low_square - 1))
        for base in range(lower | 1, isqrt(high_square) + 1, 2):
            if gcd(base, modulus) == 1:
                yield base * base
                modulus *= base
                break
        else:
            raise ValueError("The square interval has no admissible base")


def first_mixing_layer(plan):
    """Follow true wire zero until two output wires carry its contribution."""
    position = 0
    for root_pass in (0, 1):
        for layer, gates in enumerate(plan):
            for wires, gate in gates:
                if position not in wires:
                    continue
                column = wires.index(position)
                outputs = [wire for i, wire in enumerate(wires) if gate[i][column] != 0]
                if len(outputs) == 2:
                    return root_pass, layer
                if len(outputs) != 1:
                    raise ValueError("The represented column vanished")
                position = outputs[0]
                break
    raise ValueError("The two-pass Fourier column has only one wire")


def mixing_packs(shape, axis_plans):
    """Group physical indices by width and first mixing layer, then split."""
    s = ceil_log2(shape.public + 2)
    limit = max(1, shape.count // (1024 * s))
    groups = {}
    for axis, (width, plan) in enumerate(zip(shape.axes(), axis_plans, strict=True)):
        groups.setdefault((width, first_mixing_layer(plan)), []).append(axis)
    for key, group in sorted(groups.items()):
        for start in range(0, len(group), limit):
            yield key, tuple(group[start : start + limit])


def periodic_source(rank, source_rank, current_round):
    """Generate the ordered source of a periodic forest round."""
    used = 4 * (rank // 4)
    if not 1 <= source_rank <= used // 4:
        raise ValueError("The forest port does not fit this periodic rank")
    quotient = (used + source_rank - 1) // source_rank
    period = 1 << ceil_log2(quotient)
    five = (period * source_rank - used) // 4
    if not 0 <= current_round < period:
        raise ValueError("The round is outside its period")
    for t in range(source_rank):
        ticket = current_round + period * t
        yield ticket // 5 if ticket < 5 * five else ticket - 4 * five


def source_placement(rank, selected):
    """Put the ordered selected slots first and return physical swap sites."""
    at = list(range(rank))
    where = list(range(rank))
    swaps = []
    for dest, original in enumerate(selected):
        if original < 0 or original >= rank:
            raise ValueError("The selected slot is outside the field")
        pos = where[original]
        if pos < dest:
            raise ValueError("A source claims the same physical slot twice")
        if pos == dest:
            continue
        displaced = at[dest]
        swaps.append((dest, pos))
        at[dest], at[pos] = original, displaced
        where[original], where[displaced] = dest, pos
    return swaps


def in_physical_source(field, selected, rank, repetitions, window, swap, use):
    """Execute one source on a genuine contiguous prefix, then restore it.

    'swap' is the complete ordinary service. Bit offsets count from the
    start of the active slot block. 'use' receives the gathered field and
    the number of complete selected columns. It returns its updated field.
    """
    selected = tuple(selected)
    route = source_placement(rank, selected)
    width = repetitions * window
    for left, right in route:
        field = swap(field, left * width, right * width, width)
    field = use(field, len(selected) * repetitions)
    for left, right in reversed(route):
        field = swap(field, left * width, right * width, width)
    return field


def exponent_receipt(s, binary_rank_bits, complex_rank_bits, ordinary_width_bits):
    """Prove lower powers without allocating an integer with 2^s bits.

    The public precision p has s = ceil(log2(p+2)). The result bounds all
    such p from below. ordinary_width_bits is the separate ordinary result.
    """
    if min(binary_rank_bits, complex_rank_bits, ordinary_width_bits) < 1 or s < 512:
        raise ValueError("Use positive ranks and s >= 512")
    log_s = ceil_log2(s)
    crt = s - 12
    pack = s - 24 - 3 * log_s
    # The opposite exterior holds every reservation. All selected bits take part.
    mixing_pack = s - 100 - 16 * log_s
    return {
        "s": s,
        "log2_max_dyadic_width": 7 + 2 * log_s,
        "log2_pack_width_lower": pack,
        "log2_genuine_mixing_pack_lower": mixing_pack,
        "log2_active_pack_width_lower": mixing_pack,
        "log2_crt_binary_field_lower": crt,
        "log2_crt_ternary_width_lower": crt - 1,
        "full_ordinary_width": crt - 1 >= ordinary_width_bits,
        "full_ordinary_width_inside_complex": mixing_pack - complex_rank_bits - 2
        >= ordinary_width_bits,
        "native_complex_dimension": mixing_pack > complex_rank_bits,
        "log2_private_setup_log2_clock_upper": 20 + 2 * ceil_log2(s + 1),
        "private_clock_below_one_eighth_extent": 20 + 2 * ceil_log2(s + 1) < s - 9,
    }
