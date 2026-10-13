#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent T21 recurrence audit using positive binomial series.

Prepared for David Breslauer with substantial OpenAI Codex assistance.
No production arithmetic, logarithm or exponential implementation is imported.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
D = 1 << 240
TAIL_LIMIT = 1 << 70  # At most 2^-170 per power factor.


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ceil_div(n, d):
    return -(-n // d)


def power_interval(r, m, a):
    """Enclose (m/r)^a for 0 <= a <= 1, with exact integer arithmetic.

    t_0 = 1; t_(k+1) = t_k * (a+k)/(k+1) * (1-r/m).
    Subsequent exact ratios are at most x = 1-r/m, hence the tail
    after t_k is at most t_(k+1)/(1-x). Each recurrence operation is
    rounded outward on the fixed dyadic lattice with denominator D.
    """
    require(type(r) is int and type(m) is int and 0 < r <= m, 'Invalid rank or arity')
    require(isinstance(a, Q) and 0 <= a <= 1, 'Saving must be a rational in [0,1]')
    if a == 0 or r == m:
        return Q(1), Q(1), 0
    p, q = a.numerator, a.denominator
    tl = tu = sl = su = D
    for k in range(20000):
        numerator = (p + k*q) * (m-r)
        denominator = q * (k+1) * m
        nl = tl * numerator // denominator
        nu = ceil_div(tu * numerator, denominator)
        tail = ceil_div(nu * m, r)
        if tail <= TAIL_LIMIT:
            return Q(sl, D), Q(su + tail, D), k+1
        tl, tu = nl, nu
        sl, su = sl + tl, su + tu
    raise ValueError('Series did not reach the prescribed tail bound')


def moment(profile, m, live, a, surcharge=False):
    require(type(live) is int and live > 0, 'Invalid live stock')
    require(type(m) is int and m > 1 and profile, 'Invalid arity or empty profile')
    lower = upper = Q(0)
    terms = {}
    for r, count in sorted(profile.items()):
        require(type(r) is int and type(count) is int and 0 < r < m and count > 0,
                'Invalid child rank or multiplicity')
        l, u, steps = power_interval(r, m, a)
        weight = Q(r*count, m*live)
        lower += weight*l
        upper += weight*u
        terms[str(r)] = steps
    if surcharge:
        l, u, steps = power_interval(1, m, a)
        weight = Q(32*m*sum(profile.values()), 10**16*live)
        lower += weight*l
        upper += weight*u
        terms['fallback'] = steps
    return lower, upper, terms


def brackets(profile, m, live, endpoint, surcharge):
    lower = moment(profile, m, live, endpoint, surcharge)
    upper = moment(profile, m, live, endpoint + Q(1, 10**24), surcharge)
    require(lower[1] < 1, 'Claimed lower endpoint does not have a strict acceptance certificate')
    require(upper[0] > 1, 'Claimed successor does not have a strict rejection certificate')
    return {
        'endpoint': str(endpoint),
        'successor': str(endpoint + Q(1, 10**24)),
        'lower_residual_interval': [str(x-1) for x in lower[:2]],
        'successor_residual_interval': [str(x-1) for x in upper[:2]],
        'terms': lower[2],
    }


def controls(profile, endpoint, conservative):
    count = 0
    # Exact algebraic comparison for rational exponents p/q:
    # L^q <= (m/r)^p <= U^q, with no floating-point reference.
    for m in (2, 3, 5, 7, 73):
        for r in range(1, m+1):
            for a in (Q(0), Q(1, 3), Q(1, 2), Q(2, 3), Q(1)):
                l, u, _ = power_interval(r, m, a)
                exact = Q(m, r)**a.numerator
                require(l**a.denominator <= exact <= u**a.denominator, 'Algebraic enclosure failed')
                count += 1
    require(moment(profile, 73, 18816, Q(0))[:2] ==
            (Q(1366848, 73*18816), Q(1366848, 73*18816)), 'Zero-saving mass identity failed')
    # Underpricing controls: a removed child and dropped exceptional fallback
    # wrongly admit the next saving tick. These are deliberately changed
    # models, not defects alleged against the selected production checker.
    omitted = dict(profile)
    omitted[48] -= 1
    require(moment(omitted, 73, 18816, endpoint + Q(1, 10**24))[1] < 1,
            'Omitted child control failed')
    require(moment(profile, 73, 18816, conservative + Q(1, 10**24))[1] < 1,
            'Dropped conservative surcharge control failed')
    wrong_stock = moment(profile, 73, 19330, endpoint + Q(1, 10**24))
    require(wrong_stock[1] < 1, 'Physical-stock normalization control failed')
    # Same rank mass AND same child count; strict concavity still changes
    # the numerical price. Replace two rank-48 children by ranks 47 and 49.
    redistributed = dict(profile)
    redistributed[48] -= 2
    redistributed[47] = redistributed[49] = 1
    require(sum(redistributed.values()) == sum(profile.values()) and
            sum(r*c for r,c in redistributed.items()) == 1366848, 'Control mass changed')
    original = moment(profile, 73, 18816, endpoint)
    changed = moment(redistributed, 73, 18816, endpoint)
    require(changed[1] < original[0], 'Mass-preserving redistribution not distinguished')
    rejection_count = 0
    for args in ((0, 73, Q(1,2)), (74,73,Q(1,2)), (1,0,Q(1,2)),
                 (1,73,Q(-1,2)), (1,73,Q(3,2)), (True,73,Q(1,2))):
        try:
            power_interval(*args)
        except ValueError:
            rejection_count += 1
        else:
            raise ValueError('Invalid enclosure input accepted')
    for bad in ({1:0}, {73:1}, {1:True}, {1:-1}, {}):
        try:
            moment(bad, 73, 18816, endpoint)
        except ValueError:
            rejection_count += 1
        else:
            raise ValueError('Invalid profile accepted')
    return {'algebraic_comparisons':count, 'mathematical_controls':5,
            'rejected_inputs':rejection_count,
            'redistributed_minus_original_interval':
            [str(changed[0]-original[1]),str(changed[1]-original[0])]}


def repository_bindings(root, pins):
    """Compare source bytes without importing or executing supplier code."""
    root = root.resolve()
    sources = {remote: pins['files'][local]
               for local, remote in pins['provenance'].items()}
    sources.update(pins['references'])
    for relative, expected in sources.items():
        path = (root/relative).resolve()
        require(path.is_relative_to(root) and path.is_file(),
                'Missing repository source: '+relative)
        require(hashlib.sha256(path.read_bytes()).hexdigest() == expected,
                'Repository source changed: '+relative)
    return len(sources)


def audit(repository=None):
    pins = json.loads((HERE/'SOURCES.json').read_text())
    required = {'inputs/ASSEMBLY.json', 'inputs/selected-result.json',
                'inputs/CLAIM.json', 'inputs/PROOF.md'}
    require(set(pins['files']) == set(pins['provenance']) == required,
            'Incomplete pinned source inventory')
    for name, expected in pins['files'].items():
        require(hashlib.sha256((HERE/name).read_bytes()).hexdigest() == expected,
                'Pinned input changed: '+name)
    if repository is not None:
        checked = repository_bindings(repository, pins)
        print('PASS_T21_REPOSITORY_BINDINGS files='+str(checked))
    assembly = json.loads((HERE/'inputs/ASSEMBLY.json').read_text())
    selected = json.loads((HERE/'inputs/selected-result.json').read_text())
    claim = json.loads((HERE/'inputs/CLAIM.json').read_text())
    require(hashlib.sha256((HERE/'inputs/ASSEMBLY.json').read_bytes()).hexdigest() ==
            selected['certificate_sha256'], 'Selected certificate binding changed')
    require(pins['files']['inputs/PROOF.md'] ==
            selected['proof_supplements'][pins['provenance']['inputs/PROOF.md']],
            'Selected proof binding changed')
    require(Q(selected['kappa']) == Q(assembly['kappa']), 'Selection and assembly disagree')
    require(Q(claim['kappa']) == Q(assembly['kappa']) and
            Q(claim['complex_lower']) == Q(assembly['complex_lower']),
            'Construction claim and assembly disagree')
    for engine in ('moment.py', 'base_two_moment.py'):
        source = 'research/complex-k492-owner-repair/vendor/multicold/engines/'+engine
        require(pins['references'][source] == assembly['input_sha256']['engines/'+engine],
                'Assembly arithmetic source binding changed: '+engine)
    replicas, m = 21, 73
    calls, live = 9*replicas, 8*112*replicas
    physical = live+504+8+2
    require(assembly['provider_counts'] == {'gauge44':calls}, 'Assembly call count')
    local = Counter({1:2548,2:338,3:446,4:162,5:72,8:8})
    idle = {48:6292,3:1,1:3}
    require({int(r):c for r,c in claim['local_profile'].items()} == dict(local) and
            {int(r):c for r,c in claim['idle'].items()} == idle,
            'Construction claim profiles disagree with the proof accounting')
    for name, expected in (('replicas',replicas), ('calls',calls), ('live',live),
                           ('physical',physical), ('rank_mass',1366848), ('deficit',6720)):
        require(type(claim[name]) is int and claim[name] == expected,
                'Construction claim accounting changed: '+name)
    derived = Counter({r:c*calls for r,c in local.items()})
    derived.update(idle)
    profile = {int(r):c for r,c in assembly['complex_profile'].items()}
    require(dict(derived) == profile, 'Local + idle profile does not match committed assembly')
    require(sum(profile.values()) == 681782, 'Child count')
    require(sum(r*c for r,c in profile.items()) == 1366848, 'Rank mass')
    require(m*live - 1366848 == 6720 == replicas*320, 'Deficit')
    native = Q(assembly['complex_lower'])
    conservative = Q(assembly['conservative_complex_lower'])
    result = {
        'status':'PASS_T21_BINOMIAL_MOMENT',
        'base_commit':pins['base_commit'],
        'assignment_seed':69,
        'source_files_sha256':pins['files'],
        'selected_kappa_unchanged':assembly['kappa'],
        'profile':{str(r):c for r,c in sorted(profile.items())},
        'child_count':681782, 'arity':m, 'live_stock':live, 'physical_stock':physical,
        'rank_mass':1366848, 'deficit':6720,
        'native':brackets(profile,m,live,native,False),
        'conservative':brackets(profile,m,live,conservative,True),
        'controls':controls(profile,native,conservative),
        'scope':'Arithmetic consequence of the pinned T21 paid profile and fallback formula. '
                'Physical construction, owner windows, invoice, outer 47 inequalities, '
                'all-size compilation and the multiplication theorem are not replayed or proved.'
    }
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write-certificate', action='store_true')
    p.add_argument('--repository', type=Path,
                   help='Also compare all pinned sources with this repository checkout')
    args = p.parse_args()
    result = audit(args.repository)
    text = json.dumps(result,indent=2,sort_keys=True)+'\n'
    path = HERE/'CERTIFICATE.json'
    if args.write_certificate:
        path.write_text(text)
    else:
        require(path.read_text() == text, 'Recorded certificate differs from fresh independent computation')
    print(result['status'], 'four strict endpoint decisions;',
          result['controls']['algebraic_comparisons'], 'algebraic comparisons;',
          result['controls']['mathematical_controls'], 'mathematical controls;',
          result['controls']['rejected_inputs'], 'rejected inputs.')


if __name__ == '__main__':
    main()
