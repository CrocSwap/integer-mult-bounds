"""Replace independent retained helpers by a reversible source-basis word.

icekylinx, with Codex assistance. Inherited E8 input notices apply. This
certifies the finite local F2 word and nested incidences, not a new kappa.
"""
from pathlib import Path
from hashlib import sha256
import copy
import json

import os
ROOT = Path(os.environ['E8_OUTPUT']) / 'bit426-source-centres'


def replay(c, skip_inverse=False, skip_dirt=False):
    v, n = c['v'], 2*c['v'] + c['R']
    x = [1 << i for i in range(n)]
    def run(gs):
        for f, d, ss in gs:
            assert d not in ss
            for s in ss:
                x[d] ^= x[s]
    if not skip_dirt:
        run(c['D'])
    run(c['A'])
    totals = [x[r] for r in c['ret']]
    for t, ss in enumerate(c['scatter']):
        for k in ss:
            x[v+t] ^= totals[k]
    run(c['B'][c.get('source_basis_gates', 0):] if skip_inverse else c['B'])
    run(c['C'])
    expected = [1 << i for i in range(n)]
    for t in range(v):
        expected[v+t] ^= 1 << t
    return x == expected


def main():
    source = ROOT / 'bit-input.json'
    old = json.loads(source.read_bytes())
    assert replay(old)
    v = old['v']
    retired = set(old['ret'])
    full = old['final'][0]
    rows = []
    for r in old['ret']:
        row = 0
        for f, d, ss in old['A']:
            if d == r:
                assert f == full and all(s < v for s in ss)
                for s in ss:
                    row ^= 1 << s
        assert row
        rows.append(row)
    assert all(not retired.intersection(ss) for f, d, ss in old['A'] + old['B'])
    assert all(d not in retired for f, d, ss in old['B'])
    # Find an invertible minor, preserving the original order of centre rows.
    echelon = {}
    for row in rows:
        for p, q in sorted(echelon.items()):
            if row >> p & 1:
                row ^= q
        assert row, 'Retained forms must be independent'
        p = (row & -row).bit_length() - 1
        echelon[p] = row
    pivots = sorted(echelon)
    matrix = [1 << i for i in range(v)]
    for p, row in zip(pivots, rows):
        matrix[p] = row
    target = matrix[:]
    elimination = []
    def add(d, s):
        matrix[d] ^= matrix[s]
        elimination.append((d, s))
    for p in range(v):
        q = next(i for i in range(p, v) if matrix[i] >> p & 1)
        if q != p:
            add(p, q); add(q, p); add(p, q)
        for i in range(v):
            if i != p and matrix[i] >> p & 1:
                add(i, p)
    assert matrix == [1 << i for i in range(v)]
    forward = [[full, d, [s]] for d, s in reversed(elimination)]
    inverse = list(reversed(forward))
    check = [1 << i for i in range(v)]
    for f, d, ss in forward:
        check[d] ^= check[ss[0]]
    assert check == target
    out = copy.deepcopy(old)
    physical = [i for i in range(2*v+old['R']) if i not in retired]
    index = {r: i for i, r in enumerate(physical)}
    def remap(gs):
        return [[f, index[d], [index[s] for s in ss if s not in retired]]
                for f, d, ss in gs if d not in retired]
    out['R'] -= len(retired)
    out['ret'] = pivots
    out['D'] = remap(old['D'])
    out['A'] = remap(old['A']) + forward
    out['B'] = inverse + remap(old['B'])
    out['C'] = remap(old['C'])
    out['start'] = [old['start'][i] for i in physical]
    out['final'] = [old['final'][i] for i in physical]
    out['source_basis_gates'] = len(forward)
    assert replay(out), 'All independent source, target and dirty columns'
    assert not replay(out, skip_inverse=True)
    assert not replay(out, skip_dirt=True)
    # Frame incidence inclusion uses the root-closed sets in this bit format.
    frames = [set(f) for f in out['frames']]
    cur = out['start'][:]
    for phase in ['D', 'A', 'B', 'C']:
        for f, d, ss in out[phase]:
            for r in [d] + ss:
                assert frames[cur[r]] <= frames[f], (phase, r, cur[r], f)
                cur[r] = f
        if phase == 'A':
            assert all(cur[r] == full for r in out['ret'])
    assert all(frames[f] <= frames[g] for f, g in zip(cur, out['final']))
    raw = json.dumps(out, sort_keys=True, separators=(',', ':')).encode()
    (ROOT / 'bit-source-centres.json').write_bytes(raw)
    result = dict(status='PASS_LOCAL_ALL_COLUMNS_AND_NESTED_FRAMES',
                  original_R=old['R'], new_R=out['R'],
                  removed_retained_helpers=sorted(retired), retained_source_rows=pivots,
                  formal_columns=2*v+out['R'], reversible_basis_gates_each_way=len(forward),
                  source_sha256=sha256(source.read_bytes()).hexdigest(),
                  output_sha256=sha256(raw).hexdigest(),
                  controls=['unmodified word passes', 'missing inverse rejected', 'missing dirt rejected'],
                  kappa_claimed=False,
                  remaining=['global ordinary-call and reflected integration', 'finite coefficient and tape invoice', 'exact priced component comparison'])
    (ROOT / 'bit-source-centres-receipt.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
