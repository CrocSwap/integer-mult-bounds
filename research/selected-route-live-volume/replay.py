"""Measure every payload/key write in the unchanged source, not a simulated route."""
from contextlib import contextmanager
from hashlib import sha256
from itertools import product

from counts import Count
from directory import Context
from low_codes import LowCodes
from records import Tape
import routes
from words import Arena, BLANK, Ring


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Tracker:
    def __init__(self, target=None):
        self.live = self.peak = self.pending = 0
        self.tapes = []
        self.target, self.census = target, None
        tracker = self

        class MeasuredTape(Tape):
            def __init__(self):
                super().__init__()
                self.origins = {}
                tracker.tapes.append(self)

            def read(self):
                symbol = super().read()
                if self.head > 0 and symbol != BLANK:
                    tracker.pending = self.origins.get(self.head)
                return symbol

            def write(self, symbol):
                old = self.cells[self.head] if self.head < len(self.cells) else BLANK
                super().write(symbol)
                tracker.live += int(symbol != BLANK) - int(old != BLANK)
                tracker.peak = max(tracker.peak, tracker.live)
                if tracker.live == tracker.target and tracker.census is None:
                    tracker.census = sum(sum(value != BLANK for value in tape.cells[1:])
                                        for tape in tracker.tapes)
                    require(tracker.census == tracker.target, "direct census at attained sharp peak")
                if symbol == BLANK:
                    self.origins.pop(self.head, None)
                else:
                    self.origins[self.head] = tracker.pending

        self.factory = MeasuredTape

    def source(self, size):
        require(1 <= size <= 20000, "fixture payload capacity")
        tape = self.factory()
        for index in range(size):
            tape.append(((index * 13) ^ (index >> 3) ^ 0x53) & 1)
            tape.origins[index + 1] = index
        tape.rewind()
        return tape

    def audit(self, survivors):
        total = 0
        for tape in self.tapes:
            content = sum(symbol != BLANK for symbol in tape.cells[1:])
            total += content
            require(content == 0 or tape in survivors, "no leaked owned payload/key tape")
            require(tape.head == 1, "rewound payload/key tape")
        require(total == self.live, "independent final live-symbol census")


@contextmanager
def tracked_keys(tracker):
    original = routes.Tape
    routes.Tape = tracker.factory
    try:
        yield
    finally:
        routes.Tape = original


def bound(prefixes, highs, fibre, key, partitioned):
    require(1 <= prefixes <= 3 and 1 <= highs <= 625 and 1 <= fibre <= 5,
            "bounded arithmetic fixture domain")
    cube, volume = highs * fibre, prefixes * highs * fibre
    return 2 * volume + (3 * (cube + highs * key) if partitioned else 2 * cube + highs * key)


def expected_origins(q, depth, dimension, prefixes, fibre, low, chart):
    """Independent integer modular multiplication and lexicographic indexing."""
    modulus, cap = q**depth, q**(depth - 1)
    highs = cap**(dimension * dimension)
    require(highs <= 625, "complete high-cube fixture capacity")
    target_low = [[sum(low[i][k] * chart[k][j] for k in range(dimension)) % q
                   for j in range(dimension)] for i in range(dimension)]
    expected = [None] * (prefixes * highs * fibre)
    for ordinal, digits in enumerate(product(range(cap), repeat=dimension * dimension)):
        raw = [[low[i][j] + q * digits[i * dimension + j]
                for j in range(dimension)] for i in range(dimension)]
        new = [[sum(raw[i][k] * chart[k][j] for k in range(dimension)) % modulus
                for j in range(dimension)] for i in range(dimension)]
        target = 0
        for i, j in product(range(dimension), repeat=2):
            digit, remainder = divmod(new[i][j] - target_low[i][j], q)
            require(remainder == 0 and 0 <= digit < cap, "oracle routed digit")
            target = target * cap + digit
        for prefix, bit in product(range(prefixes), range(fibre)):
            expected[(prefix * highs + target) * fibre + bit] = (prefix * highs + ordinal) * fibre + bit
    require(None not in expected and len(set(expected)) == len(expected), "oracle bijection")
    return expected


def context_for(q, depth, dimension):
    require(q in (3, 5) and 1 <= depth <= 3 and dimension in (1, 2), "fixture context domain")
    arena = Arena((q**depth).bit_length() + 1)
    modulus = arena.input(q**depth)
    ring = Ring(modulus)
    context = Context(ring, LowCodes(q, dimension))
    return arena, modulus, ring, context


def close_context(arena, modulus, ring, context):
    context.close()
    ring.close()
    arena.free(modulus)
    require(not arena.live, "all arithmetic words released on successful fixture")


def run_case(q, depth, dimension, prefixes, fibre, shear):
    arena, modulus, ring, context = context_for(q, depth, dimension)
    low = ((1,),) if dimension == 1 else ((1, 1), (0, 1))
    chart = ((-1,),) if dimension == 1 else ((1, shear), (0, 1))
    route = routes.compile_route(low, chart, context.codes)
    highs = q**((depth - 1) * dimension * dimension)
    volume = prefixes * highs * fibre
    key = dimension * dimension * (arena.bits + 1)
    predicted = bound(prefixes, highs, fibre, key, depth > 1)
    tracker = Tracker(predicted)
    source = tracker.source(volume)
    original = bytes(source.cells)
    old_count, count = Count.literal(prefixes), Count.literal(fibre)
    with tracked_keys(tracker):
        output = routes.route_packet(source, route, context, old_count, count, tracker.factory)
    expected = expected_origins(q, depth, dimension, prefixes, fibre, low, chart)
    observed = [output.origins.get(index + 1) for index in range(volume)]
    require(observed == expected, "all routed independent Boolean origins")
    require(bytes(output.cells[1:]) == bytes(original[index + 1] for index in expected), "actual routed bits")
    require(bytes(source.cells) == original, "borrowed source preserved")
    require(tracker.peak == predicted, "sharp live-volume equality on literal route")
    require(tracker.census == predicted, "sharp peak independently counted")
    require(tracker.live == 2 * volume, "only source and result survive")
    tracker.audit({source, output})
    result = dict(q=q, depth=depth, dimension=dimension, prefixes=prefixes, fibre=fibre,
                  high_count=highs, key_symbols=key, volume=volume, peak=tracker.peak,
                  output_sha256=sha256(bytes(output.cells[1:])).hexdigest())
    source.clear()
    output.clear()
    tracker.audit(set())
    old_count.close()
    count.close()
    close_context(arena, modulus, ring, context)
    return result


def malformed_cleanup():
    arena, modulus, ring, context = context_for(3, 2, 1)
    route = routes.compile_route(((1,),), ((1,),), context.codes)
    tracker = Tracker()
    source = tracker.source(3)
    source.cells[2] = 7  # A nonbinary payload, with no internal BLANK hole.
    original = bytes(source.cells)
    old_count, fibre = Count.literal(1), Count.literal(1)
    rejected = False
    with tracked_keys(tracker):
        try:
            routes.route_packet(source, route, context, old_count, fibre, tracker.factory)
        except ValueError:
            rejected = True
    require(rejected and bytes(source.cells) == original, "bad payload rejected, source preserved")
    tracker.audit({source})
    source.clear()
    old_count.close()
    fibre.close()
    close_context(arena, modulus, ring, context)


def experiments():
    fixtures = [(3, 1, 1, 1, 1, 0), (3, 1, 2, 3, 2, 1),
                (3, 2, 1, 1, 5, 0), (3, 3, 1, 3, 2, 0),
                (5, 2, 1, 2, 3, 0), (3, 2, 2, 1, 1, 1),
                (3, 2, 2, 3, 2, -1), (5, 2, 2, 1, 1, 1)]
    cases = [run_case(*fixture) for fixture in fixtures]
    for case in cases:
        cube = case["high_count"] * case["fibre"]
        keys = case["high_count"] * case["key_symbols"]
        require(case["peak"] > 2 * case["volume"], "input/output-only budget rejected")
        if case["depth"] > 1:
            incomplete = 2 * case["volume"] + 2 * (cube + keys)
        else:
            incomplete = 2 * case["volume"] + cube + keys
        require(case["peak"] > incomplete, "premature current/bucket disposal budget rejected")
    malformed_cleanup()
    return {"status": "component_certificate", "cases": cases, "controls": 17,
            "scope": "Nonblank route payload/key symbols only; not total stock or host heap."}
