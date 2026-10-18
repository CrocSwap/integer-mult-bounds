"""Retained PR1252/1276 pricing recipe, with explicitly checked exact decisions.

The three unchanged engines retain their authorship and source pins. No native
supplier or full cold replay is performed by this arithmetic command.
"""
import argparse
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import core as C


def prices(profile, root=C.ROOT):
    C.need(__debug__, 'retained engine assertions must remain enabled')
    modules = []
    for name in ('moment', 'base_two_moment', 'outer'):
        spec = importlib.util.spec_from_file_location('idle27_'+name, root/(C.ENGINES+name+'.py'))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        modules.append(m)
    first, second, outer = modules
    bit_record = C.read(root/C.BIT)
    bit = Q(bit_record['nine']['bit_lower'])
    baseline = C.read(root/C.ASSEMBLY)
    C.need(bit == Q(baseline['bit_lower']), 'selected bit endpoint binding')
    bit_profile = {int(k): v for k, v in bit_record['nine']['profile'].items()}
    C.need(sum(r*n for r, n in bit_profile.items()) == 64*28416-10272, 'bit mass')

    def endpoint_checks(hist, m, width, bad, endpoint):
        result = []
        for x, accept in ((endpoint, True), (endpoint+Q(1, 10**24), False)):
            low, high = first.moment(hist, m, width, x, bad)
            l2, h2 = second.moment(m, width, list(hist.items()), x)
            if bad:
                sl, sh = second.moment(m, width, [(1, 32*m*m*sum(hist.values()))], x)
                l2 += sl/10**16
                h2 += sh/10**16
            C.need((high < 1 and h2 < 1) if accept else (low > 1 and l2 > 1), 'moment sign disagreement')
            result.append(dict(endpoint=str(x), accept=accept,
                               mercator=[str(low-1), str(high-1)], base_two=[str(l2-1), str(h2-1)]))
        return result

    bit_checks = endpoint_checks(bit_profile, 64, 28416, True, bit)
    result = {}
    for bad, label in ((False, 'native'), (True, 'conservative')):
        b = Q(first.certify(profile, 73, 14336, bad)['lower'])
        signs = endpoint_checks(profile, 73, 14336, bad, b)
        eta = beta = Q(1, 10**24)
        s = min(bit, (1-beta)*b)-Q(1, 10**27)
        chain = [Q(384599, 10**10)]
        for _ in range(7):
            old = chain[-1]
            a = (1-s)*s+s*old
            C.need(old < a < s < 1-a, 'bootstrap order')
            chain.append(a)
        q = chain[-1]*(1-2*eta)
        ticks = (1-eta)*q/(1+q)*10**18
        kappa = Q((ticks.numerator-1)//ticks.denominator, 10**18)
        bridge = {'semantic': {'C0': {'base': 2, 'exponent': 210000}, 'strict_literal_gap': 1},
                  'rows': {'degree_gap': Q(10**6)-Q(51*20161, 25)}}
        out = outer.assembly(chain[-1], b, bridge, kappa, eta=eta, beta=beta)
        C.need(len(out['strict_constraints']) == 47 and all(v > 0 for v in out['strict_constraints'].values()), 'outer constraints')
        try:
            outer.assembly(chain[-1], b, bridge, kappa+Q(1, 10**18), eta=eta, beta=beta)
        except AssertionError:
            pass
        else:
            raise ValueError('next outer grid point accepted')
        decimal = lambda v, n: '0.'+str(v.numerator*10**n//v.denominator).zfill(n)
        result[label] = dict(endpoint=str(b), endpoint_decimal=decimal(b, 24),
                             kappa=str(kappa), kappa_decimal=decimal(kappa, 18),
                             signs=signs, outer_slacks={k: str(v) for k, v in out['strict_constraints'].items()})
    result['bit'] = dict(endpoint=str(bit), decisions=bit_checks, surcharge=True,
                         scope='Exact repricing of pinned unchanged supplier; circuit not rebuilt')
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--profile', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    C.sources()
    C.need(not args.out.exists(), 'price output already exists')
    profile = {int(k): v for k, v in C.read(args.profile).items()}
    C.write(args.out, prices(profile))
