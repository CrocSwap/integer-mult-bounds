"""Exact case splitting and coordinate-span propagation for rank-two labels.

No covariance is imposed on labels. Fano automorphisms only identify
isomorphic branches of the unrestricted problem.
"""
from collections import Counter
from itertools import combinations, permutations, product
from pathlib import Path
import argparse
import json
import time
from fractions import Fraction as Q
from noncovariant_search import CLIQUE, TRIPLES, EDGES

INDEX={t:i for i,t in enumerate(TRIPLES)}
ADJ=[0]*len(TRIPLES)
for s,t in EDGES:
    ADJ[INDEX[s]]|=1<<INDEX[t];ADJ[INDEX[t]]|=1<<INDEX[s]


def classes():
    supports={t:sum(1<<i for i,c in enumerate(CLIQUE) if len(set(t)&set(c))!=1)
              for t in TRIPLES if t not in CLIQUE}
    result=[]
    for point in range(7):
        x=supports[(point,7,8)];y=127^x
        xx=[INDEX[t] for t in supports if supports[t]==x]
        yy=[INDEX[t] for t in supports if supports[t]==y]
        assert len(xx)==5 and len(yy)==6
        assert all(ADJ[i]>>j&1 for i in xx for j in yy)
        result.append((xx,yy))
    assert len({i for x,y in result for i in x+y})==77
    return result


def branch_orbits():
    fixed=set(CLIQUE)
    autos=[p for p in permutations(range(7))
           if {tuple(sorted(p[i] for i in c)) for c in CLIQUE}==fixed]
    assert len(autos)==168
    unseen=set(product(range(4),repeat=7));orbits=[]
    while unseen:
        representative=min(unseen);orbit=set()
        for p in autos:
            b=tuple(representative[p[i]] for i in range(7));orbit.add(b)
            orbit.add(tuple(1-x if x<2 else x for x in b))
        assert orbit<=unseen
        unseen-=orbit
        orbits.append((representative,len(orbit)))
    assert sum(size for _,size in orbits)==4**7
    return orbits


def all_cliques():
    out=[]
    def visit(vertices,candidates,neighbors):
        while candidates:
            bit=candidates&-candidates;candidates^=bit;i=bit.bit_length()-1
            group=vertices+(i,);common=neighbors&ADJ[i]
            out.append((group,common))
            visit(group,candidates&ADJ[i],common)
    visit((),(1<<84)-1,(1<<84)-1)
    return out


def initial_supports(branch):
    # Bits 0..6 have weight two; bit 7 is the one-dimensional remainder.
    a=[];b=[]
    for t in TRIPLES:
        if t in CLIQUE:mask=1<<CLIQUE.index(t)
        else:mask=128|sum(1<<i for i,c in enumerate(CLIQUE) if len(set(t)&set(c))!=1)
        a.append(mask);b.append(mask)
    for mode,(xx,yy) in zip(branch,classes()):
        if mode==0:
            for i in xx+yy:a[i]&=127
        elif mode==1:
            for i in xx+yy:b[i]&=127
        elif mode==2:
            for i in xx:a[i]&=127;b[i]&=127
        elif mode==3:
            for i in yy:a[i]&=127;b[i]&=127
        else:raise ValueError(mode)
    return a,b


CAPACITY=[2*(x&127).bit_count()+int(bool(x&128)) for x in range(256)]


def propagate(branch,cliques):
    a,b=initial_supports(branch);changes=[];passes=0
    while True:
        changed=False;passes+=1
        for group,common in cliques:
            for name,source,target in [('A',a,b),('B',b,a)]:
                union=0
                for i in group:union|=source[i]
                required=2*len(group);available=CAPACITY[union]
                if available<required:
                    return {'status':'EXCLUDED_BY_COORDINATE_DIMENSION','branch':branch,'passes':passes,
                            'contradiction':{'side':name,'clique':group,'union':union,
                                             'required_dimension':required,'available_dimension':available},
                            'steps':changes}
                if available==required:
                    candidates=common
                    while candidates:
                        bit=candidates&-candidates;candidates^=bit;j=bit.bit_length()-1
                        removed=target[j]&union
                        if removed:
                            target[j]&=~union;changed=True
                            changes.append({'source_side':name,'clique':group,'target':j,'removed':removed,'span':union})
        if not changed:break
    return {'status':'SURVIVES_SUPPORT_PROPAGATION','branch':branch,'passes':passes,
            'steps':changes,'A_supports':a,'B_supports':b}


def diagonal_elimination(branch,cliques):
    """Exact linear consequence: diagonal entries of saturated clique sums.

    For each of seven two-planes use its block trace divided by two.
    Variables can be signed; no positivity is assumed.
    """
    a,b=initial_supports(branch);bases=[{} for _ in range(7)]
    systems=[[] for _ in range(7)]
    for group,_ in cliques:
        union_a=0;union_b=0
        for i in group:union_a|=a[i];union_b|=b[i]
        saturated=0
        if CAPACITY[union_a]==2*len(group):saturated|=union_a
        if CAPACITY[union_b]==2*len(group):saturated|=union_b
        for slot in range(7):
            if not (saturated>>slot&1):continue
            indices=tuple(i for i in group if a[i]&b[i]&(1<<slot))
            row={i:Q(1) for i in indices};rhs=Q(1)
            source_index=len(systems[slot]);systems[slot].append({'clique':group,'variables':indices})
            combination={source_index:Q(1)};basis=bases[slot]
            while row:
                pivot=min(row)
                if pivot not in basis:
                    scale=row[pivot]
                    basis[pivot]=({i:x/scale for i,x in row.items()},rhs/scale,
                                  {i:x/scale for i,x in combination.items()})
                    break
                br,bb,bc=basis[pivot];scale=row[pivot];rhs-=scale*bb
                for dest,src in [(row,br),(combination,bc)]:
                    for i,x in src.items():
                        value=dest.get(i,Q(0))-scale*x
                        if value:dest[i]=value
                        else:dest.pop(i,None)
            if not row and rhs:
                return {'status':'EXCLUDED_BY_LINEAR_DIAGONALS','slot':slot,
                        'contradiction_rhs':str(rhs),
                        'certificate':[{'coefficient':str(coefficient),**systems[slot][i]}
                                       for i,coefficient in sorted(combination.items())]}
    # Couple the seven block diagonals by trace(P_T)=2. The remainder
    # variable is half its scalar diagonal, so every trace equation has RHS 1.
    joint={};sources=[]
    for slot,basis in enumerate(bases):
        offset=len(sources)
        sources.extend({'type':'saturated_clique','slot':slot,**row} for row in systems[slot])
        for pivot,(row,rhs,combination) in basis.items():
            joint[84*slot+pivot]=({84*slot+i:x for i,x in row.items()},rhs,
                                  {offset+i:x for i,x in combination.items()})
    for t in range(84):
        row={84*slot+t:Q(1) for slot in range(8) if a[t]&b[t]&(1<<slot)}
        rhs=Q(1);source_index=len(sources)
        sources.append({'type':'trace','vertex':t});combination={source_index:Q(1)}
        while row:
            pivot=min(row)
            if pivot not in joint:
                scale=row[pivot]
                joint[pivot]=({i:x/scale for i,x in row.items()},rhs/scale,
                              {i:x/scale for i,x in combination.items()})
                break
            br,bb,bc=joint[pivot];scale=row[pivot];rhs-=scale*bb
            for dest,src in [(row,br),(combination,bc)]:
                for i,x in src.items():
                    value=dest.get(i,Q(0))-scale*x
                    if value:dest[i]=value
                    else:dest.pop(i,None)
        if not row and rhs:
            return {'status':'EXCLUDED_BY_TRACE_COUPLING','contradiction_rhs':str(rhs),
                    'certificate':[{'coefficient':str(coefficient),**sources[i]}
                                   for i,coefficient in sorted(combination.items())]}
    # A witness to consistency of this LINEAR relaxation, not of idempotence.
    values={}
    for pivot,(row,rhs,_) in sorted(joint.items(),reverse=True):
        values[pivot]=rhs-sum(x*values.get(i,0) for i,x in row.items() if i!=pivot)
    return {'status':'SURVIVES_LINEAR_DIAGONALS_AND_TRACE','ranks':[len(b) for b in bases],
            'joint_rank':len(joint),
            'linear_witness':{str(i):str(x) for i,x in sorted(values.items()) if x}}


def run():
    start=time.monotonic();cliques=all_cliques();orbits=branch_orbits();results=[]
    for branch,size in orbits:
        result=propagate(branch,cliques);result['orbit_size']=size
        if result['status']=='SURVIVES_SUPPORT_PROPAGATION':
            result['diagonal_test']=diagonal_elimination(branch,cliques)
        results.append(result)
    counts=Counter(row['status'] for row in results)
    return {'status':'LOCAL NECESSARY-CONDITION AUDIT; NO NEW KAPPA',
            'graph_vertices':84,'graph_edges':1890,'one_coordinate_edges':210,
            'branch_modes':{'0':'A remainder rows vanish on both classes',
                            '1':'B remainder columns vanish on both classes',
                            '2':'Both vanish on the five-label class',
                            '3':'Both vanish on the six-label class'},
            'branch_count':4**7,'orbit_count':len(orbits),'outcomes':dict(counts),
            'linear_outcomes':dict(Counter(row['diagonal_test']['status'] for row in results if 'diagonal_test' in row)),
            'clique_counts':dict(Counter(len(g) for g,_ in cliques)),
            'seconds':time.monotonic()-start,'branches':results,
            'scope':'Exact consequences of the unrestricted dimension-15 rational factor system. Surviving support patterns are not matrix solutions.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=run();args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='branches'},indent=2))
