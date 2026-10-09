#!/usr/bin/env python3
"""Exact phases for completed cores with physical deferred source gauges.

Completed-core sharing and signed partition: an664 PR128, commit
530588a019b4a74f09180680c9e3961bf649ec89, with OpenAI Codex assistance.
The partition implements Xiande Zhang and Gennian Ge (2010).
Generalized gauge/physical-reuse composition and this independent audit were
prepared for eumemic with OpenAI Codex assistance. Apache-2.0.
The one-child nondegenerate Gauss normal form remains the inherited PR104
interface; finite phase verification does not establish its all-size compiler.
"""
from pathlib import Path
from itertools import combinations
from collections import Counter
from hashlib import sha256
import json,sys
assert not sys.flags.optimize, 'Assertions must remain enabled'
HERE=Path(__file__).resolve().parent
PARTITION_PIN='9117d3f010354fa2f32d5c5fb324b280977e82e76060a70a867767a90989ccaa'
UNITS=((1,0),(0,1),(-1,0),(0,-1))

def canonical(vectors):
    piv={}
    for x in vectors:
        for j in sorted(piv,reverse=True):
            if x>>j&1:x^=piv[j]
        if x:
            j=x.bit_length()-1
            for k in piv:
                if piv[k]>>j&1:piv[k]^=x
            piv[j]=x
    return tuple(piv[j]for j in sorted(piv,reverse=True))

def inventory_digest(inventory):
    return sha256(json.dumps(inventory,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def validate_inventory(inventory,R,h):
    seen=set();counts=Counter()
    for row in inventory:
        assert set(row)=={'basis','count'}, 'Source inventory fields'
        B=row['basis'];n=row['count']
        assert isinstance(B,list) and all(type(x)is int and 0<x<(1<<h)for x in B), 'Source inventory vectors'
        assert type(n)is int and n>0, 'Source inventory multiplicity'
        F=canonical(B)
        assert tuple(B)==F and F not in seen, 'Canonical distinct source inventory'
        seen.add(F);counts[F]=n
        assert len(F)<h, 'Completed core must retain a positive active space'
    assert inventory==[dict(basis=list(F),count=n)for F,n in sorted(counts.items(),key=lambda item:(len(item[0]),item[0]))], 'Source inventory ordering'
    assert sum(counts.values())==R, 'Physical source inventory role count'
    return counts

def dot(x,y):return (x&y).bit_count()&1

def multiply(a,b):return(a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])

def power(a,n):
    out=(1,0)
    while n:
        if n&1:out=multiply(out,a)
        a=multiply(a,a);n>>=1
    return out

def orthogonal_blocks(frame):
    pool=list(frame);blocks=[]
    while pool:
        k=next((j for j,x in enumerate(pool)if dot(x,x)),None)
        if k is not None:
            a=pool.pop(k);blocks.append((a,))
            pool=[x^(a if dot(x,a)else 0)for x in pool]
        else:
            a=pool.pop(0);k=next((j for j,b in enumerate(pool)if dot(a,b)),None)
            assert k is not None, 'Degenerate physical source frame'
            b=pool.pop(k);blocks.append((a,b))
            pool=[x^(a if dot(x,b)else 0)^(b if dot(x,a)else 0)for x in pool]
        assert len(canonical(pool))==len(pool)
    assert canonical(x for block in blocks for x in block)==frame
    for i,A in enumerate(blocks):
        for B in blocks[i+1:]:assert all(not dot(x,y)for x in A for y in B)
    return blocks

def project(x,blocks):
    out=0
    for block in blocks:
        if len(block)==1:out^=block[0]if dot(x,block[0])else 0
        else:
            a,b=block;out^=(a if dot(x,b)else 0)^(b if dot(x,a)else 0)
    return out

def gauss(blocks,sign):
    out=(1,0)
    for block in blocks:
        vs=[0,block[0]]if len(block)==1 else[0,block[0],block[1],block[0]^block[1]]
        vals=[UNITS[sign*x.bit_count()%4]for x in vs]
        z=(sum(x for x,y in vals),sum(y for x,y in vals))
        assert z in (((1,1),(1,-1))if len(block)==1 else((2,0),(-2,0)))
        out=multiply(out,z)
    return out

def audit(local,reflection,partition):
    h=local['h'];R=local['R'];assert h==24 and R==26597
    inventory=local['physical_auxiliary_source_frames']
    counts=validate_inventory(inventory,R,h)
    assert reflection['physical_auxiliary_source_frames']==inventory, 'Reflection source inventory binding'
    for field in ('completed_core_source_inventory_bound','completed_core_pre_exterior_frames_full','reflected_core_active_frames_complement_source','exact_birth_cut_invariants','physical_aliased_numeric_replay','exact_arbitrary_dirty_cancellation_by_dependency_cut'):
        assert reflection[field]is True, 'Completed-core interface: '+field
    assert reflection['R']==R and reflection['child_multiplicities']==local['child_multiplicities'], 'Reflection local profile binding'
    trip=list(combinations(range(h),3));masks=[sum(1<<i for i in T)for T in trip]
    assert sorted(t for G in partition['groups']for t in G)==list(range(len(trip))), 'Outer label coverage'
    tests=[0]+[1<<i for i in range(h)]+[(1<<i)|(1<<j)for i,j in combinations(range(h),2)]
    records=[];normalphases=Counter();wrong_sign_found=False
    for frame,count in counts.items():
        blocks=orthogonal_blocks(frame);rank=len(frame)
        columns=[project(1<<i,blocks)for i in range(h)]
        assert canonical(columns)==frame and all(project(x,blocks)==x for x in frame)
        assert all(dot(columns[i],1<<j)==dot(columns[j],1<<i)for i in range(h)for j in range(h))
        for x in tests:
            u=project(x,blocks);e=x^u
            assert project(e,blocks)==0 and not dot(u,e)
            assert (u.bit_count()+e.bit_count()-x.bit_count())%4==0
            assert (u.bit_count()-sum(project(x,[block]).bit_count()for block in blocks))%4==0
            # C_F C_sigma^-1 = C_sigma-perp; the reflected stage has the
            # same positive E phase, not its inverse.
            assert (x.bit_count()-u.bit_count())%4==e.bit_count()%4
            wrong_sign_found|=(-e.bit_count())%4!=e.bit_count()%4
        G=gauss(blocks,-1);z=multiply(G,power((1,-1),rank));den=1<<rank
        assert z[0]%den==z[1]%den==0
        mu=(z[0]//den,z[1]//den);assert mu in UNITS
        assert power(mu,8)==power(mu,24)==(1,0)
        normalphases[UNITS.index(mu)]+=count
        records.append(dict(basis=list(frame),count=count,rank=rank,
            orthogonal_blocks=[list(B)for B in blocks],negative_gauss=list(G),normalform_scalar=list(mu)))
    partial=iter(partition['partial_complement_basis_supports']);sizes=Counter();corrections=Counter()
    for J in partition['groups']:
        B=[masks[t]for t in J];sizes[len(B)]+=1
        if len(B)==24:C=[]
        else:
            supports=next(partial)
            assert len(supports)==16 and all(len(set(S))==len(S)and all(type(i)is int and 0<=i<h for i in S)for S in supports)
            C=[sum(1<<i for i in S)for S in supports]
        Q=B+C
        assert len(Q)==h and all(dot(x,y)==(i==j)for i,x in enumerate(Q)for j,y in enumerate(Q)), 'Signed outer complement basis'
        assert all(x.bit_count()%4==3 for x in B)
        assert not C or Counter(x.bit_count()%4 for x in C)=={1:8,3:8}
        for x in tests:assert (sum(c.bit_count()*dot(x,c)for c in Q)-x.bit_count())%4==0
        for rec in records:
            s=rec['rank'];g=len(B);width=g*s+h*len(C)
            assert width==h*h-g*(h-s)
            scalar=multiply(power(tuple(rec['normalform_scalar']),g),power((0,-1),h*sum(c.bit_count()%4==3 for c in C)))
            assert scalar==(1,0), 'Grouped complement scalar phase'
            if width:corrections[width]+=2*rec['count']
    assert next(partial,None)is None and sizes=={24:83,8:4}
    assert wrong_sign_found, 'Wrong source-sign control must detect a mismatch'
    return dict(status='PASS physical source gauges, exact Gauss phases and signed grouped complements',
        h=h,R=R,source_inventory_sha256=inventory_digest(inventory),physical_auxiliary_source_frames=inventory,
        distinct_frames=len(counts),nonzero_source_roles=sum(n for F,n in counts.items()if F),
        phase_coefficient_points=len(tests),group_sizes=dict(sorted(sizes.items())),
        normalform_scalar_exponents=dict(sorted(normalphases.items())),
        grouped_exterior_histogram=dict(sorted(corrections.items())),
        all_local_projectors_exact=True,all_source_frames_nondegenerate=True,
        all_grouped_complement_scalars_one=True,signed_stage_residuals_equal=True,
        exact_physical_source_inventory_bound=True,wrong_source_sign_rejected=True,
        complement_formula='(sigma tensor span J) orthogonal-sum (F24 tensor (span J)^perp), or transpose',
        complement_width='576-|J|*(24-dim(sigma))',
        paid_normalform='One full residual-width child with paid binary address adapters and quadratic fourth-root phase passes',
        scope='Finite exact frame/projector/Gauss-phase audit and physical core bindings. Residual-to-child, copied-center, endpoint, precision and all-size contracts remain inherited'),records

def main():
    lp=HERE/'complex-profile.json';rp=HERE/'reflection-audit.json';pp=HERE/'inputs/shared-partition.json'
    assert sha256(pp.read_bytes()).hexdigest()==PARTITION_PIN
    local=json.loads(lp.read_text());reflection=json.loads(rp.read_text())
    assert reflection['source_sha256']==sha256((HERE/'complex_deferred.py').read_bytes()).hexdigest()
    assert reflection['audit_sha256']==sha256((HERE/'reflection_audit.py').read_bytes()).hexdigest()
    result,records=audit(local,reflection,json.loads(pp.read_text()))
    result.update(partition_sha256=PARTITION_PIN,local_profile_sha256=sha256(lp.read_bytes()).hexdigest(),
        reflection_receipt_sha256=sha256(rp.read_bytes()).hexdigest(),checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    (HERE/'gauge-phase-audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    (HERE/'gauge-phase-witness.json').write_text(json.dumps(records,sort_keys=True,separators=(',',':'))+'\n')
    print('PASS exact physical gauge sharing',result['R'],result['distinct_frames'],result['nonzero_source_roles'])
if __name__=='__main__':main()
