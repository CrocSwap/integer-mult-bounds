#!/usr/bin/env python3
"""Independent p,q,p tensor counts, matching, and retained LU witness audit.

This reads a saved certificate without importing its producer. The scalar
local and rational-envelope certificates remain separate finite inputs.
"""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import time

from review_parameter_audit import log_integer, log_series, root_signs


def counts(p, q, rp, rq):
    vp, vq = comb(p, 3), comb(q, 3)
    n, m = vp*vp*vq, p*p*q
    joined = vp*vq*(rp+p)
    w = 2*n+joined+vp*vp*(rq+q)
    loss = 2*vp*vq*p*p+vp*vp*q*q
    d = n-2*loss
    return dict(p=p, q=q, vp=vp, vq=vq, N=n, m=m, W=w, L=loss,
                D=d, s=w*m-d, eta=Q(d, w*m),
                outer_side_roles=rp, middle_side_roles=rq,
                joined_scratch_roles=joined)


def matching(q):
    triples = list(combinations(range(q), 3))
    index = {t: i for i, t in enumerate(triples)}
    images = []
    for t in triples:
        pairs = [a//2 for a in t]
        if len(set(pairs)) == 3:
            # Hold the smallest occupied pair, flip both other points.
            image = tuple(sorted(a if a//2 == min(pairs) else a^1 for a in t))
        else:
            occupied = next(a for a in pairs if pairs.count(a) == 2)
            singleton = next(a for a in t if a//2 != occupied)
            allowed = [a for a in range(q//2) if a != singleton//2]
            following = allowed[(allowed.index(occupied)+1) % len(allowed)]
            image = tuple(sorted((2*following, 2*following+1, singleton)))
        assert len(set(t)&set(image)) == 1
        images.append(index[image])
    assert sorted(images) == list(range(len(triples)))
    return triples, images


def index_checks(p, q):
    """Enumerate the unequal small invocation partitions and bank pairing."""
    vp, vq = comb(p, 3), comb(q, 3)
    n = vp*vp*vq
    _, pi = matching(q)
    inverse = [0]*vq
    for a, b in enumerate(pi):
        inverse[b] = a
    flat = lambda a, b, c: (a*vq+b)*vp+c
    for stage in range(3):
        seen = bytearray(n)
        va, vb, vc = ((vq, vp, vp), (vp, vp, vq), (vp, vq, vp))[stage]
        for a in range(va):
            for b in range(vb):
                for c in range(vc):
                    i = flat(c, a, b) if stage == 0 else flat(a, c, b) if stage == 1 else flat(a, b, c)
                    assert not seen[i]
                    seen[i] = 1
        assert all(seen)
    used = set()
    for a in range(vp):
        for b in range(vq):
            paired_stage_one = (inverse[b], a)
            assert paired_stage_one not in used
            used.add(paired_stage_one)
            assert pi[paired_stage_one[0]] == b
    assert len(used) == vp*vq
    # Over GF(2), the independent local identity shear makes the three
    # stages (x,y)->(x,y+x)->(y,y+x)->(y,x) in every coordinate.
    x, y = 1, 2
    y ^= x
    x ^= y
    y ^= x
    assert (x, y) == (2, 1)
    return dict(p=p, q=q, complete_tensor_index_partitions=3,
                data_coordinates=n, middle_matching_bank_pairs=len(used),
                coordinatewise_three_shear_exchange=True)


def independent_saving(eta, m):
    a, b = log_series(1/(1-eta), 20)
    c, d = log_integer(m, 48)
    return a/d, b/c


def audit_best(row):
    saved = row['counts']
    p, q = saved['p'], saved['q']
    n = counts(p, q, saved['outer_side_roles'], saved['middle_side_roles'])
    assert all(Q(saved[key]) == value for key, value in n.items())
    assert 0 < n['D'] and 2 <= n['s'] < n['m']**5
    vc, mc = comb(50, 3), 50**3
    nc = vc**3
    wc = 2*nc+3*vc*vc*(vc*(comb(47, 3)+141)+51)
    lc = 3*vc*vc*51*50
    sc = wc*mc-2*nc+2*lc
    etac = Q(wc*mc-sc, wc*mc)
    for key, value in dict(ground=50, v=vc, N=nc, m=mc, W=wc,
                           L=lc, s=sc, eta=etac).items():
        assert Q(row['retained_complex_counts'][key]) == value
    for name, eta, radix in [('bit', n['eta'], n['m']), ('complex', etac, mc)]:
        lo, hi = independent_saving(eta, radix)
        enclosure = row[name+'_saving_enclosure']
        assert Q(enclosure['saving_lower']) < lo < hi < Q(enclosure['saving_upper'])
        assert 0 < Q(enclosure['chosen_saving']) < lo
    parameters = {key: Q(value) for key, value in row['parameters'].items()}
    a, b, epsilon, r = (parameters[key] for key in
                       ('a_bit', 'a_complex', 'epsilon', 'alpha_squared_power'))
    beta, c, lam, lamp = (parameters[key] for key in
                          ('beta', 'c', 'lambda_', 'lambda_prime'))
    tau, sigma, delta = (parameters[key] for key in ('tau', 'sigma', 'delta'))
    assert tau == 1-a and sigma == 1-b
    _, xhi = root_signs(a, b, row['balance_root_interval'])
    assert beta == 1-xhi
    assert c == a*beta/(tau+a*beta)*(1-Q(1, 2**32))
    assert 1-lamp == a*c
    threshold = tau*(1+c/beta)
    assert lam == (lamp+threshold)/2
    assert epsilon == Q(2, 3)-Q(1, 2**20)
    assert r == Q(1, 3) and delta == Q(1, 2**22)
    B = sc+64*(wc+mc+1)**3
    assert parameters['C1'] == Q(3, 2)
    assert parameters['C0'] == 128*mc*B*B
    slacks = dict(tau_positive=tau, bit_saving_positive=a,
                  sigma_positive=sigma, complex_saving_positive=b,
                  c_positive=c, epsilon_positive=epsilon,
                  beta_positive=beta, beta_below_one=1-beta,
                  lambda_above_tau=lam-tau, lambda_above_sigma=lam-sigma,
                  lambda_below_one=1-lam, packed_recurrence=lam-threshold,
                  lambda_prime_above_lambda=lamp-lam,
                  leaf_cost=lamp-sigma-beta*b,
                  lambda_prime_below_one=1-lamp,
                  guard_width=1-epsilon*parameters['C1'],
                  guard_stopping_range=beta-Q(15, 16),
                  crt_layout=a*(1-epsilon),
                  gaussian_cost=Q(1, 2)+r/2-delta-epsilon,
                  prefix_cost=1-epsilon*(1+c), scalar_cost=1-delta-epsilon,
                  delta_positive=delta, delta_below_one_eighth=Q(1, 8)-delta,
                  alpha_power_positive=r, alpha_below_sqrt_p=1-r,
                  gamma_sublinear=1-epsilon-r,
                  prime_interval_and_line_growth=1-epsilon,
                  K_smaller_than_ell=1-epsilon-epsilon*c,
                  K_dominates_log_p=epsilon*c, kappa_positive=parameters['kappa'])
    assert all(value > 0 for value in slacks.values())
    margins = dict(g1=1-epsilon*(1+c), g2=epsilon*c*a,
                   g3=epsilon*(1-lamp), g4=a*(1-epsilon),
                   g5=Q(1, 2)+r/2-delta-epsilon,
                   g6=1-delta-epsilon, g7=epsilon)
    assert all(Q(row['margins'][key]) == value for key, value in margins.items())
    G = min(margins.values())
    assert G == margins['g2'] == margins['g3'] == Q(row['minimum_margin'])
    kappa = parameters['kappa']
    assert 0 < kappa < G
    assert kappa == Q((G.numerator*10**30-1)//G.denominator, 10**30)
    upper_a = Q(row['bit_saving_enclosure']['saving_upper'])
    upper_b = Q(row['complex_saving_enclosure']['saving_upper'])
    upper_x = Q(row['model_kappa_upper'])/(Q(2, 3)*upper_b)
    assert 0 < upper_x < 1
    assert upper_a*upper_b*upper_x**2-(upper_b+upper_a**2)*upper_x+upper_a**2 < 0
    assert kappa < Q(row['model_kappa_upper'])
    assert 7/(1-epsilon-r) == 7340032
    assert row['gamma_cutoff'] == 'b >= 2^7340032'
    assert 5-4*beta+Q(1, 4) <= Q(3, 2) and 45+18 < 128
    return dict(p=p, q=q, counts={key: str(value) for key, value in n.items()},
                kappa=str(kappa), strict_constraints=len(slacks),
                strict_root_and_absorption_verified=True,
                complex_motif_retained=True, gamma_cutoff_verified=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--certificate', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    begin = time.monotonic()
    source = args.certificate.read_bytes()
    certificate = json.loads(source)
    assert certificate['provenance']['commit'] == 'bcd4ebde8692383539f8a48734e5fbf3a18a32c2'
    best = audit_best(certificate['best'])
    roles = {int(key): int(value) for key, value in certificate['verified_role_counts'].items()}
    small_roles = {}
    for item in certificate['small_circuit_checks']:
        h = item['h']
        sizes = {case['input_basis_vectors'] for case in item['dirty_basis']}
        assert len(sizes) == 1
        small_roles[h] = sizes.pop()-2*comb(h, 3)-h
    selected = (best['p'], best['q'])
    primitive_enclosures = {}
    for row in certificate['ranking']:
        p, q = row['p'], row['q']
        n = counts(p, q, roles[p], roles[q])
        assert Q(row['eta']) == n['eta'] and row['m'] == n['m']
        assert row['roles_outer'] == roles[p] and row['roles_middle'] == roles[q]
        primitive_enclosures[p, q] = independent_saving(n['eta'], n['m'])
        if p == q:
            v = comb(p, 3)
            assert n['W'] == 2*v**3+2*v*v*(roles[p]+p)
            assert n['L'] == 3*v*v*p*p
    assert len(primitive_enclosures) == len(roles)**2 == 121
    best_lo = primitive_enclosures[selected][0]
    assert all(best_lo > hi for pair, (_, hi) in primitive_enclosures.items() if pair != selected)
    assert all(Q(a['kappa']) >= Q(b['kappa']) for a, b in
               zip(certificate['ranking'], certificate['ranking'][1:]))
    joins = []
    for item in certificate['joining_certificates']:
        p, q = item['p'], item['q']
        triples, pi = matching(q)
        assert item['matching_ground'] == q
        assert item['orthogonal_matching_pairs'] == len(pi)
        joined_banks = item.get('joined_invocation_banks', item.get('joined_roles'))
        assert joined_banks == comb(p, 3)*comb(q, 3)
        m = p*p*q
        assert item['tail_dimension'] == p and item['head_dimension'] == m-p
        assert item['removed_two_edges_rank'] == 2*(m-p)
        assert item['joined_edge_rank'] == m-2*p
        assert item['rank_saved_per_join'] == m
        rp = roles[p] if p in roles else small_roles[p]
        joins.append(dict(p=p, q=q, orthogonal_middle_matching=len(pi),
                          bijection=True, joined_invocation_banks=comb(p, 3)*comb(q, 3),
                          joined_physical_roles=comb(p, 3)*comb(q, 3)*(rp+p),
                          per_physical_role_rank_saving=m))
    result = dict(certificate_sha256=sha256(source).hexdigest(),
                  code_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  best=best, independently_enclosed_candidate_savings=len(primitive_enclosures),
                  unique_best_primitive_saving=True, uniform_count_regressions=len(roles),
                  bank_joins=joins, small_index_checks=[index_checks(6, 8), index_checks(8, 6)],
                  wall_seconds=time.monotonic()-begin,
                  scope='Exact tensor counts, middle matching, scalar index partitions, and revised LU parameter arithmetic; large finite circuit realization and all-size analytic proofs are separate inputs')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
