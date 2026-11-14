#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""{0}/V re-basis: the helper-761 rung merge of #7542, rebuilt from #7334's word.

Standard library only. Written for this package; it imports no other package.

The vendored word is Clear1nsight's #7334 WORD.json.gz (SHA256 pinned below,
identical bytes to the copy vendored by #7542). The checker

1. applies the six deletions, five insertions and five appended events of the
   761 merge (the helper-761 half of #7542's edit list) and replays both words
   over the rationals from arbitrary inputs with the full legality rules of
   #7542's check.py (operands at the event chart, public MOVEs strictly
   ascend, owned MOVEs nested, owned fields cleared, public fields end at
   their final charts);
2. requires all 1,569 rows and end charts to equal #7334's, and only helper
   761's MOVE chain to change (dims 0->5->7->8->9 become 0->7->8->9);
3. checks the two re-basis facts the edit rests on, separately from the
   replay: ({0}) 761 and 1266 both sit at {0} at the new ADD and no event
   writes 761 between it and the deleted ADD at chart 1053, so 1266 receives
   the same content; (V) the four appended ADDs act at V on V-ending helpers
   whose final rows are their own unit rows, and the row 1438 carries into V
   in the new word differs from #7334's final row by exactly
   -(e_311 - e_591 + 2 e_760 + e_1439), i.e. it lies in W_V and the V-phase
   recombination restores it;
4. runs rejecting controls.
"""
import collections
import copy
import gzip
import hashlib
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE / 'data' / 'base-7334-word.json.gz'
BASE_SHA256 = '4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a'
ZERO, V = 3, 127  # frame indices of {0} and V in #7334's word

# The helper-761 half of #7542's data/edits.json (indices into #7334's program).
EDIT = {
    'delete': [
        [36446, ['MOVE', 1266, 3, 1053, False]],
        [36447, ['MOVE', 761, 3, 1053, False]],
        [36448, ['ADD', 1266, 761, '1/2', 1053]],
        [36449, ['ADD', 1438, 761, '-1/2', 1053]],
        [38225, ['MOVE', 591, 3, 1053, False]],
        [42299, ['MOVE', 761, 1053, 1083, False]],
    ],
    'insert_before': [
        [36442, [['ADD', 1266, 761, '1/2', 3]]],
        [36446, [['MOVE', 591, 3, 1053, False], ['ADD', 1438, 591, '1', 1053], ['ADD', 1438, 760, '-2', 1053]]],
        [42299, [['MOVE', 761, 3, 1083, False]]],
    ],
    'append': [
        ['ADD', 1438, 311, '1', 127], ['ADD', 1438, 591, '-1', 127], ['ADD', 1438, 760, '2', 127],
        ['ADD', 1438, 1439, '1', 127], ['MOVE', 1266, 3, 1053, False],
    ],
}


def require(cond, label):
    if not cond:
        raise AssertionError(label)


def span(vectors):
    s = {0}
    for v in vectors:
        require(type(v) is int and 0 < v < 512 and v not in s, 'frame vectors independent in F2^9')
        s |= {x ^ v for x in s}
    return frozenset(s)


def apply_edit(program, E):
    dele = {}
    for i, ev in E['delete']:
        require(program[i] == ev, 'deleted event %d matches #7334' % i)
        dele[i] = ev
    ins = collections.defaultdict(list)
    for i, evs in E['insert_before']:
        ins[i].extend(evs)
    out = []
    for i, ev in enumerate(program):
        out.extend(ins.get(i, []))
        if i not in dele:
            out.append(ev)
    return out + E['append']


def replay(W, stop=None):
    """Exact replay from arbitrary inputs; raises on any illegality. stop: replay only a prefix (no end checks)."""
    n, N = W['public'], W['public'] + W['owned_fields']
    sp = [span(f) for f in W['frames']]
    rows = [{r: Q(1)} if r < n else {} for r in range(N)]
    cur = list(W['initial']) + [None] * W['owned_fields']
    alive, chains = set(), collections.defaultdict(list)
    owned_moves, lifetimes, init_chart, peak = collections.Counter(), collections.Counter(), {}, 0
    prog = W['program'] if stop is None else W['program'][:stop]
    for i, e in enumerate(prog):
        op, r = e[0], e[1]
        require(type(r) is int and 0 <= r < N, '%d register index' % i)
        if op == 'MOVE':
            a, b, flag = e[2], e[3], e[4]
            require(type(flag) is bool and flag == (r >= n), '%d MOVE ownership flag' % i)
            require(cur[r] == a, '%d MOVE from the current chart' % i)
            if r >= n:
                require(r in alive, '%d owned MOVE on a live field' % i)
                require(sp[a] < sp[b] or sp[b] < sp[a], '%d owned MOVE nested' % i)
                owned_moves[(a, b)] += 1
            else:
                require(sp[a] < sp[b], '%d public MOVE strictly ascends' % i)
            cur[r] = b
            chains[r].append((a, b))
        elif op == 'INIT':
            require(r >= n and r not in alive and len(e) == 3, '%d INIT of a dead owned field' % i)
            alive.add(r); rows[r] = {}; cur[r] = e[2]; init_chart[r] = e[2]
            peak = max(peak, len(alive))
        elif op == 'CLEAR':
            require(r >= n and r in alive and cur[r] == e[2], '%d CLEAR at the current chart' % i)
            lifetimes[(r, init_chart.pop(r), e[2])] += 1
            alive.discard(r); rows[r] = {}; cur[r] = None
        elif op == 'SCALE':
            q = Q(e[2])
            require(q != 0 and cur[r] == e[3] and (r < n or r in alive), '%d SCALE' % i)
            rows[r] = {k: v * q for k, v in rows[r].items()}
        elif op in ('ADD', 'COPY'):
            s, q, f = e[2], Q(e[3]), e[4]
            require(type(s) is int and 0 <= s < N and s != r and q != 0, '%d operand' % i)
            require(cur[r] == f and cur[s] == f, '%d ADD/COPY operands at chart %d' % (i, f))
            require(all(x < n or x in alive for x in (r, s)), '%d owned field live' % i)
            if op == 'COPY':
                require(not rows[r], '%d COPY into a zero field' % i)
            R = rows[r]
            for k, v in rows[s].items():
                nv = R.get(k, 0) + q * v
                if nv:
                    R[k] = nv
                else:
                    R.pop(k, None)
        else:
            raise AssertionError('%d unknown op %r' % (i, op))
    if stop is None:
        require(not alive, 'every owned field cleared')
        require(cur[:n] == list(W['final']), 'public fields end at final charts')
    return dict(rows=rows, cur=cur, chains=chains, owned_moves=owned_moves, lifetimes=lifetimes, peak=peak)


def compare(B, RB, W):
    R = replay(W)
    bad = [r for r in range(len(R['rows'])) if R['rows'][r] != RB['rows'][r]]
    require(not bad, 'all rows equal #7334 (first differing %s)' % bad[:3])
    require(R['cur'] == RB['cur'], 'all end charts equal #7334')
    require(R['owned_moves'] == RB['owned_moves'] and R['lifetimes'] == RB['lifetimes'] and R['peak'] == RB['peak'],
            'owned MOVEs, lifetimes and peak unchanged')
    changed = sorted(r for r in set(R['chains']) | set(RB['chains']) if R['chains'][r] != RB['chains'][r])
    require(changed == [761], 'only helper 761 changes its MOVE chain (got %s)' % changed[:5])
    return R


def main():
    raw = BASE.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == BASE_SHA256, 'vendored #7334 word bytes')
    B = json.loads(gzip.decompress(raw))
    P0 = B['program']
    dim = [len(f) for f in B['frames']]
    require(dim[ZERO] == 0 and dim[V] == 9, 'frame 3 is {0}, frame 127 is V')
    W = dict(B); W['program'] = apply_edit(P0, EDIT)
    print('PASS #7334 word authenticated (%d events); 761 merge: %d deletions, %d insertions, %d appended -> %d events'
          % (len(P0), len(EDIT['delete']), sum(len(x[1]) for x in EDIT['insert_before']), len(EDIT['append']),
             len(W['program'])))

    RB = replay(B)
    R = compare(B, RB, W)
    f = lambda ch: '->'.join([str(dim[ch[0][0]])] + [str(dim[b]) for a, b in ch])
    old, new = f(RB['chains'][761]), f(R['chains'][761])
    require((old, new) == ('0->5->7->8->9', '0->7->8->9'), 'helper 761 chain')
    print('PASS exact replay: legal; all %d rows and end charts equal #7334; owned data unchanged; helper 761 %s became %s'
          % (len(R['rows']), old, new))
    paid = lambda P: collections.Counter(abs(dim[e[3]] - dim[e[2]]) for e in P if e[0] == 'MOVE')
    d = paid(W['program']); d.subtract(paid(P0))
    d = {k: v for k, v in sorted(d.items()) if v}
    require(d == {2: -1, 5: -1, 7: 1}, 'paid MOVE delta per native word')
    print('PASS paid MOVE ranks per native word: %s (one rank-5 and one rank-2 rung become one rank-7 MOVE)' % d)

    # ({0}) side: the new ADD reads 761 at {0}; nothing writes 761 between it and the deleted ADD at 1053.
    i0, i1 = 36442, 36448
    pre = replay(B, stop=i0)
    require(pre['cur'][761] == ZERO and pre['cur'][1266] == ZERO, '761 and 1266 sit at {0} at the new ADD')
    writes = [i for i in range(i0, i1) if P0[i][0] in ('ADD', 'COPY', 'SCALE') and P0[i][1] == 761]
    require(not writes, 'no write to 761 between {0} and chart 1053')
    mid = replay(B, stop=i1)
    require(pre['rows'][761] == mid['rows'][761], '761 content identical at {0} and at chart 1053')
    print('PASS {0} re-basis: 761 and 1266 at {0} at event %d; no event writes 761 before event %d, so 1266 += 1/2*761 '
          'reads the same content at {0} as at chart 1053 (761 row = %s)' % (i0, i1, mid['rows'][761]))

    # (V) side: the four appended ADDs act at V on V-ending helpers with final rows = unit rows.
    corr = {311: Q(1), 591: Q(-1), 760: Q(2), 1439: Q(1)}
    for r in corr:
        require(B['final'][r] == V and RB['rows'][r] == {r: Q(1)}, 'helper %d ends at V with final row e_%d' % (r, r))
    require(B['final'][1438] == V, '1438 ends at V')
    k = len(W['program']) - len(EDIT['append'])
    pre_v = replay(W, stop=k)['rows'][1438]
    target = dict(RB['rows'][1438])
    for r, c in corr.items():
        target[r] = target.get(r, 0) - c
        if not target[r]:
            del target[r]
    require(pre_v == target, '1438 V-arrival = final - (e311 - e591 + 2 e760 + e1439)')
    print('PASS V re-basis: 311, 591, 760, 1439 end at V with unit final rows; 1438 enters the V phase with '
          '#7334 final - (e_311 - e_591 + 2 e_760 + e_1439), inside W_V; the four V ADDs restore it exactly')

    # Controls.
    def rejected(label, mutate):
        W2 = dict(B); W2['program'] = copy.deepcopy(W['program'])
        mutate(W2['program'])
        try:
            compare(B, RB, W2)
        except AssertionError as exc:
            print('PASS control rejected: %s (%s)' % (label, exc))
            return
        raise AssertionError('control not rejected: ' + label)
    idx = lambda P, ev: P.index(ev)
    rejected('{0} ADD 1266 += 1/2*761 deleted', lambda P: P.remove(['ADD', 1266, 761, '1/2', 3]))
    rejected('{0} ADD with coefficient 1 instead of 1/2',
             lambda P: P.__setitem__(idx(P, ['ADD', 1266, 761, '1/2', 3]), ['ADD', 1266, 761, '1', 3]))
    rejected('local 1438 += -2*760 at 1053 deleted', lambda P: P.remove(['ADD', 1438, 760, '-2', 1053]))
    rejected('V correction 1438 += 1439 deleted', lambda P: P.remove(['ADD', 1438, 1439, '1', 127]))
    rejected('V correction 1438 += 2*760 with coefficient 1',
             lambda P: P.__setitem__(idx(P, ['ADD', 1438, 760, '2', 127]), ['ADD', 1438, 760, '1', 127]))
    rejected('V correction against 1266, which ends at chart 1053, not V',
             lambda P: P.insert(len(P) - 1, ['ADD', 1438, 1266, '1', 127]))
    rejected('merged MOVE kept but old 1053 ADDs restored without 761 at 1053',
             lambda P: P.__setitem__(idx(P, ['ADD', 1266, 761, '1/2', 3]), ['ADD', 1266, 761, '1/2', 1053]))
    print('PASS_METHODS_REBASIS')


if __name__ == '__main__':
    sys.exit(main())
