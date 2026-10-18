# SPDX-License-Identifier: Apache-2.0
"""Exact prices of the census scenarios with the pinned rational engines.

kappa() is a transcription of outer_witness in the T37 archive's runtime/code/assemble.py;
check_transcription() binds it to that file's digest and to the literal lines it transcribes.

Usage: price.py CENSUS.json OUT.json

The complex endpoint b of a profile is accepted by both pinned interval
engines at b and rejected at b + 10^-24.  kappa is the largest 10^-18 grid
point accepted by the selected T37 outer witness (seven bootstrap steps and
all 47 strict inequalities), and the next grid point must be rejected.
The baseline must reproduce the selected record exactly.
"""
import importlib.util
import json
import sys
from decimal import Decimal, localcontext
from fractions import Fraction as Q

from common import ROOT, SOURCES, archive_text, canonical, require, sha256

M_COMPLEX = 73


def engine(name):
    path = ROOT / SOURCES['engines']['directory'] / (name + '.py')
    require(sha256(path.read_bytes()) == SOURCES['engines'][name + '.py'], f'engine pin {name}')
    spec = importlib.util.spec_from_file_location('pinned_' + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOMENT, BASE_TWO, OUTER = engine('moment'), engine('base_two_moment'), engine('outer')
OW = SOURCES['outer_witness']
BIT = Q(OW['bit_lower'])
ETA, BETA = Q(OW['eta']), Q(OW['beta'])
GRID = 10 ** 18
BRIDGE = {'semantic': {'C0': {'base': 2, 'exponent': 210000}, 'strict_literal_gap': 1},
          'rows': {'degree_gap': Q(10 ** 6) - Q(51 * 20161, 25)}}


def dec(x, prec=40):
    with localcontext() as ctx:
        ctx.prec = prec
        return str(Decimal(x.numerator) / Decimal(x.denominator))


def endpoint(H, W):
    """Certified complex lower endpoint on the 10^-24 grid (native recurrence, no surcharge)."""
    b = Q(MOMENT.certify(H, M_COMPLEX, W, False)['lower'])
    for z, accept in ((b, True), (b + Q(1, 10 ** 24), False)):
        lo, hi = MOMENT.moment(H, M_COMPLEX, W, z, False)
        blo, bhi = BASE_TWO.moment(M_COMPLEX, W, list(H.items()), z)
        require((hi < 1 and bhi < 1) if accept else (lo > 1 and blo > 1), 'endpoint certification')
    return b


def check_transcription():
    text = archive_text('T37', 'source_member', 'source_sha256')
    for line in ("eta=beta=Q(1,10**24);s=min(c,(1-beta)*bb)-Q(1,10**27)",
                 "chain=[Q(384599,10**10)];cuts=[]", "for _ in range(7):",
                 "old=chain[-1];a=(1-s)*s+s*old;gap=min(s-a,1-a-s,1-a-s*(1-old),1-s)",
                 "q=chain[-1]*(1-2*eta);margin=(1-eta)*q/(1+q);ticks=margin*10**18;"
                 "k=Q((ticks.numerator-1)//ticks.denominator,10**18)",
                 "bridge={'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':1},"
                 "'rows':{'degree_gap':Q(10**6)-Q(51*20161,25)}}"):
        require(line in text, 'transcribed outer_witness line not found: ' + line)


def kappa(b):
    """Replays outer_witness of the selected T37 assembly for complex endpoint b."""
    s = min(BIT, (1 - BETA) * b) - Q(1, 10 ** 27)
    require(0 < s < BIT and s < (1 - BETA) * b, 'effective saving')
    chain = [Q(OW['bootstrap_start'])]
    for _ in range(OW['bootstrap_steps']):
        old = chain[-1]
        a = (1 - s) * s + s * old
        gap = min(s - a, 1 - a - s, 1 - a - s * (1 - old), 1 - s)
        require(old < a < s < 1 - a and gap > 0, 'bootstrap step')
        chain.append(a)
    q = chain[-1] * (1 - 2 * ETA)
    margin = (1 - ETA) * q / (1 + q)
    ticks = margin * GRID
    k = Q((ticks.numerator - 1) // ticks.denominator, GRID)
    out = OUTER.assembly(chain[-1], b, BRIDGE, k, eta=ETA, beta=BETA)
    require(len(out['strict_constraints']) == 47 and all(v > 0 for v in out['strict_constraints'].values()),
            'outer inequalities')
    try:
        OUTER.assembly(chain[-1], b, BRIDGE, k + Q(1, GRID), eta=ETA, beta=BETA)
    except AssertionError:
        pass
    else:
        raise ValueError('next kappa grid point accepted')
    return k, ('bit' if BIT <= (1 - BETA) * b else 'complex')


def drop(H0, H, W, b):
    """60-digit Decimal value of moment(H0) - moment(H) at exponent b, times m*W (ranking only)."""
    with localcontext() as ctx:
        ctx.prec = 60
        bd = Decimal(b.numerator) / Decimal(b.denominator)
        g = lambda P: sum(Decimal(r * n) * ((Decimal(M_COMPLEX) / Decimal(r)).ln() * bd).exp()
                          for r, n in P.items())
        return g(H0) - g(H)


def main():
    check_transcription()
    census = json.loads(open(sys.argv[1]).read())
    W = census['T37']['coverage']['live']
    selected = json.loads((ROOT / SOURCES['selected_record']['path']).read_text())
    assembly = json.loads((ROOT / SOURCES['constructions']['T37']['assembly']).read_text())
    require(Q(assembly['bit_lower']) == BIT, 'bit endpoint differs from the selected assembly')
    rows = {}
    for key, row in census['scenarios'].items():
        H = {int(r): n for r, n in row['profile'].items()}
        b = endpoint(H, W)
        k, binding = kappa(b)
        rows[key] = dict(complex_lower=str(b), complex_decimal=dec(b), kappa=str(k), kappa_decimal=dec(k),
                         binding=binding, rank_mass_neutral=row['rank_mass_neutral'],
                         realizable_in_selected_windows=row['realizable_in_selected_windows'],
                         rank_mass=row['rank_mass'])
    base = rows['baseline']
    require(base['complex_lower'] == assembly['complex_lower'], 'baseline complex endpoint differs from selected')
    require(base['kappa'] == selected['kappa'] == SOURCES['selected_record']['kappa'], 'baseline kappa differs')
    k0 = Q(base['kappa'])
    for row in rows.values():
        dk = Q(row['kappa']) - k0
        row['kappa_gain'] = dec(dk)
        row['kappa_gain_percent'] = dec(100 * dk / k0, 12)
    # Single-helper deferrals: rank by a 60-digit proxy, certify the best one exactly.
    H0 = {int(r): n for r, n in census['scenarios']['baseline']['profile'].items()}
    b0 = Q(base['complex_lower'])
    singles = []
    for i, prof in census['single_helper_profiles'].items():
        singles.append((drop(H0, {int(r): n for r, n in prof.items()}, W, b0), int(i)))
    singles.sort(reverse=True)
    best_gain, best = singles[0]
    Hb = {int(r): n for r, n in census['single_helper_profiles'][str(best)].items()}
    bb = endpoint(Hb, W)
    kb, _ = kappa(bb)
    joint = drop(H0, {int(r): n for r, n in census['scenarios']['defer_all_selected_hosting']['profile'].items()},
                 W, b0)
    with localcontext() as ctx:
        ctx.prec = 60
        total_single = sum(x for x, _ in singles)
    q = lambda x, e: str(x.quantize(Decimal(e)))
    single = dict(changed_profiles=len(singles), unchanged=len(census['single_helper_unchanged']),
                  best_helper=best, best_moment_drop_times_mW=q(best_gain, '1e-12'),
                  sum_of_single_moment_drops_times_mW=q(total_single, '1e-9'),
                  joint_moment_drop_times_mW=q(joint, '1e-9'),
                  best_complex_lower=str(bb), best_kappa=str(kb), best_kappa_decimal=dec(kb),
                  best_kappa_gain=dec(kb - k0), best_kappa_gain_percent=dec(100 * (kb - k0) / k0, 12),
                  ranking='60-digit Decimal drop of m*W*moment at the baseline endpoint; '
                          'only the best row is certified exactly',
                  top10=[dict(helper=i, moment_drop_times_mW=q(x, '1e-12')) for x, i in singles[:10]])
    result = dict(status='PASS_T37_RESTORATION_PRICES', base_commit=SOURCES['base_commit'],
                  engines={k: v for k, v in SOURCES['engines'].items() if k.endswith('.py')},
                  bit_lower=OW['bit_lower'], scenarios=rows, single_helper_deferral=single)
    with open(sys.argv[2], 'w') as f:
        f.write(canonical(result))
    print(result['status'])
    for key, row in rows.items():
        print(f"{key:32s} b {row['complex_decimal'][:22]}  kappa {row['kappa_decimal'][:21]}  "
              f"gain {row['kappa_gain_percent'][:9]}%  {row['binding']}")
    print(f"best single helper {best}: kappa {single['best_kappa_decimal'][:21]} gain {single['best_kappa_gain_percent'][:10]}%")


if __name__ == '__main__':
    main()
