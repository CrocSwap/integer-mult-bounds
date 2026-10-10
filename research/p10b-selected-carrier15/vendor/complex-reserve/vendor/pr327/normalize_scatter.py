#!/usr/bin/env python3
"""normalize_scatter.py: write the scatter of a gcert/1 program as the star rule by re-signing retained totals.

gcert_emit.py (PR #256, vendored unchanged) keeps every slot in a unit lam (wanted = lam * stored, the convention of
Sussman's gxconv.py). When the exact lift leaves a retained total k in a register whose unit lam_k is not 1, the
emitter writes the scatter as a table: row t, column k is the star coefficient (1/3 if coordinate k lies in port t,
-1/6 otherwise) times lam_k. The five-stage packages' complex code reads the star rule only. If every lam_k is +1 or
-1, flipping the sign convention of the registers with lam_k = -1 over the whole program (P -> D P D with
D = diag(+-1)) gives the same map from sources to targets with the star rule: every gate coefficient on an edge
with exactly one endpoint in a flipped register is negated, and the scatter column of a flipped total becomes the
star column. Registers, frames, gates, start and final labels, retained totals, blocks and N are unchanged; only
coefficient signs, the scatter field and the derived_from note change. A program already in star form is returned
unchanged. verify.py runs gx.check1 (and Sussman's gxcore mirror) on the result and compares it with the input.

Prepared by DreamingOfClouds with Anthropic Claude assistance (Apache-2.0).
usage: normalize_scatter.py IN.json[.gz] OUT.json[.gz]
"""
import copy
import gzip
import json
import sys
from fractions import Fraction as Q

if sys.flags.optimize:
    raise SystemExit('Assertions must remain enabled: run without -O')
STAR = dict(inside=[1, 3], outside=[-1, 6])


def star(c, t, k):
    return Q(1, 3) if c['ports'][t] >> k & 1 else Q(-1, 6)


def units(c):
    """lam_k of every retained total, read off a table scatter (None for a star scatter)"""
    sc = c['scat']
    if 'table' not in sc:
        assert sc == STAR, 'a star scatter must be 1/3 inside, -1/6 outside'
        return None
    h, v = c['h'], c['v']
    assert len(sc['table']) == v
    lam = {}
    for t, row in enumerate(sc['table']):
        assert [k for k, _, _ in row] == list(range(h)), 'table row %d does not list the coordinates 0..h-1 in order' % t
        for k, a, b in row:
            q = Q(a, b) / star(c, t, k)
            assert lam.setdefault(k, q) == q, 'column %d is not the star column times one unit' % k
    return lam


def normalize(c):
    lam = units(c)
    if lam is None:
        return c, dict(raw_scatter='star', flipped_coordinates=[], flipped_registers=[], changed_gates=0, changed_coefficients=0)
    assert all(q in (1, -1) for q in lam.values()), 'units other than +-1 cannot be normalized by a sign flip: %s' % lam
    v = c['v']
    ret = {k: s for k, s, _ in c['ret']}
    assert sorted(ret) == list(range(c['h'])) and len(set(ret.values())) == len(ret), 'one retained total per coordinate'
    flip = {ret[k] for k, q in lam.items() if q == -1}
    assert all(s >= 2 * v for s in flip), 'only slots are re-signed'
    c2 = copy.deepcopy(c)
    gates = coefficients = 0
    for ph in ('A', 'B'):
        for g in c2[ph]:
            assert g[0] in ('out', 'in'), 'gate kind %r' % (g[0],)
            pivot = g[2] in flip
            hit = False
            for term in g[3]:
                if pivot != (term[0] in flip):       # exactly one endpoint of this edge is re-signed
                    term[1] = -term[1]
                    coefficients += 1
                    hit = True
            gates += hit
    c2['scat'] = dict(STAR)
    c2['derived_from'] = c['derived_from'] + ' + normalize_scatter.py (registers %s re-signed; star scatter)' % sorted(flip)
    return c2, dict(raw_scatter='table', flipped_coordinates=sorted(k for k, q in lam.items() if q == -1),
                    flipped_registers=sorted(flip), changed_gates=gates, changed_coefficients=coefficients)


def same_shape(a, b):
    """True when two programs differ at most in coefficient signs, the scatter and derived_from"""
    keys = set(a) | set(b)
    for k in keys - {'A', 'B', 'scat', 'derived_from'}:
        if a.get(k) != b.get(k):
            return False
    for ph in ('A', 'B'):
        if len(a[ph]) != len(b[ph]):
            return False
        for g, h in zip(a[ph], b[ph]):
            if g[:3] != h[:3] or g[4:] != h[4:] or len(g[3]) != len(h[3]):
                return False
            if any(x[0] != y[0] or x[2] != y[2] or abs(x[1]) != abs(y[1]) for x, y in zip(g[3], h[3])):
                return False
    return True


def main():
    src, dst = sys.argv[1:3]
    raw = gzip.decompress(open(src, 'rb').read()) if src.endswith('.gz') else open(src, 'rb').read()
    c2, report = normalize(json.loads(raw))
    data = json.dumps(c2, separators=(',', ':')).encode()
    open(dst, 'wb').write(gzip.compress(data) if dst.endswith('.gz') else data)
    print(json.dumps(report))


if __name__ == '__main__':
    main()
