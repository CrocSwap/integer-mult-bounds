#!/usr/bin/env python3
"""Exact native-contact matrices; no floating arithmetic or vendor state engine.

Source compiler and literal circuit descriptions retain their original credit.
New dense Gaussian-dyadic execution and audit: Codex-assisted, Apache-2.0.
"""
from pathlib import Path
from collections import Counter
from functools import lru_cache
from copy import deepcopy
import gzip
import hashlib
import importlib.util
import json
import sys

B=Path(__file__).resolve().parent
ROOT=B.parents[1]
PRIOR=ROOT/'outputs/p104-contact-reassessment-20261025'
N=512


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def authenticate(raw, expected):
    need(sha(raw)==expected,'source authentication before import')


def load(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def frozen(value):
    return tuple(frozen(x) for x in value) if isinstance(value,(tuple,list)) else value


@lru_cache(None)
def prepared(gate):
    tag=gate[0]
    if tag=='P':
        rows=gate[1]
        need(len(rows)==9 and all(type(r) is int and 0<=r<N for r in rows),'nine-bit P rows')
        permutation=tuple(sum(((row&x).bit_count()%2)<<i for i,row in enumerate(rows)) for x in range(N))
        need(len(set(permutation))==N,'P is bijective')
        return tag,permutation
    if tag=='D':
        q,linear=gate[1:]
        need(len(q)==len(linear)==9,'nine-bit D rows')
        need(all(((q[i]>>j)&1)==((q[j]>>i)&1) for i in range(9) for j in range(9)),
             'symmetric quadratic form')
        need(all((linear[i]&1)==((q[i]>>i)&1) for i in range(9)), 'quadratic diagonal parity')
        phases=[]
        for x in range(N):
            degree_one=sum(linear[i] for i in range(9) if x>>i&1)
            cross=0
            for i in range(9):
                if x>>i&1:
                    for j in range(i+1,9):
                        if x>>j&1 and q[i]>>j&1:
                            cross+=2
            phases.append((degree_one+cross)%4)
        return tag,tuple(phases)
    if tag=='C':
        direction,sign=gate[1:]
        need(type(direction) is int and 0<direction<N and sign in (-1,1),'signed native C gate')
        return gate
    if tag=='X':
        need(type(gate[1]) is int and 0<=gate[1]<N,'native translation range')
        return gate
    need(tag=='phase' and type(gate[1]) is int,'global phase gate')
    return tag,gate[1]%4


def compile_circuit(circuit):
    return tuple(prepared(frozen(gate)) for gate in circuit)


def dense_column(circuit, basis):
    """Complex vector with integral real/imaginary parts and one dyadic scale.

    All gates run on complete dense vectors. Normalization is delayed until
    the circuit ends; no vendor tableau/state routine is called here.
    """
    real=[0]*N;imag=[0]*N;real[basis]=1;denominator=0
    for gate in circuit:
        tag=gate[0]
        if tag=='P':
            nr=[0]*N;ni=[0]*N
            for old,new in enumerate(gate[1]):
                nr[new]=real[old];ni[new]=imag[old]
            real,imag=nr,ni
        elif tag=='D' or tag=='phase':
            phases=gate[1] if tag=='D' else (gate[1],)*N
            for j,power in enumerate(phases):
                a,b=real[j],imag[j]
                if power==1:real[j],imag[j]=-b,a
                elif power==2:real[j],imag[j]=-a,-b
                elif power==3:real[j],imag[j]=b,-a
        elif tag=='X':
            offset=gate[1]
            real=[real[j^offset] for j in range(N)]
            imag=[imag[j^offset] for j in range(N)]
        else:
            need(tag=='C','known prepared gate')
            q,s=gate[1:]
            nr=[0]*N;ni=[0]*N
            for j in range(N):
                k=j^q
                a,b,c,d=real[j],imag[j],real[k],imag[k]
                nr[j]=a-s*b+c+s*d
                ni[j]=b+s*a+d-s*c
            real,imag=nr,ni
            denominator+=1
    common=0
    for v in real:common|=abs(v)
    for v in imag:common|=abs(v)
    need(common!=0,'unitary column is not zero')
    remove=min(denominator,(common&-common).bit_length()-1)
    if remove:
        real=[v>>remove for v in real];imag=[v>>remove for v in imag]
        denominator-=remove
    return real,imag,denominator


def compare_all(actual, expected, label):
    a,b=compile_circuit(actual),compile_circuit(expected)
    digest=hashlib.sha256()
    for column in range(N):
        left=dense_column(a,column)
        right=dense_column(b,column)
        need(left==right,label+' exact complete matrix column '+str(column))
        re,im,d=left
        need(sum(v*v for v in re)+sum(v*v for v in im)==1<<(2*d),label+' exact column norm')
        digest.update(json.dumps([column,d,re,im],separators=(',',':')).encode())
        digest.update(b'\n')
    return {'columns':N,'complex_entries':N*N,'matrix_sha256':digest.hexdigest()}


def first_difference(actual,expected):
    a,b=compile_circuit(actual),compile_circuit(expected)
    for column in range(N):
        if dense_column(a,column)!=dense_column(b,column):
            return column
    raise ValueError('deliberate native fault was accepted')


def main():
    manifest=json.loads((B/'INPUTS.json').read_text())
    for name,expected in manifest['files'].items():
        authenticate((ROOT/name).read_bytes(),expected)
    # Transitive source closure and previous normalized/invoice evidence stay
    # frozen. Authentication is not a rerun of their scientific computation.
    oldpins=json.loads((PRIOR/'INPUTS.json').read_text())
    for name,expected in oldpins['files'].items():
        authenticate((ROOT/name).read_bytes(),expected)
    oldreceipt=json.loads((PRIOR/'PAIR-RECEIPT.json').read_text())
    authenticate((PRIOR/'RESULT-normal.json').read_bytes(),oldreceipt['result_sha256'])
    oldresult=json.loads((PRIOR/'RESULT-normal.json').read_text())
    need(oldresult['reviewed_head']==manifest['reviewed_head'] and
         oldresult['source_endpoint']==oldresult['changed_endpoint']=='pass',
         'exact preceding source-bound endpoint coverage')
    sourcepins=json.loads((PRIOR/'sources/contact/SOURCES.json').read_text())['files']
    for name in ('clifford_exact.py','native_verify.py'):
        pin=next(p for p in sourcepins if p['path']=='research/p104-native-channel/vendor/'+name)
        raw=(B/'sources'/name).read_bytes()
        authenticate(raw,pin['sha256'])
        try:authenticate(raw+b'\n',pin['sha256'])
        except ValueError:pass
        else:raise ValueError('source corruption control accepted')
    C=load(B/'sources/clifford_exact.py','p104_native_audit_compiler')
    V=load(B/'sources/native_verify.py','p104_native_literal_definitions')
    old=json.loads(gzip.decompress((PRIOR/'sources/predecessor/WORD.json.gz').read_bytes()))
    new=json.loads(gzip.decompress((PRIOR/'sources/contact/WORD.json.gz').read_bytes()))
    need({k:v for k,v in old.items() if k!='program'}=={k:v for k,v in new.items() if k!='program'},
         'public contract, charts, endpoints and ports unchanged')
    edits={16798:[['MOVE',341,240,127,False],['MOVE',345,739,127,False]],
           16799:[['ADD',341,345,'-1',127]],16800:[['SCALE',341,'-1',127]],17061:[],17067:[]}
    need(new['program']==[e for i,old_event in enumerate(old['program']) for e in edits.get(i,[old_event])],
         'only the five source sites change')
    need([e[:-1] for e in old['program'] if e[0]!='MOVE']==
         [e[:-1] for e in new['program'] if e[0]!='MOVE'],'owned and scalar schedule unchanged')
    before=Counter((e[2],e[3]) for e in old['program'] if e[0]=='MOVE')
    after=Counter((e[2],e[3]) for e in new['program'] if e[0]=='MOVE')
    delta=Counter(after);delta.subtract(before)
    need({k:v for k,v in delta.items() if v}=={(739,240):-1,(240,127):-1,(739,127):1},
         'actual changed map multiplicities')
    controller=json.loads((PRIOR/'sources/predecessor/CONTROLLER.json').read_text())
    full=[e for e in controller['physical_events'] if e[0]=='LOCAL']
    need(len(full)==18 and all(e[3] is False for e in full),'all18 full invocations use this forward word')
    frames=old['frames']
    records={}
    circuits={}
    controls={}
    for name,a,b,rank in [('AB',739,240,1),('BD',240,127,5),('AD',739,127,6)]:
        need(len(frames[b])-len(frames[a])==rank,'literal native rank')
        op=C.canonical_frame(9,tuple(frames[a])).adjoint().then(C.canonical_frame(9,tuple(frames[b])))
        recipe,_=C.lower_child(op)
        need(recipe['rank']==rank and recipe['right'] is not None,'declared native child rank')
        actual=V.recipe(recipe)
        expected=V.adjoint(V.frame(frames[a],9))+V.frame(frames[b],9)
        checked=compare_all(actual,expected,name)
        records[name]={'old_frame':a,'new_frame':b,'rank':rank,'recipe':recipe,
                       'actual_gate_count':len(actual),'expected_gate_count':len(expected),**checked}
        circuits[name]=actual
        phased=actual+(('phase',1),)
        need(V.tableau(phased)==V.tableau(actual),'global phase fault invisible to signed Pauli tableau')
        controls[name+'_global_phase']={'first_rejected_column':first_difference(phased,expected),
                                       'signed_tableau_unchanged':True}
        inverse=list(actual)
        at=next(i for i,g in enumerate(inverse) if g[0]=='C')
        inverse[at]=('C',inverse[at][1],-inverse[at][2])
        controls[name+'_inverse_child']={'first_rejected_column':first_difference(tuple(inverse),expected)}
        wrong=deepcopy(recipe);wrong['left']['offset']^=1
        controls[name+'_wrong_boundary']={'first_rejected_column':first_difference(V.recipe(wrong),expected)}
        try:need(recipe['rank']+1==len(frames[b])-len(frames[a]),'wrong declared recursive rank')
        except ValueError:controls[name+'_wrong_rank']='rejected'
        else:raise ValueError('wrong rank accepted')
    composition=compare_all(circuits['AB']+circuits['BD'],circuits['AD'],'old two-leg versus direct')
    targets={str(r):{'initial_frame':old['initial'][r],'final_frame':old['final'][r],
                     'rank':len(frames[old['final'][r]])-len(frames[old['initial'][r]])}
             for r in (341,345)}
    result={'schema':'p104-native-contact-exact-matrices/v1','reviewed_head':manifest['reviewed_head'],
            'source_hashes':manifest['files'],'maps':records,'old_route_equals_new':composition,
            'controls':controls,'source_authentication_controls':2,
            'direct_dense_complex_entries':3*N*N,'composition_complex_entries':N*N,
            'caller_binding':{'full_calls':18,'all_forward':True,'public_fields':735,'owned_lifetimes':8,
                              'target_owners':targets,'public_chart_and_scalar_abi_unchanged':True,
                              'previous_normalized_and_invoice_receipt_reused':oldreceipt['result_sha256'],
                              'all_parent_native_maps_checked':False,'265_axis_routes_replayed':False},
            'positive_width_implication':'exact one-column chart equality tensors factorwise; common transport commutes with scalar ADD/SCALE; exterior coefficients are not tensor-powered; spectators stay identity',
            'interpretation':'dense integer real/imaginary vectors with a common power-of-two denominator; no vendor state/tableau used for matrix equality',
            'new_kappa':None,'full_parent_funding_admitted':False,'stop':True}
    print(json.dumps(result,sort_keys=True,separators=(',',':')))


if __name__=='__main__':main()
