#!/usr/bin/env python3
"""Exact certificate for stage-two scratch source frames and a third complex class.

Builds on the batched recursion of PR #10 (icekylinx), which consumes the
PR #7 finite producers (Zhihao Chen) unchanged. Two changes are certified:

1. Interchange network. Every stage-two auxiliary role starts in the frame of
   its first gate, P_{D_0}, instead of zero, and ends at I + P_{D_0}. Its
   endpoint difference is still I, so the scalar network, the rank sum and
   the deficit are unchanged. The rank-(h^2-h) entrance edge disappears and
   the exit edge becomes one projector of rank m-h. That projector is
   compiled as h singleton pivots and one contiguous block of m-2h fields.
2. Complex network. The stage-three data entrances, of rank (h^2-1)(h-1),
   become a third whole-residual child class. The dependency-path guard of
   PR #10 still allows at most one selected residual per path.
"""
from dataclasses import asdict
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import json

from batched_bit_rank_moment import rational_log_bounds, log_integer_upper
from batched_network import complex_counts as batched_complex_counts
from certify import Parameters, require
from compact_control_layer import layer_exponents
from controlled_bit_rank_moment import counts as controlled_counts
from fast_gaussian import fast_constraints, fast_margins
from prepare_layers import serializable

ROOT = Path(__file__).resolve().parents[1]
BIT_SAVING = Q(154, 10**8)
COMPLEX_SAVING = Q(18, 10**7)
KAPPA = Q(7699, 10**10)
ZETA = Q(1, 10000)


def log_upper(x):
    """Rigorous rational upper bound for log(x), x a rational at least one."""
    x = Q(x)
    if x.denominator == 1:
        return log_integer_upper(x.numerator)
    return rational_log_bounds(x)[1]


# Simple rational upper bounds for log(1/ratio); each is checked against a
# rigorous series enclosure before use.
SIMPLE_LOGS = {Q(1, 21952): Q(9997, 1000), Q(195, 196): Q(512, 100000),
               Q(10165, 10976): Q(768, 10000), Q(391, 392): Q(2555, 10**6),
               Q(27, 28): Q(36368, 10**6), Q(21141, 21952): Q(37644, 10**6)}


def moment(weights, ratios, a):
    """Upper bound for sum_i w_i ratio_i^(-a), using exp(x) <= 1/(1-x)."""
    logs = []
    for r in ratios:
        simple = SIMPLE_LOGS[r]
        require(log_upper(1/r) < simple, 'Rational logarithm bound failed')
        require(0 <= a*simple < 1, 'Exponential upper-bound range failed')
        logs.append(simple)
    return sum((w/(1-a*ell) for w, ell in zip(weights, logs)), Q(0)), logs


def bit_counts():
    n = controlled_counts()
    m, h = n['m'], n['h']
    H = h*h
    stage_two = [r for r in n['recursive_blocks'] if r['name'].startswith('second_stage_auxiliary_sink')]
    require(len(stage_two) == 2 and len({r['copies'] for r in stage_two}) == 1,
            'Unexpected stage-two auxiliary classes')
    B = stage_two[0]['copies']
    require(sum(r['chunk_digits'] for r in stage_two) == m-H,
            'Stage-two sink rank is not m-h^2')
    blocks = [dict(name=r['name'], copies=r['copies'], chunk_digits=r['chunk_digits'])
              for r in n['recursive_blocks'] if r not in stage_two]
    blocks.append(dict(name='second_stage_auxiliary_source_frame_exit_middle',
                       copies=B, chunk_digits=m-2*h))
    # Entrance edge of rank H-h removed; new exit corner contributes h pivots.
    singletons = n['singleton_calls']-B*(H-h)+B*h
    require(singletons+sum(r['copies']*r['chunk_digits'] for r in blocks) == n['original_rank_sum'],
            'Rank sum changed')
    return dict(h=h, m=m, v=n['v'], N=n['N'], W=n['W'], roles_per_invocation=n['roles_per_invocation'],
                eta=n['eta'], deficit=n['deficit'], original_rank_sum=n['original_rank_sum'],
                stage_two_auxiliary_roles=B, removed_entrance_rank=H-h,
                exit_rank=m-h, exit_corner_pivots=h, exit_block=m-2*h,
                previous_singleton_calls=n['singleton_calls'],
                singleton_calls=singletons, recursive_blocks=blocks)


def bit_certificate(a=BIT_SAVING):
    n = bit_counts()
    m, W = n['m'], n['W']
    ratios = [Q(1, m)]+[Q(r['chunk_digits'], m) for r in n['recursive_blocks']]
    weights = [Q(n['singleton_calls'], W*m)]+[
        Q(r['copies']*r['chunk_digits'], W*m) for r in n['recursive_blocks']]
    require(sum(weights) == 1-n['eta'], 'Rank-mass identity failed')
    upper, logs = moment(weights, ratios, a)
    require(upper < 1, 'The proposed bit saving exceeds the source-frame rank moment')
    return dict(bit_saving=a, tau=1-a, counts=n, normalized_widths=ratios,
                rank_mass_weights=weights, logarithm_upper_bounds=logs,
                moment_upper=upper, strict_gap=1-upper,
                formula='sum_i weight_i * ratio_i^(-bit_saving) < 1',
                bound='exp(x) <= 1/(1-x), for 0 <= x < 1')


def complex_counts():
    n = batched_complex_counts()
    m, h, N = n['m'], n['h'], n['N']
    d3 = (h*h-1)*(h-1)
    bulk = [dict(r) for r in n['bulk_classes']]
    bulk.append(dict(name='third_stage_data_entrance_residuals', copies=2*N, rank=d3))
    singletons = n['s']-sum(r['copies']*r['rank'] for r in bulk)
    require(singletons > 0, 'Invalid complex rank masses')
    out = dict(n)
    out.update(bulk_classes=bulk, singleton_calls=singletons, previous_singleton_calls=n['singleton_calls'])
    return out


def complex_certificate(a=COMPLEX_SAVING):
    n = complex_counts()
    m, W = n['m'], n['W']
    ratios = [Q(1, m)]+[Q(r['rank'], m) for r in n['bulk_classes']]
    weights = [Q(n['singleton_calls'], W*m)]+[Q(r['copies']*r['rank'], W*m) for r in n['bulk_classes']]
    require(sum(weights) == 1-n['eta'], 'Complex rank-mass identity failed')
    upper, logs = moment(weights, ratios, a)
    require(upper < 1, 'Unsupported complex exponent')
    return dict(complex_saving=a, sigma=1-a, counts=n, normalized_widths=ratios,
                rank_mass_weights=weights, logarithm_upper_bounds=logs,
                moment_upper=upper, strict_gap=1-upper,
                formula='sum_i weight_i * ratio_i^(-complex_saving) < 1',
                bound='exp(x) <= 1/(1-x), for 0 <= x < 1')


def source_frame_guard(n, beta=Q(1, 1000), zeta=ZETA):
    """PR #10's dependency-path guard with the third selected residual class."""
    h, m, W, s = n['h'], n['m'], n['W'], n['s']
    q = m+6*h
    ranks = tuple(r['rank'] for r in n['bulk_classes'])
    rho = Q(6, 5)
    lower = 160000
    theta = Q(999, 1000)
    require(lower**5 < m**6, 'Lower bound for m^(6/5) failed')
    require(all(2*a > q and a < m for a in ranks),
            'A dependency path could cross two selected bulk edges')
    moments = {'no_bulk': Q(q, lower)}
    for a in ranks:
        t = Q(m-a, m)
        power_upper = 1-Q(6, 5)*t+Q(3, 25)*t*t/(1-t)
        moments['rank_'+str(a)] = Q(q-a, lower)+power_upper
    require(all(x < theta for x in moments.values()), 'Normalized arithmetic-depth path moment failed')
    E = 64*(W+m+1)**3
    require(36*W**3+4*s+4*W+8*m+4 < E, 'Additive coefficient-depth enclosure failed')
    dependency_constant = 1000*(E+16*m+1)
    require(dependency_constant*(1-theta) >= E and dependency_constant >= 16*m,
            'Strong-induction constant failed')
    C1 = rho-(rho-1)*beta+zeta
    raw = 128*m*(1+1/zeta)*dependency_constant
    C0 = -(-raw.numerator//raw.denominator)
    require(m*(1+1/zeta)*dependency_constant+18 <= C0, 'Completed-layer guard constant failed')
    return dict(h=h, m=m, q=q, selected_ranks=ranks, at_most_one_selected_edge_per_path=True,
                rho=rho, m_to_rho_lower=lower, path_moment_upper=moments, theta_upper=theta,
                theta_slack=theta-max(moments.values()), E=E,
                dependency_constant=dependency_constant, beta=beta, zeta=zeta, C0=C0, C1=C1)


def parameters():
    tau = 1-BIT_SAVING
    return Parameters(tau=tau, sigma=1-COMPLEX_SAVING, epsilon=Q(499999, 10**6), c=Q(1),
                      beta=Q(1, 1000), delta=Q(1, 10**10), lam=tau+Q(1, 10**16),
                      lamp=tau+Q(2, 10**16), C1=Q(11999, 10000), kappa=KAPPA)


def assembly(p=None, cn=None):
    p = parameters() if p is None else p
    cn = complex_counts() if cn is None else cn
    require(p.sigma < p.tau, 'The complex network must not bind (sigma < tau)')
    g = source_frame_guard(cn, p.beta, ZETA)
    require(p.C1 == g['C1'], 'Guard exponent mismatch')
    exponents = layer_exponents(p.tau, p.sigma, p.beta, p.c)
    constraints = fast_constraints(p)
    constraints['packed_overhead'] = p.lam-exponents['internal']
    constraints['reserved_axes'] = p.lamp-exponents['preprocessing']
    for name, slack in constraints.items():
        require(slack > 0, 'Assembly constraint failed: '+name)
    margins = fast_margins(p)
    minimum = min(margins.values())
    require(minimum > p.kappa, 'No strict final absorption gap')
    require(p.kappa > Q(1, 2**21), 'Dyadic comparison failed')
    return dict(parameters=asdict(p), guard=g, recurrence=exponents, constraints=constraints,
                margins=margins, minimum_margin=minimum, absorption_gap=minimum-p.kappa,
                dyadic_corollary='2^-21', dyadic_gap=p.kappa-Q(1, 2**21))


SOURCES = ['notes/source-frame-bit.tex', 'notes/source-frame-complex.tex',
           'notes/source-frame-assembly.tex', 'notes/source-frame-21-note.tex',
           'scripts/source_frame_network.py', 'scripts/make_source_frame_patch.py']


def certificate():
    b = bit_certificate()
    c = complex_certificate()
    require(b['bit_saving'] == 1-parameters().tau and c['complex_saving'] == 1-parameters().sigma,
            'Assembly and motif exponents differ')
    w = assembly(cn=c['counts'])
    return dict(
        status='CONDITIONAL 7699/10^10 > 2^-21 INTEGER-MULTIPLICATION WITNESS; SOURCE FRAMES ON PR #10',
        upstream_commit='adc7f1241b42e322a6451854ab7e4b4c146bf78a',
        retained_PR7_commit='6725c6a17b17871a35353fd29157f4ed851bc114',
        retained_PR10_commit='62691e395a0458ce089a1c7b5d89e74291e95e29',
        bit=b, complex=c, assembly=w,
        improvement_over_PR10=KAPPA/Q(6149999, 5*10**13),
        new_source_sha256={p: sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES if (ROOT/p).exists()},
        scope='Exact exponent and assembly arithmetic for stage-two scratch source frames and the '
              'third complex residual class, consuming PR #10 and the retained PR #7 producers '
              'and the stated upstream analytic and tape interfaces. Not formal verification.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--summary', action='store_true')
    args = parser.parse_args()
    result = certificate()
    if args.output:
        args.output.write_text(json.dumps(serializable(result), indent=2, sort_keys=True)+'\n')
    w = result['assembly']
    if args.summary or not args.output:
        print('PASS kappa='+str(KAPPA)+' > 2^-21')
        print('bit saving='+str(BIT_SAVING)+'; complex saving='+str(COMPLEX_SAVING))
        print('bit moment gap='+str(float(result['bit']['strict_gap'])))
        print('complex moment gap='+str(float(result['complex']['strict_gap'])))
        print('minimum margin='+str(w['minimum_margin'])+'; gap='+str(w['absorption_gap']))


if __name__ == '__main__':
    main()
