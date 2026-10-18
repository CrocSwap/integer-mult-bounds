#!/usr/bin/env python3
"""Separate write-observed backing census; shares only source authentication."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import weakref

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('counter_source', ROOT/'verify.py')
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)


def run():
    rt = v.load_source()
    active = weakref.WeakSet()
    state = SimpleNamespace(peak=0, checked=0)

    def sample():
        v.require(len(active) <= 6, 'bounded independent counter inventory')
        state.peak = max(state.peak, sum(len(tape.cells) for tape in active))

    class CounterTape(rt.records.Tape):
        def __init__(self):
            super().__init__()
            active.add(self)
            sample()

        def write(self, symbol):
            super().write(symbol)
            sample()

    def extent(value):
        original = rt.cardinality.Natural()
        if value > 1:
            original.multiply_small(value)
        return original.marginal()

    # Counter's constructor reads stream.Tape. ADD's default payload factory
    # was captured before this substitution and remains the original Tape.
    original_tape = rt.stream.Tape
    rt.stream.Tape = CounterTape
    try:
        for before in (1,2,3):
            for middle in (1,2,4):
                for suffix in (1,2,3):
                    for modulus in (2,3,4):
                        for coefficient in (0,modulus-1):
                            v.require(not active, 'no retained previous counters')
                            state.peak = 0
                            extents = [extent(n) for n in (before,middle,suffix)]
                            arena = rt.words.Arena(modulus.bit_length()+1, capacity=32)
                            ring = rt.words.Ring(arena.input(modulus))
                            source = rt.records.Tape()
                            F = before*middle*modulus**2*suffix
                            source.cells.extend(bytes(i%2 for i in range(F)))
                            output, traffic = rt.stream.add_pass(
                                source, ring, *extents, lambda: arena.input(coefficient))
                            p,r,m,s = (before.bit_length()+3, arena.bits+2,
                                       middle.bit_length()+3,suffix.bit_length()+3)
                            expected = p+r+m+max(m,r+(2*s if suffix>1 else 0))
                            v.require(state.peak == expected, 'independent exact backing peak')
                            v.require(len(output.cells)==F+1 and traffic['output']['writes']==F,
                                      'complete independent native execution')
                            v.require(not active, 'observer has no strong counter roots')
                            state.checked += 1
    finally:
        rt.stream.Tape = original_tape
    v.require(state.checked == 162, 'complete independent fixture census')
    print('PASS_INDEPENDENT_ADD_COUNTER_BACKING cases=162')


if __name__ == '__main__':
    run()
