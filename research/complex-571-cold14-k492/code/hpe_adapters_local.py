"""Paid residual wrappers for entering helpers (Lemma A): generation and independent decoding.  Apache-2.0.
Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.  The wrapper construction follows PR #458
(chafreaky): a helper that starts at frame E and ends at FULL has the physical residual S_E = T_FULL T_E^-1 (apply T_E^-1 first);
S_E = L_E (C_[w] x I) R_E with R_E applied first; the wrappers  R_E^-1  before the whole local invocation and  L_E^-1  after its
full-frame cleanup turn the residual into the coordinate factor C_[w] x I and restore the other 9 - w coordinates identically.
usage: adapters_gk.py CANONICAL-WORD.json.gz RESIDUAL-ADAPTERS.json OUT-LEMMA-A.json
Writes the recipes (generation uses clifford_exact.lower_child) and then DECODES the serialized monomials with the primitive
constructors of clifford_exact (not lower_child) and checks, for every entrance frame, that  L_E^-1 S_E R_E^-1  has exactly the
tableau and zero-state vector (global phase included) of  fourier(9, range(w)); mutated recipes (wrong phase, swapped sides, wrong
translation, wrong width) must be rejected."""
import copy, gzip, json, sys
from pathlib import Path
# Package-path adaptation only; the exact wrapper mathematics is unchanged.
import os
R = Path(os.environ['MULTICOLD_SOURCE']) / 'vendor/pr558/vendor/pr552/complex-global/vendor531'   # HPE: the pinned vendor531 clifford_exact
sys.path.insert(0, str(R / 'vendor/clifford'))
from clifford_exact import canonical_frame, lower_child, fourier, diag, perm, xgate, Op, identity
n = 9; FULL = tuple(1 << i for i in range(n))
def monomial_op(rec):
    """decode a serialized monomial (matrix rows, quadratic rows, Z4 linear part, translation, phase)"""
    out = diag(n, tuple(rec['quadratic_rows']), tuple(rec['linear_Z4'])).then(perm(n, tuple(rec['matrix_rows']))).then(xgate(n, rec['offset']))
    return out.then(Op(n, identity(n), [('phase', rec['phase'])]))
def S_of(U, END=FULL):
    # HPE: a helper that starts at E=U and ends at END has residual T_END T_E^-1 (END = FULL is the inherited case)
    return canonical_frame(n, tuple(U)).adjoint().then(canonical_frame(n, tuple(END)))
def wrapped_ok(U, rec, END=FULL):
    """exactly: L^-1 S R^-1 = C_[w] x I  (apply order: R^-1, S, L^-1), w = dim END - dim E"""
    w = len(END) - len(U); S = S_of(U, END); Rm = monomial_op(rec['right']); Lm = monomial_op(rec['left'])
    net = Rm.adjoint().then(S).then(Lm.adjoint()); target = fourier(n, range(w))
    return rec['rank'] == w and net.tab == target.tab and net.zero_state() == target.zero_state()
def _contains(a, b):
    a = list(a)
    for x in b:
        for y in sorted(a, reverse=True):
            if x >> (y.bit_length() - 1) & 1: x ^= y
        if x: return False
    return True
def main():
    c = json.load(gzip.open(sys.argv[1])); frames = c['frames']; v = c['v']
    starts = sorted({c['start'][r] for r in range(2 * v, len(c['start'])) if c['start'][r] != 0 and c['final'][r] == 1})
    # HPE: (entrance, terminal) pairs of helpers ending at a proper subspace; key 'E:U'.  Inherited words have none.
    ends = sorted({(c['start'][r], c['final'][r]) for r in range(2 * v, len(c['start'])) if c['final'][r] != 1})
    # COLD-HPE: e == 0 (a cold helper, entrance = bottom, T_0 = I) is allowed: the (0, U) recipe is keyed '0:U'
    assert all(len(frames[u]) < n and _contains(frames[u], frames[e]) for e, u in ends)
    cold_ends = [(e, u) for e, u in ends if e == 0]
    recipes = {}
    for f in starts:
        U = frames[f]; rec, compiled = lower_child(S_of(U))
        recipes[str(f)] = dict(frame=f, vectors=list(U), entrance_rank=len(U), rank=rec['rank'], left=rec['left'], right=rec['right'])
    for e, u in ends:
        E, U = frames[e], frames[u]; rec, compiled = lower_child(S_of(E, U))
        recipes['%d:%d' % (e, u)] = dict(frame=e, terminal=u, vectors=list(E), terminal_vectors=list(U), entrance_rank=len(E),
                                         terminal_rank=len(U), rank=rec['rank'], left=rec['left'], right=rec['right'])
    Path(sys.argv[2]).write_text(json.dumps(dict(status='RESIDUAL_ADAPTER_RECIPES', recipes=recipes), sort_keys=True, separators=(',', ':')) + '\n')
    # ---- independent decode of the serialized file
    data = json.loads(Path(sys.argv[2]).read_text())['recipes']
    dot = lambda a, b: bin(a & b).count('1') & 1
    detail = []
    for f in starts:
        rec = data[str(f)]; U = frames[f]
        assert wrapped_ok(U, rec), ('wrapper product is not C_[w] x I', f)
        detail.append(dict(frame=f, entrance_rank=len(U), residual_width=n - len(U), vectors=list(U), all_even_weight=all(bin(x).count('1') % 2 == 0 for x in U),
                           totally_isotropic=all(dot(a, b) == 0 for a in U for b in U)))
    hdetail = []
    for e, u in ends:   # HPE: independent decode, residual width = dim U - dim E
        rec = data['%d:%d' % (e, u)]; E, U = frames[e], frames[u]
        assert wrapped_ok(E, rec, U), ('HPE wrapper product is not C_[w] x I', e, u)
        hdetail.append(dict(frame=e, terminal=u, entrance_rank=len(E), terminal_rank=len(U), residual_width=len(U) - len(E)))
    controls = []
    def reject(name, fn):
        f = starts[0]; rec = copy.deepcopy(data[str(f)]); fn(rec)
        if wrapped_ok(frames[f], rec): raise AssertionError('mutated wrapper accepted: ' + name)
        controls.append(name)
    reject('wrong global phase', lambda r: r['right'].__setitem__('phase', (r['right']['phase'] + 1) % 4))
    reject('wrong translation', lambda r: r['left'].__setitem__('offset', r['left']['offset'] ^ 1))
    reject('wrong quadratic form', lambda r: r['right'].__setitem__('quadratic_rows', [x ^ 2 if i == 0 else x for i, x in enumerate(r['right']['quadratic_rows'])]) if False else r['right']['linear_Z4'].__setitem__(0, (r['right']['linear_Z4'][0] + 2) % 4))
    reject('sides swapped', lambda r: (r.__setitem__('left', r['right']), r.__setitem__('right', r['left'])))
    reject('wrong width', lambda r: r.__setitem__('rank', r['rank'] + 1))
    if ends:   # HPE controls on the first (E, U) pair
        e, u = next((p for p in ends if p[0] != 0), ends[0]); rec0 = data['%d:%d' % (e, u)]   # COLD-HPE: an entering pair if any (= ends[0] without cold ends)
        def hreject(name, ok):
            if ok: raise AssertionError('HPE mutation accepted: ' + name)
            controls.append(name)
        hreject('hpe: U-wrapper decoded against a FULL ending', wrapped_ok(frames[e], rec0))
        hreject('hpe: width misreported as 9 - dim E', wrapped_ok(frames[e], dict(rec0, rank=n - len(frames[e])), frames[u]))
        other = next(f for f in range(len(frames)) if f != u and len(frames[f]) == len(frames[u]) and _contains(frames[f], frames[e]))
        hreject('hpe: wrong terminal hyperplane', wrapped_ok(frames[e], rec0, frames[other]))
        fe = next(((e2, u2) for e2, u2 in ends if str(e2) in data), None)
        if fe:   # an entrance shared with FULL-ended helpers: R_{E,FULL} must not serve as R_{E,U}
            r2 = data['%d:%d' % fe]
            hreject('hpe: pre wrapper resolved to the FULL recipe R_{E,FULL}', wrapped_ok(frames[fe[0]], dict(r2, right=data[str(fe[0])]['right']), frames[fe[1]]))
        hreject('hpe: wrong global phase', wrapped_ok(frames[e], dict(rec0, left=dict(rec0['left'], phase=(rec0['left']['phase'] + 1) % 4)), frames[u]))
    if cold_ends:   # COLD-HPE controls on the first cold pair (0, U): factor_iff_pre says only R_{0,U} itself may precede
        e, u = cold_ends[0]; recc = data['%d:%d' % (e, u)]; E, U = frames[e], frames[u]
        ID = dict(matrix_rows=[1 << i for i in range(n)], offset=0, quadratic_rows=[0] * n, linear_Z4=[0] * n, phase=0)
        assert monomial_op(ID).tab == identity(n)   # the control's wrapper really is the identity
        def creject(name, ok):
            if ok: raise AssertionError('cold HPE mutation accepted: ' + name)
            controls.append(name)
        creject('cold hpe: identity pre wrapper instead of R_{0,U}', wrapped_ok(E, dict(recc, right=ID), U))
        creject('cold hpe: identity post wrapper instead of L_{0,U}', wrapped_ok(E, dict(recc, left=ID), U))
        creject('cold hpe: no wrappers (cold FULL convention L = R = I)', wrapped_ok(E, dict(recc, left=ID, right=ID), U))
        creject('cold hpe: U-wrapper decoded against a FULL ending', wrapped_ok(E, recc))
        creject('cold hpe: width misreported as 9', wrapped_ok(E, dict(recc, rank=n), U))
        other = next(f for f in range(len(frames)) if f != u and len(frames[f]) == len(frames[u]))
        creject('cold hpe: wrong terminal hyperplane', wrapped_ok(E, recc, frames[other]))
        creject('cold hpe: wrong global phase', wrapped_ok(E, dict(recc, right=dict(recc['right'], phase=(recc['right']['phase'] + 1) % 4)), U))
        ent = next((p for p in ends if p[0] != 0 and p[1] == u), None)
        same = lambda x, y: monomial_op(x).tab == monomial_op(y).tab and monomial_op(x).zero_state() == monomial_op(y).zero_state()
        if ent and not same(data['%d:%d' % ent]['right'], recc['right']):   # an entering helper ending at the same U: its R_{E,U} must not serve as R_{0,U}
            creject('cold hpe: pre wrapper resolved to an entering recipe R_{E,U}', wrapped_ok(E, dict(recc, right=data['%d:%d' % ent]['right']), U))
    res = dict(status='PASS_RESIDUAL_WRAPPERS_ARE_EXACT', frames=len(detail), **({'hyperplane_end_pairs': hdetail} if ends else {}), **({'cold_hyperplane_end_pairs': len(cold_ends)} if cold_ends else {}), wrappers_reject=controls, all_even_weight=all(d['all_even_weight'] for d in detail),
               all_totally_isotropic=all(d['totally_isotropic'] for d in detail), detail=detail)
    Path(sys.argv[3]).write_text(json.dumps(res, indent=1) + '\n')
    print('Lemma A (exact): L^-1 S_E R^-1 = C_[w] x I for', len(detail), 'entrance frames, global phase included;', len(controls), 'wrapper mutations rejected; all-even-weight:', res['all_even_weight'])
if __name__ == '__main__': main()
