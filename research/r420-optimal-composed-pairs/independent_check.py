#!/usr/bin/env python3
"""Column-incidence proof check, independent of verify.py and matching solvers.

Sagar Thakrar, substantial OpenAI Codex assistance. Apache-2.0.
This checks the frozen matching class, not geometry or hosted execution.
"""
import copy
import gzip
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(value, message):
    if not value:
        raise ValueError(message)


def check(certificate, helper_recipe, word):
    # Each integer holds a helper column's 120 target coefficients.
    cols = [0]*420
    for frame, destination, sources in word['D']:
        require(frame == 0 and 120 <= destination < 240, 'input D')
        for source in sources:
            cols[source-240] ^= 1 << (destination-120)
    original = cols[:]
    used = set()
    for pair in helper_recipe['pairs']:
        a, b = pair['dst']-240, pair['src']-240
        require(a != b and 0 <= a < 420 and 0 <= b < 420 and not ({a, b} & used), 'helper domain')
        cols[b] ^= cols[a]
        used.update((a, b))
    counts = [0]*120
    common = [[0]*120 for _ in range(120)]
    for column in cols:
        support = [t for t in range(120) if column & (1 << t)]
        for a in support:
            counts[a] += 1
            for b in support:
                common[a][b] += 1
    q = certificate['doubled_vertex_prices']
    require(len(q) == 120 and all(type(x) is int and x >= 0 for x in q), 'dual domain')
    for a, b in itertools.combinations(range(120), 2):
        # This incidence formula avoids row-set symmetric differences.
        weight = max(0, 2*common[a][b]-counts[a]-2, 2*common[a][b]-counts[b]-2)
        require(q[a]+q[b] >= 2*weight, 'edge inequality')
    used, saving = set(), 0
    transformed = cols[:]
    pairs = certificate['pairs']
    for source, destination, claimed in pairs:
        a, b = source-120, destination-120
        require(0 <= a < 120 and 0 <= b < 120 and a != b and not ({a, b} & used), 'target domain')
        actual = 2*common[a][b]-counts[a]-2
        require(actual == claimed and actual > 0, 'oriented saving')
        used.update((a, b)); saving += actual
        for i, column in enumerate(transformed):
            if column & (1 << a):
                transformed[i] ^= 1 << b
    require(sum(q) == 2*saving == 2884 and certificate['gain'] == saving, 'tight objective')
    # Direct literal Boolean inputs cover all 120 dirty targets and 420 helpers.
    for input_column in range(540):
        targets = [int(input_column == t) for t in range(120)]
        helpers = [int(input_column == 120+h) for h in range(420)]
        for pair in helper_recipe['pairs']:
            helpers[pair['dst']-240] ^= helpers[pair['src']-240]
        for a, b, _ in pairs:
            targets[b-120] ^= targets[a-120]
        for h, column in enumerate(transformed):
            if helpers[h]:
                for t in range(120):
                    targets[t] ^= (column >> t) & 1
        for a, b, _ in reversed(pairs):
            targets[b-120] ^= targets[a-120]
        for pair in reversed(helper_recipe['pairs']):
            helpers[pair['dst']-240] ^= helpers[pair['src']-240]
        for t in range(120):
            expected = int(input_column == t)
            if input_column >= 120:
                expected ^= (original[input_column-120] >> t) & 1
            require(targets[t] == expected, 'target column')
        require(helpers == [int(input_column == 120+h) for h in range(420)], 'helper return')
    reads = sum(column.bit_count() for column in transformed)
    require(2*201 + 2*len(pairs) + reads == 11546, 'complete D cost')
    return saving


def main():
    manifest = json.loads((HERE/'SOURCES.json').read_text())
    raw = (ROOT/'research/e8-bit-r420/data/bitE8mut-r420.json.gz').read_bytes()
    payload = gzip.decompress(raw)
    pin = manifest['base_files']['research/e8-bit-r420/data/bitE8mut-r420.json.gz']
    require(hashlib.sha256(payload).hexdigest() == pin['sha256'], 'original word pin')
    helper_bytes = (HERE/'vendor/pr694-recipe.json').read_bytes()
    require(hashlib.sha256(helper_bytes).hexdigest() ==
            manifest['imported']['vendor/pr694-recipe.json']['sha256'], 'helper recipe pin')
    word, helpers = json.loads(payload), json.loads(helper_bytes)
    cert = json.loads((HERE/'OPTIMUM.json').read_text())
    check(cert, helpers, word)
    controls = []
    mutants = [copy.deepcopy(cert) for _ in range(4)]
    mutants[0]['doubled_vertex_prices'] = [0]*120
    mutants[1]['doubled_vertex_prices'][11] += 1
    mutants[2]['pairs'].append(mutants[2]['pairs'][0])
    mutants[3]['pairs'][0][2] += 1
    for i, mutant in enumerate(mutants):
        try:
            check(mutant, helpers, word)
        except ValueError:
            controls.append(i)
        else:
            raise ValueError('certificate mutation accepted')
    print('PASS_R420_COLUMN_MATCHING optimum=1442 coefficients=50400 edges=7140 '
          'boolean_columns=540 D_ADDs=11546 controls=4')


if __name__ == '__main__':
    main()
