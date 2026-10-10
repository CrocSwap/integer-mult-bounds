#!/usr/bin/env python3
"""Research only: exact nested-frame retiming of the literal PR315 complex gcert.

Scalar gates, their order, participants/spectators and scatter source cut stay fixed.
For one gate, feasible common frames lie between the join of predecessor frames
and the meet of successor frames. Convexity of sum d log d means an exact local
maximum of the rank-product objective occurs at one of these two endpoints.
AI-assisted by OpenAI Codex, 2026-10-10. Source provenance remains in input package.
"""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
import argparse, collections, copy, gzip, hashlib, importlib.util, json, math, pathlib, time

ROOT=pathlib.Path(__file__).resolve().parent/'vendor/pr315'
SOURCE=ROOT/'inputs/complex/gcert1-p11-cmod-centre-mw-flow.json.gz'

def basis(rows):
    piv={}
    for row in rows:
        while row:
            k=row.bit_length()-1
            if k in piv: row ^= piv[k]
            else:
                piv[k]=row; break
    for k in sorted(piv):
        for j in piv:
            if j>k and (piv[j]>>k)&1: piv[j]^=piv[k]
    return tuple(piv[k] for k in sorted(piv,reverse=True))

def annihilator(rows,h):
    rows=basis(rows)
    piv={r.bit_length()-1:r for r in rows}
    return basis((1<<i) | sum(1<<p for p,r in piv.items() if (r>>i)&1)
                 for i in range(h) if i not in piv)

def regs(g):
    if g[0]=='neg': return [g[2]]
    return [g[2]]+[x[0] for x in g[3]]+(g[4] if g[0]=='out' else [])

def digest(raw): return hashlib.sha256(raw).hexdigest()

def scalar_flat(gs):
    out=[]
    for g in gs:
        if g[0]=='neg': out.append(('neg',g[2]));continue
        for r,a,b in g[3]:out.append((r,g[2],a,b) if g[0]=='out' else (g[2],r,a,b))
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',type=pathlib.Path,required=True)
    ap.add_argument('--passes',type=int,default=1); ap.add_argument('--screen-only',action='store_true')
    ap.add_argument('--split-groups',action='store_true')
    args=ap.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    begun=time.time(); raw=gzip.decompress(SOURCE.read_bytes()); c=json.loads(raw)
    original=copy.deepcopy(c)
    if args.split_groups:
        for phase in ('A','B'):
            expanded=[]
            for g in c[phase]:
                if g[0]=='neg': expanded.append(g);continue
                for term in g[3]:expanded.append([g[0],g[1],g[2],[term]]+([[]] if g[0]=='out' else []))
                if g[0]=='out' and g[4]:expanded.append(['out',g[1],g[2],[],g[4]])
            c[phase]=expanded
    frames=[tuple(f) for f in c['frames']]; frameids={f:i for i,f in enumerate(frames)}
    h,v,R=c['h'],c['v'],c['R']; gates=c['A']+c['B']; n=len(gates); cut=len(c['A'])
    gr=[regs(g) for g in gates]; prev=[[] for _ in gates]; nxt=[[] for _ in gates]
    last=[-1]*(2*v+R); locked=set(); retregs={s:f for _,s,f in c['ret']}
    for i,rs in enumerate(gr):
        if i==cut:
            for s,f in retregs.items():
                assert last[s]>=0 and gates[last[s]][1]==f
                locked.add(last[s])
        for r in rs:
            prev[i].append(last[r]); last[r]=i
    last=[n]*(2*v+R)
    for i in range(n-1,-1,-1):
        for r in gr[i]: nxt[i].append(last[r]); last[r]=i
    orth={}
    def ann(f):
        if f not in orth: orth[f]=annihilator(f,h)
        return orth[f]
    weights=[1]+[r**r for r in range(1,h+1)]
    def localprod(k,lo,hi):
        return math.prod(weights[k-a]*weights[b-k] for a,b in zip(lo,hi))
    candidates=[]; edits=[]; cumulative_num=1; cumulative_den=1
    for sweep in range(args.passes):
        count=0
        for i,g in enumerate(gates):
            if i in locked: continue
            before=[frames[c['start'][r]] if j<0 else frames[gates[j][1]] for r,j in zip(gr[i],prev[i])]
            after=[frames[c['final'][r]] if j==n else frames[gates[j][1]] for r,j in zip(gr[i],nxt[i])]
            old=frames[g[1]]; d=len(old); lo=[len(f) for f in before]; hi=[len(f) for f in after]
            lower=basis(x for f in set(before) for x in f)
            upper=ann(basis(x for f in set(after) for x in ann(f)))
            assert len(lower)<=d<=len(upper)
            oldp=localprod(d,lo,hi); bestp=oldp; best=old; direction=None
            for direct,new in [('lower',lower),('upper',upper)]:
                newp=localprod(len(new),lo,hi)
                if newp>bestp: bestp=newp;best=new;direction=direct
            if bestp==oldp:continue
            common=math.gcd(bestp,oldp); num=bestp//common;den=oldp//common
            item=dict(sweep=sweep,phase='A' if i<cut else 'B',index=i if i<cut else i-cut,
                      global_index=i,old_frame=g[1],old_rank=d,new_rank=len(best),direction=direction,
                      previous_ranks=lo,next_ranks=hi,ratio_num=str(num),ratio_den=str(den),
                      log_improvement=math.log(num)-math.log(den),new_frame_basis=list(best))
            candidates.append(item)
            if not args.screen_only:
                if best not in frameids: frameids[best]=len(frames);frames.append(best)
                g[1]=frameids[best]; item['new_frame']=g[1]; edits.append(item); count+=1
                cumulative_num*=num;cumulative_den*=den
                common=math.gcd(cumulative_num,cumulative_den);cumulative_num//=common;cumulative_den//=common
        print(json.dumps(dict(sweep=sweep,candidates=len(candidates),edits=count,seconds=time.time()-begun)),flush=True)
        if not count: break
    c['frames']=[list(f) for f in frames]
    H={k:collections.Counter() for k in ('x','y','s','c')}; cur=c['start'][:]
    def climb(r,f):
        o=cur[r];delta=len(frames[f])-len(frames[o]);assert delta>=0
        if o!=f:
            assert delta>0 and basis(frames[o]+frames[f])==frames[f]
            H['x' if r<v else 'y' if r<2*v else 's'][delta]+=1;cur[r]=f
    for i,g in enumerate(gates):
        if i==cut:
            for _,s,f in c['ret']: assert cur[s]==f;H['c'][len(frames[f])]+=1
        for r in gr[i]:climb(r,g[1])
    for r,f in enumerate(c['final']):climb(r,f)
    c['blocks']={k:{str(r):val for r,val in sorted(w.items())} for k,w in H.items()}
    assert c['N']==sum(r*val for w in H.values() for r,val in w.items())
    assert scalar_flat(original['A'])==scalar_flat(c['A']) and scalar_flat(original['B'])==scalar_flat(c['B'])
    assert original['ret']==c['ret'] and original['scat']==c['scat']
    out=json.dumps(c,separators=(',',':')).encode();(args.output/'candidate.json').write_bytes(out)
    (args.output/'selection.json').write_text(json.dumps(edits,indent=2)+'\n')
    summary=dict(status='FRAME_SCREEN_ONLY' if args.screen_only else 'EXACT_NESTED_RETIMING_LOCAL_PRICE_IMPROVEMENT',
                 source=str(SOURCE),source_uncompressed_sha256=digest(raw),candidate_sha256=digest(out),
                 candidates=len(candidates),edits=len(edits),locked_gates=len(locked),
                 old_blocks=original['blocks'],new_blocks=c['blocks'],rank_mass=c['N'],
                 log_product_gain=sum(x['log_improvement'] for x in edits),
                 rank_product_ratio_num=str(cumulative_num),rank_product_ratio_den=str(cumulative_den),
                 new_frames=len(frames)-len(original['frames']),seconds=time.time()-begun)
    summary['split_groups']=args.split_groups
    summary['gate_counts']={p:len(c[p]) for p in ('A','B')}
    (args.output/'RESULT.json').write_text(json.dumps(summary,indent=2)+'\n')
    (args.output/'screen.json').write_text(json.dumps(candidates,indent=2)+'\n')
    print(json.dumps({k:val for k,val in summary.items() if k not in ('rank_product_ratio_num','rank_product_ratio_den')},indent=2),flush=True)

if __name__=='__main__':main()
