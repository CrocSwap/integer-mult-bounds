"""Literal-primitive cross-check of a many-helper gauge; Apache-2.0.

Philipp / GPT-6 Astra. Does not import the new search/transform/replay/invoice or
PR1161's engine. Retains and credits Sagar Thakrar's literal PR696 lowerer.
"""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def source():
    pins = json.loads((HERE / 'vendor/pr1161/SOURCES.json').read_bytes())
    for name, expected in pins['files'].items():
        raw = (ROOT / name).read_bytes()
        normalized = raw if name.endswith('.gz') else raw.replace(b'\r\n', b'\n')
        need(hashlib.sha256(normalized).hexdigest() == expected, 'input hash ' + name)
    with tarfile.open(ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz') as archive:
        values = []
        for name in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz'):
            raw = archive.extractfile('candidate/strict/global8/base/providers/gauge44/' + name).read()
            need(hashlib.sha256(raw).hexdigest() == pins['archive_members']['slots/local/' + name], 'archive member')
            values.append(json.loads(gzip.decompress(raw)))
    return values


def reconstruct(word, events, gauges):
    # Deliberately reconstruct by register scale ratios rather than exponent shifts.
    scales = {('L', h): F(2) ** k for h, k in gauges.items()}
    entry = [['scalar', ['scale', ['L', h], (F(2) ** k).numerator, (F(2) ** k).denominator], 0]
             for h, k in sorted(gauges.items())]
    leave = [['scalar', ['scale', ['L', h], (F(2) ** -k).numerator, (F(2) ** -k).denominator], 1]
             for h, k in sorted(gauges.items())]
    interior = json.loads(json.dumps(events[1:-1]))
    for event in interior:
        if event[0] == 'scalar' and event[1][0] == 'add':
            g = event[1]
            coefficient = F(g[3], g[4]) * scales.get(tuple(g[1]), 1) / scales.get(tuple(g[2]), 1)
            g[3:5] = [coefficient.numerator, coefficient.denominator]
    return events[:1] + entry + interior + leave + events[-1:]


def valuation(q):
    q = abs(q)
    exponent = 0
    while q.denominator > 1:
        q *= 2
        exponent -= 1
    while q.numerator % 2 == 0:
        q /= 2
        exponent += 1
    return exponent


def execute(operations, initial, positive=False):
    state = initial.copy()
    peak = max(state.values()) if positive else F(0)
    for op in operations:
        tag, target = op[:2]
        if tag == 'clear':
            state[target] = F(0)
        elif tag == 'copy':
            state[target] = state[op[2]]
        elif tag == 'double':
            state[target] *= 2
        elif tag == 'halve':
            state[target] /= 2
        elif tag == 'negate':
            if not positive:
                state[target] = -state[target]
        elif tag in ('add', 'subtract'):
            state[target] += state[op[2]] * (1 if positive or tag == 'add' else -1)
        else:
            raise ValueError('unknown primitive')
        if positive:
            peak = max(peak, state[target])
    return state, peak


def denominator_depth(operations, registers):
    """Conservative dyadic denominator depth relative to integral dirty inputs."""
    depths = {r: 0 for r in registers}
    peak = 0
    for op in operations:
        tag, target = op[:2]
        if tag == 'clear':
            depths[target] = 0
        elif tag == 'copy':
            depths[target] = depths[op[2]]
        elif tag == 'double':
            depths[target] = max(0, depths[target] - 1)
        elif tag == 'halve':
            depths[target] += 1
        elif tag in ('add', 'subtract'):
            depths[target] = max(depths[target], depths[op[2]])
        elif tag != 'negate':
            raise ValueError('unknown primitive')
        peak = max(peak, depths[target])
    return peak


def run():
    word, programs = source()
    gauges_raw = json.loads((HERE / 'GAUGES.json').read_bytes())
    receipt = json.loads((HERE / 'CERTIFICATE.json').read_bytes())
    spec = importlib.util.spec_from_file_location('credited_sagar_lowerer', ROOT / 'research/complex-dyadic-lowering/lower.py')
    lower = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lower)
    helpers = set(range(224, 704)) - set(word['centers'])
    for stream in programs.values():
        for e in stream:
            if e[0] == 'residual_adapter':
                helpers.discard(e[2])
            if e[0] == 'scalar' and e[1][0] in ('copy', 'clear'):
                for r in e[1][1:]:
                    if isinstance(r, list) and r[0] == 'L':
                        helpers.discard(r[1])
    helpers = sorted(h for h in helpers if word['start'][h] == 0 and word['final'][h] == 1)
    need(helpers == receipt['eligible_helpers'] and len(helpers) == 237, 'domain identity')

    @lru_cache(None)
    def price(n, d, exponent):
        q = F(n, d) * F(2) ** exponent
        return len(lower.lower(['add', ['L', 0], ['L', 1], q.numerator, q.denominator]))

    results = {}
    for orientation in ('forward', 'backward'):
        events = programs[orientation]
        gauges = {int(h): k for h, k in gauges_raw[orientation].items()}
        need(set(gauges) <= set(helpers), 'eligible gauge')
        candidate = reconstruct(word, events, gauges)
        expected = receipt['orientations'][orientation]
        need(hashlib.sha256(canonical(candidate)).hexdigest() == expected['candidate_sha256'], 'independent reconstruction')
        need([e for e in candidate if e[0] != 'scalar'] == [e for e in events if e[0] != 'scalar'], 'nonscalar equality')
        baseline_ops = [op for e in events if e[0] == 'scalar' for op in lower.lower(e[1])]
        new_ops = [op for e in candidate if e[0] == 'scalar' for op in lower.lower(e[1])]
        need(len(baseline_ops) == expected['baseline']['real_primitives'], 'literal original price')
        need(len(new_ops) == expected['candidate']['real_primitives'], 'literal new price')
        need(2 * (len(baseline_ops) - len(new_ops)) == 13000 == expected['saving_complex'], 'literal saving')
        registers = [('L', i) for i in range(704)] + [('C', i) for i in range(8)] + [('W', 0)]
        rng = random.Random(29)
        for case in range(3):
            initial = {r: F(rng.randrange(-20000, 20001), 2 ** rng.randrange(5)) for r in registers}
            if case == 1:
                initial.update({('L', i): F((-1) ** i * (i + 1) ** 3, 8) for i in range(224, 704)})
            if case == 2:
                initial.update({('L', i): F(0) for i in range(224)})
            final = initial.copy()
            for i in range(112):
                if orientation == 'forward':
                    final['L', 112 + i] += initial['L', i]
                else:
                    final['L', i] -= initial['L', 112 + i]
            final.update({('C', i): F(0) for i in range(8)})
            final['W', 0] = F(0)
            for ops in (baseline_ops, new_ops):
                actual, _ = execute(ops, initial)
                need(actual == final, 'literal dirty-state endpoint')
        _, peak = execute(new_ops, {r: F(1) for r in registers}, positive=True)
        need(str(peak) == expected['candidate']['prefix_l1'], 'primitive positive envelope')
        need(peak < 2 ** 192, 'retained local cap')
        need(denominator_depth(baseline_ops, registers) == (22 if orientation == 'forward' else 26), 'baseline dyadic grid')
        need(denominator_depth(new_ops, registers) == (24 if orientation == 'forward' else 26), 'candidate dyadic grid')
        # An independently constructed complete integer interval for each
        # one-coordinate objective. At either end all absolute-value slopes
        # point outward and no unit discounts remain, so no exterior point wins.
        incident = {h: Counter() for h in helpers}
        for e in events:
            if e[0] != 'scalar' or e[1][0] != 'add':
                continue
            g = e[1]
            total_shift = sum(sign * gauges.get(r[1], 0) for sign, r in zip((1, -1), g[1:3]) if r[0] == 'L')
            for sign, r in zip((1, -1), g[1:3]):
                if r[0] == 'L' and r[1] in incident:
                    h = r[1]
                    incident[h][g[3], g[4], total_shift - sign * gauges.get(h, 0), sign] += 1
        evaluations = 0
        for h, terms in incident.items():
            k0 = gauges.get(h, 0)
            breaks = {0} | {-sign * (valuation(F(n, d)) + shift) for n, d, shift, sign in terms}
            lo, hi = min(breaks) - 1, max(breaks) + 1
            deltas = [2 * (abs(k) - abs(k0)) + sum(count * (price(n, d, shift + sign * k) - price(n, d, shift + sign * k0))
                      for (n, d, shift, sign), count in terms.items()) for k in range(lo, hi + 1)]
            need(min(deltas) == 0, 'coordinate local optimum')
            need(deltas[0] > deltas[1] and deltas[-1] > deltas[-2], 'outward tails')
            evaluations += len(deltas)
        results[orientation] = {'literal_baseline_real': len(baseline_ops), 'literal_candidate_real': len(new_ops),
                                'dirty_cases': 3, 'integer_coordinate_evaluations': evaluations,
                                'primitive_prefix_l1': str(peak),
                                'baseline_denominator_depth': denominator_depth(baseline_ops, registers),
                                'candidate_denominator_depth': denominator_depth(new_ops, registers)}
    return {'status': 'PASS_INDEPENDENT_MANY_DYADIC_PRIMITIVES', 'orientations': results}


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True))
