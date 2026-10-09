"""Cancellation-free weighted triple exclusion by recursively paired points.

Scalar producer for the p=3 five-subset motif and complex disjoint sums. It
generalizes the repository's paired weighted-edge recursion to degree three.
"""
from itertools import combinations
from collections import defaultdict,Counter
import argparse
import json
from paired_exclusion_circuit import PairedExclusionCircuit


class PairedTriple(PairedExclusionCircuit):
    def __init__(self,n,base=4):
        self.n=n;self.base=base
        self.inputs=list(combinations(range(n),3))
        self.variables={s:i+1 for i,s in enumerate(self.inputs)}
        self.support=[0]+[1<<i for i in range(len(self.inputs))]
        self.args=[None]*len(self.support)
        self.lookup={s:i for i,s in enumerate(self.support)}
        results=self.triple(list(range(n)),self.variables)
        self.outputs={s:results[s] for s in self.inputs}
        self.active=set();stack=list(self.outputs.values())
        while stack:
            x=stack.pop()
            if not x or x in self.active:continue
            self.active.add(x)
            if self.args[x]:stack.extend(self.args[x])
        self.additions=sum(self.args[x] is not None for x in self.active)

    def triple(self,pts,w):
        subsets=[s for k in range(4) for s in combinations(pts,k)]
        if len(pts)<=self.base:
            return {s:self.total([v for t,v in w.items() if not set(s)&set(t)]) for s in subsets}
        groups=self.grouping(pts);ng=len(groups)
        group_of={u:i for i,g in enumerate(groups) for u in g}
        coarse_parts=defaultdict(list)
        for t,v in w.items():coarse_parts[tuple(sorted({group_of[u] for u in t}))].append(v)
        coarse={s:self.total(xs) for s,xs in coarse_parts.items()}
        out_coarse=self.triple(list(range(ng)),coarse)
        # Contract one surviving point and aggregate by the other point groups.
        one={}
        for u in pts:
            g=group_of[u];others=[j for j in range(ng) if j!=g]
            pieces=defaultdict(list)
            for t,v in w.items():
                if u not in t:continue
                rest=[a for a in t if a!=u]
                if any(group_of[a]==g for a in rest):continue
                pieces[tuple(sorted({group_of[a] for a in rest}))].append(v)
            coeff={s:self.total(xs) for s,xs in pieces.items()}
            edges={s:coeff.get(s,0) for s in combinations(others,2)}
            weights={j:coeff.get((j,),0) for j in others}
            total,single,pair=self.block(others,edges,weights)
            const=coeff.get((),0)
            one[u]={():self.add(const,total)}
            one[u].update({(j,):self.add(const,x) for j,x in single.items()})
            one[u].update({s:self.add(const,x) for s,x in pair.items()})
        # Contract two surviving points. The remaining degree is at most one.
        two={}
        for u,v in combinations(pts,2):
            i,j=group_of[u],group_of[v]
            if i==j:continue
            others=[k for k in range(ng) if k not in (i,j)]
            vals=[self.total([w.get(tuple(sorted((u,v,a))),0) for a in groups[k]]) for k in others]
            total,leave,_=self.vector([w.get((u,v),0)]+vals,False)
            two[u,v]={():total}|{(k,):x for k,x in zip(others,leave[1:])}

        result={}
        for excluded in subsets:
            E=set(excluded);G=tuple(sorted({group_of[a] for a in E}))
            survivors=[u for i in G for u in groups[i] if u not in E]
            assert len(survivors)<=3
            pieces={():out_coarse[G]}
            for u in survivors:
                omit=tuple(i for i in G if i!=group_of[u])
                pieces[u,]=one[u][omit]
            for u,v in combinations(survivors,2):
                omit=tuple(i for i in G if i not in (group_of[u],group_of[v]))
                pieces[u,v]=two[u,v][omit]
            if len(survivors)==3:pieces[tuple(survivors)]=w.get(tuple(survivors),0)
            if len(survivors)==3:
                a,b,c=survivors
                order=[(),(a,),(b,),(a,b),(c,),(a,c),(b,c),(a,b,c)]
            else:order=[s for k in range(len(survivors)+1) for s in combinations(survivors,k)]
            result[excluded]=self.total([pieces[s] for s in order])
        return result

    def verify(self):
        for s,node in self.outputs.items():
            E=set(s)
            expected=sum(1<<j for j,t in enumerate(self.inputs) if not E&set(t))
            assert self.support[node]==expected,s
        core={0:(1<<self.n)-1};hist=Counter()
        for n in sorted(self.active):
            if self.args[n]:
                a,b=self.args[n]
                assert not self.support[a]&self.support[b]
                assert self.support[n]==self.support[a]|self.support[b]
                core[n]=core[a]&core[b];hist[core[n].bit_count()]+=1
            else:core[n]=sum(1<<i for i in self.inputs[n-1])
        return dict(n=self.n,base=self.base,inputs=len(self.inputs),outputs=len(self.outputs),
                    additions=self.additions,roles=self.additions+len(self.outputs),
                    roles_per_output=(self.additions+len(self.outputs))/len(self.outputs),
                    additions_by_core=dict(hist),all_disjoint_output_coefficients_exact=True,
                    status='SCALAR PRODUCER ONLY; NO COMPLETE NETWORK CLAIM')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('sizes',type=int,nargs='*',default=[6,10,18,26,28]);p.add_argument('--base',type=int,default=4);a=p.parse_args()
    for n in a.sizes:
        c=PairedTriple(n,a.base);print(json.dumps(c.verify(),sort_keys=True),flush=True)
