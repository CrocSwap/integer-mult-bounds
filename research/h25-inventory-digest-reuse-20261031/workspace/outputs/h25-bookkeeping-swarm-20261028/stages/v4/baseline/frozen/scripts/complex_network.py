#!/usr/bin/env python3
"""Conditional 59/10^11 witness: a compressed complex side circuit.

The compact-control witness was limited by the original complex motif, whose
v*z_c side wires per invocation dilute its rank deficit. The new side circuit
computes the same correction with shared sums, binary coordinate and pair-star
labels, and the bit network's transparent twelve-operation schedule. The bit
network, compact-control movement and assembly recipe are unchanged.
"""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import json

from certify import Parameters, constraints, margins, require, verify_sources
from compact_control_layer import layer_exponents
from complex_circuit import ComplexSideCircuit, Checks, compile_roles, verify_role_frames
from paired_network import BIT_SAVING
from prepare_layers import serializable
from search_network import log_integer_bounds

ROOT = Path(__file__).resolve().parents[1]
H = 25
COMPLEX_SAVING = Q(14, 10**9)
LOG_BOUND = Q(966, 100)
KAPPA = Q(59, 10**11)


def counts(c):
    h = c.h; v = comb(h, 3); m = h**3; N = v**3; I = 3*v*v
    R = c.roles; W = 2*N+I*(R+h+1); L = I*(h+1)*h
    s = W*m-2*N+2*L
    require(L < N, 'Complex deficit is not positive')
    return dict(h=h, v=v, m=m, N=N, I=I, side_roles_per_invocation=R,
                central_roles=h+1, W=W, L=L, s=s, deficit=W*m-s, eta=Q(W*m-s, W*m),
                original_side_wires_per_invocation=v*(comb(h-3, 3)+3*(h-3)))


def gate_count(c, n):
    """Per invocation: four mixer passes, two copies, two injections, four central gates."""
    per = 4*len(c.active)+4*n['v']+4
    require(n['I']*per <= 12*n['W'], 'The 12W gate bound behind E=64(W+m+1)^3 failed')
    return dict(gates_per_invocation=per, total_gates=n['I']*per, twelve_W=12*n['W'])


def guard(n, beta, zeta):
    """Generalized stopped-depth guard with the new complex constants."""
    m, s, W = n['m'], n['s'], n['W']
    E = 64*(W+m+1)**3; B = s+E
    require(m >= 3 and 2 <= s < m**5, 'Unverified coefficient-depth hypothesis')
    require(s*(8+E) <= 9*B*B, 'One-piece constant failed')
    C1 = 5-4*beta+zeta
    raw = max(Q(128*m*B*B), 18*m*B*B*(1+1/zeta))
    C0 = -(-raw.numerator//raw.denominator)
    require(9*m*B*B*(1+1/zeta)+18 <= C0, 'Whole-layer constant failed')
    return dict(m=m, s=s, E=E, B=B, beta=beta, zeta=zeta, C0=C0, C1=C1)


def parameters():
    return Parameters(tau=1-BIT_SAVING, sigma=1-COMPLEX_SAVING,
                      epsilon=Q(19999, 100000), c=Q(999, 1000),
                      lam=1-Q(2958, 10**12), lamp=1-Q(2956, 10**12),
                      kappa=KAPPA, beta=Q(1, 1000), delta=Q(1, 10**6),
                      C1=Q(49961, 10000))


def witness(p, n):
    g = guard(n, p.beta, Q(1, 10000))
    require(p.C1 == g['C1'], 'Guard mismatch')
    e = layer_exponents(p.tau, p.sigma, p.beta, p.c)
    slacks = constraints(p, layout_model='nonadjacent', assembly_model='tight-gaussian')
    slacks['packed_overhead'] = p.lam-e['internal']  # compact control: internal = max exponent
    slacks['reserved_axes'] = p.lamp-e['preprocessing']
    for name, slack in slacks.items(): require(slack > 0, 'Constraint failed: '+name)
    gs = margins(p, layout_model='nonadjacent', assembly_model='tight-gaussian')
    require(min(gs.values()) > p.kappa, 'No final absorption gap')
    return dict(parameters=vars(p), guard=g, recurrence=e, constraint_slacks=slacks,
                margins=gs, minimum_margin=min(gs.values()),
                limiting_margins=[k for k, v in gs.items() if v == min(gs.values())],
                absorption_gap=min(gs.values())-p.kappa)


def witness_only():
    """Counts and parameter witness without the full finite checks (for the patch)."""
    n = counts(ComplexSideCircuit(H))
    require(n['eta'] > COMPLEX_SAVING*LOG_BOUND, 'Complex saving failed')
    return witness(parameters(), n)


def certificate():
    c = ComplexSideCircuit(H); checks = Checks(c); code = compile_roles(c)
    side = checks.verify_map(); labels = checks.verify_labels()
    roles = verify_role_frames(c, checks, code)
    n = counts(c)
    lo, hi = log_integer_bounds(n['m'])
    require(hi < LOG_BOUND, 'Logarithm enclosure failed')
    require(n['eta'] > COMPLEX_SAVING*LOG_BOUND, 'Complex saving failed')
    p = parameters(); w = witness(p, n)
    require(Q(1, 2**31) < KAPPA < Q(1, 2**30), 'Unexpected dyadic scale')
    # With the bit exponent fixed, g3 <= epsilon*(1-lambda) < epsilon*a_b < a_b/5.
    ceiling = BIT_SAVING/5
    require(ceiling < Q(1, 2**30), 'This bit network could cross 2^-30')
    return dict(status='CONDITIONAL 59/10^11 WITNESS; COMPRESSED COMPLEX SIDE CIRCUIT; NOT FORMAL VERIFICATION',
                upstream_commit=verify_sources(), circuit=c.stats(), side_map=side,
                labels=labels, role_frames=roles, gates=gate_count(c, n),
                complex_counts=n, complex_saving=COMPLEX_SAVING, log_m_upper=LOG_BOUND,
                log_enclosure=(lo, hi), complex_deficit_slack=n['eta']-COMPLEX_SAVING*LOG_BOUND,
                bit_saving=BIT_SAVING, witness=w,
                improvement_over_compact_control=KAPPA/Q(83, 10**12),
                scoped_ceiling=dict(upper=ceiling, below_2_to_minus_30=True,
                    scope='Published h=50 paired bit network and retained Gaussian margin; not a bound on other networks or algorithms.'),
                scope='Conditional on the pinned upstream interfaces, the compact-control movement and guard proofs, the paired bit network, and the written binary-frame transfer for this complex side circuit. Exact arithmetic and finite checks are not formal verification.')


if __name__ == '__main__':
    result = serializable(certificate())
    (ROOT/'certificates/complex-network.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('PASS conditional', KAPPA, '> 2^-31; minimum margin', result['witness']['minimum_margin'])
    print('Side roles per invocation', result['complex_counts']['side_roles_per_invocation'],
          'vs original', result['complex_counts']['original_side_wires_per_invocation'])
