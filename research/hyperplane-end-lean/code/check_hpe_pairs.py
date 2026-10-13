# Apache-2.0.  Prepared with Claude Opus 5.5 (Anthropic) in omp; submitted by jeremykothe2.
"""Instance check for the hyperplane-end theorems on an emitted HPE word.

usage: python3 check_hpe_pairs.py RUN_DIR [--mutants]
  RUN_DIR holds CANONICAL-WORD.json.gz and WRAPPER-CHECKS.json of an HPE local run (hpe/code emit + wrap).

For every gate ['add', h, p, q, _, U] of the word's `tail` (the `cleanup_tail` phase) it checks, over F_2^9 with
frames given as lists of 9-bit basis rows:
  * the hypotheses of `hyperplane_width`: E = start[h] has dim 1, U has dim 8, E <= U, U != FULL;
  * the shape of `tail`/`hpe_labels`: q = -1, h != p, each helper has one tail gate, final[h] = U (the post wrapper
    names U), and no gate of the remaining cleanup touches h;
  * (N) was checked exactly for the pair: WRAPPER-CHECKS.json has status PASS_RESIDUAL_WRAPPERS_ARE_EXACT, and its
    hyperplane_end_pairs lists (start[h], U) with residual_width = dim U - dim E;
  * (N) is proved in Lean for the pair: its basis rows (frames[E], frames[U]) are one of LEAN_PAIRS, the pairs of
    `HyperplaneEnd.Exact.pairs` (`exact_N`, `hpe_word_exact`).
Python 3.9+, standard library only."""
import copy, gzip, json, sys
from pathlib import Path


# (E rows, U rows) of HyperplaneEnd/Exact.lean `pair1`, `pair2`, `pair3`
LEAN_PAIRS = {((45,), (256, 128, 64, 33, 16, 9, 5, 2)), ((51,), (256, 128, 64, 33, 17, 8, 4, 3)),
              ((30,), (256, 128, 64, 32, 18, 10, 6, 1))}


def rank(rows):
    basis = []                                   # reduced rows, distinct leading bits
    for r in rows:
        for b in basis:
            r = min(r, r ^ b)
        if r:
            basis.append(r)
    return len(basis)


def check(word, wrap):
    viol = []
    frames, start, final = word['frames'], word['start'], word['final']
    dim = lambda f: rank(frames[f])
    full = [f for f, rows in enumerate(frames) if rank(rows) == 9]
    if wrap.get('status') != 'PASS_RESIDUAL_WRAPPERS_ARE_EXACT':
        viol.append(f"wrapper status {wrap.get('status')}")
    checked = {(p['frame'], p['terminal']): p for p in wrap.get('hyperplane_end_pairs', [])}
    helpers, pairs = set(), {}
    for g in word['tail']:
        op, h, p, q, U = g[0], g[1], g[2], g[3], g[-1]
        E = start[h]
        if op != 'add' or q != -1 or g[4] != 1 or h == p: viol.append(f'tail gate {g}: not h -= p')
        if h in helpers: viol.append(f'helper {h}: two tail gates')
        helpers.add(h)
        if dim(E) != 1: viol.append(f'helper {h}: dim E = {dim(E)}')
        if dim(U) != 8: viol.append(f'helper {h}: dim U = {dim(U)}')
        if rank(frames[E] + frames[U]) != dim(U): viol.append(f'helper {h}: E not in U')
        if U in full: viol.append(f'helper {h}: U is FULL')
        if final[h] != U: viol.append(f'helper {h}: final {final[h]} != U {U}')
        c = checked.get((E, U))
        if c is None: viol.append(f'helper {h}: pair ({E},{U}) not checked exactly')
        elif c.get('residual_width') != dim(U) - dim(E): viol.append(f'helper {h}: width {c.get("residual_width")}')
        if (tuple(frames[E]), tuple(frames[U])) not in LEAN_PAIRS: viol.append(f'helper {h}: pair ({E},{U}) not proved in Lean')
        pairs.setdefault((E, U), []).append(h)
    for g in word['cleanup']:
        if g[1] in helpers or g[2] in helpers: viol.append(f'cleanup gate {g} touches an HPE helper')
    return viol, helpers, pairs


def main():
    run = Path(sys.argv[1])
    word = json.load(gzip.open(run / 'CANONICAL-WORD.json.gz'))
    if not word.get('tail'):
        print(f'{run.name}: no cleanup_tail gates (not an HPE word)'); print('FAIL'); sys.exit(1)
    wrap = json.loads((run / 'WRAPPER-CHECKS.json').read_text())
    viol, helpers, pairs = check(word, wrap)
    print(f'{run.name}: {len(helpers)} hyperplane-ended helpers, {len(pairs)} distinct (E, U) pairs')
    for (E, U), hs in sorted(pairs.items()):
        print(f'  E={E} (dim 1) <= U={U} (dim 8), width 7: {len(hs)} helpers')
    if '--mutants' in sys.argv:
        g0 = word['tail'][0]
        muts = {}
        w = copy.deepcopy(word); w['tail'][0] = g0[:-1] + [1]; w['final'][g0[1]] = 1; muts['U = FULL'] = (w, wrap)
        w = copy.deepcopy(word); w['tail'][0] = g0[:3] + [1] + g0[4:]; muts['gate h += p'] = (w, wrap)
        w = copy.deepcopy(word); w['tail'][0][4] = 2; muts['gate h -= p/2'] = (w, wrap)
        w = copy.deepcopy(word); w['final'][g0[1]] = 1; muts['post wrapper names FULL'] = (w, wrap)
        w = copy.deepcopy(word); w['cleanup'] = w['cleanup'] + [['add', g0[1], g0[2], -1, 1, 1]]; muts['gate left in FULL cleanup'] = (w, wrap)
        x = copy.deepcopy(wrap); x['hyperplane_end_pairs'] = x['hyperplane_end_pairs'][1:]; muts['pair not checked exactly'] = (word, x)
        x = copy.deepcopy(wrap); x['hyperplane_end_pairs'][0]['residual_width'] = 8; muts['width 8 reported'] = (word, x)
        for name, (w, x) in muts.items():
            v, _, _ = check(w, x)
            print(f'  mutant {name!r}: {"REJECTED" if v else "ACCEPTED"}')
            if not v: viol.append(f'mutant {name} accepted')
    if viol:
        print('FAIL'); [print('  ', v) for v in viol[:50]]; sys.exit(1)
    print('PASS')


if __name__ == '__main__':
    main()
