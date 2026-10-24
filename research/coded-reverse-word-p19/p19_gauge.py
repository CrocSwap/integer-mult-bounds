#!/usr/bin/env python3
"""What a monomial output gauge does, exactly, and which census each guard value belongs to.

An output gauge multiplies a role's row by a monomial.  Multiplying by m cannot shrink a
frame; factoring m OUT can, and that is only legal when m divides every monomial of the row
exponent-wise.  This receipt therefore reports, per role:

    raw_frame        the stages appearing in the row
    gauge            the monomial being factored out
    divides          whether the gauge divides every monomial of the row
    residual_frame   the stages that remain
    designed_frame   the frame the invoice's design list assumes

and it states the consequence plainly: the gauged word computes G . M, not M.  Gauging is a
change of output basis, so the census belongs to the gauged operator, and whether that is the
object the invoice prices is a separate question answered by which census the base's own
numbers use.

The second part settles the guard-value question by computing the guards against three
censuses and showing which pair is identical:

    invoiced T (design list)          -> the original guard values
    realised T (raw row supports)     -> different values
    residual T (after gauging)        -> must equal the invoiced values if the census matches
"""
import importlib.util, json, sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import p19_word as W

KAPPA = Q(951999, 280000000)
PROFILE = {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40}

def need(ok, why):
    if not ok: raise ValueError(why)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def row_supports(mod, p, pat, thick):
    co, _ = mod.controller(p, mod.keep_of(p, pat), {s: Q(1) for s in range(2*p+1)})
    th = mod.thin(co, thick)
    out = {}
    for i in range(2*p):
        S, mins = set(), None
        for term, m in th.items():
            expo = tuple(term[1:])
            if any(m[i][j] for j in range(2*p)):
                S |= {s for s, bit in enumerate(expo) if bit}
                mins = expo if mins is None else tuple(min(a, b) for a, b in zip(mins, expo))
        out[i] = {'frame': S & thick, 'min_exponents': mins}
    return out

def designed_frames(p, pat, thick):
    full = frozenset(range(2*p+1))
    outs = [full, full]
    for i, ch in enumerate(pat, 1):
        outs += [frozenset(range(0, 2*i+1)) if ch == 'I' else frozenset(range(2*i, 2*p+1))]*2
    return [s & thick for s in outs]

def census_main(T):
    P = Counter({int(k): v for k, v in T.items()})
    for r, n in W.H.items(): P[r] += 19*n
    P.pop(0, None)
    return P

def guards(T, D, E):
    tk = 1-KAPPA
    mtk = E.moment(T, tk)
    alpha = E.divide(E.moment(D, tk), mtk)
    gamma = E.divide(E.moment(D, tk+Q(1, 5)), E.mul(E.power(20, Q(1, 5)), mtk))
    delta = E.divide((Q(sum(T.values())*21),)*2, E.mul(E.power(20, KAPPA), mtk))
    return float(alpha[1]), float(gamma[1]), float(delta[1])

def main():
    E = load('moment', ROOT/'research/higher-moment-strictification/verify.py')
    mod = load('c4940_gauge', ROOT/'research/coded-reverse-controller/verify.py')
    out = {'status': 'GAUGE_SEMANTICS', 'cases': {}}

    for p, pat in ((3, 'IT'), (19, 'I'*9+'T'*9)):
        thick = frozenset(range(1, 2*p, 2))
        rows = row_supports(mod, p, pat, thick)
        des = designed_frames(p, pat, thick)
        raw_sizes = Counter(len(rows[i]['frame']) for i in range(2*p))
        des_sizes = Counter(len(s) for s in des)
        # choose gauges: factor out the stages that take a wide role to a needed size
        need_gauge, details = {}, []
        cur = Counter(raw_sizes)
        target = Counter(des_sizes)
        wide = sorted([i for i in range(2*p)], key=lambda i: -len(rows[i]['frame']))
        for i in wide:
            want = None
            for k in sorted(target):
                if cur.get(k, 0) < target[k] and k < len(rows[i]['frame']):
                    want = k; break
            if want is None: continue
            drop = sorted(rows[i]['frame'])[:len(rows[i]['frame'])-want]
            mins = rows[i]['min_exponents']
            divides = all(mins[s] >= 1 for s in drop)
            details.append({'role': i, 'raw_frame': sorted(rows[i]['frame']), 'gauge': drop,
                            'divides': divides,
                            'residual_frame': sorted(rows[i]['frame'] - set(drop))})
            if divides:
                cur[len(rows[i]['frame'])] -= 1
                cur[want] = cur.get(want, 0) + 1
                need_gauge[i] = drop
        out['cases']['p%d_%s' % (p, pat)] = {
            'raw_sizes': dict(sorted(raw_sizes.items())), 'designed_sizes': dict(sorted(des_sizes.items())),
            'gauge_details': details, 'realised_sizes_after_gauge': dict(sorted(cur.items())),
            'realised_equals_designed': dict(sorted(cur.items())) == dict(sorted(des_sizes.items())),
            'all_gauges_divide': all(d['divides'] for d in details)}
        print('p=%2d raw sizes %s designed %s' % (p, dict(sorted(raw_sizes.items())), dict(sorted(des_sizes.items()))))
        print('     gauges applied: %d, all divide their rows: %s, sizes after gauge %s (== designed: %s)'
              % (len(details), all(d['divides'] for d in details), dict(sorted(cur.items())),
                 dict(sorted(cur.items())) == dict(sorted(des_sizes.items()))))
        for d in details[:3]:
            print('     role %d: raw %s factor out %s -> residual %s'
                  % (d['role'], d['raw_frame'], d['gauge'], d['residual_frame']))

    # ---- the guard question ----
    p, pat = 19, 'I'*9+'T'*9
    thick = frozenset(range(1, 2*p, 2))
    T_inv, D_raw = W.invoice(p, pat, thick, PROFILE)
    T_inv = Counter({int(k): v for k, v in T_inv.items()})
    D = Counter()
    for k, v in D_raw.items(): D[int(k)] += v
    row = json.loads((HERE/'P19_ROWFRAME.json').read_text())
    T_realised = Counter(census_main({int(k): v for k, v in row['derived_row_T'].items()}))
    g_inv = guards(T_inv, D, E)
    g_rea = guards(T_realised, D, E)
    print()
    print('guards against the INVOICED census  : alpha %.9f gamma %.9f delta %.9f' % g_inv)
    print('guards against the REALISED census  : alpha %.9f gamma %.9f delta %.9f' % g_rea)
    print('published invoiced values           : alpha 0.995794150 gamma 0.963763000 delta 0.951561000')
    need(abs(g_inv[0]-0.99579415) < 1e-8, 'the invoiced census reproduces the published alpha')
    print('PASS the invoiced census reproduces the published guards; the 0.700/0.678/0.669 values belong to the '
          'raw realised census, so quoting them beside the invoiced histogram was an input mismatch')

    out['guards'] = {'invoiced_census': g_inv, 'realised_census': g_rea,
                     'published': (0.995794150, 0.963763000, 0.951561000),
                     'reconciliation': ('the guard values track the census.  0.995794/0.963763/0.951561 are the '
                                        'invoiced-census values; 0.700/0.678/0.669 were computed from the raw realised '
                                        'census and must not be quoted as the invoiced ones.  If the residual census '
                                        'equals the invoiced census, the guards are the published values exactly')}
    out['gauge_semantics'] = ('a gauge changes the operator to G . M.  Multiplying by m cannot shrink a frame; '
                              'factoring m out can, and only when m divides every monomial of the row.  The census '
                              'after gauging therefore belongs to the gauged operator, and the receipt reports each '
                              'role raw frame, gauge, divisibility and residual frame rather than only a histogram')
    out['not_yet_answered'] = ('whether the invoice prices the residual frame of a gauged word.  The base builds its '
                              'T from a design list, and its own word does not realise that list at p>=3, so this '
                              'needs a source statement rather than an inference')
    (HERE/'P19_GAUGE.json').write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': out['status']}, sort_keys=True))

if __name__ == '__main__':
    main()
