"""Exact changed-owner constructions, returns, phase controls and invoices.
intqwq; substantial OpenAI Codex assistance. Apache-2.0.
No optimizer, widened native replay or new recursive supplier admission.
"""
from collections import Counter
import argparse
import ast
from fractions import Fraction as Q
from hashlib import sha1,sha256
import gzip
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import verify_lean as VLean

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CE='research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py'
WORD='research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
PACKET='research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/certificate.json.gz'
SELECTED=(0,7,20,27,36,46,57,111)


def need(ok,message):
    if not ok:raise ValueError(message)


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module


def plus(a,b,c=Q(1)):
    out=dict(a)
    for k,v in b.items():out[k]=out.get(k,Q(0))+c*v
    return {k:v for k,v in out.items() if v}


def mm(a,b):
    out=[]
    for row in a:
        ans={}
        for j,v in row.items():ans=plus(ans,b[j],v)
        out.append(ans)
    return out


def identity(n):return [{i:Q(1)} for i in range(n)]


def scalar_matrix_ops(matrix,roles):
    """Dyadic-unit Gaussian elimination; source lineage: round5 port_matrix."""
    n=len(roles);a=[[matrix[i].get(j,Q(0)) for j in range(n)] for i in range(n)];elimination=[]
    for j in range(n):
        def unit(q):return bool(q) and abs(q.numerator)&(abs(q.numerator)-1)==0 and q.denominator&(q.denominator-1)==0
        pivot=next(i for i in range(j,n) if unit(a[i][j]))
        if pivot!=j:a[j],a[pivot]=a[pivot],a[j];elimination.append(['swap',j,pivot])
        if a[j][j]!=1:
            q=1/a[j][j];a[j]=[q*v for v in a[j]];elimination.append(['scale',j,q])
        for i in range(n):
            if i!=j and a[i][j]:
                q=-a[i][j];a[i]=[v+q*w for v,w in zip(a[i],a[j])];elimination.append(['add',i,j,q])
    need(a==[[Q(i==j) for j in range(n)] for i in range(n)],'Exact dyadic elimination')
    out=[]
    for e in reversed(elimination):
        if e[0]=='swap':
            x,y=roles[e[1]],roles[e[2]]
            out.extend([['add',x,y,Q(1)],['add',y,x,Q(-1)],['add',x,y,Q(1)],['scale',y,Q(-1)]])
        elif e[0]=='scale':out.append(['scale',roles[e[1]],1/e[2]])
        else:out.append(['add',roles[e[1]],roles[e[2]],-e[3]])
    return out


def tariff(e):
    q=e[-1];n,d=abs(q.numerator),q.denominator
    need(n>0 and d&(d-1)==0,'Nonzero dyadic scalar')
    if e[0]=='scale':
        need(n&(n-1)==0,'Only dyadic-unit SCALE')
        return 2*(abs(n.bit_length()-d.bit_length())+int(q<0))
    return 2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)


def replay_scalar(ops,n):
    rows=identity(n);prefix=Q(1);den=1
    for e in ops:
        if e[0]=='add':
            need(e[1]!=e[2],'Distinct ADD owners')
            rows[e[1]]=plus(rows[e[1]],rows[e[2]],e[3])
        else:rows[e[1]]={k:e[2]*v for k,v in rows[e[1]].items()}
        prefix=max(prefix,sum(map(abs,rows[e[1]].values()),Q(0)))
        den=max(den,max((v.denominator for v in rows[e[1]].values()),default=1))
    return rows,prefix,den


def completion(packet):
    R=[{int(k):Q(v) for k,v in row.items()} for row in packet['R_rows']]
    B=[{k:r[i]/2 for k,r in enumerate(R) if r.get(i)} for i in range(112)]
    C=[{i:v/2 for i,v in row.items()} for row in R]
    need(mm(C,B)==[{i:Q(14)} for i in range(8)],'Authenticated CB14I')
    J=[plus({i:Q(1)},r,Q(-1)) for i,r in enumerate(mm(B,C))]
    A=[]
    for i,row in enumerate(J):
        row=plus(row,{112+k:v for k,v in B[i].items()},Q(-1))
        row=plus(row,{120+k:v for k,v in B[i].items()},Q(26));A.append(row)
    for k,row in enumerate(C):A.append({**{i:-16*v for i,v in row.items()},112+k:Q(-15),120+k:Q(449)})
    for k,row in enumerate(C):A.append({**{i:-v for i,v in row.items()},112+k:Q(-1),120+k:Q(28)})
    A2=mm(A,A);need(mm(A2,A)==identity(128),'All128 order-three matrix columns')
    need(A2!=A and A!=identity(128),'Nontrivial order3 does not equal a repeated-owner split')
    D=[{k:r.get(port,Q(0)) for k,port in enumerate(SELECTED) if r.get(port)} for r in C]
    Dt=[{k:D[k][j] for k in range(8) if D[k].get(j)} for j in range(8)]
    need(mm(D,Dt)==mm(Dt,D)==identity(8),'Selected dyadic orthogonal query coordinates')
    Cp=mm(Dt,C);Bp=mm(B,D);ordinary=[i for i in range(112) if i not in SELECTED]
    need(all({i:v for i,v in row.items() if i in SELECTED}=={SELECTED[k]:Q(1)} for k,row in enumerate(Cp)),
         'No odd division in source coordinate extraction')
    ops=scalar_matrix_ops(Dt,list(range(112,120)))+scalar_matrix_ops(Dt,list(range(120,128)))
    for k,a in enumerate(SELECTED):
        ops += [['add',a,i,v] for i,v in sorted(Cp[k].items()) if i in ordinary]
    for i in ordinary:
        for k,v in sorted(Bp[i].items()):
            ops += [['add',i,SELECTED[k],-v],['add',i,112+k,-v],['add',i,120+k,26*v]]
    block=[{0:Q(-13),1:Q(-14),2:Q(364)},{0:Q(-16),1:Q(-15),2:Q(449)},{0:Q(-1),1:Q(-1),2:Q(28)}]
    for k,a in enumerate(SELECTED):ops+=scalar_matrix_ops(block,[a,112+k,120+k])
    for k,a in enumerate(SELECTED):
        ops += [['add',a,i,-v] for i,v in sorted(Cp[k].items()) if i in ordinary]
    ops+=scalar_matrix_ops(D,list(range(112,120)))+scalar_matrix_ops(D,list(range(120,128)))
    actual,prefix,den=replay_scalar(ops,128)
    need(actual==A,'Actual in-place scalar adapter on every arbitrary owner')
    returned,triple_prefix,triple_den=replay_scalar(ops*3,128)
    need(returned==identity(128),'Three complete adapters restore every arbitrary owner')
    bad=ops[:-1];need(replay_scalar(bad,128)[0]!=A,'Omitted final return/basis step is rejected')
    mismatch=next((i,j,A2[i].get(j,Q(0))-A[i].get(j,Q(0))) for i in range(128) for j in range(128) if A2[i].get(j,Q(0))!=A[i].get(j,Q(0)))
    return dict(status='PASS_EXACT_CHANGED_OWNER_ORDER3_ALGEBRA',owners=128,order=3,
                scalar_operations=len(ops),scalar_tariff=sum(map(tariff,ops)),maximum_prefix_row_l1=str(prefix),maximum_prefix_denominator=den,
                triple_adapter_restores_all_owners=True,triple_adapter_maximum_prefix_row_l1=str(triple_prefix),
                triple_adapter_maximum_prefix_denominator=triple_den,
                ordinary_gaussian_calls_in_standalone_A=0,
                scalar_word=[[str(v) if isinstance(v,Q) else v for v in e] for e in ops],
                all_owner_adapter_and_cube=True,omitted_final_step_rejected=True,
                wrong_shared_owner_tensor_split=dict(rejected=True,output_owner=mismatch[0],input_owner=mismatch[1],coefficient_difference=str(mismatch[2])),
                split_scope='The ordinary tensor split duplicates owner factors. Keeping one owner bank and applying A on both digit factors produces A^2, not A. This exact witness excludes only that proposed split, not every new typed split/merge.',
                invoice=dict(source_paid_rank_mass=5093,remaining_independent_helper_mass=3013,unconverted_coupled_main_mass=2080,
                             unconverted_deficit=0,ordinary_conversion_paid_H1=32,ordinary_target_rank_lost=32,ordinary_main_mass=2048,converted_deficit=64),
                retained_controller_conditional_ledgers=[dict(p=p,calls=2*p+1,
                    surplus_before_direct_Q_heads=128*((2*p+1)-1)-64*(2*p+1),
                    direct_Q_heads=256*p,surplus_after_heads=-64*(2*p+1)) for p in [1,2]],
                resource_scope='Standalone A is only fixed dyadic owner mixing at a common frame and earns no Gaussian productive credit. Expensive main jobs must bind actual F_final A F_start^-1 and Q^-1 M Q endpoint phases. No widened native replay or new consumer admission is claimed.')


def dirty_protocol(wrong_inverse=False,omit_return=False):
    rows=[{(i,0):Q(1)} for i in range(3)];prefix=Q(1)
    def add(a,b,q):
        nonlocal prefix
        rows[a]=plus(rows[a],rows[b],Q(q));prefix=max(prefix,sum(map(abs,rows[a].values()),Q(0)))
    def call(power):rows[2]={(i,k+power):v for (i,k),v in rows[2].items()}
    add(2,0,1);call(1);add(1,2,1);call(1 if wrong_inverse else -1)
    if not omit_return:add(2,0,-1)
    call(1);add(1,2,-1)
    return rows,prefix


def dirty(word,ce):
    rows,prefix=dirty_protocol();wanted=[{(0,0):Q(1)},{(1,0):Q(1),(0,1):Q(1)},{(2,1):Q(1)}]
    need(rows==wanted,'All three arbitrary owner returns, independent helper')
    need(dirty_protocol(omit_return=True)[0]!=wanted,'Omitted helper decontamination is rejected')
    need(dirty_protocol(wrong_inverse=True)[0]!=wanted,'Wrong literal inverse is rejected algebraically')
    center=next(e for e in word['programs']['forward'] if e[0]=='center');basis=word['canonical']['frames'][center[2]]
    F=ce.canonical_frame(9,tuple(basis)).adjoint();unit=ce.ident(9)
    correct=F.then(F.adjoint());wrong=F.then(F)
    need(correct.tab==unit.tab and correct.zero_state()==unit.zero_state(),'Actual native center F and true inverse cancel with phase')
    need(wrong.tab!=unit.tab and wrong.zero_state()!=unit.zero_state(),'Actual native inverse substitution is observably wrong')
    need(ce.rank([x for x,z,p in F.tab[9:]])==8,'Actual first center operator is rank8')
    # At a Gaussian spectral value z, the target owner matrix is
    # [[1,0,0],[z,1,0],[0,0,z]]. Its difference from z=1 at z=i
    # has rank two, while one single-owner call gives rank at most one.
    # Any constant-owner circuit with even many F^+/- calls has determinant
    # c*z^(even). z=1 forces c=1 and z=i then contradicts det(target)=i.
    zero,one,imag=(0,0),(1,0),(0,1)
    def cmul(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
    def csub(a,b):return a[0]-b[0],a[1]-b[1]
    def target(z):return [[one,zero,zero],[z,one,zero],[zero,zero,z]]
    at_i,at_1=target(imag),target(one)
    delta=[[csub(a,b) for a,b in zip(ra,rb)] for ra,rb in zip(at_i,at_1)]
    rank_two_minor=csub(cmul(delta[1][0],delta[2][2]),cmul(delta[1][2],delta[2][0]))
    need(rank_two_minor==(0,-2),'Exact nonzero two-by-two Gaussian-integer minor')
    # The z=1 target determinant forces all constant mixing determinants to
    # multiply to 1. Exhaust the possible zero/two-call exponent sums at i.
    powers=[one,imag,(-1,0),(0,-1)]
    determinant_controls=[dict(exponent=k,value=powers[k%4]) for k in [-2,0,2]]
    need(all(case['value']!=imag for case in determinant_controls),'Zero/two-call determinant gate')
    return dict(status='PASS_ARBITRARY_DIRTY_HELPER_RETURN_AND_NEGATIVE_INVOICE',owners=3,paid_F_calls=3,scalar_ADDs=4,
                maximum_prefix_sum_operator_l2_norm_bound=str(prefix),final_helper='F h, independent of x and y',
                all_f='For F_(r,f)=C_r tensor f, the same additive identity holds for every f. Paid widths r*f, r*f, r*f; one helper width r*f. No rounding/tape transfer theorem is asserted.',
                actual_first_center=dict(from_frame=center[2],to_frame=center[3],rank=8,literal_adjoint_phase_checked=True),
                controls=dict(omitted_helper_decontamination_rejected=True,wrong_literal_inverse_rejected=True),
                minimum_call_gate=dict(minimum=3,scope='Constant invertible owner mixing and calls F or F^-1 on a single owner; desired helper is F h. Uses two spectral values 1,i (or 1,-i for the adjoint). Shared multi-owner or different operator calls are outside this gate.',
                                       one_call_rank_two_minor=rank_two_minor,zero_and_two_call_determinants_at_i=determinant_controls,
                                       even_calls_determinant_parity='i^(even) is real and cannot equal i'),
                invoice=dict(owned_comparator='r^t',dirty_paid='3*r^t',independent_helper_reward='r^t',dirty_net='2*r^t',net_extra='r^t > 0 for r>0 and every real t'),
                physical_scope='Four fixed whole-field ADDs are charged scalar primitives; three actual Gaussian oracle calls are paid. Operator l2 bound is not a componentwise finite-precision admission theorem.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--git-provenance',action='store_true');args=parser.parse_args()
    pins=read(HERE/'SOURCES.json')
    for pin in pins['files']:
        raw=(HERE/pin['copy']).read_bytes();need(sha256(raw).hexdigest()==pin['sha256'],'Exact source SHA')
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['blob'],'Retained source bytes self-hash to recorded Git blob')
        if args.git_provenance:
            need(subprocess.check_output(['git','rev-parse',pin['commit']+':'+pin['path']],cwd=ROOT).decode().strip()==pin['blob'],
                 'Optional origin commit:path resolves to source blob')
            need(subprocess.check_output(['git','cat-file','blob',pin['blob']],cwd=ROOT)==raw,'Optional origin Git blob bytes')
    ce=load(HERE/'sources'/CE,'owner_actual_phase_compiler')
    packet=read(HERE/'sources'/PACKET);word=read(HERE/'sources'/WORD)
    a=completion(packet);b=dirty(word,ce)
    primitive_source=HERE/'sources/research/kappa-rebuild/complex/rebuild_native.py'
    nodes=[n for n in ast.parse(primitive_source.read_text(encoding='utf-8')).body
           if isinstance(n,ast.FunctionDef) and n.name=='primitive_allowance']
    need(len(nodes)==1,'Exact inherited scalar-tariff function exists')
    namespace={'Q':Q,'need':need}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(primitive_source),'exec'),namespace)
    costs=[]
    for event in a['scalar_word']:
        q=Q(event[-1]);gate=([event[0],['L',event[1]],['L',event[2]],q.numerator,q.denominator]
                           if event[0]=='add' else [event[0],['L',event[1]],q.numerator,q.denominator])
        costs.append(namespace['primitive_allowance'](gate))
    need(sum(costs)==a['scalar_tariff'],'Complete scalar tariff matches pinned legacy primitive implementation')
    a['scalar_tariff_independently_replayed_from_pinned_source']=True
    lean=VLean.check_receipt()
    out=dict(status='PASS_TWO_CHANGED_OWNER_GATES_NO_KAPPA',order_three=a,dirty_helper=b,new_kappa=False,
             environment_provenance=dict(python_executable=sys.executable,python_version=sys.version),
             source_check='Retained SHA256 and Git blob self-hash; no history ancestry claim.',
             source_manifest_sha256=sha256((HERE/'SOURCES.json').read_bytes()).hexdigest(),
             script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),lean_receipt_sha256=sha256((HERE/'LEAN.json').read_bytes()).hexdigest())
    (HERE/'RESULT.json.gz').write_bytes(gzip.compress(json.dumps(out,sort_keys=True,separators=(',',':')).encode(),mtime=0))
    print(out['status'],'order3 owners',a['owners'],'scalar ops',a['scalar_operations'],'tariff',a['scalar_tariff'],
          'prefix',a['maximum_prefix_row_l1'],'dirty paid',b['paid_F_calls'])


if __name__=='__main__':main()
