#!/usr/bin/env python3
"""Universal exact affine-adapter compiler for the H6 source-line/cap word.

The recipe family covers every indexed edge without materializing the edge
stream. Orthogonal completion and the mod4 weight identity fix phases.
"""
from pathlib import Path
from collections import Counter
import hashlib, importlib.util, json, sys
import numpy as np

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('physical_sample_compiler',HERE/'compile.py')
sample=importlib.util.module_from_spec(spec);spec.loader.exec_module(sample)
ce=sample.ce;need=sample.need;H=17;E=(1<<H)-1

def dot(a,b):return (a&b).bit_count()&1

def completion(fixed,n=H):
    """Deterministic orthonormal basis, with specified fixed vectors last."""
    fixed=tuple(map(int,fixed));chosen=list(fixed)
    need(all(v>0 and v<(1<<n) and dot(v,v)==1 for v in chosen),'norm-one fixed vectors')
    need(all(dot(a,b)==0 for i,a in enumerate(chosen) for b in chosen[i+1:]),'fixed vectors orthogonal')
    char=(1<<n)-1
    for v in chosen:char^=v
    need(len(chosen)==n or char!=0,'remaining form is alternating')
    rest=[]
    while len(chosen)<n:
        dimension=n-len(chosen);projected=[]
        for bit in range(n):
            v=1<<bit
            for old in chosen:
                if dot(1<<bit,old):v^=old
            if v:projected.append(v)
        candidate=next((v for v in projected if dot(v,v) and (dimension==1 or v!=char)),None)
        if candidate is None:
            # If only char among spanning projected vectors is odd, add any
            # nonzero even vector to it; such a vector exists for dimension>1.
            odd=next((v for v in projected if dot(v,v)),None)
            even=next((v for v in projected if not dot(v,v)),None)
            need(dimension>1 and odd==char and even is not None,'nonalternating completion fallback')
            candidate=odd^even
        need(dot(candidate,candidate)==1 and all(dot(candidate,v)==0 for v in chosen),'new orthonormal column')
        chosen.append(candidate);rest.append(candidate);char^=candidate
        need(len(chosen)==n or char!=0,'completion must retain nonalternating complement')
    columns=tuple(rest)+fixed;rows=ce.transpose(columns,n)
    need(ce.inv(rows,n)==ce.transpose(rows,n),'orthogonal matrix inverse')
    return rows

def affine(rows,offset=0):return {'matrix_rows':list(rows),'offset':int(offset)}

def phase_translation(rows):
    need(all(row.bit_count()%2 for row in rows),'orthogonal rows have odd norm')
    return sum((((row.bit_count()-1)//2)&1)<<i for i,row in enumerate(rows))

def residual_recipe(fixed,n=H):
    """F product(C_v^-1) for orthonormal fixed noncharacteristic columns."""
    G=completion(fixed,n);Gi=ce.transpose(G,n);b=phase_translation(G)
    return {'rank':n-len(fixed),'left':affine(G),'right':affine(Gi,ce.mv(Gi,b)),
            'orthogonal_rows':list(G),'phase_translation':b,'fixed_columns':list(fixed)}

def rankone_recipe(p,n=H):
    G0=completion((p,),n);cols=ce.transpose(G0,n)
    G=ce.transpose((cols[-1],)+cols[:-1],n)
    return {'rank':1,'left':affine(G),'right':affine(ce.transpose(G,n)),
            'orthogonal_rows':list(G),'phase_translation':0,'fixed_columns':[p]}

def center_recipe(inverse=False,n=H):
    I=tuple(1<<i for i in range(n))
    return {'rank':n,'left':affine(I),'right':affine(I,(1<<n)-1 if inverse else 0),
            'phase_translation':(1<<n)-1 if inverse else 0,'fixed_columns':[]}

def inverse_recipe(rec,n=H):
    l,r=rec['left'],rec['right'];li=ce.inv(tuple(l['matrix_rows']),n);ri=ce.inv(tuple(r['matrix_rows']),n)
    # C_[r]^-1=C_[r] X_[r] exactly; no untracked global scalar.
    return {'rank':rec['rank'],'left':affine(ri,ce.mv(ri,r['offset'])),
      'right':affine(li,ce.mv(li,l['offset'])^((1<<rec['rank'])-1))}

def decode(rec,n=H):
    def a(x):return ce.perm(n,tuple(x['matrix_rows'])).then(ce.xgate(n,x['offset']))
    return a(rec['right']).then(ce.fourier(n,range(rec['rank']))).then(a(rec['left']))

def verify_symbolic(rec,n=H):
    G=tuple(rec['orthogonal_rows']);need(ce.inv(G,n)==ce.transpose(G,n),'orthogonality receipt')
    b=phase_translation(G)
    # Degree<=2 mod4 weight polynomial: diagonal coefficients and every
    # offdiagonal coefficient. Orthogonal rows make all offdiagonals vanish.
    need(all((row.bit_count()-1)%4==2*((b>>i)&1) for i,row in enumerate(G)),'weight linear coefficients')
    need(all((G[i]&G[j]).bit_count()%2==0 for i in range(n) for j in range(i+1,n)),'weight quadratic coefficients')
    return True

def main():
    ce.Op.zero_state=sample.accelerated_zero_state
    sys.path.insert(0,str(ROOT/'research/niemeier-lattices/code'))
    import e8_cubed as geo
    roots,_,shell,profiles=geo.construct_shell();P=shell[(profiles&4)==0,:16].astype(np.int64)
    _,packed,_=geo.binary_labels(roots,P);labels=sorted(map(int,np.unique(packed)))
    need(len(P)==30960 and len(labels)==14670,'actual port/label census')
    need(all(p!=E and dot(p,p)==1 for p in labels),'all endpoints noncharacteristic and norm-one')
    # Full endpoint census checks completion for every actual label (each
    # recipe is derivable from its address by the fixed finite algorithm).
    endpoints=0
    for p in labels:
        rec=residual_recipe((p,));verify_symbolic(rec);endpoints+=1
    # Pair properties include actual labels and the full fixed-column Gram.
    pair_checks=[]
    for j in range(512):
        p=labels[(37*j+3)%len(labels)]
        t=next(labels[(53*j+k)%len(labels)] for k in range(len(labels)) if dot(p,labels[(53*j+k)%len(labels)])==0)
        rec=residual_recipe((p,t));verify_symbolic(rec)
        need(ce.rank([x for x,z,q in decode(rec).tab[H:]])==15,'actual middle minimal rank')
        pair_checks.append([p,t])
    F=ce.fourier(H);I=ce.ident(H);actual=[];recipes=[]
    for target,wanted in ((0,1),(0,3),(287,1)):
        s=int(np.flatnonzero((P@P[target])//4==wanted)[0]);p,t=int(packed[s]),int(packed[target])
        A=ce.cgate(H,p);B=ce.cgate(H,t).adjoint().then(F)
        entries=[('zero_to_line',rankone_recipe(p),A),
          ('line_to_cap',residual_recipe((p,t)),A.adjoint().then(B)),
          ('cap_to_full',rankone_recipe(t),B.adjoint().then(F)),
          ('source_tail',residual_recipe((p,)),A.adjoint().then(F)),
          ('target_climb',residual_recipe((t,)),B)]
        chain=I
        for name,rec,definition in entries:
            decoded=decode(rec);need(sample.equal_exact(decoded,definition),'universal exact phase recipe')
            need(ce.rank([x for x,z,q in definition.tab[H:]])==rec['rank'],'minimal rank')
            # Independent differential comparison with the pinned Bruhat compiler.
            prior,lowered=ce.lower_child(definition)
            need(prior['rank']==rec['rank'] and sample.equal_exact(decoded,lowered),'pinned lowering differential phase test')
            inv=inverse_recipe(rec);need(sample.equal_exact(decode(inv),definition.adjoint()),'exact inverse recipe')
            recipes.append(dict(name=name,source=s,target=target,**rec))
            if name in ('zero_to_line','line_to_cap','cap_to_full'):chain=chain.then(decoded)
        need(sample.equal_exact(chain,F),'universal helper full residual')
        actual.append(dict(source=s,target=target,pairing=wanted,source_address=p,target_address=t))
    for inv in (False,True):
        rec=center_recipe(inv);expected=F.adjoint() if inv else F
        need(sample.equal_exact(decode(rec),expected),'coordinate center recipe exact phase')
        recipes.append(dict(name='K_private_descent' if inv else 'K_center_ascent',**rec))
    import copy
    mutant=copy.deepcopy(recipes[1]);mutant['right']['offset']^=1
    need(not sample.equal_exact(decode(mutant),decode(recipes[1])),'phase translation mutation accepted')
    # Characteristic p is precisely the excluded extension obstruction.
    rejected=False
    try:residual_recipe((E,))
    except ValueError:rejected=True
    need(rejected,'characteristic source gate accepted by orthogonal extension')
    raw=json.dumps(dict(h=H,recipes=recipes),sort_keys=True,separators=(',',':')).encode()+b'\n'
    (HERE/'UNIVERSAL-RECIPES.json').write_bytes(raw)
    inputs=['research/niemeier-lattices/code/e8_cubed.py','research/split-centres-global/vendor/clifford_exact.py',
      'research/h6-compensation-network/physical_compiler/compile.py',
      'research/h6-compensation-network/physical_compiler/universal.py','research/h6-compensation-network/routes/BUCKETED-SCHEMA.json']
    result=dict(status='PASS_UNIVERSAL_H6_AFFINE_TRANSITION_FAMILY',h=H,ports=len(P),unique_labels=len(labels),
      characteristic_labels=0,full_endpoint_completion_checks=endpoints,pair_property_checks=len(pair_checks),
      pair_property_sha256=hashlib.sha256(json.dumps(pair_checks,separators=(',',':')).encode()).hexdigest(),
      phase_verified_actual_edges=actual,full_phase_and_signed_tableau_recipes=len(recipes),
      recipe_sha256=hashlib.sha256(raw).hexdigest(),negative_controls=['wrong affine phase translation','characteristic endpoint obstruction'],
      coverage='Every indexed line/cap compensation transition and source/target/K-center transition in the declared full-edge and bucketed schemas, by the proven finite recipe family.512 pair instances and all14670 endpoint instances checked;17 physical recipes differential tested.',
      adapter_bound=dict(affine_moves_per_positive_rank_transition=2,unit_phase_factors=0,
        explicit_translation_xors_per_forward_transition_at_most=1,
        explicit_translation_xors_per_inverse_transition_at_most=2,complex_coordinates_per_move=131072,
        scalar_real_component_moves_per_transition_at_most=4*131072,
        inverse_scope='Inverse recipes remain two affine monomials; translations combine with their permutation. No extra Fourier child or unit-phase factor.'),
      scope='Full finite local phase compiler family, not a materialized billion-event physical tape, integrated bank compiler, precision/all-size transfer or admitted supplier.',
      source_hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs})
    (HERE/'UNIVERSAL-RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],endpoints,len(pair_checks),len(recipes))

if __name__=='__main__':main()
