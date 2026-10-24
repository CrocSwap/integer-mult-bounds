"""Rebuild off-pattern spaces from direct generator combinations."""
from itertools import combinations, permutations
from pathlib import Path
from math import comb
import hashlib
import json

BASE = Path(__file__).resolve().parents[1]
OFF_POSITIONS = [(i, j) for i in range(4) for j in range(4) if i != j]


def span(generators):
    out = {0}
    for value in generators:
        out |= {x ^ value for x in tuple(out)}
    return tuple(sorted(out))


def matrix(value):
    return sum(((value >> k) & 1) << (4 * i + j)
               for k, (i, j) in enumerate(OFF_POSITIONS))


def connected(space):
    edges = 0
    for value in space:
        edges |= value
    # Boolean matrix closure, independent of the source's vertex scans.
    paths = [[i == j for j in range(4)] for i in range(4)]
    for k, (i, j) in enumerate(OFF_POSITIONS):
        paths[i][j] = bool(edges >> k & 1)
    for k in range(4):
        for i in range(4):
            for j in range(4):
                paths[i][j] |= paths[i][k] and paths[k][j]
    return all(all(row) for row in paths)


def main():
    source = json.loads((BASE / 'independent/off-pattern-spaces.json').read_text())
    projectors = []
    for x in range(1, 16):
        for y in range(1, 16):
            if sum(((x >> i) & 1) * ((y >> i) & 1) for i in range(4)) % 2:
                off = sum((((x >> i) & 1) * ((y >> j) & 1)) << k
                          for k, (i, j) in enumerate(OFF_POSITIONS))
                projectors.append((x, y, off))
    patterns = sorted({off for x, y, off in projectors} - {0})
    maps = []
    for perm in permutations(range(4)):
        destinations = [OFF_POSITIONS.index((perm[i], perm[j]))
                        for i, j in OFF_POSITIONS]
        maps.append([sum(((value >> k) & 1) << destinations[k] for k in range(12))
                     for value in range(4096)])
    rows = []
    for dimension in (1, 2, 3):
        # Direct combinations differ from the producer's iterative closure.
        spaces = {space for basis in combinations(patterns, dimension)
                  if len(space := span(basis)) == 1 << dimension}
        strong = {s for s in spaces if connected(s)}
        unseen = set(strong)
        representatives = set()
        while unseen:
            chosen = next(iter(unseen))
            orbit = {tuple(sorted(mapping[v] for v in chosen)) for mapping in maps}
            assert orbit <= strong
            unseen -= orbit
            representative = min(tuple(sorted(matrix(v) for v in s)) for s in orbit)
            representatives.add(representative)
        recorded = source['levels'][dimension - 1]
        assert len(spaces) == recorded['spaces']
        assert len(strong) == recorded['irreducible_spaces']
        expected = {tuple(r['space']): r['projectors'] for r in recorded['representatives']}
        assert representatives == set(expected)
        for space in representatives:
            actual = [[x, y] for x, y, off in projectors if matrix(off) in space]
            assert actual == expected[space]
        payload = json.dumps(sorted(representatives), separators=(',', ':')).encode()
        rows.append(dict(dimension=dimension, spaces=len(spaces),
                         strongly_connected_spaces=len(strong), classes=len(representatives),
                         representatives_sha256=hashlib.sha256(payload).hexdigest(),
                         eight_multisets=sum(comb(len(pool)+7, 8) for pool in expected.values())))
    result = dict(status='PASS_INDEPENDENT_OFF_PATTERN_CATALOGUE', projectors=len(projectors),
                  nonzero_off_patterns=len(patterns), levels=rows)
    Path(__file__).with_name('OFF-CATALOGUE-RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
