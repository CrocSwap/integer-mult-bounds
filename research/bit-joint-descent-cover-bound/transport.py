"""Exact support and span checks for the selected BIT owned descents."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys

PIN = '51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78'


def basis(values):
    out = {}
    for value in values:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in out:
                out[pivot] = value
                break
            value ^= out[pivot]
    return out


def residue(value, pivots):
    while value and value.bit_length() - 1 in pivots:
        value ^= pivots[value.bit_length() - 1]
    return value


def rational_rank(matrix):
    rows = [list(map(Q, row)) for row in matrix]
    rank = 0
    for column in range(8):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [x / scale for x in rows[rank]]
        for i in range(len(rows)):
            if i != rank and rows[i][column]:
                scale = rows[i][column]
                rows[i] = [x - scale * y for x, y in zip(rows[i], rows[rank], strict=True)]
        rank += 1
    return rank


def main(path):
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == PIN
    word = json.loads(gzip.decompress(raw))
    n = word['public']
    frames = {int(i): frame for i, frame in word['frames'].items()}
    lines = [tuple(map(Q, frames[f]['B'][0])) for f in word['start'][:111]]
    assert len(set(word['start'][:111])) == 111
    allowed = {}
    maxima = Counter()
    for f, frame in frames.items():
        annihilator = [tuple(map(Q, row)) for row in frame['A']]
        subspace = [tuple(map(Q, row)) for row in frame['B']]
        assert len(subspace) == rational_rank(subspace) == frame['dim']
        assert len(annihilator) == rational_rank(annihilator) == 8 - frame['dim']
        assert all(sum(x*y for x,y in zip(a,b,strict=True)) == 0
                   for a in annihilator for b in subspace)
        mask = sum(1 << i for i, line in enumerate(lines)
                   if all(sum(x*y for x,y in zip(line, row)) == 0 for row in annihilator))
        allowed[f] = mask
        maxima[frame['dim']] = max(maxima[frame['dim']], mask.bit_count())
    assert maxima == {0: 0, 1: 1, 2: 2, 4: 12, 6: 30, 7: 62, 8: 111}
    capacities = [0]
    for cap in range(1, 7):
        capacities.append(max(capacities[cap-d]+maximum for d,maximum in maxima.items() if 0<d<=cap))
    assert capacities[-1] == 30

    cur = word['start'] + [None]*word['owned_fields']
    rows = [1 << r for r in range(n)] + [None]*word['owned_fields']
    summaries, first_use = {}, {}
    public_moves = 0
    for i, event in enumerate(word['program']):
        op, r, *args = event
        if op == 'MOVE':
            a,b = args
            assert cur[r] == a
            if r < n:
                assert frames[a]['dim'] < frames[b]['dim'] and allowed[a] & ~allowed[b] == 0
                public_moves += 1
            else:
                assert r not in summaries and frames[a]['dim'] == 7 and b == 0
                summaries[r] = rows[r] & ((1 << 111)-1)
            cur[r] = b
        elif op == 'ADD':
            s,f = args
            assert cur[r] == cur[s] == f
            if s in summaries and s not in first_use:
                peers = basis(v for j,v in enumerate(rows) if j != s and cur[j] == 0 and v)
                assert residue(rows[s], peers)
                first_use[s] = {'event': i, 'available_rank': len(peers)}
            rows[r] ^= rows[s]
        elif op == 'INIT':
            assert cur[r] is None
            cur[r],rows[r] = args[0],0
        elif op == 'CLEAR':
            assert cur[r] == args[0]
            cur[r] = rows[r] = None
        else:
            assert op == 'SWAP'
            s = args[0]
            cur[r],cur[s] = cur[s],cur[r]
            rows[r],rows[s] = rows[s],rows[r]
    assert cur == word['final'] + [None]*word['owned_fields']
    assert set(summaries) == set(first_use) == set(range(770,779))
    code = [0]
    for value in summaries.values():
        code += [x ^ value for x in code[:]]
    assert len(set(code)) == 512
    duplicate = list(summaries.values())
    duplicate[0] = duplicate[1]
    bad_code = [0]
    for value in duplicate:
        bad_code += [x ^ value for x in bad_code[:]]
    assert len(set(bad_code)) == 256
    weights = Counter(x.bit_count() for x in code[1:])
    assert min(weights) == 48 > capacities[-1]
    print(json.dumps(dict(status='PASS_OWNED_DESCENT_TRANSPORT_BOUND', word_sha256=PIN,
                          public_monotone_moves=public_moves, first_use=first_use,
                          max_catalogue_lines_by_rank=maxima, total_rank_capacities=capacities,
                          nonzero_summary_code_weights=weights, minimum_nonzero_weight=48),
                     sort_keys=True, indent=2))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
