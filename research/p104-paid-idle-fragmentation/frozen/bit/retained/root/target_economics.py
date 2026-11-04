#!/usr/bin/env python3
"""Source-bound comparison of complete invoices, with exact target prices.

The first derivative is a diagnostic, never a substitute for the actual
signed-moment test. The F16 caller is independently replayed before pricing.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import importlib.util,json,hashlib,time
H=Path(__file__).resolve().parent

def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    begun=time.monotonic();I=load(H/'inputs/independent_interval.py','economics_exact');A=load(H/'audit_binary_mixed.py','economics_audit')
    for p in json.loads((H/'INPUT-PINS.json').read_text()):
        b=(H/p['path']).read_bytes();A.need(hashlib.sha256(b).hexdigest()==p['sha256'],'Pinned history')
    @lru_cache(None)
    def pw(r,t):
        lo,hi=I.power(r,t);s=10**60;return Q((lo*s).__floor__(),s),Q(-((-hi*s).__floor__()),s)
    def moment(h,t):
        lo=hi=Q(0)
        for r,n in h.items():
            a,b=pw(int(r),t);lo+=n*a;hi+=n*b
        return lo,hi
    def gap(T,P,k):
        a,b=moment(T,1-k),moment(P,1-k);return a[0]-b[1],a[1]-b[0]
    def rank_entropy(h):
        lo=hi=Q(0)
        for r,n in h.items():
            a,b=I.logarithm(int(r));lo+=n*int(r)*a;hi+=n*int(r)*b
        return lo,hi
    oldc=json.loads((H/'inputs/PREVIOUS-COMPLEX-ADMISSION.json').read_text())
    newc=json.loads((H.parent/'clean_composition/RESULT.json').read_text())
    oldb=json.loads((H/'inputs/BASELINE-ADMISSION.json').read_text())['branches']['bit']
    newb=json.loads((H/'BINARY-MIXED-ADMISSION.json').read_text())
    word=A.load(H.parent/'bit_mixed_caller/GOAL-BALANCED-16-CALLER.json.gz','8824b4cc22ba67b576b9d648e88483bb47d0f54678b94c7e9e3d90b42e804df9')
    checked=A.backward(word)
    source=A.load(A.SOURCE,A.SOURCE_SHA);pp,hh,_=A.source_audit(source)
    F=word['stages'];P=Counter({r:F*v for r,v in pp.items()});T=Counter({r:F*v for r,v in hh.items()})
    for e in word['events']:
        if e[0]=='QUERY':P[1]+=111
        if e[0]=='IDLE':P[7*len(e[3])]+=222
        if e[0]=='IDLE_ONE':P[7*len(e[2])]+=111
    for d in word['diagonal']:T[1+7*len(d['stages'])]+=111
    rows=[('previous_complete_complex_F19',oldc,19,Q(oldc['kappa'])),
          ('new_complete_complex_F18',newc['price'],18,Q(newc['kappa'])),
          ('previous_complete_BIT_F19',oldb,19,Q(oldb['ordinary_admitted'])),
          ('new_complete_BIT_F18',newb,18,Q(newb['ordinary_admitted'])),
          ('goal_balanced_BIT_F16',dict(paid=P,targets=T),16,None)]
    out=[]
    for label,r,F,k in rows:
        paid={int(x):v for x,v in r['paid'].items()};targets={int(x):v for x,v in r['targets'].items()}
        mass=sum(x*v for x,v in targets.items())-sum(x*v for x,v in paid.items())
        a,b=rank_entropy(targets),rank_entropy(paid);slope=(a[0]-b[1],a[1]-b[0]);A.need(slope[0]>0,'Positive first-order loss')
        goals={}
        for goal in (Q('.0042'),Q('.00424927762')):
            g=gap(targets,paid,goal);A.need(g[1]<0,'Current complete invoice remains below the goal')
            goals[str(goal)]=dict(complete_margin=I.bounds_text(g,26),
                additional_net_saving_per_source=I.bounds_text((-g[1]/F,-g[0]/F),26))
        out.append(dict(label=label,admitted_saving=str(k)if k else None,source_calls=F,
            rank_surplus=mass,rank_log_rank_loss=I.bounds_text(slope,20),
            first_order_crossing_diagnostic=I.bounds_text((Q(mass)/slope[1],Q(mass)/slope[0]),20),
            goals=goals))
    goal=Q('.00424927762');price=1+4**float(1-goal)-5**float(1-goal)
    # Exact clean native concentration gain, not a removal of rank mass.
    p4,p5=pw(4,1-goal),pw(5,1-goal)
    merge=(1+p4[0]-p5[1],1+p4[1]-p5[0])
    res=dict(status='PASS_COMPLETE_INVOICE_ECONOMICS',cases=out,
        exact_stronger_goal=str(goal),reference_complete_baseline=str(Q('.00324927762')),
        new_complete_gain=str(Q(newc['kappa'])-Q('.00324927762')),
        new_complete_relative_percent=str(100*(Q(newc['kappa'])/Q('.00324927762')-1)),
        missing_to_0042=str(Q('.0042')-Q(newc['kappa'])),
        missing_to_exact_plus_001=str(goal-Q(newc['kappa'])),
        clean_merge_gain_per_source_at_goal=I.bounds_text(merge,26),
        goal_caller_independent_polynomial_entries=checked,
        scope='All margins are outward rational enclosures of complete emitted profiles. Per-source gaps assume a repeated source improvement with unchanged caller interfaces and the indicated multiplicity; they are requirements, not invented savings. The rank-log-rank ratio is only a first-order diagnostic.',seconds=time.monotonic()-begun)
    (H/'TARGET-ECONOMICS.json').write_text(json.dumps(res,indent=2)+'\n')
    print(json.dumps(res,indent=2))

if __name__=='__main__':main()
