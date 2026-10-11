"""Generate and check coordinate residual routes for the selected R715 word.

Prepared for eumemic with OpenAI Codex assistance; Apache-2.0.
The unchanged PR443 bank auditor independently validates these witnesses.
"""
import argparse
import json
from collections import Counter
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--word', type=Path, required=True)
    ap.add_argument('--frames', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    w = json.loads(a.word.read_bytes())
    fs = json.loads(a.frames.read_text())['frames']
    assert (w['h'], w['v'], w['R']) == (8, 120, 715)
    # The first eight original roots are exactly the doubled coordinate axes.
    assert w['lines'][:8] == [[2 * int(i == j) for j in range(8)] for i in range(8)]
    starts = w['start'][240:]
    census = Counter(8 - fs[str(f)]['dim'] for f in starts)
    assert census == Counter({6: 11, 7: 98, 8: 606})
    assert sum(r * n for r, n in census.items()) == 5600
    rows = []
    for f in sorted(set(starts)):
        e = fs[str(f)]['dim']
        coords = [i for i in w['frames'][f] if i < 8]
        assert len(coords) == e
        assert all(not any(x and j not in coords for j, x in enumerate(w['lines'][i]))
                   for i in w['frames'][f])
        order = coords + [i for i in range(8) if i not in coords]
        cur = order[:]
        operations = []
        for i in range(8):
            j = cur.index(i)
            if i != j:
                operations.append(['swap', i, j, None])
                cur[i], cur[j] = cur[j], cur[i]
        assert cur == list(range(8)) and len(operations) <= 7
        rows.append(dict(frame=f, entrance_rank=e, denominator=2,
                         entrance_basis=coords, residual_basis=order[e:],
                         orthogonal_rows_numerator=[w['lines'][i] for i in order],
                         gaussian_reduction=operations))
    a.out.write_text(json.dumps(rows, indent=2) + '\n')
    print(json.dumps(dict(status='PASS_COORDINATE_RESIDUAL_ISOMETRIES',
                          distinct_entrances=len(rows), entrance_rank=120,
                          residual_width_census=dict(census), residual_mass=5600)))


if __name__ == '__main__':
    main()
