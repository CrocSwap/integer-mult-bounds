#!/usr/bin/env python3
"""Independent bounded accounting review. No author or native engine imported.

P2 powers use fresh positive exp series and reciprocal bounds, distinct from
the reviewed worker's alternating negative exp engine. All decisions rational.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import ast
import json
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AUTHOR = ROOT/'outputs/new-approach-ceilings-20261023'
PINS = {
 'DIRECT-COMPARATOR-PROOF.md':'7462ddb298e137dd397d9dd59253d1287ca85288e3e97b151f1939f208b8b1e0',
 'SOURCES.json':'5a559fec47ea22c25a94c92ed5e4208d2788151a810912ea5701426063edb1bb',
 'CHECK-RESULT.json':'c756dbb2f47356706fc46611599ba56cbf4520360b6383fa6c02dd728ec95d5b',
 'centre0-p2/SOURCES.json':'30f720c1debd63c091280752d340ca514987f1bfa789432be177291da65592b9',
 'centre0-p2/CHECK-RESULT.json':'ce7b255e9645c66a99e5e4a849a6896b1024d9986c1b32c76943305428e08449',
 'centre0-p2/REPORT.md':'c5cea3ffb6f8fe129bb9207d619bb8d290e430fd6403532f8f2db52c32981c70',
}


def require(ok, label):
    if not ok:
        raise RuntimeError(label)


def authenticate(mode):
    pins = {p:q for p,q in PINS.items() if mode == 'both' or
            (p.startswith('centre0-p2/') == (mode == 'p2'))}
    got = {p:sha256((AUTHOR/p).read_bytes()).hexdigest() for p in pins}
    require(got == pins, 'reviewed author packet changed')
    subdirs = ('','centre0-p2') if mode == 'both' else (('centre0-p2',) if mode == 'p2' else ('',))
    for subdir in subdirs:
        base = AUTHOR/subdir
        manifest = json.loads((base/'SOURCES.json').read_text())
        for item in manifest['files']:
            path = base/item['snapshot'] if item.get('snapshot') else ROOT/item['provenance']
            require(sha256(path.read_bytes()).hexdigest() == item['sha256'], 'source manifest hash '+str(path))
    return got


@lru_cache(maxsize=None)
def log_series(z):
    require(0 <= z <= Q(1,3), 'atanh series domain')
    # log((1+z)/(1-z)) has positive terms. Bound every omitted denominator
    # below by 2N+1 and sum the remaining geometric powers.
    N = 48
    lo = sum((2*z**(2*j+1)/Q(2*j+1) for j in range(N)),Q())
    tail = 2*z**(2*N+1)/((2*N+1)*(1-z*z))
    return lo,lo+tail


@lru_cache(maxsize=None)
def logint(r):
    require(isinstance(r,int) and 1 <= r <= 17, 'bounded positive rank')
    k = r.bit_length()-1
    t = Q(r,2**k)
    a,b = log_series((t-1)/(t+1))
    c,d = log_series(Q(1,3))
    return a+k*c,b+k*d


def exp_positive(t):
    require(0 <= t < Q(1,50), 'positive exp range')
    N = 24
    term,total = Q(1),Q(1)
    for j in range(1,N+1):
        term *= t/j
        total += term
    first_omitted = term*t/(N+1)
    upper_tail = first_omitted/(1-t/(N+2))
    return total,total+upper_tail


@lru_cache(maxsize=None)
def rankpower(r,c):
    require(0 <= c <= Q(17,5000), 'bounded saving domain')
    l,u = logint(r)
    require(u < 3, 'rank logarithm below3')
    exp_lower = exp_positive(c*l)[0]
    exp_upper = exp_positive(c*u)[1]
    return r/exp_upper,r/exp_lower


def moment(hist,c):
    pairs = [(n,rankpower(r,c)) for r,n in hist.items()]
    return tuple(sum((n*x[k] for n,x in pairs),Q()) for k in (0,1))


def outward(a,b,places=24):
    scale = 10**places
    low = (a*scale).__floor__()
    high = (b*scale).__ceil__()
    return {'lower':str(Q(low,scale)),'upper':str(Q(high,scale)),
            'scale':scale,'floor_units':low,'ceil_units':high}


def direct_review():
    # Symbolic payload entries are (original_chunk,index). C reverses index.
    # Exact permutation composition checks orientation, not the source theorem.
    def swap_reverse(state,a,b):
        out = [list(x) for x in state]
        out[a],out[b] = list(reversed(state[b])),list(reversed(state[a]))
        return out
    def J(state,a,b):
        out = [list(x) for x in state]
        out[a],out[b] = list(state[b]),list(state[a])
        return out
    tested = []
    for width in (1,2,3,4,7,8):
        start = [[(owner,j) for j in range(width)] for owner in range(4)]
        out = swap_reverse(swap_reverse(swap_reverse(start,0,1),1,2),0,1)
        require(out == J(start,0,2), 'F12 F23 F12 ordinary J13 including spectator')
        out2 = swap_reverse(swap_reverse(swap_reverse(start,1,2),0,1),1,2)
        require(out2 == out, 'bab orientation')
        # R_tail reverses only the later field of this two-bank operation.
        wrapped = [list(x) for x in start]
        wrapped[1].reverse()
        wrapped = swap_reverse(wrapped,0,1)
        wrapped[1].reverse()
        require(wrapped == J(start,0,1), 'Rtail F Rtail ordinary target')
        tested.append(width)
    # Delta is NEW outside overhead minus DIRECT outside overhead. These
    # algebraic differences compare complete matched tariffs to one upper recipe.
    tariff_cases = []
    for b,delta in ((Q(6,5),Q()),(Q(5,4),Q()),(Q(3,2),Q()),(Q(3,2),Q(-2))):
        f,q = Q(1),Q(1,2)
        difference = f+4*b+delta-(3*f+6*q)
        threshold = (2*f+6*q-delta)/4
        require((difference < 0) == (b < threshold), 'complete tariff threshold')
        tariff_cases.append({'B':str(b),'Delta':str(delta),'new_minus_direct_upper':str(difference),
                              'strict_B_threshold':str(threshold)})
    require(399**5000 < 2**4983*200**5000, 'uniform domain integer power bound')
    x = Q(399,200)
    cap,deficit = Q(1,2)+Q(3,2)/x,4*x-2-6/x
    require(cap == Q(333,266) and deficit == Q(19767,6650), 'exact sharp rational constants')
    require((4*Q(3,2)-2-6/Q(3,2)) == 0, 'transition equality')
    require(4*Q(7,5)-2-6/Q(7,5) < 0, 'sign reversal below transition')
    # d/dx(4x-2-6/x)=4+6/x²>0, and cap decreases in x.
    require(4+6/(x*x) > 0, 'monotone nominal deficit')
    return {'status':'PASS_SCOPED_SOURCE_ORIENTATION_AND_CONDITIONAL_TARIFF_REVIEW',
            'orientation_width_controls':tested,'complete_tariff_cases':tariff_cases,
            'domain_C':['0','17/5000'],'strict_x_lower':'399/200',
            'strict_necessary_B_over_F_upper':str(cap),'strict_nominal_deficit_lower':str(deficit),
            'upper_recipe_logic':'Failure to beat a constructive upper recipe excludes improvement against an available competitor; passing is not a physical admission or optimality proof',
            'power_B_price':'hypothetical only; scalar owner rank is not recursive address rank',
            'author_formal_theorem_replay':False,'new_kappa':None}


def p2_review():
    base = AUTHOR/'centre0-p2'
    checked = json.loads((base/'CHECK-RESULT.json').read_text())
    design = json.loads((base/'frozen/AUTHOR-OPTIMISTIC-SCREEN.json').read_text())
    producer = json.loads((base/'frozen/SOURCE-DERIVED-PRODUCER.json').read_text())
    native_audit = json.loads((HERE/'PRODUCER-PACKET-RESULT.json').read_text())
    require(native_audit['status'] == 'PASS_SOURCE_PACKET_AUDIT_ONLY', 'independent source packet audit')
    require(sha256((base/'frozen/SOURCE-DERIVED-PRODUCER.json').read_bytes()).hexdigest()
            == native_audit['packet_hashes_after']['CORRECTED-DERIVATION.json'], 'exact same corrected producer')
    local = Counter({int(k):v for k,v in producer['paid_profile'].items()})
    paid = Counter({r:2*n for r,n in local.items()})
    paid[1] += 336
    paid[8] += 224
    targets = Counter({int(k):2*v for k,v in producer['full_independent_inputs']['helper_native_target_rank_profile'].items()})
    require(sum(targets.values()) == 816, 'each original helper credited once')
    targets[9] += 224
    targets[17] += 224
    require(dict(paid) == {1:4754,2:824,3:1020,4:254,5:80,8:226}, 'full conditional payment incidence')
    require(dict(targets) == {4:56,7:14,8:94,9:876,17:224}, 'full unproved target grant')
    require(dict(paid) == {int(k):v for k,v in design['conditional_paid_minimum'].items()}, 'author paid profile')
    require(dict(targets) == {int(k):v for k,v in design['target_grant'].items()}, 'author target grant')
    require(design['status'] == 'AUTHOR_DESIGN_OPTIMISM_ONLY_UNREALIZED_TARGET_GRANT', 'unrealized status')
    proposal = (base/'frozen/FAILED-PREDECESSOR-PROPOSAL.md').read_text()
    require('required h endpoint fails' in proposal, 'predecessor failure stays explicit')
    original_paid = ast.literal_eval(re.search(r'`P=(\{[^\n]+\})`',proposal).group(1))
    require(original_paid[8]+2 == paid[8] and original_paid[1] == paid[1], '+2H8 and no H1 removal')
    a,b = Q('.0030217758'),Q('.00339999')
    points = {}
    for c in (a,b):
        tl,tu = moment(targets,c)
        pl,pu = moment(paid,c)
        lo,hi = tl-pu,tu-pl
        recorded = checked['point_enclosures'][str(c)]
        require(Q(recorded['outward_lower']) <= lo <= hi <= Q(recorded['outward_upper']),
                'independent positive-exp interval inside reported outward enclosure')
        points[str(c)] = outward(lo,hi)
        if c == b:
            minimum_lo,minimum_hi = lo,hi
    # H_r decreases, log r is nonnegative, so this is an upper derivative on [a,b].
    paid_upper = sum((n*rankpower(r,a)[1]*logint(r)[1] for r,n in paid.items()),Q())
    targets_lower = sum((n*rankpower(r,b)[0]*logint(r)[0] for r,n in targets.items()),Q())
    derivative_upper = paid_upper-targets_lower
    require(derivative_upper < -19660, 'uniform strict derivative upper bound')
    require(12 < minimum_lo <= minimum_hi < 13, 'minimum endpoint sharp H1 integer budget')
    require(rankpower(12,a)[1] < minimum_lo, 'single rank12 fits entire interval')
    require(rankpower(13,b)[0] > minimum_hi, 'single rank13 fails included endpoint')
    placement = json.loads((HERE/'DECLARED-PRODUCT-RESULT.json').read_text())
    require(placement['status'] == 'REJECT_DECLARED_PRODUCT_PLACEMENT_BY_EXACT_NECESSARY_UNIT_IDENTITY',
            'failed candidate placement cannot be omitted from interpretation')
    return {'status':'PASS_CONDITIONAL_RELAXATION_ARITHMETIC_ONLY_FAILED_PLACEMENT_RETAINED',
            'independent_method':'48-term rational atanh log plus positive 24-term exp with geometric tail and reciprocal; no author/worker engine imported',
            'target_grant':dict(sorted(targets.items())),'conditional_paid':dict(sorted(paid.items())),
            'original_helpers_once':816,'unproved_main_jobs':448,'new_H8':2,'removed_H1':0,
            'point_enclosures':points,'derivative_upper':outward(derivative_upper,derivative_upper),
            'minimum_at':'included right endpoint by uniform strict decrease',
            'maximum_additional_integer_H1_calls':12,'thirteen_positive_rank_calls_fail_at_b':True,
            'largest_single_additional_integer_rank_uniformly':12,
            'remaining_after12H1_at_b':outward(minimum_lo-12,minimum_hi-12),
            'candidate_declared_product_placement':'FAILED_e1_coefficient0_residual42',
            'compiler_reserve':None,'finite_work_funded':False,'actual_caller':False,'new_kappa':None}


def main():
    require(not ('--p2-only' in sys.argv and '--direct-only' in sys.argv), 'choose one separate review mode')
    mode = 'p2' if '--p2-only' in sys.argv else ('direct' if '--direct-only' in sys.argv else 'both')
    before = authenticate(mode)
    after_values = {}
    if mode in ('both','direct'):
        after_values['direct_comparator'] = direct_review()
    if mode in ('both','p2'):
        after_values['corrected_centre_p2_relaxation'] = p2_review()
    after = authenticate(mode)
    result = {'status':'PASS_SCOPED_INDEPENDENT_ECONOMIC_REVIEW_'+mode.upper(),
              'author_packet_hashes_before':before,'author_packet_hashes_after':after,
              **after_values,
              'source_author_packets_edited':False,'native_or_compiler_execution':False,
              'new_kappa':None}
    stem = 'ECONOMIC-REVIEWS' + ('' if mode == 'both' else '-'+mode.upper()) + '-RESULT'
    out = HERE/(stem+('-OPTIMIZED' if sys.flags.optimize else '')+'.json')
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'result':str(out)}))


if __name__ == '__main__':
    main()
