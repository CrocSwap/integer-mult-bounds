#!/usr/bin/env python3
"""Two adjacent bit invocations with shared physical data wires.

The third tensor factor stays on its fixed line. Candidate frames may mix
the first two factors. All outer data and auxiliary boundaries are fixed.
This is a bounded search, not an all-matrix fusion impossibility theorem.
"""
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations
from math import comb
from pathlib import Path
from hashlib import sha256
import json

from audit_joint_frames import (eye,zero,matrix,add,sub,scale,rank,paired_invocation)
from audit_cancellation import line_projection
from paired_network import circuit
from certify import require,verify_sources
from prepare_layers import serializable
from rational_span_frames import basis,join


def kron(A,B):
    return tuple(tuple(x*y for x in a for y in b) for a in A for b in B)


def local_events(h):
    """Forward gates, common frames, physical local roles and XOR operations."""
    original=paired_invocation(h)
    c=circuit(h);code=c.compile();v=len(c.inputs);R=code['roles']
    sources={t:[] for t in c.inputs};outputs={t:[] for t in c.inputs}
    for t,s in code['sources'].items():sources[t].append(2*v+s)
    for (_,t),s in code['outputs'].items():outputs[t].append(2*v+s)
    events=[]
    for step,op in enumerate(('L','J','Li','R','V','G','R','L','J','Li','G','V')):
        if op in ('L','Li'):
            gates=code['gates'] if op=='L' else reversed(code['gates'])
            for node,ins,outs in gates:
                ops=[(2*v+ins[0],2*v+s) for s in ins[1:]]
                ops += [(2*v+s,2*v+ins[0]) for s in outs[1:]]
                if op=='Li':ops.reverse()
                events.append(((step,node),[2*v+s for s in set(ins+outs)],
                               original['frames'][step,node],ops))
        elif op in ('V','J'):
            for j,t in enumerate(c.inputs):
                roles=[j]+sources[t] if op=='V' else [v+j]+outputs[t]
                ops=[(s,j) for s in sources[t]] if op=='V' else [(v+j,s) for s in outputs[t]]
                events.append(((step,j),roles,original['frames'][step,j],ops))
        else:
            centers=list(range(2*v+R,2*v+R+h))
            data=list(range(v)) if op=='G' else list(range(v,2*v))
            ops=[(2*v+R+i,j) if op=='G' else (v+j,2*v+R+i)
                 for j,t in enumerate(c.inputs) for i in t]
            events.append(((step,'central'),data+centers,
                           original['frames'][step,'central'],ops))
    return c.inputs,R,events


def stage_pair(h=6,a=(0,1,2),b=(1,2,3)):
    triples,R,events=local_events(h)
    require(a in triples and b in triples,'Missing crossing triples')
    v=len(triples);I=eye(h);Z=zero(h);J=eye(h*h);O=zero(h*h)
    P={t:matrix(line_projection(h,t)) for t in triples}
    E=kron(I,P[b]);D=kron(sub(I,P[a]),I)
    frames={};last={};roles={};edges=[];operations=[];incident={}
    maps=[];terminals={}
    for phase in range(2):
        mapping=[]
        for bank in ('X','Y'):
            for t in triples:
                coords=(t,b) if phase==0 else (a,t)
                key=(bank,)+coords
                if key not in roles:
                    r=len(roles);roles[key]=r
                    incoming=(kron(P[t],P[b]) if bank=='X' else O) if phase==0 else (
                        kron(I,P[t]) if bank=='X' else kron(sub(I,P[a]),P[t]))
                    frames['in',r]=incoming;last[r]=('in',r)
                r=roles[key];mapping.append(r)
                terminals[r]=(E if bank=='X' else kron(sub(I,P[t]),P[b])) if phase==0 else (
                    J if bank=='X' else sub(J,kron(P[a],P[t])))
        for s in range(R+h):
            key=('aux',phase,s);r=len(roles);roles[key]=r;mapping.append(r)
            frames['in',r]=O;last[r]=('in',r);terminals[r]=E if phase==0 else J
        maps.append(mapping)
    for phase in range(2):
        def local_to_global(r):
            if phase==1 and r<2*v:r=(r+v)%(2*v)
            return maps[phase][r]
        sequence=events if phase==0 else reversed(events)
        for name,touched,M,ops in sequence:
            vertex=(phase,)+name
            frames[vertex]=kron(M,P[b]) if phase==0 else add(D,kron(P[a],sub(I,M)))
            for local in sorted(set(touched)):
                r=local_to_global(local)
                edge=(last[r],vertex,r)
                edges.append(edge);last[r]=vertex
            if phase==1:ops=reversed(ops)
            operations.extend((local_to_global(t),local_to_global(s)) for t,s in ops)
    for r,out in terminals.items():
        frames['out',r]=out;edges.append((last[r],('out',r),r))
    for index,(u,w,_) in enumerate(edges):
        for vertex in (u,w):incident.setdefault(vertex,set()).add(index)
    return dict(h=h,m=h*h,v=v,R=R,a=a,b=b,frames=frames,edges=edges,
                operations=operations,roles=roles,maps=maps,incident=incident)


def scalar_check(g):
    bits=[1<<i for i in range(len(g['roles']))];want=list(bits);v=g['v']
    first,second=g['maps']
    for i in range(v):want[first[v+i]] ^= want[first[i]]
    for i in range(v):want[second[i]] ^= want[second[v+i]]
    got=list(bits)
    for target,source in g['operations']:got[target] ^= got[source]
    require(got==want,'Fused scalar map or arbitrary scratch restoration failed')
    for target,source in reversed(g['operations']):got[target] ^= got[source]
    require(got==bits,'Inverse fused map failed')
    return dict(independent_variables=len(bits),two_shared_data_roles=True,
                forward_and_inverse_exact=True,all_auxiliary_inputs_restored=True)


def baseline(g):
    F=g['frames'];result=[]
    for u,v,_ in g['edges']:result.append(rank(sub(F[v],F[u])))
    return result


@lru_cache(maxsize=65536)
def modular_rank(A,prime=101):
    rows=[[int(x.numerator)*pow(int(x.denominator)%prime,-1,prime)%prime for x in row] for row in A]
    n=len(rows);pivot=0
    for j in range(len(rows[0])):
        k=next((i for i in range(pivot,n) if rows[i][j]),None)
        if k is None:continue
        rows[pivot],rows[k]=rows[k],rows[pivot]
        inv=pow(rows[pivot][j],-1,prime)
        rows[pivot]=[(x*inv)%prime for x in rows[pivot]]
        for i in range(pivot+1,n):
            if rows[i][j]:
                c=rows[i][j];rows[i]=[(x-c*y)%prime for x,y in zip(rows[i],rows[pivot])]
        pivot+=1
        if pivot==n:break
    return pivot


def candidate_score(g,base,changes):
    require(all(k in g['frames'] and k[0] in (0,1) for k in changes),
            'Only internal gates may change')
    affected=set().union(*(g['incident'][k] for k in changes))
    matrices=[];old=0
    for e in sorted(affected):
        u,v,_=g['edges'][e];old+=base[e]
        matrices.append(sub(changes.get(v,g['frames'][v]),changes.get(u,g['frames'][u])))
    lower=sum(modular_rank(M) for M in matrices)
    if lower>=old:
        return dict(rank_change_lower_bound=lower-old,improvement_excluded=True,
                    affected_edges=len(affected),method='mod-101 lower bound on rational ranks')
    exact=sum(rank(M) for M in matrices)
    return dict(rank_change=exact-old,improvement_excluded=exact>=old,
                affected_edges=len(affected),method='exact rational ranks')


def directions(g):
    h=g['h'];I=eye(h)
    Pa=matrix(line_projection(h,g['a']));Pb=matrix(line_projection(h,g['b']))
    E=kron(I,Pb)
    # Coordinate conjugation controlled by the other tensor factor. This
    # produces a rank-h projector which is not a single Kronecker product.
    perm=[i*h+(j+i)%h for i in range(h) for j in range(h)]
    entangled=tuple(tuple(E[perm[i]][perm[j]] for j in range(h*h)) for i in range(h*h))
    return dict(crossing_line=kron(Pa,Pb),row_active=E,
                column_active=kron(Pa,I),controlled_conjugate=entangled)


def product_matrix_rank(M,h):
    """Rank of reshuffling: a nonzero Kronecker product has rank one here."""
    return rank(tuple(tuple(M[i*h+j][k*h+l] for j in range(h) for l in range(h))
                      for i in range(h) for k in range(h)))


def overlap_control(h,A,B):
    """Independent exact subspace dimensions, including dependent inputs."""
    A=basis(tuple(A));B=basis(tuple(B))
    unit=[tuple(int(i==j) for i in range(h)) for j in range(h)]
    tensor=lambda x,y:tuple(a*b for a in x for b in y)
    rows=basis(tuple(tensor(x,y) for x in unit for y in B))
    cols=basis(tuple(tensor(x,y) for x in A for y in unit))
    common=basis(tuple(tensor(x,y) for x in A for y in B))
    actual=len(rows)+len(cols)-len(join(rows,cols))
    require(join(rows,common)==rows and join(cols,common)==cols,
            'Shared tensor space is not contained in both sides')
    require(actual==len(common)==len(A)*len(B),'Tensor overlap identity failed')
    return dict(h=h,row_label_span=len(B),column_label_span=len(A),
                row_space=len(rows),column_space=len(cols),intersection=actual)


def small_winner_scaling(h):
    require(h>=6 and h!=9,'Invalid ground size')
    v=comb(h,3);z=3*comb(h-3,2)
    return dict(h=h,erase_one_return=2*(v-h*h),
                crossing_collapse_pair=8*v-4*z-4-4*h*h,
                crossing_collapse_with_seam_lower_bound=8*v-4*z-4-4*h*h-24)


def candidates(g):
    F=g['frames'];triples=list(combinations(range(g['h']),3))
    ia,ib=triples.index(g['a']),triples.index(g['b'])
    A1,C1,A2,C2=(0,5,'central'),(0,6,'central'),(1,6,'central'),(1,5,'central')
    seam=[(0,11,ia),(0,8,ia),(1,8,ib),(1,11,ib)]
    patterns=[('first_A',((A1,-1),)),('first_C',((C1,1),)),
              ('second_A',((A2,-1),)),('second_C',((C2,1),)),
              ('A1_C2',((A1,-1),(C2,1))),('C1_A2',((C1,1),(A2,-1))),
              ('all_four',((A1,-1),(C1,1),(A2,-1),(C2,1)))]
    for name,Q0 in directions(g).items():
        for pattern,terms in patterns:
            changes={k:add(F[k],scale(Q0,c)) for k,c in terms}
            for cross in (False,True):
                proposal=dict(changes)
                if cross:
                    proposal.update({k:add(F[k],scale(Q0,c))
                                     for k,c in zip(seam,(-1,1,-1,1))})
                yield dict(direction=name,pattern=pattern,change_seam=cross),proposal
        # Rank-h changes can remove the entire central return, but the rest
        # of the graph must then pay for the altered data/side incidences.
        changes={A1:sub(F[A1],Q0),C1:sub(F[A1],Q0),
                 A2:add(F[C2],Q0),C2:add(F[C2],Q0)}
        for cross in (False,True):
            proposal=dict(changes)
            if cross:
                proposal.update({k:add(F[k],scale(Q0,c))
                                 for k,c in zip(seam,(-1,1,-1,1))})
            yield dict(direction=name,pattern='collapse_returns',change_seam=cross),proposal


def certificate():
    g=stage_pair();base=baseline(g);F=g['frames']
    scalar=scalar_check(g)
    costs={k:rank(M) for k,M in F.items()}
    positive=[]
    for edge,cost in zip(g['edges'],base):
        u,v,r=edge
        extra=cost-costs[v]+costs[u]
        require(extra>=0,'Negative rank excess')
        if extra:positive.append(dict(tail=u,head=v,role=r,excess=extra))
    require(len(positive)==2*g['h'] and sum(e['excess'] for e in positive)==4*g['h']**2,
            'Unexpected excess outside the central returns')
    require(sum(base)==8684,'Two-invocation baseline changed')
    records=[]
    for description,changes in candidates(g):
        outcome=candidate_score(g,base,changes)
        records.append(description|outcome)
    require(len(records)==64 and sum(not r['improvement_excluded'] for r in records)==6,
            'Changed search outcome requires research review')
    require(min(r.get('rank_change_lower_bound',r.get('rank_change')) for r in records)==-32,
            'Candidate lower-bound minimum changed')
    directions_info={name:dict(rank=rank(M),kronecker_reshuffle_rank=product_matrix_rank(M,g['h']))
                     for name,M in directions(g).items()}
    require(directions_info['controlled_conjugate']['kronecker_reshuffle_rank']>1,
            'Cross-factor direction accidentally remains a product')
    vectors=[tuple(int(i in t) for i in range(g['h']))
             for t in combinations(range(g['h']),3)]
    overlaps=[overlap_control(g['h'],vectors[:q],vectors[-q:]) for q in (1,2,3,5)]
    root=Path(__file__).resolve().parents[1]
    proofs=['scripts/audit_stage_pair.py','docs/research/stage-pair-audit.md']
    return dict(status='BOUNDED TWO-INVOCATION FRAME SEARCH; NO NEW KAPPA',
                upstream_commit=verify_sources(),h=g['h'],ambient_dimension=g['m'],
                scalar=scalar,vertices=len(F),edges=len(base),rank_sum=sum(base),
                signed_rank_sum=sum(base)-sum(e['excess'] for e in positive),
                positive_excess_edges=positive,directions=directions_info,candidates=records,
                improved_candidates=[r for r in records if not r['improvement_excluded']],
                block_overlap_controls=overlaps,
                small_winner_scaling=[small_winner_scaling(h) for h in (6,8,10,40,50)],
                boundary_only_saving_excluded=True,
                shared_component_dimension=1,
                source_sha256={p:sha256((root/p).read_bytes()).hexdigest() for p in proofs},
                scope='Fixed scalar pair and outer cuts; 64 explicit correlated frame assignments at h=6, including nonproduct rank-h changes. Six tiny-size improvements are excluded in the retained positive-deficit range by the written scaling audit. No all-matrix optimum, general fusion obstruction, positive-deficit network or improved multiplication witness is claimed.')


if __name__=='__main__':
    result=certificate()
    root=Path(__file__).resolve().parents[1]
    (root/'certificates/stage-pair-audit.json').write_text(
        json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS two-invocation audit:',len(result['candidates']),'candidates;',
          len(result['improved_candidates']),'local improvements. No new kappa.')
