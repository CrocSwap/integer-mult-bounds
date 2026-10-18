"""Full high-cube permutations with exact low carries and complete spectators."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from types import SimpleNamespace
import json
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stage_sources
_source, retained, _data = stage_sources.activate()
from cardinal_counts import Count
from check_support import no_decode
from compile_routes import Registry, inverse_word
from directory import Context
from low_codes import LowCodes
from macro_code import Code
from ordinary import Ordinary
from physical_words import PhysicalArena, PhysicalWord
from provenance import Provenance
from records import Tape
from routes import compile_route, route_packet
from scratch_pool import ScratchPool
from stage import Adapter, StagePool
from words import BLANK, Ring, Word, need


def body(tape):
    tape = getattr(tape, "physical", tape)
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def native_fixture(q):
    binding = SimpleNamespace(codes=SimpleNamespace(q=q))
    return Ordinary(q, binding, SimpleNamespace(families=0),
                    (Code((("unreachable",),), 0),), capacity=64)


def one_case(q, width, low, word, old_prefixes=2, fibre_value=3):
    codes = LowCodes(q, 2, 1)
    chart = retained.replay(word, 2)
    registry = Registry(2)
    registry.register(chart, word)
    inverse = inverse_word(word)
    registry.register(retained.replay(inverse, 2), inverse)
    route = compile_route(low, chart, codes)
    maximum = Count.literal(q**width)
    bank, pool = PhysicalArena(64), ScratchPool(q*q+256)
    bank.prepare(maximum)
    modulus = bank.load(maximum)
    ring = Ring(modulus)
    context = Context(ring, codes)
    prefixes, fibre = Count.literal(old_prefixes), Count.literal(fibre_value)
    high = q**(width-1)
    rows = high**4
    length = old_prefixes*rows*fibre_value
    source = Tape()
    for address in range(length):
        source.append((address*13 ^ address//3 ^ 5) & 1)
    source.rewind()
    initial = body(source)
    observer = Provenance(length)
    observer.mark(source)
    adapter = Adapter(native_fixture(q), registry, capacity=64)
    scope = StagePool(pool, adapter)
    def forbidden(*_args, **_kwargs):
        raise ValueError("fixture-only operation in routed payload")
    with no_decode(), observer.installed(), patch.object(Word, "__init__", forbidden), \
            patch.object(PhysicalWord, "inspect", forbidden), scope.install():
        output = route_packet(source, route, context, prefixes, fibre)
        expected, masks = bytearray(length), [0]*length
        lifted = [[int(F(value).numerator * pow(F(value).denominator, -1, q**width)) % (q**width)
                   for value in row] for row in chart]
        for index, digits in enumerate(product(range(high), repeat=4)):
            matrix = [[low[i][j]+q*digits[2*i+j] for j in range(2)] for i in range(2)]
            mapped = [[sum(matrix[i][k]*lifted[k][j] for k in range(2)) % (q**width)
                       for j in range(2)] for i in range(2)]
            target = 0
            for i in range(2):
                for j in range(2):
                    target = target*high + (mapped[i][j]-route.target_low[i][j])//q
            for prefix in range(old_prefixes):
                for suffix in range(fibre_value):
                    origin = (prefix*rows+index)*fibre_value+suffix
                    destination = (prefix*rows+target)*fibre_value+suffix
                    expected[destination], masks[destination] = initial[origin], 1 << origin
        need(body(output) == expected and observer.masks(output.physical, length) == tuple(masks),
             "complete high route, low carry and independent input columns")
        need(body(source) == initial and source.head == output.head == 1,
             "route packet preserves borrowed source and heads")
        output.clear()
        pool.empty()
    adapter.close()
    need(adapter.native.closed and all(bit == BLANK for bit in adapter.native.output.cells),
         "preceding-stage output port closes after routing")
    result = dict(q=q, width=width, columns=length, low=[list(row) for row in low],
                  operations=len(registry.compile(route)), calls=adapter.calls,
                  parent_peak=pool.peak)
    source.clear()
    prefixes.close()
    fibre.close()
    context.close()
    ring.close()
    bank.free(modulus)
    bank.erase_owned()
    maximum.close()
    return result


def run():
    # Noncommuting order, reverse ADD, dyadic scaling and signed low carries.
    word = (("add", 0, 1, F(1,2)), ("scale", 1, 1, F(-2)), ("swap", 0, 1, F(1)))
    cases = []
    for low in (((1,0),(0,1)), ((1,2),(2,2)), ((2,1),(1,1))):
        cases.append(one_case(3, 2, low, word))
    cases.append(one_case(3, 1, ((1,2),(2,2)), word))
    cases.append(one_case(5, 2, ((1,4),(2,1)), inverse_word(word)))
    return cases


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
    print("PASS_COMPLETE_HIGH_ROUTES")
