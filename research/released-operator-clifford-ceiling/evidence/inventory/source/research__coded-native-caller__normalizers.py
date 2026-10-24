"""Exact signed-permutation normalizers for PR4929's coupled native offer.
Apache-2.0; substantial OpenAI Codex assistance. Retained Clifford sources are
credited in PHYSICAL.md. Run read-only by default; --write emits the receipt.
"""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
import argparse
import gzip
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent
SOURCE_PAYLOAD='cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
CODE_HASH='8be7f3f073b7981ec91c6af43edff0ac8a89f4824ef6026ae758c287dd6c03d0'
CLIFFORD_HASH='2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962'
MODE_LINES=(7,25,42,52,76,82,97,127)

def need(ok,message):
    if not ok: raise ValueError(message)

def nullspace(rows,n):
    a=[[F(x)for x in row]for row in rows];piv=[];k=0
    for j in range(n):
        t=next((i for i in range(k,len(a))if a[i][j]),None)
        if t is None:continue
        a[t],a[k]=a[k],a[t];d=a[k][j];a[k]=[x/d for x in a[k]]
        for i in range(len(a)):
            if i!=k:
                d=a[i][j]
                if d:a[i]=[x-d*y for x,y in zip(a[i],a[k])]
        piv.append(j);k+=1
    return [[F(i==j) if i not in piv else -a[piv.index(i)][j] for i in range(n)]for j in range(n)if j not in piv]

def mode_factor(A,ports):
    E=[[A[i][j]-F(i==j)for j in range(112)]for i in range(112)]
    selected=(0,1,2,3,4,5,6,12)
    G=[[E[i][j]for j in selected]for i in range(112)]
    columns=[]
    for line in MODE_LINES:
        ns=nullspace([G[i]for i,q in enumerate(ports)if(q&line).bit_count()%2],8)
        need(len(ns)==1,'Mode nullspace is one dimensional')
        v=[sum(x*y for x,y in zip(row,ns[0]))for row in G]
        scale=next(x for x in v if x);v=[x/scale for x in v]
        need(all(x in (-1,0,1)for x in v),'Integral signed mode')
        columns.append([int(x)for x in v])
    need(all(sum(x*y for x,y in zip(a,b))==56*(i==j)for i,a in enumerate(columns)for j,b in enumerate(columns)),'Orthogonal mode Gram matrix')
    need(all(sum(c[i]*c[j]for c in columns)==-4*E[i][j]for i in range(112)for j in range(112)),'All code entries from eight modes')
    need(all(sum(c[i]!=0 for c in columns)==4 for i in range(112)),'Four mode contacts per row')
    return columns

def run():
    raw=gzip.decompress((HERE/'native-source.json.gz').read_bytes())
    need(sha256(raw).hexdigest()==SOURCE_PAYLOAD,'Changed actual native source payload')
    code=(HERE/'CODE.json').read_bytes();need(sha256(code).hexdigest()==CODE_HASH,'Changed PR4929 code')
    cp=HERE/'clifford_exact.py';need(sha256(cp.read_bytes()).hexdigest()==CLIFFORD_HASH,'Changed retained exact Clifford implementation')
    spec=importlib.util.spec_from_file_location('coded_normalizers_clifford',cp)
    ce=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ce;spec.loader.exec_module(ce)
    canonical=json.loads(raw)['canonical'];ports=canonical['ports']
    need(len(ports)==112 and all(q.bit_count()in(3,7)for q in ports),'Exact port domain')
    A=[[F(x)for x in row]for row in json.loads(code)['A']]
    need(len(A)==112 and all(len(row)==112 for row in A),'Code shape')
    M=mode_factor(A,ports)
    N=9;R=ce.fourier(N);Q=ce.cgate(N,1);D=ce.fourier(N,range(1,N))
    def equal(a,b):return a.tab==b.tab and a.zero_state()==b.zero_state()
    def monomial(op):return all(x==0 for x,z,ph in op.tab[N:])
    def conjugate(op):
        circuit=[]
        for e in op.circuit:
            if e[0]=='D':circuit.append(('D',e[1],tuple((-x)%4 for x in e[2])))
            elif e[0]=='C':circuit.append(('C',e[1],-e[2]))
            elif e[0]=='phase':circuit.append(('phase',(-e[1])%4))
            else:circuit.append(e)
        return ce.Op(N,tuple((x,z,(-ph)%4)for x,z,ph in op.tab),circuit)
    def trans(v,x):return x^(v if ce.parity(x&v)else 0)
    records=[];phase_controls=0
    for idx,q in enumerate(ports):
        if not(q&1):vs=[1^q]
        else:
            j=next(j for j in range(1,N)if not(q>>j&1));vs=[1^(1<<j),(1<<j)^q]
        columns=[]
        for j in range(N):
            x=1<<j
            for v in vs:x=trans(v,x)
            columns.append(x)
        G=ce.transpose(columns,N)
        need(columns[0]==q,'Central line image')
        need(all(ce.parity(a&b)==(i==j)for i,a in enumerate(columns)for j,b in enumerate(columns)),'Binary orthogonality')
        z=sum((((row.bit_count()-1)//2)&1)<<j for j,row in enumerate(G))
        perm=ce.perm(N,G)
        K=perm.then(ce.diag(N,(0,)*N,tuple(2*((z>>j)&1)for j in range(N))))
        # Exact symbolic tableau plus an absolute-phase state; not merely ranks.
        need(equal(K.then(R),R.then(K)),'Exact full-Gaussian commutator')
        need(all((ce.mv(ce.transpose(G,N),x).bit_count()-x.bit_count()-2*ce.parity(z&x))%4==0 for x in range(512)),'Literal weight congruence')
        if z:
            need(not equal(perm.then(R),R.then(perm)),'Omitting signed phase must fail')
            phase_controls+=1
        E=ce.canonical_frame(N,canonical['frames'][canonical['start'][idx]])
        S=ce.canonical_frame(N,canonical['frames'][canonical['final'][112+idx]])
        need(canonical['final'][idx]==1 and canonical['start'][112+idx]==0,'Full-X and ground-Y boundaries')
        MX=Q.adjoint().then(K).then(E);MY=K;OX=K.adjoint();OY=S.adjoint().then(K.adjoint()).then(D)
        need(all(monomial(op)for op in (MX,MY,OX,OY)),'Every physical wrapper is monomial')
        need(equal(MX.then(E.adjoint()),Q.adjoint().then(K)),'All incoming coded columns')
        need(equal(S.then(OY),K.adjoint().then(D)),'All outgoing coded rows')
        need(equal(MX.then(E.adjoint()).then(R).then(OX),D),'Independent X diagonal')
        need(equal(MY.then(S).then(OY),D),'Independent Y diagonal')
        need(equal(MX.then(E.adjoint()).then(S).then(OY),Q.adjoint().then(D)),'Original same-port shear block')
        # K is a real signed permutation. The real transpose equals its adjoint.
        need(all(e[0]!='D'or all(a%2==0 for a in e[2])for e in K.circuit),'Real K phases')
        # Raw inverse transpose uses conjugated endpoint frames and wrappers.
        Q2=Q.then(Q);D2=D.then(D)
        BX=Q2.adjoint().then(conjugate(MX))
        BO=conjugate(OX).then(D2).then(Q2)
        BY=conjugate(OY).then(D2)
        need(equal(BX.then(conjugate(E).adjoint()).then(conjugate(R)).then(BO),D),'Backward corrected X diagonal')
        need(equal(K.then(conjugate(S)).then(BY),D),'Backward corrected Y diagonal')
        need(equal(conjugate(R).then(BO),K.adjoint().then(Q).then(D)),'Backward all coded outgoing rows')
        need(all(monomial(op)for op in (BX,K,BO,BY)),'Backward corrected wrappers monomial')
        operations={'input_X':MX,'input_Y':MY,'output_X':OX,'output_Y':OY,
                    'backward_input_X':BX,'backward_input_Y':K,'backward_output_X':BO,'backward_output_Y':BY}
        compiled={}
        for name,op in operations.items():
            mon,recipe=ce.monomial(op)
            need(equal(mon,op),'Compiled monomial exact phase and tableau')
            need(all(e[0] in ('P','D','X','phase')for e in mon.circuit),'No Gaussian in emitted wrapper')
            compiled[name]={'word':mon.circuit,'recipe':recipe}
        wrong=ce.Op(N,K.tab,K.circuit+[('phase',1)])
        need(not equal(wrong,K),'Absolute-phase-only mutation rejected')
        records.append({'port':idx,'q':q,'orthogonal_transvections':vs,'G_rows':G,'Z_mask':z,
                        'K_word':K.circuit,'compiled_wrappers':compiled})
    need(phase_controls>0,'Nonvacuous omitted-phase control')
    # Independent scalar execution of A and A^-1 on every arbitrary-input basis.
    for inverse,den in ((False,4),(True,52)):
        for j in range(112):
            x=[F(i==j)for i in range(112)]
            temp=[sum(F(c[i])*x[i]for i in range(112))for c in M]
            y=[x[i]-sum(F(M[k][i])*temp[k]for k in range(8))/den for i in range(112)]
            target=[A[i][j]if not inverse else (A[i][j]+12*F(i==j))/13 for i in range(112)]
            need(y==target,'Literal owned-mode scalar recoding')
    result={'schema':'coded-native-real-normalizers/1','status':'PASS_CODED_NATIVE_REAL_NORMALIZERS',
        'source_payload_sha256':SOURCE_PAYLOAD,'code_sha256':CODE_HASH,'clifford_sha256':CLIFFORD_HASH,
        'ports':records,'mode_columns':M,'finite_checks':{'ports':112,'weight_congruence_addresses':112*512,
        'exact_endpoint_factor_identities':112*8,'monomial_wrappers':896,'omitted_phase_rejections':phase_controls,
        'scalar_basis_recodings':224,'gaussian_free_compiled_wrappers':896,'absolute_phase_mutations_rejected':112},
        'recoding_bill':{'owned_fields':8,'signed_mode_adds':448,'output_scaled_adds':448,
        'owned_initial_clears':8,'owned_terminal_clears':8,'monomial_field_maps':224,
        'forward_update_coefficient':'-1/4','inverse_update_coefficient':'-1/52',
        'forward_prefix_component_l1_upper':57,'inverse_prefix_component_l1_upper':56,'inverse_output_prefix_component_l1_upper':'69/13'},
        'local_gauge_bill':{'recodings':2,'added_recursive_calls':0,'owned_fields_reused':8,
        'recoding_scalar_adds':1792,'recoding_owned_clears':32,'recoding_monomial_field_maps':448,
        'main_wrapper_field_maps':448,'backward_extra_monomial_field_maps_upper':448},
        'scope':'Exact physical central ABI and local gauges; not full-controller or multiplication admission.'}
    return json.loads(json.dumps(result,sort_keys=True))

def render_receipt(result):
    """Keep each generated port record on one line; compare parsed mathematics."""
    entries=[]
    for key,value in sorted(result.items()):
        if key=='ports':
            body='[\n'+',\n'.join('    '+json.dumps(row,sort_keys=True,separators=(',',':')) for row in value)+'\n  ]'
        else:
            body=json.dumps(value,sort_keys=True,separators=(',',':'))
        entries.append('  '+json.dumps(key)+': '+body)
    return '{\n'+',\n'.join(entries)+'\n}\n'

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
    result=run();path=HERE/'NORMALIZERS.json'
    if args.write:path.write_text(render_receipt(result))
    else:need(json.loads(path.read_text())==result,'Changed generated normalizer receipt')
    print(result['status'],json.dumps(result['finite_checks'],sort_keys=True))
if __name__=='__main__':main()
