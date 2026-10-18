"""Frame-universal CR2 certificates (writes data/universal.json).

For each configuration (Desargues 10_3, Pappus 9_3) and each structured frame (three non-collinear configuration points sent
to e_1, e_2, e_3, or three non-concurrent configuration lines sent to the coordinate lines), plus the identity frame of the
base realisation, search GF(2^k), k = 1..4 in order, for a frame-universal char-2 realisation (lib/universal.py).
For the identity frame, and for one frame per configuration, also record which k are exhaustively excluded.

usage: python3 -I -B scripts/universal_sweep.py
"""
import json, os, sys, time
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PKG, 'lib'))
from classical import pappus, desargues, check_config, frames, transform
from universal import universal_realise, check_universal

LIMIT = 200000


def main():
    out = dict(limit=LIMIT, configs={})
    t0 = time.time()
    for C, n in [(desargues(), 10), (pappus(), 9)]:
        assert check_config(C, n, 3)
        recs = []
        for fr in [('I',)] + frames(C):
            if fr == ('I',):
                P2, L2 = C['points'], C['lines']
            else:
                P2, L2 = transform(C, fr)
            rec = dict(frame=list(fr), P=[list(p) for p in P2], L=[list(l) for l in L2], excluded=[], timeout=[])
            for k in (1, 2, 3, 4):
                r = universal_realise(P2, L2, k, limit=LIMIT)
                if isinstance(r, dict):
                    assert check_universal(P2, L2, k, r['X'], r['Y'])
                    rec.update(k=k, X=r['X'], Y=r['Y'])
                    break
                (rec['excluded'] if r is None else rec['timeout']).append(k)
            recs.append(rec)
            print(C['name'], fr, 'k=%s' % rec.get('k'), 'excluded', rec['excluded'], 'timeout', rec['timeout'],
                  '%.1fs' % (time.time() - t0), flush=True)
        out['configs'][C['name']] = recs
    out['elapsed_s'] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(PKG, 'data', 'universal.json'), 'w'), separators=(',', ':'))


if __name__ == '__main__':
    main()
