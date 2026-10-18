"""Special (zero-richer) realisations: Desargues / Pappus realisations over Z with exactly the configuration incidences but
EXTRA collinear point triples or concurrent line triples (so frame coordinates have extra zeros).  Small-integer parameter
grid (fixed order, no randomness); one realisation per distinct extra-triple signature, at most MAXSIG per configuration;
frame-universal char-2 search over GF(2^k), k = 1..4, in every frame (writes data/special.json).

usage: python3 -I -B scripts/special_sweep.py
"""
import itertools, json, os, sys, time
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PKG, 'lib'))
from classical import pappus, desargues, check_config, frames, transform, det3
from universal import universal_realise, check_universal

MAXSIG = 20; LIMIT = 200000; R = range(-3, 4)


def extras(C, n):
    pts, lines = C['points'], C['lines']; inc = {tuple(x) for x in C['incidences']}; pn, ln = C['pnames'], C['lnames']
    ec = [t for t in itertools.combinations(range(n), 3) if det3(*[pts[i] for i in t]) == 0
          and not any(all((pn[i], ln[l]) in inc for i in t) for l in range(n))]
    el = [t for t in itertools.combinations(range(n), 3) if det3(*[lines[i] for i in t]) == 0
          and not any(all((pn[p], ln[l]) in inc for l in t) for p in range(n))]
    return tuple(ec), tuple(el)


def candidates(name):
    if name == 'desargues':
        for x, y in itertools.product(R, R):
            for lam in itertools.product([l for l in R if l], repeat=3):
                yield dict(a=((1, 0, 1), (0, 1, 1), (x, y, 1)), lam=lam)
    else:
        for a2, b1, b2 in itertools.product(range(-15, 16), range(-15, 16), range(-15, 16)):
            if a2 in (0, 1):
                continue
            yield dict(a=(0, 1, a2), b=(0, b1, b2))


def main():
    t0 = time.time(); out = dict(limit=LIMIT, maxsig=MAXSIG, configs={})
    for name, n, mk in [('desargues', 10, desargues), ('pappus', 9, pappus)]:
        sigs = {}; scanned = 0
        for par in candidates(name):
            scanned += 1
            try:
                C = mk(**par)
            except AssertionError:
                continue
            if not check_config(C, n, 3):
                continue
            ex = extras(C, n)
            if (ex[0] or ex[1]) and ex not in sigs and len(sigs) < MAXSIG:
                sigs[ex] = (par, C)
        recs = []
        for ex, (par, C) in sigs.items():
            fr_res = []; worst = 0
            for fr in [('I',)] + frames(C):
                P2, L2 = (C['points'], C['lines']) if fr == ('I',) else transform(C, fr)
                got = None
                for k in (1, 2, 3, 4):
                    r = universal_realise(P2, L2, k, limit=LIMIT)
                    if isinstance(r, dict):
                        assert check_universal(P2, L2, k, r['X'], r['Y'])
                        got = dict(frame=list(fr), k=k, X=r['X'], Y=r['Y']); break
                    if r == 'timeout':
                        got = dict(frame=list(fr), k=None, timeout=k); break
                if got is None:
                    got = dict(frame=list(fr), k=None, excluded_upto=4)
                fr_res.append(got); worst = max(worst, got['k'] or 99)
            recs.append(dict(params={k: list(v) if isinstance(v, tuple) else v for k, v in par.items()},
                             points=[list(p) for p in C['points']], lines=[list(l) for l in C['lines']],
                             extra_point_triples=[list(t) for t in ex[0]], extra_line_triples=[list(t) for t in ex[1]],
                             frames=fr_res))
            print(name, 'extra', ex, 'frames', len(fr_res), 'k-dist',
                  sorted({(x['k'] if x['k'] else 'none') for x in fr_res}, key=str), '%.1fs' % (time.time() - t0), flush=True)
        out['configs'][name] = dict(scanned=scanned, signatures=len(sigs), realisations=recs)
    out['elapsed_s'] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(PKG, 'data', 'special.json'), 'w'), separators=(',', ':'))


if __name__ == '__main__':
    main()
