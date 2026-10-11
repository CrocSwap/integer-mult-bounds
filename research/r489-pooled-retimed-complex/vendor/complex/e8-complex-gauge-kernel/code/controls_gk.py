"""Mutation controls for the kernel and gauge gates, with an independent in-memory checker.  Apache-2.0.
Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
usage: controls_gk.py GK_FULL-WORD.json.gz OUT.json
The checker (exact_ok) replays the explicit program precondition + compensation + main + cleanup on every column with arbitrary
helper dirt, forward and inverse-transpose, as audit_gk.py does, but shares no code with it or with gk_word.py except
`profile` (frame chains).  Every control must be REJECTED; the unmutated word must be accepted."""
import copy, gzip, json, sys
from fractions import Fraction as Q
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gk_common import V, FULL, basis
import gk_word as GW


def ap(e, rows):
    if e[0] == 'scale':
        q = Q(e[2], e[3]); rows[e[1]] = {j: q * x for j, x in rows[e[1]].items()}
    else:
        q = Q(e[3], e[4]); t, s = e[1], e[2]
        for j, x in list(rows[s].items()):
            z = rows[t].get(j, Q(0)) + q * x
            if z: rows[t][j] = z
            else: rows[t].pop(j, None)


def inv(e):
    e = copy.deepcopy(e)
    if e[0] == 'add': e[3] *= -1
    else: e[2], e[3] = e[3], e[2]
    return e


def dual(e):
    e = inv(e)
    if e[0] == 'add': e[1], e[2] = e[2], e[1]
    return e


def exact_ok(w):
    """raises AssertionError unless the word is an exact arbitrary-dirt, inverse-transpose program with frame-legal compensation"""
    R = w['report']['R']; n = 2 * V + R
    ident = lambda: [{r: Q(1)} for r in range(n)]
    A, B, cut, prec = w['A'], w['B'], w['cut'], w['precondition']
    main = A + cut + B
    M = ident()
    for e in main: ap(e, M)
    dirty = [{} for _ in range(n)]
    for r in range(V, 2 * V): dirty[r] = {j: x for j, x in M[r].items() if j >= 2 * V}
    for e in prec: ap(e, dirty)
    comp = [['add', r, j, -x.numerator, x.denominator, []] for r in range(V, 2 * V) for j, x in sorted(dirty[r].items())]
    start = {int(r) for r in w.get('start_extra', {})}
    assert not any(e[2] in start for e in comp), 'a helper with a frame-zero compensation must start at frame zero'
    cleanup = [inv(e) for e in reversed(A + B) if not V <= e[1] < 2 * V]
    program = list(prec) + comp + main + cleanup
    actual = ident()
    for e in program: ap(e, actual)
    expected = ident()
    for t in range(V): expected[V + t][t] = Q(1)
    assert actual == expected, 'arbitrary-dirt exactness'
    back = ident()
    for e in program: ap(dual(e), back)
    eb = ident()
    for t in range(V): eb[t][V + t] = Q(-1)
    assert back == eb, 'inverse-transpose exactness'
    GW.profile(w)           # frame chains, entrance containment, centre chains and levels


def controls(w):
    out = []
    exact_ok(w)
    def expect_reject(name, fn):
        q = copy.deepcopy(w); fn(q)
        try: exact_ok(q)
        except (AssertionError, KeyError, StopIteration): out.append(name)
        else: raise AssertionError('mutation accepted: ' + name)
    kern = [i for i, e in enumerate(w['A']) if e[0] == 'add' and e[1] >= 2 * V and e[2] >= 2 * V and e[5] and e[-1] and str(e[2]) in w['start_extra']]
    gaug = [i for i, e in enumerate(w['A']) if e[0] == 'add' and V <= e[1] < 2 * V and str(e[2]) in w['start_extra']]
    assert kern and gaug, 'word has neither kernel nor gauge gates'
    expect_reject('kernel: donor update omitted', lambda q: q['A'].pop(kern[0]))
    expect_reject('kernel: donor update sign flipped', lambda q: q['A'][kern[0]].__setitem__(3, -q['A'][kern[0]][3]))
    expect_reject('gauge: compensation gate omitted', lambda q: q['A'].pop(gaug[0]))
    expect_reject('gauge: compensation coefficient doubled', lambda q: q['A'][gaug[0]].__setitem__(3, 2 * q['A'][gaug[0]][3]))
    def bad_entrance(q):                      # entrance outside the helper's first frame (the gate frames are unchanged)
        e = q['A'][gaug[0]]; h = str(e[2]); E = e[-1]
        q['start_extra'][h] = [next(x for x in range(1, 512) if basis(E + [x]) != basis(E))]
    expect_reject('gauge: entrance not inside the first frame of its gates', bad_entrance)
    expect_reject('gauge: start_extra of a compensated helper without gauge or kernel', lambda q: q['start_extra'].__setitem__(str(2 * V + next(h for h in range(q['report']['R']) if str(2 * V + h) not in q['start_extra'])), [1]))
    expect_reject('gauge: target level forgotten', lambda q: q['target_levels'].pop(next(iter(q['target_levels']))))
    def wrong_level(q):                       # a target level that its compensation gates do not produce
        t = next(iter(q['target_levels'])); E = q['target_levels'][t]
        q['target_levels'][t] = [next(x for x in range(1, 512) if basis(E + [x]) != basis(E))]
    expect_reject('gauge: target level different from the compensation frame', wrong_level)
    return out


def selection_controls(base, sel):
    """structural controls on the selection itself (gk_word.build must refuse)"""
    out = []
    GW.build(base, sel)
    def refuse(name, fn):
        q = copy.deepcopy(sel); fn(q)
        try: GW.build(base, q)
        except (AssertionError, KeyError, StopIteration): out.append(name)
        else: raise AssertionError('selection accepted: ' + name)
    h0 = next(iter(sel['gauge']))
    first = GW.first_frames(base)
    refuse('gauge: entrance outside the first frame', lambda q: q['gauge'].__setitem__(h0, list(first[int(h0)]) + [next(x for x in range(1, 512) if basis(list(first[int(h0)]) + [x]) != basis(list(first[int(h0)])))]))
    col = GW.responses(base)
    def incomparable(q):                      # two entering helpers sharing a target with incomparable entrances
        hs = [int(h) for h in q['gauge']]
        for a in hs:
            for b in hs:
                if a < b and set(col[a]) & set(col[b]):
                    ea = basis(q['gauge'][str(a)])
                    other = [x for x in GW.span(first[b]) if x and x not in GW.span(ea) and len(basis(ea)) == 1 and basis([x]) != ea]
                    if other: q['gauge'][str(b)] = [other[0]]; return
        raise RuntimeError('control not applicable')
    refuse('gauge: non-nested entrances at one target', incomparable)
    c0 = sel['kernel'][0]
    refuse('kernel: pivot outside the donor span', lambda q: q['kernel'][0].__setitem__('donors', q['kernel'][0]['donors'][:-1]) if len(c0['donors']) > 1 and GW.solve_relation(col, c0['donors'][:-1], c0['pivots'][0]) is None else (_ for _ in ()).throw(RuntimeError('control not applicable')))
    refuse('kernel: entrance outside a donor first frame', lambda q: q['kernel'][0].__setitem__('E', [next(x for x in range(1, 512) if x not in GW.span(first[c0['donors'][0]]))]))
    return out


if __name__ == '__main__':
    w = json.load(gzip.open(sys.argv[1])); res = controls(w)
    Path(sys.argv[2]).write_text(json.dumps(dict(status='PASS_GAUGE_KERNEL_MUTATION_CONTROLS', rejected=res), indent=2) + '\n'); print(len(res), 'controls rejected')
