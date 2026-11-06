#!/usr/bin/env python3
"""Complete source-bound economics; no physical realization/admission claim.
Jerry Chen / @CubeJerry, substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json
import sys

sys.dont_write_bytecode=True

HERE=Path(__file__).resolve().parent
def need(x,message):
    if not x: raise ValueError(message)
pins=json.loads((HERE/'PINS.json').read_text())
for name,pin in pins['files'].items():
    need(sha256((HERE/'inputs'/name).read_bytes()).hexdigest()==pin['sha256'],'source pin '+name)
spec=importlib.util.spec_from_file_location('retained_power_intervals',HERE/'inputs/interval_engine.py')
E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)
ZERO=(Q(0),Q(0))
def add(*xs):return sum(x[0]for x in xs),sum(x[1]for x in xs)
def scale(x,c):return (x[0]*c,x[1]*c)if c>=0 else(x[1]*c,x[0]*c)
def fixed(x):return Q(x),Q(x)
def maximum(xs):
    xs=list(xs);return max(x[0]for x in xs),max(x[1]for x in xs)
def signed(T,P):
    x=Counter(T);x.subtract(P);return {r:n for r,n in x.items()if n}
def find_invoice(x):
    if isinstance(x,dict):
        if x.get('status')=='PASS_TWO_PAID_FRAGMENTS_COMPLETE_PRICE':return x
        for v in x.values():
            y=find_invoice(v)
            if y is not None:return y
    return None
def native(label):
    w=json.loads(gzip.decompress((HERE/'inputs'/f'{label}-WORD.json.gz').read_bytes()))
    if label=='COMPLEX':
        rank=lambda f:len(w['frames'][f])
        start=w['initial'];main=set(w['live'])|{x+112 for x in w['live']}
    else:
        rank=lambda f:w['frames'][str(f)]['dim']
        start=w['start'];main=set(range(222))
    P=Counter(abs(rank(e[3])-rank(e[2]))for e in w['program']if e[0]=='MOVE')
    T=Counter(abs(rank(w['final'][j])-rank(start[j]))for j in range(w['public'])if j not in main)
    need(0 not in P and 0 not in T,'strictly positive native ranks')
    return T,P

def root_signature(label):
    p=HERE/'inputs'/('COMPLEX-CALLER.json'if label=='COMPLEX'else'BIT-CALLER.json.gz')
    blob=p.read_bytes();w=json.loads(gzip.decompress(blob)if p.suffix=='.gz'else blob)
    groups=[set(range(1,5)),set(range(5,9)),{9},{10},set(range(11,15)),set(range(15,19))]
    def mask(stages):
        stages=set(stages);m=sum(1<<j for j,g in enumerate(groups)if g<=stages)
        need(set().union(*(g for j,g in enumerate(groups)if m>>j&1))==stages,'root uses whole child monomials')
        return m
    nodes=[e for e in w['events']if e[0]=='IDLE'];internal={r for e in nodes for r in e[1:3]}
    target=Counter();paid=Counter()
    for r,d in enumerate(w['diagonal']):
        if r in internal:continue
        head,stages=(d[0]%2,[j for j,v in enumerate(d[2:],1)if v])if label=='COMPLEX'else(d['q'],d['stages'])
        target[head,mask(stages)]+=1
    for e in w['events']:
        if e[0]=='IDLE_ONE':paid[0,mask(e[2])]+=1
    paid[1,0]=sum(e[0]=='QUERY'for e in w['events'])-len(nodes)
    need(paid[1,0]==3,'root thin queries, after binary-node queries')
    expected={(1,63):1,(1,7):1,(1,56):1,(1,6):1,(1,4):1,(1,24):1,(1,8):1,(1,0):-2,(0,6):-1,(0,4):-1,(0,24):-1,(0,8):-1}
    need(signed(target,paid)==expected,'complete symbolic six-child root signature')
    return {'root_productive_fields':sum(target.values()),'root_paid_idles':sum(v for (q,m),v in paid.items()if q==0),'root_thin_queries':paid[1,0],'symbolic_signature_matches':True}

def run(label,s,ports,lower,ceiling):
    root=root_signature(label)
    T0,P0=native(label);signed0=signed(T0,P0)
    original=json.loads((HERE/'inputs'/f'{label}-INVOICE.json').read_bytes())
    invoice=find_invoice(original)if label=='COMPLEX'else original
    T={int(r):n for r,n in invoice['targets'].items()};P={int(r):n for r,n in invoice['paid'].items()}
    # Full invoice at the retained (4,4,1,1,4,4) allocation, before cancellation.
    TT=Counter({r:18*n for r,n in T0.items()});PP=Counter({r:18*n for r,n in P0.items()})
    for n,count in [(2,8),(4,4)]:
        TT[s*n+1]+=2*ports*count;PP[s*n]+=2*ports*count;PP[1]+=ports*count
    for r,count in [(18*s+1,1),(9*s+1,2),(5*s+1,2),(s+1,2),(4*s,2),(1,1)]:TT[r]+=ports*count
    for r,count in [(1,3),(5*s,2),(4*s,2),(s,2)]:PP[r]+=ports*count
    need(dict(TT)==T and dict(PP)==P,'separate full target AND paid histograms')
    need(sum(T.values())==invoice.get('productive_fields',sum(T.values())),'productive field count')
    cap=Q('.004');lo=Q(lower);K=Q(ceiling);t=1-K
    h=lambda n:E.power(n,t)
    inc=lambda n:add(h(s*n+1),scale(h(s*n),-1))
    ell=scale(add(E.moment(T0,t),scale(E.moment(P0,t),-1)),Q(1,ports))
    A=add(scale(inc(2),2),fixed(-1))
    # Uniformly positive ordinary-node envelope on the whole stated interval.
    A_cap=add(scale(add(E.power(2*s+1,1-cap),scale(E.power(2*s,1-cap),-1)),2),fixed(-1))
    need(A_cap[0]>0,'ordinary node envelope positive')
    # i decreases in k and in its positive integer argument.
    i_low=add(E.power(s+1,1-lo),scale(E.power(s,1-lo),-1))
    i_high=add(E.power(49*s+1,1-cap),scale(E.power(49*s,1-cap),-1))
    replacement=add(scale(i_low,2),scale(i_high,-2),fixed(-1))
    need(replacement[1]<0,'all sub-50 replacements lose uniformly')
    # Retain the genuine local-gain regime as a scope control. The integral
    # derivative bound i(N)<=t*(s*N)^(-k) avoids huge H cancellation.
    local_positive=add(scale(i_low,2),scale(E.power(s*2**400,-lo),-2*(1-lo)),fixed(-1))
    need(local_positive[0]>0,'huge-asymmetry local gain remains possible')
    # Native signed moment decreases throughout [lower,.004].
    derivative=ZERO
    for r,c in signed0.items():
        pr=(E.power(r,1-cap)[0],E.power(r,1-lo)[1])
        derivative=add(derivative,scale(E.mul(pr,E.log_bounds(r)),Q(-c,ports)))
    need(derivative[1]<0,'native signed moment decreasing')
    def envelope(k):
        tt=1-k;H=lambda n:E.power(n,tt)
        I=lambda n:add(H(s*n+1),scale(H(s*n),-1))
        L=scale(add(E.moment(T0,tt),scale(E.moment(P0,tt),-1)),Q(1,ports))
        aa=add(scale(I(2),2),fixed(-1))
        B=add(scale(L,50),scale(aa,44),scale(I(1),4),H(50*s+1),scale(H(25*s+1),2),fixed(-2))
        d=add(L,aa,scale(E.power(50*s+1,-k),s*tt),scale(E.power(25*s+1,-k),s*tt))
        need(B[1]<0 and d[1]<0,'concave all-size tail at 50')
        return B,d
    tail,tailprime=envelope(lo)
    # Exact ordinary grammar maximization; four-query nodes are dominated here.
    dp=[ZERO]*50
    for n in range(2,50):dp[n]=add(maximum(add(dp[j],dp[n-j])for j in range(1,n)),scale(inc(n),2),fixed(-1))
    triples={n:maximum(add(dp[a],dp[b],dp[n-a-b],inc(n-a),inc(n-a-b))
                        for a in range(1,n-1)for b in range(1,n-a))for n in range(3,50)}
    finite={F:add(scale(ell,F),h(s*F+1),fixed(-2),maximum(add(triples[x],triples[F-x],h(s*x+1),h(s*(F-x)+1))for x in range(3,F-2)))for F in range(6,50)}
    need(all(x[1]<0 for x in finite.values()),'all finite allocations below raw ceiling')
    best=max(finite,key=lambda F:finite[F][1])
    need(finite[best][0]>max(x[1]for F,x in finite.items()if F!=best),'best leaf count separated by exact intervals')
    # Literal fresh-field cancellation for a same-orientation node (a=1,b=3).
    a,b=s,3*s
    newT=Counter({a+1:2,b:2});newP=Counter({a:2,b:2,1:2})
    need(signed(newT,newP)=={a+1:2,a:-2,1:-2},'four fresh productive targets, all idles and two thin queries')
    controls={}
    def node_invoice(tt,pp):need(tt==newT and pp==newP,'complete separate four-query node invoice')
    for name,tt,pp in [('unpaid_right_idle',newT,Counter({a:2,1:2})),('missing_fresh_targets',Counter({a+1:2}),newP),('missing_extra_query',newT,Counter({a:2,b:2,1:1}))]:
        try:node_invoice(tt,pp)
        except ValueError:controls[name]='rejected'
        else:raise ValueError('accepted invoice mutant '+name)
    free_extra=add(scale(inc(1),2),fixed(-1))
    need(free_extra[0]>A[1],'free extra query would defeat the A-envelope premise')
    controls['free_extra_query_breaks_envelope']='confirmed; changed tariff excluded'
    return dict(body_rank=s,ports=ports,native_helpers=dict(T0),native_paid=dict(P0),source_paid_jobs=sum(P0.values()),source_helpers=sum(T0.values()),literal_target_fields=sum(T.values()),literal_paid_jobs=sum(P.values()),literal_separate_histograms_match=True,
        root=root,uniform_interval=[str(lo),str(cap)],raw_ceiling=str(K),ordinary_envelope_at_cap=E.display(A_cap),replacement_gain_upper=E.display(replacement),huge_local_gain_lower=E.display(local_positive),huge_local_total_leaves='2^400',native_derivative=E.display(derivative),tail_start=50,tail_at_lower=E.display(tail),tail_derivative_at_lower=E.display(tailprime),finite_best_leaves=best,finite_maximum_at_ceiling=E.display(finite[best]),negative_controls=controls)

out={'status':'PASS_COMPLETE_MIXED_BINARY_GRAMMAR_CEILINGS','complex':run('COMPLEX',8,104,'.0033','.0033072446849'),'bit':run('BIT',7,111,'.0037','.0037667234776'),
 'scope':'Fixed six-site root, unchanged native source contracts, arbitrary positive six-child allocations and mixed ordinary/four-query binary trees. Power tariff, independently fresh retired fields, full thin and idle charges. No changed root, packed query tariff, new supplier or outer admission.'}
data=json.dumps(out,sort_keys=True,indent=2)+'\n'
if sys.argv[1:]==['--write']:
    (HERE/'RESULT.json').write_text(data)
else:
    need(not sys.argv[1:],'usage: verify.py [--write]')
    need((HERE/'RESULT.json').read_text()==data,'exact committed receipt')
print(data)
