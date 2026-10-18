"""Independent necessary-frame replay of the 992 changed-entry experiments.

All arithmetic is exact. Joins propagate necessary lower frames along the
register chains; equality pins add their complete subspace to the preceding
gate. No optimization result or claimed infeasibility receipt is trusted.
Only direct, contiguous scalar recovery after the host's final original use is
screened. This is not an exclusion of changed scalar circuits or staged undo.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import copy
import functools
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
FULL = tuple(1 << i for i in range(8, -1, -1))
HOSTEES = (592,593,594,596,600,601,602,604,608,609,610,612,617,624,
           625,626,632,633,634,640,642,644,648,649,650,652,656,657,
           658,660,673,674)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def basis(vectors):
    pivots = {}
    for vector in vectors:
        while vector:
            k = vector.bit_length()-1
            if k in pivots:
                vector ^= pivots[k]
            else:
                pivots[k] = vector
                break
    for k in sorted(pivots):
        for j in pivots:
            if j > k and pivots[j] >> k & 1:
                pivots[j] ^= pivots[k]
    return tuple(pivots[k] for k in sorted(pivots,reverse=True))


@functools.lru_cache(None)
def join(a,b):
    return basis(a+b)


@functools.lru_cache(None)
def perp(a):
    return basis(x for x in range(1,512) if all((x&y).bit_count()%2==0 for y in a))


@functools.lru_cache(None)
def meet(a,b):
    return perp(join(perp(a),perp(b)))


def regs(gate):
    return gate[1:3] if gate[0]=='add' else gate[1:2]


def events(word):
    result=[]
    for i,g in enumerate(word['A']):
        result.append(('A',i,g))
    result.append(('cut',None,None))
    warps=defaultdict(list)
    for op,rec in enumerate(word['warps'],1):
        warps[rec[0]].append((op,rec))
    for i in range(len(word['B'])+1):
        for op,rec in warps[i]:
            result.append(('Bwarp',i,['warp',rec[1],op,rec[3],rec[4]]))
        if i<len(word['B']):
            result.append(('B',i,word['B'][i]))
    result.extend(('restore',i,g) for i,g in enumerate(word['restore']))
    return result


def boundary(word):
    v=word['report']['v']
    pins={v+t:basis(word.get('target_levels',{}).get(str(t),[])) for t in range(v)}
    pins.update({q:basis(U) for q,U in zip(word['centers'],word['center_frames'])})
    return pins


def chains(word):
    ev=events(word); forced=defaultdict(tuple); previous={}; pins=boundary(word)
    for t,(sec,_,g) in enumerate(ev):
        if sec=='cut':
            for q,U in pins.items():
                if q in previous:
                    forced[previous[q]]=join(forced[previous[q]],U)
            continue
        if g[0]=='warp':
            if g[1] in previous:
                forced[previous[g[1]]]=join(forced[previous[g[1]]],basis(g[3]))
            previous.pop(g[1],None)
        else:
            for q in regs(g):
                previous[q]=t
    return ev,forced,pins


def starts(word):
    v=word['report']['v'];n=2*v+word['report']['R']
    current=[(p,) for p in word['ports']]+[()]*(n-v)
    for q,U in word['start_extra'].items():current[int(q)]=basis(U)
    return current


def base_bounds(word):
    """Independent lower/upper passes, used to identify the exact rank5 caps."""
    ev,forced,pins=chains(word);cur=starts(word);lo={}
    for t,(sec,idx,g) in enumerate(ev):
        if sec=='cut':
            for q,U in pins.items():cur[q]=join(cur[q],U)
        elif g[0]=='warp':cur[g[1]]=basis(g[4])
        else:
            U=forced[t]
            for q in regs(g):U=join(U,cur[q])
            for q in regs(g):cur[q]=U
            lo[sec,idx]=U
    v=word['report']['v'];n=2*v+word['report']['R']
    cur=[FULL]*v+[perp((p,)) for p in word['ports']]+[FULL]*(n-2*v)
    for q,U in word['helper_final'].items():cur[int(q)]=basis(U)
    hi={}
    for t in range(len(ev)-1,-1,-1):
        sec,idx,g=ev[t]
        if sec=='cut':
            for q,U in pins.items():cur[q]=meet(cur[q],U)
        elif g[0]=='warp':cur[g[1]]=basis(g[3])
        else:
            U=forced[t] if t in forced and forced[t] else FULL
            for q in regs(g):U=meet(U,cur[q])
            for q in regs(g):cur[q]=U
            hi[sec,idx]=U
    return lo,hi


def hyperplanes(U):
    require(len(U)==5,'first-write cap must have rank5')
    vec={}
    for mask in range(1,32):
        x=0
        for i,u in enumerate(U):
            if mask>>i&1:x^=u
        vec[mask]=x
    ans=sorted({basis(x for mask,x in vec.items() if (mask&f).bit_count()%2==0) for f in range(1,32)})
    require(len(ans)==31 and all(len(x)==4 for x in ans),'hyperplane enumeration')
    return ans


def hosting(word,h,E,c=277):
    """Only proof-relevant frame/scalar fields of J's frozen hosting edit.

    Initial corrections and cleanup have no framed gates in the searched
    interval. They are deliberately outside this necessary-condition replay.
    The original experiment separately certified complete hosted words.
    """
    w=copy.deepcopy(word);v=w['report']['v'];B=w['B']
    pos=[i for i,g in enumerate(B) if h in regs(g)]
    first=next(i for i in pos if not(B[i][0]=='add' and B[i][2]==h and v<=B[i][1]<2*v))
    reads=[i for i in pos if i<first]
    require(str(c) in w['helper_final'] and str(c) not in w['start_extra'],'host interface')
    require(str(h) in w['start_extra'] and str(h) not in w['helper_final'],'hostee interface')
    require(not any(c in regs(g) for g in w['restore']),'host used in restore')
    require(not any(rec[1] in (h,c) for rec in w['warps']),'existing host/hostee warp')
    require(max((i for i,g in enumerate(B) if c in regs(g)),default=-1)<first,'host retirement')
    U=w['helper_final'][str(c)]
    require(len(basis(U))==len(E)==4,'rank4 entry')
    for g in B[first:]:
        for k in (1,2) if g[0]=='add' else (1,):
            if g[k]==h:g[k]=c
    deleted=set(reads);w['B']=[g for i,g in enumerate(B) if i not in deleted]
    shift=lambda p:p-sum(i<p for i in deleted)
    w['warps']=[[shift(rec[0])]+rec[1:] for rec in w['warps']]
    # G does not enter the necessary frame/recovery constraint. The frozen
    # constructor generates and checks its invertible extension separately.
    w['warps'].append([shift(first),c,None,U,list(E)])
    del w['helper_final'][str(c)];del w['start_extra'][str(h)];w['removed'].append(h)
    return w


def expressions(w):
    c=w['warps'][-1][1];start=w['warps'][-1][0]
    last=max(i for i,g in enumerate(w['B']) if c in regs(g))
    coeff={c:Fraction(1)};samples={};other=defaultdict(list)
    for rec in w['warps'][:-1]:other[rec[0]].append(rec[1])
    def step(g):
        a=coeff.get(g[1],0)
        if a:
            if g[0]=='add':coeff[g[2]]=coeff.get(g[2],0)-a*Fraction(g[3],g[4])
            else:coeff[g[1]]/=Fraction(g[2],g[3])
        for q in [q for q,v in coeff.items() if not v]:del coeff[q]
    for i in range(start,len(w['B'])):
        require(not any(coeff.get(q) for q in other[i]),'non-scalar recovery outside domain')
        step(w['B'][i])
        if i>=last:samples['B',i]=tuple(coeff)
    require(not any(coeff.get(q) for q in other[len(w['B'])]),'terminal non-scalar recovery')
    for i,g in enumerate(w['restore']):
        step(g);samples['restore',i]=tuple(coeff)
    return samples


def screen(w):
    samples=expressions(w);ev,forced,pins=chains(w);cur=starts(w);hist=Counter()
    for t,(sec,idx,g) in enumerate(ev):
        if sec=='cut':
            for q,U in pins.items():cur[q]=join(cur[q],U)
        elif g[0]=='warp':cur[g[1]]=basis(g[4])
        else:
            U=forced[t]
            for q in regs(g):U=join(U,cur[q])
            for q in regs(g):cur[q]=U
            if (sec,idx) in samples:
                F=()
                for q in samples[sec,idx]:F=join(F,cur[q])
                hist[len(F)]+=1
    return dict(min_rank=min(hist),rank_histogram={str(r):n for r,n in hist.items()},
                scalar_slots=sum(hist.values()),non_scalar_slots=0)


def work(item):
    h,E=item
    return dict(hostee=h,host=277,E=list(E),**screen(hosting(BASE,h,E)))


def initialize(word):
    global BASE
    BASE=word


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=4);args=ap.parse_args()
    require(1<=args.workers<=24,'workers must be in1..24')
    pins=json.loads((HERE/'PINS.json').read_text())
    for name,key in [('base-b.json.gz','base_b_sha256'),('EXPECTED.json','expected_sha256')]:
        require(hashlib.sha256((HERE/name).read_bytes()).hexdigest()==pins[key],'source hash: '+name)
    base=json.loads(gzip.decompress((HERE/'base-b.json.gz').read_bytes()))
    expected=json.loads((HERE/'EXPECTED.json').read_text());lo,hi=base_bounds(base)
    # Original literal frames give a feasible positive control for every bound.
    for sec in ('A','B','restore'):
        for i,g in enumerate(base[sec]):
            if g[0]=='warp':continue
            F=basis(g[-1]);require(join(lo[sec,i],F)==F and meet(hi[sec,i],F)==F,'literal positive control')
    jobs=[]
    for h in HOSTEES:
        first=next(i for i,g in enumerate(base['B']) if h in regs(g) and not(g[0]=='add' and g[2]==h and 112<=g[1]<224))
        jobs.extend((h,E) for E in hyperplanes(hi['B',first]))
    require(len(jobs)==992,'case count')
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers,initializer=initialize,initargs=(base,)) as pool:
        actual=list(pool.map(work,jobs,chunksize=4))
    key=lambda x:(x['hostee'],x['E'])
    require(sorted(actual,key=key)==sorted(expected['results'],key=key),'exact census differs')
    require(all(x['min_rank']==9 for x in actual),'rank9 result')
    # A changed result and a corrupted input cannot silently pass this binding.
    bad=copy.deepcopy(actual);bad[0]['min_rank']=8
    require(sorted(bad,key=key)!=sorted(expected['results'],key=key),'forged rank control')
    corrupted=bytearray((HERE/'base-b.json.gz').read_bytes());corrupted[-1]^=1
    require(hashlib.sha256(corrupted).hexdigest()!=pins['base_b_sha256'],'source corruption control')
    print(json.dumps(dict(status='PASS_CHANGED_ENTRY_NECESSARY_FRAME_CENSUS',cases=len(actual),
                         slots=sum(x['scalar_slots'] for x in actual),minimum_rank_counts=dict(Counter(x['min_rank'] for x in actual)),
                         controls=['literal_bounds','forged_rank','source_corruption'],
                         scope='host277, b orientation,32 specified hostees,31 rank4 entries each; contiguous direct recovery only'),sort_keys=True))


if __name__=='__main__':main()
