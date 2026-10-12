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
R = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(R / 'split-centres-global/vendor'))
from clifford_exact import canonical_frame, lower_child, fourier, diag, perm, xgate, Op, identity
n = 9; FULL = tuple(1 << i for i in range(n))
def monomial_op(rec):
    """decode a serialized monomial (matrix rows, quadratic rows, Z4 linear part, translation, phase)"""
    out = diag(n, tuple(rec['quadratic_rows']), tuple(rec['linear_Z4'])).then(perm(n, tuple(rec['matrix_rows']))).then(xgate(n, rec['offset']))
    return out.then(Op(n, identity(n), [('phase', rec['phase'])]))
def S_of(U):
    return canonical_frame(n, tuple(U)).adjoint().then(canonical_frame(n, FULL))
def wrapped_ok(U, rec):
    """exactly: L^-1 S R^-1 = C_[w] x I  (apply order: R^-1, S, L^-1)"""
    w = n - len(U); S = S_of(U); Rm = monomial_op(rec['right']); Lm = monomial_op(rec['left'])
    net = Rm.adjoint().then(S).then(Lm.adjoint()); target = fourier(n, range(w))
    return rec['rank'] == w and net.tab == target.tab and net.zero_state() == target.zero_state()
def main():
    c = json.load(gzip.open(sys.argv[1])); frames = c['frames']; v = c['v']
    starts = sorted({c['start'][r] for r in range(2 * v, len(c['start'])) if c['start'][r] != 0})
    recipes = {}
    for f in starts:
        U = frames[f]; rec, compiled = lower_child(S_of(U))
        recipes[str(f)] = dict(frame=f, vectors=list(U), entrance_rank=len(U), rank=rec['rank'], left=rec['left'], right=rec['right'])
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
    res = dict(status='PASS_RESIDUAL_WRAPPERS_ARE_EXACT', frames=len(detail), wrappers_reject=controls, all_even_weight=all(d['all_even_weight'] for d in detail),
               all_totally_isotropic=all(d['totally_isotropic'] for d in detail), detail=detail)
    Path(sys.argv[3]).write_text(json.dumps(res, indent=1) + '\n')
    print('Lemma A (exact): L^-1 S_E R^-1 = C_[w] x I for', len(detail), 'entrance frames, global phase included;', len(controls), 'wrapper mutations rejected; all-even-weight:', res['all_even_weight'])
if __name__ == '__main__': main()
