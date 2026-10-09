#!/usr/bin/env python3
"""Expand deferred readout frames subject to all later target frames.

This changes actual rational frames, preserving the original readout order.
The reverse sweep intersects each slot's admissible start with the frames of
the next read on every affected target. The original sigma is contained in
this intersection, so enlargements preserve all predecessor containments.
Full generic and finite checks are required separately for any winning file.
"""
from collections import Counter
from fractions import Fraction as Q
import gzip
import json
from math import gcd
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
VENDOR=HERE/'vendor';sys.path[:0]=[str(VENDOR/'independent/deferred-readout')]
import check_lifted as cl
import deferred as dr
from linalg import Echelon,Q31,null_exact,rank_mod,rank_exact
from histogram_engine import histogram,float_root


def prim(row):
    row=[Q(x) for x in row];den=1
    for x in row:den=den*x.denominator//gcd(den,x.denominator)
    row=[int(x*den) for x in row];g=0
    for x in row:g=gcd(g,x)
    return [x//g for x in row] if g else row


def gram_rank(B,exact=False):
    sm=list(map(sum,B));M=[[9*sum(x*y for x,y in zip(a,b))-sa*sb for b,sb in zip(B,sm)] for a,sa in zip(B,sm)]
    return rank_exact(M) if exact else rank_mod(M,Q31)


def nondeg(B):return gram_rank(B)==len(B)


def extend_nondeg(old,cap):
    """Enlarge a nondegenerate subspace inside a possibly degenerate cap."""
    want=gram_rank(cap,exact=True);B=[r[:] for r in old]
    while len(B)<want:
        # Testing individual cap vectors, then their pairwise sums, finds an
        # anisotropic direction in every nonzero symmetric residual form.
        # Orthogonal projection to B is implicit in the Gram determinant.
        candidates=cap+[ [x+y for x,y in zip(a,b)] for i,a in enumerate(cap) for b in cap[i+1:] ]
        for r in candidates:
            test=B+[r]
            if rank_mod(test,Q31)==len(test) and nondeg(test):B=test;break
        else:raise AssertionError(('could not reach exact Gram rank',len(B),want))
    assert len(B)==want and nondeg(B)
    return B


def main():
    tic=time.time();W,D=dr.load();S=dr.Schedule(W,D);pr=cl.Prog(W)
    bas,dn=cl.spans(pr);users=cl.users_of(pr,dn);fr=cl.Frames(pr,dn,bas,users);fr.cobases()
    # The separately executed base checker verifies every lifted frame equals
    # U_n. This experiment also checks the equality from frozen dimensions.
    assert all(S.node_dims[n]==S.h-len(fr.K[n]) for n in pr.j)
    annih={};h=S.h
    def constraints(k):
        if k in annih:return annih[k]
        tag=k[0]
        if tag=='v':A=[prim(z) for z in null_exact(S.vstart[k[1]],h)]
        elif tag=='n':
            n=k[1]
            A=([fr.rootcov[fr.rkeys[r]] for r in fr.K[n]] if n in pr.j else
               [prim(z) for z in null_exact([cl.trow(h,pr.trip[i]) for i in bas[n]],h)])
        elif tag=='c':
            n,suffix=k[1:];A=[]
            for j in suffix:
                u=users[n][j];A.extend(constraints(('n',u[1]) if u[0]=='gate' else cl.root_key(u)))
        elif tag in ('out','ret'):A=[fr.rootcov[k]]
        else:raise ValueError(k)
        annih[k]=A;return A
    fullcov=S.adjoint();results={}
    for mode in ('Z','F2'):
        cov=fullcov if mode=='Z' else [{t:n for t,n in C.items() if n%2} for C in fullcov]
        nxt={t:[[9*int(q in T)-3 for q in range(h)]] for t,T in enumerate(S.trip)}
        sigma={};changes=[];deg=0;oldrank=0;degcases=[]
        for s in reversed(S.readout):
            old=S.sigma[s];A=list(constraints(S.start_key(s)))
            for t in cov[s]:A.extend(nxt[t])
            # Every original frame belongs to the new intersection.
            assert all(sum(x*y for x,y in zip(r,a))==0 for r in old for a in A),(mode,s)
            E=Echelon(Q31);selected=[]
            for a in A:
                if E.insert(a):selected.append(a)
            rank=len(selected);assert rank<=h-len(old)
            if rank==h-len(old):
                # Modular independence + old containment proves exact rank.
                B=old;oldrank+=1
            else:
                B=[prim(z) for z in null_exact(selected,h)]
                # Exact annihilation of every input row proves the selected
                # rows span all constraints, independent of modular reductions.
                assert all(sum(x*y for x,y in zip(r,a))==0 for r in B for a in A)
                if not nondeg(B):
                    gr=gram_rank(B);ge=gram_rank(B,exact=True)
                    degcases.append(dict(slot=s,old_dim=len(old),candidate_dim=len(B),gram_rank_mod_q=gr,gram_rank_exact=ge))
                    B=extend_nondeg(old,B);deg+=1
                if len(B)>len(old):changes.append(dict(slot=s,old_dim=len(old),new_dim=len(B)))
            sigma[s]=B
            # This selected basis is an exact annihilator when the dimension
            # changed; for unchanged/fallback frames use their exact nullspace.
            C=selected if len(B)==h-rank else [prim(z) for z in null_exact(B,h)]
            for t in cov[s]:nxt[t]=C
        candidate=dict(D);candidate['sigma']=[sigma[s] for s in D['readout_order']]
        candidate['readout_order']=sorted(S.readout,key=lambda s:(len(sigma[s]),s))
        candidate['sigma']=[sigma[s] for s in candidate['readout_order']]
        c,p=histogram(W,candidate,cov);r=float_root(c)
        path=HERE/('saturated-'+mode+'.json.gz')
        with gzip.open(path,'wt') as f:json.dump(candidate,f,separators=(',',':'))
        row=dict(changed_slots=len(changes),dimension_increase=sum(x['new_dim']-x['old_dim'] for x in changes),
            changes=changes,unchanged_maximal_slots=oldrank,degenerate_fallbacks=deg,
            degenerate_cases=degcases,
            root_float=r,histogram=c,full_physical_qualification=False,
            reason='Exact start/target containment and reverse-sweep nesting verified; generic-pivot and complete frame checks still needed.',
            data_file=str(path));results[mode]=row
        print(mode,{k:v for k,v in row.items() if k not in ('changes','histogram')},flush=True)
    results['seconds']=time.time()-tic
    (HERE/'saturation-results.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__=='__main__':main()
