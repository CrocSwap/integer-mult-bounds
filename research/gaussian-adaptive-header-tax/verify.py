#!/usr/bin/env python3
"""Exact source-bound adaptive Gaussian controls; no numerical entropy oracle."""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
from itertools import combinations
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_NAMES = ('research/gaussian-clique-copy-bound/geometry.py',
                'research/gaussian-clique-copy-bound/verify.py',
                'research/gaussian-clique-copy-bound/certificate.json',
                'research/gaussian-clique-copy-bound/PROOF.md',
                'research/gaussian-nonlinear-copy-floor/PROOF.md',
                'research/hurwitz-adaptive-routing/PROOF.md')


def require(value, message):
    if not value:
        raise ValueError(message)


def pins():
    data = (HERE / 'SOURCES.json').read_bytes()
    manifest = json.loads(data)
    inputs = [x for x in manifest['files'] if x['usage'] == 'input']
    require({x['path'] for x in inputs} == set(SOURCE_NAMES), 'source inventory')
    for item in inputs:
        content = (ROOT / item['path']).read_bytes()
        require(hashlib.sha256(content).hexdigest() == item['sha256'], 'source SHA256')
        blob = b'blob ' + str(len(content)).encode() + b'\0' + content
        require(hashlib.sha1(blob).hexdigest() == item['git_blob'], 'source Git blob')
    return hashlib.sha256(data).hexdigest()


def geometry():
    env = os.environ.copy()
    env.pop('PYTHONOPTIMIZE', None)
    result = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'geometry_check.py')],
                            env=env, capture_output=True, check=True, timeout=300)
    return json.loads(result.stdout)


def rank(rows):
    """Independent Fraction elimination; never imports retained rank code."""
    rows = [list(map(Q, row)) for row in rows]
    n = 0
    for col in range(len(rows[0]) if rows else 0):
        pivot = next((i for i in range(n, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[n], rows[pivot] = rows[pivot], rows[n]
        divisor = rows[n][col]
        rows[n] = [x / divisor for x in rows[n]]
        for i in range(n + 1, len(rows)):
            factor = rows[i][col]
            rows[i] = [a - factor * b for a, b in zip(rows[i], rows[n])]
        n += 1
    return n


def J(v):
    return tuple(x for i in range(0, 8, 2) for x in (-v[i + 1], v[i]))


def charge(lines, sources, readers):
    a = [v for i in sources for v in (lines[i], J(lines[i]))]
    r = [v for i in readers for v in (lines[i], J(lines[i]))]
    n = rank([[sum(x * y for x, y in zip(u, v)) for v in a] for u in r])
    require(n % 2 == 0, 'odd rational Gaussian pairing rank')
    return n // 2


def prefix(words):
    words = set(words)
    require(all(set(w) <= {'0', '1'} for w in words), 'nonbinary codeword')
    require(all(not b.startswith(a) for a in words for b in words if a != b),
            'non-prefix codebook')
    require(sum((Q(1, 2 ** len(w)) for w in words), Q()) <= 1, 'Kraft failure')


def frames(graph):
    selected, used = [], set()
    for frame in combinations(range(60), 4):
        if used.intersection(frame):
            continue
        mask = sum(1 << t for t in frame)
        if all(not (graph[t] & mask) for t in frame):
            selected.append(list(frame))
            used.update(frame)
            if len(selected) == 3:
                return selected
    raise ValueError('three disjoint orthogonal frames missing')


def fixture(frame):
    ports = sum(frame, [])
    first = frame[0] + frame[1]
    branch = {0: [(first, first), (frame[2], frame[2])],
              1: [(frame[2], frame[2])]}
    table = []
    for word in range(4096):
        z = [(word >> (4 * f) & 15).bit_count() % 2 for f in range(3)]
        m = z[0] & z[1]
        pair = {(0, 0): '0', (0, 1): '10', (1, 0): '11'}
        values = [str(z[2])] if m else [pair[z[0], z[1]], str(z[2])]
        table.append((m, tuple(values)))
    return {'ports': ports, 'branches': branch, 'headers': {0: '0', 1: '1'}, 'table': table}


_prices = {}


def charge_cache(lines, a, r):
    key = tuple(map(tuple, lines)), tuple(a), tuple(r)
    if key not in _prices:
        _prices[key] = charge(lines, a, r)
    return _prices[key]


def check_code(code, lines, graph, cliques, header_price=4):
    ports, branch, table = code['ports'], code['branches'], code['table']
    n, size = len(ports), 1 << len(ports)
    require(len(table) == size and len(set(ports)) == n, 'input domain')
    require(header_price == charge_cache(lines, range(60), range(60)) == 4,
            'full-space header tariff')
    prefix(code['headers'].values())
    require(len(set(code['headers'].values())) == len(code['headers']), 'ambiguous header')
    local = {p: i for i, p in enumerate(ports)}
    costs, lengths, counts = [], [], Counter()
    source_maps, books = {}, {}
    for word, (m, values) in enumerate(table):
        require(m in code['headers'] and m in branch, 'undeclared header')
        require(len(values) == len(branch[m]), 'payload count')
        counts[m] += 1
        lengths.append(len(code['headers'][m]))
        cost = header_price * lengths[-1]
        for j, ((a, r), value) in enumerate(zip(branch[m], values)):
            require(set(a + r) <= set(range(60)), 'invalid support')
            mask = sum(1 << local[t] for t in a if t in local)
            key = m, j, word & mask
            require(key not in source_maps or source_maps[key] == value, 'undeclared source')
            source_maps[key] = value
            books.setdefault((m, j), set()).add(value)
            cost += charge_cache(lines, a, r) * len(value)
        costs.append(cost)
    for words in books.values():
        prefix(words)
    # Reader-conflict check uses no producer decoder or assumed inverse.
    observations = [{} for _ in ports]
    side_masks = [sum(1 << k for k, q in enumerate(ports)
                      if q != p and not (graph[p] >> q & 1)) for p in ports]
    for word, (m, values) in enumerate(table):
        for t, p in enumerate(ports):
            received = tuple(values[j] for j, (_, readers) in enumerate(branch[m]) if p in readers)
            key = m, word & side_masks[t], received
            bit = word >> t & 1
            require(key not in observations[t] or observations[t][key] == bit, 'receiver conflict')
            observations[t][key] = bit
    projected = 0
    for clique in cliques:
        inside = sum(1 << i for i, p in enumerate(ports) if clique >> p & 1)
        outside, seen = (size - 1) ^ inside, {}
        relevant_indices = {m: [j for j, (a, r) in enumerate(pairs)
                                if any(clique >> p & 1 for p in a)
                                and any(clique >> p & 1 for p in r)]
                            for m, pairs in branch.items()}
        for word, (m, values) in enumerate(table):
            relevant = tuple(values[j] for j in relevant_indices[m])
            key = word & outside, m, relevant
            require(key not in seen or seen[key] == word & inside, 'conditional collision')
            seen[key] = word & inside
            projected += 1
    average, length = Q(sum(costs), size), Q(sum(lengths), size)
    concentrated = max(sum(clique >> p & 1 for p in ports) for clique in cliques)
    floor = max(Q(2, 3) * (n + length), concentrated + 3 * length)
    require(average >= floor, 'header-tax bound')
    return {'inputs': size, 'receiver_checks': size * n, 'conditional_checks': projected,
            'header_counts': {str(k): v for k, v in sorted(counts.items())},
            'average_cost': str(average), 'header_length': str(length),
            'tax_floor': str(floor), 'cost_histogram': {str(k): v for k, v in sorted(Counter(costs).items())},
            'payload_codebooks': {str(k): sorted(v) for k, v in sorted(books.items())},
            'transcript_sha256': hashlib.sha256(json.dumps(table).encode()).hexdigest()}


def rejection(function, message):
    try:
        function()
    except ValueError as error:
        require(message in str(error), 'wrong rejection: ' + str(error))
        return
    raise ValueError('negative control accepted: ' + message)


def calculate():
    source_hash = pins()
    geo = geometry()
    lines, graph = geo['lines'], geo['graph']
    cliques = [x for x in geo['cliques'] if x.bit_count() == 12]
    require(len(lines) == 60 and len(cliques) == 640, 'geometry size')
    require([sum(q >> t & 1 for q in cliques) for t in range(60)] == [128] * 60,
            'weighted clique incidence')
    require(Q(640, 192) == Q(10, 3) and 4 - Q(640, 192) == Q(2, 3), 'header gap')
    frame = frames(graph)
    code = fixture(frame)
    result = check_code(code, lines, graph, cliques)
    require(result['average_cost'] == '13' and result['tax_floor'] == '26/3', 'fixture cost')
    require(code['table'][0][0] ^ code['table'][1][0] ^ code['table'][16][0]
            ^ code['table'][17][0] == 1, 'header is not nonlinear')
    bad = deepcopy(code)
    bad['table'][0] = (0, ('0', '1'))
    rejection(lambda: check_code(bad, lines, graph, cliques), 'undeclared source')
    bad = deepcopy(code)
    bad['branches'][0][0] = ([], bad['branches'][0][0][1])
    rejection(lambda: check_code(bad, lines, graph, cliques), 'undeclared source')
    bad = deepcopy(code)
    bad['table'] = [(m, tuple('0' if j == len(v) - 1 else x for j, x in enumerate(v)))
                    for m, v in bad['table']]
    rejection(lambda: check_code(bad, lines, graph, cliques), 'receiver conflict')
    rejection(lambda: check_code(code, lines, graph, cliques, header_price=0), 'header tariff')
    # Correct parity code with free termination violates the claimed floor.
    frame_price = charge_cache(lines, frame[0], frame[0])
    require(frame_price == 4, 'orthogonal frame price')
    free_end = ['' if w.bit_count() % 2 == 0 else '1' for w in range(16)]
    for w, encoded in enumerate(free_end):
        parity = int(encoded == '1')
        for t in range(4):
            require(parity ^ ((w & (15 ^ (1 << t))).bit_count() % 2) == (w >> t & 1),
                    'termination boundary decode')
    require(Q(sum(map(len, free_end)) * frame_price, 16) == 2 < Q(8, 3), 'termination boundary')
    rejection(lambda: prefix(free_end), 'non-prefix')
    # Extra nonorthogonal side information permits an inadmissible parity code.
    clique_ports = [t for t in range(60) if cliques[0] >> t & 1]
    require(len(clique_ports) == 12, 'clique boundary size')
    def legal_side():
        require(all(not (graph[p] >> q & 1) for p in clique_ports
                    for q in clique_ports if p != q), 'illegal side information')
    rejection(legal_side, 'illegal side information')
    for w in range(4096):
        parity = w.bit_count() % 2
        for t in range(12):
            require(parity ^ ((w & (4095 ^ (1 << t))).bit_count() % 2) == (w >> t & 1),
                    'illegal-side boundary decode')
    require(4 < 12, 'illegal-side boundary cost')
    # Valid prefix-free variable header violates a false pointwise strengthening.
    headers = ['0' if w == 0 else '1' + format(w, '012b') for w in range(4096)]
    prefix(headers)
    require(len(set(headers)) == 4096 and 4 * len(headers[0]) == 4 < 8, 'pointwise boundary')
    mean_header = Q(sum(map(len, headers)), 4096)
    require(4 * mean_header >= Q(2, 3) * (12 + mean_header), 'variable header tax')
    return {'schema': 1, 'status': 'scoped expected-cost theorem; no supplier or kappa',
            'sources_sha256': source_hash, 'retained_geometry': geo['receipt'],
            'frames': frame, 'full_header_price': 4, 'weighted_cliques': 640,
            'incidence_per_port': 128, 'header_tax': '2/3', 'adaptive_fixture': result,
            'unpaid_termination_cost': '2', 'unpaid_termination_floor': '8/3',
            'pointwise_boundary_minimum': 4, 'pointwise_boundary_mean': str(4 * mean_header),
            'controls': 6}


def same_receipt(actual, expected):
    """Keep discrete proof counts distinct from JSON booleans and floats."""
    if type(actual) is not type(expected):
        return False
    if isinstance(actual, dict):
        return actual.keys() == expected.keys() and all(
            same_receipt(value, expected[key]) for key, value in actual.items())
    if isinstance(actual, list):
        return len(actual) == len(expected) and all(
            same_receipt(a, b) for a, b in zip(actual, expected))
    return actual == expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    if args.write:
        require(not args.write.exists(), 'output exists')
    result = calculate()
    expected = HERE / 'RESULT.json'
    if expected.exists():
        require(same_receipt(result, json.loads(expected.read_text())), 'receipt mismatch')
    else:
        require(args.write is not None, 'missing committed receipt')
    if args.write:
        with args.write.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    print('PASS_GAUSSIAN_ADAPTIVE_HEADER_TAX inputs=4096 receiver_checks=49152 cliques=640 controls=6')


if __name__ == '__main__':
    main()
