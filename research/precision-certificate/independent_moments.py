"""Independent exact supplier enclosures; Apache-2.0, OpenAI Codex assistance.

Uses -log(1-u), not the submitted artanh logarithm. For 0<=u<=1/2,
sum(u**j/j,j=1..N) has tail at most u**(N+1)/((N+1)*(1-u)).
For 0<=x<1, the exponential series through J has tail at most its
first omitted term divided by 1-x/(J+2), since later term ratios decrease.
Outward rounding to a rational grid preserves these bounds.

This arithmetic module has no repository implementation imports. Local histograms and supplier compiler
contracts remain assumed. This file does not derive the final exponent.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys
import time


GRID = 10**36
LOG_TERMS = 120
EXP_TERMS = 16
BAD = Q(1, 10**16)
ATOM = Q(1, 1000)
OLD = Q(384599, 10**10)


class EnclosureError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise EnclosureError(message)


def rational(value, name):
    require(type(value) in (int, str, Q), 'nonexact rational: ' + name)
    try:
        return Q(value)
    except (ValueError, ZeroDivisionError) as error:
        raise EnclosureError('invalid rational: ' + name) from error


def round_bounds(lower, upper):
    require(lower <= upper, 'reversed enclosure')
    lo = lower * GRID
    hi = upper * GRID
    return (Q(lo.numerator // lo.denominator, GRID),
            Q(-((-hi.numerator) // hi.denominator), GRID))


@lru_cache(maxsize=4096, typed=True)
def log_bounds(value):
    """Enclose natural log for exact value>=1 by power-of-two reduction."""
    value = rational(value, 'log argument')
    require(value >= 1, 'log argument below one')
    power = 0
    while value > 2:
        value /= 2
        power += 1

    def unit(y):
        u = 1 - 1/y
        require(0 <= u <= Q(1, 2), 'log unit interval')
        total = Q(0)
        term = u
        for j in range(1, LOG_TERMS + 1):
            total += term / j
            term *= u
        return total, total + term / ((LOG_TERMS + 1) * (1-u))

    lo, hi = unit(value)
    two_lo, two_hi = unit(Q(2))
    return round_bounds(lo + power*two_lo, hi + power*two_hi)


def exp_bounds(value):
    """Enclose exp(value) for an exact value in [0,1)."""
    value = rational(value, 'exp argument')
    require(0 <= value < 1, 'exp argument outside [0,1)')
    term = total = Q(1)
    for j in range(1, EXP_TERMS + 1):
        term *= value/j
        total += term
    first_omitted = term*value/(EXP_TERMS+1)
    remainder = first_omitted/(1-value/(EXP_TERMS+2))
    return round_bounds(total, total+remainder)


def power_ratio_bounds(rank, width, saving):
    """Bounds for (rank/width)**(1-saving), with proper positive rank."""
    require(type(rank) is int and type(width) is int and 0 < rank < width,
            'improper recursive child')
    saving = rational(saving, 'saving')
    require(0 <= saving < 1, 'saving outside [0,1)')
    lo, hi = log_bounds(Q(width, rank))
    elo = exp_bounds(saving*lo)[0]
    ehi = exp_bounds(saving*hi)[1]
    return Q(rank, width)*elo, Q(rank, width)*ehi


def normalize_children(children, width):
    require(type(children) is dict and children, 'empty/nonobject child inventory')
    result = {}
    for key, count in children.items():
        if type(key) is str:
            require(key.isascii() and key.isdigit() and str(int(key)) == key,
                    'invalid child rank key')
            rank = int(key)
        else:
            require(type(key) is int, 'invalid child rank type')
            rank = key
        require(rank not in result, 'duplicate normalized child rank')
        require(0 < rank < width and type(count) is int and count > 0,
                'invalid child rank/count')
        result[rank] = count
    return result


def supplier_bounds(width, stock, children, saving, *, bad_fraction=Q(0),
                    fallback_children_per_edge=0):
    """Reusable bound for complete ideal children plus entire rank-one fallback.

    stock is the number of ambient roles per vertex. The bad contribution
    is added in full, without subtracting any ideal child it might replace.
    Domains too wide for the exp enclosure are rejected rather than guessed.
    """
    require(type(width) is int and width >= 2 and type(stock) is int and stock > 0,
            'invalid width/stock')
    children = normalize_children(children, width)
    saving = rational(saving, 'saving')
    bad_fraction = rational(bad_fraction, 'bad fraction')
    require(0 <= bad_fraction <= 1, 'bad fraction outside [0,1]')
    require(type(fallback_children_per_edge) is int and fallback_children_per_edge >= 0,
            'invalid fallback multiplicity')
    require((bad_fraction == 0) == (fallback_children_per_edge == 0),
            'partial fallback specification')
    lower = upper = Q(0)
    for rank, count in children.items():
        lo, hi = power_ratio_bounds(rank, width, saving)
        lower += Q(count, stock)*lo
        upper += Q(count, stock)*hi
    fallback_lo = fallback_hi = Q(0)
    edges = sum(children.values())
    if bad_fraction:
        lo, hi = power_ratio_bounds(1, width, saving)
        factor = bad_fraction*Q(fallback_children_per_edge*edges, stock)
        fallback_lo, fallback_hi = factor*lo, factor*hi
    mass = sum(rank*count for rank, count in children.items())
    contaminated_mass = Q(mass)+bad_fraction*fallback_children_per_edge*edges
    return dict(width=width, stock=stock, saving=saving, edge_count=edges,
                rank_mass=mass, ambient_rank_mass=width*stock,
                ideal_lower=lower, ideal_upper=upper,
                fallback_lower=fallback_lo, fallback_upper=fallback_hi,
                bad_fraction=bad_fraction,
                fallback_children_per_edge=fallback_children_per_edge,
                total_lower=lower+fallback_lo, total_upper=upper+fallback_hi,
                characteristic_gap_lower=1-upper-fallback_hi,
                contaminated_rank_mass=contaminated_mass,
                rank_gap=width*stock-contaminated_mass)


def require_contraction(bounds):
    require(bounds['total_upper'] < 1, 'contaminated characteristic does not contract')
    require(bounds['contaminated_rank_mass'] < bounds['ambient_rank_mass'],
            'contaminated rank moment does not contract')
    return bounds


def certify_bit_supplier(width, stock, children, coarse_saving, *,
                         atom=ATOM, ordinary_saving=OLD):
    """Selected compiler: full 32m^2 fallback, fixed bad fraction, stopped saving."""
    coarse = rational(coarse_saving, 'coarse saving')
    atom = rational(atom, 'atom')
    ordinary = rational(ordinary_saving, 'ordinary saving')
    require(0 < coarse < 1 and 0 < atom < 1 and 0 < ordinary < 1,
            'bit saving/atom domain')
    bounds = require_contraction(supplier_bounds(width, stock, children, coarse,
        bad_fraction=BAD, fallback_children_per_edge=32*width*width))
    require(Q(2*width**3, 2**80) < BAD, 'fixed-prime bad-class allowance')
    effective = (1-atom)*coarse+atom*ordinary
    require(effective < atom < 1-effective, 'adapter and row tolls not subordinate')
    return dict(bounds, effective_saving=effective, atom=atom,
                ordinary_saving=ordinary,
                prime_bad_fraction_upper=Q(2*width**3, 2**80))


def js(value):
    if type(value) is Q:
        return str(value)
    if type(value) is dict:
        return {str(k): js(v) for k, v in value.items()}
    if type(value) in (list, tuple):
        return [js(v) for v in value]
    return value

