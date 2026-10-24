"""Change a native G map and jointly retime its adjacent scalar contacts.

For an operator appearing at only one nontrivial frame pair, other occurrences
at zero/full frames impose no subspace restriction. Equal-dimensional warp
entrance and exit frames can be matched by an explicit invertible G.
"""
from collections import Counter,defaultdict
from copy import deepcopy
import gzip,json,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from warp_merge import J,F,roles,synthesize
sys.path.insert(0,str(ROOT/'research/scalar-reorder-20261022'))
from intervals import complete_interval,basis


def matching_map(A,B):
    assert len(A)==len(B)
    def extend(a):
        a=a[:]
        for i in range(9):
            if len(basis(a+[1<<i]))>len(a):a.append(1<<i)
        assert len(a)==9;return a
    A,B=extend(A),extend(B);images={0:0}
    for a,b in zip(A,B):images.update({x^a:y^b for x,y in list(images.items())})
    assert len(images)==512 and len(set(images.values()))==512
    return [images[1<<i] for i in range(9)]


def main():
    start=time.monotonic();c,programs,*_=J.construct()
    spans=[F.span(b) for b in c['frames']];dims=[len(b) for b in c['frames']]
    p=[deepcopy(e) for e in programs['forward'] if e[0]!='climb']
    occurrences=defaultdict(list)
    for i,e in enumerate(p):
        if e[0]=='warp':occurrences[abs(e[2])].append(i)
    prev,nxt={},{};prev_event,nxt_event={},{};cur=c['start'][:];last=[None]*632
    for i,e in enumerate(p):
        for r in roles(e):prev[i,r]=cur[r];prev_event[i,r]=last[r];cur[r]=e[4] if e[0]=='warp' else e[2];last[r]=i
    cur=c['final'][:];last=[None]*632
    for i in reversed(range(len(p))):
        e=p[i]
        for r in roles(e):nxt[i,r]=cur[r];nxt_event[i,r]=last[r];cur[r]=e[3] if e[0]=='warp' else e[2];last[r]=i
    labels={s:i for i,s in enumerate(spans)}
    def label(b):
        s=F.span(b)
        if s not in labels:labels[s]=len(spans);spans.append(s);dims.append(len(b));c['frames'].append(b)
        return labels[s]
    t=1-.00302016597705;val=[0.]+[r**t for r in range(1,10)];count=Counter();nominees=[];best=0.
    for i,e in enumerate(p):
        if e[0]!='warp' or e[2]<0:continue
        if any(j!=i and (dims[p[j][3]] not in (0,9) or dims[p[j][4]]!=dims[p[j][3]]) for j in occurrences[e[2]]):continue
        count['free_warp_occurrences']+=1
        r=e[1][1];j,k=prev_event[i,r],nxt_event[i,r]
        if j is None or k is None or p[j][0]!='scalar' or p[k][0]!='scalar' or len(roles(p[j]))!=2 or len(roles(p[k]))!=2:continue
        o1=next(x for x in roles(p[j]) if x!=r);o2=next(x for x in roles(p[k]) if x!=r)
        if o1==o2:continue
        count['windows']+=1;L=prev[j,r];H=nxt[k,r];qstat={}
        a=complete_interval(spans,dims,c['frames'],(L,prev[j,o1]),(nxt[j,o1],),qstat,max_gap=5)
        b=complete_interval(spans,dims,c['frames'],(prev[k,o2],),(H,nxt[k,o2]),qstat,max_gap=5)
        count.update(qstat)
        if qstat.get('skipped_large_interval'):continue
        old=Counter()
        for x,y in [(L,p[j][2]),(p[j][2],e[3]),(e[4],p[k][2]),(p[k][2],H),(prev[j,o1],p[j][2]),(p[j][2],nxt[j,o1]),(prev[k,o2],p[k][2]),(p[k][2],nxt[k,o2])]:
            if dims[y]>dims[x]:old[dims[y]-dims[x]]+=1
        oldv=sum(n*val[z] for z,n in old.items())
        for fa in a:
            for fb in b:
                count['frame_pairs']+=1
                if dims[fa]>dims[fb]:continue
                new=Counter()
                # The chosen output is any dim(fa)-subspace of fb.
                increments=[dims[fa]-dims[L],dims[fb]-dims[fa],dims[H]-dims[fb],dims[fa]-dims[prev[j,o1]],dims[nxt[j,o1]]-dims[fa],dims[fb]-dims[prev[k,o2]],dims[nxt[k,o2]]-dims[fb]]
                F.need(min(increments)>=0,'All complete charged edge ranks nonnegative')
                for d in increments:
                    if d:new[d]+=1
                gain=oldv-sum(n*val[z] for z,n in new.items())
                if gain>best+1e-11:
                    best=gain;outbasis=c['frames'][fb][:dims[fa]];fo=label(outbasis)
                    G=matching_map(c['frames'][fa],outbasis)
                    row={'warp_event':i,'before_scalar':j,'after_scalar':k,'role':r,'operator':e[2],
                         'old_frames':[p[j][2],e[3],e[4],p[k][2]],'new_frames':[fa,fa,fo,fb],
                         'new_G_columns':G,'old_local_paid':dict(old),'new_local_paid':dict(new),'moment_reduction':gain}
                    nominees.append(row);print('NOMINEE',json.dumps(row),flush=True)
    record={'status':'DISCOVERY_ONLY','counts':dict(count),'best_gain':best,'nominees':nominees,'seconds':time.monotonic()-start}
    (HERE/'FREE-G-SCREEN.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in record.items() if k!='nominees'},sort_keys=True))
    if not nominees:return
    best=nominees[-1];altered={}
    for direction,word in programs.items():
        raw=[deepcopy(e) for e in word if e[0]!='climb'];fa,inp,out,fb=best['new_frames']
        raw[best['before_scalar']][2]=fa;raw[best['after_scalar']][2]=fb;raw[best['warp_event']][3:5]=[inp,out]
        altered[direction]=synthesize(c,raw)
    for w in c['warps']:
        if w['op']==best['operator']:w['G_columns']=best['new_G_columns']
    prof={d:Counter(e[5] for e in word if e[0]=='climb') for d,word in altered.items()}
    for d,word in altered.items():prof[d].update(e[4] for e in word if e[0]=='center')
    F.need(prof['forward']==prof['backward'],'Equal complete dual paid profiles');best['paid']=dict(prof['forward'])
    (HERE/'CANDIDATE.json').write_text(json.dumps(best,indent=2,sort_keys=True)+'\n')
    (HERE/'CANDIDATE-WORD.json.gz').write_bytes(gzip.compress(json.dumps({'canonical':c,'programs':altered},sort_keys=True,separators=(',',':')).encode(),mtime=0))
    print('CANDIDATE',json.dumps(best,sort_keys=True))


if __name__=='__main__':main()
