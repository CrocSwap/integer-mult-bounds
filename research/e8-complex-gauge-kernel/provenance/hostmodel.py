"""Hosted complex model: replicates idle-axis-hosting/complex_hosted.py profile arithmetic for arbitrary local paid profile
and per-helper residual widths (same for every stage/replica).  Needs scipy (venv python)."""
import gzip,json,sys,math,importlib.util,time
from collections import Counter
from pathlib import Path
from fractions import Fraction as Q
import os
CX=os.environ['CXG_BASE'];REPO=os.environ.get('CXG_REPO','.')
sys.path.insert(0,REPO+'/research/idle-axis-hosting')
import hosting_core as HC
V,K,T,L,M=120,4,8,9,73
DATA=2*K*V*T
PAR=Path(CX+'/parent/changed')
_t=json.loads(gzip.decompress((PAR/'split-centres/GLOBAL-TEMPLATE.json.gz').read_bytes()))
def _eng(name):
    sp=importlib.util.spec_from_file_location('h_'+name,PAR/'work/pr361/code/engines'/(name+'.py'));mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);return mod
ENG=_eng('moment')
rank={};pair_of_stage={e['stage']:e['pair'] for e in _t['recipe'] if e['kind']=='local'}
sched=[];side_of={};pair_of={}
for it in _t['idle_children']:rank.setdefault(it['child'],it['rank'])
for e in _t['execution_schedule']:
    if e['kind']=='local_cover_sweep':sched.append(dict(kind='local',stage=e['stage'],pair=pair_of_stage[e['stage']]))
    elif e['kind']=='bridge':sched.append(dict(kind='bridge',dst=e['dst'],src=e['src']))
    elif e['kind']=='idle_cover_sweep':
        for sd,ch in enumerate(e['child_indices']):
            if ch in rank:sched.append(dict(kind='idle',pair=e['pair'],rank=rank[ch],idx=ch));side_of[ch]=sd;pair_of[ch]=e['pair']
WINALL=HC.windows(sched)
IDLE=_t['idle_children']
def evaluate(local_profile,widths,discover=True,sel=None,verbose=False,pad_val=None,exact=False):
    """local_profile: {rank:count per call}; widths: list of residual widths (len R) -> dict(b,W,profile)"""
    R=len(widths);wmin=min(widths)
    win={k:x for k,x in WINALL.items() if x[1]>=wmin and x[2]}
    cnt=Counter(widths)
    avail={(s,w):c for s in range(L) for w,c in cnt.items()}
    # identify helper ids per width
    hl={};
    ids=sorted(range(R),key=lambda h:(-widths[h],h))
    helpers={s:[(h,widths[h]) for h in ids] for s in range(L)}
    if discover:
        ys,zs,val=HC.solve(win,V,avail,M,pad_value=(HC.cost(1,M)/8 if pad_val is None else pad_val))
    else:ys,zs,val=sel
    slots,rem=HC.expand(win,ys,zs,helpers,V)
    hosted={(s,h) for i,port,off,w,s,h in slots}  # per replica? slots are per (idx,copy) -> one replica set
    hosted_cnt=Counter((s,h) for i,c,o,w,s,h in slots)
    # each slot hosts replicas T times (same for all replicas)
    base=DATA;partial=Counter();banks=[]
    paid=Counter()
    W=DATA
    for s in range(L):
        left=[(rep,h) for rep in range(T) for h in range(R) if (s,h) not in {(s2,h2) for (_,_,_,_,s2,h2) in []}]
    # build hosted set
    hset={(s,h) for (_,_,_,_,s,h) in slots}
    for s in range(L):
        items=sorted([widths[h] for rep in range(T) for h in range(R) if (s,h) not in hset],reverse=True)
        bins=[]
        for w in items:
            for i,b in enumerate(bins):
                if b+w<=M:bins[i]+=w;break
            else:bins.append(w)
        W+=len(bins);banks.append(len(bins))
        for b in bins:
            if M-b:paid[M-b]+=1
    for r_,z in local_profile.items():paid[int(r_)]+=int(z)*L*T
    nid=0
    for it in IDLE:
        ch,port=it['child'],it['port'];rr=rem.get((ch,port),it['rank']) if ch in win else it['rank']
        if rr:paid[rr]+=T
    mass=sum(r*z for r,z in paid.items());D=M*W-mass
    out=dict(W=W,D=D,profile=dict(sorted(paid.items())),hosted=len(slots)*T,banks=banks,val=val,sel=(ys,zs,val))
    if exact:
        rc=ENG.certify({int(r):n for r,n in paid.items()},M,W,True);out['b']=float(Q(int(Q(rc['lower'])*10**18),10**18))
    else:out['b']=float(bfloat(paid,W))
    return out
def bfloat(paid,W,m=M):
    lo,hi=0.,.01
    for _ in range(80):
        q=(lo+hi)/2
        mom=sum(r*z/(m*W)*(m/r)**q for r,z in paid.items())+32*m*sum(paid.values())/(10**16*W)*m**q
        if mom<1:lo=q
        else:hi=q
    return (lo+hi)/2
if __name__=='__main__':
    t0=time.time()
    loc={1:1912,2:784,3:168,4:224,5:392,8:24}
    r=evaluate(loc,[9]*560,discover=False,sel=HC.load_selection(REPO+'/research/idle-axis-hosting/SELECTION.json','complex'),exact=True)
    print('frozen sel:',r['W'],r['D'],r['b'],r['banks'],r['hosted'],time.time()-t0)
    r=evaluate(loc,[9]*560,discover=True,exact=True)
    print('discover:',r['W'],r['D'],r['b'],r['banks'],r['hosted'],time.time()-t0)
