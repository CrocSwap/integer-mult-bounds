#!/usr/bin/env python3
"""Exact optimistic arithmetic only for a released, unrealized T/P invoice.

No native/physical/compiler/Lean code is imported. Standard-library rational
logarithm and alternating-exponential enclosures. Substantial OpenAI assistance.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
STOCK=HERE.parents[1]/'coded-port-adapter-ceiling-20261023/outputs/released-operator-inventory-20261023'
A,B=Q('0.0030217758'),Q('0.00339999')
H={4:28,7:7,8:47,9:326}
P0={1:2201,2:412,3:510,4:127,5:40}
T={9:816,17:224}
P={1:4608,2:838,3:1020,4:254,5:136}

def need(ok,message):
    if not ok:raise ValueError(message)

def rounded(a,b,grid=10**40):
    return Q((a*grid).__floor__(),grid),Q((b*grid).__ceil__(),grid)

def logsmall(z):
    need(0<=z<=Q(1,3),'reduced logarithm range')
    n=40
    lower=sum((2*z**(2*j+1)/(2*j+1) for j in range(n)),Q(0))
    tail=2*z**(2*n+1)/((2*n+1)*(1-z*z))
    return lower,lower+tail

def logint(r):
    need(isinstance(r,int) and r>=1,'positive integer rank')
    k=r.bit_length()-1;x=Q(r,2**k)
    a,b=logsmall((x-1)/(x+1));c,d=logsmall(Q(1,3))
    return rounded(a+k*c,b+k*d,10**50)

def alternating(x,n):
    need(0<=x<Q(1,50),'negative exponential range')
    term=total=Q(1)
    for j in range(1,n+1):
        term*=-x/j;total+=term
    return total

def power(r,c):
    need(A<=c<=B,'declared comparison interval only')
    lo,hi=logint(r)
    return rounded(r*alternating(c*hi,17),r*alternating(c*lo,18))

def moment(hist,c,log_weight=False):
    lower=upper=Q(0)
    for r,n in hist.items():
        lo,hi=power(r,c)
        if log_weight:
            a,b=logint(r);lo*=a;hi*=b
        lower+=n*lo;upper+=n*hi
    return lower,upper

def margin(c):
    tl,tu=moment(T,c);pl,pu=moment(P,c)
    return tl-pu,tu-pl

def enc(interval):
    lo,hi=interval;scale=10**24
    def fmt(n):
        return ('-' if n<0 else '')+str(abs(n)//scale)+'.'+str(abs(n)%scale).zfill(24)
    return {'exact_lower':str(lo),'exact_upper':str(hi),
            'lower_decimal':fmt((lo*scale).__floor__()),
            'upper_decimal':fmt((hi*scale).__ceil__())}

def audit(targets,paid):
    # One completed return for each original arbitrary owner, never two.
    need(sum(targets.values())==224+2*sum(H.values()),'1040 original productive owners exactly once')
    need(targets==T,'all 816 helper owners complete once to H9; main224H17')
    complements=Counter()
    for r,n in H.items():
        if r<9:complements[9-r]+=2*n
    need(dict(complements)=={5:56,2:14,1:94},'helper complement ranks and multiplicities')
    expected=Counter({1:112})
    for r,n in P0.items():expected[r]+=2*n
    expected.update(complements)
    need(paid==dict(expected),'two FULLs, one112-query bank and all helper complements paid')
    need(sum(r*n for r,n in targets.items())==11152,'target rank mass')
    need(sum(r*n for r,n in paid.items())==11040,'paid rank mass')
    return dict(complements)

def authenticate():
    files=json.loads((STOCK/'FILES.json').read_text());out=[]
    for name,digest in files.items():
        path=STOCK/name
        need(not path.is_symlink() and sha256(path.read_bytes()).hexdigest()==digest,'frozen stock source '+name)
        out.append({'path':str(path.relative_to(HERE.parents[1])),'sha256':digest})
    release=json.loads((STOCK/'source/RELEASE-MONITOR.json').read_text())
    invoice=release['conditional_inventory']
    need({int(r):n for r,n in invoice['T'].items()}==T,'released target census')
    need({int(r):n for r,n in invoice['P'].items()}==P,'released paid census')
    return release,out

def run():
    release,sources=authenticate();complements=audit(T,P)
    ma,mb=margin(A),margin(B)
    # M'(C)=P_log(C)-T_log(C). Each log-weighted positive sum decreases.
    pla,pua=moment(P,A,True);plb,pub=moment(P,B,True)
    tla,tua=moment(T,A,True);tlb,tub=moment(T,B,True)
    derivative=(plb-tua,pua-tlb)
    need(derivative[1]<0,'strictly decreasing M throughout declared interval')
    need(Q(44)<mb[0]<=mb[1]<Q(45),'endpoint margin strictly between44 and45')
    need(ma[1]<112,'one additional full112-query bank fails everywhere')
    # Min M occurs at B. n H1 subtracts exactly n at every C.
    need(mb[0]-44>0 and mb[1]-45<0,'44 succeeds uniformly;45 fails at B')
    mutants={
      'omit_one_helper':(dict(T)|{9:815},dict(P)),
      'omit_original112_queries':(dict(T),dict(P)|{1:P[1]-112}),
      'omit_paid_helper_complements':(dict(T),{r:n-complements.get(r,0) for r,n in P.items()}),
      'doublecredit_original_helpers_after_completion':(dict(Counter(T)+Counter({r:2*n for r,n in H.items()})),dict(P)),
      'credit_owned112_query_fields_as_inputs':(dict(Counter(T)+Counter({1:112})),dict(P)),
    }
    controls={}
    for name,(tt,pp) in mutants.items():
        try:audit(tt,pp)
        except ValueError as error:controls[name]={'rejected':True,'reason':str(error)}
        else:raise ValueError('accepted invalid stock/control '+name)
    return {'status':'PASS_OPTIMISTIC_UNREALIZED_INVOICE_ARITHMETIC_ONLY',
      'comparison_interval':[str(A),str(B)],'targets':T,'paid':P,
      'native_helper_profile_per_FULL':H,'native_paid_profile_per_FULL':P0,
      'helper_count_once':816,'main_count':224,'total_independent_owner_count':1040,
      'helper_complement_paid':complements,'original_query_H1':112,
      'target_rank_mass':11152,'paid_rank_mass':11040,'rank_mass_surplus':112,
      'point_margins':{str(A):enc(ma),str(B):enc(mb)},
      'uniform_derivative_enclosure':enc(derivative),
      'uniform_margin_enclosure':enc((mb[0],ma[1])),
      'max_uniform_integer_extra_H1':44,
      'uniform_margin_after44_H1':enc((mb[0]-44,ma[1]-44)),
      'endpoint_margin_after45_H1':enc((mb[0]-45,mb[1]-45)),
      'uniform_margin_after_an_extra112_H1':enc((mb[0]-112,ma[1]-112)),
      'safe_sufficient_extra_profile_rule':'For a finite nonnegative extra paid profile, sum_r extra_r*r^(1-A)<=44 implies positive raw moment residual on [A,B] under unchanged realized T/P; not actual funding or compiler reserve.',
      'integer_budget_claim':'44 is maximal for strict raw moment positivity uniformly on the declared closed interval, conditional on this unrealized complete T/P and unchanged target credit.',
      'controls':controls,'release_url':release['url'],'scientific_source_pin':release['source_scientific_pin'],
      'source_inventory_files':sources,
      'source_inventory_manifest_sha256':sha256((STOCK/'FILES.json').read_bytes()).hexdigest(),
      'checker_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
      'scope':'No t0/free implementations, physical contacts/helper complements, full operator/control word, precision/tape costs, compiler reserve, ordinary BIT or outer transfer are established. No kappa claim; no root-digit extraction.',
      'ordinary_BIT_extension_performed':False}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    result=run();args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],'max_uniform_extra_H1=44')

if __name__=='__main__':main()
