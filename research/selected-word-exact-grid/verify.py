#!/usr/bin/env python3
"""Exact internal grid of the selected complex word: ceil(9 lambda/2)+6 extra fractional bits, attained.

Standard library only; about one to two minutes.  Inputs, pinned by SHA256 in SOURCES.json:
  * research/eight-owned-relations/WORD.json.gz - the #5383 eight-relation body (backward and forward programs)
    used by the selected #5383 -> #5392 -> #5398 -> #5413 chain;
  * research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz - Cao Yifan's #4610 source word;
  * the repository's exact Gaussian-dyadic Clifford compiler clifford_exact.py (canonical charts).

Model (PR2772 / PR2813 / p104-joint-prefix-grid): public physical inputs, including dirty helpers and owned
entries, are arbitrary arrays on 2^-f Z[i]. At an atomic cut a field standing in frame F holds
    sum_s c_s  U_s^(tensor lambda)  V_s(0),
with exact rational scalar coefficients c_s (one per input s and native warp word) and U_s a product of canonical
charts, chart inverses and native maps; for a term without a warp word U_s = Delta_F Delta_{I_s}^-1. Every such
U_s is an exact dyadic Gaussian Clifford on 9 binary coordinates (inherited: kappa-round3-warp-20261022's exact
Clifford admission of all native G operators). A Clifford column with Fourier rank r has 2^r nonzero entries,
each a Gaussian unit times 2^(-r/2); its reduced denominator is exactly 2^ceil(r/2) (Ross Richardson's lemma,
retained in p104-retimed-internal-grid). Under the payload lift r becomes r*lambda.

Checks, for both words and both programs:
  1. pinned inputs; exact replay of the scalar program; every coefficient is dyadic (no odd denominator);
  2. per term, the Fourier rank of Delta_F Delta_{I_s}^-1 from clifford_exact; warp-word or owned-entry terms get
     the universal rank 9; sanity: the chart-change rank equals the paid rank of every climb;
  3. guard g(lambda) = max over terms of v2(den c_s) + ceil(r lambda / 2): for the selected body
     backward ceil(9 lambda/2) + 6, forward ceil(9 lambda/2) + 5;
  4. attainment: a witness term whose input occurs exactly once in its row, with v2 = 6 (backward) or 5 (forward)
     and computed rank 9; inputs are independent, so no other term can cancel it and the guard is necessary;
  5. magnitude: max sum_s |c_s| = L bounds every stored component by H L 2^(9 lambda/2);
  6. the stored RESULT.json equals the rebuild.
Usage: python3 -I -B verify.py [--write]
"""
import argparse, collections, gzip, hashlib, importlib.util, json, sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
WORDS = {'eight_relation_body': ROOT / 'research' / 'eight-owned-relations' / 'WORD.json.gz',
         'source_4610': ROOT / 'research' / 'kappa-round3-warp-20261022' / 'ACTUAL-WORD.json.gz'}
CLIFFORD = ROOT / 'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py'
EXPECT = {('eight_relation_body', 'backward'): 6, ('eight_relation_body', 'forward'): 5,
          ('source_4610', 'backward'): 6, ('source_4610', 'forward'): 5}


def require(ok, message):
    if not ok:
        raise SystemExit('FAIL: ' + message)


def pinned_inputs():
    rows = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))['files']
    for row in rows:
        if row['usage'] == 'input':
            data = (ROOT / row['path']).read_bytes()
            require(hashlib.sha256(data).hexdigest() == row['sha256'], 'input drift: ' + row['path'])


def clifford():
    spec = importlib.util.spec_from_file_location('selected_grid_clifford_exact', CLIFFORD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def v2(n):
    n = abs(n)
    return (n & -n).bit_length() - 1


def add_into(dst, src, q):
    for k, v in src.items():
        nv = dst.get(k, 0) + q * v
        if nv:
            dst[k] = nv
        else:
            dst.pop(k, None)


class Ranks:
    def __init__(self, ce, canonical):
        self.ce, self.c, self.charts, self.cache = ce, canonical, {}, {}
        self.n = canonical['h']

    def chart(self, f):
        if f not in self.charts:
            self.charts[f] = self.ce.canonical_frame(self.n, self.c['frames'][f])
        return self.charts[f]

    def rank(self, F, I):
        key = (F, I)
        if key not in self.cache:
            op = self.chart(I).adjoint().then(self.chart(F))
            self.cache[key] = self.ce.rank([x for x, z, p in op.tab[self.n:]])
        return self.cache[key]


def census(word, orient, ranks):
    c = word['canonical']; nl = len(c['start']); prog = word['programs'][orient]
    require(c['h'] == 9, 'nine binary coordinates')
    backward = orient == 'backward'
    rows = {('L', i): {(('L', i), ()): Q(1)} for i in range(nl)}
    rows.update({('C', j): {(('C', j), ()): Q(1)} for j in range(9)})
    frames = {('L', i): c['start'][i] for i in range(nl)}
    frames.update({('C', j): None for j in range(9)})
    pairs = collections.Counter(); witness = {}; odd = 0; l1 = Q(0); climbs = 0

    def stat(t, role):
        nonlocal odd, l1
        r_ = rows[role]
        if not r_:
            return
        F = frames[role]
        per_input = collections.Counter(inp for inp, wd in r_)
        l1 = max(l1, sum(abs(q) for q in r_.values()))
        for (inp, wd), q in r_.items():
            if q.denominator >> v2(q.denominator) != 1:
                odd += 1
            if wd or inp[0] == 'C' or F is None:
                r = 9
            else:
                r = ranks.rank(F, c['start'][inp[1]])
            key = (v2(q.denominator), r)
            pairs[key] += 1
            if key not in witness and per_input[inp] == 1 and not wd and inp[0] == 'L':
                witness[key] = [t, list(role), list(inp), str(q)]
    for t, e in enumerate(prog):
        k = e[0]
        if k == 'warp':
            X = tuple(e[1]); op = e[2]
            sym = (1 if op > 0 else -1) * (abs(op) + (10 ** 6 if backward else 0))
            rows[X] = {(r_, wd[1:] if wd and wd[0] == -sym else (sym,) + wd): q for (r_, wd), q in rows[X].items()}
            frames[X] = e[4]
        elif k == 'climb':
            require(ranks.rank(e[4], e[3]) == e[5], 'chart-change Fourier rank equals the paid climb rank')
            climbs += 1
            frames[('L', e[2])] = e[4]
        elif k == 'center':
            frames[('C', e[1])] = e[3]
        elif k == 'zero_retag':
            require(not rows[tuple(e[1])], 'zero identity on an identically zero row')
            frames[tuple(e[1])] = e[3]
        elif k == 'scalar':
            g, fr_ = e[1], e[2]; d_ = tuple(g[1])
            if g[0] == 'clear':
                rows[d_] = {}
            elif g[0] == 'copy':
                rows[d_] = dict(rows[tuple(g[2])])
            elif g[0] == 'add':
                add_into(rows[d_], rows[tuple(g[2])], Q(g[3], g[4]))
            elif g[0] == 'scale':
                rows[d_] = {kk: Q(g[2], g[3]) * v for kk, v in rows[d_].items()}
            else:
                require(False, 'unknown scalar operation')
            if fr_ is not None:
                frames[d_] = fr_
            stat(t, d_)
        else:
            require(k in ('adapter', 'phase'), 'unknown event')
    require(odd == 0, 'every scalar coefficient is dyadic')
    keys = sorted(pairs)
    front = [k for k in keys if not any(o != k and o[0] >= k[0] and o[1] >= k[1] for o in keys)]
    guard = {lam: max(a - (-b * lam // 2) for a, b in keys) for lam in (1, 2, 3, 4)}
    return dict(front=[list(k) for k in front], guard=guard, max_l1=str(l1), climbs_checked=climbs,
                witness={str(list(k)): witness.get(k) for k in front})


def build():
    pinned_inputs()
    ce = clifford()
    out = {}
    for name, path in WORDS.items():
        word = json.loads(gzip.decompress(path.read_bytes()))
        ranks = Ranks(ce, word['canonical'])
        for orient in ('backward', 'forward'):
            res = census(word, orient, ranks)
            s = EXPECT[(name, orient)]
            require(res['front'] == [[s, 9]], 'Pareto front of (v2, rank) is {(%d, 9)}: %s %s' % (s, name, orient))
            require(all(res['guard'][lam] == s - (-9 * lam // 2) for lam in res['guard']), 'guard ceil(9 lambda/2) + %d' % s)
            require(res['witness'][str([s, 9])] is not None, 'attaining witness with a single occurrence of its input')
            res['guard_formula'] = 'ceil(9 lambda/2) + %d' % s
            out[name + '/' + orient] = res
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    result = build()
    path = HERE / 'RESULT.json'
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    if args.write:
        path.write_bytes(text.encode('utf-8'))
    require(path.exists() and json.loads(path.read_text(encoding='utf-8')) == json.loads(text), 'stored RESULT.json equals the rebuild')
    print('PASS_SELECTED_WORD_EXACT_GRID_CEIL_9L_2_PLUS_6')


if __name__ == '__main__':
    main()
