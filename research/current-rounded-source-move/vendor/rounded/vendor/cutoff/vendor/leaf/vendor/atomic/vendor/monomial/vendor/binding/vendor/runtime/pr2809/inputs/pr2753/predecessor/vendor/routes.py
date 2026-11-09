"""Owner/common high-cube routes by binary keys and sequential stable passes."""
from dataclasses import dataclass
from fractions import Fraction

from bitstream import copy_bits
from counts import Count
from directory import Odometer, append_tape
from matrices import Matrices
from records import WORD_END, Tape, append_word, read_word
from stream import Counter
from words import BLANK, ONE, RIGHT, ZERO, need


@dataclass(frozen=True)
class Route:
    q: int
    dimension: int
    low: tuple
    target_low: tuple
    chart: tuple


def compile_route(low, chart, vocabulary):
    """Compile fixed labels only; no input modulus or high digit is available."""
    import oracle
    q, dimension = vocabulary.q, vocabulary.dimension
    vocabulary.rank(low)
    need(len(chart) == dimension and all(len(row) == dimension for row in chart), "fixed chart shape")
    chart = tuple(tuple(Fraction(x) for x in row) for row in chart)
    reduced = oracle.reduce_rational(chart, q)
    oracle.inverse(reduced, q)
    target = tuple(map(tuple, oracle.multiply(low, reduced, q)))
    vocabulary.rank(target)
    return Route(q, dimension, tuple(map(tuple, low)), target, chart)


def inverse_rational(matrix):
    """Fixed source compilation; fractions never enter measured payload loops."""
    size = len(matrix)
    rows = [[Fraction(x) for x in row]+[Fraction(i == j) for j in range(size)]
            for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = next((i for i in range(column, size) if rows[i][column]), None)
        need(pivot is not None, "invertible fixed rational chart")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [x/scale for x in rows[column]]
        for i in range(size):
            if i != column:
                factor = rows[i][column]
                rows[i] = [x-factor*y for x, y in zip(rows[i], rows[column])]
    return tuple(tuple(row[size:]) for row in rows)


def high_key(high, route, chart, context):
    matrices, arena = Matrices(context.ring), context.arena
    raw = matrices.raw_header(route.low, high, context.q)
    common = matrices.multiply(raw, chart)
    matrices.free(raw)
    divisor = arena.literal(context.q)
    keys = []
    try:
        for i in range(context.dimension):
            row = []
            keys.append(row)
            for j in range(context.dimension):
                low = arena.literal(route.target_low[i][j])
                difference = context.raw.subtract_exact(common[i][j], low)
                quotient, remainder = context.raw.divmod(difference, divisor)
                arena.free_many(low, difference)
                valid = remainder.zero() and context.raw.compare(quotient, context.cap) < 0
                arena.free(remainder)
                row.append(quotient)
                need(valid, "exact routed low class and high carry")
        return keys
    except ValueError:
        matrices.free(keys)
        raise
    finally:
        matrices.free(common)
        arena.free(divisor)


def copy_key(source, output, context, selected=None, cursor=None):
    bit = ZERO
    template = context.arena.template
    for coordinate in range(context.dimension*context.dimension):
        template.rewind()
        if coordinate == selected:
            cursor.rewind()
        while template.read() != RIGHT:
            value = source.read()
            need(value in (ZERO, ONE), "complete binary route key")
            if coordinate == selected:
                if cursor.read() == ONE:
                    bit = value
                cursor.step(1)
            output.append(value)
            source.step(1)
            template.step(1)
        need(source.read() == WORD_END, "route key word extent")
        output.append(WORD_END)
        source.step(1)
        template.rewind()
        if coordinate == selected:
            cursor.rewind()
    return bit


def copy_rows(source, output, count, fibre):
    remaining = Counter(count)
    try:
        while not remaining.finished:
            copy_bits(source, output, fibre)
            remaining.decrement()
    finally:
        remaining.close()


def partition(source, coordinate, cursor, context, fibre, factory):
    buckets = (factory(), factory())
    counts = (Count.literal(0), Count.literal(0))
    records = Counter(context.highs)
    output = factory()
    try:
        while not records.finished:
            key = Tape()
            try:
                bit = copy_key(source, key, context, coordinate, cursor)
                append_tape(key, buckets[bit])
                copy_bits(source, buckets[bit], fibre)
                counts[bit].increment()
            finally:
                key.clear()
            records.decrement()
        need(source.read() == BLANK, "complete route partition")
        source.rewind()
        for bucket, count in zip(buckets, counts):
            bucket.rewind()
            remaining = Counter(count)
            while not remaining.finished:
                copy_key(bucket, output, context)
                copy_bits(bucket, output, fibre)
                remaining.decrement()
            remaining.close()
            need(bucket.read() == BLANK, "complete stable route bucket")
        output.rewind()
        return output
    except ValueError:
        output.clear()
        raise
    finally:
        records.close()
        for bucket, count in zip(buckets, counts):
            bucket.clear()
            count.close()


def route_cube(source, route, context, fibre, factory=Tape):
    need((route.q, route.dimension) == (context.q, context.dimension), "route/context binding")
    matrices, arena = Matrices(context.ring), context.arena
    chart = matrices.constants(route.chart)
    high, decorated = Odometer(context), factory()
    source.rewind()
    current, output = decorated, None
    try:
        while not high.finished:
            key = high_key(high.digits, route, chart, context)
            for row in key:
                for digit in row:
                    append_word(decorated, digit)
            matrices.free(key)
            copy_bits(source, decorated, fibre)
            high.advance()
        need(source.read() == BLANK, "complete source high cube")
        source.rewind()
        decorated.rewind()
        if context.raw.compare(context.cap, context.ring.one) > 0:
            for coordinate in reversed(range(context.dimension*context.dimension)):
                cursor = arena.copy(context.ring.one)
                try:
                    while True:
                        following = partition(current, coordinate, cursor, context, fibre, factory)
                        current.clear()
                        current = following
                        cursor.msb()
                        final = cursor.read() == ONE
                        cursor.rewind()
                        if final:
                            break
                        shifted = context.raw.shift_add_bit(cursor, ZERO)
                        arena.free(cursor)
                        cursor = shifted
                finally:
                    arena.free(cursor)
        high.close()
        high = Odometer(context)
        output = factory()
        while not high.finished:
            for row in high.digits:
                for expected in row:
                    actual = read_word(current, arena)
                    valid = context.raw.compare(actual, expected) == 0
                    arena.free(actual)
                    need(valid, "complete bijective routed high order")
            copy_bits(current, output, fibre)
            high.advance()
        need(current.read() == BLANK, "complete routed key removal")
        output.rewind()
        return output
    except ValueError:
        if output is not None:
            output.clear()
        raise
    finally:
        current.clear()
        high.close()
        matrices.free(chart)
        source.rewind()


def route_packet(source, route, context, old_count, fibre, factory=Tape):
    outer, output = Counter(old_count), factory()
    source.rewind()
    try:
        need(not outer.finished, "positive route prefix count")
        while not outer.finished:
            local = factory()
            try:
                copy_rows(source, local, context.highs, fibre)
                local.rewind()
                changed = route_cube(local, route, context, fibre, factory)
                try:
                    copy_rows(changed, output, context.highs, fibre)
                    need(changed.read() == BLANK, "closed routed prefix")
                finally:
                    changed.clear()
            finally:
                local.clear()
            outer.decrement()
        need(source.read() == BLANK, "complete old-prefix route")
        output.rewind()
        return output
    except ValueError:
        output.clear()
        raise
    finally:
        outer.close()
        source.rewind()
