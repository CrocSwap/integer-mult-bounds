# Copyright 2026 icekylinx. Apache-2.0.
# Prepared with OpenAI GPT-6 Astra and Codex assistance; see NOTICE.
"""Pair-first cube override of the retained PairedTriple recursion."""
from itertools import combinations
from collections import defaultdict
from .interval import IntervalTriple

def cube_values(self,G,groups,out_coarse,one,two,w):
    (a,a2),(b,b2),(c,c2)=[groups[g] for g in G]
    def piece(*points):
        p=tuple(sorted(points))
        if not p:return out_coarse[G]
        if len(p)==1:
            u=p[0];omit=tuple(g for g in G if u not in groups[g]);return one[u][omit]
        if len(p)==2:
            omit=tuple(g for g in G if not set(p)&set(groups[g]));return two[p][omit]
        return w.get(p,0)
    def plane(z):
        val=lambda *p:piece(*(p+(() if z is None else (z,))))
        F=val();Sa,Sa2,Sb,Sb2=[val(x) for x in (a2,a,b2,b)]
        e=lambda u,v:val(u,v)
        FSa,FSa2,FSb,FSb2=[self.add(F,x) for x in (Sa,Sa2,Sb,Sb2)]
        Y1=self.add(FSb,Sa);Y2=self.add(FSa,Sb2)
        Y3=self.add(FSa2,e(a,b2));Y4=self.add(FSb2,e(a,b))
        return {(a2,b2):self.add(e(a2,b2),Y1),(a2,b):self.add(e(a2,b),Y2),
                (a,b2):self.add(Y3,Sb),(a,b):self.add(Y4,Sa2)}
    F=plane(None);V={z:plane(z) for z in (c,c2)}
    return {tuple(sorted((u,v,z))):self.add(F[u,v],V[z][u,v]) for u,v in F for z in (c,c2)}

class CubeTriple(IntervalTriple):
    cube_values=cube_values
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

        result={};cube_cache={}
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
            if len(survivors)==3 and all(len(groups[g])==2 for g in G):
                if G not in cube_cache:cube_cache[G]=self.cube_values(G,groups,out_coarse,one,two,w)
                result[excluded]=cube_cache[G][tuple(sorted(survivors))]
                continue
            if len(survivors)==3:
                a,b,c=survivors
                order=[(),(a,),(b,),(a,b),(c,),(a,c),(b,c),(a,b,c)]
            else:order=[s for k in range(len(survivors)+1) for s in combinations(survivors,k)]
            result[excluded]=self.total([pieces[s] for s in order])
        return result
