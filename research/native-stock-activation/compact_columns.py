"""Execute an affine column row on complete tapes with dirty controls."""

from spool import scratch, transfer


def get(x, pos, width):
    return (x >> pos) & ((1 << width) - 1)


class Columns:
    """All positions below are binary bit positions counted from the low end."""

    def __init__(self, window, offset, digit, front_u, front_t, back, suffix, swap):
        self.window, self.offset, self.digit = window, offset, digit
        self.u, self.t, self.back, self.suffix = front_u, front_t, back, suffix
        self.swap = swap

    def one(self, field, target, source=None):
        if source is None or target < source:
            field.rotate(target, 1, lambda addr: 1 if source is None else get(addr, source, 1))
        else:
            field.swap(source, target, 1, self.swap)
            field.rotate(source, 1, lambda addr: get(addr, target, 1))
            field.swap(source, target, 1, self.swap)

    def row(self, field, targets, sources=None):
        k, rho, g = self.window, self.offset, self.digit
        ys = tuple(targets)
        xs = tuple(sources) if sources is not None else ()
        if not ys or (xs and len(xs) != len(ys)):
            raise ValueError("The native row needs a full positive column count")
        if len(ys) == 1:
            self.one(field, ys[0], xs[0] if xs else None)
            return
        if ys != tuple(range(ys[0], ys[0] + k * len(ys), k)) or (
            xs and xs != tuple(range(xs[0], xs[0] + k * len(xs), k))
        ):
            raise ValueError("Compact native columns must be in contiguous complete slots")
        n = len(ys) - 1
        ctl = n * g
        y0, yw = ys[0] - rho, k * len(ys)
        touched = [(self.u, ctl), (self.t, ctl), (self.back, ctl), (y0, yw)]
        if xs:
            touched.append((xs[0] - rho, yw))
        placed = sorted(touched)
        if (
            placed[0][0] < self.suffix
            or placed[-1][0] + placed[-1][1] > field.ambient_bits
            or any(a + w > b for (a, w), (b, _) in zip(placed, placed[1:]))
            or not (placed[0][0] == self.back and {p for p, _ in placed[-2:]} == {self.u, self.t})
        ):
            raise ValueError("A compact control or its grouped suffix is unavailable")
        later = bool(xs) and xs[0] < ys[0]
        digit_mask = (1 << g) - 1

        def digit_at(a, base, i):
            return get(a, base + i * g, g)

        def controls(a, i):
            if later:
                return get(a, self.u + i * g, 1)
            return get(a, xs[i], 1) if xs else 1

        def packed(a, position, z=False):
            return sum(
                (get(a, position[i], 1) ^ (controls(a, i) if z else 0)) << (i * g) for i in range(n)
            )

        def move(top, amount):
            return [
                ("swap", top, self.back, ctl),
                ("rot", self.back, ctl, amount),
                ("swap", top, self.back, ctl),
            ]

        first = [
            (
                "rot",
                y0,
                yw,
                lambda a: sum(
                    2 * controls(a, i) * digit_at(a, self.t, i) << (ys[i] - y0) for i in range(n)
                ),
            )
        ]
        first += move(self.t, lambda a: packed(a, ys))
        first += [
            (
                "rot",
                y0,
                yw,
                lambda a: sum(
                    controls(a, i) * (1 - 2 * digit_at(a, self.t, i)) << (ys[i] - y0)
                    for i in range(n)
                ),
            )
        ]
        first += move(self.t, lambda a: -packed(a, ys, True))
        ops = first
        if later:
            ops = (
                first
                + move(self.u, lambda a: packed(a, xs))
                + first
                + move(self.u, lambda a: -packed(a, xs))
            )
        for op, a, b, c in ops:
            if op == "swap":
                field.swap(a, b, c, self.swap)
            else:
                field.rotate(a, b, c)

        def good(addr):
            for i in range(n):
                guard = get(addr, ys[i] + 1, k - 1)
                if (
                    digit_at(addr, self.t, i) == digit_mask
                    or (later and digit_at(addr, self.u, i) == digit_mask)
                    or not 2 * (1 << g) <= guard < (1 << (k - 1)) - 2 * (1 << g)
                ):
                    return False
            return True

        def repair_key(addr):
            for op, a, b, c in reversed(ops):
                if op == "swap":
                    v = get(addr, a, c) ^ get(addr, b, c)
                    addr ^= (v << a) | (v << b)
                else:
                    old = get(addr, a, b)
                    prefix = addr & ~((1 << (a + b)) - 1)
                    current = (old - c(prefix)) % (1 << b)
                    addr ^= (old ^ current) << a
            return addr ^ sum((get(addr, xs[i], 1) if xs else 1) << ys[i] for i in range(n))

        self.repair(field, good, repair_key)
        self.one(field, ys[-1], xs[-1] if xs else None)

    def repair(self, field, good, key):
        remaining = field.ambient_bits - self.suffix
        record = field.record << self.suffix
        width = max(1, (remaining + 7) // 8)
        out = field.blank()
        with scratch() as dirty, scratch() as zero, scratch() as one, scratch() as clean:
            field.stream.seek(0)
            errors = 0
            for i in range(1 << remaining):
                addr = i << self.suffix
                if good(addr):
                    transfer(field.stream, clean, record)
                else:
                    dest = key(addr)
                    if dest & ((1 << self.suffix) - 1):
                        raise ArithmeticError("The correction changed its grouped suffix")
                    dirty.write((dest >> self.suffix).to_bytes(width, "little"))
                    transfer(field.stream, dirty, record)
                    errors += 1
            for bit in range(remaining):
                dirty.seek(0)
                for tube in (zero, one):
                    tube.seek(0)
                for _ in range(errors):
                    label = dirty.read(width)
                    tube = one if label[bit // 8] & (1 << (bit % 8)) else zero
                    tube.write(label)
                    transfer(dirty, tube, record)
                dirty.seek(0)
                for tube in (zero, one):
                    total = tube.tell()
                    tube.seek(0)
                    transfer(tube, dirty, total)
            dirty.seek(0)
            clean.seek(0)
            for i in range(1 << remaining):
                if good(i << self.suffix):
                    transfer(clean, out.stream, record)
                else:
                    if int.from_bytes(dirty.read(width), "little") != i:
                        raise ArithmeticError("The corrected records do not fill their true holes")
                    transfer(dirty, out.stream, record)
        field.replace(out)
