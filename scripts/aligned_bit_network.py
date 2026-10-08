#!/usr/bin/env python3
"""Conditional 1624/10^12 witness: aligned bit circuit with cheaper centers.

The fast-Gaussian assembly gives kappa < a_b/2, so the bit network binds.
The new side circuit (scripts/bit_circuit.py) aligns the paired blocks
across common points, shares the top-level pair-star sums between the two
groups that use them, and keeps each group's total. The totals feed the
center wires, which then lose h-1 dimensions per invocation instead of h.
"""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import json

from bit_circuit import AlignedPairedCircuit
from certify import Parameters, require, verify_sources
from complex_circuit import ComplexSideCircuit
from complex_network import COMPLEX_SAVING, H as COMPLEX_H, counts as complex_counts
from fast_gaussian import ZETA, witness
from paired_network import BIT_SAVING as OLD_BIT_SAVING
from prepare_layers import serializable
from search_network import log_integer_bounds

ROOT = Path(__file__).resolve().parents[1]
H = 50
BIT_SAVING = Q(325, 10**11)
LOG_BOUND = Q(11737, 1000)
KAPPA = Q(1624, 10**12)
ROLES = 494196  # certified by certificate(); used by the patch and tests


def counts(c):
    require(c.h == H, 'Wrong ground size')
    return counts_from(c.additions+len(c.outputs))   # side outputs and the h center roles


def counts_from(R, h=H):
    v = comb(h, 3); N = v**3; m = h**3
    W = 2*N+2*v*v*R; L = 3*v*v*h*(h-1); D = N-2*L
    require(D > 0, 'Bit deficit is not positive')
    return dict(h=h, v=v, m=m, N=N, side_and_center_roles=R, W=W, L=L, s=W*m-D,
                deficit=D, eta=Q(D, W*m), published_roles=509194+h)


def parameters():
    b = Q(19, 25)
    return Parameters(tau=1-BIT_SAVING, sigma=1-COMPLEX_SAVING,
                      epsilon=Q(49999, 100000), c=Q(9999, 10000),
                      lam=1-Q(32495, 10**13), lamp=1-Q(3249, 10**12),
                      kappa=KAPPA, beta=b, delta=Q(1, 10**6), C1=5-4*b+ZETA)


def witness_only(n=None):
    n = n or counts_from(ROLES)
    require(n['eta'] > BIT_SAVING*LOG_BOUND, 'Bit saving failed')
    return witness(parameters(), complex_counts(ComplexSideCircuit(COMPLEX_H)))


def certificate():
    c = AlignedPairedCircuit(H); circuit = c.verify(); frames = c.verify_frames()
    n = counts(c)
    require(n['side_and_center_roles'] == ROLES, 'Role count changed')
    lo, hi = log_integer_bounds(n['m'])
    require(hi < LOG_BOUND, 'Logarithm enclosure failed')
    require(n['eta'] > BIT_SAVING*LOG_BOUND, 'Bit saving failed')
    w = witness_only(n)
    require(Q(1, 2**30) < KAPPA < Q(1, 2**29), 'Unexpected dyadic scale')
    old = dict(roles=509194+H, deficit=n['N']-6*n['v']**2*H*H)
    return dict(status='CONDITIONAL 1624/10^12 WITNESS; ALIGNED BIT CIRCUIT AND CHEAPER CENTERS; NOT FORMAL VERIFICATION',
                upstream_commit=verify_sources(), circuit=circuit, frames=frames, bit_counts=n,
                bit_saving=BIT_SAVING, previous_bit_saving=OLD_BIT_SAVING, log_m_upper=LOG_BOUND,
                log_enclosure=(lo, hi), bit_deficit_slack=n['eta']-BIT_SAVING*LOG_BOUND,
                previous_counts=old, complex_saving=COMPLEX_SAVING, witness=w,
                improvement_over_fast_gaussian=KAPPA/Q(1479, 10**12),
                scoped_ceiling=dict(upper=BIT_SAVING/2, below_2_to_minus_29=BIT_SAVING/2 < Q(1, 2**29),
                    scope='g2,g3,g4 <= a_b*min(eps,1-eps) for this bit network; leaf needs (1-beta)a_c > 1-lambprime with beta>3/4.'),
                scope='Conditional on the pinned upstream interfaces, compact-control movement and guard, the compressed '
                      'complex network, the fast resampling lemmas, and the written center-frame argument. '
                      'Exact arithmetic and finite checks are not formal verification.')


if __name__ == '__main__':
    result = serializable(certificate())
    (ROOT/'certificates/aligned-bit-network.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('PASS conditional', KAPPA, '> 2^-30; minimum margin', result['witness']['minimum_margin'],
          'limiting', result['witness']['limiting_margins'])
    print('roles', result['bit_counts']['side_and_center_roles'], 'vs published', result['bit_counts']['published_roles'])
