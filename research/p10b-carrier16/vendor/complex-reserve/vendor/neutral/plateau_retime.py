#!/usr/bin/env python3
"""Retimes exact same-frame incidence components, keeping the literal scalar word.
AI-assisted by OpenAI Codex. Research derivative of PR315 complex supplier.
"""
from frame_retime import *

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=pathlib.Path,required=True)
    ap.add_argument('--output',type=pathlib.Path,required=True);ap.add_argument('--passes',type=int,default=20)
    ap.add_argument('--neutral',choices=['none','up','down'],default='none')
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True);begun=time.time()
    raw=args.input.read_bytes();c=json.loads(raw);original=copy.deepcopy(c)
    h,v,R=c['h'],c['v'],c['R'];gs=c['A']+c['B'];n=len(gs);cut=len(c['A'])
    frames=[tuple(f) for f in c['frames']];ids={f:i for i,f in enumerate(frames)}
    gr=[regs(g) for g in gs];prev=[[] for _ in gs];nxt=[[] for _ in gs];last=[-1]*(2*v+R)
    locked=set();ret={s:f for _,s,f in c['ret']}
    for i,rs in enumerate(gr):
        if i==cut:
            for s,f in ret.items():assert gs[last[s]][1]==f;locked.add(last[s])
        for r in rs:prev[i].append(last[r]);last[r]=i
    last=[n]*(2*v+R)
    for i in range(n-1,-1,-1):
        for r in gr[i]:nxt[i].append(last[r]);last[r]=i
    orth={}
    def ann(f):
        if f not in orth:orth[f]=annihilator(f,h)
        return orth[f]
    weight=[1]+[r**r for r in range(1,h+1)]
    def value(k,lo,hi):return math.prod(weight[k-a]*weight[b-k] for a,b in zip(lo,hi))
    edits=[]
    for sweep in range(args.passes):
        parent=list(range(n))
        def find(i):
            while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
            return i
        def union(i,j):
            i,j=find(i),find(j)
            if i!=j:parent[max(i,j)]=min(i,j)
        for i in range(n):
            for j in prev[i]:
                if j>=0 and gs[j][1]==gs[i][1]:union(i,j)
        groups=collections.defaultdict(list)
        for i in range(n):groups[find(i)].append(i)
        changed=0;strict=0;neutral=0
        for root,group in groups.items():
            if any(i in locked for i in group):continue
            before={};after={}
            for i in group:
                for r,j,k in zip(gr[i],prev[i],nxt[i]):
                    if j<0 or find(j)!=root:
                        assert r not in before;before[r]=frames[c['start'][r]] if j<0 else frames[gs[j][1]]
                    if k==n or find(k)!=root:
                        assert r not in after;after[r]=frames[c['final'][r]] if k==n else frames[gs[k][1]]
            assert before.keys()==after.keys()
            rs=sorted(before);lo=[len(before[r]) for r in rs];hi=[len(after[r]) for r in rs]
            lower=basis(x for f in set(before.values()) for x in f)
            upper=ann(basis(x for f in set(after.values()) for x in ann(f)))
            oldid=gs[group[0]][1];old=frames[oldid];d=len(old);assert len(lower)<=d<=len(upper)
            oldp=value(d,lo,hi);newp=oldp;best=old;direction=None
            def hist(k):return collections.Counter(x for a,b in zip(lo,hi) for x in (k-a,b-k) if x)
            oldhist=hist(d)
            for direct,new in [('lower',lower),('upper',upper)]:
                candidate=value(len(new),lo,hi)
                tie=(candidate==oldp==newp and hist(len(new))==oldhist and
                     ((args.neutral=='up' and len(new)>len(best)) or (args.neutral=='down' and len(new)<len(best))))
                if candidate>newp or tie:newp=candidate;best=new;direction=direct
            if best==old:continue
            if best not in ids:ids[best]=len(frames);frames.append(best)
            common=math.gcd(newp,oldp);num,den=newp//common,oldp//common
            edits.append(dict(sweep=sweep,gate_indices=group,roles=rs,old_frame=oldid,new_frame=ids[best],
                              old_rank=d,new_rank=len(best),new_basis=list(best),direction=direction,
                              ratio_num=str(num),ratio_den=str(den),log_gain=math.log(num)-math.log(den),neutral=(num==den)))
            for i in group:gs[i][1]=ids[best]
            changed+=1
            if num==den:neutral+=1
            else:strict+=1
        print(json.dumps(dict(sweep=sweep,components=len(groups),changed_components=changed,strict=strict,neutral=neutral,seconds=time.time()-begun)),flush=True)
        if not changed:break
    c['frames']=[list(f) for f in frames];H={k:collections.Counter() for k in ('x','y','s','c')};cur=c['start'][:]
    def climb(r,f):
        old=cur[r]
        if old==f:return
        assert len(frames[old])<len(frames[f]) and basis(frames[old]+frames[f])==frames[f]
        H['x' if r<v else 'y' if r<2*v else 's'][len(frames[f])-len(frames[old])]+=1;cur[r]=f
    for i,g in enumerate(gs):
        if i==cut:
            for _,s,f in c['ret']:assert cur[s]==f;H['c'][len(frames[f])]+=1
        for r in gr[i]:climb(r,g[1])
    for r,f in enumerate(c['final']):climb(r,f)
    c['blocks']={k:{str(r):val for r,val in sorted(w.items())} for k,w in H.items()}
    assert c['N']==sum(r*val for w in H.values() for r,val in w.items())
    assert scalar_flat(original['A'])==scalar_flat(c['A']) and scalar_flat(original['B'])==scalar_flat(c['B'])
    out=json.dumps(c,separators=(',',':')).encode();(args.output/'candidate.json').write_bytes(out)
    (args.output/'selection.json').write_text(json.dumps(edits,indent=2)+'\n')
    result=dict(status='EXACT_COMPONENT_RETIMING_LABEL_AND_LOCAL_OBJECTIVE_CHECKED',source=str(args.input),source_sha256=digest(raw),
                candidate_sha256=digest(out),components_changed=len(edits),gate_edits=sum(len(x['gate_indices']) for x in edits),
                log_gain=sum(x['log_gain'] for x in edits),old_blocks=original['blocks'],new_blocks=c['blocks'],
                new_frames=len(frames)-len(original['frames']),rank_mass=c['N'],seconds=time.time()-begun)
    result['neutral_direction']=args.neutral;result['strict_components']=sum(not x['neutral'] for x in edits)
    (args.output/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
