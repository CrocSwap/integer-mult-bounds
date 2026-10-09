#!/usr/bin/env python3
"""Exact-DFT exponent transfer: the complex suppliers of this repository are batched networks in the sense of
eumemic/exact-dft-bounds (notes/batched-dft-note.tex, Theorem 3.1), so each certified complex moment root a gives
an exact DFT and exact complex convolution in O(n (log n)^(1-a) (log log n)^(3+a)) operations in the exact
complex-arithmetic model of OpenAI's "An explicit power saving for the exact discrete Fourier transform"
(25 September 2026). PROOF.md states the transfer and the three supplier propositions.

This script (Python stdlib only; -O refused)
  1. checks every pin in SOURCE.json (the main certificate of PR #144, the vendored certificates of PR #200 and
     PR #194, byte for byte as `git show <commit>:<path>`);
  2. rebuilds the three per-vertex child histograms from those certificates and compares them with
     certificates/network-children-*.json;
  3. checks each ledger identity (rank sum, deficit = Wm - rank = 2v - 3 loss, largest child < m);
  4. certifies the batched moment at the claimed saving a for each supplier in exact rational arithmetic and
     rejects the next 10^-7 grid point as a control;
  5. with --check, compares the results with expected.json.
usage: python3 -B research/exact-dft-transfer/verify.py [--check] [--write]"""
import argparse
import hashlib
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

if sys.flags.optimize:
    raise SystemExit('Assertions must remain enabled: run without -O')
sys.set_int_max_str_digits(0)
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE / 'scripts'))
from moment import moment_margin  # noqa: E402

SUPPLIERS = {
    'pr144': dict(field=('child_histogram',), profile=lambda d: d, a=Q(607, 1250000)),
    'pr200': dict(field=('complex', 'profile'), profile=lambda d: d['complex']['profile'], a=Q(3327, 5000000)),
    'pr194': dict(field=('complex_profile',), profile=lambda d: d['complex_profile'], a=Q(7009, 10**7)),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def children(name, pin):
    path = REPO / pin['local_path']
    assert sha(path) == pin['sha256'], '%s: %s differs from its pin' % (name, pin['local_path'])
    d = json.loads(path.read_bytes())
    p = SUPPLIERS[name]['profile'](d)
    hist = {str(r): n for r, n in sorted(((int(r), n) for r, n in p['child_histogram'].items()), key=lambda t: t[0]) if n}
    return dict(source=dict(repository=pin['repository'], pr=pin['pr'], commit=pin['commit'], path=pin['path'],
                            field='.'.join(SUPPLIERS[name]['field']), sha256=pin['sha256']),
                m=p['m'], h=p.get('h'), v=p.get('v'), loss=p.get('loss'), R=p.get('R'),
                roles_per_vertex=p['W_per_vertex'], rank_per_vertex=p['rank_per_vertex'],
                deficit_per_vertex=p['deficit_per_vertex'], child_histogram=hist)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--write', action='store_true', help='rewrite certificates/*.json and expected.json')
    o = ap.parse_args()
    src = json.loads((HERE / 'SOURCE.json').read_text())
    out = {}
    for name, spec in SUPPLIERS.items():
        pin = src['suppliers'][name]
        c = children(name, pin)
        cpath = HERE / 'certificates' / ('network-children-%s.json' % name)
        if o.write:
            cpath.write_text(json.dumps(c, indent=1) + '\n')
        committed = json.loads(cpath.read_text())
        assert committed == c, '%s: committed children differ from the pinned certificate' % name
        m, W = c['m'], c['roles_per_vertex']
        hist = {int(r): n for r, n in c['child_histogram'].items()}
        rank = sum(r * n for r, n in hist.items())
        assert rank == c['rank_per_vertex'] and W * m - rank == c['deficit_per_vertex'], '%s: ledger identity' % name
        if c['v'] is not None and c['loss'] is not None:
            assert c['deficit_per_vertex'] == 2 * c['v'] - 3 * c['loss'], '%s: deficit 2v - 3 loss' % name
        a = spec['a']
        margin, total = moment_margin(m, W, hist, a)
        assert margin > 0, '%s: moment not below W at a = %s' % (name, a)
        nxt = a + Q(1, 10**7)
        margin_next, _ = moment_margin(m, W, hist, nxt)
        assert margin_next <= 0, '%s: the next 10^-7 grid point also passes; raise the claim' % name
        scale = 10**30
        upper = -((-total.numerator * scale) // total.denominator)
        rec = dict(children_sha256=sha(cpath), m=m, roles_per_vertex=W, rank_per_vertex=rank,
                   deficit_per_vertex=W * m - rank, max_child=max(hist), a=str(a), theta=str(1 - a),
                   moment_upper_bound='%d/10^30' % upper, margin_lower_bound='%d/10^30' % (W * scale - upper),
                   next_grid_point=str(nxt), next_grid_point_rejected=True, passed=True)
        mpath = HERE / 'certificates' / ('moment-%s.json' % name)
        if o.write:
            mpath.write_text(json.dumps(rec, indent=1) + '\n')
        assert json.loads(mpath.read_text()) == rec, '%s: committed moment certificate differs' % name
        out[name] = dict(a=str(a), theta=str(1 - a), m=m, W=W, deficit=W * m - rank, max_child=max(hist),
                         margin=float(margin), commit=pin['commit'][:7])
        print('%s: m %d W %d deficit %d max child %d  a = %s = %.4e  margin %.3e  next grid point rejected'
              % (name, m, W, W * m - rank, max(hist), a, float(a), float(margin)))
    for name, pin in src['references'].items():
        assert sha(REPO / pin['local_path']) == pin['sha256'], 'reference %s differs from its pin' % name
    best = max(out, key=lambda k: Q(out[k]['a']))
    result = dict(suppliers=out, best=best, theta=out[best]['theta'], framework=src['framework'])
    if o.write:
        (HERE / 'expected.json').write_text(json.dumps(result, indent=1, sort_keys=True) + '\n')
    if o.check:
        assert json.loads((HERE / 'expected.json').read_text()) == json.loads(json.dumps(result, sort_keys=True)), 'results differ from expected.json'
        print('PASS results equal expected.json')
    print('PASS exact-dft-transfer: theta = 1 - %s with the %s supplier' % (out[best]['a'], best))


if __name__ == '__main__':
    main()
