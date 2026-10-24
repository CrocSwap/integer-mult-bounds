"""Price the complete BIT controller, cover and compiler.

The controller and tail proof follow Cinna Davis, zxv and the retained
mixed-target work of Jacob Alan Sussman. Apache-2.0.
Ali Romman with substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import json
import local as L

TESTED, UNIFORM = Q('.0034678'), Q('.0034668')
AFTER, ATOM, OLD_ORDINARY = Q('.0034578'), Q('.004'), Q('.0000384599')
ADMITTED = Q('.00344412')


def encode(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k):encode(v) for k,v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    return value


def controller(word):
    n = 2*word['pairs']
    L.need((word['kind'], n, word['prefix_pairs']) == ('bit', 32, 7), 'Source BIT p16/a7 controller')
    def xor(dst, src):
        for term, mask in src.items():
            value = dst.get(term, 0) ^ mask
            if value:
                dst[term] = value
            else:
                dst.pop(term, None)
    def shifted(row, monomial):
        return {term ^ monomial: mask for term, mask in row.items()}
    def boundary(program):
        rows = [1 << i for i in range(n)]
        for event in program:
            op, a, b = event
            if op == 'ADD':
                rows[a] ^= rows[b]
            else:
                L.need(op == 'SWAP', 'Binary boundary operation')
                rows[a], rows[b] = rows[b], rows[a]
        return rows
    for side in ('left', 'right'):
        L.need(boundary(word['boundaries'][side+'_program']) == word['boundaries'][side+'_rows'],
               'Every binary boundary coefficient')
    rows = [{0:mask} for mask in word['boundaries']['right_rows']]
    for event in word['physical_events']:
        op = event[0]
        if op in ('LOCAL', 'QUERY_SHEAR'):
            _, stage, pair, reverse = event
            x, y = 2*pair, 2*pair+1
            if reverse:
                x, y = y, x
            xor(rows[y], shifted(rows[x], 1))
            if op == 'LOCAL':
                for role in (x, y):
                    rows[role] = shifted(rows[role], 1 << (stage+1))
        elif op == 'IDLE':
            _, pair, stages = event
            monomial = sum(1 << (stage+1) for stage in stages)
            for role in (2*pair, 2*pair+1):
                rows[role] = shifted(rows[role], monomial)
        elif op == 'ADD':
            xor(rows[event[1]], rows[event[2]])
        else:
            L.need(op == 'SWAP', 'Physical controller operation')
            rows[event[1]], rows[event[2]] = rows[event[2]], rows[event[1]]
    result = []
    for mask in word['boundaries']['left_rows']:
        row = {}
        for i in range(n):
            if mask >> i & 1:
                xor(row, rows[i])
        result.append(row)
    L.need(result == [{term:1 << i} for i,term in enumerate(word['diagonal'])],
           'Complete controller endpoint on all binary monomials')
    return {'parent_inputs_per_port': n, 'physical_events': len(word['physical_events']),
            'full_calls': sum(e[0] == 'LOCAL' for e in word['physical_events']),
            'thin_calls': sum(e[0] == 'QUERY_SHEAR' for e in word['physical_events'])}


def invoice(word, paid, helpers):
    targets, children = Counter(), Counter()
    for event in word['physical_events']:
        if event[0] == 'LOCAL':
            targets.update(helpers)
            children.update(paid)
        elif event[0] == 'QUERY_SHEAR':
            children[1] += L.PORTS
        elif event[0] == 'IDLE':
            children[7*len(event[2])] += 2*L.PORTS
    for term in word['diagonal']:
        L.need(term & 1, 'Every main target retains its central direction')
        targets[1+7*(term >> 1).bit_count()] += L.PORTS
    return targets, children


def tail(E, T, P, tested, uniform):
    t, u, v, cutoff, floor = 1-tested, Q(1, 5), 1024, 17, 18
    target, paid = E.moment(T, t), E.moment(P, t)
    alpha = E.divide(paid, target)
    second = L.load('research/kappa-rebuild/architecture/mixed_target_probe.py', 'bit_relation_second_moments')
    tl, th = second.moment(T, tested)
    pl, ph = second.moment(P, tested)
    L.need(tl > ph and max(tl, target[0]) <= min(th, target[1])
           and max(pl, paid[0]) <= min(ph, paid[1]), 'Two exact moment engines agree')
    gamma = E.divide(E.moment(P, t+u), E.mul(E.power(cutoff, u), target))
    delta = E.divide((Q(sum(T.values())*floor),)*2, E.mul(E.power(cutoff, tested), target))
    reserve = Q(1, 250000)
    L.need(alpha[1] < 1-reserve and gamma[1] < Q(31, 32) and delta[1] < Q(19, 20),
           'All three charged compiler ratios')
    L.need(Q(31,32)**128 < Q(1,16) and Q(19,20)**128 < Q(1,16), 'Strict tail decay blocks')
    surplus = 1-Q(1)/(1+v*reserve)-Q(4, 2**32)
    L.need(surplus > 0 and cutoff**64 < floor**63 and max(T) < 256,
           'Completion, splitting and rounding surplus')
    h = Q(1,64)
    z, z0 = 1-uniform, (t+1-uniform)/2
    gap = z0-t
    B, debt = (5+8*h)*v, 1+8*v*(1-z0)
    x = (gap*B+debt)/(h*gap)
    H0 = -((-x.numerator)//x.denominator)
    x = H0*(1-z0)/(z-z0)
    H1 = x.numerator//x.denominator+1
    L.need(H0 >= 8*v and H0*h*gap >= gap*B+debt and (H0-1)*h*gap < gap*B+debt,
           'Exact first compiler threshold')
    L.need(H1*(z-z0) > H0*(1-z0) >= (H1-1)*(z-z0), 'Exact strict uniform threshold')
    return {'tested': tested, 'uniform': uniform, 'alpha': E.display(alpha),
            'gamma': E.display(gamma), 'delta': E.display(delta), 'reserve': reserve,
            'tensor_power': v, 'cutoff': cutoff, 'floor': floor,
            'normalized_surplus_lower': surplus, 'H0': H0, 'H1': H1,
            'uniform_N': '2^'+str(H1), 'winning_word_materialized': False}


def root(E, T, P):
    def margin(kappa):
        a, b = E.moment(T, 1-kappa), E.moment(P, 1-kappa)
        return a[0]-b[1], a[1]-b[0]
    lo, hi, grid = 0, 10**10, 10**12
    while hi-lo > 1:
        mid = (lo+hi)//2
        if margin(Q(mid,grid))[0] > 0:
            lo = mid
        else:
            hi = mid
    L.need(margin(Q(lo,grid))[0] > 0 > margin(Q(hi,grid))[1], 'Exact raw moment crossing')
    return [Q(lo,grid), Q(hi,grid)]


def run(local):
    word = json.loads((L.ROOT/'research/query-thinned-controllers/BIT-CONTROLLER.json').read_text())
    replay = controller(word)
    L.need((replay['full_calls'], replay['thin_calls']) == (18,15), 'All full and thin calls counted')
    T, P = invoice(word, local['paid'], local['helpers'])
    oldT, oldP = invoice(word, L.OLD_PAID, {8:439})
    old_invoice = word['invoice']
    L.need(oldT == Counter({int(k):v for k,v in old_invoice['targets'].items()})
           and oldP == Counter({int(k):v for k,v in old_invoice['paid'].items()}),
           'Independent reconstruction of the complete predecessor invoice')
    L.need(oldP-P == {1:162,7:162} and oldT-T == {8:162}, 'All eighteen local exchanges and target debits')
    difference = {r:(P[r]-T[r])-(oldP[r]-oldT[r]) for r in set(P)|set(T)|set(oldP)|set(oldT)}
    difference = {r:n for r,n in difference.items() if n}
    concave = {k:sum(n*min(r,k) for r,n in difference.items()) for k in sorted(difference)}
    L.need(all(v <= 0 for v in concave.values()) and min(concave.values()) < 0,
           'Exact uniform improvement for every strict concave rank power')
    E = L.load('research/higher-moment-strictification/verify.py', 'bit_relation_exact_moments')
    new_tail = tail(E, T, P, TESTED, UNIFORM)
    old_tail = tail(E, oldT, oldP, Q('.00346'), Q('.003459'))
    old_root, new_root = root(E, oldT, oldP), root(E, T, P)
    L.need(new_root[0] > old_root[1] and TESTED < new_root[0], 'Changed raw ceiling and compiler headroom')
    ordinary = (1-ATOM)*AFTER+ATOM*OLD_ORDINARY
    old_ordinary = (1-ATOM)*Q('.00345')+ATOM*OLD_ORDINARY
    L.need(UNIFORM-AFTER == Q('.003459')-Q('.00345') and 2**26 > 256/(UNIFORM-AFTER),
           'Same funded cover loss and finite prime rule')
    L.need(ATOM > ordinary > ADMITTED > old_ordinary and ATOM < 1-ordinary,
           'Strict ordinary BIT admission and stock')
    source_local_upper = 10**6
    source_scalar_events = 24305+2*9
    added_pointwise = local['scalar_events']-source_scalar_events
    L.need(added_pointwise == 1568, 'All added pointwise XOR and CLEAR records')
    local_bound = source_local_upper+added_pointwise
    boundary = word['boundaries']['boundary_unit_ADDs_per_port']
    raw_bound = 18*local_bound+15*111*16+32*111*(len(word['physical_events'])+boundary)
    L.need(raw_bound < 10**9, 'Retained source allowance plus every added record fits')
    def complete_census(targets, children):
        expected_targets, expected_paid = invoice(word, local['paid'], local['helpers'])
        L.need(targets == expected_targets and children == expected_paid, 'Every paid job and earned target must match the literal word')
    controls = {}
    try:
        complete_census(oldT, P)
    except ValueError as error:
        controls['missing_target_debit'] = str(error)
    else:
        raise ValueError('Accepted unearned helper targets')
    a, b = E.moment(oldT,1-TESTED), E.moment(oldP,1-TESTED)
    L.need(a[1] < b[0], 'The old complete bill fails at the new tested saving')
    controls['old_word_at_new_saving'] = 'Rejected by the exact raw moment'
    complex_receipt = json.loads((L.ROOT/'research/kappa-backward-controller-20261023/RESULT.json').read_text())['arithmetic']
    params = {k:Q(v) for k,v in complex_receipt['outer']['parameters'].items()}
    params['bit_saving'] = ADMITTED
    engine = L.load('research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py', 'bit_relation_complete_outer')
    outer = engine.ledger(params)
    outer['functional_checks']['actual_new_BIT_stock_sublinear'] = params['beta']*(1-ATOM)
    L.need(0 < params['beta']*(1-ATOM) < params['beta'] < 1,
           'The actual BIT row stock is sublinear in its active group')
    L.need(len(outer['strict_checks']) == 54 and len(outer['functional_checks']) == 4, 'All outer predicates are present')
    L.need(all(v > 0 for group in ('strict_checks','functional_checks') for v in outer[group].values()),
           'The complete unchanged multiplication endpoint still passes')
    L.need(params['kappa'] == Q('.00302728823'), 'No new multiplication kappa is claimed')
    return encode({'controller': replay, 'targets': T, 'paid': P,
                   'target_count': sum(T.values()), 'paid_count': sum(P.values()),
                   'rank_credit': sum(r*n for r,n in T.items()), 'rank_bill': sum(r*n for r,n in P.items()),
                   'signed_delta': difference, 'concave_order_certificate': concave,
                   'old_raw_root': old_root, 'new_raw_root': new_root,
                   'old_compiler': old_tail, 'new_compiler': new_tail,
                   'ordinary_BIT': {'old_ordinary':old_ordinary, 'new_ordinary':ordinary,
                                    'gain_at_matched_parameters':ordinary-old_ordinary,
                                    'admitted':ADMITTED, 'atom':ATOM, 'after_cover':AFTER,
                                    'prime_rule':'Odd q > 2^26*N^5, avoiding all fixed denominators and rank witnesses'},
                   'budgets':{'inherited_source_local_upper':source_local_upper,
                              'added_pointwise_records_per_call':added_pointwise,
                              'local_scalar':local['scalar_events'], 'local_complete_upper':local_bound,
                              'complete_raw_nonrecursive':raw_bound,'raw_allowance':10**9},
                   'negative_controls':controls, 'outer_at_unchanged_complex_endpoint':outer,
                   'complete_multiplication_kappa_improvement':False,
                   'binding_constraint':'The complex supplier remains below this BIT saving.'})
