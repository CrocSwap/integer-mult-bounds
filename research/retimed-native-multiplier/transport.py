"""Compile a finite time schedule for an unpowered native word with descending loans."""

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction as F
from math import isqrt


def ceil(q):
    return -(-q.numerator // q.denominator)


class Measure:
    """Enclose integrals of V*x**(-1-t) at rational interval endpoints."""

    def __init__(self, t, volume, precision):
        if t <= 0 or t > 1 or t.denominator.bit_count() != 1:
            raise ValueError(
                "The density needs a dyadic exponent between zero and one."
            )
        self.t, self.volume, self.grid = t, volume, 1 << precision

    def inverse_power(self, x):
        t, g = self.t, self.grid
        q = g / F(x)
        a, b = q.numerator // q.denominator, ceil(q)
        lo = hi = g
        for j in range(t.denominator.bit_length()):
            if (t.numerator >> (t.denominator.bit_length() - 1 - j)) & 1:
                lo, hi = lo * a // g, -(-hi * b // g)
            if j + 1 != t.denominator.bit_length():
                a = isqrt(a * g)
                b = isqrt(b * g - 1) + 1
        return lo, hi

    def mass(self, left, right):
        if right <= left:
            return F(0), F(0)
        a, b = self.inverse_power(left)
        c, d = self.inverse_power(right)
        scale = F(self.volume, self.grid) / self.t
        return max(0, a - d) * scale, (b - c) * scale


@dataclass(frozen=True)
class Link:
    start: int
    count: int
    band: int
    port: int
    other: int


@dataclass(frozen=True)
class Source:
    start: int
    count: int
    base: int
    period: int


def axes(length, size, period, row):
    five = (period * size - length) // 4
    for ticket in range(row, period * size, period):
        yield ticket // 5 if ticket < 5 * five else ticket - 4 * five


class Plan:
    def __init__(
        self,
        n,
        targets,
        paid,
        cells,
        t,
        lower,
        upper,
        volume,
        ticks,
        rounds,
        *,
        delay_base,
        scale_step=F(6, 5),
        padding=4096,
        width=None,
    ):
        if not 0 < lower < upper or lower % 2 or upper % 2 or lower <= 8:
            raise ValueError(
                "The scale endpoints must be even and the column count positive."
            )
        if n % 4 or n < 4 * max(targets) * (upper - 8) or delay_base < len(paid):
            raise ValueError("The word or periodic source does not fit the carrier.")
        self.n, self.targets, self.paid = n, tuple(targets), tuple(paid)
        self.ticks, self.rounds = ticks, rounds
        self.bands = range(lower, upper, 2)
        self.delay, self.count = {}, {}
        self.send, self.receive, self.sources = (
            defaultdict(list),
            defaultdict(list),
            defaultdict(list),
        )
        self.source_width = 0
        t = F(t)
        measure = Measure(t, volume, max(256, 64 * n.bit_length()))
        ids = defaultdict(list)
        for i, k in enumerate(targets):
            ids[k].append(i)
        by_paid = defaultdict(list)
        for (r, k), share in cells.items():
            if r <= 0 or not ids[k] or share <= 0 or 5 * r > 4 * k:
                raise ValueError(
                    "Every positive transport cell needs a funded descending edge."
                )
            for i in ids[k]:
                by_paid[r].append((i, k, F(share) / len(ids[k])))
        for r in set(paid):
            if sum(q for i, k, q in by_paid[r]) != 1:
                raise ValueError("Every paid label needs a complete probability row.")
        headroom = defaultdict(int)
        level, limit = 0, F(lower)
        for e in self.bands:
            while limit * scale_step <= e:
                level += 1
                limit *= scale_step
            self.delay[e] = delay_base**level
            self.count[e] = ceil(measure.mass(e, e + 2)[1])
        for e in self.bands:
            for j, r in enumerate(paid):
                used = 0
                for i, k, share in by_paid[r]:
                    left, right = F(e * r, k), F((e + 2) * r, k)
                    low = max(lower, 2 * (left // 2))
                    high = min(upper, 2 * ceil(right / 2))
                    for d in range(low, high, 2):
                        if self.delay[d] >= self.delay[e]:
                            raise ValueError(
                                "An allocated loan would miss its return time."
                            )
                        a, b = max(e, F(d * k, r)), min(e + 2, F((d + 2) * k, r))
                        q = measure.mass(a, b)[0] * share
                        number = q.numerator // q.denominator
                        if number:
                            offset = headroom[d, i]
                            self.send[e, j].append(Link(used, number, d, i, offset))
                            self.receive[d, i].append(Link(offset, number, e, j, used))
                            headroom[d, i] += number
                            used += number
                if used > self.count[e]:
                    raise ArithmeticError(
                        "Outgoing allocations exceed the available copies."
                    )
        for e in self.bands:
            for j, r in enumerate(paid):
                for i, k, share in by_paid[r]:
                    a, b = max(upper, F(e * k, r)), F((e + 2) * k, r)
                    q = measure.mass(a, b)[0] * share
                    number = q.numerator // q.denominator
                    if not number:
                        continue
                    size = (e - 8) * k
                    period = 4 * ceil(F(n, 4 * size))
                    base = self.source_width
                    self.source_width += number * ticks * (rounds // period)
                    self.sources[e, i].append(
                        Source(headroom[e, i], number, base, period)
                    )
                    headroom[e, i] += number
        for (e, i), num in headroom.items():
            if num > self.count[e]:
                raise ArithmeticError(
                    "More fields reached an input than there are native copies."
                )
        if self.source_width <= 0:
            raise ValueError("The epoch has no complete productive period.")
        minimum = 1 << (padding * self.source_width - 1).bit_length()
        self.width = minimum if width is None else width
        if self.width < minimum or self.width.bit_count() != 1:
            raise ValueError("The productive width must cover all complete source periods")

    def _external(self, band, port, replica, birth):
        size = (band - 8) * self.targets[port]
        for src in self.sources.get((band, port), ()):
            offset = replica - src.start
            if 0 <= offset < src.count:
                cycles = self.rounds // src.period
                base = src.base + (birth * src.count + offset) * cycles
                return (2, base, size, src.period)
        return (0, size)

    def events(self):
        serial = 0
        q = len(self.paid)
        maximum = max(self.count.values())
        span = (self.bands.stop - self.bands.start) // 2

        def frame(e, tick, rep):
            return (tick * span + (e - self.bands.start) // 2) * maximum + rep

        for tick in range(self.ticks + q * max(self.delay.values())):
            pending = {}
            for e in self.bands:
                birth = tick - q * self.delay[e]
                if 0 <= birth < self.ticks:
                    for rep in range(self.count[e]):
                        yield (2, frame(e, birth, rep))
            for e in reversed(self.bands):
                step = self.delay[e]
                for j in range(q):
                    birth = tick - j * step
                    if not 0 <= birth < self.ticks:
                        continue
                    for rep in range(self.count[e]):
                        ident = frame(e, birth, rep)
                        if not j:
                            row = [0, ident, e - 8]
                            for i in range(len(self.targets)):
                                loan = pending.pop((e, rep, i), None)
                                if loan is not None:
                                    row.extend((1, loan))
                                    continue
                                for link in self.receive.get((e, i), ()):
                                    if 0 <= rep - link.start < link.count:
                                        if tick >= link.port * self.delay[link.band]:
                                            raise ArithmeticError(
                                                "A scheduled parent loan did not arrive."
                                            )
                                        break
                                row.extend(self._external(e, i, rep, birth))
                            yield tuple(row)
                        selected = 0
                        if tick < self.ticks:
                            for link in self.send.get((e, j), ()):
                                d = rep - link.start
                                if 0 <= d < link.count:
                                    selected = self.targets[link.port] * (link.band - 8)
                                    key = link.band, link.other + d, link.port
                                    if key in pending:
                                        raise ArithmeticError(
                                            "Two parents supplied the same input."
                                        )
                                    pending[key] = serial
                                    break
                        size = self.paid[j] * (e - 8)
                        if size != int(size) or not 0 <= selected <= size:
                            raise ArithmeticError(
                                "The parent cannot cover the selected interval."
                            )
                        yield (1, ident, serial, int(size), selected)
                        serial += 1
            if pending:
                raise ArithmeticError("A pending loan was not collected.")

    @property
    def leaves_per_epoch(self):
        count = 0
        q = len(self.paid)
        for e in self.bands:
            for j in range(q):
                full = self.ticks * self.count[e] * self.paid[j] * (e - 8)
                routed = max(0, self.ticks - j * self.delay[e]) * sum(
                    link.count * self.targets[link.port] * (link.band - 8)
                    for link in self.send.get((e, j), ())
                )
                count += full - routed
        if count != int(count):
            raise ArithmeticError("The paid interval has a fractional axis.")
        return int(count)

    def decode(self, rows, round_no, group, machine, records):
        live, pending = {}, {}
        for row in records:
            op, ident, *args = row
            if op == 0:
                columns, *bindings = args
                ports, zeros = [], []
                cursor = iter(bindings)
                for kind in cursor:
                    if kind == 1:
                        ports.append(pending.pop(next(cursor)))
                        continue
                    base = next(cursor) if kind == 2 else None
                    size = next(cursor)
                    if base is not None:
                        period = next(cursor)
                        cycle, step = divmod(round_no, period)
                        index = group * self.source_width + base + cycle
                        if cycle < self.rounds // period and index < self.width:
                            ports.append(
                                rows[index].select(axes(self.n, size, period, step))
                            )
                            continue
                    job = machine.zero(rows[0].select(range(size)))
                    ports.append(job)
                    zeros.append(job)
                live[ident] = iter(machine.native(ports, columns)), zeros
            elif op == 1:
                serial, size, selected = args
                job = next(live[ident][0])
                if len(job.axes) != size:
                    raise ArithmeticError(
                        "The physical native word issued the wrong rank."
                    )
                for k in range(selected, size):
                    machine.leaf(job.select((k,)))
                if selected:
                    pending[serial] = job.select(range(selected))
            else:
                iterator, zeros = live.pop(ident)
                if next(iterator, None) is not None:
                    raise ArithmeticError("The word emitted an extra loan.")
                for job in zeros:
                    machine.retire_zero(job)
        if live or pending:
            raise ArithmeticError("The last native owner did not return.")

    def run(self, rows, machine):
        if len(rows) != self.width:
            raise ValueError("The caller has the wrong productive width.")
        for group in range(ceil(F(self.width, self.source_width))):
            for round_no in range(self.rounds):
                self.decode(rows, round_no, group, machine, self.events())


class Recipe:
    def __init__(
        self, rank_log, ambient, targets, paid, cells, trial, level_floor=2**15
    ):
        if rank_log < 3000:
            raise ValueError(
                "The production width proof requires rank_log at least 3000."
            )
        self.rank_log, self.ambient = rank_log, ambient
        self.targets, self.paid, self.cells = targets, paid, cells
        self.trial, self.level_floor = trial, level_floor
        self.width_log = 92 * rank_log

    @property
    def width(self):
        return 1 << self.width_log

    def open(self):
        n = 1 << self.rank_log
        upper = 2 * (n // (2048 * self.ambient))
        return Plan(
            n,
            self.targets,
            self.paid,
            self.cells,
            1 - self.trial,
            self.level_floor,
            upper,
            n**6,
            n**82,
            n**2,
            width=self.width,
            delay_base=2**19,
        )
