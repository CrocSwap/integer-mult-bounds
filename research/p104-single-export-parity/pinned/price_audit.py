#!/usr/bin/env python3
"""Exact arithmetic screen for a hypothetical paid histogram, not a circuit rewrite.

Run: python3 -B price_audit.py [receipt.json]
Uses only the Python standard library. The two adjacent compressed inputs are
pinned #8027 / inherited caller source bytes. The 48-call positive inventory is
from #8035's reconstructed physical word, and can be cross-checked using the
separate source_binding.py against the #8035 extracted package.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from math import isqrt
from pathlib import Path
import gzip, json, sys

ROOT = Path(__file__).resolve().parent
UNIT = 1 << 192
BITS = 184
K = Q('0.00389046')
G = Q(1, 10**17)
ORDINARY = Q('0.00389046000001')
ETA = Q(39, 10000)
RANK_LOGS = (106811524, 1708984375, 27343750000, 437500000000,
             7000000000000, 112000000000000)
M_LOG = 1600000
Z = Q(593, 2048)
W = Q(491, 1024)
WEIGHT = Q(1, 64)
POS_C = Q(2043, 524288)


def ceil_div(a, b):
    return -(-a // b)


def ceil_frac(x):
    return ceil_div(x.numerator, x.denominator)


def floor_frac(x):
    return x.numerator // x.denominator


def enclosing_text(lo, hi, digits=18):
    """Return outward decimal endpoints, each with exactly `digits` places."""
    s = 10**digits
    a, b = floor_frac(lo*s), ceil_frac(hi*s)
    def form(n):
        sign = '-' if n < 0 else ''
        n = abs(n)
        return f'{sign}{n//s}.{n%s:0{digits}d}'
    return [form(a), form(b)]


def load_inputs():
    gp = ROOT/'strong-bit.json.gz'; cp = ROOT/'EFREE-CALLER.json.gz'
    gd, cd = gp.read_bytes(), cp.read_bytes()
    assert sha256(gd).hexdigest() == '74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
    assert sha256(cd).hexdigest() == '757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b'
    graph, caller = json.loads(gzip.decompress(gd)), json.loads(gzip.decompress(cd))
    dims = {int(k): v['dim'] for k,v in graph['frames'].items()}
    ports = caller['ports']
    local = sum(r[0]=='LOCAL' for r in caller['events'])
    assert (ports, local, caller['body_rank']) == (111,36,7)
    targets, paid = Counter(), Counter()
    for row in caller['diagonal']:
        targets[1 + caller['body_rank'] * len(row['stages'])] += ports
    for src, dst in zip(graph['start'][2*ports:], graph['final'][2*ports:], strict=True):
        targets[abs(dims[dst] - dims[src])] += local
    for row in graph['program']:
        if row[0] == 'MOVE': paid[abs(dims[row[3]] - dims[row[2]])] += local
    for row in caller['events']:
        if row[0] == 'QUERY': paid[1] += ports
        elif row[0] == 'IDLE_ONE': paid[len(row[2])*caller['body_rank']] += ports
    assert dict(sorted(targets.items())) == BIT_TARGET
    assert dict(sorted(paid.items())) == BIT_PAID
    assert sum(targets.values()) == 18906 and sum(paid.values()) == 104904
    assert sum(k*v for k,v in paid.items()) == 285600
    return targets, paid


BIT_TARGET = {4:612,8:14520,15:444,22:444,29:444,36:444,43:444,50:444,57:444,64:444,127:222}
BIT_PAID = {1:48972,2:44892,3:1980,4:1512,5:1044,6:2916,7:480,14:444,21:444,
            28:444,35:444,42:444,49:444,56:444}
# Reconstructed from #8035's changed positive graph and caller, not the old grade-14 word.
POS_TARGET = {1:1008,2:432,3:480,4:11568,5:1584,6:48,7:672,8:1584,9:25872,
              17:1248,25:1248,33:1248,41:1248,49:1248,57:1248,65:1248,129:624}
POS_PAID = {1:183312,2:38016,3:23040,4:10848,5:15072,6:1968,7:480,8:1344,
            16:1248,24:1248,32:1248,40:1248,48:1248,56:1248}


@lru_cache(None)
def power_bound(rank, exponent):
    """Prove lo/UNIT <= rank**exponent <= hi/UNIT for rational exponent >= 0.

    Each iterative square root is rounded outward. After BITS bits, one
    additional copy of the last root encloses any nonzero fractional tail.
    """
    assert rank > 0 and exponent >= 0
    n, rem_n = divmod(exponent.numerator, exponent.denominator)
    den = exponent.denominator
    lo = hi = rank**n * UNIT
    root_lo = root_hi = rank * UNIT
    for _ in range(BITS):
        root_lo = isqrt(root_lo * UNIT)
        z = root_hi * UNIT
        root_hi = isqrt(z)
        if root_hi * root_hi < z: root_hi += 1
        rem_n *= 2
        if rem_n >= den:
            rem_n -= den
            lo = lo * root_lo // UNIT
            hi = ceil_div(hi * root_hi, UNIT)
    if rem_n: hi = ceil_div(hi * root_hi, UNIT)
    return lo, hi


def moment(hist, exponent):
    lo = hi = 0
    for rank, count in hist.items():
        a,b = power_bound(rank,exponent)
        lo += count*a; hi += count*b
    return lo,hi


def raw_difference(targets, paid, c):
    tl,th=moment(targets,1-c); pl,ph=moment(paid,1-c)
    return Q(tl-ph,UNIT),Q(th-pl,UNIT)


def changed(paid, m):
    assert isinstance(m,int) and 0 <= m <= paid[1]//2
    p = paid.copy(); p[1] -= 2*m; p[2] += m
    assert sum(r*n for r,n in p.items()) == 285600
    assert sum(p.values()) == 104904-m
    return p


def powered_surplus(targets, paid, c, v, z, w, weight, keep):
    t=1-c
    tl,th=moment(targets,t); pl,ph=moment(paid,t)
    gl,gh=moment(paid,t+z); p12lo,p12hi=power_bound(12,z)
    ol,oh=moment(targets,t-w); klo,khi=power_bound(keep,w)
    alo,ahi=Q(pl,th),Q(ph,tl)
    gamlo,gamhi=Q(gl*UNIT,th*p12hi),Q(gh*UNIT,tl*p12lo)
    lamlo,lamhi=Q(ol*klo,th*UNIT),Q(oh*khi,tl*UNIT)
    lo = 1-ahi**v-weight*gamhi**v-lamhi**v
    hi = 1-alo**v-weight*gamlo**v-lamlo**v
    assert lo<=hi
    return lo,hi


def crossing(targets, paid):
    """Directed 1e-26 bracket; monotonicity is proved in README."""
    s=10**26; center=floor_frac(K*s)
    lo,hi=center-10**19,center+10**19
    assert raw_difference(targets,paid,Q(lo,s))[0] > 0
    assert raw_difference(targets,paid,Q(hi,s))[1] < 0
    while hi-lo>1:
        mid=(lo+hi)//2
        a,b=raw_difference(targets,paid,Q(mid,s))
        assert a>0 or b<0, 'directed grid too coarse to decide a bisection point'
        if a>0: lo=mid
        else: hi=mid
    return enclosing_text(Q(lo,s),Q(hi,s),26)


def bit_debit(v, floor, c):
    scale=4*(134*127)**v*floor
    assert Q(1024*floor,15*(floor-2)) < 69 and 69**100 < 2**611
    return ceil_frac(Q(611,100)+c*(scale-1).bit_length())


def positive_debit():
    floor=1<<15; v=128
    assert 32*floor*4 < 9*15*(floor-2) and 9**4 < 2**5*4**4
    scale=4*(153*129)**v*floor
    return ceil_frac(Q(5,4)+POS_C*(scale-1).bit_length()+1)


def stage_prices(c, d):
    prev=Q(0); result=[]
    for i,h in enumerate(RANK_LOGS):
        covered=c-Q(d,h)
        limit=min((249*covered+prev)/250,ETA)
        rate=ORDINARY if i==len(RANK_LOGS)-1 else Q(floor_frac(limit*10**18)-1,10**18)
        assert prev<rate<limit
        result.append((h,covered,limit,rate))
        prev=rate
    return result


def signed_margins(k,g,ordinary,positive):
    # Self-contained transcription of #8035 outer_budget.py's 54+4 gates.
    a,b,q=k+4*g,k+5*g,k+3*g
    ep,be=1-g,1-3*g
    r0=g/10
    sigma,tau=1-b,1-a
    internal=tau+(1-g)*max(sigma-tau,0)
    leaf=sigma+g*(1-sigma)
    lam=1-(q+a)/2
    xi=ep*(1+q)-Q(3,32)+g
    key=be+1-ep
    powers=[ep*q,a,1-ep+q*be,1-ep+a*be,1-ep+be,Q(3,32)+xi-ep,
            xi+Q(1,2)-ep,ep,1-(ep+be+48-128+2)]
    strict=[ordinary-a,b-a,q,b-q,a-q,g,1-g,(1-g)*b-a,1-internal-q,1-leaf-q,
            lam-tau,lam-sigma,lam-internal,1-q-lam,1-q-leaf,ep,1-ep,xi-Q(1,2),ep-xi,
            be,ep-be,1-be,1-(2*xi-2)-r0-be,1-(2*xi-2)-be,1-ep-r0,1-ep,r0,1-key,
            1-be-2*(1-ep),128-48-be,g,ep-a,Q(1,32)-b,Q(2**45-7**16),Q(2),2-xi,
            Q(5),1-be,1-be,1-ep,powers[2]-powers[0],g,k-Q('.001730970419199163702738'),
            1-ep,Q(11,2)]+[x-k for x in powers]
    functional=[1-be,be*(1-Q(3,1000)),128-48-ep-be-1,be*(1-Q(1,250))]
    assert len(strict)==54 and len(functional)==4
    return strict,functional,positive-b


def power_and_enumeration_checks(v, L, c, paid_count):
    assert 0<c<Q(1,250) and c<=Z<=1
    assert Q(101,100)**250>2 and Q(101,100)*c/Z<WEIGHT
    assert 18906**v+paid_count**v+23800**v < 2**(18*v)
    assert 5**13>16*4**13 and 15**v>=2*12**v
    assert 512*v <= min(RANK_LOGS)
    assert 2**64*(v+1)*2**(28*v)<2**(512*v)
    assert 872*(Q(13,4)+Q(2,512))*(512*v)<2**(512*v)
    assert L>2


def main():
    targets,paid=load_inputs()
    # Round c upward from a readable decimal to the 2^-56 grid.
    c = Q(ceil_frac(Q('0.00389046000025')*2**56),2**56)
    assert K < ORDINARY < c < ETA
    m0=raw_difference(targets,paid,K)
    p2lo,p2hi=power_bound(2,1-K)
    delta_lo,delta_hi=2-Q(p2hi,UNIT),2-Q(p2lo,UNIT)
    assert m0[1]<0 and 0<delta_lo<=delta_hi
    threshold=((-m0[1])/delta_hi,(-m0[0])/delta_lo)
    assert 24 < threshold[0] <= threshold[1] < 25
    for m in (24,25):
        a,b=raw_difference(targets,changed(paid,m),K)
        assert (b<0 if m==24 else a>0)

    assert bit_debit(268,1<<50,c)==21 and positive_debit()==10
    stages=stage_prices(c,21)
    positive=POS_C-Q(10,M_LOG)
    assert 0<G<=Q(1,10**14) and ORDINARY>K+4*G and positive>K+5*G
    strict,functional,pay=signed_margins(K,G,ORDINARY,positive)
    assert min(*strict,*functional,pay)>0
    assert min(*signed_margins(K,G,K+4*G,positive)[0])==0
    assert signed_margins(K,G,ORDINARY,K+5*G)[2]==0
    assert min(*signed_margins(K,Q(0),ORDINARY,positive)[0])==0
    power_and_enumeration_checks(268,1<<50,c,104904-25)
    out={
      'interpretation':'m replacements of two separate rank-one paid occurrences by one rank-two paid occurrence within the whole 36-call raw word; no physical realization asserted',
      'sources':{'paired_pr_8027_head':'fb9b6a7b0d27da1cf98430893a3016bf811e2aa4',
                 'profile_pr_8035_head':'ea776471bf8ed143a0625cf2d7532f65d15eb5f9',
                 'graph_sha256':'74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326',
                 'caller_sha256':'757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b'},
      'kappa':str(K), 'bit_c_fraction':str(c), 'bit_c_decimal_bounds':enclosing_text(c,c,20),
      'ordinary_rate':str(ORDINARY), 'signed_gap':str(G), 'eta':str(ETA),
      'positive_paid_cap':str(positive), 'positive_paid_cap_decimal_bounds':enclosing_text(positive,positive,20),
      'ordinary_margin':str(ORDINARY-K-4*G), 'positive_margin':str(pay),
      'bit_debit':21,'positive_debit':10,'rank_logs':RANK_LOGS,'ordinary_stage_rates':[str(x[3]) for x in stages],
      'sixth_stage_headroom':str(stages[-1][2]-ORDINARY),
      'signed_gates':{'strict':len(strict),'functional':len(functional),'minimum_margin':str(min(*strict,*functional,pay)),
                      'controls':'equality at either supplier gate and g=0 each fail'},
      'raw_minimum_real_replacements_at_target_bounds':enclosing_text(*threshold,14),
      'raw_difference_at_target_bounds':{}, 'raw_crossing_bounds':{},
      'powered_268_surplus_bounds':{},
    }
    for m in (24,25,26,27,36):
        p=changed(paid,m)
        d=raw_difference(targets,p,K)
        su=powered_surplus(targets,p,c,268,Z,W,WEIGHT,15)
        out['raw_difference_at_target_bounds'][str(m)]=enclosing_text(*d,16)
        out['powered_268_surplus_bounds'][str(m)]=enclosing_text(*su,18)
        if m==24: assert su[1] < 0
        else: assert su[0] > Q(2,1<<50)
    # Although a replacement increases the tilted split moment, certify that
    # the full powered bound decreases throughout the real interval [0, 36].
    # The base debit decreases and the split debit increases with m; bounding
    # both derivative magnitudes at m=36 proves the net derivative negative.
    t=1-c; target_lo,target_hi=moment(targets,t)
    end=changed(paid,36)
    pl,_=moment(end,t); _,ph_tilt=moment(end,t+Z)
    p2tlo,p2thi=power_bound(2,t)
    p2zlo,p2zhi=power_bound(2,t+Z)
    p12lo,_=power_bound(12,Z)
    assert p2thi<2*UNIT and p2zlo>2*UNIT
    alpha_end_lo=Q(pl,target_hi)
    gamma_end_hi=Q(ph_tilt*UNIT,target_lo*p12lo)
    base_saving_lo=Q(2*UNIT-p2thi,target_hi)
    tilt_surcharge_hi=Q((p2zhi-2*UNIT)*UNIT,target_lo*p12lo)
    assert base_saving_lo*alpha_end_lo**267 > WEIGHT*tilt_surcharge_hi*gamma_end_hi**267
    out['powered_268_certificate_strictly_decreases_on_m_0_to_36']=True
    out['raw_crossing_bounds']={str(m):crossing(targets,changed(paid,m)) for m in (24,25)}
    # At most 36 such substitutions cannot absorb even one additional rank-one
    # occurrence. This control applies to the whole 36-call raw word.
    extra=changed(paid,36); extra[1]+=1
    extra_bound=raw_difference(targets,extra,K)
    assert extra_bound[1] < 0
    out['m36_plus_one_rank_one_raw_difference_at_target_bounds']=enclosing_text(*extra_bound,16)
    pos_su=powered_surplus(POS_TARGET,POS_PAID,POS_C,128,Q(19,64),Q(23,64),Q(2),16)
    assert pos_su[0] > Q(2,1<<15)
    out['positive_128_surplus_bounds']=enclosing_text(*pos_su,15)

    # Arithmetic-only smaller power: this is not enabled in #8035's runtime.
    small=powered_surplus(targets,changed(paid,25),c,132,Z,W,WEIGHT,15)
    assert small[0] > Q(2,1<<25) and bit_debit(132,1<<25,c)==14
    smallstages=stage_prices(c,14)
    power_and_enumeration_checks(132,1<<25,c,104904-25)
    out['exploratory_power_132']={'floor':str(1<<25),'bit_debit':14,
        'surplus_bounds':enclosing_text(*small,18),
        'sixth_stage_headroom':str(smallstages[-1][2]-ORDINARY),
        'status':'arithmetic screen only; power 132 needs new runtime/physical/stock and supplier transfer proof'}
    assert powered_surplus(targets,changed(paid,25),c,131,Z,W,WEIGHT,15)[1] < 0
    rendered=json.dumps(out,indent=2,sort_keys=True)+'\n'
    if len(sys.argv)==2: Path(sys.argv[1]).write_text(rendered)
    else: print(rendered,end='')
    print('PASS_HYPOTHETICAL_PRICE_BOUNDARY_24_25; NO_REWRITE_OR_THEOREM_CLAIMED')

if __name__=='__main__': main()
