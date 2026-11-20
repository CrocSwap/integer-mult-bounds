"""Lower a full-grid normalized H layer to the exact selected C operation."""
from dataclasses import dataclass
from fine_ring import Tape, map_tape, tz


def phase(z, k):
    real, imag = z
    return ((real, imag), (-imag, real), (-real, -imag), (imag, -real))[k%4]


@dataclass(frozen=True)
class CRequest:
    """Exact output uses 2^rank C^tensor on the input integer numerators."""
    address_bits: int
    selected: tuple
    input_fraction: int
    output_width: int

    @property
    def rank(self):
        return len(self.selected)


def single_c_numerator(field, axis):
    """Execute 2C on one actual address bit; preserve all spectator labels."""
    width, trace = field.width, field.trace
    count = len(field.cells)
    halves = [Tape(width, trace) for _ in range(2)]
    field.home()
    for i in range(count):
        halves[(i >> axis)&1].append(field.read())
    field.release()
    for tape in halves:
        tape.home()
    products = [Tape(width, trace) for _ in range(2)]
    for _ in range(count//2):
        a, b = halves[0].read()
        c, d = halves[1].read()
        products[0].append((a+c-b+d, b+d+a-c))
        products[1].append((a+c+b-d, b+d-a+c))
    for tape in halves:
        tape.release()
    for tape in products:
        tape.home()
    returned = Tape(width, trace)
    for i in range(count):
        returned.append(products[(i >> axis)&1].read())
    for tape in products:
        tape.release()
    return returned


def elementary_c(field, request):
    """Finite native operation for test and base cases, with an explicit cap."""
    if request.rank > 12:
        raise ValueError("finite C interpreter admits at most twelve selected coordinates")
    for axis in request.selected:
        field = single_c_numerator(field, axis)
    return field


class SelectedH:
    """The supplied child computes selected exact C on a full global tensor."""

    def __init__(self, native_c):
        self.native_c = native_c

    def __call__(self, field, volume, bits, fraction):
        h = len(bits)
        if fraction is None or fraction < 1 or h < 1:
            raise ValueError("selected C requires a positive binary grid and rank")
        ambient = volume.bit_length()-1
        if volume != 1<<ambient or len(field.cells) != volume or len(set(bits)) != h or min(bits)<0 or max(bits)>=ambient:
            raise ValueError("incomplete selected C rectangle")
        width = field.width
        # This buys both the C numerator and its temporary component growth.
        request = CRequest(ambient, tuple(bits), fraction, width+2*h+3)
        mask = sum(1 << bit for bit in bits)
        def local_phase(i, value):
            return phase(value, (i & mask).bit_count())
        field = map_tape(field, volume, local_phase, request.output_width)
        field = self.native_c(field, request)
        if len(field.cells) != volume or field.width != request.output_width:
            raise ValueError("incomplete C numerator return")
        pairs, odd = divmod(h, 2)
        divisor = 1 << (h+pairs+odd)
        def finish(i, value):
            a, b = phase(local_phase(i, value), -pairs)
            if odd:
                a, b = a+b, b-a
            return tz(a, divisor), tz(b, divisor)
        return map_tape(field, volume, finish, width)
