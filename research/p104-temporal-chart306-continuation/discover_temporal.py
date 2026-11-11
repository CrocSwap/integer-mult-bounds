"""Bounded exact temporal helper nomination using existing neutral paths.

Ali Romman's causal-history identity and CubeJerry's contact-free retiming;
Matarener's exact pure kernels. Rohan Arun/OpenAI Codex, Apache-2.0.
No native, physical or complete-price acceptance is inferred from this search.
"""
import argparse,gzip,json,time
from pathlib import Path
from collections import defaultdict,Counter
from fractions import Fraction as Q
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from support import L
from split import basis

def encode(x):
    if isinstance(x,Q): return str(x)
    if isinstance(x,dict): return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [encode(v) for v in x]
    return x


def smooth(n):
    if not n:return False
    for p in (2,3,5):
        while n%p==0:n//=p
    return n==1


def legal(prog):
    for e in prog:
        q=Q(e[-2])
        if not q or abs(q)+1>=2**16 or not smooth(q.denominator):return False
        if e[0]=='SCALE' and not smooth(abs(q.numerator)):return False
    return True



def kernel(observations,side,group):
    pivots={};out=[]
    order=sorted(range(len(observations)),key=lambda i:observations[i]['lo'] if side=='pre' else -observations[i]['hi'])
    for i in order:
        row=observations[i][side]
        outside={k:v for k,v in row.items() if k not in group}
        inside={k:v for k,v in row.items() if k in group};coef={i:Q(1)}
        while outside:
            k=min(outside)
            if k not in pivots:
                q=1/outside[k];pivots[k]=[{j:v*q for j,v in x.items()}for x in (outside,inside,coef)];break
            q=-outside[k]
            for dst,src in zip((outside,inside,coef),pivots[k]):L.add(dst,src,q)
        if not outside and inside:
            boundary=max(observations[j]['lo']for j in coef) if side=='pre' else min(observations[j]['hi']for j in coef)
            out.append((inside,coef,boundary))
    return out

def run(a):
    start=time.monotonic();w=json.loads(gzip.decompress(a.word.read_bytes()));seq=w['program'];n=w['public'];N=n+w['owned_fields']
    spans=list(map(L.span,w['frames']));U,V=a.group
    main=set(w['live'])|{r+112 for r in w['live']}|set(w['hosted']['X2'])|set(w['hosted']['Y2'])
    group={r for r in range(n)if r not in main and (w['initial'][r],w['final'][r])==(U,V)}
    valid={f for f,F in enumerate(spans)if spans[U]<F<spans[V]}
    contacts=defaultdict(list);moves=defaultdict(list)
    for i,e in enumerate(seq):
        if e[0]=='MOVE':moves[e[1]].append(i)
        else:
            contacts[e[1]].append(i)
            if e[0]in('ADD','COPY'):contacts[e[2]].append(i)
    observations=[];frames=defaultdict(list);paid_frames=defaultdict(list);starts=defaultdict(list);ends=defaultdict(list)
    for r in range(N):
        cuts=[-1]+contacts[r]+[len(seq)]
        for lo,hi in zip(cuts,cuts[1:]):
            mi=[i for i in moves[r]if lo<i<hi]
            if not mi:continue
            path=[seq[mi[0]][2]]+[seq[i][3]for i in mi]
            for f in sorted(set(path)&valid):
                p={'role':r,'lo':lo+1,'hi':hi,'frame':f,'moves':mi,'frames':path}
                idx=len(observations);observations.append(p);frames[f].append(idx);starts[lo+1].append(idx);ends[hi].append(idx)
            if a.paid_limit:
                x,y=path[0],path[-1];old=[abs(len(w['frames'][seq[i][3]])-len(w['frames'][seq[i][2]]))for i in mi]
                for f in sorted(valid-set(path)):
                    if not(spans[x]<=spans[f]<=spans[y] or spans[y]<=spans[f]<=spans[x]):continue
                    new=[abs(len(w['frames'][f])-len(w['frames'][x])),abs(len(w['frames'][y])-len(w['frames'][f]))]
                    t=1-a.kappa;cost=sum(v**t for v in new)-sum(v**t for v in old)
                    gain=(len(w['frames'][f])-len(w['frames'][U]))**t+(len(w['frames'][V])-len(w['frames'][f]))**t-(len(w['frames'][V])-len(w['frames'][U]))**t
                    if cost>=gain-1e-12:continue
                    p={'role':r,'lo':lo+1,'hi':hi,'frame':f,'moves':mi,'old':x,'new':y,'old_paid':old,'new_paid':new,'cost':cost,'gain':gain,'private':r>=n,'paid':True}
                    idx=len(observations);observations.append(p);paid_frames[f].append(idx);starts[lo+1].append(idx);ends[hi].append(idx)
    print('DOMAIN',len(group),'helpers',len(observations),'observations',len(frames),'frames',flush=True)
    rows=[{r:Q(1)}if r<n else{}for r in range(N)]
    for cut in range(len(seq)+1):
        for idx in starts.get(cut,[]):observations[idx]['pre']=rows[observations[idx]['role']].copy()
        if cut==len(seq):break
        e=seq[cut];op,r=e[:2]
        if op in('INIT','CLEAR'):rows[r]={}
        elif op=='SCALE':rows[r]={k:v*Q(e[-2])for k,v in rows[r].items()}
        elif op in('ADD','COPY'):
            if op=='COPY':rows[r]={}
            L.add(rows[r],rows[e[2]],Q(e[-2]))
    print('PREFIX',round(time.monotonic()-start,2),flush=True)
    cols=[{r:Q(1)}if r<n else{}for r in range(N)]
    for cut in range(len(seq),-1,-1):
        for idx in ends.get(cut,[]):observations[idx]['suf']=cols[observations[idx]['role']].copy()
        if not cut:break
        e=seq[cut-1];op,r=e[:2]
        if op in('INIT','CLEAR'):cols[r]={}
        elif op=='SCALE':cols[r]={k:v*Q(e[-2])for k,v in cols[r].items()}
        elif op in('ADD','COPY'):
            L.add(cols[e[2]],cols[r],Q(e[-2]))
            if op=='COPY':cols[r]={}
    print('SUFFIX',round(time.monotonic()-start,2),flush=True)
    stats=Counter();a.out.mkdir(exist_ok=False)
    trials=[(f,ids,None)for f,ids in sorted(frames.items())]
    if a.paid_limit:
        trials=[(f,frames.get(f,[])+[i],i)for f,ids in sorted(paid_frames.items())for i in ids][:a.paid_limit]
    for f,ids,paid_idx in trials:
        obs=[observations[i]for i in ids];pre=kernel(obs,'pre',group);suf=kernel(obs,'suf',group)
        stats['frames']+=1;stats['prefix_pure']+=len(pre);stats['suffix_pure']+=len(suf)
        for c,aa,lo in pre:
            for dd,bb,hi in suf:
                if lo>hi:continue
                pair=sum(v*dd.get(k,0)for k,v in c.items())
                if not pair:continue
                stats['causal_nonzero_pairs']+=1
                d={k:v/pair for k,v in dd.items()};b={k:v/pair for k,v in bb.items()}
                pivots=[(max(lo,o['lo']),o['role'],j)for j,o in enumerate(obs)if o['role']in group and max(lo,o['lo'])<=min(hi,o['hi'])]
                for cut,pivot,pidx in sorted(pivots):
                    stats['resident_pairs']+=1
                    scales={Q(1)}|{1/v for v in d.values()}
                    for scale in sorted(scales,key=lambda v:abs(v.numerator).bit_length()+v.denominator.bit_length()):
                        cc={k:v/scale for k,v in c.items()};dv={k:v*scale for k,v in d.items()};av={k:v/scale for k,v in aa.items()};bv={k:v*scale for k,v in b.items()}
                        code=basis(cc,dv,pivot,U)+[['ADD',N,obs[j]['role'],str(v),f]for j,v in list(av.items())+list(bv.items())]
                        if not legal(code):continue
                        used=sorted(j for j in set(av)|set(bv)|{pidx}if not obs[j].get('paid'));remap={j:i for i,j in enumerate(used)}
                        paths=[{k:v for k,v in obs[j].items()if k not in ('pre','suf')}for j in used]
                        def point(j,v,side):return {'cut':obs[j]['lo' if side=='pre' else 'hi'],'role':obs[j]['role'],'frame':f,**({'paid_path':0}if obs[j].get('paid')else{'path':remap[j]}),'coefficient':v}
                        hit={'frame':f,'cut':cut,'pivot':pivot,'ranks':[len(w['frames'][f])-len(w['frames'][U]),len(w['frames'][V])-len(w['frames'][f])],'c':cc,'d':dv,'gathers':[point(j,v,'pre')for j,v in av.items()],'injections':[point(j,v,'suf')for j,v in bv.items()],'paid_delta':{}}
                        if paid_idx is not None:
                            path={k:v for k,v in observations[paid_idx].items()if k not in ('pre','suf','paid')};delta=Counter(v for v in path['new_paid']if v);delta.subtract(path['old_paid']);hit.update(paid_path=0,path=path,paid_delta={r:v for r,v in delta.items()if v})
                        (a.out/'WITNESS.json').write_text(json.dumps(encode(hit),indent=2));(a.out/'PATHS.json').write_text(json.dumps(encode(paths),indent=2))
                        (a.out/'SEARCH.json').write_text(json.dumps({'status':'EXACT_TEMPORAL_NOMINATION_ONLY','counts':stats,'seconds':time.monotonic()-start},indent=2));print('NOMINEE',f,cut,pivot,dict(stats),flush=True);return
        if stats['frames']%100==0:print('FRAMES',dict(stats),flush=True)
    (a.out/'SEARCH.json').write_text(json.dumps({'status':'NO_NOMINEE_IN_BOUNDED_TEMPORAL_DOMAIN','paid_limit':a.paid_limit,'counts':stats,'seconds':time.monotonic()-start},indent=2));print('NO_NOMINEE',dict(stats),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--word',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--group',nargs=2,type=int,default=[3,127]);p.add_argument('--paid-limit',type=int,default=0);p.add_argument('--kappa',type=float,default=0.003);run(p.parse_args())
