# SPDX-License-Identifier: Apache-2.0
"""Certify the fixed-rank successor using only measured integer rank inventories."""
from decimal import Decimal
from fractions import Fraction as F
from functools import cache
from math import factorial

from interval import I

V = 768
H = 299_610_000_000_000
P = 23
SHIFT = 1300
TRIAL = F('0.003890115286593')
T = 1 - TRIAL
OLD_TRIAL = F('0.003890115276594')
OLD_CLAIM = F('0.00389011527141')
OLD_CAP = F('0.003890115271496')
COVER = F(1, H * 2**38)
CHILD = 210
ROOT = F('3.23')
DEPTH = 10
BINS = 32
SEED = F('.00385248')
TICK = F(1, 10**14)


def require(yes, name):
    if not yes:
        raise ValueError(name)


@cache
def ln(r):
    return I.point(r).ln()


@cache
def power(r, exponent):
    return (ln(r)*exponent).exp()


def real_power(log_r, exponent):
    return (log_r*exponent).exp()


def total(hist, exponent):
    return sum(count*power(rank, exponent) for rank, count in hist.items())


def positive_hist(raw):
    hist = {int(rank):int(count) for rank, count in raw.items()}
    require(len(hist)==len(raw) and all(str(k) in raw and k>0 and n==raw[str(k)] and n>0
                                      for k,n in hist.items()), 'positive rank histogram')
    return hist


def ceil_at(x, places):
    return F(-(-(F(x)*10**places)//1), 10**places)


def decimal(q, places):
    k = F(q)*10**places
    require(k.denominator==1 and 0<=k<10**places, 'fixed-point output grid')
    return f'0.{int(k):0{places}d}'


def four(covered, rational):
    previous = SEED
    stages = []
    for _ in range(4):
        bound = (249*covered+previous)/250
        admitted = F(((bound*10**15)//1)-1, 10**15)
        require(previous<admitted<bound<F(1,250)<1-bound, 'strict ordinary service stage')
        stages.append({'previous':str(previous), 'bound':str(bound), 'admitted':decimal(admitted,15),
                       'slack':str(min(bound-admitted, F(1,250)-admitted, 1-F(1,250)-admitted))})
        previous = admitted
    return previous, (min(previous,rational)//TICK-8)*TICK, stages


def strict_unit(paid, targets):
    z_paid, z_target = total(paid,T), total(targets,T)
    alpha = z_paid/z_target
    gamma = total(paid,T+F(1,5))/(power(15,F(1,5))*z_target)
    lost = power(16,F(1,5))*total(targets,T-F(1,5))/z_target
    require(all(0<z.lo<=z.hi<1 for z in (alpha,gamma,lost)), 'three directed separation ratios')
    invoice = alpha**V + 2*gamma**V + lost**V
    require(invoice.hi<1, 'strict completed paid plus discarded target bill')
    rho = gamma/alpha
    require(0<rho.lo<=rho.hi<1, 'positive split tail ratio')
    return z_paid,z_target,rho,{
        'alpha':alpha.bounds(),'gamma':gamma.bounds(),'discarded_target_ratio':lost.bounds(),
        'normalized_strict_gap':(I.point(1)-invoice).bounds(),
        'positive_split_uplift_upper':str((2*rho**V).hi),
    }


def average_law(hist, exponent):
    z = total(hist,exponent)
    atoms = [(ln(k)/ln(15), count*power(k,exponent)/z) for k,count in hist.items()]
    mean = sum(x*q for x,q in atoms)
    variance = (sum((x**2)*q for x,q in atoms)-mean**2)/V
    require(0<variance.lo, 'positive sample-mean variance')
    return mean,variance,z


def middle_child(paid, z_t, rho, j, tilted, left, right, low, upper):
    mean, var, z_alt = average_law(paid,tilted)
    # Take the difference with outward rounding before squaring.
    distance = min((mean-I.point(left)).lo,(I.point(right)-mean).lo)
    require(distance>0, 'tilted anchor contains its mean')
    anchor_alt = I.point(1)-var/(I.point(distance)**2)
    require(anchor_alt.lo>0, 'tilted anchor has positive mass')
    weight = T-tilted
    anchor = (z_alt/z_t)**V * real_power(j,weight*left) * anchor_alt
    raw_bad = real_power(j,weight*(low-left))/anchor_alt
    # Each R>J has full slabs of size J and at most one sub-J remainder.
    # For U<=J^upper<J, its eligible remainder contributes at most U^t/R^t.
    bad_split = rho**V * real_power(j,T*(upper-1))/anchor
    bad = raw_bad+bad_split
    require(bad.hi<Decimal('.01'), 'under-cut bad mass, including every eligible split remainder')
    return {'tilt':str(tilted),'anchor':[str(left),str(right)],'bad_cut':str(low),
            'upper_cut':str(upper),'mean':mean.bounds(),'variance':var.bounds(),
            'anchor_tilt_mass':anchor_alt.bounds(),'anchor_raw_lower':str(anchor.lo),
            'raw_bad_upper':str(raw_bad.hi),'split_bad_upper':str(bad_split.hi),'bad_upper':str(bad.hi)}


def child_capacity(paid,z,rho,j,k):
    low = real_power(k-j*F('0.35'),TRIAL)
    a = middle_child(paid,z,rho,j,F('.45'),F('.28'),F('.35'),F('.24'),F('.59'))
    b = middle_child(paid,z,rho,j,F('.8'),F('.49'),F('.59'),F('.47'),F('.82'))
    require((low*F(99,100)).lo>CHILD, 'small and middle cutoff capacity')
    # On eligible raw ranks use exponent t+C=1 in the numerator. Exact one-letter
    # rank mass and a fresh positive tilt pay the whole high tail.
    z1 = sum(r*n for r,n in paid.items())
    tail = (total(paid,F('1.1'))/(power(15,F('.082'))*z1))**V
    hight = (I.point(z1)/z)**V * (I.point(1)-tail)/(I.point(1)+2*rho**V)
    require(hight.lo>CHILD, 'large cutoff capacity with the full split denominator')
    return {'factor':CHILD,'small_cut_factor':low.bounds(),'middle_cut_factors':[a,b],
            'upper_rank_mass_tail':tail.bounds(),'large_cut_factor':hight.bounds()}


def convolve(a,b):
    return [sum(a[i]*b[d-i] for i in range(d+1)) for d in range(len(a))]


def poly_power(poly,n):
    result = [I.point(1)]+[I.point(0)]*(len(poly)-1)
    while n:
        if n&1:
            result=convolve(result,poly)
        n//=2
        if n:
            poly=convolve(poly,poly)
    return result


def derivative_coefficients(poly,n):
    # If B=A^n and A(0)=1, A B'=n B A'. Here n=768>P, so
    # all coefficients of this independent recurrence are nonnegative.
    require(len(poly)<=n, 'positive derivative certificate')
    out = [I.point(1)]
    for d in range(1,len(poly)):
        out.append(sum(poly[i]*out[d-i]*((n+1)*i-d) for i in range(1,d+1))/d)
    return out


def paid_norms(paid,z,rho,j):
    x = [ln(r)/j for r in paid]
    weights = [n*power(r,T)/z for r,n in paid.items()]
    letters = [I.point(1)]+[sum(w*xi**a for w,xi in zip(weights,x,strict=True))/factorial(a)
                           for a in range(1,P+1)]
    raw = poly_power(letters,V)
    other = derivative_coefficients(letters,V)
    require(all(max(a.lo,b.lo)<=min(a.hi,b.hi) for a,b in zip(raw,other,strict=True)),
            'independent raw moment evaluations overlap at every degree')
    eps = 2*rho**V
    completed = [I.point(1)]+[I.point(min(a.hi,b.hi)) + I.point(eps.hi)/factorial(i)
                            for i,(a,b) in enumerate(zip(raw[1:],other[1:],strict=True),1)]
    bounds, exact, iterated = [], [], [I.point(1)]+[I.point(0)]*P
    for q in range(1,DEPTH+2):
        iterated = convolve(iterated,completed)
        doubled = poly_power(completed,q)
        a,b = iterated[P],doubled[P]
        require(max(a.lo,b.lo)<=min(a.hi,b.hi), 'independent completed moment powering agrees')
        moment = I.point(min(a.hi,b.hi)) * F(factorial(P),q**P)
        norm = ceil_at((moment.ln()*F(1,P)).exp().hi,8)
        require(F(moment.hi)<norm**P, 'outward-padded Lp bound')
        exact.append(str(moment.hi)); bounds.append(norm)
    return bounds, {'raw_23_convolution':raw[P].bounds(),'raw_23_derivative':other[P].bounds(),
                    'completed_average_moment_upper':exact,'norm_uppers':[str(x) for x in bounds]}


def flow_bounds(paid,targets,z_p,z_t,rho,j,k,m):
    child = child_capacity(paid,z_p,rho,j,k)
    root_unit = ((I.point(sum(r*n for r,n in targets.items()))/z_t)/power(16,TRIAL))**V
    require(root_unit.lo>I.point(ROOT).hi, 'completed target mass improves root complements')
    ratio = (z_t/z_p)**V
    u = F(1,100)
    decay = (power(16,u)*total(targets,T-u)/z_t)**V
    require((ratio*decay).hi<1, 'root-source fraction bound decreases with successive heights')
    h = ln(2)*SHIFT
    eta = real_power(m,-TRIAL)*T
    a, b, beta = h/j,(h+m)/j,k/j
    norms, moment = paid_norms(paid,z_p,rho,j)
    worst = (F(0), None)

    def root_fraction(g,f):
        return min(Decimal(1), (ratio**(g+1)*decay**g*real_power(k,u*f)).hi)

    def budget(g,lower,upper):
        cost = ((a+norms[g]*(g+1))/(b+beta*(g+lower)))**P
        root = real_power(k,TRIAL*(1-upper))*ROOT
        if g==0:
            available = root
        else:
            # S>=E and S_root/S<=min(1,S_root/E). If the root bound is better
            # than the child bound, ignore this extra root credit.
            discount = max(Decimal(0),(I.point(CHILD)-root).hi)
            available = I.point(CHILD)-I.point(root_fraction(g,upper))*discount
        total_capacity = eta*available
        return cost,total_capacity

    for g in range(DEPTH):
        for cell in range(BINS):
            lower,upper=F(cell,BINS),F(cell+1,BINS)
            cost,capacity=budget(g,lower,upper)
            require(cost.hi<capacity.lo, f'finite source capacity cell {g}/{cell}')
            ratio_hi=F((cost/capacity).hi)
            if ratio_hi>worst[0]:
                worst=ratio_hi, [g,cell,str(cost.hi),str(capacity.lo)]
    root_tail = root_fraction(DEPTH,F(1))
    large_capacity = eta*(I.point(CHILD)-I.point(root_tail)*(I.point(CHILD)-ROOT))
    at_depth = ((a+norms[-1]*(DEPTH+1))/(b+beta*DEPTH))**P
    limit = (I.point(norms[-1])/beta)**P
    require(max(at_depth.hi,limit.hi)<large_capacity.lo, 'all larger heights by decreasing root mass and affine endpoint bound')
    require(limit.lo>eta.hi, 'uniform per-source-capacity negative control at infinite height')
    require(((I.point(1)+m/h)**P).lo>real_power(m,TRIAL).hi, 'all ordinary base ranks by logarithm concavity')
    return {'root_factor':root_unit.bounds(),'root_ray_ratio':ratio.bounds(),'root_tail_factor':decay.bounds(),
            'root_fraction_from_height_10_upper':str(root_tail),'eta':eta.bounds(),
            'finite_shape_cells':DEPTH*BINS,'worst_finite_cell':worst[1],
            'worst_finite_margin_ratio_upper':str(ceil_at(worst[0],10)),
            'tail_capacity_lower':str(large_capacity.lo),'tail_height_10_upper':str(at_depth.hi),
            'tail_infinite_upper':str(limit.hi),'child':child,'moments':moment}


def certify(paid_json,targets_json,binary_raw,rational_raw):
    paid,targets=positive_hist(paid_json),positive_hist(targets_json)
    require(sum(paid.values())==104904 and sum(targets.values())==18906 and max(paid)==56 and max(targets)==127,
            'complete literal paired inventories')
    require(8**512*64**256==16**V and targets[8]>0 and targets[64]>0, 'attained retained productive floor')
    require(tuple(map(F,binary_raw))==(F('.003890115286594'),F('.003890115286595')) and TRIAL<F(binary_raw[0]),
            'directed crossing pins and strict trial')
    z_p,z_t,rho,strict = strict_unit(paid,targets)
    flow = flow_bounds(paid,targets,z_p,z_t,rho,ln(15)*V,ln(16)*V,ln(134)*V)
    numerator,denominator=(H+SHIFT)**P,SHIFT**P
    debit=(numerator//denominator).bit_length()
    require(denominator*2**(debit-1)<=numerator<denominator*2**debit and debit*(H+SHIFT)>2*H*P,
            'adjacent terminal and derivative tail controls')
    covered=TRIAL-F(debit,H)-COVER
    cap,claim,rows=four(covered,F(rational_raw[0]))
    old_cap,old_claim,_=four(OLD_TRIAL-F(1524,H)-COVER,F(rational_raw[0]))
    require(old_cap==OLD_CAP and old_claim==OLD_CLAIM, 'complete #8029 fixed predecessor price')
    shape_upper=F(binary_raw[1])-F(1524,H)
    require(OLD_CLAIM<shape_upper<claim<claim+7*TICK<cap<F(rational_raw[0]), 'strict full gain above generous predecessor shape upper')
    return {'trial':str(TRIAL),'C':decimal(TRIAL,15),'h':SHIFT,'p':P,'H':H,'v':V,
            'same_cover_debit':str(COVER),'terminal_debit_numerator':debit,
            'covered':str(covered),'cap':decimal(cap,15),'claim':decimal(claim,14),
            'tested':decimal(claim+7*TICK,14),'stages':rows,'strict':strict,'flow':flow,
            'raw_crossings':{'BIT':binary_raw,'rational':rational_raw},
            'predecessor_claim':decimal(OLD_CLAIM,14),'predecessor_shape_upper':str(shape_upper),
            'absolute_gain':str(claim-OLD_CLAIM),'percent_gain':str(100*(claim-OLD_CLAIM)/OLD_CLAIM),
            'strict_separation':str(claim-shape_upper),'distance_to_raw_BIT_upper':str(F(binary_raw[1])-claim)}
