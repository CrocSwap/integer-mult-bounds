"""Expand the frozen integer pattern flows without a solver or third-party library.

Credit: PR858 physical windows; local promo4 pattern-flow formulation; standard
regular bipartite multigraph decomposition by successive perfect matchings.
Every matching and every integer conservation equation is checked explicitly.
"""
import argparse
from collections import Counter,defaultdict,deque
from common import P,ROOT,read,dump,load,identity,sha

def matching(A):
    n=len(A);left=[-1]*n;right=[-1]*n
    while True:
        distance=[-1]*n;q=deque()
        for u in range(n):
            if left[u]<0:distance[u]=0;q.append(u)
        while q:
            u=q.popleft()
            for v in sorted(A[u]):
                z=right[v]
                if z>=0 and distance[z]<0:distance[z]=distance[u]+1;q.append(z)
        def augment(u):
            for v in sorted(A[u]):
                z=right[v]
                if z<0 or(distance[z]==distance[u]+1 and augment(z)):
                    left[u]=v;right[v]=u;return True
            distance[u]=-1;return False
        count=sum(augment(u) for u in range(n)if left[u]<0)
        if all(v>=0 for v in left):break
        assert count,'Regular bipartite graph has no perfect matching'
    assert sorted(left)==list(range(n)) and all(A[u][v]>0 for u,v in enumerate(left))
    return left

def construct(parent,word,flow,order):
    expected_order=sorted([[s,r]for s in range(9)for r in range(37)],key=lambda k:(37*k[0]+8*k[1],k[0],k[1]))
    assert order==expected_order,'Frozen wave order'
    mod=load(ROOT/'research/complex-t21-owners/vendor/pr870/t16/build_parent.py','original_actual_windows')
    windows,schedule=mod.actual_windows(parent,order)
    original=read(P/'vendor/pr1022/research/gauge44-slots/data/PLAN.json')
    widths=[len(word['frames'][word['final'][h]])-len(word['frames'][word['start'][h]])for h in range(224,224+word['R'])]
    assert Counter(widths)=={4:56,5:32,7:30,8:122,9:240}
    pools=defaultdict(list)
    for t in range(333):
        for h,w in enumerate(widths):pools[t,w].append(h)
    roles=[];seen=set();flow_edges=0;bin_count=0
    for group in flow:
        keys=group['physical_windows'];assert keys and len(keys)==len(set(keys))
        assert not seen.intersection(keys);seen.update(keys)
        cap,times=windows[keys[0]]
        assert all(windows[key]==[cap,times]for key in keys)
        n=len(times);portbase=0
        for pattern in group['patterns']:
            widths_p=pattern['widths'];N=pattern['count'];flows={}
            assert type(N)is int and 0<N<=112*len(keys)
            assert all(type(w)is int and w in (4,5,7,8,9)for w in widths_p)
            assert widths_p==sorted(widths_p) and sum(widths_p)<=cap and len(widths_p)<=n
            for t,w,count in pattern['flow']:
                assert all(type(x)is int for x in (t,w,count))
                assert t in times and w in widths_p and 0<count<=N and(t,w)not in flows
                flows[t,w]=count
            flow_edges+=len(flows)
            counts=Counter(widths_p)
            assert all(sum(flows.get((t,w),0)for t in times)==N*count for w,count in counts.items())
            assert all(sum(flows.get((t,w),0)for w in counts)<=N for t in times)
            if not widths_p:
                assert not flows;portbase+=N;bin_count+=N;continue
            A=[defaultdict(int)for _ in range(n)];row_widths=[]
            for w,count in sorted(counts.items()):
                remaining=[flows.get((t,w),0)for t in times];ti=0
                for _ in range(count):
                    row=len(row_widths);row_widths.append(w);need=N
                    while need:
                        while remaining[ti]==0:ti+=1
                        take=min(need,remaining[ti]);A[row][ti]+=take;remaining[ti]-=take;need-=take
                assert not any(remaining)
            K=len(row_widths);deficit=[N-sum(A[i].get(t,0)for i in range(K))for t in range(n)];ti=0
            assert min(deficit)>=0
            for row in range(K,n):
                need=N
                while need:
                    while deficit[ti]==0:ti+=1
                    take=min(need,deficit[ti]);A[row][ti]+=take;deficit[ti]-=take;need-=take
            assert not any(deficit) and all(sum(row.values())==N for row in A)
            actual=Counter()
            for color in range(N):
                match=matching(A);slots=sorted((times[match[i]],row_widths[i])for i in range(K))
                for i,t in enumerate(match):
                    A[i][t]-=1
                    if not A[i][t]:del A[i][t]
                index,port=divmod(portbase+color,112);owner,child=map(int,keys[index].split(','));offset=0
                for t,w in slots:
                    actual[t,w]+=1;assert pools[t,w];helper=pools[t,w].pop();stage,replica=order[t]
                    roles.append(dict(stage=stage,replica=replica,time=t,helper=helper,width=w,owner_replica=owner,child=child,port=port,offset=offset,copy=112*owner+port,family=896*owner+112*(2*original['pairs'][str(child)]+original['sides'][str(child)])+port))
                    offset+=w
                assert offset==sum(widths_p)
            assert not any(A) and actual==flows
            portbase+=N;bin_count+=N
        assert portbase==112*len(keys)
    assert seen==set(windows) and not any(pools.values()) and len(roles)==159840
    roles.sort(key=lambda z:(z['time'],z['helper']))
    return roles,dict(status='PASS_FROZEN_INTEGER_FLOW_AND_REGULAR_MATCHING',roles=len(roles),bins=bin_count,windows=len(windows),flow_edges=flow_edges,owner_content_sha256=identity(roles),schedule_content_sha256=identity(schedule))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ('parent','word','out'):ap.add_argument('--'+k,type=__import__('pathlib').Path,required=True)
    a=ap.parse_args();out=a.out.resolve();assert not out.exists() and not out.is_relative_to(ROOT);out.mkdir(parents=True)
    roles,receipt=construct(read(a.parent),read(a.word),read(P/'data/FLOW.json.gz'),read(P/'data/ORDER.json'))
    dump(out/'OWNERS.json.gz',roles)
    receipt['inputs']={str(p):sha(p)for p in (a.parent,a.word,P/'data/FLOW.json.gz',P/'data/ORDER.json')}
    dump(out/'CONSTRUCTION.json',receipt);print(receipt['status'],len(roles),flush=True)
if __name__=='__main__':main()
