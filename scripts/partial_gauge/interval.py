# Copyright 2026 icekylinx. Apache-2.0.
# Prepared with OpenAI GPT-6 Astra and Codex assistance; see NOTICE.
"""Cyclic intervals and core-aware pairs, adapted from Avi Eisenberg PR62."""
from pathlib import Path
from itertools import combinations
import sys
from paired_triple_circuit import PairedTriple
from paired_exclusion_circuit import PairedExclusionCircuit

def interval_sums(add,values):
    nz=[(i,x) for i,x in enumerate(values) if x]
    n=len(nz)
    if not n:return 0,[0]*len(values)
    if n==1:
        result=[nz[0][1]]*len(values);result[nz[0][0]]=0
        return nz[0][1],result
    v=[x for _,x in nz];states={(a,1):x for a,x in enumerate(v)}
    for length in range(2,n):
        for a in range(n):states[a,length]=add(states[a,length-1],v[(a+length-1)%n])
    total=add(states[0,n-1],v[-1])
    out=[total]*len(values)
    for j,(i,x) in enumerate(nz):out[i]=states[(j+1)%n,n-1]
    return total,out

class IntervalTriple(PairedTriple):
    def vector(self,values,two=True):
        if two:return super().vector(values,two)
        total,one=interval_sums(self.add,values)
        return total,one,{}

    def block(self,points,edges,weights):
        if len(points)<=2:
            return PairedExclusionCircuit.block(self,points,edges,weights)
        groups=self.grouping(points);ng=len(groups)
        edge=lambda a,b:edges[tuple(sorted((a,b)))]
        coarse={(i,j):self.total([edge(a,b) for a in groups[i] for b in groups[j]])
                for i,j in combinations(range(ng),2)}
        wt={i:self.total([weights[a] for a in g]+[edge(a,b) for a,b in combinations(g,2)])
            for i,g in enumerate(groups)}
        total,outside,far=self.block(list(range(ng)),coarse,wt)
        strips={};sums={}
        for i,g in enumerate(groups):
            other=[j for j in range(ng) if j!=i]
            for a in g:
                carry=self.total([weights[u] for u in g if u!=a])
                vals=[self.total([edge(u,v) for u in g if u!=a for v in groups[j]]) for j in other]
                st,one=interval_sums(self.add,[carry]+vals)
                strips[a]={j:z for j,z in zip(other,one[1:])};sums[a]=st
        out={};single={a:self.add(outside[i],sums[a]) for i,g in enumerate(groups) for a in g}
        for i,g in enumerate(groups):
            for a,b in combinations(g,2):out[a,b]=outside[i]
        for i,j in combinations(range(ng),2):
            if len(groups[i])==len(groups[j])==2:
                (a,a2),(b,b2)=groups[i],groups[j]
                F=far[i,j];Sa,Sa2,Sb,Sb2=strips[a][j],strips[a2][j],strips[b][i],strips[b2][i]
                FSa,FSa2=self.add(F,Sa),self.add(F,Sa2)
                FSb,FSb2=self.add(F,Sb),self.add(F,Sb2)
                Y1=self.add(FSb,Sa);Y2=self.add(FSa,Sb2)
                Y3=self.add(FSa2,edge(a,b2));Y4=self.add(FSb2,edge(a,b))
                out[a,b]=self.add(edge(a2,b2),Y1)
                out[a,b2]=self.add(edge(a2,b),Y2)
                out[a2,b]=self.add(Y3,Sb)
                out[a2,b2]=self.add(Y4,Sa2)
            else:
                for a in groups[i]:
                    left=self.add(far[i,j],strips[a][j])
                    for b in groups[j]:
                        cross=self.total([edge(u,v) for u in groups[i] if u!=a for v in groups[j] if v!=b])
                        out[a,b]=self.add(left,self.add(strips[b][i],cross))
        return total,single,out
