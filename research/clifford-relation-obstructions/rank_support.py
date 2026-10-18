"""Add exact consequences of invertibility to the path-support relaxation.

For each middle label g: R_g=C M_g A. When M_g is a partial permutation
with scalar entries, its rank is its number of nonzero entries. A zero
column/row of R_g also gives a zero column/row after cancelling C/A.
"""
from collections import defaultdict
from itertools import combinations, permutations

from model import Engine, generic_paths, coefficient_records
from support import encode_support


def strengthen(cnf, records):
    assert cnf['blocks'] == 3
    clauses, labels = cnf['clauses'], cnf['labels']
    selectors = {(v[1], v[2]): i for i, v in enumerate(labels) if v and v[0] == 'frame'}
    groups = defaultdict(dict)
    for record in records:
        cells = set()
        for mask in record['poly']:
            middle = (mask >> 9) & 511
            assert middle.bit_count() == 1
            cells.add(middle.bit_length()-1)
        key = tuple(sorted(cells))
        position = record['output'], record['column']
        assert position not in groups[key]
        groups[key][position] = record
    added = CounterLite()
    for cells, grid in sorted(groups.items()):
        assert len(grid) == 9
        rows, columns = [i//3 for i in cells], [i % 3 for i in cells]
        partial = len(set(rows)) == len(rows) and len(set(columns)) == len(columns)
        if not partial:
            continue
        allowed = {(r, s): selectors[s, record['frame']] for (r, s), record in grid.items() if record['rank'] == 3}
        for s, targets in enumerate(cnf['target_frames']):
            for frame in targets:
                if any(grid[r, s]['rank'] == 3 and grid[r, s]['frame'] == frame for r in range(3)):
                    continue
                for cell in cells:
                    i, j = divmod(cell, 3)
                    clauses.append([-selectors[s, frame], -(10+cell), -(3*j+s+1)])
                    added['zero_column'] += 1
        for r in range(3):
            guards = sorted({allowed[r, s] for s in range(3) if (r, s) in allowed})
            for cell in cells:
                i, j = divmod(cell, 3)
                clauses.append([-(19+3*r+i), -(10+cell), *guards])
                added['zero_row'] += 1
        for size in range(1, len(cells)+1):
            matchings = []
            for rs in combinations(range(3), size):
                for ss in permutations(range(3), size):
                    positions = list(zip(rs, ss))
                    if not all(p in allowed for p in positions):
                        continue
                    labels.append(['rank_matching', list(cells), [list(p) for p in positions]])
                    v = len(labels)-1
                    matchings.append(v)
                    for guard in sorted({allowed[p] for p in positions}):
                        clauses.append([-v, guard])
            for active in combinations(cells, size):
                clauses.append([*(-(10+i) for i in active), *matchings])
                added['rank_bound'] += 1
    cnf['variables'] = len(labels)-1
    cnf['strengthening_counts'] = dict(added)
    return cnf


class CounterLite(dict):
    def __missing__(self, key):
        return 0


def compile_support(program):
    ring = Engine()
    rows, blocks = generic_paths(ring, program, 3)
    records, targets = coefficient_records(ring, rows)
    return strengthen(encode_support(records, targets, blocks), records)
