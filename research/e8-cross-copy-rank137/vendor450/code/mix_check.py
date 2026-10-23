# Exact checks of a (target-mixed) bitE8/1 word and the four mixing mutation controls.  Derived from the checks written
# for the target-mixing lever (same Claude Opus 5.5 (Anthropic) via Claude Code effort as this package; DreamingOfClouds).
# Uses PR #417/#435/#443's e8core.replay unchanged.  Apache-2.0.
"""usage: mix_check.py WORD(.json|.json.gz) RECORDS_DIR [--controls BASE_WORD(.json.gz)]
(1) e8core.replay: F2 on all 980 formal columns incl. dirt and target inputs, nested frames, D at frame 0, y at frame 0 at
    the scatter, finals, integer source spans of non-target operands;
(2) the defining identity of the bitE8/1 word (x,h restored, y_t += x_t) on independent bit-vector columns;
(3) the stricter target-operand span check: the integer x-support of every target operand lies in the gate frame
    (centre content excluded);
(4) with --controls: four mutants (no frame-0 preconditioner, no scatter fix, mixing at the full frame, mixing omitted)
    must each be rejected."""
import copy, gzip, json, math, os, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'e8-r740-replica32/code'))
from e8core import Lat, replay
ld = lambda p: json.load(gzip.open(p, 'rt') if str(p).endswith('.gz') else open(p))

def check(w, frames):
    L = Lat(w['lines']); masks = [sum(1 << x for x in f) for f in w['frames']]
    for i, m in enumerate(masks): L._close[m] = m; L._dim[m] = frames[str(i)]['dim']
    r = replay(w, L=L, masks=masks, span_mode='z'); assert not r['viol'], r['viol'][:5]
    H = r['H']; cost = sum(n * k * math.log(64 / k) for k, n in H.items())
    v, n = w['v'], 2 * w['v'] + w['R']
    x = [1 << i for i in range(n)]
    def run(gs):
        for f, d, ss in gs:
            assert d not in ss
            for s in ss: x[d] ^= x[s]
    run(w['D']); run(w['A']); tot = [x[q] for q in w['ret']]
    for t, ss in enumerate(w['scatter']):
        for k in ss: x[v + t] ^= tot[k]
    run(w['B']); run(w['C'])
    exp = [1 << i for i in range(n)]
    for t in range(v): exp[v + t] ^= 1 << t
    assert x == exp
    fs = [frozenset(f) for f in w['frames']]
    supp = [Counter({i: 1}) if i < v else Counter() for i in range(n)]
    viol = 0; tops = 0
    for ph in ('D', 'A', 'B', 'C'):
        for f, d, ss in w[ph]:
            for s in ss:
                if v <= s < 2 * v:
                    tops += 1
                    if any(k not in fs[f] for k in supp[s]): viol += 1
                for k, a in supp[s].items(): supp[d][k] += a
    assert viol == 0, ('target operand outside its gate frame', viol)
    return dict(status='PASS', columns=r['n'], R=w['R'], profile=dict(sorted(H.items())), local_cost_per_call=round(cost, 3),
                target_operands=tops, strict_target_span_violations=viol)

def controls(w, base, frames):
    v = w['v']; nD = len(base['D']); res = {}
    def test(name, m):
        try: check(m, frames)
        except (AssertionError, KeyError, IndexError, ValueError, TypeError): res[name] = 'REJECTED'
        else: res[name] = 'ACCEPTED'
    m = copy.deepcopy(w); m['D'] = m['D'][:nD]; test('omit frame-0 preconditioners', m)
    m = copy.deepcopy(w); m['scatter'] = base['scatter']; test('omit scatter correction', m)
    mixed = [k for k, g in enumerate(w['B']) if v <= g[2][0] < 2 * v]
    m = copy.deepcopy(w); full = next(i for i, f in enumerate(m['frames']) if len(f) == len(m['lines'])); m['B'][mixed[0]] = [full, m['B'][mixed[0]][1], m['B'][mixed[0]][2]]; test('mix at the full frame', m)
    m = copy.deepcopy(w); m['B'] = [g for g in m['B'] if not (v <= g[2][0] < 2 * v)]; test('omit mix additions', m)
    assert all(x == 'REJECTED' for x in res.values()), res
    return res

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    w = ld(args[0]); frames = json.load(open(Path(args[1]) / 'frames.json'))['frames']
    out = check(w, frames)
    if '--controls' in sys.argv:
        base = ld(sys.argv[sys.argv.index('--controls') + 1]); out['mutation_controls'] = controls(w, base, frames)
    print(json.dumps(out))
