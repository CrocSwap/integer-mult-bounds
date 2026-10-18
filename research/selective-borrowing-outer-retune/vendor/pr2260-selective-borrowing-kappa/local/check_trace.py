"""Independent exact row replay of the literal complete forward trace."""
import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent

def need(condition, message):
    if not condition:
        raise ValueError(message)

def span(vectors):
    result = {0}
    for v in vectors:
        result.update(x ^ v for x in list(result))
    return frozenset(result)

def run(data):
    active = data['active_registers']
    values = {r: {(r, ()): Fraction(1)} for r in active}
    frames = {r: span(data['endpoints'][str(r)]['initial']) for r in active}
    private = set()
    profile = Counter()
    maximum_row_l1 = Fraction(1)
    maximum_at = None
    def add_to(d, s, coefficient):
        need(d != s, 'self addition')
        need(frames[d] == frames[s], 'literal ADD common chart')
        for k, value in list(values[s].items()):
            new = values[d].get(k, 0) + coefficient * value
            if new:
                values[d][k] = new
            else:
                values[d].pop(k, None)
    def warp(r, symbol):
        result = {}
        for (var, word), coefficient in values[r].items():
            transformed = word[1:] if word and word[0] == -symbol else (symbol,) + word
            key = var, transformed
            result[key] = result.get(key, 0) + coefficient
        values[r] = {k: q for k, q in result.items() if q}
    for index, e in enumerate(data['events']):
        kind = e[0]
        if kind == 'transport':
            _, r, old, new, paid = e
            need(frames[r] == span(old) and span(old) < span(new) or
                 r in private and frames[r] == span(old) and span(new) < span(old),
                 ('nested physical transport', index))
            need(paid == abs(len(new) - len(old)), 'actual positive dimension gap')
            frames[r] = span(new)
            profile[paid] += 1
        elif kind == 'add':
            _, d, s, q, common = e
            need(frames[d] == span(common) == frames[s], ('ADD chart', index))
            add_to(d, s, Fraction(q))
        elif kind == 'scale':
            _, r, q, common = e
            need(frames[r] == span(common), 'SCALE chart')
            q = Fraction(q)
            need(q != 0, 'invertible SCALE')
            values[r] = {k: q * value for k, value in values[r].items()}
        elif kind == 'swap':
            _, d, s, common = e
            need(frames[d] == frames[s] == span(common), 'SWAP chart')
            values[d], values[s] = values[s], values[d]
        elif kind in ('logical_monomial', 'dual_monomial'):
            _, r, symbol, common = e
            need(frames[r] == span(common), 'monomial chart')
            warp(r, symbol)
        elif kind in ('handoff', 'dual_handoff'):
            _, r, old, new, symbol = e
            need(frames[r] == span(old) and len(old) == len(new), 'handoff chart')
            warp(r, symbol)
            frames[r] = span(new)
        elif kind == 'copy':
            _, r, source, common = e
            need(r not in values or not values[r], 'owned COPY zero guard')
            need(frames[source] == span(common), 'COPY source frame')
            values[r] = dict(values[source])
            frames[r] = span(common)
            private.add(r)
        elif kind == 'clear':
            _, r, common = e
            need(r in private and frames[r] == span(common), 'owned CLEAR guard')
            values[r] = {}
        elif kind == 'zero_buffer':
            _, r, common, restored_role = e
            need(r not in values and restored_role in active, 'fresh zero buffer')
            values[r] = {}
            frames[r] = span(common)
            private.add(r)
        elif kind == 'zero_reframe':
            _, r, common = e
            need(r in private and not values[r], 'only a proved zero array may be reframed freely')
            frames[r] = span(common)
        else:
            raise ValueError(('unknown literal event', e))
        touched = (e[1:3] if kind in ('add', 'swap') else e[1:2])
        for r in touched:
            if r not in values:
                continue
            magnitude = sum(abs(q) for q in values[r].values())
            if magnitude > maximum_row_l1:
                maximum_row_l1, maximum_at = magnitude, [index, r]
    for r in active:
        expected = {(r, ()): Fraction(1)}
        if data.get('orientation') == 'backward':
            if r < 112:
                expected[r + 112, ()] = Fraction(-1)
        elif 112 <= r < 224:
            expected[r - 112, ()] = Fraction(1)
        need(values[r] == expected, ('complete endpoint independent column', r))
        need(frames[r] == span(data['endpoints'][str(r)]['final']), 'endpoint chart')
    need(all(not values[r] for r in private), 'every owned private buffer returned zero')
    need({str(k): v for k, v in profile.items()} == data['local_profile'], 'literal paid profile')
    return dict(status='PASS_COMPLETE_' + data.get('orientation', 'forward').upper() + '_LITERAL_TRACE', independent_input_columns=len(active),
                events=len(data['events']), private_fields=len(private),
                helper_width_inventory=dict(sorted(Counter(data['helper_widths'].values()).items())),
                paid_profile=dict(sorted(profile.items())),
                rank_mass=sum(r * count for r, count in profile.items()),
                exact_free_operator_prefix_row_l1=str(maximum_row_l1),
                prefix_peak_event_and_register=maximum_at)
