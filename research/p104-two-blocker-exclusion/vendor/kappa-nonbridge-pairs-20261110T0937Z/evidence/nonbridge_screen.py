"""Exact or directed-upper pricing for initially noncoframed cut-pair retimings."""

from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from pathlib import Path
import gzip
import json
import sys
import time

PREVIOUS = Path(__file__).resolve().parents[2] / 'kappa-contact-release-20261110T0922Z' / 'evidence'
sys.path.insert(0,str(PREVIOUS))
from release import BRACKET, WORD_SHA, bounds, changed_blocks, chart, join, load, subspace_count
from constrained import solve_equalities
from resolve_pair import quotient_domain, volume


def options(event_index, event, model, ignored=None):
    _, dest, source, *_ = event
    lo, hi = 0, model['events']
    for group in (model['writes'].get(str(source),[]), model['reads'].get(str(dest),[])):
        if ignored is not None:
            group=[i for i in group if i!=ignored]
        at = bisect_left(group,event_index)
        assert at==len(group) or group[at]!=event_index
        if at:
            lo=max(lo,group[at-1]+1)
        if at<len(group):
            hi=min(hi,group[at])
    assert lo<=event_index<hi
    timelines=[model['times'][r] for r in (dest,source)]
    cuts={lo,hi+1}
    for t in timelines:
        cuts.update(k for k,_ in t if lo<k<=hi)
    cuts=sorted(cuts)
    return [(l,h-1,tuple(t[bisect_right(t,[l,10**9])-1][1] for t in timelines))
            for l,h in zip(cuts,cuts[1:])]


def propagate(lo,hi,equalities,ordered_paid):
    low,high=lo.copy(),hi.copy()
    while True:
        before=(low.copy(),high.copy())
        for u,v in equalities:
            low[u]=low[v]=join(low[u],low[v])
            high[u]=high[v]=high[u]&high[v]
        for u,v in ordered_paid:
            low[v]=join(low[u],low[v])
        for u,v in reversed(ordered_paid):
            high[u]&=high[v]
        if any(not a<=b for a,b in zip(low,high)):
            return None
        if (low,high)==before:
            return low,high


def screen(word,model,splits,graph,engine,journal,cap,broad=False):
    sequence=word['program']
    model['events']=len(sequence)
    visits=model['visits']
    roots=model['roots']
    root_list=sorted(set(roots))
    root_id={r:i for i,r in enumerate(root_list)}
    component=[root_id[r] for r in roots]
    n=word['public']
    original=[graph.span(word['frames'][visits[r][2]]) if visits[r][2] is not None else None for r in root_list]
    assert all(visits[i][2]==visits[r][2] for i,r in enumerate(roots))
    original_chart={i:chart(s) for i,s in enumerate(original) if s is not None}
    raw_paid=[(u,v) for _,u,v in model['paid'] if visits[u][0]<n]
    raw_target=[(u,v) for _,u,v in model['targets']]
    fixed=model['anchors']
    assert len(raw_target)==1080
    p0=Counter((component[u],component[v]) for u,v in raw_paid)
    t0=Counter((component[u],component[v]) for u,v in raw_target)
    assert sum((original_chart[b][1]-original_chart[a][1])*c for (a,b),c in p0.items())>0
    old_lo,old_hi,_=bounds(original,p0,{component[u] for u in fixed})
    old_state=original_chart | {len(original):None}
    left,right=map(Q,BRACKET)
    weights={r:(engine.raw_margin({r:1},right)[0],engine.raw_margin({r:1},left)[1]) for r in range(1,10)}
    deadline=time.monotonic()+cap
    counts=Counter()
    hits,pending=[],[]
    for split in splits['relaxed']:
        e,f=split['adds']
        if time.monotonic()>=deadline:
            pending.append([e,f])
            continue
        before_e=tuple(model['edges'][str(e)])
        before_f=tuple(model['edges'][str(f)])
        assert e<f and component[before_e[0]]==component[before_f[0]]
        part=set(split['parts'][0]['visits'])
        other=set(split['parts'][1]['visits'])
        root=component[before_e[0]]
        assert part and other and not part&other and all(component[i]==root for i in part|other)
        assert len(part)+len(other)==roots.count(root_list[root])
        assert all((a in part)!=(b in part) for a,b in (before_e,before_f))
        new_id=len(original)
        belong=lambda i:new_id if i in part else component[i]
        old_state[new_id]=original_chart[root]
        paid=Counter((belong(a),belong(b)) for a,b in raw_paid)
        target=Counter((belong(a),belong(b)) for a,b in raw_target)
        space=[*original,original[root]]
        low,high,adj=bounds(space,paid,{belong(i) for i in fixed})
        paid_order=sorted(paid,key=lambda edge:(old_state[edge[0]][1],old_state[edge[1]][1],edge))
        changed={i for i,(a,b) in enumerate(zip(low,high))
                 if i==new_id or (a,b)!=(old_lo[i],old_hi[i])}|{root}
        _,d1,s1,*_=sequence[e]
        _,d2,s2,*_=sequence[f]
        commute=s1!=d2 and s2!=d1
        if broad and commute:
            continue
        ep=options(e,sequence[e],model,f if broad else None)
        fp=options(f,sequence[f],model,e if broad else None)
        if broad and ep==options(e,sequence[e],model) and fp==options(f,sequence[f],model):
            continue
        local_counts=Counter()
        cache={}
        for a,b in product(ep,fp):
            l1,h1,v1=a
            l2,h2,v2=b
            if v1==before_e or v2==before_f:
                local_counts['one original equality retained']+=1
                continue
            cut1,cut2=l1,l2 if commute else max(l1,l2)
            if cut2>h2:
                local_counts['relative order incompatible']+=1
                continue
            if not broad and visits[v1[0]][2]==visits[v1[1]][2] and visits[v2[0]][2]==visits[v2[1]][2]:
                local_counts['both coframed on baseline']+=1
                continue
            equalities=tuple(tuple(sorted(map(belong,v))) for v in (v1,v2))
            key=tuple(sorted(set(equalities)))
            if key in cache:
                local_counts[cache[key]]+=1
                continue
            narrowed=propagate(low,high,key,paid_order)
            if narrowed is None:
                status='weak chart feasibility fails'
            else:
                lo,hi=narrowed
                neighbors=[x.copy() for x in adj]
                touched=set(changed)
                for u,v in key:
                    touched.update((u,v))
                    if u!=v:
                        neighbors[u].add(v)
                        neighbors[v].add(u)
                blocks=changed_blocks(space,low,high,neighbors,target,touched)
                rank_results=[solve_equalities(block,old_state,lo,hi,paid,target,key,weights,True)
                              for block in blocks]
                if any(x.get('infeasible') for x in rank_results):
                    status='rank feasibility fails'
                elif sum(Q(x['upper']) for x in rank_results)<=0:
                    status='rank upper nonpositive'
                else:
                    answers=[]
                    for block in blocks:
                        qs={i:len(hi[i]).bit_length()-len(lo[i]).bit_length() for i in block}
                        sizes={i:sum(subspace_count(d,r) for r in range(d+1)) for i,d in qs.items()}
                        if max(qs.values())>7 or volume({i:range(v) for i,v in sizes.items()},neighbors,750000) is None:
                            answers.append(dict(deferred=True,vertices=block,quotient_dimensions=qs))
                            continue
                        domains={i:quotient_domain(lo[i],hi[i]) for i in block}
                        answers.append(solve_equalities(block,old_state,lo,hi,paid,target,key,weights,False,domains))
                    if any(x.get('infeasible') for x in answers):
                        status='exact chart feasibility fails'
                    elif any(x.get('deferred') for x in answers):
                        status='deferred geometry'
                    else:
                        lower=sum(Q(x['lower']) for x in answers)
                        upper=sum(Q(x['upper']) for x in answers)
                        status=('strict chart nominee' if lower>0 else 'exact upper nonpositive' if upper<=0
                                else 'interval unresolved')
                    if status in ('strict chart nominee','deferred geometry','interval unresolved'):
                        packet=dict(adds=[e,f],cuts=[cut1,cut2],raw_new_contacts=[v1,v2],
                                    constraints=key,split_root=root,split_component=new_id,
                                    split_visits=[visits[i] for i in sorted(part)],
                                    status=status,rank_relaxation=rank_results,exact=answers)
                        hits.append(packet)
                        journal.write(json.dumps(dict(hit=packet),separators=(',',':'))+'\n')
                        journal.flush()
            cache[key]=status
            local_counts[status]+=1
        counts.update(local_counts)
        counts['pairs_checked']+=1
        journal.write(json.dumps(dict(adds=[e,f],counts=local_counts),separators=(',',':'))+'\n')
        journal.flush()
        if counts['pairs_checked']%100==0:
            print(f"checked {counts['pairs_checked']} pairs; latest {e},{f}",file=sys.stderr,flush=True)
    result=dict(word=WORD_SHA,bracket=BRACKET,counts=counts,hits=hits,pending=pending)
    if broad:
        result['scope']='partner removed from both crossing-barrier lists, relative order retained'
    return result


def main(word_path,model_path,splits_path,graph_path,price_path,journal_path,cap,mode=None):
    raw=gzip.decompress(Path(word_path).read_bytes())
    model=json.loads(Path(model_path).read_bytes())
    splits=json.loads(Path(splits_path).read_bytes())
    assert sha256(raw).hexdigest()==WORD_SHA==model['source']==splits['source']
    assert len(splits['relaxed'])==1371
    with Path(journal_path).open('x') as out:
        result=screen(json.loads(raw),model,splits,load('chart_graph',Path(graph_path)),
                      load('directed_price',Path(price_path)),out,int(cap),mode=='--partner-free')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    if not __debug__:
        raise RuntimeError('Assertions are proof checks')
    main(*sys.argv[1:])
