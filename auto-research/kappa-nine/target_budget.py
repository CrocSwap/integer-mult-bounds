"""Exact necessary screens for kappa > 1/512; no new finite construction.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
Run from any directory. Does not modify published certificates.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import math

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DENOM = 511
SCALE = 10**16


def require(condition, message):
    if not condition:
        raise ValueError(message)


def encode(x):
    if isinstance(x, Q):
        return str(x)
    if isinstance(x, dict):
        return {str(k): encode(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [encode(v) for v in x]
    return x


@lru_cache(None)
def root_bounds(value, degree=DENOM, scale=SCALE):
    """Enclose value**(1/degree) by adjacent fixed-denominator rationals.

    Every endpoint is checked by integer powers. No floating-point acceptance.
    """
    value = Q(value)
    require(value > 0 and degree > 0 and scale > 0, 'positive root input')
    lo, hi = 0, scale
    rhs = value.numerator * scale**degree
    den = value.denominator
    while hi**degree * den < rhs:
        hi *= 2
    while hi - lo > 1:
        mid = (hi + lo)//2
        if mid**degree * den <= rhs:
            lo = mid
        else:
            hi = mid
    require(lo**degree*den <= rhs <= hi**degree*den, 'root enclosure')
    return Q(lo, scale), Q(hi, scale)


def moment(rows, m, W):
    """Bounds on sum(n_t/W)*(t/m)**(1-1/511). Fractional counts allowed
    for explicitly optimistic relaxations, never emitted as physical calls.
    """
    require(m > 1 and W > 0, 'positive dimension and volume')
    lower = upper = Q(0)
    for t, n in rows.items():
        require(type(t) is int and 0 < t < m and n >= 0, 'invalid child')
        l, u = root_bounds(Q(m, t))
        weight = Q(n)*t/(W*m)
        lower += weight*l
        upper += weight*u
    return lower, upper


def profile_parts(certificate, profiles):
    b = certificate['bit']
    N, m, W = b['N'], b['m'], b['W']
    parts = {'data': Counter({1:19*N, 21:2*N, 17:2*N, 481:2*N})}
    for p in profiles:
        h, v, R = p['h'], p['v'], p['R']
        require(N % v == 0, 'nonintegral invocation count')
        rep, bank = N//v, N//v*R
        parts[f'compiler_{h}'] = Counter({t:n*rep for t,n in enumerate(p['blocks']) if t and n})
        parts[f'role_boundary_{h}'] = Counter({h:bank, m-2*h:bank})
        parts[f'fixed_center_{h}'] = Counter({1:2*N, h-2:2*N})
    full = sum(parts.values(), Counter())
    require(full == Counter({int(t):n for t,n in b['child_multiplicities'].items()}), 'profile reconstruction')
    require(sum(t*n for t,n in full.items()) == b['total_rank'], 'rank mass')
    require(2*N+sum(N//p['v']*p['R'] for p in profiles) == W, 'volume roles')
    return parts


def hypothetical_assembly(certificate):
    path = ROOT/'research/pair-assembly/balanced_assembly.py'
    spec = importlib.util.spec_from_file_location('kappa9_assembly', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # These exponents are targets ONLY; baseline networks do not certify them.
    result = module.assembly(certificate['finite_bridge'], Q(11,5000),
                             Q(1,512)+Q(1,10**9), a_complex=Q(1,400))
    require(len(result['constraints']) == 47, 'assembly coverage')
    return {'status':'hypothetical exponent substitution only; no networks supplied',
            'bit_target':Q(11,5000), 'complex_target':Q(1,400),
            'kappa':result['parameters']['kappa'],
            'all_47_slacks':result['constraints'], 'margins':result['margins'],
            'bridge_scope':'Current dimensions/role/child/scalar bridge only; changed constructions need their own bridge.',
            'assembly_source_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def audit():
    manifest = json.loads((HERE/'baseline/SOURCE.json').read_text())
    for name, receipt in manifest['files'].items():
        require(hashlib.sha256((HERE/'baseline'/name).read_bytes()).hexdigest() == receipt['sha256'], 'baseline changed: '+name)
    d = json.loads((HERE/'baseline/certificate.json').read_text())
    profiles = [json.loads((HERE/f'baseline/profiles-{h}.json').read_text()) for h in (23,25)]
    b=d['bit']; N,m,W,s=b['N'],b['m'],b['W'],b['total_rank']
    parts=profile_parts(d,profiles)
    details={}
    for name, rows in parts.items():
        lo,hi=moment(rows,m,W)
        mass=Q(sum(t*n for t,n in rows.items()),W*m)
        details[name]={'rank_mass':mass,'moment_interval':[lo,hi],
                       'target_penalty_interval':[lo-mass,hi-mass],
                       'diagnostic_entropy_float':sum(n/W*t/m*math.log(m/t) for t,n in rows.items())}
    actual=moment(sum(parts.values(),Counter()),m,W)
    require(actual[0]>1, 'baseline unexpectedly attains target')
    r=max(int(t) for t in b['child_multiplicities'])
    require(s**DENOM*m >= (W*m)**DENOM*r, 'maxchild exclusion')
    # Keep the data/center ledger. Grant arbitrary R_h >= 0 and ideal packing
    # of compiler mass h*R_h+h*(h-1) into h-wide children. Each R coefficient
    # is strictly larger than its contribution to W, so the constant term
    # alone excludes EVERY nonnegative role-count pair if it is >2N.
    fixed=sum((rows for name,rows in parts.items() if name=='data' or name.startswith('fixed_center_')),Counter())
    constant=fixed.copy()
    coefficients={}
    for p in profiles:
        h,v=p['h'],p['v']
        constant[h]+=Q(N,v)*(h-1)
        coeff=moment(Counter({h:2,m-2*h:1}),m,1)
        require(coeff[0]>1, 'role coefficient bound')
        coefficients[h]={'per_invocation_role_moment_interval':coeff,
                         'role_volume_coefficient':1}
    bound=moment(constant,m,2*N)
    require(bound[0]>1, 'role compression exclusion failed')
    # Still more generous: entirely erase the non-role compiler overhead.
    no_center_return=moment(fixed,m,2*N)
    require(no_center_return[0]>1, 'fixed data floor does not exclude')
    # A second, more generous relaxation: replace each retained non-compiler
    # macro by ONE child with its entire rank. Concavity gives a lower bound
    # on every subdivision of that rank. Not an implemented batching lemma.
    ideal_fixed=Counter({m-47:2*N,1:N,22:2*N,24:2*N})
    ideal_constant=ideal_fixed.copy()
    ideal_coefficients={}
    for p in profiles:
        h,v=p['h'],p['v']
        ideal_constant[h]+=Q(N,v)*(h-1)
        coeff=moment(Counter({h:1,m-h:1}),m,1)
        require(coeff[0]>1, 'ideal role coefficient')
        ideal_coefficients[h]=coeff
    ideal_bound=moment(ideal_constant,m,2*N)
    require(ideal_bound[0]>1, 'ideal per-macro exclusion failed')
    # Retaining the current distinct auxiliary source-injection ports forces
    # R_h >= v_h. Even erase every fixed center overhead and grant all the
    # ideal macro blocks: the mandatory one source role per label still fails.
    source_floor=ideal_fixed.copy()
    for p in profiles:
        h=p['h'];source_floor[h]+=N;source_floor[m-h]+=N
    source_floor_bound=moment(source_floor,m,4*N)
    require(source_floor_bound[0]>1,'source floor exclusion failed')
    a=Q(1,DENOM)
    return {'status':'EXACT TARGET FEASIBILITY SCREENS; no improved kappa',
            'baseline':manifest,'target_kappa':Q(1,512),'necessary_bit_saving_strictly_above':a,
            'necessary_complex_at_beta_1_over_20_strictly_above':a/Q(19,20),
            'bit_rank_deficit':Q(W*m-s,W*m),'actual_target_moment_interval':actual,
            'parts':details,
            'fixed_mass_maxchild_screen':{'m':m,'maxchild':r,'rank_sum':s,'W':W,
                'exact_exclusion':True,'inequality':'s^511*m >= (W*m)^511*r',
                'necessary_maxchild_at_same_normalized_rank_mass':m*s**DENOM//((W*m)**DENOM)+1},
            'arbitrary_role_compression_screen':{'scope':'m=575; retained data/center profile and auxiliary boundary blocks; compiler mass hR+h(h-1) packed optimistically into h-blocks; any nonnegative R23,R25',
                'constant_moment_at_R_zero_interval':bound,'role_coefficients':coefficients,
                'even_if_fixed_compiler_return_mass_erased_interval':no_center_return,
                'conclusion':'Cannot reach a=1/511 in this relaxation. Must change retained data/center blocks or another stated assumption.'},
            'ideal_whole_macro_screen':{'scope':'Retain two rank-528 data macros and one rank-one correction per pair, two rank-(h-1) growth macros per axis and pair, auxiliary boundary rank m-h, and compiler mass hR+h(h-1) with child widths at most h. Grant full-rank single-child batching for every non-compiler macro and arbitrary R23,R25>=0.',
                'constant_moment_at_R_zero_interval':ideal_bound,
                'role_moment_coefficients':ideal_coefficients,
                'no_central_overhead_constant_interval':moment(ideal_fixed,m,2*N),
                'conclusion':'Even ideal within-macro batching plus arbitrary role compression cannot reach the target under this ledger. Changing macro boundaries, central rank loss, geometry or volume obligations is outside this exclusion.'},
            'zero_center_loss_source_floor_screen':{'scope':'Same rank-one 23x25 data/growth/boundary macros, all fixed center loss erased, ideal batching, and the retained distinct auxiliary injection ports R_h>=v_h.',
                'minimum_role_ratios':[1,1],'moment_interval':source_floor_bound,
                'proof':'Start from each axis R_h=v_h. All additional role coefficients exceed their volume coefficients, so they preserve rejection. The floor follows from the distinct source-port inventory, not from an assertion about all possible circuits.',
                'conclusion':'Even eliminating central loss cannot attain the target while retaining these geometry, macro and injection-port obligations.'},
            'hypothetical_joint_target':hypothetical_assembly(d),
            'scope':'All exclusions concern the stated full-volume moment and preserved ledger. They are not all-network or integer multiplication lower bounds.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
    result=encode(audit());text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.output:args.output.write_text(text)
    print('PASS baseline reconstruction, exact 511th-root enclosures, fixed-mass and role-compression exclusions, hypothetical 47-row assembly')
