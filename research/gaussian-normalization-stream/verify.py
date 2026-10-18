#!/usr/bin/env python3
"""Independent Gaussian-integer oracle and physical tape invoices (seed 34)."""
import argparse
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from random import Random
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def bootstrap():
    path = HERE/'norm_sources.py'
    module = types.ModuleType('norm_sources')
    module.__file__ = str(path)
    sys.modules[module.__name__] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    module.activate()
    return module

sources = bootstrap()
normalizer = sources.load_bytes((HERE/'normalizer.py').read_bytes(), 'normalizer', HERE/'normalizer.py')
from cardinal_counts import Count
from check_support import no_decode
from records import Tape
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from stream import Counter
from words import BLANK, need


def body(tape):
    return bytes(borrowed_tape(tape).cells[1:]).rstrip(bytes([BLANK]))


def encode(values, width):
    return bytes((value >> bit) & 1 for value in values for bit in range(width))


def fill(tape, raw):
    for bit in raw:
        tape.append(bit)
    tape.rewind()


def snapshot(counts):
    return tuple((bytes(borrowed_tape(c.tape).cells), borrowed_tape(c.tape).head) for c in counts)


def closed(engine):
    need(engine.closed and not engine.pool.live, 'normalizer closed roles')
    need(all(t.head == 1 and all(c == BLANK for c in t.cells) for t in engine.pool.tapes),
         'normalizer erases all scratch bodies and markers')


def dispose(tape):
    tape.clear()
    erase_marker(tape)
    need(tape.head == 1 and all(c == BLANK for c in tape.cells), 'protected output disposal')


def mul(z, w):
    a, b = z
    c, d = w
    return a*c-b*d, a*d+b*c


def power(z, exponent):
    result = (1, 0)
    for _ in range(exponent):
        result = mul(result, z)
    return result


def oracle(values, degree):
    """Integer Gaussian multiplication by (1-i)^D / 2^D; no phase shortcut."""
    numerator, denominator = power((1, -1), degree), 1 << degree
    out = []
    for offset in range(0, len(values), 2):
        pair = mul(tuple(values[offset:offset+2]), numerator)
        if any(x % denominator for x in pair):
            return None
        out.extend(x // denominator for x in pair)
    return out


def execute_case(engine, source, width, count, degree, h, d, values):
    raw = encode(values, h)
    fill(source, raw)
    descriptors = (width, count, degree)
    saved = snapshot(descriptors)
    expected = oracle(values, d)
    need(expected is None or all(-(1 << (h-1)) <= value < (1 << (h-1)) for value in expected),
         'independent exact output fits its signed word')
    with no_decode():
        try:
            result = engine.run(source, *descriptors)
        except normalizer.NormalizationError as error:
            need(expected is None and 'inexact' in str(error), 'independent divisibility rejection')
            need(all(c == BLANK for c in engine.output.cells), 'rejected output erased')
        else:
            need(expected is not None and body(result) == encode(expected, h), 'independent Gaussian result')
            need(result.head == 1, 'protected output origin')
            dispose(result)
    closed(engine)
    need(body(source) == raw and source.head == 1, 'borrowed source preserved')
    need(snapshot(descriptors) == saved, 'borrowed descriptors preserved')
    source.clear()
    return expected


def identities():
    engine, source = normalizer.Normalizer(), Tape()
    rng, digest = Random(34), sha256()
    counts = dict(exhaustive=0, boundary=0, valid=0, inexact=0)
    for h in (2, 3, 4, 5, 17, 65):
        width, count = Count.literal(h), Count.literal(1)
        limit = 1 << (h-1)
        degrees = range(h+1) if h <= 5 else sorted({0, 1, 2, 3, h//2, h-1, h})
        for d in degrees:
            degree = Count.literal(d)
            if h <= 5:
                cases = product(range(-limit, limit), repeat=2)
            else:
                edges = (-limit, -limit+1, -1, 0, 1, limit-2, limit-1)
                cases = list(product(edges, repeat=2))
                factor = power((1, 1), d)
                for _ in range(24):
                    pair = mul((rng.randrange(-32, 33), rng.randrange(-32, 33)), factor)
                    if all(-limit <= x < limit for x in pair):
                        cases.append(pair)
            for values in cases:
                result = execute_case(engine, source, width, count, degree, h, d, values)
                counts['exhaustive' if h <= 5 else 'boundary'] += 1
                counts['inexact' if result is None else 'valid'] += 1
                digest.update(json.dumps((h, d, values, result), separators=(',', ':')).encode())
            degree.close()
        width.close()
        count.close()
    return dict(counts=counts, sha256=digest.hexdigest(), peak_scratch_roles=engine.pool.peak)


def copy_packet(source, target):
    source = borrowed_tape(source)
    source.rewind()
    while source.read() != BLANK:
        target.append(source.read())
        source.step(1)
    source.rewind()
    target.rewind()


class StagedControl:
    """Physical encoded D-loop, including parent/child copies and disposal.

This comparator intentionally repeats the exact D=1 kernel. It is not claimed
as a lower bound for every staged implementation or as the predecessor's code.
"""
    def __init__(self):
        self.pool = ScratchPool(32)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        self.child = normalizer.Normalizer()
        self.closed = True
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)

    def run(self, source, width, count, degree):
        for tape in (*self.pool.tapes, self.output):
            initialize_marker(tape)
        self.closed = False
        with sealed_constructors(), self.scope.installed():
            current = self.pool.acquire()
            copy_packet(source, current)
            one, remaining = Count.literal(1), Counter(degree)
            while not remaining.finished:
                with self.scope.suspended():
                    result = self.child.run(borrowed_tape(current), borrowed_count(width),
                                            borrowed_count(count), borrowed_count(one))
                following = self.pool.acquire()
                copy_packet(result, following)
                dispose(result)
                current.clear()
                current = following
                remaining.decrement()
            copy_packet(current, self.output)
            current.clear()
            one.close()
            remaining.close()
            self.pool.empty()
        for tape in self.pool.tapes:
            erase_marker(tape)
        self.closed = True
        return self.output


def invoice(tapes):
    unique = {id(t): t for t in tapes}.values()
    return {key: sum(getattr(t.meter, key) for t in unique) for key in ('reads', 'writes', 'moves')}


def benchmark(engine_type, h, d, values):
    engine, source = engine_type(), Tape()
    descriptors = tuple(Count.literal(x) for x in (h, len(values)//2, d))
    raw, expected = encode(values, h), oracle(values, d)
    fill(source, raw)
    saved = snapshot(descriptors)
    tapes = [source, *(c.tape for c in descriptors), *engine.pool.tapes, engine.output]
    if isinstance(engine, StagedControl):
        tapes.extend((*engine.child.pool.tapes, engine.child.output))
    before = invoice(tapes)
    with no_decode():
        result = engine.run(source, *descriptors)
        need(body(result) == encode(expected, h), 'same-input physical comparator value')
        dispose(result)
    after = invoice(tapes)
    closed(engine)
    if isinstance(engine, StagedControl):
        closed(engine.child)
    need(body(source) == raw and source.head == 1 and snapshot(descriptors) == saved,
         'same-input comparator preserves borrows')
    costs = {key: after[key]-before[key] for key in before}
    costs['total'] = sum(costs.values())
    source.clear()
    for count in descriptors:
        count.close()
    return costs


def comparisons():
    rows = []
    for d in (1, 2, 8, 17, 34, 64):
        factor = power((1, 1), d)
        values = tuple(x for pair in ((1, 2), (-3, 5), (0, -7), (11, -13)) for x in mul(pair, factor))
        fused = benchmark(normalizer.Normalizer, 96, d, values)
        staged = benchmark(StagedControl, 96, d, values)
        if d >= 8:
            need(fused['total'] < staged['total'], 'multi-pass comparison improvement')
        rows.append(dict(h=96, N=4, D=d, V=768, input_sha256=sha256(encode(values, 96)).hexdigest(),
                         fused=fused, staged=staged))
    return rows


def failures():
    engine, source = normalizer.Normalizer(), Tape()
    width, count, degree = (Count.literal(x) for x in (8, 3, 6))
    # Two fields succeed before a low bit of the third field forces rollback.
    bad, good = (32, -32, 8, 16, 1, 0), (32, -32, 8, 16, -24, 8)
    execute_case(engine, source, width, count, degree, 8, 6, bad)
    execute_case(engine, source, width, count, degree, 8, 6, good)
    for descriptor in (width, count, degree):
        descriptor.close()

    for h, d in ((1, 1), (8, 9)):
        descriptors = tuple(Count.literal(x) for x in (h, 1, d))
        fill(source, encode((0, 0), h))
        saved = snapshot(descriptors)
        with no_decode():
            try:
                engine.run(source, *descriptors)
            except normalizer.NormalizationError as error:
                need('parameter domain' in str(error), 'named parameter rejection')
            else:
                raise ValueError('invalid parameter accepted')
        closed(engine)
        need(snapshot(descriptors) == saved and body(source) == encode((0, 0), h)
             and source.head == 1, 'parameter rejection preserves borrows')
        source.clear()
        for descriptor in descriptors:
            descriptor.close()

    descriptors = tuple(Count.literal(x) for x in (8, 1, 0))
    fill(source, encode((-128, 127), 8))
    with no_decode():
        engine.run(source, *descriptors)
        before = body(engine.output)
        try:
            engine.run(source, *descriptors)
        except ValueError as error:
            need('consume normalization output' in str(error), 'live output guard')
        else:
            raise ValueError('unconsumed output accepted')
        need(body(engine.output) == before, 'pending output preserved')
        dispose(engine.output)
        for alias in (engine.output, engine.pool.tapes[0]):
            try:
                engine.run(alias, *descriptors)
            except ValueError as error:
                need('distinct normalization source' in str(error), 'owned-source alias guard')
            else:
                raise ValueError('owned source alias accepted')
    closed(engine)
    source.clear()
    for descriptor in descriptors:
        descriptor.close()
    return dict(late_inexact_rollback_and_retry=True, domain_rejections=2,
                unconsumed_output_preserved=True, owned_source_alias_rejections=2)


def nested():
    parent, engine = ScratchPool(16), normalizer.Normalizer()
    scope = OuterScope(parent)
    values, h, d = (-48, 80, 0, -112, 176, -208), 17, 8
    raw, expected = encode(values, h), encode(oracle(values, d), h)
    with no_decode(), sealed_constructors(), scope.installed():
        source = parent.acquire()
        fill(source, raw)
        width, count, degree, unrelated = (Count.literal(x) for x in (h, 3, d, 37))
        descriptors = (width, count, degree, unrelated)
        saved = snapshot(descriptors)
        with scope.suspended():
            output = engine.run(borrowed_tape(source), *(borrowed_count(c) for c in descriptors[:3]))
        target = parent.acquire()
        copy_packet(output, target)
        dispose(output)
        need(body(target) == expected and body(source) == raw and snapshot(descriptors) == saved,
             'nested normalization with live parent descriptors')
        closed(engine)
        target.clear()
        source.clear()
        for descriptor in descriptors:
            descriptor.close()
        parent.empty()
    for tape in parent.tapes:
        erase_marker(tape)
    need(not parent.live and all(t.head == 1 and all(c == BLANK for c in t.cells)
                                for t in parent.tapes), 'nested caller complete disposal')
    return dict(parent_peak=parent.peak, child_peak=engine.pool.peak,
                retained_parent_counts=4, gaussians=3, output_sha256=sha256(expected).hexdigest())


def mutations():
    original = (HERE/'normalizer.py').read_text()
    controls = (
        ('discarded_low_bit', 'if digit:\n', 'if False:\n', 1, (1, 0)),
        ('quarter_phase', 'phase_rows(odd, low_phase(half))', 'phase_rows(odd, 0)', 2, (4, 0)),
        ('odd_shift', 'shift.increment()', 'pass', 3, (4, 4)),
        ('negative_carry', 'total % 2, total // 2', 'total % 2, int(total / 2)', 1, (-2, 0)),
    )
    detected = []
    for name, before, after, d, values in controls:
        need(before in original, 'mutation target exists')
        mutant = sources.load_bytes(original.replace(before, after).encode(), 'mutant_'+name,
                                    HERE/('mutant_'+name+'.py'))
        engine, source = mutant.Normalizer(), Tape()
        descriptors = tuple(Count.literal(x) for x in (8, 1, d))
        fill(source, encode(values, 8))
        expected = oracle(values, d)
        with no_decode():
            try:
                output = engine.run(source, *descriptors)
            except ValueError:
                mismatch = expected is not None
            else:
                mismatch = expected is None or body(output) != encode(expected, 8)
                dispose(output)
        need(mismatch, 'independent oracle detects '+name)
        detected.append(name)
        source.clear()
        for descriptor in descriptors:
            descriptor.close()
    return dict(detected=detected)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit', action='store_true')
    parser.add_argument('--suite', choices=('identities', 'comparison', 'controls', 'all'), default='all')
    args = parser.parse_args()
    result = {}
    if args.suite in ('identities', 'all'):
        result['identities'] = identities()
    if args.suite in ('comparison', 'all'):
        result['comparison'] = comparisons()
    if args.suite in ('controls', 'all'):
        result['controls'] = dict(failures=failures(), nested=nested(), mutations=mutations())
    if not args.emit:
        expected = json.loads((HERE/'RESULT.json').read_bytes())
        if args.suite != 'all':
            expected = {key: expected[key] for key in result}
        need(json.dumps(result, sort_keys=True, separators=(',', ':'), allow_nan=False) ==
             json.dumps(expected, sort_keys=True, separators=(',', ':'), allow_nan=False),
             'complete typed normalization receipt')
    print(json.dumps(result, sort_keys=True, indent=2))
    if not args.emit:
        print('PASS_GAUSSIAN_NORMALIZATION_STREAM')


if __name__ == '__main__':
    main()
