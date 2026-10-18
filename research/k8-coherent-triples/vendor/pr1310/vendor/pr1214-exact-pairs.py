"""Exact two-helper dyadic gauges. Hanson Sun / OpenAI Codex, Apache-2.0.

PR1161's source loader, exact scalar replay, lowering price and single-coordinate
transform are retained byte-for-byte. The new search includes the pair interaction.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import importlib.util
import json
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXPONENTS = (-2, -1, 1, 2)  # Radius 1 + assignment seed 25 % 3.
VENDOR_FILES = frozenset(('engine.py', 'SOURCES.json', 'BASE-SELECTED.json',
                          'PROVENANCE.md', 'PROOF.md'))


def need(value, message):
    if not value:
        raise ValueError(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def predecessor(manifest=None):
    pins = manifest or json.loads((HERE / 'SOURCES.json').read_bytes())
    need(pins['base'] == '1b59b624d21924f8e3537cdc1ac52d3be6eda2fe', 'base pin')
    need(pins['pr1161_head'] == 'd210969d3158a1e6c505e41f67dd84e555c88564', 'PR1161 pin')
    need(set(pins['vendor']) == VENDOR_FILES, 'vendor inventory')
    folder = HERE / 'vendor/pr1161'
    for name, digest in pins['vendor'].items():
        need(sha((folder / name).read_bytes()) == digest, 'vendor hash: ' + name)
    spec = importlib.util.spec_from_file_location('credited_pr1161', folder / 'engine.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = ROOT  # Relocation only; the original module bytes are unchanged.
    return module


def eligible(lib, word, programs):
    helpers, _ = lib.domain(word, programs)
    wrapped = {e[2] for stream in programs.values() for e in stream
               if e[0] == 'residual_adapter'}
    return [h for h in helpers if word['start'][h] == 0 and word['final'][h] == 1
            and h not in wrapped]


def census(lib, events, helpers):
    allowed = set(helpers)
    single = {h: {k: 2 * abs(k) for k in EXPONENTS} for h in helpers}
    shared = defaultdict(Counter)

    def variable_price(unit, exponent):
        return abs(exponent) - int(unit and exponent == 0)

    for event in events:
        if event[0] != 'scalar' or event[1][0] != 'add':
            continue
        gate = event[1]
        p, e = lib.parts(lib.Q(gate[3], gate[4]))
        unit = p == 1
        target = gate[1][1] if gate[1][0] == 'L' else None
        source = gate[2][1] if gate[2][0] == 'L' else None
        need(target is None or source is None or target != source, 'distinct ADD operands')
        for helper, sign in ((target, 1), (source, -1)):
            if helper in allowed:
                for k in EXPONENTS:
                    single[helper][k] += variable_price(unit, e + sign * k) - variable_price(unit, e)
        if target in allowed and source in allowed:
            pair = tuple(sorted((target, source)))
            shared[pair][(unit, e, target == pair[0])] += 1

    rows = []
    histogram = Counter()
    winner = None
    for (a, b), edges in sorted(shared.items()):
        values = []
        for ka in EXPONENTS:
            for kb in EXPONENTS:
                correction = 0
                for (unit, e, target_first), count in edges.items():
                    kt, ks = (ka, kb) if target_first else (kb, ka)
                    correction += count * (variable_price(unit, e + kt - ks)
                                           - variable_price(unit, e + kt)
                                           - variable_price(unit, e - ks)
                                           + variable_price(unit, e))
                delta = single[a][ka] + single[b][kb] + correction
                values.append(delta)
                histogram[delta] += 1
                key = (delta, a, b, abs(ka) + abs(kb), ka, kb)
                if winner is None or key < winner:
                    winner = key
        rows.append([a, b, values])
    need(winner is not None, 'nonempty interacting-pair domain')
    d, a, b, _, ka, kb = winner
    return {'helpers': helpers, 'exponents': list(EXPONENTS), 'pairs': len(rows),
            'assignments': 16 * len(rows), 'rows': rows,
            'delta_histogram': [[d, n] for d, n in sorted(histogram.items())],
            'winner': {'helpers': [a, b], 'exponents': [ka, kb], 'delta_real': d,
                       'separate_single_delta_real': single[a][ka] + single[b][kb],
                       'interaction_delta_real': d - single[a][ka] - single[b][kb]}}


def exact_census(lib, events, helpers):
    """Affine-cell vertices certify all integer exponents; axes allow one helper."""
    allowed = set(helpers)
    incident = {h: Counter() for h in helpers}
    shared = defaultdict(Counter)
    for event in events:
        if event[0] != 'scalar' or event[1][0] != 'add':
            continue
        g = event[1]
        p, e = lib.parts(lib.Q(g[3], g[4]))
        t = g[1][1] if g[1][0] == 'L' else None
        s = g[2][1] if g[2][0] == 'L' else None
        for h, sign in ((t, 1), (s, -1)):
            if h in allowed:
                incident[h][p == 1, e, sign] += 1
        if t in allowed and s in allowed:
            a, b = sorted((t, s))
            shared[a, b][p == 1, e, t == a] += 1

    def f(unit, exponent):
        return abs(exponent) - int(unit and exponent == 0)

    cache = {}

    def single(h, k):
        if (h, k) not in cache:
            cache[h, k] = 2 * abs(k) + sum(n * (f(u, e + sign * k) - f(u, e))
                for (u, e, sign), n in incident[h].items())
        return cache[h, k]

    rows = []
    counts = Counter()
    best = None
    for a, b in combinations(helpers, 2):
        edges = shared.get((a, b), {})
        # Removing shared edges leaves vertical/horizontal slope-change lines.
        ta, tb = incident[a].copy(), incident[b].copy()
        diagonals = set()
        for (u, e, target_first), n in edges.items():
            sa = 1 if target_first else -1
            ta[u, e, sa] -= n
            tb[u, e, -sa] -= n
            diagonals.add(-sa * e)
        vertical = {0} | {-s * e for (u, e, s), n in ta.items() if n}
        horizontal = {0} | {-s * e for (u, e, s), n in tb.items() if n}
        vertices = {(k, ell) for k in vertical for ell in horizontal}
        vertices.update((k, k - d) for k in vertical for d in diagonals)
        vertices.update((ell + d, ell) for ell in horizontal for d in diagonals)
        pair_best = None
        evaluated = []
        for ka, kb in sorted(vertices):
            correction = 0
            for (u, e, target_first), n in edges.items():
                kt, ks = (ka, kb) if target_first else (kb, ka)
                correction += n * (f(u, e + kt - ks) - f(u, e + kt) - f(u, e - ks) + f(u, e))
            delta = single(a, ka) + single(b, kb) + correction
            key = (delta, abs(ka) + abs(kb), ka, kb)
            evaluated.append([ka, kb, delta])
            if pair_best is None or key < pair_best:
                pair_best = key
        delta, _, ka, kb = pair_best
        rows.append([a, b, len(vertices), delta, ka, kb, sha(canonical(evaluated))])
        counts['pairs'] += 1
        counts['interacting_pairs' if edges else 'separable_pairs'] += 1
        counts['vertices'] += len(vertices)
        key = (delta, a, b, abs(ka) + abs(kb), ka, kb)
        if best is None or key < best:
            best = key
    d, a, b, _, ka, kb = best
    return {'helpers': helpers, 'domain': 'all integer exponent pairs, including zero',
            **counts, 'rows': rows,
            'winner': {'helpers': [a, b], 'exponents': [ka, kb], 'delta_real': d,
                       'separate_single_delta_real': single(a, ka) + single(b, kb),
                       'interaction_delta_real': d - single(a, ka) - single(b, kb)}}


def construct(lib, word, events, winner):
    result = events
    for helper, exponent in zip(winner['helpers'], winner['exponents']):
        result = lib.transform(result, word, helper, exponent)
    return result


def compute():
    lib = predecessor()
    word, programs, _, _ = lib.load()
    helpers = eligible(lib, word, programs)
    certificate = {'base': '1b59b624d21924f8e3537cdc1ac52d3be6eda2fe',
                   'seed': 25, 'scope': 'all integer gauges on at most two cold/FULL unwrapped helpers',
                   'orientations': {}}
    witnesses = {}
    for orientation, events in programs.items():
        pilot = census(lib, events, helpers)
        result = exact_census(lib, events, helpers)
        result['bounded_pilot'] = {k: v for k, v in pilot.items() if k != 'rows'}
        candidate = construct(lib, word, events, result['winner'])
        result['candidate_sha256'] = sha(canonical(candidate))
        result['baseline_endpoint'] = lib.replay(events, orientation)
        result['candidate_endpoint'] = lib.replay(candidate, orientation)
        result['prices'] = {}
        for mode in ('copy-init', 'horner'):
            before = lib.invoice(events, mode)
            after = lib.invoice(candidate, mode)
            need(before['paid_profile'] == after['paid_profile'], 'unchanged recursive profile')
            if mode == 'copy-init':
                need(after['real_primitives'] - before['real_primitives'] == result['winner']['delta_real'],
                     'search versus complete invoice')
            result['prices'][mode] = {'before': before, 'after': after,
                                     'saving_complex': before['complex_primitives'] - after['complex_primitives']}
        certificate['orientations'][orientation] = result
        witnesses[orientation] = candidate
    certificate['status'] = 'PASS_K8_PAIR_DYADIC_CENSUS'
    return certificate, witnesses


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result, programs = compute()
    pair_rows = {o: row.pop('rows') for o, row in result['orientations'].items()}
    for orientation, rows in pair_rows.items():
        result['orientations'][orientation]['pair_rows_sha256'] = sha(canonical(rows))
    if args.write:
        (HERE / 'CERTIFICATE.json').write_bytes(canonical(result) + b'\n')
        (HERE / 'PAIR-CENSUS.json.gz').write_bytes(gzip.compress(canonical(pair_rows), mtime=0))
        (HERE / 'PROGRAMS.json.gz').write_bytes(gzip.compress(canonical(programs), mtime=0))
    else:
        need(canonical(result) == canonical(json.loads((HERE / 'CERTIFICATE.json').read_bytes())),
             'complete certificate mismatch')
        need(canonical(programs) == canonical(json.loads(gzip.decompress((HERE / 'PROGRAMS.json.gz').read_bytes()))),
             'complete candidate program mismatch')
        need(canonical(pair_rows) == canonical(json.loads(gzip.decompress((HERE / 'PAIR-CENSUS.json.gz').read_bytes()))),
             'complete pair census mismatch')
    print(result['status'])
    for orientation, row in result['orientations'].items():
        print(orientation, 'pairs', row['pairs'], 'vertices', row['vertices'],
              'winner', row['winner'], 'saving_complex', row['prices']['copy-init']['saving_complex'])


if __name__ == '__main__':
    main()
