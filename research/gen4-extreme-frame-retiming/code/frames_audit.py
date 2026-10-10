#!/usr/bin/env python3
"""Independent exact audit of every new frame against the word it is applied to.

For each selected unit (one ADD component or one gate) the boundary frames of its operand roles
are read off the input word: the frame of each role's use immediately before the unit (or its
initial frame) and immediately after (or its final frame). A join frame must contain every
previous frame and have dimension equal to the rank of their union; a meet frame must lie in
every next frame and have dimension 24 minus the rank of their stacked annihilators. Each new
frame is checked as an exact rational basis/annihilator pair of complementary rank.
"""
import json, struct, sys
from fractions import Fraction
from pathlib import Path

if not __debug__:
    raise SystemExit('assertions are required')
N = 24


def rank(rows):
    m = [[Fraction(x) for x in r] for r in rows]
    rk = 0
    for c in range(N):
        piv = next((i for i in range(rk, len(m)) if m[i][c]), None)
        if piv is None:
            continue
        m[rk], m[piv] = m[piv], m[rk]
        for i in range(len(m)):
            if i != rk and m[i][c]:
                t = m[i][c] / m[rk][c]
                m[i] = [x - t * y for x, y in zip(m[i], m[rk])]
        rk += 1
    return rk


def vec(row):
    return [Fraction(x) if isinstance(x, str) else Fraction(x) for x in row]


def inside(fs, a, b):
    return fs[a]['dim'] <= fs[b]['dim'] and all(sum(x * y for x, y in zip(vec(u), vec(w))) == 0
                                                 for u in fs[a]['B'] for w in fs[b]['A'])


def audit(base_frames, word, step):
    word = Path(word)
    fs = {int(k): v for k, v in json.loads(Path(base_frames).read_text())['frames'].items()}
    fs.update({int(k): v for k, v in json.loads((word / 'COHORT249-FRAMES.json').read_text()).items()})
    new = {int(k): v for k, v in step['frames'].items()}
    fs.update(new)
    for k, f in new.items():
        assert all(isinstance(x, int) for r in f['B'] + f['A'] for x in r), 'integer rows'
        assert len(f['B']) == f['dim'] == rank(f['B']) and rank(f['A']) == len(f['A']) == N - f['dim']
        assert all(sum(x * y for x, y in zip(u, w)) == 0 for u in f['B'] for w in f['A'])
    initial = {int(k): f for k, f in json.loads((word / 'COHORT249-INITIAL.json').read_text()).items()}
    final = {int(k): f for k, f in json.loads((word / 'COHORT249-FINAL.json').read_text()).items()}
    raw = list(struct.iter_unpack('<6i', (word / 'COHORT249-RECORDS.bin').read_bytes()))
    uses = {}
    for i, (op, a, b, c, f, z) in enumerate(raw):
        if op == 1:
            uses.setdefault(a, []).append((i, f)); uses.setdefault(b, []).append((i, f))
        elif op == 2:
            uses.setdefault(a, []).append((i, c))
    kinds = {'join': 0, 'meet': 0}
    for item in step['selection']:
        gates = set(item['gates']); g = item['new_frame']; old = item['old_frame']
        prev, nxt = set(), set()
        for r in {raw[x][k] for x in gates for k in (1, 2)}:
            idx = [k for k, (i, _) in enumerate(uses[r]) if i in gates]
            k0, k1 = min(idx), max(idx)
            assert all(uses[r][k][0] in gates for k in range(k0, k1 + 1)), 'unit is contiguous on each role'
            prev.add(uses[r][k0 - 1][1] if k0 else initial[r])
            nxt.add(uses[r][k1 + 1][1] if k1 + 1 < len(uses[r]) else final[r])
        assert all(inside(fs, p, g) for p in prev) and all(inside(fs, g, x) for x in nxt)
        if fs[g]['dim'] < fs[old]['dim']:
            assert inside(fs, g, old) and fs[g]['dim'] == rank([r for p in prev for r in fs[p]['B']] or [[0] * N])
            kinds['join'] += 1
        else:
            assert inside(fs, old, g) and fs[g]['dim'] == N - rank([r for x in nxt for r in fs[x]['A']] or [[0] * N])
            kinds['meet'] += 1
    return dict(units=len(step['selection']), new_frames=len(new), **kinds)


if __name__ == '__main__':
    base, word, passes, index = sys.argv[1:5]
    print(json.dumps(audit(base, word, json.loads(Path(passes).read_text())['passes'][int(index)])))
