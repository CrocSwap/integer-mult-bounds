"""Stream ordinary coefficient order, CRT coordinates, and Gaussian image slots."""
from contextlib import closing
from math import gcd, prod

from fine_ring import Tape, Trace, grouped_h, map_tape


def coordinates(sides):
    """Enumerate a rectangle with its first coordinate fastest."""
    digits = [0] * len(sides)
    for _ in range(prod(sides)):
        yield digits
        for j, radix in enumerate(sides):
            digits[j] += 1
            if digits[j] < radix:
                break
            digits[j] = 0


def register_groups(padded):
    widths = [s.bit_length() - 1 for s in padded]
    return tuple(sum(widths[i + 1:]) + j
                 for i, width in enumerate(widths) for j in range(width))


def involutions(permutation):
    left, right = [], []
    used = set()
    for i in range(len(permutation)):
        if i in used:
            continue
        cycle = []
        k = i
        while k not in used:
            used.add(k)
            cycle.append(k)
            k = permutation[k]
        if k != i:
            raise ValueError("address map is not a permutation")
        for j, x in enumerate(cycle):
            for offset, out in ((0, left), (1, right)):
                y = cycle[(offset - j) % len(cycle)]
                if x < y:
                    out.append((x, y))
    return left, right


class Banks:
    """Reuse the same finite inventory of erased stage roles."""

    def __init__(self, trace):
        self.trace = trace
        self.roles = [None] * 24

    def free_role(self):
        for j, bank in enumerate(self.roles):
            if bank is None or bank.released:
                return j
        raise ArithmeticError("fixed CRT and Gaussian stage roles exhausted")

    def keep(self, field):
        if field not in self.roles:
            self.roles[self.free_role()] = field
        return field

    def make(self, bits):
        j = self.free_role()
        field = self.roles[j]
        if field is None:
            field = self.roles[j] = Tape(bits, self.trace)
        else:
            if field.head or field.cells:
                raise ArithmeticError("nonempty released stage role")
            field.width = bits
            field.released = False
        return field

    def close(self):
        for field in self.roles:
            if field is not None and not field.released:
                field.release()


def import_field(values, count, width, owner):
    bank = owner.make(width)
    if isinstance(values, Tape):
        if values.released or values.trace is not owner.trace or len(values.cells) != count:
            raise ValueError("invalid borrowed CRT tape")
        head = values.head
        values.home()
        try:
            for _ in range(count):
                bank.append(values.read())
        finally:
            values.seek(head)
    else:
        if len(values) != count:
            raise ValueError("incorrect external record count")
        for value in values:
            bank.append(value)
    return bank


def export_field(bank):
    bank.home()
    return [bank.read() for _ in range(len(bank.cells))]


def phase_signs(length, pairs, trace=None):
    """Read each mate bit at its actual position as the binary counter changes."""
    if trace is None:
        trace = Trace()
    partners = {}
    for a, b in pairs:
        if not 0 <= a < length or not 0 <= b < length or a == b or a in partners or b in partners:
            raise ValueError("phase edges must be a matching")
        partners[a], partners[b] = b + 1, a + 1
    with closing(Banks(trace)) as owner:
        address = owner.make(2)
        mates = owner.make(max(2, length.bit_length() + 1))
        for j in range(length):
            address.append((0, 0))
            mates.append((partners.get(j, 0), 0))
        parity = 0
        for _ in range(1 << length):
            sign = -1 if parity else 1
            mates.home()
            for j in range(length):
                mate, _ = mates.read()
                if mate:
                    address.seek(mate - 1)
                    parity ^= address.read()[0]
                address.seek(j)
                bit = 1 - address.read()[0]
                address.replace(j, (bit, 0))
                if bit:
                    break
            yield sign


def permute_bank(bank, permutation, word_bits, max_batch, owner, backend):
    size = len(bank.cells)
    length = len(permutation)
    if size != 1 << length or sorted(permutation) != list(range(length)) or max_batch < 1:
        raise ValueError("incorrect dyadic address layout")
    for layer in involutions(permutation):
        for start in range(0, len(layer), max_batch):
            pairs = layer[start:start + max_batch]
            for target in (1, 0, 1):
                bits = tuple(pair[target] for pair in pairs)
                h = len(bits)
                width = bank.width
                bank = owner.keep(map_tape(bank, size, lambda _, z: (z[0] << h, z[1] << h), width + h))
                args = dict(backend=backend, fractional_bits=word_bits + h + 3)
                bank = owner.keep(grouped_h(bank, size, bits, **args))
                with closing(phase_signs(length, pairs, owner.trace)) as signs:
                    def signed(_, z):
                        return z if next(signs) == 1 else (-z[0], -z[1])
                    bank = owner.keep(map_tape(bank, size, signed))
                bank = owner.keep(grouped_h(bank, size, bits, **args))
                bank = owner.keep(map_tape(bank, size, lambda _, z: z, width))
    return bank


def permute(values, permutation, word_bits, max_batch, trace, backend=None):
    with closing(Banks(trace)) as owner:
        bank = import_field(values, 1 << len(permutation), word_bits + 2, owner)
        return export_field(permute_bank(bank, permutation, word_bits, max_batch, owner, backend))


def shear_bank(field, axes, padded, axis, inverse, owner):
    """Rotate one target interval per prefix. Copy its invalid tail unchanged."""
    modulus = axes[axis]
    prefix_source = prod(axes[:axis])
    mu = pow(prefix_source, -1, modulus)
    width = max(padded).bit_length() + 1
    # Read the prefix in the same order as divmod on its physical rank.
    page = owner.make(width)
    weight = prefix_source
    for j in reversed(range(axis)):
        weight //= axes[j]
        page.append((axes[j],padded[j]))
        page.append(((weight * mu) % modulus,0))

    out = owner.make(field.width)
    suffix = prod(padded[axis + 1:])
    row = padded[axis] * suffix
    field.home()
    for prefix in range(prod(padded[:axis])):
        rank = prefix
        good = True
        shift = 0
        page.home()
        for _ in range(axis):
            s, t = page.read()
            weight, _ = page.read()
            rank, x = divmod(rank, t)
            good = good and x < s
            shift = (shift + x * weight) % modulus
        if not good:
            shift = 0
        cut = shift if inverse else modulus - shift
        base = row * prefix
        for lo, hi in ((cut, modulus), (0, cut), (modulus, padded[axis])):
            if lo == hi:
                continue
            field.seek(base + lo * suffix)
            for _ in range((hi - lo) * suffix):
                out.append(field.read())
    field.release()
    page.release()
    return out


def shear(values, axes, padded, i, inverse, *, word_bits=None, trace=None):
    if trace is None:
        trace = Trace()
    if word_bits is None:
        word_bits = max((abs(a).bit_length() for z in values for a in z), default=1) + 1
    with closing(Banks(trace)) as owner:
        field = import_field(values, prod(padded), word_bits + 1, owner)
        return export_field(shear_bank(field, axes, padded, i, inverse, owner))


def valid_slot(x, source, target, original):
    if not original:
        return x < source
    j = (2 * source * x + target) // (2 * target)
    return j < source and (2 * target * j + source) // (2 * source) == x


def masks(sources, targets, original, trace):
    """Carry a count of invalid digits. Only changed digits need new tests."""
    with closing(Banks(trace)) as owner:
        width = max(targets).bit_length() + 1
        parameters = owner.make(width)
        digits = owner.make(width)
        for s, t in zip(sources, targets, strict=True):
            parameters.append((s,t))
            digits.append((0,1))
        bad = 0
        for _ in range(prod(targets)):
            valid = bad == 0
            parameters.home()
            digits.home()
            for j in range(len(targets)):
                s, t = parameters.read()
                x, before = digits.read()
                x = (x + 1) % t
                after = int(valid_slot(x, s, t, original))
                digits.replace(j, (x, after))
                bad += before - after
                if x:
                    break
            yield valid


def reshape_bank(field, sources, targets, extract, original, owner):
    out = owner.make(field.width)
    field.home()
    with closing(masks(sources, targets, original, owner.trace)) as mask:
        for active in mask:
            if extract:
                z = field.read()
                if active:
                    out.append(z)
                elif not original and z != (0, 0):
                    raise ValueError("nonzero CRT padding")
            elif active:
                out.append(field.read())
            else:
                out.append((0, 0))
    if field.head != len(field.cells):
        raise ValueError("incorrect number of occupied slots")
    field.release()
    return out


def validate(sources, targets, coprime):
    if not sources or len(sources) != len(targets):
        raise ValueError("invalid rectangular extents")
    past = 1
    for s, t in zip(sources, targets, strict=True):
        if not 1 <= s < t or t & (t - 1) or (coprime and (s < 3 or s % 2 == 0 or gcd(past, s) != 1)):
            raise ValueError("invalid source or dyadic target")
        past *= s


def original_reshape(values, sources, targets, word_bits, trace, *, extract):
    validate(sources, targets, False)
    with closing(Banks(trace)) as owner:
        count = prod(targets if extract else sources)
        field = import_field(values, count, word_bits + 1, owner)
        return export_field(reshape_bank(field, sources, targets, extract, True, owner))


def padded(values, sides, targets, extract, word_bits, trace):
    validate(sides, targets, False)
    if isinstance(values, Tape):
        if trace is None:
            trace = values.trace
        if word_bits is None:
            word_bits = values.width
    if trace is None:
        trace = Trace()
    if word_bits is None:
        word_bits = max((abs(a).bit_length() for z in values for a in z), default=1) + 1
    with closing(Banks(trace)) as owner:
        field = import_field(values, prod(targets if extract else sides), word_bits + 1, owner)
        return export_field(reshape_bank(field, sides, targets, extract, False, owner))


def inject(compact, sides, padded_shape, *, word_bits=None, trace=None):
    return padded(compact, sides, padded_shape, False, word_bits, trace)


def restrict(field, sides, padded_shape, *, word_bits=None, trace=None):
    return padded(field, sides, padded_shape, True, word_bits, trace)


def route(values, physical_sources, physical_targets, inverse, word_bits, max_batch, trace, backend=None):
    """Use physical coordinate i = k / product(s[j] for j>i), modulo s[i]."""
    validate(physical_sources, physical_targets, True)
    if word_bits < 1 or max_batch < 1:
        raise ValueError("invalid record width or batch size")
    axes = tuple(reversed(physical_sources))
    targets = tuple(reversed(physical_targets))
    wiring = register_groups(targets)
    with closing(Banks(trace)) as owner:
        data = import_field(values, prod(axes), word_bits + 2, owner)
        if inverse:
            data = reshape_bank(data, physical_sources, physical_targets, False, False, owner)
            for i in range(1,len(axes)):
                data = shear_bank(data, axes, targets, i, True, owner)
            backward = [0] * len(wiring)
            for j,k in enumerate(wiring):
                backward[k] = j
            data = permute_bank(data, backward, word_bits, max_batch, owner, backend)
            data = reshape_bank(data, axes, targets, True, False, owner)
        else:
            data = reshape_bank(data, axes, targets, False, False, owner)
            data = permute_bank(data, wiring, word_bits, max_batch, owner, backend)
            for i in reversed(range(1,len(axes))):
                data = shear_bank(data, axes, targets, i, False, owner)
            data = reshape_bank(data, physical_sources, physical_targets, True, False, owner)
        return export_field(data)
