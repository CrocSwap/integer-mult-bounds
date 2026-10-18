"""Independent integer-grid and literal-primitive check; Hanson Sun, OpenAI Codex.

Apache-2.0. Imports Sagar Thakrar's pinned lowerer. Does not import verify.py
or PR1161's engine, search, transform, price, invoice, or replay implementation.
"""
from collections import Counter, defaultdict
from fractions import Fraction as F
from functools import lru_cache
import gzip
import hashlib
import importlib.util
from itertools import combinations
import json
from pathlib import Path
import random
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(value, message):
    if not value:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def run():
    pins = json.loads((HERE / 'vendor/pr1161/SOURCES.json').read_bytes())
    for name, expected in pins['files'].items():
        data = (ROOT / name).read_bytes()
        need(digest(data if name.endswith('.gz') else data.replace(b'\r\n', b'\n')) == expected,
             'source hash: ' + name)
    with tarfile.open(ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz') as archive:
        def read(name):
            data = archive.extractfile('candidate/strict/global8/base/providers/gauge44/' + name).read()
            need(digest(data) == pins['archive_members']['slots/local/' + name], 'archive member')
            return json.loads(gzip.decompress(data))
        word = read('CANONICAL-WORD.json.gz')
        programs = read('LOCAL-PROGRAMS.json.gz')
    candidate = json.loads(gzip.decompress((HERE / 'PROGRAMS.json.gz').read_bytes()))
    certificate = json.loads((HERE / 'CERTIFICATE.json').read_bytes())
    pair_rows = json.loads(gzip.decompress((HERE / 'PAIR-CENSUS.json.gz').read_bytes()))
    for orientation, rows in pair_rows.items():
        raw = json.dumps(rows, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
        need(digest(raw) == certificate['orientations'][orientation]['pair_rows_sha256'], 'census binding')
    spec = importlib.util.spec_from_file_location('sagar_thakrar_lower', ROOT / 'research/complex-dyadic-lowering/lower.py')
    lower = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lower)
    helpers = set(range(224, 704)) - set(word['centers'])
    for events in programs.values():
        for event in events:
            if event[0] == 'residual_adapter':
                helpers.discard(event[2])
            if event[0] == 'scalar' and event[1][0] in ('copy', 'clear'):
                for register in event[1][1:]:
                    if isinstance(register, list) and register[0] == 'L':
                        helpers.discard(register[1])
    helpers = sorted(h for h in helpers if word['start'][h] == 0 and word['final'][h] == 1)
    need(len(helpers) == 237, 'exact physical helper domain')
    helper_set = set(helpers)
    results = {}

    @lru_cache(None)
    def literal_cost(numerator, denominator, shift):
        q = F(numerator, denominator) * F(2) ** shift
        return len(lower.lower(['add', ['L', 0], ['L', 1], q.numerator, q.denominator]))

    def valuation(q):
        exponent = 0
        q = abs(q)
        while q.denominator > 1:
            q *= 2
            exponent -= 1
        while q.numerator % 2 == 0:
            q /= 2
            exponent += 1
        return exponent

    for orientation, events in programs.items():
        by_helper = {h: Counter() for h in helpers}
        by_pair = defaultdict(Counter)
        max_valuation = 0
        for event in events:
            if event[0] != 'scalar' or event[1][0] != 'add':
                continue
            gate = event[1]
            t, s = gate[1:3]
            n, d = gate[3:5]
            q = F(n, d)
            max_valuation = max(max_valuation, abs(valuation(q)))
            for register, sign in ((t, 1), (s, -1)):
                if register[0] == 'L' and register[1] in helper_set:
                    by_helper[register[1]][n, d, sign] += 1
            if t[0] == s[0] == 'L' and t[1] in helper_set and s[1] in helper_set:
                a, b = sorted((t[1], s[1]))
                by_pair[a, b][n, d, t[1] == a] += 1

        # Every vertex of k=c, ell=c, k-ell=c lies inside [-2M,2M]^2
        # when all nonzero intercepts have magnitude at most M. Search the
        # ENTIRE integer square, plus its outer ring; no vertex routine is used.
        radius = 2 * max_valuation + 1
        grid = range(-radius, radius + 1)
        singles = {}
        for h, terms in by_helper.items():
            singles[h] = {k: 2 * abs(k) + sum(count * (literal_cost(n, d, sign * k) - literal_cost(n, d, 0))
                for (n, d, sign), count in terms.items()) for k in grid}
        rows = {(row[0], row[1]): row for row in pair_rows[orientation]}
        need(set(rows) == set(combinations(helpers, 2)), 'complete pair inventory')
        need(certificate['orientations'][orientation]['helpers'] == helpers, 'helper domain equality')
        grid_evaluations = 0
        minima = []
        for a, b in combinations(helpers, 2):
            edges = by_pair.get((a, b), {})
            if not edges:
                # Independent separable enumeration, not Cartesian vertex enumeration.
                ka = min(grid, key=lambda k: (singles[a][k], abs(k), k))
                kb = min(grid, key=lambda k: (singles[b][k], abs(k), k))
                best = (singles[a][ka] + singles[b][kb], abs(ka) + abs(kb), ka, kb)
            else:
                # Tabulate the shared ADD price directly from primitive lengths.
                coupled = {difference: sum(count * literal_cost(n, d, difference if target_a else -difference)
                    for (n, d, target_a), count in edges.items())
                    for difference in range(-2 * radius, 2 * radius + 1)}
                baseline_shared = coupled[0]
                solo_a = {k: sum(count * literal_cost(n, d, k if target_a else -k)
                    for (n, d, target_a), count in edges.items()) for k in grid}
                solo_b = {k: sum(count * literal_cost(n, d, -k if target_a else k)
                    for (n, d, target_a), count in edges.items()) for k in grid}
                best = min((singles[a][ka] + singles[b][kb] + coupled[ka - kb]
                            - solo_a[ka] - solo_b[kb] + baseline_shared,
                            abs(ka) + abs(kb), ka, kb) for ka in grid for kb in grid)
                grid_evaluations += len(grid) ** 2
            need(best[0] == rows[a, b][3], 'pair optimum: ' + str((a, b)))
            # Primary tie choice is among vertices; an interior grid point may tie.
            minima.append((best[0], a, b))
        selected = certificate['orientations'][orientation]['winner']
        need(min(minima) == (selected['delta_real'], *selected['helpers']), 'global minimum')
        new_events = candidate[orientation]
        need([e for e in events if e[0] != 'scalar'] == [e for e in new_events if e[0] != 'scalar'],
             'non-scalar event identity')
        old_ops = [op for e in events if e[0] == 'scalar' for op in lower.lower(e[1])]
        new_ops = [op for e in new_events if e[0] == 'scalar' for op in lower.lower(e[1])]
        price = certificate['orientations'][orientation]['prices']['copy-init']
        need(len(old_ops) == price['before']['real_primitives'], 'baseline literal count')
        need(len(new_ops) == price['after']['real_primitives'], 'candidate literal count')
        need(len(new_ops) - len(old_ops) == selected['delta_real'], 'literal saving')
        rng = random.Random(25 + (orientation == 'backward'))
        all_registers = [('L', i) for i in range(704)] + [('C', i) for i in range(8)] + [('W', 0)]
        for case in range(3):
            original = {r: F(rng.randrange(-10000, 10000), 2 ** rng.randrange(4)) for r in all_registers}
            if case == 1:
                original.update({('L', i): F((-1) ** i * (i + 1) ** 3, 8) for i in range(224, 704)})
            if case == 2:
                original.update({('L', i): F(0) for i in range(224)})
            expected = original.copy()
            for i in range(112):
                if orientation == 'forward':
                    expected['L', 112 + i] += original['L', i]
                else:
                    expected['L', i] -= original['L', 112 + i]
            for i in range(8):
                expected['C', i] = F(0)
            expected['W', 0] = F(0)
            for operations in (old_ops, new_ops):
                state = original.copy()
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
                        state[target] = -state[target]
                    elif tag == 'add':
                        state[target] += state[op[2]]
                    elif tag == 'subtract':
                        state[target] -= state[op[2]]
                    else:
                        raise ValueError('unknown primitive')
                need(state == expected, 'literal dirty-state endpoint')
        results[orientation] = {'pairs': len(rows), 'interacting_pairs': len(by_pair),
            'valuation_bound': max_valuation, 'grid_radius': radius,
            'grid_evaluations': grid_evaluations, 'exact_dirty_cases': 3,
            'baseline_real_primitives': len(old_ops), 'candidate_real_primitives': len(new_ops)}
    return {'status': 'PASS_INDEPENDENT_PAIR_GRID_AND_PRIMITIVES', 'orientations': results}


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True))
