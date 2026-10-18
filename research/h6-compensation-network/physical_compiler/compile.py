#!/usr/bin/env python3
"""Reusable exact h17 transition compiler plus bounded representative receipts.

Uses retained PR425/PR531 Gaussian-dyadic lowering without altering it.
NumPy accelerates literal state evaluation; signed tableaus and whole-state
witnesses jointly determine each exact operator including global phase.
"""
from pathlib import Path
from functools import lru_cache
from collections import Counter
import hashlib, importlib.util, json, sys
import numpy as np

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
CE_PATH=ROOT/'research/split-centres-global/vendor/clifford_exact.py'
spec=importlib.util.spec_from_file_location('physical17_pinned_clifford',CE_PATH)
ce=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ce;spec.loader.exec_module(ce)
original_zero_state=ce.Op.zero_state

def need(ok,message):
    if not ok: raise ValueError(message)

@lru_cache(maxsize=16)
def address_tables(n):
    return np.arange(1<<n,dtype=np.int64),np.array([x.bit_count()&1 for x in range(1<<n)],dtype=np.int64)

@lru_cache(maxsize=16)
def movement(n,rows,offset=0):
    xs,par=address_tables(n)
    return sum(par[xs&r]<<i for i,r in enumerate(rows))^offset

@lru_cache(maxsize=16)
def phases(n,rows,linear):
    xs,_=address_tables(n)
    out=sum(int(a)*((xs>>i)&1) for i,a in enumerate(linear))
    for i in range(n):
        for j in range(i+1,n):
            if rows[i]>>j&1:out+=2*((xs>>i)&1)*((xs>>j)&1)
    return out%4

def exact_state(op,basis=0):
    n=op.n;xs,_=address_tables(n)
    re=np.zeros(1<<n,dtype=np.int64);im=re.copy();re[basis]=1;den=0
    for gate in op.circuit:
        # Each C sum has four terms; this precheck rules out signed-int64 overflow.
        need(max(int(np.abs(re).max()),int(np.abs(im).max()))<2**59,'pre-operation integer guard')
        kind=gate[0]
        if kind=='P':
            idx=movement(n,tuple(gate[1]));a=np.empty_like(re);b=np.empty_like(im)
            a[idx]=re;b[idx]=im;re,im=a,b
        elif kind=='X':re,im=re[xs^gate[1]],im[xs^gate[1]]
        elif kind in ('D','phase'):
            q=phases(n,tuple(gate[1]),tuple(gate[2])) if kind=='D' else np.full(1<<n,gate[1]%4,dtype=np.int64)
            re,im=np.choose(q,[re,-im,-re,im]),np.choose(q,[im,re,-im,-re])
        elif kind=='C':
            j=xs^gate[1];s=gate[2]
            re,im=re-s*im+re[j]+s*im[j],im+s*re+im[j]-s*re[j];den+=1
        else:raise ValueError(gate)
        while den and not np.any((re|im)&1):re//=2;im//=2;den-=1
    return re,im,den

def accelerated_zero_state(self,basis=0):
    a,b,d=exact_state(self,basis);return list(zip(a.tolist(),b.tolist())),d

def equal_exact(a,b):
    if a.tab!=b.tab:return False
    ar,ai,ad=exact_state(a);br,bi,bd=exact_state(b)
    return ad==bd and np.array_equal(ar,br) and np.array_equal(ai,bi)

def monomial(recipe,n):
    return ce.diag(n,tuple(recipe['quadratic_rows']),tuple(recipe['linear_Z4'])).then(
      ce.perm(n,tuple(recipe['matrix_rows']))).then(ce.xgate(n,recipe['offset'])).then(
      ce.Op(n,ce.identity(n),[('phase',recipe['phase'])]))

def decode(recipe,n):
    if recipe['rank']==0:return monomial(recipe['left'],n)
    return monomial(recipe['right'],n).then(ce.fourier(n,range(recipe['rank']))).then(monomial(recipe['left'],n))

def adapter_count(rec,n):
    if rec is None:return dict(unit_phase_factors=0,address_moves=0,rank_zero=True)
    quadratic=sum((int(row)>>(i+1)).bit_count() for i,row in enumerate(rec['quadratic_rows']))
    linear=sum(int(a)%4!=0 for a in rec['linear_Z4']);global_phase=int(rec['phase'])%4!=0
    moved=tuple(rec['matrix_rows'])!=tuple(1<<i for i in range(n)) or rec['offset']!=0
    return dict(unit_phase_factors=quadratic+linear+int(global_phase),
      quadratic_factors=quadratic,linear_factors=linear,global_phase=int(global_phase),
      address_moves=int(moved),rank_zero=True)

def compile_transition(old,new,expected_rank):
    op=old.adjoint().then(new)
    rec,lowered=ce.lower_child(op)
    need(rec['rank']==expected_rank,'minimal Fourier rank differs from frame distance')
    # Decode the serialized integer fields, not the lowerer's returned circuit.
    serialized=json.loads(json.dumps(rec));decoded=decode(serialized,old.n)
    need(equal_exact(op,decoded),'serialized recipe signed tableau or exact global phase mismatch')
    need(equal_exact(lowered,decoded),'lowering return and independent decode differ')
    for side in ('left','right'):
        if rec[side] is not None:
            adapter=monomial(rec[side],old.n)
            need(ce.rank([x for x,z,p in adapter.tab[old.n:]])==0,'adapter has nonzero Fourier rank')
    rec['adapter_counts']={side:adapter_count(rec[side],old.n) for side in ('left','right')}
    rec['signed_pauli_generators_checked']=2*old.n
    rec['global_phase_witness_coordinates']=1<<old.n
    return rec,decoded

def main():
    # First compare accelerated evaluation to literal retained evaluation on small
    # states, covering every primitive and inverses with nontrivial phases.
    small_checks=0
    for n in (2,3,4):
        G=ce.transpose(ce.basis_extend((3,),n),n)
        op=ce.perm(n,G).then(ce.diag(n,tuple(1<<i for i in range(n)))).then(
          ce.fourier(n)).then(ce.xgate(n,1)).then(ce.Op(n,ce.identity(n),[('phase',3)]))
        for candidate in (op,op.adjoint()):
            for basis in (0,(1<<n)-1):
                need(accelerated_zero_state(candidate,basis)==original_zero_state(candidate,basis),'accelerator disagrees with literal exact state')
                small_checks+=1
    ce.Op.zero_state=accelerated_zero_state
    sys.path.insert(0,str(ROOT/'research/niemeier-lattices/code'))
    import e8_cubed as geo
    roots,_,shell,profiles=geo.construct_shell();P=shell[(profiles&4)==0,:16].astype(np.int64)
    _,packed,_=geo.binary_labels(roots,P)
    H=17;F=ce.fourier(H);I=ce.ident(H)
    pairs=[]
    for target,wanted in ((0,1),(0,3),(287,1)):
        values=(P@P[target])//4;source=int(np.flatnonzero(values==wanted)[0])
        pairs.append((source,target,wanted))
    recipes=[];chains=[]
    for source,target,pairing in pairs:
        ps,pt=int(packed[source]),int(packed[target])
        need(ps.bit_count()%2==1 and pt.bit_count()%2==1 and (ps&pt).bit_count()%2==0,'actual norm-one nested endpoints')
        A=ce.cgate(H,ps);B=ce.cgate(H,pt).adjoint().then(F)
        ops=(I,A,B,F);total=I;steps=[]
        for step,r in enumerate((1,15,1)):
            rec,compiled=compile_transition(ops[step],ops[step+1],r)
            rec.update(name=f'helper_{source}_{target}_{step}',source_port=source,target_port=target,transition_step=step)
            recipes.append(rec);steps.append(rec['name']);total=total.then(compiled)
        need(equal_exact(total,F),'helper whole invocation residual differs from exact C17')
        # Source and target chains use the exact inherited norm-one representatives.
        for name,old,new,r in [('source_tail',A,F,16),('target_climb',I,B,16)]:
            rec,compiled=compile_transition(old,new,r)
            rec.update(name=f'{name}_{source}_{target}',source_port=source,target_port=target)
            recipes.append(rec)
        chains.append(dict(source=source,target=target,pairing=pairing,source_address=ps,target_address=pt,
          recipes=steps,whole_invocation_residual='EXACT_C17',endpoint_adapter_count=0,
          exact_endpoint_convention='source=C_p; target=C_p^-1 then F; zero=I; full=F'))
    for name,old,new in [('K_center_ascent',I,F),('K_private_descent',F,I)]:
        rec,compiled=compile_transition(old,new,17);rec.update(name=name);recipes.append(rec)
    # A global unit phase leaves every signed Pauli column unchanged and must
    # still be rejected; a translation tests tableau and state sensitivity.
    import copy
    mutated=copy.deepcopy(recipes[0]);mutated['left']['phase']=(mutated['left']['phase']+1)%4
    need(decode(mutated,H).tab==decode(recipes[0],H).tab,'phase mutant should preserve signed tableau')
    need(not equal_exact(decode(mutated,H),decode(recipes[0],H)),'global phase mutant accepted')
    shifted=copy.deepcopy(recipes[0]);shifted['left']['offset']^=1
    need(not equal_exact(decode(shifted,H),decode(recipes[0],H)),'translation mutant accepted')
    wrongrank=copy.deepcopy(recipes[0]);wrongrank['rank']+=1
    need(not equal_exact(decode(wrongrank,H),decode(recipes[0],H)),'child rank mutant accepted')
    # Reverse-complement residual differs exactly by a charged Pauli X, not
    # merely by equality of frame cosets or binary symplectic matrices.
    Xall=ce.xgate(H,(1<<H)-1)
    need(equal_exact(F.then(F),Xall),'exact F square is not Pauli Xall')
    need(equal_exact(F.adjoint().then(Xall),F),'reverse endpoint reconciliation loses global phase')
    raw=json.dumps(dict(h=H,recipes=recipes,chains=chains),sort_keys=True,separators=(',',':')).encode()
    (HERE/'RECIPES.json').write_bytes(raw+b'\n')
    paths=['notes/general-clifford-frames.tex','research/split-centres-global/vendor/clifford_exact.py',
      'research/niemeier-lattices/code/e8_cubed.py','research/h6-compensation-network/construction/network.py',
      'research/h6-compensation-network/k_encoder/network.py']
    result=dict(status='PASS_REPRESENTATIVE_EXACT_H17_TRANSITION_COMPILER',h=H,
      tested_recipes=len(recipes),tested_helper_chains=len(chains),signed_tableau_columns_per_recipe=34,
      exact_phase_witness_coordinates_per_recipe=131072,literal_acceleration_crosschecks=small_checks,
      tested_rank_histogram=dict(Counter(r['rank'] for r in recipes)),
      adapter_counts_by_recipe={r['name']:r['adapter_counts'] for r in recipes},
      recipe_sha256=hashlib.sha256(raw+b'\n').hexdigest(),negative_controls=['unit global phase','translation','Fourier rank'],
      symbolic_all_transition_adapter_bound=dict(monomials=2,unit_phase_factors_each=171,address_moves_each=1,
        derivation='At most 17*16/2=136 quadratic off-diagonal factors, 17 linear Z4 factors and one global phase: actual h17 total154<=171 conservative retained bound. P and X combine to one binary affine address movement. Diagonal unit Gaussian phases and permutations have Fourier rank zero.'),
      phase_convention='Literal Gaussian dyadics (integer real/imaginary numerators /2^d); i^p X^x Z^z signed generators; C=(1+i)I/2+(1-i)X/2.',
      exact_endpoint_convention='Inherited representatives source C_p and target F C_p^-1; norm-one p; zero I and FULL F. No canonical endpoint adapter is necessary for this convention. F^-1-to-F reconciliation is exact Xall.',
      scope='Reusable exact compiler and17 representative physical recipes. All distinct full-network transitions, bank placement, whole-word routing/literal/tape/precision and all-size supplier transfer remain uncompiled. No fully physical compiled supplier is claimed.',
      source_hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths})
    (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],result['tested_recipes'],result['tested_rank_histogram'])

if __name__=='__main__':main()
