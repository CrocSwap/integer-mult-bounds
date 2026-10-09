"""Exact complete-profile certificate and a separately evaluated enclosure.

Directed Taylor certification follows Rohan Arun's PR65/67. The 3/2 range
reduction follows the independently evaluated PR67 audit. Existing PR48
balanced assembly and contributor attributions remain in their source.
Integration by huxint with OpenAI Codex assistance. Apache-2.0.
"""
from functools import lru_cache
from fractions import Fraction as Q
import json
from math import factorial
from support import HERE, ROOT, SELECTED, load, json_value
import binary_frame_math as inherited

balanced = load(ROOT/'references/frame-compiler/pr48/research/copied-fixed/balanced_assembly.py', 'balanced_split_assembly')
GRID = 10**18
BACKOFF = Q(1, 10**12)


def down(value, grid=10**40):
    return Q(value.numerator*grid//value.denominator, grid)


def up(value, grid=10**40):
    return -down(-value, grid)


def moment(profile, saving):
    assert type(saving) is Q and 0 < saving < 1
    lower, upper = Q(), Q()
    rows = {int(t): n for t, n in profile['child_multiplicities'].items()}
    assert sum(t*n for t, n in rows.items()) == profile['total_rank']
    terms = {}
    for t, n in sorted(rows.items()):
        assert type(n) is int and n > 0 and 0 < t < profile['m']
        lo, hi = inherited.logs(Q(profile['m'], t))
        u, v = saving*lo, saving*hi
        assert 0 <= u <= v < 1
        elo = sum((u**j/factorial(j) for j in range(9)), Q())
        ehi = sum((v**j/factorial(j) for j in range(9)), Q())
        ehi += v**9/factorial(9)/(1-v/10)
        weight = Q(t*n, profile['m']*profile['W'])
        lower += weight*down(elo)
        upper += weight*up(ehi)
        terms[t] = dict(weight=weight, log_lower=lo, log_upper=hi)
    return dict(saving=saving, lower=lower, upper=upper, strict_gap=1-upper, terms=terms)


def bridge_for(profile):
    source = ROOT/'references/frame-compiler/pr48/research/copied-fixed/certificate.json'
    bridge = json.loads(source.read_text())['finite_bridge']
    bridge['bit']['W'] = profile['W']
    assert bridge['bit']['m'] == profile['m'] == 575
    assert bridge['bit']['maxchild'] == profile['maxchild'] == 529
    bridge['bit']['wire_bits'] = profile['W'].bit_length()
    coefficient = sum(bridge[x]['halving_degree']*bridge[x]['wire_bits'] for x in ('bit', 'complex'))
    bridge['rows']['coefficient'] = coefficient
    bridge['rows']['degree_gap'] = Q(bridge['rows']['degree'])-Q(51, 25)*coefficient
    assert bridge['bit']['wire_bits'] == 27 and coefficient == 843
    assert bridge['rows']['degree_gap'] == Q(7007, 25)
    assert 2*529**9 < 575**9 and 2*529**8 >= 575**8
    assert bridge['bit']['halving_degree'] == 9
    return bridge


def certify(profile):
    low, high = 1, 71700000000000
    assert moment(profile, Q(low, GRID))['upper'] < 1
    assert moment(profile, Q(high, GRID))['lower'] > 1
    while low+1 < high:
        middle = (low+high)//2
        test = moment(profile, Q(middle, GRID))
        if test['upper'] < 1:
            low = middle
        elif test['lower'] > 1:
            high = middle
        else:
            raise ArithmeticError('Inconclusive interval; no implicit tolerance is allowed')
    saving = Q(low, GRID)
    bridge = bridge_for(profile)
    first = balanced.assembly(bridge, saving, Q(1, GRID), h=BACKOFF)
    margin = first['minimum_margin']
    kappa = up(margin, GRID)-Q(1, GRID)
    accepted = balanced.assembly(bridge, saving, kappa, h=BACKOFF)
    assert len(accepted['constraints']) == 47 and len(accepted['margins']) == 7
    try:
        balanced.assembly(bridge, saving, kappa+Q(1, GRID), h=BACKOFF)
    except balanced.InvalidAssembly as error:
        next_rejection = str(error)
    else:
        raise AssertionError('Next kappa grid point unexpectedly passed')
    predecessor = json.loads((HERE/'vendor/pr82-certificate.json').read_text())
    old_profile = predecessor['bit']
    old_test = moment(old_profile, saving)
    assert old_test['lower'] > 1, 'The complete PR82 profile must be excluded'
    a, b = moment(profile, saving), moment(profile, Q(high, GRID))
    assert a['upper'] < 1 < b['lower']
    return dict(status='Finite conditional witness; inherited all-size and analytic interfaces remain assumptions',
                kappa=kappa, bit_saving=saving, next_bit_saving=Q(high, GRID), bit=profile,
                accepted_moment=a, rejected_moment=b, assembly=accepted, finite_bridge=bridge,
                next_kappa_rejection=next_rejection, eventual_bounds=balanced.cutoffs(bridge, accepted),
                comparison=dict(pr82_commit='3410b940aa26e5876202152dfa7c4f66451ee22c',
                    pr82_kappa=Q(predecessor['kappa']), difference=kappa-Q(predecessor['kappa']),
                    ratio=kappa/Q(predecessor['kappa']), complete_pr82_moment_lower=old_test['lower'],
                    initial_pr77_commit='83298467291d3bd4b53f76faaef60dbf585be171',
                    initial_pr77_kappa=Q(12886963972497,250000000000000000)))


@lru_cache(None)
def independent_log(x):
    k = 0
    while x > Q(3, 2):
        x /= Q(3, 2)
        k += 1
    def expand(y):
        z = (y-1)/(y+1)
        power, total = z, Q()
        for j in range(60):
            total += power/(2*j+1)
            power *= z*z
        return 2*total, 2*total+2*power/(121*(1-z*z))
    lo, hi = expand(x)
    blo, bhi = expand(Q(3, 2))
    return lo+k*blo, hi+k*bhi


def independent_moment(profile, saving):
    lower, upper = Q(), Q()
    for t, n in sorted((int(t), n) for t, n in profile['child_multiplicities'].items()):
        lo, hi = independent_log(Q(profile['m'], t))
        u, v = down(lo*saving), up(hi*saving)
        assert 0 < u <= v < Q(1, 1000)
        tl = th = el = eh = Q(1)
        for j in range(1, 13):
            tl, th = tl*u/j, th*v/j
            el, eh = el+tl, eh+th
        eh += 2*th*v/13
        weight = Q(t*n, profile['m']*profile['W'])
        lower += weight*down(el)
        upper += weight*up(eh)
    return lower, upper


def independent_audit(certificate):
    p = certificate['bit']
    saving, successor = Q(certificate['bit_saving']), Q(certificate['next_bit_saving'])
    accepted = independent_moment(p, saving)
    rejected = independent_moment(p, successor)
    assert accepted[1] < 1 < rejected[0]
    actual = balanced.assembly(bridge_for(p), saving, Q(certificate['kappa']), h=BACKOFF)
    assert json_value(actual) == certificate['assembly']
    assert all(x > 0 for x in actual['constraints'].values())
    assert all(x > Q(certificate['kappa']) for x in actual['margins'].values())
    return dict(status='PASS separately evaluated logarithm/exponential enclosure and assembly',
                accepted_gap=1-accepted[1], rejected_gap=rejected[0]-1,
                logarithm_base='3/2', logarithm_terms=60, exponential_degree=12,
                constraints=47, margins=7)
