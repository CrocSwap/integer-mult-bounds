#!/usr/bin/env python3
"""Closed-form kappa ceiling and reduced feasibility check for the exponent assembly.

Copyright 2026 romainhedouin. Apache-2.0.
AI assistance: drafted with Claude Code (Anthropic Claude); the proof status of
each implication is stated in docs/research/assembly-ceiling.md.

Provenance: the informal ceilings a/(1+2a) and a/(1+a) are stated in the RaD project
(hipotures) report references/semantic-bulk/rad20/reports/downstream-semantic-bulk-assembly.md.
This module is tested against two in-tree assemblies, both of which it avoids
importing: scripts/structured_bulk_assembly.py (original prefix; icekylinx, adapted
from Zhihao Chen (jacklightChen) PR23, which credits the RaD project) and
research/copied-fixed/balanced_assembly.py (balanced prefix; attributed to the RaD
project (hipotures) and its James Chang (jamesyc) PR34 specialization, adapting
Zhihao Chen PR23/29; see NOTICE).

Arithmetic only: no new kappa claim, no formal verification, and no statement
that the balanced layout is valid for any particular network. All values are
exact Fractions; there is no floating point.
"""
from fractions import Fraction as Q
from types import MappingProxyType
from typing import Callable, NamedTuple

from certify import require

STATUSES = ('reduced', 'duplicate', 'identity', 'implied')


def exact(x, name):
    """Return x as a Fraction; accept only int and Fraction (no float, bool or str)."""
    require(type(x) in (int, Q), name + ': expected an int or Fraction')
    return Q(x)


class Prefix(NamedTuple):
    """Prefix-dependent formulas; each takes exact (q, backoff) and does no domain check."""
    description: str
    c: Callable
    denominator: Callable
    epsilon: Callable
    ceiling: Callable


def _original_c(q, e):
    return exact(q, 'q')*(1 + exact(e, 'backoff'))


def _original_denominator(q, e):
    return 1 + exact(q, 'q')*(2 + exact(e, 'backoff'))


def _balanced_c(q, e):
    return exact(q, 'q') + exact(e, 'backoff')/4


def _balanced_denominator(q, e):
    return 1 + exact(q, 'q')


def _prefix(c, denominator, description):
    def epsilon(q, e):
        return (1 - exact(e, 'backoff'))/denominator(q, e)

    def ceiling(q, e):
        return epsilon(q, e)*exact(q, 'q')
    return Prefix(description, c, denominator, epsilon, ceiling)


PREFIXES = {
    'original': _prefix(_original_c, _original_denominator,
                        'c=q(1+e), D=1+q(2+e); scripts/structured_bulk_assembly.py'),
    'balanced': _prefix(_balanced_c, _balanced_denominator,
                        'c=q+e/4, D=1+q; research/copied-fixed/balanced_assembly.py'),
}


class Coverage(NamedTuple):
    """How a reference constraint relates to the reduced conditions.

    reduced:   the slack is the reduced condition's own slack.
    duplicate: on the reduced-feasible set the slack is positive_factor * the slack
               named in why ('FACTOR*NAME'; NAME is a reference constraint or a
               reduced condition).
    identity:  the slack is an explicit sum or product of terms that are positive
               whenever the conditions in by hold (why states the expression).
    implied:   positivity follows from the conditions in by through a range bound
               or a rational inequality (why states it).
    by lists reduced conditions whose joint positivity is claimed sufficient; it is
    not claimed minimal. Every non-'reduced' claim is tested only at finitely many
    exact points (see the proof status in docs/research/assembly-ceiling.md).
    """
    status: str
    by: tuple
    why: str


_NAMES = ('bit_positive', 'beta_positive', 'beta_below_one', 'backoff_positive',
          'q_positive', 'complex_below_one_over32', 'leaf_saving_above_bit',
          'kappa_below_ceiling', 'literal_scalar_guard', 'row_product_gap',
          'kappa_positive')
_DOM = ('bit_positive', 'backoff_positive', 'q_positive')
_AB = ('bit_positive', 'beta_positive', 'beta_below_one',
       'complex_below_one_over32', 'leaf_saving_above_bit')
_BO = ('backoff_positive',)
_QO = ('q_positive', 'backoff_positive')
_KC = ('kappa_below_ceiling',)
_ABD = _AB + _DOM
_ABK = _ABD + _KC


def _row(name, status, why, *groups):
    by = set()
    for group in groups:
        by.update((group,) if isinstance(group, str) else group)
    require(status in STATUSES and by <= set(_NAMES), name + ': bad coverage row')
    return name, Coverage(status, tuple(n for n in _NAMES if n in by), why)


def _table(rows):
    table = {}
    for name, entry in rows:
        require(name not in table, name + ': duplicate coverage row')
        table[name] = entry
    require(len(table) == 47, 'a reference constraint table has 47 names')
    for name, entry in table.items():
        if entry.status == 'duplicate':
            factor, _, rep = entry.why.partition('*')
            require(Q(factor) > 0 and (rep in table or rep in _NAMES) and rep != name,
                    name + ': bad duplicate target')
    return MappingProxyType(table)


_ORIGINAL = _table((
    _row('bit_positive', 'reduced', 'a', 'bit_positive'),
    _row('complex_above_bit', 'identity', 'b-a = s + beta*b, s=(1-beta)*b-a',
         'bit_positive', 'beta_positive', 'beta_below_one', 'leaf_saving_above_bit'),
    _row('complex_below_one_over32', 'reduced', '1/32-b', 'complex_below_one_over32'),
    _row('beta_positive', 'reduced', 'beta', 'beta_positive'),
    _row('beta_below_one', 'reduced', '1-beta', 'beta_below_one'),
    _row('leaf_saving_above_bit', 'reduced', '(1-beta)*b-a', 'leaf_saving_above_bit'),
    _row('q_positive', 'reduced', 'q', 'q_positive'),
    _row('q_below_internal', 'duplicate', '2*lambda_above_tau',
         'bit_positive', 'beta_positive', 'beta_below_one', 'backoff_positive',
         'leaf_saving_above_bit'),
    _row('q_below_leaf', 'identity', 's + 2*a*eta, s=(1-beta)*b-a',
         'leaf_saving_above_bit', 'bit_positive', 'backoff_positive'),
    _row('c_positive', 'identity', 'c = q*(1+eta)', _QO),
    _row('c_below_one', 'implied', '(1-a) + a*eta*(1+2*eta); a<1/32',
         'bit_positive', 'beta_positive', 'beta_below_one', 'backoff_positive',
         'complex_below_one_over32', 'leaf_saving_above_bit'),
    _row('q_below_reservations', 'identity', 'eta*q', _QO),
    _row('lambda_above_tau', 'identity', 'a*eta', 'bit_positive', 'backoff_positive'),
    _row('lambda_above_sigma', 'identity', '(b-a) + a*eta',
         'bit_positive', 'beta_positive', 'beta_below_one', 'backoff_positive',
         'leaf_saving_above_bit'),
    _row('lambda_above_internal', 'duplicate', '1*lambda_above_tau',
         'bit_positive', 'beta_positive', 'beta_below_one', 'backoff_positive',
         'leaf_saving_above_bit'),
    _row('lambda_prime_above_lambda', 'duplicate', '1*lambda_above_tau',
         'bit_positive', 'backoff_positive'),
    _row('compact_leaf', 'duplicate', '1*q_below_leaf',
         'leaf_saving_above_bit', 'bit_positive', 'backoff_positive'),
    _row('compact_reservations', 'duplicate', '1*q_below_reservations', _QO),
    _row('lambda_prime_below_one', 'duplicate', '1*q_positive', 'q_positive'),
    _row('epsilon_positive', 'implied', '(1-eta)/D, D>0', _DOM),
    _row('epsilon_below_one', 'identity', '1-eps = G + eta + eps*c', _DOM),
    _row('guard_width', 'duplicate', '1*epsilon_below_one', _DOM),
    _row('K_geometry', 'identity', 'G + eta', _DOM),
    _row('K_dominates_log', 'identity', 'eps*c', _DOM),
    _row('record_suffix', 'duplicate', '1*epsilon_below_one', _DOM),
    _row('phase_local', 'identity', 'G + 7*eta/8 + eps*c', _DOM),
    _row('phase_boundary', 'identity', 'G + 3*eta/8 + eps*c/2', _DOM),
    _row('gamma_sublinear', 'identity', '(eta + eps*c)/2', _DOM),
    _row('cell_above_band', 'implied', '(2-3*eta-q*(1+2*eta))/(4*D); a<1/32', _ABD),
    _row('prime_interval_packing', 'duplicate', '1*epsilon_below_one', _DOM),
    _row('alpha_positive', 'identity', 'r = G + (eta + eps*c)/2', _DOM),
    _row('alpha_below_one', 'implied', 'r=(G+1-eps)/2 with G<1, 0<eps<1', _DOM),
    _row('alpha_below_one_fourth', 'implied', '(1-2*eta)*(1-a*(4-eta))/(4*D); a<1/32', _ABD),
    _row('delta_positive', 'duplicate', '1/8*backoff_positive', _BO),
    _row('delta_below_one_eighth', 'implied', '(1-eta)/8; eta<1/2', _DOM),
    _row('short_record_fallback', 'implied', '(1-eta-a-a*q*(2+eta))/D; a<1/32', _ABD),
    _row('small_field_exposure', 'duplicate', '2*gamma_sublinear', _DOM),
    _row('artificial_boundary', 'implied', '17/2 - 3*eps/2 - eps*q/2 - eta/8 > 6', _DOM),
    _row('literal_scalar_guard', 'reduced', 'strict_literal_gap', 'literal_scalar_guard'),
    _row('row_product_gap', 'reduced', 'degree_gap', 'row_product_gap'),
    _row('original_prefix_above_kappa', 'identity', '(G-kappa) + eta', _BO, _KC),
    _row('coordinate_movement_above_kappa', 'identity',
         '(G-kappa) + 2*a*eta + q*(1-eps)', _DOM, _KC),
    _row('compact_phase_layer_above_kappa', 'reduced', 'G-kappa', _KC),
    _row('bulk_exposure_above_kappa', 'duplicate', '1*coordinate_movement_above_kappa',
         _DOM, _KC),
    _row('Gaussian_arithmetic_above_kappa', 'identity',
         '(G-kappa) + 3*eta/8 + eps*c/2', _DOM, _KC),
    _row('scalar_work_above_kappa', 'identity', '(G-kappa) + 7*eta/8 + eps*c', _DOM, _KC),
    _row('dimension_above_kappa', 'implied', '(G-kappa) + eps*(1-q); q<a<1/32', _ABK),
))

_BALANCED = _table((
    _row('a_positive', 'reduced', 'a', 'bit_positive'),
    _row('a_below_b', 'identity', 'b-a = s + beta*b, s=(1-beta)*b-a',
         'bit_positive', 'beta_positive', 'beta_below_one', 'leaf_saving_above_bit'),
    _row('b_below_one_over32', 'reduced', '1/32-b', 'complex_below_one_over32'),
    _row('beta_positive', 'reduced', 'beta', 'beta_positive'),
    _row('beta_below_one', 'reduced', '1-beta', 'beta_below_one'),
    _row('phase_leaf_above_bit', 'reduced', '(1-beta)*b-a', 'leaf_saving_above_bit'),
    _row('q_positive', 'reduced', 'q', 'q_positive'),
    _row('q_below_internal', 'duplicate', '2*lambda_above_tau',
         'bit_positive', 'beta_positive', 'beta_below_one', 'backoff_positive',
         'leaf_saving_above_bit'),
    _row('q_below_leaf', 'identity', 's + 2*a*h, s=(1-beta)*b-a',
         'leaf_saving_above_bit', 'bit_positive', 'backoff_positive'),
    _row('c_positive', 'identity', 'c = q + h/4', _QO),
    _row('c_below_one', 'implied', '1-q-h/4; a<1/32, h<1/2', _ABD),
    _row('q_below_reservations', 'duplicate', '1/4*backoff_positive', _BO),
    _row('lambda_above_tau', 'identity', 'a*h', 'bit_positive', 'backoff_positive'),
    _row('lambda_above_sigma', 'identity', '(b-a) + a*h',
         'bit_positive', 'beta_positive', 'beta_below_one', 'backoff_positive',
         'leaf_saving_above_bit'),
    _row('lambda_above_internal', 'duplicate', '1*lambda_above_tau',
         'bit_positive', 'beta_positive', 'beta_below_one', 'backoff_positive',
         'leaf_saving_above_bit'),
    _row('lambda_prime_above_lambda', 'duplicate', '1*lambda_above_tau',
         'bit_positive', 'backoff_positive'),
    _row('compact_leaf', 'duplicate', '1*q_below_leaf',
         'leaf_saving_above_bit', 'bit_positive', 'backoff_positive'),
    _row('compact_reservations', 'duplicate', '1/4*backoff_positive', _BO),
    _row('lambda_prime_below_one', 'duplicate', '1*q_positive', 'q_positive'),
    _row('epsilon_positive', 'implied', '(1-h)/(1+q), D>0', _DOM),
    _row('epsilon_below_one', 'identity', '1-eps = G + h', _DOM),
    _row('guard_width', 'duplicate', '1*epsilon_below_one', _DOM),
    _row('K_geometry', 'implied', 'h*(1-eps/4); eps<1', _DOM),
    _row('K_dominates_log', 'identity', 'eps*c', _DOM),
    _row('record_suffix', 'duplicate', '1*epsilon_below_one', _DOM),
    _row('phase_local', 'identity', 'G + 7*h/8', _DOM),
    _row('phase_boundary', 'identity', 'G + 3*h/8', _DOM),
    _row('gamma_sublinear', 'duplicate', '1/2*backoff_positive', _BO),
    _row('cell_above_band', 'implied', '(2-3*h-h*q)/(4*(1+q)); a<1/32', _ABD),
    _row('prime_interval_packing', 'duplicate', '1*epsilon_below_one', _DOM),
    _row('alpha_positive', 'identity', 'r = G + h/2', _DOM),
    _row('alpha_below_one', 'implied', 'r = G + h/2 with G<1, h<1/2', _DOM),
    _row('alpha_below_one_fourth', 'implied', '(1-2*h)*(1-a*(3-2*h))/(4*(1+q)); a<1/32', _ABD),
    _row('delta_positive', 'duplicate', '1/8*backoff_positive', _BO),
    _row('delta_below_one_eighth', 'implied', '(1-h)/8; h<1/2', _DOM),
    _row('short_record_fallback', 'implied', '(1-h-a-a*q)/(1+q); a<1/32', _ABD),
    _row('small_field_exposure', 'duplicate', '1*backoff_positive', _BO),
    _row('artificial_boundary', 'implied', '8 - eps + 3*h/8 > 6', _DOM),
    _row('literal_scalar_guard', 'reduced', 'strict_literal_gap', 'literal_scalar_guard'),
    _row('row_product_gap', 'reduced', 'degree_gap', 'row_product_gap'),
    _row('g1_above_kappa', 'identity', '(G-kappa) + h', _BO, _KC),
    _row('g2_above_kappa', 'identity', '(G-kappa) + 2*a*h + q*(1-eps)', _DOM, _KC),
    _row('g3_above_kappa', 'reduced', 'G-kappa', _KC),
    _row('g4_above_kappa', 'duplicate', '1*g2_above_kappa', _DOM, _KC),
    _row('g5_above_kappa', 'identity', '(G-kappa) + 3*h/8', _DOM, _KC),
    _row('g6_above_kappa', 'identity', '(G-kappa) + 7*h/8', _DOM, _KC),
    _row('g7_above_kappa', 'implied', '(G-kappa) + eps*(1-q); q<a<1/32', _ABK),
))

COVERAGE = MappingProxyType({'original': _ORIGINAL, 'balanced': _BALANCED})


class Condition(NamedTuple):
    """One reduced feasibility condition: feasible only if slack(point) > 0.

    kind: 'domain' (evaluated first), 'bound', 'kappa' or 'bridge'.
    covers: (prefix, reference constraint) pairs whose slack is this condition up
    to a positive factor; for the kappa-ceiling condition, all seven margins.
    """
    name: str
    formula: str
    slack: Callable
    kind: str
    prefixes: tuple
    covers: tuple


def _covers(name, kind):
    pairs = []
    for prefix, table in COVERAGE.items():
        for ref, entry in table.items():
            if name in entry.by and (entry.by == (name,) or kind == 'kappa'):
                pairs.append((prefix, ref))
    return tuple(pairs)


_BOTH = ('original', 'balanced')


def _condition(name, formula, slack, kind, prefixes=_BOTH):
    return Condition(name, formula, slack, kind, prefixes, _covers(name, kind))


REDUCED = (
    _condition('bit_positive', 'a', lambda p: p.a, 'domain'),
    _condition('beta_positive', 'beta', lambda p: p.beta, 'domain'),
    _condition('beta_below_one', '1 - beta', lambda p: 1 - p.beta, 'domain'),
    _condition('backoff_positive', 'backoff', lambda p: p.backoff, 'domain'),
    _condition('q_positive', 'q = a*(1 - 2*backoff)', lambda p: p.q, 'domain'),
    _condition('complex_below_one_over32', '1/32 - b', lambda p: Q(1, 32) - p.b, 'bound'),
    _condition('leaf_saving_above_bit', '(1 - beta)*b - a',
               lambda p: (1 - p.beta)*p.b - p.a, 'bound'),
    _condition('kappa_below_ceiling', 'G - kappa, G = q*(1-backoff)/D',
               lambda p: p.ceiling - p.kappa, 'kappa'),
    _condition('literal_scalar_guard', 'strict_literal_gap (bridge constant)',
               lambda p: p.literal_scalar_guard, 'bridge'),
    _condition('row_product_gap', 'degree_gap (bridge constant)',
               lambda p: p.row_product_gap, 'bridge'),
    _condition('kappa_positive', 'kappa (balanced reference only)',
               lambda p: p.kappa, 'kappa', ('balanced',)),
)
require(tuple(c.name for c in REDUCED) == _NAMES, 'reduced condition names out of order')
require(all(c.kind == 'domain' for c in REDUCED[:5])
        and all(c.kind != 'domain' for c in REDUCED[5:]), 'domain conditions come first')


class _Point:
    __slots__ = ('a', 'b', 'kappa', 'beta', 'backoff', 'q', 'ceiling',
                 'literal_scalar_guard', 'row_product_gap')


class Verdict(NamedTuple):
    """Result of check().

    ok: no checked condition has slack <= 0.  complete: every applicable condition
    was evaluated (False when a domain condition fails or a bridge constant is
    missing).  ceiling: G, or None when a domain condition fails.  headroom: G -
    kappa, or None.  slacks: condition name -> Fraction, None if not evaluated.
    failing: names of conditions with slack <= 0.  reference_names: reference
    constraints (in the prefix's own namespace) whose coverage depends on a
    failing condition; a reference constraint that fails is always among them
    unless it depends only on conditions that were not evaluated.
    """
    ok: bool
    complete: bool
    prefix: str
    ceiling: object
    headroom: object
    slacks: object
    failing: tuple
    reference_names: tuple


def _spec(prefix):
    require(isinstance(prefix, str) and prefix in PREFIXES,
            'prefix must be one of the names in PREFIXES')
    return PREFIXES[prefix]


def _optional(x, name):
    return None if x is None else exact(x, name)


def ceiling(a, *, prefix, backoff):
    """Return G = q(1-backoff)/D, the supremum of feasible kappa (not attained).

    Requires a > 0 and 0 < backoff < 1/2.
    """
    spec = _spec(prefix)
    a, e = exact(a, 'a'), exact(backoff, 'backoff')
    require(a > 0 and 0 < e < Q(1, 2), 'ceiling needs a > 0 and 0 < backoff < 1/2')
    return spec.ceiling(a*(1 - 2*e), e)


def check(a, b, kappa, beta, *, prefix, backoff, literal_scalar_guard=None,
          row_product_gap=None):
    """Evaluate every reduced condition; never raises for infeasible exact values."""
    spec = _spec(prefix)
    p = _Point()
    p.a, p.b, p.kappa = exact(a, 'a'), exact(b, 'b'), exact(kappa, 'kappa')
    p.beta, p.backoff = exact(beta, 'beta'), exact(backoff, 'backoff')
    p.literal_scalar_guard = _optional(literal_scalar_guard, 'literal_scalar_guard')
    p.row_product_gap = _optional(row_product_gap, 'row_product_gap')
    p.q = p.a*(1 - 2*p.backoff)
    p.ceiling = None
    active = [c for c in REDUCED if prefix in c.prefixes]
    slacks = {}
    for cond in active:
        if cond.kind == 'domain':
            slacks[cond.name] = cond.slack(p)
    if all(slacks[c.name] > 0 for c in active if c.kind == 'domain'):
        # a > 0 and 0 < backoff < 1/2 here, so D > 0 and nothing divides by zero.
        p.ceiling = spec.ceiling(p.q, p.backoff)
    for cond in active:
        if cond.kind != 'domain':
            slacks[cond.name] = None if p.ceiling is None else cond.slack(p)
    failing = tuple(n for n, s in slacks.items() if s is not None and s <= 0)
    names = tuple(ref for ref, entry in COVERAGE[prefix].items()
                  if any(n in failing for n in entry.by))
    return Verdict(not failing, all(s is not None for s in slacks.values()), prefix,
                   p.ceiling, None if p.ceiling is None else p.ceiling - p.kappa,
                   MappingProxyType(slacks), failing, names)


def feasible(a, b, kappa, beta, *, prefix, backoff, literal_scalar_guard,
             row_product_gap):
    """True iff every reduced condition, bridge constants included, is positive."""
    verdict = check(a, b, kappa, beta, prefix=prefix, backoff=backoff,
                    literal_scalar_guard=literal_scalar_guard,
                    row_product_gap=row_product_gap)
    return verdict.ok and verdict.complete
