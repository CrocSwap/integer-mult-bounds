#!/usr/bin/env python3
"""Independent rational audit of the readout-frame mutation; stdlib only.

Imports the pinned lifted-frame reader for 22 start frames only. All matrix
arithmetic, adjoint support and component histogram deltas below are local.
Unaffected frame facts are inherited from the separate baseline audit.
"""
from collections import Counter, defaultdict
from fractions import Fraction as F
import gzip, hashlib, json
from itertools import combinations
from math import comb
from pathlib import Path
import sys, time
HERE=Path(__file__).resolve().parent
R=HERE.parent/'round7-review'

def load(p):
    with gzip.open(p,'rt') as f:return json.load(f)

def echelon(A,n):
    A=[list(map(F,r)) for r in A]; i=0;p=[]
    for j in range(n):
        k=next((k for k in range(i,len(A)) if A[k][j]),None)
        if k is None:continue
        A[i],A[k]=A[k],A[i];q=A[i][j];A[i]=[x/q for x in A[i]]
        for k in range(len(A)):
            if k!=i and A[k][j]:
                q=A[k][j];A[k]=[x-q*y for x,y in zip(A[k],A[i])]
        p.append(j);i+=1
        if i==len(A):break
    return A[:i],p

def null(A,n):
    E,p=echelon(A,n);out=[]
    for j in set(range(n))-set(p):
        r=[F(0)]*n;r[j]=1
        for row,k in zip(E,p):r[k]=-row[j]
        out.append(r)
    return out

def inside(A,B,n):
    E,p=echelon(B,n)
    for row in A:
        r=list(map(F,row))
        for b,j in zip(E,p):
            if r[j]:
                q=r[j];r=[x-q*y for x,y in zip(r,b)]
        if any(r):return False
    return True

def gram(B):
    return [[9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b) for b in B] for a in B]

def determinant(A):
    A=[list(map(F,r)) for r in A];d=F(1)
    for j in range(len(A)):
        k=next((k for k in range(j,len(A)) if A[k][j]),None)
        if k is None:return F(0)
        if k!=j:A[j],A[k]=A[k],A[j];d=-d
        q=A[j][j];d*=q
        for k in range(j+1,len(A)):
            if A[k][j]:
                z=A[k][j]/q
                for l in range(j+1,len(A)):A[k][l]-=z*A[j][l]
                A[k][j]=0
    return d

def inner(r,h):
    return Counter({1:r}) if 2*r<=h else Counter([1]*(h-r)+[2*r-h])

def put(out,A,mult):
    for w,n in A.items():out[w]+=n*mult

def main():
    tic=time.time();original=R/'vendor/certificates/round7/deferred_23.json.gz';candidate=R/'saturated-Z.json.gz'
    O,D=load(original),load(candidate);W=load(R/'vendor/certificates/round7/witness_23.json.gz')
    assert set(O)==set(D)
    untouched=[k for k in O if k not in ('sigma','readout_order')]
    assert all(O[k]==D[k] for k in untouched)
    h=D['h'];trip=list(combinations(range(h),3));tid={t:i for i,t in enumerate(trip)};v=len(trip)
    old=dict(zip(O['readout_order'],O['sigma']));new=dict(zip(D['readout_order'],D['sigma']))
    assert len(old)==len(O['readout_order'])==len(new)==len(D['readout_order']) and set(old)==set(new)
    changed={s for s in old if old[s]!=new[s]};assert len(changed)==22
    assert D['readout_order']==sorted(new,key=lambda s:(len(new[s]),s))
    C=[Counter() for _ in range(D['R'])]
    for s,c,t in D['out']:C[s][tid[tuple(t)]]+=1
    for s,c in D['ret']:
        C[s].update(i for i,t in enumerate(trip) if c in t)
    for op in reversed(D['ops']):
        if op[0]=='add':C[op[2]].update(C[op[1]])
        elif op[0]=='fan':
            for g in op[2]:C[op[1]].update(C[g])
    target=[[] for _ in trip]
    for s in D['readout_order']:
        for t,x in C[s].items():
            if x:target[t].append(s)
    opos={s:i for i,s in enumerate(O['readout_order'])};edges=set();inherited=0
    for seq in target:
        for a,b in zip(seq,seq[1:]):
            if a in changed or b in changed or opos[a]>opos[b]:edges.add((a,b))
            else:inherited+=1
    for a,b in edges:assert inside(new[a],new[b],h),(a,b)
    print('Exact target-edge checks passed:',len(edges),flush=True)
    # Need exact start frames only at the altered slots; no full base audit.
    sys.path[:0]=[str(R/'vendor/independent/deferred-readout')]
    import check_lifted as cl
    import deferred as dr
    pr=cl.Prog(W);bas,dn=cl.spans(pr);users=cl.users_of(pr,dn);fr=cl.Frames(pr,dn,bas,users);fr.cobases();S=dr.Schedule(W,D)
    def ukey(n,k):
        u=users[n][k];return ('n',u[1]) if u[0]=='gate' else cl.root_key(u)
    def exact(k):
        if k[0]=='v':return S.vstart[k[1]]
        if k[0]=='c':
            n,ks=k[1:];A=exact(ukey(n,ks[-1]))
            for i in reversed(ks[:-1]):A=null(null(exact(ukey(n,i)),h)+null(A,h),h)
            return A
        if k[0] in ('out','ret'):return null([fr.rootcov[k]],h)
        n=k[1]
        if n in pr.j:
            assert S.node_dims[n]==h-len(fr.K[n])
            return null([fr.rootcov[fr.rkeys[r]] for r in fr.K[n]],h)
        return [[int(i in pr.trip[t]) for i in range(h)] for t in bas[n]]
    later={s:[] for s in changed}
    for seq in target:
        for a,b in zip(seq,seq[1:]):
            if a in changed:later[a].append(new[b])
        if seq and seq[-1] in changed:
            s=seq[-1];t=next(i for i,seq2 in enumerate(target) if seq2 is seq)
            cov=[9*int(i in trip[t])-3 for i in range(h)];later[s].append(null([cov],h))
    records=[]
    for s in sorted(changed):
        A,B=old[s],new[s];G=gram(B);det=determinant(G);rank=len(echelon(B,h)[0])
        assert rank==len(B) and det and inside(A,B,h)
        start=exact(S.start_key(s));assert inside(B,start,h)
        # The actual subsequent target frames define the saturated cap.
        constraints=null(start,h)
        for L in later[s]:constraints.extend(null(L,h))
        cap=null(constraints,h);gcap=gram(cap);gr=len(echelon(gcap,len(cap))[0])
        assert inside(B,cap,h)
        # Nondegenerate extension cannot exceed rank of the cap's form.
        assert len(B)==gr,(s,len(B),gr)
        for t,x in C[s].items():
            if x:assert all(sum(r[i]*(9*int(i in trip[t])-3) for i in range(h))==0 for r in B)
        records.append(dict(slot=s,old_dim=len(A),new_dim=len(B),new_rank_exact=rank,gram_determinant=str(det),old_contained=True,
            start_contained=True,target_contained=True,cap_dimension=len(cap),cap_gram_rank_exact=gr,maximal_for_fixed_later_frames=True))
    # Recompute histogram delta from exactly the components touched by sigma.
    delta={k:Counter() for k in ('auxiliary','slot_corners','slot_chains','targets')}
    nd=dict(D['node_dims']);ld={(n,tuple(ks)):d for n,ks,d in D['late_dims']};vd=dict(zip(D['vleaf_slots'],map(len,D['vleaf_start'])))
    def startdim(s):
        k=S.start_key(s)
        return vd[s] if k[0]=='v' else nd[k[1]] if k[0]=='n' else ld[k[1],k[2]]
    for s in changed:
        a,b=len(old[s]),len(new[s]);r0,r1=h-a,h-b
        delta['auxiliary'][h*h-2*r0]-=2*v;delta['auxiliary'][h*h-2*r1]+=2*v
        put(delta['slot_corners'],inner(r0,h),-2*v);put(delta['slot_corners'],inner(r1,h),2*v)
        put(delta['slot_chains'],inner(startdim(s)-a,h),-2*v);put(delta['slot_chains'],inner(startdim(s)-b,h),2*v)
    for seq in target:
        for frames,sgn in ((old,-1),(new,1)):
            levels=sorted({0,h-1}|{len(frames[s]) for s in seq})
            for a,b in zip(levels,levels[1:]):put(delta['targets'],inner(b-a,h),sgn*2*v)
    all_delta=Counter()
    for x in delta.values():all_delta.update(x)
    sat=json.loads((R/'saturation-results.json').read_text())['Z'];base=json.loads((R/'qualification.json').read_text())['histogram']
    expected=Counter(dict(sat['histogram']['hist']));expected.subtract(dict(base['hist']))
    assert +all_delta==+expected and +(-all_delta)==+(-expected)
    assert sum(w*n for w,n in all_delta.items())==0
    result=dict(status='PASS',changed_frames=records,changed_count=len(changed),dimension_increase=sum(len(new[s])-len(old[s]) for s in changed),
        schedule_fields_identical=untouched,independent_exact_target_edges_checked=len(edges),inherited_target_edges=inherited,
        independently_recomputed_component_deltas={k:{w:n for w,n in x.items() if n} for k,x in delta.items()},
        total_histogram_delta={w:n for w,n in all_delta.items() if n},preserved_rank=True,
        source_hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (original,candidate)},seconds=time.time()-tic,
        limitations=['Start-frame extraction uses pinned lifted-frame helper; all other matrix arithmetic in this review is local.',
        'Unchanged frame containment and generic pivots inherit separate complete baseline/candidate audits.',
        'Stage-two complementary time reversal and all-size tape/analytic transfer retain upstream proof assumptions.'])
    (HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('changed_frames','source_hashes','independently_recomputed_component_deltas')},indent=2))
if __name__=='__main__':main()
