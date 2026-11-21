"""Use four two-trit product-module atoms to place live records for a CRT switch."""

from collections import Counter
from ctypes import CDLL, POINTER, c_size_t, c_ubyte, c_int
from io import BytesIO
from itertools import product


SIDE = 81
BODY = SIDE * SIDE
LOWS = 48


def lower_atom(left, right, coefficient):
    for component in (0, 1):
        yield 0, 2 * left + component, 2 * right + component, coefficient % 3


def atom_swap(left, right):
    for component in (0, 1):
        yield 1, 2 * left + component, 2 * right + component, 0


def weighted_pair(left, right, weight):
    reciprocal = pow(weight, -1, 3)
    for factor in (reciprocal, -weight):
        yield from lower_atom(left, right, factor)
        yield from atom_swap(left, right)
    yield from lower_atom(left, right, reciprocal)
    for trit in (2 * left, 2 * left + 1):
        yield 2, trit, trit, 0


def leaf_program(u, v):
    from ternary_leaf import lower_coefficient, lower_slot, ordered_chart, pivot_pairs, select_pivot

    order, b, c = ordered_chart(u, v, select_pivot(u, v), 3)
    pairs = pivot_pairs(2, order[0])
    for left, right in pairs:
        yield from weighted_pair(left, right, 1)
    h_inverse = pow(c[0], -1, 3)
    for undo in (False, True):
        if undo:
            yield from weighted_pair(0, 3, c[0])
        for slot in reversed(range(4)) if undo else range(4):
            dst, src, i = lower_slot(2, slot)
            factor = lower_coefficient(slot, i, b, c, 1, 1, h_inverse, 3)
            yield from lower_atom(src, dst, -factor if undo else factor)
    for left, right in reversed(pairs):
        yield from weighted_pair(left, right, 1)


def code(operations):
    return bytes(x for operation in operations for x in operation)


class SplitTranspose:
    def __init__(self, library):
        from streaming_routes import regular
        from ternary_frames import covered_factors
        from ternary_leaf import select_pivot

        self.kernel = CDLL(str(library)).run_packet
        self.kernel.argtypes = [POINTER(c_ubyte), c_size_t, c_size_t, POINTER(c_ubyte), c_size_t]
        self.kernel.restype = c_int
        self.programs = []
        for row in product(range(3), repeat=4):
            if regular(row, 2):
                u, v = covered_factors(((1, 0), (1, 0)), (row[:2], row[2:]), 1)
                self.programs.append((code(leaf_program(u, v)), select_pivot(u, v)))
        if len(self.programs) != LOWS:
            raise ArithmeticError("Wrong size of GL2(F3)")
        self.stats = Counter()

    def run(self, data, suffix, program):
        if len(data) != suffix * BODY or len(program) % 4:
            raise ValueError("Wrong packet or instruction length")
        source = (c_ubyte * len(data)).from_buffer(data)
        ops = (c_ubyte * len(program)).from_buffer_copy(program)
        if self.kernel(source, len(data), suffix, ops, len(program) // 4):
            raise RuntimeError("The physical tape program failed")
        self.stats["trit_passes"] += len(program) // 4
        self.stats["payload_bytes_per_pass_summed"] += len(data) * (len(program) // 4)

    def right(self, rows, suffix):
        from streaming_routes import right_route

        out = BytesIO()
        right_route(BytesIO(rows), out, 2, 1, 1, BODY * suffix, (("swap", 0, 1),))
        self.stats["right_routes"] += 1
        return bytearray(out.getvalue())

    def reversed(self, rows, suffix):
        width = BODY * suffix
        for second in (False, True):
            if second:
                rows = self.right(rows, suffix)
            for low, (program, pivot) in enumerate(self.programs):
                packet = memoryview(rows)[width * low : width * (low + 1)]
                self.run(packet, suffix, program)
                self.stats["nonleading_leaves" if pivot else "leading_leaves"] += 1
            if second:
                rows = self.right(rows, suffix)
        return rows

    def apply(self, data, suffix):
        if suffix <= 0 or len(data) != LOWS * BODY * suffix:
            raise ValueError("The complete low stock and body are required")
        rows = bytearray(data)
        for k in range(3):
            program = []
            for j in range(2):
                program.extend(lower_atom(j, 2 + j, 1 if k == 1 else -1))
            if k == 2:
                program.extend((2, j, j, 0) for j in range(4, 8))
            for low in range(LOWS):
                width = BODY * suffix
                packet = memoryview(rows)[low * width : (low + 1) * width]
                self.run(packet, suffix, code(program))
            if k < 2:
                rows = self.reversed(rows, suffix)
        self.stats["ordinary_swaps"] += 1
        return rows


def switched_block(block, width, program, suffix, reverse):
    """Apply each Beneš row to sequential records in one exposed axis."""
    length = 1 << width
    steps = reversed(program) if reverse else program
    for bit, controls in steps:
        half = 1 << bit
        source, target = BytesIO(block), BytesIO()
        for start in range(0, length, 2 * half):
            first = BytesIO(source.read(half * suffix))
            later = BytesIO()
            for j in range(half):
                a, b = first.read(suffix), source.read(suffix)
                if controls[start + j]:
                    a, b = b, a
                target.write(a)
                later.write(b)
            target.write(later.getvalue())
        target.write(source.read())
        block = target.getvalue()
    return block


def physical_crt(machine, field, transpose, reverse):
    """Move the actual fixed-point limbs to a row before using its switches."""
    nx, ny = machine.widths
    if max(nx, ny) > SIDE or len(field) != nx * ny:
        raise ValueError("The two-axis rectangle does not fit into the finite tape example")
    scalar = isinstance(field[0], int)
    channels = 1 if scalar else 2
    bits = machine.grid.bits + 4
    part = (bits * channels + LOWS - 1) // LOWS
    suffix = (part + 7) // 8
    mask = (1 << bits) - 1
    part_mask = (1 << part) - 1
    limit = 1 << (bits - 1)
    packed = []
    for item in field:
        components = (item,) if scalar else item
        if len(components) != channels or any(not -limit <= u < limit for u in components):
            raise OverflowError("The CRT channel exceeds its fixed signed format")
        packed.append(sum((u & mask) << (i * bits) for i, u in enumerate(components)))
    pad = bytes(suffix)
    src = BytesIO()
    for low in range(LOWS):
        shift = low * part
        for y in range(ny):
            for value in packed[y * nx : (y + 1) * nx]:
                src.write(((value >> shift) & part_mask).to_bytes(suffix, "little"))
            src.write(pad * (SIDE - nx))
        src.write(pad * (SIDE * (SIDE - ny)))
    major = BytesIO(transpose.apply(src.getvalue(), suffix))
    routed = BytesIO()
    for _ in range(LOWS):
        for x in range(nx):
            [(_, width, program)] = machine.router.offset_programs((x, 0), 1)
            routed.write(switched_block(major.read(SIDE * suffix), width, program, suffix, reverse))
        routed.write(major.read((SIDE - nx) * SIDE * suffix))
    if major.read(1):
        raise ArithmeticError("The CRT switch left unread rows")
    restored = BytesIO(transpose.apply(routed.getvalue(), suffix))
    packed = [0] * (nx * ny)
    for low in range(LOWS):
        for y in range(ny):
            for x in range(nx):
                chunk = int.from_bytes(restored.read(suffix), "little")
                if chunk > part_mask:
                    raise ArithmeticError("A returned CRT channel violates its extent")
                packed[y * nx + x] += chunk << (low * part)
            if any(restored.read((SIDE - nx) * suffix)):
                raise ArithmeticError("The CRT row has a dirty retired column")
        if any(restored.read((SIDE - ny) * SIDE * suffix)):
            raise ArithmeticError("The CRT plane has a dirty retired row")
    if restored.read(1) or any(u >> (bits * channels) for u in packed):
        raise ArithmeticError("Retirement found extra data")
    output = []
    for value in packed:
        components = []
        for _ in range(channels):
            u = value & mask
            components.append(u - (1 << bits) if u >= limit else u)
            value >>= bits
        output.append(components[0] if scalar else tuple(components))
    transpose.stats["inverse_crt" if reverse else "forward_crt"] += 1
    return output
