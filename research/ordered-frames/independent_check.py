#!/usr/bin/env python3
"""Independent rational audit of the ordered-frame finite certificate.

Uses 40-term logarithm sums and degree-ten exponential bounds, reconstructs
paid child multiplicities and all 47 assembly slacks without importing the
production arithmetic or assembly modules. Construction and all-size theorem
hypotheses remain outside this arithmetic audit. Prepared with Codex assistance.
"""
import argparse
import ast
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import sys

if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rational(value):
    require(type(value) in (int, str, Q), 'Non-exact rational input')
    return Q(value)


def integer(value):
    value = rational(value)
    require(value.denominator == 1, 'Nonintegral input')
    return value.numerator


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def serialize(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serialize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serialize(v) for v in value]
    return value


def check_hashes(manifest):
    for name, expected in manifest['files'].items():
        require(digest(ROOT/name) == expected, 'Pinned source changed: '+name)


@lru_cache(None)
def logarithm(value):
    """Exact atanh series after range reduction; no decimal rounding."""
    value = rational(value)
    require(value >= 1, 'Logarithm domain')
    powers = 0
    while value > 2:
        value /= 2
        powers += 1
    def reduced(y):
        z = (y-1)/(y+1)
        lower = 2*sum((z**(2*j+1)/Q(2*j+1) for j in range(40)), Q())
        return lower, lower+2*z**81/(81*(1-z*z))
    lo, hi = reduced(value)
    lo2, hi2 = reduced(Q(2))
    return lo+powers*lo2, hi+powers*hi2


def exponential(value):
    """Terms through degree ten; tail ratios from term eleven are <= x/12."""
    value = rational(value)
    require(0 <= value < 1, 'Exponential domain')
    total = term = Q(1)
    for degree in range(1, 11):
        term *= value/degree
        total += term
    return total, total+(term*value/11)/(1-value/12)


def moment(m, width, rows, saving):
    require(0 < saving < 1 and width > 0, 'Moment domain')
    lower = upper = Q()
    for child, count in sorted(rows.items()):
        require(type(child) is int and type(count) is int and 0 < child < m and count > 0,
                'Invalid paid child')
        lo, hi = logarithm(Q(m, child))
        weight = Q(child*count, m*width)
        lower += weight*exponential(saving*lo)[0]
        upper += weight*exponential(saving*hi)[1]
    return lower, upper


def reconstruct_paid(certificate):
    bit = certificate['bit']
    m, count = 23*25, comb(23, 3)*comb(25, 3)
    rows = Counter({1: 19*count, 21: 2*count, 17: 2*count, 481: 2*count})
    width, loss = 2*count, 0
    axes = bit['axes']
    require(sorted(f['h'] for f in axes) == [23, 25], 'Missing physical axis')
    for f in axes:
        h, vertices, roles = (integer(f[k]) for k in ('h', 'v', 'R'))
        require(vertices == comb(h, 3) and roles > 0, 'Invalid physical axis dimensions')
        require(f['loss'] == h*(h-1), 'Axis loss changed')
        require(f['crt_disagreements'] == 0 and f['field_prime'] == 2**61-1,
                'Finite profile exactness receipt failed')
        blocks = list(map(integer, f['blocks']))
        require(all(n >= 0 for n in blocks) and blocks[h] == 0, 'Copied center counted twice')
        mass = sum(t*n for t, n in enumerate(blocks))
        require(mass == f['rank_sum'] == h*roles+h*(h-1), 'Axis rank identity failed')
        replay = certificate['axes'][str(h)]['replay']
        require(replay['roles'] == roles and replay['rank_mass'] == mass,
                'Axis replay/profile mismatch')
        repetitions = count//vertices
        width += repetitions*roles
        loss += repetitions*h*(h-1)
        for child, multiplicity in enumerate(blocks):
            if child and multiplicity:
                rows[child] += repetitions*multiplicity
        rows[h] += repetitions*roles
        rows[m-2*h] += repetitions*roles
        rows[1] += 2*count
        rows[h-2] += 2*count
    supplied = {int(t): integer(n) for t, n in bit['child_multiplicities'].items()}
    require(dict(rows) == supplied, 'Paid child multiplicities differ from reconstructed axes')
    mass = sum(t*n for t, n in rows.items())
    require(mass == m*width-count+loss == m*width-1846900,
            'Full paid rank identity failed')
    require((bit['m'], bit['N'], bit['W'], bit['L'], bit['total_rank'], bit['deficit'], bit['maxchild']) ==
            (m, count, width, loss, mass, 1846900, max(rows)), 'Paid dimensions mismatch')
    require(max(rows) == 529, 'Largest child changed')
    bridge = certificate['assembly']['finite_bridge']['bit']
    require((bridge['m'], bridge['W'], bridge['maxchild']) == (m, width, max(rows)),
            'Paid profile/assembly bridge mismatch')
    return m, width, rows


def check_bridge(bridge):
    coefficient = 0
    for name in ('bit', 'complex'):
        data = bridge[name]
        m, width, child = (integer(data[k]) for k in ('m', 'W', 'maxchild'))
        require(0 < child < m and width > 0, 'Bridge contraction failed')
        power = 1
        while m**power <= 2*child**power:
            power += 1
        require(data['halving_degree'] == power and data['wire_bits'] == width.bit_length(),
                'Bridge dimension logarithm mismatch')
        coefficient += power*width.bit_length()
    p = bridge['complex']
    m, width, child, rank, scalar = (integer(p[k]) for k in ('m', 'W', 'maxchild', 's', 'scalar_group_upper'))
    require(0 < rank < m*width and scalar > 0, 'Complex bridge domain')
    error = 64*(width+m+scalar+1)**3
    bound = rank+error
    literal = 2*scalar*width**2+8*rank+4*width+4+32*m
    semantics = dict(E=error, B=bound, C0=32*m*bound**2, C1=1,
                     literal_charge=literal, strict_literal_gap=error-literal,
                     induction_gap=2*bound*(m-child)-(rank+error))
    require(error > literal and semantics['induction_gap'] >= 0 and semantics['C0'] > 2*bound+18,
            'Semantic bridge inequality failed')
    require({k:rational(v) for k,v in bridge['semantic'].items()} == semantics,
            'Semantic bridge constants mismatch')
    stock = bridge['rows']
    degree = integer(stock['degree'])
    gap = degree-Q(51,25)*coefficient
    expected = dict(coefficient=coefficient, degree=degree, degree_gap=gap, suffix_slope=4*degree)
    require(gap > 0 and degree > 0 and {k:rational(v) for k,v in stock.items()} == expected,
            'Row stock constants mismatch')
    return semantics, expected


def independent_assembly(certificate):
    supplied = certificate['assembly']
    a, kappa, h = (rational(certificate[k]) for k in ('bit_saving', 'kappa', 'h'))
    b = rational(supplied['parameters']['a_complex'])
    beta = rational(supplied['parameters']['beta'])
    require(0 < a < b < Q(1,32) and 0 < beta < 1 and 0 < h < Q(1,2) and kappa > 0,
            'Assembly parameter domain')
    semantics, stock = check_bridge(supplied['finite_bridge'])
    q = a-2*a*h
    epsilon = (1-h)/(1+q)
    lam_prime = 1-q
    tau, sigma = 1-a, 1-b
    lam = (tau+lam_prime)/2
    c = q+h/4
    controlling = epsilon*q
    r = (controlling+1-epsilon)/2
    delta = h/8
    internal, leaf = 1-a, 1-(1-beta)*b
    margins = dict(g1=1-epsilon, g2=a, g3=controlling, g4=a,
                   g5=min(1-epsilon-delta,r-delta), g6=1-epsilon-delta, g7=epsilon)
    slacks = dict(
        a_positive=a, a_below_b=b-a, b_below_one_over32=Q(1,32)-b,
        beta_positive=beta, beta_below_one=1-beta, phase_leaf_above_bit=(1-beta)*b-a,
        q_positive=q, q_below_internal=1-internal-q, q_below_leaf=1-leaf-q,
        c_positive=c, c_below_one=1-c, q_below_reservations=c-q,
        lambda_above_tau=lam-tau, lambda_above_sigma=lam-sigma,
        lambda_above_internal=lam-internal, lambda_prime_above_lambda=lam_prime-lam,
        compact_leaf=lam_prime-leaf, compact_reservations=lam_prime-1+c,
        lambda_prime_below_one=q, epsilon_positive=epsilon, epsilon_below_one=1-epsilon,
        guard_width=1-epsilon, K_geometry=1-epsilon*(1+c), K_dominates_log=epsilon*c,
        record_suffix=1-epsilon, phase_local=1-epsilon-delta, phase_boundary=r-delta,
        gamma_sublinear=1-epsilon-r, cell_above_band=epsilon-(1-r)/2,
        prime_interval_packing=1-epsilon, alpha_positive=r, alpha_below_one=1-r,
        alpha_below_one_fourth=Q(1,4)-r, delta_positive=delta,
        delta_below_one_eighth=Q(1,8)-delta, short_record_fallback=epsilon-a,
        small_field_exposure=1-epsilon-controlling,
        artificial_boundary=8-epsilon+r-delta-controlling,
        literal_scalar_guard=Q(semantics['strict_literal_gap']), row_product_gap=stock['degree_gap'])
    slacks.update({name+'_above_kappa': margin-kappa for name,margin in margins.items()})
    require(len(slacks) == 47 and all(x > 0 for x in slacks.values()), 'Strict assembly inequality failed')
    require(slacks == {name:rational(x) for name,x in supplied['constraints'].items()},
            'Recomputed assembly slacks mismatch')
    require(margins == {name:rational(x) for name,x in supplied['margins'].items()} and
            min(margins.values()) == controlling, 'Recomputed exponent margins mismatch')
    parameters = dict(a_bit=a, a_complex=b, tau=tau, sigma=sigma, beta=beta, h=h,
                      q=q, c=c, epsilon=epsilon, lambda_=lam, lambda_prime=lam_prime,
                      alpha_squared_power=r, delta=delta, C0=semantics['C0'], C1=1, kappa=kappa)
    require(parameters == {name:rational(x) for name,x in supplied['parameters'].items()},
            'Assembly parameter formulas mismatch')
    require(rational(supplied['minimum_margin']) == controlling and
            rational(supplied['absorption_gap']) == controlling-kappa and
            rational(supplied['scoped_limit']) == a/(1+a), 'Assembly bounds mismatch')
    require({name:rational(x) for name,x in supplied['recurrence'].items()} ==
            dict(internal=internal, leaf=leaf, reservations=1-c), 'Recurrence formulas mismatch')
    require(1-epsilon-controlling == h and 1-epsilon-r == h/2 and
            1-epsilon*(1+c) == h-epsilon*h/4, 'Balanced identities failed')
    return controlling, slacks, margins


def compiler_equivalence():
    """Check production functions against the original plus stated policy edit."""
    base = (ROOT/'scripts/experiments/rank_pair_compiler.py').read_text()
    old = """   for s in sorted(retired,key=lambda s:(-blocks[frames[s]]['rank'],s)):
    if not contains(blocks[frames[s]]['frame'],blocks[g]['frame']):continue
    e=ins(s)
    if e is None:continue
    assert e>>s&1;e^=1<<s;aa=[]
    while e:
     bit=e&-e;aa.append(bit.bit_length()-1);e^=bit
    for a in aa:xor(s,a,g)
    assert not slots[s];retired.remove(s);stats['reclaimed']+=1;stats['clearing_xors']+=len(aa);return s"""
    new = """   candidates=[]
   for s in sorted(retired,key=lambda s:(-blocks[frames[s]]['rank'],s)):
    if not contains(blocks[frames[s]]['frame'],blocks[g]['frame']):continue
    e=ins(s)
    if e is None:continue
    assert e>>s&1;e^=1<<s;aa=[]
    while e:
     bit=e&-e;aa.append(bit.bit_length()-1);e^=bit
    candidates.append(((sum(blocks[g]['rank']-blocks[frames[a]]['rank'] for a in [s]+aa),len(aa),-blocks[frames[s]]['rank'],s),s,aa))
    if not minimum_raise:break
   if candidates:
    _,s,aa=min(candidates)
    for a in aa:xor(s,a,g)
    assert not slots[s];retired.remove(s);stats['reclaimed']+=1;stats['clearing_xors']+=len(aa);return s"""
    require(base.count(old) == 1, 'Original compiler selection block changed')
    expected = base.replace(old,new).replace('def compile_(h,matching=True,reclaim=False,dirty=True):',
                                             'def compile_(h,matching=True,reclaim=False,dirty=True,minimum_raise=True):')
    def functions(text):
        return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(text).body
                if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    require(functions(expected) == functions((HERE/'compiler.py').read_text()),
            'Production compiler has an unstated function change')
    return dict(result='PASS',functions_checked=sorted(functions(expected)),
                allowed_change='Select minimum paid frame-rank increase among witnessed dependent retired slots; optional false mode retains first eligible dependency')


def positive_lower_bound(value):
    scale = 10**40
    scaled = value*scale
    result = Q(scaled.numerator//scaled.denominator,scale)
    require(result > 0, 'Rounded positive gap vanished')
    return result


def generate():
    source = json.loads((HERE/'SOURCE.json').read_text())
    check_hashes(source)
    cert = json.loads((HERE/'certificate.json').read_text())
    require(cert['sources'] == source, 'Certificate/source manifest mismatch')
    for h in (23,25):
        require(json.loads((HERE/f'frame-profiles-{h}.json').read_text()) ==
                next(f for f in cert['bit']['axes'] if f['h'] == h), 'Frozen axis profile mismatch')
        axis = json.loads((HERE/f'axis-{h}.json').read_text())
        require(axis == cert['axes'][str(h)] and digest(HERE/f'frame-word-{h}.json.gz') == axis['gzip_sha256'],
                'Frozen axis word/receipt mismatch')
    m, width, rows = reconstruct_paid(cert)
    a, kappa = rational(cert['bit_saving']), rational(cert['kappa'])
    next_a = rational(cert['bit']['next_saving'])
    step = next_a-a
    require(step == Q(1,10**18) and rational(cert['h']) == step, 'Grid/backoff mismatch')
    lo, hi = moment(m,width,rows,a)
    next_lo, next_hi = moment(m,width,rows,next_a)
    require(rational(cert['bit']['accepted']['lower']) <= lo <= hi <=
            rational(cert['bit']['accepted']['upper']) < 1, 'Accepted moment enclosure failed')
    require(1 < rational(cert['bit']['rejected']['lower']) <= next_lo <= next_hi <=
            rational(cert['bit']['rejected']['upper']), 'Next bit grid enclosure failed')
    margin, slacks, margins = independent_assembly(cert)
    require(kappa < margin <= kappa+step, 'Next kappa grid rejection failed')
    old = json.loads((ROOT/'research/rank-pair/screen-certificate.json').read_text())
    old_kappa = rational(old['kappa'])
    require(kappa > old_kappa == rational(cert['comparison']['pr63_kappa']),
            'Incumbent comparison failed')
    require(rational(cert['comparison']['absolute_gain']) == kappa-old_kappa and
            rational(cert['comparison']['relative_gain']) == kappa/old_kappa-1 and
            cert['comparison']['saved_wires'] == old['bit']['W']-width,
            'Incumbent comparison arithmetic mismatch')
    old_rows = {int(t):integer(n) for t,n in old['bit']['child_multiplicities'].items()}
    old_lower, _ = moment(old['bit']['m'],old['bit']['W'],old_rows,a)
    require(1 < rational(cert['comparison']['pr63_network_at_new_bit_lower']) <= old_lower,
            'Old network exclusion failed')
    controls = []
    bad = deepcopy(source)
    bad['files'][next(iter(bad['files']))] = '0'*64
    try:
        check_hashes(bad)
    except ValueError as err:
        require('Pinned source changed' in str(err), 'Wrong source control failure')
        controls.append('Incorrect pinned source hash rejected')
    else:
        raise ValueError('Bad source hash accepted')
    omitted = deepcopy(cert)
    child = min(omitted['bit']['child_multiplicities'], key=int)
    del omitted['bit']['child_multiplicities'][child]
    try:
        reconstruct_paid(omitted)
    except ValueError as err:
        require('Paid child multiplicities' in str(err), 'Wrong omitted-child control failure')
        controls.append('Omitted paid child rejected by independent reconstruction')
    else:
        raise ValueError('Omitted paid child accepted')
    changed = deepcopy(cert)
    changed['assembly']['constraints']['g3_above_kappa'] = '0'
    try:
        independent_assembly(changed)
    except ValueError as err:
        require('slacks mismatch' in str(err), 'Wrong assembly control failure')
        controls.append('Falsified assembly slack rejected by independent formulas')
    else:
        raise ValueError('Falsified assembly slack accepted')
    names = ['independent_check.py','check.py','compiler.py','producer.py','selection.json','SOURCE.json','certificate.json']
    return serialize(dict(
        status='PASS independent finite arithmetic and source audit',
        audited_files={name:digest(HERE/name) for name in names},
        source_hashes_checked=len(source['files']),
        parameters=dict(bit_saving=a,kappa=kappa,h=rational(cert['h'])),
        finite_profile=dict(m=m,W=width,paid_children=len(rows),total_rank=sum(t*n for t,n in rows.items()),
                            independently_reconstructed=True),
        method=dict(logarithm='40 exact atanh terms; tail 2*z^81/(81*(1-z^2)); no rounding',
                    exponential='Taylor degree 10; tail term_11/(1-x/12); no rounding',
                    assembly='Independent transcription and exact comparison of all 47 slacks, seven margins, parameter, semantic bridge and row-stock formulas'),
        bounds=dict(accepted_moment_upper_gap_at_least=positive_lower_bound(1-hi),
                    next_bit_moment_lower_gap_at_least=positive_lower_bound(next_lo-1),
                    assembly_gap=margin-kappa,next_kappa_rejected=True,
                    old_network_lower_gap_at_least=positive_lower_bound(old_lower-1)),
        assembly=dict(strict_constraints_checked=len(slacks),margins_checked=len(margins)),
        compiler=compiler_equivalence(),negative_controls=controls,
        scope='Finite arithmetic and source equivalence only. The separate production check replays complete dirty words and regenerates actual fixed-basis profiles. This audit does not prove the inherited analytic, all-size compiler, fixed-alphabet tape, precision, routing, prime-selection or recovery hypotheses; no unconditional theorem, practical speedup or global optimality is claimed.'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    result = generate()
    path = HERE/'independent-audit.json'
    if args.record:
        path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        require(result == json.loads(path.read_text()), 'Independent audit receipt mismatch')
    print('PASS independent exact moment, paid profile, 47 constraints and seven margins')
    print('PASS source/compiler equivalence and three failure controls')
