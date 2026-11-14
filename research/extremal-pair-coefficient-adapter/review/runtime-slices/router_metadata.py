"""Fixed-tape permutation validation, cycle factorization and record geometry."""

from contextlib import contextmanager
from router_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import read_fixed, reduced, write_fixed
from encoded import compare, subtract
from stream import Counter
from words import BLANK, need


@contextmanager
def owned(*values):
    """Close a lexically bounded tuple of numerical scratch roles."""
    try:
        yield values
    finally:
        for value in reversed(values):
            value.close()


def indices(count):
    with owned(Count.literal(0), Counter(count)) as (index, remaining):
        while not remaining.finished:
            yield index
            index.increment()
            remaining.decrement()


def ceiling_log(value):
    positive(value)
    with owned(Count.literal(1)) as (one,):
        current = subtract(value, one)
    result = Count.literal(0)
    try:
        while not current.zero():
            current.divide_small(2)
            result.increment()
        return result
    except BaseException:
        result.close()
        raise
    finally:
        current.close()


def position_width(value):
    result = ceiling_log(value)
    if result.zero():
        result.increment()
    return result


class Pairs:
    def __init__(self, tape, count, width):
        self.tape, self.count, self.width = tape, count, width

    @contextmanager
    def at(self, index):
        self.tape.rewind()
        with owned(Count.product(index, self.width)) as (distance,):
            distance.multiply_small(2)
            for _ in indices(distance):
                need(self.tape.read() in (0, 1), "complete router pair prefix")
                self.tape.step(1)
        first = second = None
        try:
            first = read_fixed(self.tape, self.width)
            second = read_fixed(self.tape, self.width)
            yield first, second
        finally:
            if first is not None:
                first.close()
            if second is not None:
                second.close()
            self.tape.rewind()

    def exact_end(self):
        with owned(Count.product(self.count, self.width)) as (extent,):
            extent.multiply_small(2)
            self.tape.rewind()
            try:
                for _ in indices(extent):
                    need(self.tape.read() in (0, 1), "complete router pair descriptor")
                    self.tape.step(1)
                need(self.tape.read() == BLANK, "exact router pair descriptor extent")
            finally:
                self.tape.rewind()

    def image(self, source):
        for index in indices(self.count):
            with self.at(index) as (old, new):
                if compare(old, source) == 0:
                    return Count(new)
        raise ValueError("permutation image in listed support")

    def validate(self, n):
        positive(n)
        need(isinstance(self.count, Count) and isinstance(self.width, Count), "encoded router metadata")
        with owned(position_width(n)) as (width,):
            need(compare(width, self.width) == 0, "canonical router position width")
        need(compare(self.count, n) <= 0, "listed support fits address")
        self.exact_end()
        identity = True
        previous = None
        try:
            for index in indices(self.count):
                with self.at(index) as (source, target):
                    need(compare(source, n) < 0 and compare(target, n) < 0, "bounded permutation position")
                    need(previous is None or compare(previous, source) < 0, "sorted unique support")
                    if previous is not None:
                        previous.close()
                    previous = Count(source)
                    identity = identity and compare(source, target) == 0
                    found = False
                    for other in indices(self.count):
                        with self.at(other) as (other_source, other_target):
                            found = found or compare(other_source, target) == 0
                            need(compare(index, other) == 0 or compare(target, other_target) != 0,
                                 "unique permutation images")
                    need(found, "equal permutation source and image sets")
            return identity
        finally:
            if previous is not None:
                previous.close()


def write_pair(tape, first, second, width):
    write_fixed(first, tape, width)
    write_fixed(second, tape, width)


def factor(table, first, second, factory):
    """Emit J0 then J1, where J1 J0 moves old coordinates by pi."""
    cycle = factory()
    counts = (Count.literal(0), Count.literal(0))
    try:
        for ordinal in indices(table.count):
            with table.at(ordinal) as (start, _):
                current, length, least = Count(start), Count.literal(0), True
                try:
                    for _ in indices(table.count):
                        write_pair(cycle, current, current, table.width)
                        least = least and compare(start, current) <= 0
                        following = table.image(current)
                        current.close()
                        current = following
                        length.increment()
                        if compare(current, start) == 0:
                            break
                    need(compare(current, start) == 0, "closed bounded permutation cycle")
                    if least:
                        view = Pairs(cycle, length, table.width)
                        for phase, destination in enumerate((first, second)):
                            for index in indices(length):
                                with owned(subtract(length, index)) as (partner_raw,):
                                    if phase:
                                        partner_raw.increment()
                                    with owned(reduced(partner_raw, length)) as (partner,):
                                        if compare(index, partner) < 0:
                                            with view.at(index) as (a, _), view.at(partner) as (b, _):
                                                write_pair(destination, a, b, table.width)
                                            counts[phase].increment()
                finally:
                    current.close()
                    length.close()
                    # Keep this lease for the next cycle.
                    from session import borrowed_tape
                    borrowed_tape(cycle).clear()
        first.rewind()
        second.rewind()
        return counts
    except BaseException:
        for count in counts:
            count.close()
        raise
    finally:
        cycle.clear()


def block_image(position, a, b, width):
    """Conjugate a coordinate by an actual disjoint equal-block exchange."""
    with owned(Count(a), Count(b)) as (a_end, b_end):
        a_end.add(width)
        b_end.add(width)
        if compare(a, position) <= 0 and compare(position, a_end) < 0:
            result = subtract(position, a)
            result.add(b)
            return result
        if compare(b, position) <= 0 and compare(position, b_end) < 0:
            result = subtract(position, b)
            result.add(a)
            return result
        return Count(position)


def untouched_gap(table, n, ell):
    candidate = Count(ell)
    try:
        # table is sorted by original source coordinate.
        for index in indices(table.count):
            with table.at(index) as (source, _), owned(Count(candidate)) as (end,):
                end.add(ell)
                if compare(source, candidate) >= 0 and compare(source, end) < 0:
                    candidate.close()
                    candidate = Count(source)
                    candidate.increment()
        with owned(Count(candidate)) as (end,):
            end.add(ell)
            if compare(end, n) <= 0:
                result, candidate = candidate, None
                return result
        return None
    finally:
        if candidate is not None:
            candidate.close()
