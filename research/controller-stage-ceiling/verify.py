#!/usr/bin/env python3
"""Exact stage-family bound. Apache-2.0; substantial OpenAI Codex assistance.

Credits the floating DP in kappa-hybrid-controller/search/direct_stage_dp.py.
All acceptance scores here are outward integer bounds, never floating output.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse,gzip,importlib.util,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SCALE=2**64
MAX_P=64

def need(v,s):
    if not v:raise ValueError(s)
def read(path):
    raw=path.read_bytes();return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)
def authenticate():
    for row in read(HERE/'SOURCES.json')['files']:
        if row['usage']=='input':need(sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'Changed input: '+row['path'])
def engine():
    spec=importlib.util.spec_from_file_location('stage_intervals',ROOT/'research/higher-moment-strictification/verify.py')
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m
def profiles():
    a=read(ROOT/'research/joint-helper-lattice/NATIVE.json.gz');b=read(HERE/'inputs/pr4610-native.json');c=read(HERE/'inputs/pr4626-arithmetic.json')
    ints=lambda d:{int(k):v for k,v in d.items()}
    return {'PR4470':(ints(a['helpers']),ints(a['paid'])),'PR4610':(ints(b['helpers']),ints(b['paid'])),'PR4626':(ints(c['local_helpers']),ints(c['local_paid']))}
def weights(E,c):
    ranks={*range(1,10),*(8*k for k in range(1,2*MAX_P+2)),*(1+8*k for k in range(2*MAX_P+2))}
    low,high={0:0},{0:0}
    for r in sorted(ranks):
        a,b=E.power(r,1-c);low[r]=(a*SCALE).__floor__();high[r]=-((-b*SCALE).__floor__())
        need(Q(low[r],SCALE)<=a<=b<=Q(high[r],SCALE),'Outward integer powers')
    return low,high

def branches(length,low,high,omit_middle=False):
    states={k:(0,(1<<k)-1) for k in range(3 if length else 2)}
    for j in range(1,length+1):
        new={}
        for count,(score,mask) in states.items():
            for even in (0,1):
                n=count+even
                val=score+224*(high[1+8*n]-low[8*count]-(0 if omit_middle else even*low[8]))
                m=mask|(even<<(2*j))
                for odd in ((0,1) if j<length else (0,)):
                    nn,mm=n+odd,m|(odd<<(2*j+1))
                    if nn not in new or val>new[nn][0]:new[nn]=val,mm
        states=new
    return states

def envelope(low,high,max_p=MAX_P,omit_middle=False):
    arms=[branches(n,low,high,omit_middle) for n in range(max_p)];best={}
    for p in range(1,max_p+1):
        for cut in range(p):
            right=p-1-cut
            for nl,(sl,ml) in arms[cut].items():
                for nr,(sr,mr) in arms[right].items():
                    for middle in (0,1):
                        n=nl+nr+middle
                        val=sl+sr-112*(2*p+1)*low[1]+224*high[1+8*n]
                        if n not in best or val>best[n][0]:
                            reflected=sum(1<<(2*p-j) for j in range(2*right+1) if mr>>j&1)
                            best[n]=val,(p,cut,ml|reflected|(middle<<(2*cut+1)))
    return best

def maximum(env,lo,hi,h,paid):
    delta=112*hi[1]+sum(v*hi[r] for r,v in h.items())-sum(v*lo[r] for r,v in paid.items())
    return max((score+n*delta,args) for n,(score,args) in env.items())

def invoice(p,cut,mask,h,local,omit_middle=False):
    n=mask.bit_count();T=Counter({r:n*v for r,v in h.items()});P=Counter({r:n*v for r,v in local.items()})
    P[1]+=112*(2*p+1-n);T[1+8*n]+=224
    for length,reverse in ((cut,False),(p-1-cut,True)):
        for j in range(1,length+1):
            pos=list(range(2*j+1))
            if reverse:pos=[2*p-s for s in pos]
            count=sum(mask>>s&1 for s in pos);idle=sum(mask>>s&1 for s in pos[:-1])
            T[1+8*count]+=224
            if idle:P[8*idle]+=224
    if not omit_middle:P[8]+=224*sum(mask>>(2*j)&1 for j in range(1,p))
    return +T,+P

def brute_arm(length,lo,hi):
    result={}
    for mask in range(1<<(2*length+1)):
        val=0
        for j in range(1,length+1):
            old=(mask&((1<<(2*j))-1)).bit_count();even=mask>>(2*j)&1
            val+=224*(hi[1+8*(old+even)]-lo[8*old]-even*lo[8])
        n=mask.bit_count();result[n]=max(result.get(n,val),val)
    return result

def monotonicity(E,h,paid):
    lg=E.log_bounds(8);lower=Q(paid[1]-112,8)*lg[0]
    for r,v in h.items():
        if r<8:lower-=v*(lg[1]-E.log_bounds(r)[0])
    need(lower>0 and max(paid)<=8 and min(h)>=1,'Strict separator derivative')
    return str(lower)

def literal_control(h,paid):
    row=read(ROOT/'research/joint-helper-lattice/CONTROLLER.json');T,P=Counter(),Counter()
    for e in row['physical_events']:
        if e[0]=='LOCAL':T.update(h);P.update(paid)
        elif e[0]=='QUERY_SHEAR':P[1]+=112
        elif e[0]=='IDLE':P[8*len(e[2])]+=224
    for term in row['diagonal']:T[1+8*sum(term[1:])]+=112
    mask=sum(1<<s for s in {0,32,*range(1,32,2)})
    need((+T,+P)==invoice(16,7,mask,h,paid),'Full literal p16 invoice')

def run():
    authenticate();E=engine();local=profiles();c=Q('.003022');lo,hi=weights(E,c)
    print('POWERS_READY',flush=True);env=envelope(lo,hi);receipt={}
    for name,(h,paid) in local.items():
        val,args=maximum(env,lo,hi,h,paid);need(val<0,'Stage-family rejection: '+name)
        T,P=invoice(*args,h,paid);a,b=E.moment(T,1-c),E.moment(P,1-c)
        need(a[1]-b[0]<=Q(val,SCALE),'Independent invoice bound at DP witness');literal_control(h,paid)
        receipt[name]={'surplus_upper':str(Q(val,SCALE)),'witness_parameters':args,'separator_derivative_lower':monotonicity(E,h,paid)}
    for length in range(5):
        need({n:s for n,(s,_) in branches(length,lo,hi).items()}==brute_arm(length,lo,hi),'Every small-arm pattern')
    small=envelope(lo,hi,3)
    for name,(h,paid) in local.items():
        found=-10**100
        for p in range(1,4):
            for cut in range(p):
                for mask in range(1<<(2*p+1)):
                    T,P=invoice(p,cut,mask,h,paid)
                    found=max(found,sum(v*hi[r] for r,v in T.items())-sum(v*lo[r] for r,v in P.items()))
        upper,_=maximum(small,lo,hi,h,paid)
        need(0<=upper-found<10**6,'Small full census and outward rounding')
    h,paid=local['PR4610'];bad,_=maximum(envelope(lo,hi,omit_middle=True),lo,hi,h,paid)
    need(bad>0,'Omitting real middle-idle work changes sign')
    duplicate,_=maximum(env,lo,hi,{r:2*v for r,v in h.items()},paid)
    need(duplicate>0,'Duplicate helper credit changes sign')
    print('CEILING_AND_CONTROLS_PASS',flush=True);funding={};optimistic=dict(paid);optimistic[1]+=8;del optimistic[8]
    for tested in (Q('.004'),Q('.006'),Q('.01')):
        low,high=weights(E,tested);ee=envelope(low,high);val,args=maximum(ee,low,high,h,optimistic)
        T,P=invoice(*args,h,optimistic);a,b=E.moment(T,1-tested),E.moment(P,1-tested)
        funding[str(tested)]={'best_surplus_upper':str(Q(val,SCALE)),'witness_surplus_lower':str(a[0]-b[1]),'witness_parameters':args,'status':'OPTIMISTIC_INVOICE_ONLY_NO_H_NATIVE_ADMISSION'}
        print('BUDGET_READY',tested,flush=True)
    return {'status':'PASS_EXACT_STAGE_FAMILY_CEILING','ceiling':str(c),'pair_counts':[1,MAX_P],'all_splits':True,'all_native_stage_subsets':True,'patterns_per_profile':str(sum(p*(1<<(2*p+1)) for p in range(1,MAX_P+1))),'fixed_point_scale':str(SCALE),'profiles':receipt,'optimistic_H_repair_budgets':funding,'controls':['all_5_small_arm_censuses','all_complete_patterns_p1_to_p3','all_3_literal_p16_invoices','missing_middle_idle_changes_sign','duplicate_helper_credit_changes_sign'],'new_kappa':None,'scope':'Frozen native invoices and minimal-cut path family, p<=64. No global operator/controller ceiling or new supplier.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args();result=run();target=HERE/'RESULT.json'
    if args.write:target.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(read(target)==json.loads(json.dumps(result)),'Exact stored receipt')
    print(json.dumps(result,indent=2,sort_keys=True))
