"""Generate a retimed physical program for two independently weighted native words."""

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction as Q
from transport import Plan, Source, Measure, ceil


@dataclass(frozen=True)
class NativeType:
    targets: tuple
    paid: tuple
    multiplicity: int


@dataclass(frozen=True)
class TypedLink:
    start: int
    count: int
    band: int
    kind: int
    port: int
    other: int


def column_header(columns, kind):
    """Write the type in the low bit of a positive even column count."""
    if columns < 2 or columns % 2 or kind not in (0, 1):
        raise ValueError("Invalid two-type column descriptor")
    return columns + kind


class TypedPlan(Plan):
    """Interleave the two raw jobs at each physical column scale."""

    def __init__(
        self,
        n,
        types,
        cells,
        t,
        lower,
        upper,
        volume,
        ticks,
        rounds,
        *,
        delay_base,
        scale_step=Q(6, 5),
        padding=4096,
        width=None,
    ):
        if min(ticks, rounds, padding, volume) <= 0 or scale_step <= 1:
            raise ValueError("Use positive clock sizes and an increasing scale step")
        if len(types) != 2 or lower <= 8 or upper <= lower or lower % 2 or upper % 2:
            raise ValueError("Use two raw types and positive even scale endpoints")
        if (
            n % 4
            or min(min(w.multiplicity, len(w.paid), len(w.targets)) for w in types) < 1
            or delay_base < max(len(w.paid) for w in types)
        ):
            raise ValueError(
                "The carrier and the temporal base must support each real raw word"
            )
        if n < 4 * max(max(w.targets) for w in types) * (upper - 8):
            raise ValueError("The productive jobs must fit the carrier")
        self.n, self.types, self.ticks, self.rounds = n, types, ticks, rounds
        self.bands = range(lower, upper, 2)
        self.delay, self.count = {}, {}
        self.send, self.receive, self.sources = (
            defaultdict(list),
            defaultdict(list),
            defaultdict(list),
        )
        self.source_width = 0
        measure = Measure(t, volume, max(256, 64 * n.bit_length()))
        ids = defaultdict(list)
        shares = defaultdict(list)
        for b, w in enumerate(types):
            for i, k in enumerate(w.targets):
                ids[b, k].append(i)
        for (a, r, b, k), share in cells.items():
            if not (0 < r and 5 * r <= 4 * k and share > 0 and ids[b, k]):
                raise ValueError("A physical funding edge fails strict descent")
            owners = ids[b, k]
            for i in owners:
                shares[a, r].append((b, i, k, share / len(owners)))
        for a, w in enumerate(types):
            for r in set(w.paid):
                if sum(p for b, i, k, p in shares[a, r]) != 1:
                    raise ValueError("A paid label lacks funding")
        headroom = defaultdict(int)
        level = 0
        limit = Q(lower)
        for e in self.bands:
            while limit * scale_step <= e:
                level += 1
                limit *= scale_step
            self.delay[e] = delay_base**level
            for a, w in enumerate(types):
                self.count[e, a] = ceil(w.multiplicity * measure.mass(e, e + 2)[1])
        for e in self.bands:
            for a, w in enumerate(types):
                for j, r in enumerate(w.paid):
                    used = 0
                    for b, i, k, share in shares[a, r]:
                        left, right = Q(e * r, k), Q((e + 2) * r, k)
                        low = max(lower, 2 * (left // 2))
                        high = min(upper, 2 * ceil(right / 2))
                        for d in range(low, high, 2):
                            if self.delay[d] >= self.delay[e]:
                                raise ValueError("The child misses its return time")
                            left_end, right_end = (
                                max(e, Q(d * k, r)),
                                min(e + 2, Q((d + 2) * k, r)),
                            )
                            number = int(
                                w.multiplicity
                                * measure.mass(left_end, right_end)[0]
                                * share
                            )
                            if number:
                                cap = headroom[d, b, i]
                                self.send[e, a, j].append(
                                    TypedLink(used, number, d, b, i, cap)
                                )
                                self.receive[d, b, i].append(
                                    TypedLink(cap, number, e, a, j, used)
                                )
                                headroom[d, b, i] += number
                                used += number
                    if used > self.count[e, a]:
                        raise ArithmeticError("More outgoing copies than supplied")
        for e in self.bands:
            for a, w in enumerate(types):
                for j, r in enumerate(w.paid):
                    for b, i, k, share in shares[a, r]:
                        left_end, right_end = max(upper, Q(e * k, r)), Q((e + 2) * k, r)
                        number = int(
                            w.multiplicity
                            * measure.mass(left_end, right_end)[0]
                            * share
                        )
                        if not number:
                            continue
                        size = (e - 8) * k
                        period = 4 * ceil(Q(n, 4 * size))
                        base = self.source_width
                        self.source_width += number * ticks * (rounds // period)
                        self.sources[e, b, i].append(
                            Source(headroom[e, b, i], number, base, period)
                        )
                        headroom[e, b, i] += number
        for (e, b, i), qty in headroom.items():
            if qty > self.count[e, b]:
                raise ArithmeticError("A target owner received two independent fields")
        if self.source_width <= 0:
            raise ValueError("The epoch has no complete productive period")
        self.width = (
            (1 << (padding * self.source_width - 1).bit_length())
            if width is None
            else width
        )
        if self.width < padding * self.source_width or self.width.bit_count() != 1:
            raise ValueError("Too few productive rows")

    def external(self, e, a, i, rep, birth):
        size = (e - 8) * self.types[a].targets[i]
        for src in self.sources.get((e, a, i), ()):
            offset = rep - src.start
            if 0 <= offset < src.count:
                cycles = self.rounds // src.period
                return (
                    2,
                    src.base + (birth * src.count + offset) * cycles,
                    size,
                    src.period,
                )
        return (0, size)

    def open_record(self, owner, band, kind, replica, birth, tick, pending):
        row = [0, owner, column_header(band - 8, kind)]
        for port in range(len(self.types[kind].targets)):
            serial = pending.pop((band, kind, replica, port), None)
            if serial is not None:
                row.extend((1, serial))
                continue
            for link in self.receive.get((band, kind, port), ()):
                if 0 <= replica - link.start < link.count:
                    if tick >= link.port * self.delay[link.band]:
                        raise ArithmeticError(
                            "The funded source failed to deliver its live owner"
                        )
                    break
            row.extend(self.external(band, kind, port, replica, birth))
        return tuple(row)

    def send_prefix(self, band, kind, paid_port, replica, serial, pending):
        for link in self.send.get((band, kind, paid_port), ()):
            offset = replica - link.start
            if 0 <= offset < link.count:
                target = (link.band, link.kind, link.other + offset, link.port)
                if target in pending:
                    raise ArithmeticError("Two loans occupied one target")
                pending[target] = serial
                return self.types[link.kind].targets[link.port] * (link.band - 8)
        return 0

    def events(self):
        serial = 0
        maximum = max(self.count.values())
        span = (self.bands.stop - self.bands.start) // 2

        def frame(e, a, birth, rep):
            return (
                (birth * span + (e - self.bands.start) // 2) * 2 + a
            ) * maximum + rep

        qmax = max(len(w.paid) for w in self.types)
        for tick in range(self.ticks + qmax * max(self.delay.values())):
            pending = {}
            for e in self.bands:
                for a, w in enumerate(self.types):
                    birth = tick - len(w.paid) * self.delay[e]
                    if 0 <= birth < self.ticks:
                        for rep in range(self.count[e, a]):
                            yield (2, frame(e, a, birth, rep))
            for e in reversed(self.bands):
                step = self.delay[e]
                for a, w in enumerate(self.types):
                    first = max(0, (tick - self.ticks) // step + 1)
                    stop = min(len(w.paid), tick // step + 1)
                    for j in range(first, stop):
                        r = w.paid[j]
                        birth = tick - j * step
                        for rep in range(self.count[e, a]):
                            own = frame(e, a, birth, rep)
                            if j == 0:
                                yield self.open_record(
                                    own, e, a, rep, birth, tick, pending
                                )
                            selected = (
                                self.send_prefix(e, a, j, rep, serial, pending)
                                if tick < self.ticks
                                else 0
                            )
                            size = r * (e - 8)
                            if size != int(size) or not 0 <= selected <= size:
                                raise ArithmeticError("The child exceeds its parent")
                            yield (1, own, serial, int(size), selected)
                            serial += 1
            if pending:
                raise ArithmeticError("An emitted loan lost its receiver")

    @property
    def leaves_per_epoch(self):
        total = 0
        for e in self.bands:
            for a, w in enumerate(self.types):
                for j, r in enumerate(w.paid):
                    spent = self.ticks * self.count[e, a] * r * (e - 8)
                    routed = max(0, self.ticks - j * self.delay[e]) * sum(
                        u.count * self.types[u.kind].targets[u.port] * (u.band - 8)
                        for u in self.send.get((e, a, j), ())
                    )
                    total += spent - routed
        if total != int(total):
            raise ArithmeticError("An issued suffix has a fractional axis")
        return int(total)
