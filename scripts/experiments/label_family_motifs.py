#!/usr/bin/env python3
"""Exact scalar identities and optimistic screens beyond five-subset labels.

These are research controls, not multiplication witnesses. The parity-cube
family uses a different vertex geometry and dense Fourier centers. The
coordinate-block family has higher-rank terminal subspaces. Both retain
three tensor stages and returns of each center through zero.
"""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from audit_kappa_targets import saving_enclosure
from prepare_layers import serializable
from search_network import log_integer_bounds

CURRENT_KAPPA = Q(4281, 10**12)
ODD_PRIMES_BELOW_23 = (3, 5, 7, 11, 13, 17, 19)


def krawtchouk(h, degree, weight):
    """Exact character sum over the Hamming sphere of the given degree."""
    return sum((-1)**j*comb(weight, j)*comb(h-weight, degree-j)
               for j in range(max(0, degree-h+weight), min(weight, degree)+1))


def parity_cube_spectrum(p, h):
    """Rank of I + distance-(2p) adjacency over F_p, without a large matrix.

    Vertices are even-parity bit strings of length h. Characters indexed by
    subsets T and T^c coincide on this group; take one per complementary pair.
    As p is odd, its character table is invertible over F_p.
    """
    if p not in ODD_PRIMES_BELOW_23 or not 2*p <= h < 4*p:
        raise ValueError('Expected a supported odd prime and 2p <= h < 4p')
    rows = []
    for w in range(h//2+1):
        eigenvalue = (1+krawtchouk(h, 2*p, w)) % p
        multiplicity = comb(h, w)//(2 if 2*w == h else 1)
        rows.append(dict(weight=w, eigenvalue=eigenvalue, multiplicity=multiplicity))
    if sum(row['multiplicity'] for row in rows) != 2**(h-1):
        raise ValueError('Character quotient multiplicity mismatch')
    return rows


def parity_cube_case(p, h):
    """Give every internal addition away, keeping only designated outputs.

    Rational labels z_x = ((-1)^x_1,...,(-1)^x_h,1) have diagonal form
    diag(1/4,...,1/4,p-h/4), hence Gram p-distance(x,y)/2 and rank h+1.
    The form is positive definite because h<4p. For even distances below4p,
    1-(distance/2)^(p-1) equals I+distance-(2p) adjacency over F_p.
    Each surviving Fourier center has nonzero coefficients at every vertex;
    its source labels span the complete h+1 dimensional address space.
    """
    spectrum = parity_cube_spectrum(p, h)
    v, r = 2**(h-1), h+1
    centers = sum(row['multiplicity'] for row in spectrum if row['eigenvalue'])
    deficit = v-6*centers*r
    result = dict(p=p, h=h, vertices=v, address_rank=r, terminal_rank=1,
                  exact_scalar_center_rank=centers, center_span_rank=r,
                  deficit_numerator=deficit, spectrum=spectrum,
                  form_last_diagonal=Q(4*p-h, 4))
    if deficit <= 0:
        return result | dict(positive_deficit_possible=False)
    # One side output per vertex and one retained output per Fourier center.
    # All arithmetic and its auxiliary roles are made free in this bound.
    role_floor = v+centers
    eta = Q(deficit, 2*r**3*(v+role_floor))
    lo, hi = saving_enclosure(eta, r**3)
    result.update(positive_deficit_possible=True, designated_role_floor=role_floor,
                  optimistic_eta=eta, bit_saving_lower=lo, bit_saving_upper=hi,
                  kappa_lower_for_relaxation=lo/2, kappa_upper=hi/2)
    return result


def parity_cube_audit():
    cases = [parity_cube_case(p, h) for p in ODD_PRIMES_BELOW_23
             for h in range(2*p, 4*p)]
    positive = [row for row in cases if row['positive_deficit_possible']]
    best = max(positive, key=lambda row: row['kappa_lower_for_relaxation'])
    if not all(best['kappa_lower_for_relaxation'] > row['kappa_upper']
               for row in positive if (row['p'], row['h']) != (best['p'], best['h'])):
        raise ValueError('Optimistic optimum not separated by exact intervals')
    # For every prime >=23, r=h+1>=47. Discard all center losses and retain
    # only the side-output floor R>=v. Then eta<1/(4r^3), decreasing in r.
    tail_rank = 47
    tail = 1/(2*(4*tail_rank**3-1)*log_integer_bounds(tail_rank**3)[0])
    if tail >= best['kappa_lower_for_relaxation']:
        raise ValueError('Infinite prime tail not excluded')
    return dict(
        status='OPTIMISTIC FAMILY CEILING; NO CIRCUIT OR EXPONENT WITNESS',
        family='Even-parity Hamming cube, odd p, 2p <= h < 4p.',
        scalar_identity='B(x,y)=1-(distance(x,y)/2)^(p-1)=I+A_distance_2p over F_p.',
        rational_gram='p-distance(x,y)/2; positive definite address form of rank h+1.',
        center_factorization='Exact Fourier support; each retained center uses the full source span.',
        relaxation='All additions and their roles are free; designated outputs and three center returns remain.',
        best=best, kappa_upper=best['kappa_upper'],
        factor_over_current_upper=best['kappa_upper']/CURRENT_KAPPA,
        first_tail_prime=23, tail_minimum_address_rank=tail_rank, tail_kappa_upper=tail,
        prime_summaries=[dict(p=p, positive_ground_sizes=sum(row['positive_deficit_possible']
                                                          for row in cases if row['p']==p),
                              best=max((row['kappa_upper'] for row in positive if row['p']==p), default=Q(0)))
                         for p in ODD_PRIMES_BELOW_23],
        obstacle='Even the global optimum is below 26 times the current kappa. '
                 'Actual sphere-transform roles can only lower this ceiling; '
                 'another center return or tensor architecture is needed for orders of magnitude.')


def coordinate_block_case(p, h):
    """Higher-rank coordinate-subspace labels with a concrete scalar identity.

    U_S=span(e_i:i in S), |S|=p, has terminal rank p in ambient rank h.
    B(S,T)=1-|S intersect T|^(p-1)=I+A_disjoint over F_p. Its binomial-basis
    coefficients are (-1)^d for 0<=d<p. Every corresponding d-set center
    sees all coordinates in the union of its terminal subspaces, hence its
    span has rank h for h>=p+1. No deficit can survive these center returns:
      p*C(h,p)=(h-p+1)*C(h,p-1) <= h*C(h,p-1) <= h*sum_{d<p}C(h,d).
    This excludes this explicit center factorization, not all block labels.
    """
    if p not in (2,)+ODD_PRIMES_BELOW_23 or h < p+1:
        raise ValueError('Expected a supported prime and h >= p+1')
    vertices = comb(h, p)
    centers = sum(comb(h, d) for d in range(p))
    terminal_gain = p*vertices
    center_loss = h*centers
    if terminal_gain > center_loss:
        raise ValueError('Coordinate-block obstruction failed')
    return dict(p=p, h=h, vertices=vertices, terminal_rank=p, address_rank=h,
                center_count=centers, center_span_rank=h,
                terminal_gain=terminal_gain, center_loss_per_invocation=center_loss,
                deficit_numerator=terminal_gain-6*center_loss,
                positive_deficit_possible=False)


def audit():
    return dict(status='NEW LABEL-FAMILY SCREENS; CURRENT CERTIFICATES UNCHANGED',
                current_kappa=CURRENT_KAPPA,
                parity_cube=parity_cube_audit(),
                higher_rank_coordinate_blocks=dict(
                    scalar_identity='I+A_disjoint = sum_{d=0}^{p-1} (-1)^d binomial(intersection,d) over F_p.',
                    all_ground_sizes_obstruction='p*C(h,p) <= h*sum_{d<p} C(h,d), so the three-return deficit is negative even with free roles.',
                    scope='Rank-p coordinate terminal subspaces, explicit subset-incidence centers, three tensor stages.',
                    controls=[coordinate_block_case(p, 2*p+3) for p in (2,3,5,7,11)]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = audit()
    if args.output:
        args.output.write_text(json.dumps(serializable(result), indent=2, sort_keys=True)+'\n')
    best = result['parity_cube']['best']
    print('Parity-cube optimistic best:', (best['p'], best['h']),
          '; kappa <', float(best['kappa_upper']),
          '; factor <', float(result['parity_cube']['factor_over_current_upper']))
    print('Coordinate-block terminal-rank gain never pays for the explicit center returns.')
