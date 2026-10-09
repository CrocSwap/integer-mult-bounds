#!/usr/bin/env python3
"""Source-bound compact complete PR64 ambient schedule and child-profile correspondence.

The two huge banks are indexed products, not eagerly expanded billions of times.
One verified local word is replicated for each exact fixed triple-line projector.
Tensor identities and fixed controlled-corner index formulas justify replication.
Existing exact CRT and data-corner certificates are reused, never recomputed here.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import subprocess
import forward_local
import reverse_local

PIN='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e'


def require(ok,msg):
    if not ok: raise ValueError(msg)


def digest(path): return sha256(path.read_bytes()).hexdigest()


def pinned_sources(upstream):
    names=['research/copied-fixed/PROOF.md','notes/copied-centers-bit.tex',
           'notes/copied-centers-lemma.tex','research/copied-fixed/verify.py',
           'research/copied-fixed/reversed/pr34/independent_controls.py',
           'research/copied-fixed/reversed/geometry.py','research/copied-fixed/data-corners.json',
           'research/copied-fixed/data_recovery.py']
    records={}
    for name in names:
        raw=subprocess.check_output(['git','show',PIN+':'+name],cwd=upstream)
        require(raw==(upstream/name).read_bytes(),'Changed pinned source: '+name)
        records[name]=sha256(raw).hexdigest()
    return records


def actual_lines(h):
    """Actual rational projectors t*(t^T G/2), and their fixed I+J conjugates."""
    triples=list(combinations(range(h),3)); transcript=sha256()
    for triple in triples:
        t=[int(i in triple) for i in range(h)]
        phi=[Q(3*x-1,6) for x in t]
        require(sum(t[i]*phi[i] for i in range(h))==1,'Actual line projector not idempotent')
        require([Q(x)-Q(sum(t),9) for x in t]==[2*x for x in phi],'Line dual not G-normalized')
        p=[Q(x+3) for x in t]
        dual=[Q(x,2)-Q(5,3*(h+1)) for x in t]
        require(all(p) and all(dual),'Zero fixed-basis corner scale')
        require(sum(p[i]*dual[i] for i in range(h))==1,'Conjugated line projector not idempotent')
        # Exact L*t and phi*L^-1, not just a normalization checksum.
        require(p==[Q(x+sum(t)) for x in t] and
                dual==[x-sum(phi)/Q(h+1) for x in phi],'Wrong I+J conjugation')
        transcript.update(json.dumps([triple,[str(x) for x in p],[str(x) for x in dual]],separators=(',',':')).encode()+b'\n')
    require(h!=9,'Degenerate ambient metric')
    return dict(h=h,triples=len(triples),exact_line_table_sha256=transcript.hexdigest(),
                primal_formula='t+3*1',dual_formula='t/2-5*1/(3(h+1))',
                nonzero_corner_scales_for_every_actual_triple=True)


def controlled_corner():
    """Check index identities for EVERY symbolic matrix entry, without random values."""
    a,b,m,d=23,25,575,47
    rows=list(range(a))+[a-1]+list(range(a))
    cols=list(range(a))+[0]+list(range(a))
    partial=[{} for _ in range(b)]
    for labels,offset in [(rows,0),(cols,m-d)]:
        for k,label in enumerate(labels):
            alpha,beta=divmod(offset+k,b)
            require(alpha not in partial[beta] or partial[beta][alpha]==label,'Conflicting controlled row')
            require(label not in partial[beta].values() or partial[beta].get(alpha)==label,'Noninjective controlled row')
            partial[beta][alpha]=label
    perms=[]
    for prescribed in partial:
        missing=iter(sorted(set(range(a))-set(prescribed.values())))
        p=[prescribed[i] if i in prescribed else next(missing) for i in range(a)]
        require(sorted(p)==list(range(a)),'Controlled completion not a permutation')
        perms.append(p)
    def indices(i,j):
        alpha,beta=divmod(i,b); gamma,delta=divmod(j,b)
        return perms[beta][alpha],perms[delta][gamma],beta,delta
    for i in range(a):
        for j in range(a):
            require(indices(i,m-a+j)==(i,j,i,j+2),'First-factor symbolic contraction')
    rs=[perms[i][0] for i in range(b)]
    cs=[perms[j][(m-b+j)//b] for j in range(b)]
    require(rs==list(range(a))+[a-1,0] and cs==[a-1,0]+list(range(a)),'Second-factor scale indices')
    for i in range(b):
        for j in range(b):
            require(indices(i,m-b+j)==(rs[i],cs[j],i,j),'Second-factor symbolic contraction')
    for i in range(d):
        for j in range(d):
            require(indices(i,m-d+j)==(rows[i],cols[j],i%b,(m-d+j)%b),'Data null-corner symbolic contraction')
    return dict(dimensions=[a,b],permutations=perms,
                local_a_formula='(M tensor v*nu)[i,m-a+j] = v[i]*M[i,j]*nu[j+2]',
                local_b_formula='(p*xi tensor M)[i,m-b+j] = p[rs[i]]*M[i,j]*xi[cs[j]]',
                local_profiles_preserved_by_nonzero_diagonal_scalings=True,
                entry_index_equalities=a*a+b*b+d*d,
                first_corner_rows=list(range(a)),first_corner_columns=list(range(m-a,m)),
                second_corner_rows=list(range(b)),second_corner_columns=list(range(m-b,m)))


def algebra():
    """Exact tensor-projector calculus, not dimension-only labels.

    Four orthogonal atoms: P*Q, P*(1-Q), (1-P)*Q, (1-P)*(1-Q).
    P and Q act in different tensor factors. Each coefficient is integer;
    multiplication is coordinatewise in their four-component product ring.
    """
    a,b=23,25; ranks=[1,b-1,a-1,(a-1)*(b-1)]
    def coeff(mask):return [int(mask>>i&1) for i in range(4)]
    def rank(mask):return sum(r for i,r in enumerate(ranks) if mask>>i&1)
    def add(x,y):return [a+b for a,b in zip(x,y)]
    def mul(x,y):return [a*b for a,b in zip(x,y)]
    # Literal 2-by-2 partial-swap matrices over the four-component ring.
    def D(mask):
        p=coeff(mask); q=coeff(15^mask)
        return [[q,p],[p,q]]
    def matmul(A,B):return [[add(mul(A[i][0],B[0][j]),mul(A[i][1],B[1][j])) for j in range(2)] for i in range(2)]
    for s in range(16):
        require(matmul(D(s),D(s))==D(0),'Actual partial-swap involution')
        for t in range(16):
            require(matmul(D(s),D(t))==D(s^t),'Actual partial-swap composition')
    steps=[('stage1_X',1,5,4),('stage1_Y',0,4,4),
           ('front_X',5,13,8),('front_Y',4,12,8),
           ('stage2_X',13,15,2),('stage2_Y',12,14,2),
           ('stage1_aux_exterior',5,15,10),('stage2_aux_exterior',15,3,12),
           ('paid_data_copy',15,14,1)]
    for name,old,new,residual in steps:
        require(old^new==residual and matmul(D(new),D(old))==D(residual),'Boundary residual: '+name)
    # Input roles: X has gauge PQ; Y has gauge 0. Aux1:0; Aux2:Pbar*I.
    endpoints={'X':(1,14),'Y':(0,15),'auxiliary_stage1':(0,15),'auxiliary_stage2':(12,3)}
    for role,(first,last) in endpoints.items():
        require(first^last==15,'Noncomplementary original-role endpoint: '+role)
    # Independent exact operator-tag payload calculation. Tags (source,mask)
    # are row pullbacks by D_mask. Sets add over F2 by symmetric difference.
    def transform(value,mask):return {(source,s^mask) for source,s in value}
    x,y={('x',0)},{('y',0)}
    logical_x,logical_y=transform(x,1),y
    logical_y ^= logical_x                # verified first forward local shear
    logical_x ^= logical_y                # verified second inverse-renamed shear
    X,Y=transform(logical_x,15),transform(logical_y,14)
    require(X=={('y',15)} and Y=={('x',15),('y',14)},'Precorrection framed payload')
    copy=transform(X,1)                   # one FRESH copy, rank-one transport
    Y ^= copy
    require(X=={('y',15)} and Y=={('x',15)},'Paid endpoint correction not interchange')
    return dict(atom_order=['P tensor Q','P tensor (I-Q)','(I-P) tensor Q','(I-P) tensor (I-Q)'],
                atom_ranks=ranks,partial_swap_matrix_equations=16+256,
                boundaries=[dict(name=name,old_mask=old,new_mask=new,residual_mask=residual,rank=rank(residual)) for name,old,new,residual in steps],
                original_role_complementary_endpoints={k:list(v) for k,v in endpoints.items()},
                before_correction=['D_I y','D_I x + D_(I-P tensor Q) y'],
                after_correction=['D_I y','D_I x'],
                fresh_endpoint_copy_frame=[15,14],paid_copy_residual_rank=1,
                scalar_bank_exchange=True,all_original_roles_receive_full_interchange=True)


def profile(selected,local23,local25,receipts):
    a,b=23,25; va,vb=comb(a,3),comb(b,3);N=va*vb;m=a*b
    parts={}
    for h,v,other,local in [(a,va,vb,local23),(b,vb,va,local25)]:
        blocks=receipts[h]['profile']['blocks'];R=local['R']
        parts['internal_'+str(h)]={str(t):n*other for t,n in enumerate(blocks) if n}
        parts['exterior_'+str(h)]={str(h):R*other,str(m-2*h):R*other}
        parts['data_growth_'+str(h)]={'1':2*N,str(h-2):2*N}
    parts['data']={'1':18*N,'21':2*N,'17':2*N,'481':2*N}
    parts['paid_endpoint_copy']={'1':N}
    require(parts==selected['bit']['parts'],'Complete schedule classes do not match selected child profile')
    total=Counter()
    for part in parts.values():total.update({int(t):n for t,n in part.items()})
    W=2*N+vb*local23['R']+va*local25['R'];mass=sum(t*n for t,n in total.items())
    require({str(t):n for t,n in total.items()}==selected['bit']['child_multiplicities'],'Complete child multiplicities')
    require(W==selected['bit']['W'] and mass==selected['bit']['total_rank'] and m==selected['bit']['m'],'Role/rank binding')
    scalar=vb*local23['full_wrapper_literal_xors']+va*local25['scalar_wrapper_xors']+N
    centers=vb*a+va*b
    return dict(m=m,N=N,W=W,total_rank=mass,deficit=W*m-mass,parts=parts,
                child_multiplicities={str(t):n for t,n in sorted(total.items())},
                original_role_classes={'data_X':N,'data_Y':N,'stage1_auxiliary':vb*local23['R'],'stage2_auxiliary':va*local25['R']},
                local_invocations={'forward_h23':vb,'inverse_renamed_h25':va},
                scalar_xors_including_final_correction=scalar,
                fresh_center_clones=centers,fresh_endpoint_clones=N,
                xor_equivalents_including_all_fresh_clones=scalar+centers+N,
                copy_erase_cost='All clones start blank and complete copies/erasure are separately linear stream operations; no extra original row coordinate or zero-dirty assumption.',
                inherited_profile_facts='Unchanged exact local CRT profiles, fixed-basis exterior/growth profiles and all-pair data corner profile. This checker establishes exact physical residual/class correspondence and sums, not new pivot-minor certificates.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--upstream',required=True,type=Path)
    p.add_argument('--word-dir',required=True,type=Path)
    p.add_argument('--profile-inputs',required=True,type=Path)
    p.add_argument('--certificate',required=True,type=Path)
    p.add_argument('--prior-audit',required=True,type=Path)
    p.add_argument('--output-dir',required=True,type=Path)
    args=p.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
    sources=pinned_sources(args.upstream.resolve())
    manifest=args.word_dir/'source-word-manifest.json'
    receipts={h:json.loads((args.word_dir/f'pair-ranked-{h}-receipt.json').read_text()) for h in (23,25)}
    f=forward_local.audit(args.word_dir/'pair-ranked-word-23.json.gz',manifest,args.word_dir/'pair-ranked-23-receipt.json',args.profile_inputs/'ranked-23.bin')
    print('PASS actual forward local h23',flush=True)
    r=reverse_local.audit(args.word_dir/'pair-ranked-word-25.json.gz',manifest,args.word_dir/'pair-ranked-25-receipt.json',args.profile_inputs/'ranked-25.bin')
    print('PASS actual inverse+bank-renamed local h25',flush=True)
    # The reversed h25 side flags are complements of the ACTUAL checked h25
    # forward flags, even though this forward word is not a global stage.
    dual_flags=forward_local.audit(args.word_dir/'pair-ranked-word-25.json.gz',manifest,args.word_dir/'pair-ranked-25-receipt.json',args.profile_inputs/'ranked-25.bin')
    selected=json.loads(args.certificate.read_text())
    prior=json.loads(args.prior_audit.read_text())
    for local in [f,r]:
        axis=next(x for x in prior['axes'] if x['h']==local['h'])
        require(axis['word_sha256']==local['word_sha256'] and axis['binary_profiler_input_sha256']==local['binary_profiler_input_sha256'], 'Prior independent word/CRT source binding')
        require(axis['profile']==receipts[local['h']]['profile']['blocks'], 'Prior independently verified local profile')
    result=dict(status='PASS',selected_profile='PR64',source_pin=PIN,source_files=sources,
        certificate_sha256=digest(args.certificate),prior_independent_audit_sha256=digest(args.prior_audit),source_manifest_sha256=digest(manifest),
        checker_sha256=digest(Path(__file__)),actual_lines=[actual_lines(23),actual_lines(25)],
        controlled_basis=controlled_corner(),ambient=algebra(),complete_profile=profile(selected,f,r,receipts),
        role_layout={'data_X':'s*v_b+t','data_Y':'N+s*v_b+t','stage1_auxiliary':'2N+t*R_a+r','stage2_auxiliary':'2N+v_b*R_a+s*R_b+r','ranges':'0<=s<v_a; 0<=t<v_b; 0<=r<R_a or R_b. These disjoint consecutive product ranges cover exactly W original roles. Stage1 holds t fixed; stage2 holds s fixed; final merge exchanges the two data banks and fixes both auxiliary banks.'},
        local_reports={'forward23':f,'reverse25':r,'forward25_flag_and_profile_reference':dual_flags},
        tensor_lift_contract={'stage1':'U -> U tensor Q; Q is each actual b-triple rank-one orthogonal projector',
          'stage2':'U -> (I-P) tensor I + P tensor U; P is each actual a-triple rank-one orthogonal projector',
          'residuals':'The common background cancels; both embeddings send Q-P to the corresponding tensor residual of identical local rank. Complement/reverse local paths therefore reuse exactly the same CRT input.',
          'universal_algebra_boundary':'Tensor-product identity (A tensor B)(C tensor D)=AC tensor BD and orthogonal-projector absorption are mathematical identities used to interpret this exact expression certificate; no dense 575x575 matrix is expanded for every replicated gate.'},
        scope='Complete compact ambient two-direction finite schedule, exact common-frame and endpoint expressions, physical inverse-renamed dirty-basis replay, and full charged-profile correspondence. Existing pivot/profile certificates are reused. No full Lean Trace term, tape running-time bound or multiplication theorem is claimed.')
    (args.output_dir/'full-ambient.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS complete ambient endpoint/copy/profile correspondence',result['complete_profile']['W'],result['complete_profile']['total_rank'],flush=True)

if __name__=='__main__': main()
