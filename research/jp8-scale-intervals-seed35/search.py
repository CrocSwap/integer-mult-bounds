"""Exact, finite one-register JP8 scale-deferral census. Apache-2.0.

Eva Ayala / ToikY, with substantial OpenAI Codex assistance.
Coefficient preparation is the retained PR837/PR882 implementation.
"""
from functools import lru_cache
from fractions import Fraction as Q
import gzip
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = 'research/community-k492-audit/pr626/replay/mixed-global/base/providers/jp8/LOCAL-PROGRAMS.json.gz'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


horner = load('interval_pr837', 'research/dyadic-horner-direction/lower.py')
grid = load('interval_pr882', 'research/jp8-grid-bounded-synthesis/synth.py')


@lru_cache(None)
def coefficient(q):
    op = ['add', ['T', 0], ['S', 0], q.numerator, q.denominator]
    words = list(horner.candidates(op).values())
    a = abs(q)
    if a != 1 and a.numerator <= 127 and a.denominator in (1, 2, 4, 8, 16):
        entry = grid.solve(a.numerator, a.denominator)
        if grid.improved(entry):
            words.append(grid.lower(op, {a: entry}))
    return min(words, key=len)


def lower(op):
    if op[0] != 'add':
        return horner.lower(op)
    if tuple(op[1]) == tuple(op[2]) or ('W', 0) in (tuple(op[1]), tuple(op[2])):
        raise ValueError('aliased scalar addition')
    replacements = {('T', 0): tuple(op[1]), ('S', 0): tuple(op[2])}
    return [tuple(replacements.get(x, x) if isinstance(x, tuple) else x for x in primitive)
            for primitive in coefficient(Q(op[3], op[4]))]


def shift(h):
    return Q(2**h) if h >= 0 else Q(1, 2**(-h))


def exponent(q):
    a = abs(q)
    if a.numerator & (a.numerator - 1) or a.denominator & (a.denominator - 1):
        raise ValueError('scale is not signed power of two')
    return a.numerator.bit_length() - a.denominator.bit_length()


def touched(op, r):
    return any(isinstance(x, list) and tuple(x) == r for x in op[1:])


def adjusted(op, r, h):
    if op[0] != 'add':
        return op
    power = h * (int(tuple(op[2]) == r) - int(tuple(op[1]) == r))
    q = Q(op[3], op[4]) * shift(power)
    return ['add', op[1], op[2], q.numerator, q.denominator]


def runs(events):
    i = 0
    while i < len(events):
        if events[i][0] != 'scalar':
            i += 1
            continue
        end, frame = i + 1, events[i][2]
        while end < len(events) and events[end][0] == 'scalar' and events[end][2] == frame:
            end += 1
        if frame != 0:
            yield i, end, frame
        i = end


def intervals(events):
    """Every allowed start and cutoff; restoration at a scale is also tried."""
    for begin, end, frame in runs(events):
        for start in range(begin, end):
            op = events[start][1]
            if op[0] != 'scale' or op[1][0] != 'L':
                continue
            h = exponent(Q(op[2], op[3]))
            if abs(h) != 1:
                continue
            r = tuple(op[1])
            delta = -abs(h)
            for stop in range(start + 1, end + 1):
                yield {'start': start, 'stop': stop, 'mode': 'flush',
                       'register': list(r), 'h': h, 'frame': frame,
                       'delta': delta + abs(h)}
                if stop == end:
                    break
                current = events[stop][1]
                if current[0] in ('copy', 'swap') and touched(current, r):
                    break
                if current[0] == 'clear' and tuple(current[1]) == r:
                    yield {'start': start, 'stop': stop + 1, 'mode': 'clear',
                           'register': list(r), 'h': h, 'frame': frame, 'delta': delta}
                    break
                if current[0] == 'scale' and tuple(current[1]) == r:
                    q = Q(current[2], current[3]) * shift(h)
                    combined = ['scale', current[1], q.numerator, q.denominator]
                    yield {'start': start, 'stop': stop + 1, 'mode': 'absorb',
                           'register': list(r), 'h': h, 'frame': frame,
                           'delta': delta + len(lower(combined)) - len(lower(current))}
                delta += len(lower(adjusted(current, r, h))) - len(lower(current))


def materialize(events, candidate):
    start, stop = candidate['start'], candidate['stop']
    r, h = tuple(candidate['register']), candidate['h']
    first = events[start][1]
    sign = -1 if Q(first[2], first[3]) < 0 else 1
    word = lower(['scale', list(r), sign, 1])
    for index in range(start + 1, stop):
        op = events[index][1]
        if candidate['mode'] == 'absorb' and index == stop - 1:
            q = Q(op[2], op[3]) * shift(h)
            op = ['scale', op[1], q.numerator, q.denominator]
        else:
            op = adjusted(op, r, h)
        word.extend(lower(op))
    if candidate['mode'] == 'flush':
        q = shift(h)
        word.extend(lower(['scale', list(r), q.numerator, q.denominator]))
    return word


def share_power_runs(ops, fanin):
    """Credited PR755 fan-out / PR751 fan-in on equal-magnitude cohorts.

    This witness-only composition requires signed power-of-two coefficients.
    Both variants use one existing W, paid literal source reads, and clear it.
    """
    result, i, work = [], 0, ('W', 0)
    while i < len(ops):
        op = ops[i]
        if op[0] == 'add':
            if tuple(op[1]) == tuple(op[2]) or work in (tuple(op[1]), tuple(op[2])):
                raise ValueError('aliased shared addition')
        if op[0] != 'add' or abs(Q(op[3], op[4])) == 1:
            result.extend(lower(op))
            i += 1
            continue
        q = Q(op[3], op[4])
        exponent(q)  # This composition does not synthesize other numerators.
        end = i + 1
        while end < len(ops):
            other = ops[end]
            if other[0] == 'add' and (tuple(other[1]) == tuple(other[2])
                    or work in (tuple(other[1]), tuple(other[2]))):
                raise ValueError('aliased shared addition')
            if (other[0] != 'add' or abs(Q(other[3], other[4])) != abs(q)
                    or other[1 if fanin else 2] != op[1 if fanin else 2]):
                break
            end += 1
        result.append(('copy', work, tuple(op[2])))
        if fanin:
            for other in ops[i + 1:end]:
                relative = Q(other[3], other[4]) / q
                result.append(('add' if relative > 0 else 'subtract', work, tuple(other[2])))
        h = exponent(q)
        result.extend([('double' if h > 0 else 'halve', work)] * abs(h))
        if fanin:
            result.append(('add' if q > 0 else 'subtract', tuple(op[1]), work))
        else:
            for other in ops[i:end]:
                sign = Q(other[3], other[4])
                result.append(('add' if sign > 0 else 'subtract', tuple(other[1]), work))
        result.append(('clear', work))
        i = end
    return result


def census(events):
    histogram, starts, count, improving, best = {}, set(), 0, 0, None
    key = lambda row: (row['delta'], row['start'], row['stop'], row['mode'])
    for row in intervals(events):
        histogram[str(row['delta'])] = histogram.get(str(row['delta']), 0) + 1
        starts.add(row['start'])
        count += 1
        improving += row['delta'] < 0
        if best is None or key(row) < key(best):
            best = row
    return {'starts': len(starts), 'intervals': count,
            'delta_histogram': histogram, 'best': best, 'improving_count': improving}


def main():
    programs = json.load(gzip.open(ROOT / INPUT, 'rt'))
    receipt = {direction: census(events) for direction, events in programs.items()}
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
