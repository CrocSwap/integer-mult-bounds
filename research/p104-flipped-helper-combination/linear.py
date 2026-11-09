"""Exact linear operations and event replay for the mixed-port native word.

Helper-basis replay developed by Ali Romman; extension and explicit four-main
contract by @CubeJerry with substantial OpenAI assistance. Apache-2.0.
The ownership and owned-ascent model is inherited from the pinned #6917 word.
"""
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def add(dst, src, coefficient):
    for k, v in tuple(src.items()):
        value = dst.get(k, 0) + coefficient * v
        if value:
            dst[k] = value
        else:
            dst.pop(k, None)


def span(basis):
    result = {0}
    for v in basis:
        need(type(v) is int and 0 < v < 512 and v not in result,
             'Independent binary frame basis')
        result |= {x ^ v for x in tuple(result)}
    return frozenset(result)


def main_roles(word):
    return (set(word['live']) | {r + 112 for r in word['live']}
            | set(word['hosted']['X2']) | set(word['hosted']['Y2']))


def source_contract(word, source):
    need(all(word[k] == source[k] for k in ('frames', 'live', 'ports', 'hosted')),
         'Fixed native frames and four-main contract')
    need(all(word['initial'][r] == source['initial'][r]
             and word['final'][r] == source['final'][r]
             for r in main_roles(source)),
         'All four main sets retain their initial and final frames')
    need(word['owned_fields'] == source['owned_fields'], 'Fixed owned inventory')


def replay(word, source):
    """All rational input coefficients, frames, ownership, and rank charges.

    MOVE is the identity after conjugation by the current signed frame chart.
    Its literal physical map is checked separately. Public inputs are independent
    basis columns; owned fields start at zero and are not credited as inputs.
    """
    source_contract(word, source)
    n = word['public']
    owned_count = word['owned_fields']
    total = n + owned_count
    need(type(n) is int and n >= source['public'], 'Public field inventory')
    need(len(word['initial']) == len(word['final']) == n, 'Public boundaries')
    need(len(main_roles(word)) == 2*len(word['live'])+2*len(word['hosted']['Dports']), 'Protected mixed-port main sets')
    spaces = [span(b) for b in word['frames']]
    dimensions = list(map(len, word['frames']))
    valid_frame = lambda f: type(f) is int and 0 <= f < len(spaces)
    need(all(valid_frame(f) for f in word['initial'] + word['final']),
         'Boundary frame labels')
    rows = [{r: Q(1)} if r < n else {} for r in range(total)]
    current = word['initial'] + [None] * owned_count
    live_owned = set()
    paid, owned_up, opcounts = Counter(), Counter(), Counter()
    lifetimes = peak = dirty = scalar_allowance = scalar_upper = 0
    max_coefficient = Q(0)
    numerator_bits = denominator_bits = 0

    for index, event in enumerate(word['program']):
        op, r = event[:2]
        opcounts[op] += 1
        need(type(r) is int and 0 <= r < total, ('Register', index))
        if op == 'MOVE':
            old, new, private = event[2:]
            need(valid_frame(old) and valid_frame(new), ('MOVE frames', index))
            need(type(private) is bool and current[r] == old
                 and private == (r in live_owned), ('MOVE source/ownership', index))
            if private:
                need(spaces[old] < spaces[new] or spaces[new] < spaces[old],
                     ('Nested owned transport; inherited A6', index))
                if spaces[old] < spaces[new]:
                    owned_up[dimensions[new] - dimensions[old]] += 1
            else:
                need(r < n and spaces[old] < spaces[new],
                     ('Strict public ascent', index))
            current[r] = new
            paid[abs(dimensions[new] - dimensions[old])] += 1
        elif op == 'INIT':
            need(len(event) == 3 and valid_frame(event[2]) and r >= n
                 and r not in live_owned, ('INIT', index))
            live_owned.add(r)
            rows[r] = {}
            current[r] = event[2]
            lifetimes += 1
            peak = max(peak, len(live_owned))
            scalar_allowance += 2
        elif op == 'CLEAR':
            need(len(event) == 3 and r in live_owned and current[r] == event[2],
                 ('CLEAR', index))
            dirty += bool(rows[r])
            live_owned.remove(r)
            rows[r] = {}
            current[r] = None
            scalar_allowance += 2
        else:
            need(op in ('SCALE', 'ADD', 'COPY'), ('Opcode', index))
            q, frame = Q(event[-2]), event[-1]
            need(valid_frame(frame) and q and current[r] == frame,
                 ('Scalar destination chart', index))
            a, d = abs(q.numerator), q.denominator
            need(d & (d - 1) == 0 and abs(q) + 1 < 2 ** 16,
                 ('Dyadic coefficient alphabet', index))
            max_coefficient = max(max_coefficient, abs(q))
            numerator_bits = max(numerator_bits, a.bit_length())
            denominator_bits = max(denominator_bits, d.bit_length())
            if op == 'SCALE':
                need(len(event) == 4 and a & (a - 1) == 0,
                     ('Dyadic unit scaling', index))
                rows[r] = {k: q * v for k, v in rows[r].items()}
                scalar_allowance += 2 * (abs(a.bit_length() - d.bit_length()) + int(q < 0))
                scalar_upper += 4 * (a.bit_length() + d.bit_length() + 1)
            else:
                s = event[2]
                need(len(event) == 5 and type(s) is int and 0 <= s < total
                     and s != r and current[s] == frame,
                     ('Scalar source chart', index))
                if op == 'COPY':
                    need(r in live_owned and not rows[r], ('COPY into owned zero', index))
                add(rows[r], rows[s], q)
                scalar_allowance += 2 * (3 + a.bit_length() - 1 + a.bit_count() + d.bit_length() - 1)
                scalar_upper += 4 * (a.bit_length() + a.bit_count() + d.bit_length() + 1)

    need(not live_owned and current[:n] == word['final'], 'Final charts and owned return')
    x = set(word['live'])
    y = {r + 112 for r in x}
    active = {word['live'][i] for i in word['hosted']['Dports']}
    second_pairs = dict(zip(word['hosted']['X2'], word['hosted']['Y2']))
    alpha, beta = Q(word['hosted']['alpha']), Q(word['hosted']['beta'])
    for r, row in enumerate(rows):
        expected = {r: Q(1)} if r < n else {}
        if r in x and r not in active:
            expected[r+112] = alpha
        if r in y:
            if r-112 in active:
                expected[r-112] = Q(1)
            else:
                expected = {r-112: beta, r: 1+alpha*beta}
        if r in second_pairs:
            expected[second_pairs[r]] = Q(word['hosted']['alpha2'])
        need(row == expected, ('Every exact public input coefficient', r, row, expected))
    helpers = Counter()
    for r, (old, new) in enumerate(zip(word['initial'], word['final'])):
        if r not in main_roles(word):
            need(spaces[old] < spaces[new], ('Strict productive helper', r))
            helpers[dimensions[new] - dimensions[old]] += 1
    return dict(public=n, owned_fields=owned_count, events=len(word['program']),
                opcounts=dict(opcounts), paid=dict(paid), helpers=dict(helpers),
                owned_lifetimes=lifetimes, peak_owned_fields=peak,
                dirty_owned_clears=dirty, owned_ascent=dict(owned_up),
                exact_public_coefficients=n*n,
                scalar_allowance=scalar_allowance, scalar_upper=scalar_upper,
                max_coefficient=str(max_coefficient), numerator_bits=numerator_bits,
                denominator_bits=denominator_bits)
