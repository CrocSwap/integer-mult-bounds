"""Complete mixed-target price, compiler and outer transfer.

The interval and compiler bounds follow zxv and Cao Yifan. The productive
recursion is by Jacob Alan Sussman. The controller is by Cinna Davis.
Adapted from Ali Romman's PR5544/5545 for the two coupled contact changes.
Successor choices prepared for thu-nmrc with substantial OpenAI Codex assistance.
Ali Romman's complete caller/price proof and all predecessor credit are retained.
Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
import local as L

KAPPA, TESTED = Q('.00304153'), Q('.0030415305')
PREVIOUS = Q('.00304117')


def encode(x):
    if isinstance(x,Q):
        return str(x)
    if isinstance(x,dict):
        return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):
        return [encode(v) for v in x]
    return x


def assemble(local, native, word, physical):
    paid, targets = Counter(), Counter()
    counts = Counter()
    L.need(local['helpers'] == native['helpers'], 'Every productive helper has a native target')
    for e in word['physical_events']:
        counts[e[0]] += 1
        if e[0] == 'LOCAL':
            L.need(e[3] is False, 'Every source invocation is forward')
            paid.update(local['paid'])
            targets.update(local['helpers'])
        elif e[0] == 'QUERY_SHEAR':
            paid[1] += 104
        elif e[0] == 'IDLE':
            paid[8*len(e[2])] += 208
    main = Counter()
    idle = Counter({8*len(e[2]):0 for e in word['physical_events'] if e[0] == 'IDLE'})
    for e in word['physical_events']:
        if e[0] == 'IDLE':
            idle[8*len(e[2])] += 208
    L.need(idle == physical['whole_idle_jobs'], 'Every whole idle has a native Gaussian and full rank')
    for term in word['diagonal']:
        main[1+8*sum(term[1:])] += 104
    L.need(main == physical['main_targets'], 'Every main target has its full native phase')
    targets.update(main)
    L.need(counts['LOCAL'] == 18 and counts['QUERY_SHEAR'] == counts['IDLE'] == 15, 'Complete call census')
    # Recount by the two path lengths, without using emitted main diagonals.
    second_t = Counter({r:18*n for r,n in local['helpers'].items()})
    second_p = Counter({r:18*n for r,n in local['paid'].items()})
    second_t[145] += 208
    second_p[1] += 15*104
    for length in (7,8):
        for j in range(1,length+1):
            second_t[1+8*(j+1)] += 208
            second_p[8*(j+1)] += 208
    L.need((targets,paid) == (second_t,second_p), 'Independent full invoice')
    L.need(max(targets) == 145 and max(paid) == 72, 'Maximum recursive ranks')
    L.need(sum(targets.values()) == 12814 and sum(paid.values()) == 69912, 'Complete field and call counts')
    L.need(sum(r*n for r,n in targets.items())-sum(r*n for r,n in paid.items()) == 760, 'Complete rank surplus')
    return targets,paid,counts


def run(local,native,word,physical):
    T,P,counts = assemble(local,native,word,physical)
    E = L.load(L.ROOT/'research/higher-moment-strictification/verify.py','p104_productive_intervals')
    other = L.load(L.ROOT/'research/kappa-rebuild/architecture/mixed_target_probe.py','p104_productive_second_intervals')
    def margin(k):
        a,b = E.moment(T,1-k), E.moment(P,1-k)
        return a[0]-b[1],a[1]-b[0]
    lo,hi,grid = 0,10**12,10**14
    while hi-lo > 1:
        m=(lo+hi)//2
        if margin(Q(m,grid))[0] > 0:
            lo=m
        else:
            hi=m
    lower,upper = Q(lo,grid),Q(hi,grid)
    L.need(margin(lower)[0] > 0 and margin(upper)[1] < 0, 'Strict rational crossing enclosure')
    L.need(PREVIOUS < KAPPA < TESTED < lower and margin(PREVIOUS)[0] > 0, 'Changed complete bill improves selected kappa')
    t,u,v,c,b = 1-TESTED,Q(1,5),1024,17,18
    target,paid = E.moment(T,t),E.moment(P,t)
    tl,th = other.moment(T,TESTED)
    pl,ph = other.moment(P,TESTED)
    L.need(tl > ph and max(tl,target[0]) <= min(th,target[1]) and max(pl,paid[0]) <= min(ph,paid[1]), 'Two exact moment engines')
    alpha = E.divide(paid,target)
    gamma = E.divide(E.moment(P,t+u),E.mul(E.power(c,u),target))
    delta = E.divide((Q(sum(T.values())*b),)*2,E.mul(E.power(c,TESTED),target))
    reserve,decay = Q(1,10**10),Q(97,100)
    L.need(alpha[1] < 1-reserve and gamma[1] < decay and delta[1] < decay, 'All three charged tail ratios')
    L.need(decay**128 < Q(1,16), 'Both tail decay blocks')
    normalized = 1/(1+v*reserve)+Q(4,2**32)
    L.need(normalized < 1 and c**64 < b**63, 'Full completion, splitting and rounding charges')
    theta,power = Q(63,64),1000
    eta = E.scale(E.power(145,-v*TESTED),t)
    L.need(2*(c**v)**64 <= (145**v)**63 and eta[0] > theta**power, 'Shifted exits and complement capacity')
    L.need(E.power(145,v*TESTED)[1] < 2**power, 'Compiler initial range')
    gap = (TESTED-KAPPA)/7
    L.need(gap.numerator == 1, 'Exact compiler integer grid')
    step = gap.denominator
    def wins(j):
        return (step*j+1)**power < 2**j
    left,right=1,2
    while not wins(right):
        left,right=right,2*right
    while right-left > 1:
        m=(left+right)//2
        if wins(m):
            right=m
        else:
            left=m
    H=step*right
    L.need(H > 8*v and wins(right) and not wins(right-1), 'Finite uniform threshold with predecessor rejection')
    local_routes = (sum(local['paid'].values())+native['helper_normalizers']+native['main_adapters']+4*104+4*local['owned_lifetimes'])*1000
    L.need(local['real_scalar_allowance']+local_routes < 10**7, 'Every local scalar, route and owned operation is funded')
    boundary = sum(len(word['boundaries'][side+'_program']) for side in ('left','right'))
    raw = 18*10**7 + 15*1664 + 32*104*(len(word['physical_events'])+boundary)
    raw += 32*104*(26+1000)
    L.need(raw < 10**9, 'Complete nonrecursive raw bound')
    bit = L.read(L.ROOT/'research/query-thinned-controllers/RESULT.json')['ordinary_BIT']
    atom = Q(bit['atom'])
    ordinary=(1-atom)*Q(bit['after_cover'])+atom*Q('.0000384599')
    admitted=Q(bit['admitted'])
    L.need(atom > ordinary > admitted > TESTED and atom < 1-ordinary, 'Retained BIT admission and stock')
    outer_module=L.load(L.ROOT/'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py','p104_productive_outer')
    params={'kappa':KAPPA,'tested_saving':TESTED,'complex_uniform_saving':KAPPA+6*gap,
            'b':KAPPA+5*gap,'a':KAPPA+4*gap,'q':KAPPA+3*gap,'bit_saving':admitted,
            'epsilon':1-gap,'beta':1-3*gap,'r0':gap/10,'stop':gap,'layout':gap,'d':gap}
    outer=outer_module.ledger(params)
    outer['functional_checks']['actual_new_BIT_stock_sublinear']=params['beta']*(1-atom)
    L.need(len(outer['strict_checks']) == 54 and len(outer['functional_checks']) == 4, 'Complete outer predicate inventory')
    L.need(all(x > 0 for key in ('strict_checks','functional_checks') for x in outer[key].values()), 'All outer inequalities strict')
    wrong_cutoff = E.divide((Q(sum(T.values())*21),)*2,E.mul(E.power(20,TESTED),target))
    L.need(wrong_cutoff[0] > 1, 'Old cutoff fails with this helper inventory')
    bad=outer_module.ledger(dict(params,bit_saving=Q('.0027')))
    L.need(any(x <= 0 for x in bad['strict_checks'].values()), 'Insufficient BIT contract rejected')
    return encode({'kappa':KAPPA,'kappa_decimal':'.00304153','previous_open_pr5545':PREVIOUS,'gain':KAPPA-PREVIOUS,
                   'relative_gain_percent':100*(KAPPA/PREVIOUS-1),'raw_root_interval':[lower,upper],
                   'raw_headroom':[lower-KAPPA,upper-KAPPA],'margin_at_previous':E.display(margin(PREVIOUS)),
                   'targets':T,'paid':P,'productive_fields':sum(T.values()),'paid_calls':sum(P.values()),
                   'rank_mass_surplus':760,'full_forward_calls':18,'query_shears':15,'whole_idle_jobs':3120,
                   'strictification':{'tested':TESTED,'power':v,'cutoff':c,'floor':b,'tail_offset':u,'reserve':reserve,
                                     'alpha':E.display(alpha),'gamma':E.display(gamma),'delta':E.display(delta),'normalized_paid_upper':normalized},
                   'compiler':{'theta':theta,'logarithm_power':power,'eta':E.display(eta),'gap':gap,'H':H,'N':'2^'+str(H),
                               'integer_test_exponent':right,'uniform_saving':params['complex_uniform_saving'],'word_materialized':False},
                   'nonrecursive':{'local_scalar':local['real_scalar_allowance'],'local_routes':local_routes,
                                   'raw_scalar_upper':raw,'raw_budget':10**9,'peak_owned_fields':1,
                                   'fixed_scalar_growth_bound':'At most 2^(16*26000) before native factors; a declared constant, not an attained norm.',
                                   'tensor_native_growth_bound':'Each rank-r Gaussian has row l1 norm at most 2^(rf); sum of local ranks is 5894.'},
                   'ordinary_BIT':bit,'outer':outer,
                   'negative_controls':{'old_cutoff':'Rejected by completion-tail ratio greater than one','old_BIT':'Rejected by outer inequalities'}})
